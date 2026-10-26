"""Provider-neutral, GitHub-owned identity resolution for accepted giveaways.

Exactly one selected adapter. Every output is fail-closed, including failed
lookups, stale cached evidence, unimplemented providers and conflicting offers.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import giveaway_identity_itad as itad

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/giveaway_identity_provider.json"
CACHE = ROOT / "data/production/giveaways/v1/identity_cache.json"
EPIC_ID = re.compile(r"[0-9a-fA-F]{32}:[0-9a-fA-F]{32}\\Z")
GOG_ID = re.compile(r"[1-9][0-9]*\\Z")
STEAM_ID = re.compile(r"[1-9][0-9]*\\Z")


def load_config(path=CONFIG):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("contract") != "GIVEAWAY-IDENTITY-PROVIDER-V1" or doc.get("status") != "canonical":
        raise ValueError("giveaway identity provider contract invalid")
    selected = doc.get("giveaway_identity_provider")
    if selected not in ("itad", "igdb"):
        raise ValueError("giveaway identity provider unknown")
    return doc


def _utc(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_id(storefront, raw):
    if not isinstance(raw, str):
        return None
    if storefront == "epic" and EPIC_ID.fullmatch(raw):
        return raw.split(":", 1)[1]
    if storefront == "gog" and GOG_ID.fullmatch(raw):
        return raw
    if storefront == "steam" and STEAM_ID.fullmatch(raw):
        return raw
    return None


def _result(storefront, source_product_id, exact_id, provider, now, *, game_id=None,
            steam_appid=None, reason="unresolved", shop_ids=None, auth="none"):
    resolved = type(steam_appid) is int and steam_appid > 0
    return {
        "schema_version": 1,
        "source_storefront": storefront,
        "source_product_id": source_product_id,
        "source_provider_product_id": exact_id,
        "identity_provider": provider,
        "provider_game_id": game_id,
        "steam_appid": steam_appid if resolved else None,
        "status": "resolved" if resolved else "unresolved",
        "reason": reason,
        "provenance": {
            "authority": "source_exact_shop_id" if storefront in ("epic", "gog") else "first_party_steam_appid",
            "source_shop_id": (shop_ids or {}).get(storefront),
            "steam_shop_id": (shop_ids or {}).get("steam"),
            "lookup_forward": (
                "/lookup/id/shop/{shopId}/v1" if storefront in ("epic", "gog") and provider == "itad" else None
            ),
            "lookup_reverse": (
                "/lookup/shop/{shopId}/id/v1" if storefront in ("epic", "gog") and provider == "itad" else None
            ),
            "shop_map": "/service/shops/map/v1" if storefront in ("epic", "gog") and provider == "itad" else None,
            "auth_route": auth,
            "checked_at_utc": _utc(now),
            "api_docs": itad.API_DOC if provider == "itad" and storefront in ("epic", "gog") else None,
        },
    }


def _load_cache(path):
    try:
        cache = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(cache, dict) or cache.get("contract") != "GIVEAWAY-IDENTITY-CACHE-V1":
        return {}
    entries = cache.get("entries")
    return entries if isinstance(entries, dict) else {}


def _cache_key(provider, storefront, source_product_id):
    return "|".join((provider, storefront, source_product_id))


def _cached(entries, key, now, conf, storefront, source_product_id, exact_id, provider):
    row = entries.get(key)
    if not isinstance(row, dict):
        return None
    try:
        stamp = datetime.fromisoformat(row["cached_at_utc"].replace("Z", "+00:00"))
    except (KeyError, AttributeError, ValueError, TypeError):
        return None
    result = row.get("result")
    if not isinstance(result, dict):
        return None
    hours = conf["cache"]["resolved_ttl_hours"] if result.get("status") == "resolved" else conf["cache"]["unresolved_ttl_hours"]
    if stamp.tzinfo is None or stamp > now or now - stamp > timedelta(hours=hours):
        return None
    if (result.get("source_storefront"), result.get("source_product_id"),
        result.get("source_provider_product_id"), result.get("identity_provider")) != (
        storefront, source_product_id, exact_id, provider
    ):
        return None
    if result.get("reason") in ("provider_unavailable", "provider_not_ready", "source_id_invalid"):
        return None
    if result.get("status") == "resolved" and (type(result.get("steam_appid")) is not int or result["steam_appid"] <= 0):
        return None
    if result.get("status") not in ("resolved", "unresolved"):
        return None
    return {**result, "provenance": {**result.get("provenance", {}), "cache_reused": True}}


def resolve_snapshot(snapshot, session, now, *, config=None, cache_path=CACHE, api_key=None):
    """Enrich in place; returns bounded identity-resolution counts.

    Called only by scripts/giveaway_production.py before its one snapshot write.
    """
    conf = config or load_config()
    provider = conf["giveaway_identity_provider"]
    api_key = os.environ.get("ITAD_API_KEY") if api_key is None else api_key
    auth = "ITAD-API-Key_header" if api_key else "none_documented"
    entries = _load_cache(cache_path)
    new_entries = dict(entries)
    shop_ids = None
    shop_error = None
    counts = {"resolved": 0, "unresolved": 0, "cache_hits": 0, "network_lookups": 0}
    for game in snapshot.get("games", []):
        for offer in game.get("offers", []):
            storefront = offer.get("storefront")
            product = offer.get("source_product_id")
            exact = _source_id(storefront, product)
            if storefront not in ("steam", "epic", "gog") or exact is None:
                result = _result(storefront, product, exact, provider, now, reason="source_id_invalid")
            elif storefront == "steam":
                result = _result(storefront, product, exact, provider, now,
                                 steam_appid=int(exact), reason="first_party_exact_steam")
            elif provider != "itad":
                result = _result(storefront, product, exact, provider, now, reason="provider_not_ready")
            else:
                key = _cache_key(provider, storefront, product)
                result = _cached(entries, key, now, conf, storefront, product, exact, provider)
                if result is not None:
                    counts["cache_hits"] += 1
                else:
                    if shop_ids is None and shop_error is None:
                        try:
                            shop_ids = itad.discover_shop_ids(session, conf, api_key)
                        except itad.ITADUnavailable as exc:
                            shop_error = str(exc)
                    if shop_error:
                        result = _result(storefront, product, exact, provider, now,
                                         reason="provider_unavailable:" + shop_error, auth=auth)
                    else:
                        counts["network_lookups"] += 1
                        gid, appid, reason = itad.resolve_exact(
                            session, conf, shop_ids, storefront, exact, api_key
                        )
                        result = _result(storefront, product, exact, provider, now,
                                         game_id=gid, steam_appid=appid, reason=reason,
                                         shop_ids=shop_ids, auth=auth)
                        if reason != "provider_unavailable":
                            new_entries[key] = {"cached_at_utc": _utc(now), "result": result}
            offer["identity_resolution"] = result
            counts[result["status"]] += 1

        resolutions = [o.get("identity_resolution") for o in game.get("offers", [])]
        appids = {r["steam_appid"] for r in resolutions if r and r["status"] == "resolved"}
        if resolutions and all(r and r["status"] == "resolved" for r in resolutions) and len(appids) == 1:
            appid = next(iter(appids))
            state, reason = "resolved", "all_offers_exact_same_steam_app"
        else:
            appid = None
            state = "unresolved"
            reason = "offer_identities_conflict" if len(appids) > 1 else "offer_identity_unresolved"
        game["analysis_identity"] = {
            "schema_version": 1, "status": state, "reason": reason,
            "steam_appid": appid, "identity_provider": provider,
            "source_offer_ids": [o.get("source_offer_id") for o in game.get("offers", [])],
        }
    if new_entries != entries:
        path = Path(cache_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "contract": "GIVEAWAY-IDENTITY-CACHE-V1", "entries": new_entries
        }, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    snapshot["identity_provider"] = provider
    snapshot["identity_resolution_counts"] = counts
    return counts
