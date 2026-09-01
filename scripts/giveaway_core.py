from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONTRACT = "CROSS-PLATFORM-GIVEAWAY-V1"
SCHEMA_VERSION = 1
COUNTRY_CODE = "KZ"
REQUIRED_SOURCES = ("steam", "epic", "gog")
SNAPSHOT_FRESHNESS_HOURS = 30

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_ROOT = ROOT / "data" / "production"
OUTPUT_ROOT = PRODUCTION_ROOT / "giveaways"
VERSION_ROOT = OUTPUT_ROOT / "v1"
CURRENT_PATH = VERSION_ROOT / "current.json"
AUDIT_PATH = VERSION_ROOT / "audit.jsonl"
INDEX_PATH = OUTPUT_ROOT / "index.json"

class SourceError(RuntimeError):
    code = "SOURCE_ERROR"

class SourceSchemaError(SourceError):
    code = "SOURCE_SCHEMA_FAILURE"

class SourceFreshnessError(SourceError):
    code = "SOURCE_STALE"

@dataclass
class SourceCollection:
    source_id: str
    candidates: list[dict[str, Any]]
    complete: bool
    status: str
    endpoint: str
    observed_at_utc: str
    details: dict[str, Any]
    error_code: str | None = None
    error: str | None = None

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def iso_utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        result = datetime.fromisoformat(text)
    except ValueError:
        return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)

def safe_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return float(value)
    if not isinstance(value, str):
        return None
    match = re.search(r"-?\d+(?:[.,]\d+)?", value.replace("\u00a0", "").replace(" ", ""))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "."))
    except ValueError:
        return None

def normalize_identity_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())

def source_offer_key(source_id: str, product_id: str, end_at: str | None, suffix: str | None = None) -> str:
    parts = [source_id, product_id, end_at or "window-unknown"]
    if suffix:
        parts.append(str(suffix))
    return ":".join(parts)

def base_candidate(source_id: str, observed_at: datetime) -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "schema_version": SCHEMA_VERSION,
        "source_id": source_id,
        "storefront": source_id,
        "source_kind": "first_party_store",
        "source_offer_id": None,
        "source_product_id": None,
        "title": None,
        "claim_url": None,
        "promotion_start_utc": None,
        "promotion_end_utc": None,
        "observed_at_utc": iso_utc(observed_at),
        "promotion_type": "unknown",
        "ownership_semantics": "unknown",
        "active_now_evidence": False,
        "explicit_giveaway_evidence": False,
        "base_price": None,
        "final_price": None,
        "currency": None,
        "discount_percent": None,
        "region_status": "unknown",
        "region_evidence": None,
        "content_type": "unknown",
        "requires_subscription": False,
        "access_expires_after_claim": None,
        "identity_publishers": [],
        "source_provenance": {},
        "classification_status": None,
        "classification_reason_codes": [],
        "classification_confidence": None,
    }

def _classified(item: dict[str, Any], status: str, code: str, confidence: str = "high") -> dict[str, Any]:
    result = dict(item)
    result["classification_status"] = status
    result["classification_reason_codes"] = [code]
    result["classification_confidence"] = confidence
    return result

