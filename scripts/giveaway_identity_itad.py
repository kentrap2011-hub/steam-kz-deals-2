"""Exact ITAD shop-ID adapter. No title, deal, price or fuzzy endpoints."""
from __future__ import annotations

import re
import uuid

from giveaway_http import HTTP_TIMEOUT_SECONDS

API_DOC = "https://docs.isthereanydeal.com/"
APP_ID = re.compile(r"app/([1-9][0-9]*)\\Z")


class ITADUnavailable(RuntimeError):
    """A transport/schema failure; never authorizes an identity."""


def _json_response(response):
    response.raise_for_status()
    return response.json()


def _headers(key):
    result = {"Accept": "application/json", "Content-Type": "application/json"}
    if key:
        result["ITAD-API-Key"] = key
    return result


def discover_shop_ids(session, config, key=None):
    """Read the official shop map; accept only a unique exact configured title."""
    api = config["itad"]
    try:
        rows = _json_response(session.get(
            api["api_base"] + api["shop_map"],
            headers=_headers(key), timeout=HTTP_TIMEOUT_SECONDS,
        ))
    except Exception as exc:
        raise ITADUnavailable("shop_map_unavailable") from exc
    if not isinstance(rows, list):
        raise ITADUnavailable("shop_map_schema_invalid")
    result = {}
    for storefront, titles in api["shop_titles"].items():
        ids = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ITADUnavailable("shop_map_schema_invalid")
            shop_id = row.get("id")
            if not isinstance(shop_id, int) or isinstance(shop_id, bool) or shop_id <= 0 or not isinstance(row.get("title"), str):
                raise ITADUnavailable("shop_map_schema_invalid")
            if row["title"] in titles:
                ids.add(shop_id)
        if len(ids) != 1:
            raise ITADUnavailable("shop_id_missing_or_ambiguous:" + storefront)
        result[storefront] = ids.pop()
    return result


def resolve_exact(session, config, shop_ids, storefront, exact_product_id, key=None):
    """Return (ITAD UUID or None, Steam appid or None, reason).

    Official lookup schemas are keyed objects: shop product ID -> UUID|null,
    then UUID -> array of exact shop IDs|null.
    """
    api = config["itad"]
    try:
        first = _json_response(session.post(
            api["api_base"] + api["forward"].format(shopId=shop_ids[storefront]),
            json=[exact_product_id], headers=_headers(key),
            timeout=HTTP_TIMEOUT_SECONDS,
        ))
    except Exception:
        return None, None, "provider_unavailable"
    if not isinstance(first, dict) or set(first) != {exact_product_id}:
        return None, None, "forward_response_ambiguous"
    game_id = first[exact_product_id]
    if game_id is None:
        return None, None, "no_exact_shop_mapping"
    if not isinstance(game_id, str):
        return None, None, "forward_identity_invalid"
    try:
        if str(uuid.UUID(game_id)) != game_id.lower():
            return None, None, "forward_identity_invalid"
    except ValueError:
        return None, None, "forward_identity_invalid"
    try:
        second = _json_response(session.post(
            api["api_base"] + api["reverse"].format(shopId=shop_ids["steam"]),
            json=[game_id], headers=_headers(key),
            timeout=HTTP_TIMEOUT_SECONDS,
        ))
    except Exception:
        return game_id, None, "provider_unavailable"
    if not isinstance(second, dict) or set(second) != {game_id}:
        return game_id, None, "reverse_response_ambiguous"
    shop_products = second[game_id]
    if shop_products is None:
        return game_id, None, "no_exact_steam_app"
    if not isinstance(shop_products, list) or any(not isinstance(v, str) for v in shop_products):
        return game_id, None, "reverse_response_invalid"
    # A sub or bundle is not an app. More than one app remains unresolved.
    appids = [int(m.group(1)) for v in shop_products if (m := APP_ID.fullmatch(v))]
    if not appids:
        return game_id, None, "no_exact_steam_app"
    if len(appids) != 1:
        return game_id, None, "ambiguous_steam_app"
    return game_id, appids[0], "exact_unique"
