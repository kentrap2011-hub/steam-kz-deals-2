from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import requests

from giveaway_core import (
    PRODUCTION_ROOT,
    SourceCollection,
    SourceFreshnessError,
    SourceSchemaError,
    base_candidate,
    iso_utc,
    parse_iso,
    source_offer_key,
)
from giveaway_http import get_json, get_text, html_to_text

MAX_SOURCE_AGE_HOURS = 36
FREEBIES = PRODUCTION_ROOT / "freebies.tsv"
FREEBIES_INDEX = PRODUCTION_ROOT / "freebies_index.json"
MANIFEST = PRODUCTION_ROOT / "manifest.json"
APPDETAILS = "https://store.steampowered.com/api/appdetails"
STORE_URL = "https://store.steampowered.com/app/{appid}/?cc=KZ"

TYPE_MAP = {
    "game": "game",
    "dlc": "dlc",
    "demo": "demo",
    "music": "soundtrack",
    "video": "other",
    "mod": "other",
    "hardware": "other",
    "advertising": "other",
}


def _load_candidates(now: datetime) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if not (MANIFEST.exists() and FREEBIES_INDEX.exists() and FREEBIES.exists()):
        raise SourceSchemaError("Steam candidate artifacts are missing")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    index = json.loads(FREEBIES_INDEX.read_text(encoding="utf-8"))
    if manifest.get("country_code") != "kz" or manifest.get("complete") is not True:
        raise SourceSchemaError("Steam manifest is not a complete KZ traversal")

    updated = parse_iso(index.get("source_updated_at_utc") or manifest.get("updated_at_utc"))
    if updated is None:
        raise SourceFreshnessError("Steam candidate freshness timestamp is missing")
    age_hours = (now - updated).total_seconds() / 3600
    if age_hours < -1 or age_hours > MAX_SOURCE_AGE_HOURS:
        raise SourceFreshnessError(f"Steam candidate snapshot is stale: {age_hours:.1f}h")

    columns = index.get("columns")
    if not isinstance(columns, list) or not {"appid", "discount_percent", "title"}.issubset(columns):
        raise SourceSchemaError("Steam freebies index schema changed")

    rows: list[dict[str, str]] = []
    for raw in FREEBIES.read_text(encoding="utf-8").splitlines():
        values = raw.split("\t")
        if len(values) != len(columns):
            raise SourceSchemaError("Steam freebies row width does not match index")
        rows.append(dict(zip(columns, values)))
    if len(rows) != int(index.get("item_count", -1)):
        raise SourceSchemaError("Steam freebies item_count does not match file")

    return rows, {
        "candidate_source_updated_at_utc": iso_utc(updated),
        "candidate_count": len(rows),
        "source_age_hours": round(age_hours, 3),
        "candidate_rule": "existing KZ catalog: final price 0 + positive discount; validation is separate",
    }


def _page_evidence(raw_html: str) -> dict[str, Any]:
    text = html_to_text(raw_html).casefold()
    expiration = re.search(r'data-discount-expiration=["\'](\d+)["\']', raw_html, re.I)
    return {
        "region_unavailable": any(marker in text for marker in (
            "this item is currently unavailable in your region",
            "not available for purchase in your country",
        )),
        "free_to_keep": "free to keep when you get it before" in text,
        "access_only": any(marker in text for marker in (
            "free weekend", "play for free", "play it for free",
        )),
        "promotion_end_utc": iso_utc(datetime.fromtimestamp(int(expiration.group(1)), tz=timezone.utc)) if expiration else None,
    }