def classify_candidate(item: dict[str, Any], now: datetime) -> dict[str, Any]:
    if item.get("precheck_reason"):
        return _classified(item, "rejected", str(item["precheck_reason"]))

    content = (item.get("content_type") or "unknown").casefold()
    if content not in {"game", "complete_edition"}:
        if content == "unknown":
            return _classified(item, "unverified", "CONTENT_TYPE_UNKNOWN", "low")
        return _classified(item, "rejected", "NON_GAME_CONTENT")
    if item.get("requires_subscription"):
        return _classified(item, "rejected", "REQUIRES_SUBSCRIPTION")
    if item.get("region_status") == "unavailable":
        return _classified(item, "rejected", "KZ_UNAVAILABLE")
    if item.get("region_status") != "available":
        return _classified(item, "unverified", "KZ_REGION_UNKNOWN", "low")
    if item.get("access_expires_after_claim") is True or item.get("promotion_type") == "access_only":
        return _classified(item, "rejected", "ACCESS_ONLY_FREE_WEEKEND")
    if item.get("promotion_type") == "permanent_f2p":
        return _classified(item, "rejected", "PERMANENT_F2P")

    final_price = safe_number(item.get("final_price"))
    base_price = safe_number(item.get("base_price"))
    if final_price is None:
        return _classified(item, "unverified", "FINAL_PRICE_UNKNOWN", "low")
    if final_price != 0:
        return _classified(item, "rejected", "NOT_ZERO_PRICE")
    if not ((base_price is not None and base_price > 0) or item.get("explicit_giveaway_evidence")):
        return _classified(item, "rejected", "PERMANENT_F2P")
    if item.get("ownership_semantics") != "permanent_after_claim":
        return _classified(item, "unverified", "OWNERSHIP_SEMANTICS_UNKNOWN", "low")

    start = parse_iso(item.get("promotion_start_utc"))
    end = parse_iso(item.get("promotion_end_utc"))
    if end is None:
        return _classified(item, "unverified", "PROMOTION_WINDOW_UNKNOWN", "low")
    if start is not None and now < start:
        return _classified(item, "rejected", "UPCOMING_NOT_ACTIVE")
    if now >= end:
        return _classified(item, "rejected", "PROMOTION_EXPIRED")
    if start is None and not item.get("active_now_evidence"):
        return _classified(item, "unverified", "PROMOTION_WINDOW_UNKNOWN", "low")
    if not item.get("claim_url"):
        return _classified(item, "unverified", "CLAIM_URL_UNKNOWN", "low")

    result = dict(item)
    result["classification_status"] = "accepted"
    result["classification_reason_codes"] = [
        "ACTIVE_WINDOW", "ZERO_PRICE", "PAID_BASE_OR_EXPLICIT_GIVEAWAY",
        "PERMANENT_GRANT", "FULL_GAME", "KZ_AVAILABLE",
    ]
    result["classification_confidence"] = "high"
    return result

def safe_cross_store_identity(item: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    title = normalize_identity_text(str(item.get("title") or ""))
    publishers = sorted({normalize_identity_text(str(x)) for x in (item.get("identity_publishers") or []) if normalize_identity_text(str(x))})
    if title and publishers:
        payload = json.dumps([title, publishers], separators=(",", ":"), ensure_ascii=False)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        return f"meta-v1:{digest}", "high", {"basis": "exact_normalized_title_and_publishers", "publishers": publishers}
    source_id = str(item.get("source_id") or "unknown")
    product_id = str(item.get("source_product_id") or item.get("source_offer_id") or "unknown")
    return f"source-v1:{source_id}:{product_id}", "source_only", {"basis": "source_identity_only"}

def group_accepted_offers(accepted: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for offer in accepted:
        key, confidence, evidence = safe_cross_store_identity(offer)
        public = {name: offer.get(name) for name in (
            "source_id", "source_offer_id", "source_product_id", "storefront", "title", "claim_url",
            "promotion_start_utc", "promotion_end_utc", "observed_at_utc", "base_price", "final_price",
            "currency", "discount_percent", "content_type", "region_status", "classification_reason_codes",
        )}
        group = groups.setdefault(key, {
            "canonical_game_key": key,
            "identity_confidence": confidence,
            "identity_evidence": evidence,
            "title": offer.get("title"),
            "offers": [],
        })
        group["offers"].append(public)
    for group in groups.values():
        group["offers"].sort(key=lambda x: (str(x.get("source_id")), str(x.get("source_offer_id"))))
    return sorted(groups.values(), key=lambda x: (normalize_identity_text(str(x.get("title") or "")), x["canonical_game_key"]))

def source_health_record(collection: SourceCollection, classified: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"accepted": 0, "rejected": 0, "unverified": 0}
    for item in classified:
        status = item.get("classification_status")
        if status in counts:
            counts[status] += 1
    return {
        "required": collection.source_id in REQUIRED_SOURCES,
        "status": collection.status,
        "complete": bool(collection.complete),
        "observed_at_utc": collection.observed_at_utc,
        "endpoint": collection.endpoint,
        "candidate_count": len(classified),
        "accepted_count": counts["accepted"],
        "rejected_count": counts["rejected"],
        "unverified_count": counts["unverified"],
        "error_code": collection.error_code,
        "error": collection.error,
        "details": collection.details,
    }

def build_snapshot(collections: dict[str, SourceCollection], now: datetime) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    classified_all: list[dict[str, Any]] = []
    health: dict[str, Any] = {}
    for source_id in REQUIRED_SOURCES:
        collection = collections[source_id]
        classified = [classify_candidate(item, now) for item in collection.candidates]
        classified_all.extend(classified)
        health[source_id] = source_health_record(collection, classified)

    accepted = [item for item in classified_all if item.get("classification_status") == "accepted"]
    accepted = [item for item in accepted if parse_iso(item.get("promotion_end_utc")) is not None and now < parse_iso(item.get("promotion_end_utc"))]
    complete = all(health[source_id]["complete"] for source_id in REQUIRED_SOURCES)
    groups = group_accepted_offers(accepted)
    snapshot = {
        "contract": CONTRACT,
        "schema_version": SCHEMA_VERSION,
        "country_code": COUNTRY_CODE,
        "generated_at_utc": iso_utc(now),
        "fresh_until_utc": iso_utc(now + timedelta(hours=SNAPSHOT_FRESHNESS_HOURS)),
        "snapshot_status": "complete" if complete else "incomplete",
        "required_sources": list(REQUIRED_SOURCES),
        "source_health": health,
        "accepted_offer_count": len(accepted),
        "game_group_count": len(groups),
        "rejected_offer_count": sum(1 for x in classified_all if x.get("classification_status") == "rejected"),
        "unverified_offer_count": sum(1 for x in classified_all if x.get("classification_status") == "unverified"),
        "games": groups,
        "publication_invariants": {
            "accepted_offers_are_active_at_generated_at": True,
            "stale_source_rows_are_not_reused": True,
            "title_only_cross_store_merge": False,
            "subscription_entitlements_included": False,
            "paid_ranking_or_taste_modified": False,
        },
    }
    return snapshot, classified_all

def failed_collection(source_id: str, endpoint: str, now: datetime, exc: Exception) -> SourceCollection:
    code = exc.code if isinstance(exc, SourceError) else "SOURCE_ERROR"
    return SourceCollection(source_id, [], False, "failed", endpoint, iso_utc(now) or "", {}, code, str(exc))

def write_snapshot(snapshot: dict[str, Any], audit: list[dict[str, Any]]) -> None:
    VERSION_ROOT.mkdir(parents=True, exist_ok=True)
    CURRENT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT_PATH.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in audit), encoding="utf-8")
    index = {
        "contract": CONTRACT,
        "schema_version": SCHEMA_VERSION,
        "country_code": COUNTRY_CODE,
        "generated_at_utc": snapshot["generated_at_utc"],
        "fresh_until_utc": snapshot["fresh_until_utc"],
        "snapshot_status": snapshot["snapshot_status"],
        "required_sources": snapshot["required_sources"],
        "source_health": snapshot["source_health"],
        "accepted_offer_count": snapshot["accepted_offer_count"],
        "game_group_count": snapshot["game_group_count"],
        "current_path": "data/production/giveaways/v1/current.json",
        "audit_path": "data/production/giveaways/v1/audit.jsonl",
        "writer": "scripts/giveaway_production.py",
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def validate_existing_artifact(require_complete: bool) -> int:
    if not CURRENT_PATH.exists() or not INDEX_PATH.exists():
        return 2
    snapshot = json.loads(CURRENT_PATH.read_text(encoding="utf-8"))
    if snapshot.get("contract") != CONTRACT or snapshot.get("schema_version") != SCHEMA_VERSION:
        return 2
    if any(source_id not in (snapshot.get("source_health") or {}) for source_id in REQUIRED_SOURCES):
        return 2
    generated = parse_iso(snapshot.get("generated_at_utc"))
    fresh_until = parse_iso(snapshot.get("fresh_until_utc"))
    if generated is None or fresh_until is None or fresh_until <= generated:
        return 2
    if require_complete and snapshot.get("snapshot_status") != "complete":
        return 3
    return 0