def normalize_candidate(row: dict[str, str], payload: dict[str, Any], page_html: str, observed: datetime) -> dict[str, Any]:
    appid = str(row.get("appid") or "").strip()
    item = base_candidate("steam", observed)
    item["source_product_id"] = appid
    item["title"] = row.get("title") or None
    item["claim_url"] = STORE_URL.format(appid=appid)
    item["source_provenance"] = {
        "candidate": "data/production/freebies.tsv",
        "appdetails": f"{APPDETAILS}?appids={appid}&cc=KZ&l=english",
        "store_page": item["claim_url"],
    }

    if not isinstance(payload, dict) or appid not in payload:
        item["precheck_reason"] = "SOURCE_SCHEMA_FAILURE"
        return item
    envelope = payload[appid]
    if not isinstance(envelope, dict) or envelope.get("success") is not True or not isinstance(envelope.get("data"), dict):
        item["precheck_reason"] = "SOURCE_SCHEMA_FAILURE"
        return item

    data = envelope["data"]
    item["title"] = data.get("name") or item["title"]
    item["content_type"] = TYPE_MAP.get(str(data.get("type") or "").casefold(), "unknown")
    item["identity_publishers"] = [str(x) for x in (data.get("publishers") or []) if x]

    price = data.get("price_overview") if isinstance(data.get("price_overview"), dict) else {}
    if price:
        item["base_price"] = price.get("initial")
        item["final_price"] = price.get("final")
        item["currency"] = price.get("currency")
        item["discount_percent"] = price.get("discount_percent")
    else:
        discount = row.get("discount_percent")
        item["final_price"] = 0 if str(discount) == "100" else None
        item["discount_percent"] = int(discount) if str(discount).isdigit() else None

    evidence = _page_evidence(page_html)
    item["region_status"] = "unavailable" if evidence["region_unavailable"] else "available"
    item["region_evidence"] = {"requested_country": "KZ", "store_page_loaded": True}
    item["promotion_end_utc"] = evidence["promotion_end_utc"]
    item["active_now_evidence"] = bool(evidence["free_to_keep"])
    item["explicit_giveaway_evidence"] = bool(evidence["free_to_keep"])

    if evidence["access_only"] and not evidence["free_to_keep"]:
        item["promotion_type"] = "access_only"
        item["ownership_semantics"] = "access_only"
        item["access_expires_after_claim"] = True
    elif evidence["free_to_keep"]:
        item["promotion_type"] = "claim_to_keep"
        item["ownership_semantics"] = "permanent_after_claim"
        item["access_expires_after_claim"] = False
    elif item.get("final_price") == 0 and item.get("base_price") in (0, None):
        item["promotion_type"] = "permanent_f2p"

    item["source_offer_id"] = source_offer_key("steam", appid, item.get("promotion_end_utc"))
    return item


def collect(session: requests.Session, now: datetime) -> SourceCollection:
    rows, details = _load_candidates(now)
    candidates: list[dict[str, Any]] = []
    validation_errors = 0
    for row in rows:
        appid = str(row.get("appid") or "").strip()
        try:
            payload = get_json(session, APPDETAILS, {"appids": appid, "cc": "KZ", "l": "english"})
            page = get_text(session, STORE_URL.format(appid=appid))
            candidates.append(normalize_candidate(row, payload, page, now))
        except Exception as exc:
            validation_errors += 1
            item = base_candidate("steam", now)
            item.update({
                "source_product_id": appid,
                "source_offer_id": source_offer_key("steam", appid, None),
                "title": row.get("title") or None,
                "precheck_reason": "SOURCE_VALIDATION_FETCH_FAILED",
                "source_provenance": {"error": str(exc)},
            })
            candidates.append(item)

    details["targeted_validation_errors"] = validation_errors
    complete = validation_errors == 0
    return SourceCollection(
        source_id="steam",
        candidates=candidates,
        complete=complete,
        status="ok" if complete else "degraded",
        endpoint="existing KZ catalog candidates + targeted Steam first-party validation",
        observed_at_utc=iso_utc(now) or "",
        details=details,
        error_code=None if complete else "SOURCE_VALIDATION_FETCH_FAILED",
        error=None if complete else f"{validation_errors} Steam candidate validation request(s) failed",
    )
