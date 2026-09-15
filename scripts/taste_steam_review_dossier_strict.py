#!/usr/bin/env python3
"""Source-independent strict Steam-review-dossier validation.

This module closes worker/validator shape, type, identity and consistency gaps while
intentionally leaving review-source access/sufficiency semantics to the dedicated
review-source follow-up.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from taste_steam_review_dossier import (
    canonical_sha256,
    parse_utc,
    validate_dossier as validate_legacy_dossier,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = ROOT / "config/taste_steam_review_dossier_schema.json"


def load_worker_schema(path=DEFAULT_SCHEMA_PATH):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V1"
        or type(doc.get("version")) is not int
        or doc.get("version") != 1
        or doc.get("status") != "active"
    ):
        raise ValueError("worker-facing dossier schema is missing, stale or unsupported")
    return doc


def _json_int(value):
    return type(value) is int


def _require_fields(obj, fields, label):
    if not isinstance(obj, dict):
        raise ValueError(f"{label} must be an object")
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")


def _url_binds_appid(url, appid):
    if not isinstance(url, str) or not url:
        return False
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "store.steampowered.com":
        return False
    parts = [part for part in parsed.path.split("/") if part]
    for marker in ("app", "appreviews"):
        if marker in parts:
            index = parts.index(marker)
            if index + 1 < len(parts) and parts[index + 1] == appid:
                return True
    return False


def _validate_timestamp_if_present(obj, field, label):
    if field not in obj:
        return
    try:
        parse_utc(obj[field])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}.{field} must be a timezone-aware ISO-8601 timestamp") from exc


def validate_dossier_strict(
    dossier,
    contract,
    *,
    expected_appid=None,
    expected_title=None,
    expected_ttl_days=None,
    now=None,
    schema_doc=None,
):
    """Validate all source-independent canonical dossier invariants."""
    schema_doc = schema_doc or load_worker_schema()
    _require_fields(dossier, schema_doc["required_top_level_fields"], "dossier")

    if dossier.get("schema") != schema_doc["dossier_schema"]:
        raise ValueError("unsupported Steam review dossier schema")
    if not _json_int(dossier.get("schema_version")) or dossier["schema_version"] != schema_doc["dossier_schema_version"]:
        raise ValueError("dossier schema_version must be JSON integer 1")

    appid = dossier.get("appid")
    if not isinstance(appid, str) or not appid.isdigit():
        raise ValueError("dossier appid must be a numeric string")
    if expected_appid is not None and appid != str(expected_appid):
        raise ValueError("dossier appid does not match prepared work scope")

    title = dossier.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > 300:
        raise ValueError("dossier title is missing or invalid")
    if expected_title is not None and title != expected_title:
        raise ValueError("dossier title does not exactly match prepared descriptor title")

    ttl = dossier.get("ttl_days")
    ttl_rule = schema_doc["integer_rules"]["ttl_days"]
    if not _json_int(ttl) or not ttl_rule["minimum"] <= ttl <= ttl_rule["maximum"]:
        raise ValueError("dossier ttl_days must be a canonical JSON integer in range")
    if expected_ttl_days is not None and ttl != expected_ttl_days:
        raise ValueError("dossier TTL does not match prepared work manifest")

    generated = parse_utc(dossier.get("generated_at_utc"))
    expires = parse_utc(dossier.get("expires_at_utc"))
    if expires != generated + timedelta(days=ttl):
        raise ValueError("dossier expiry must equal generated_at + ttl_days")
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    max_future = int(schema_doc["timestamp_rules"]["maximum_future_skew_minutes_at_ingest"])
    if generated > now_utc + timedelta(minutes=max_future):
        raise ValueError("future-generated dossier cannot be canonically ingested")

    enums = schema_doc["enums"]
    observations = dossier.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("dossier observations must be a non-empty list")
    seen_observations = set()
    recurrence_min = schema_doc["observation_invariants"]["recurrence_minimum_mentions"]
    for index, observation in enumerate(observations):
        _require_fields(
            observation,
            ("category", "statement", "sentiment", "recurrence", "mention_count", "evidence_languages"),
            f"observation {index}",
        )
        if observation["category"] not in enums["observation_category"]:
            raise ValueError(f"observation {index} has unsupported category")
        if observation["sentiment"] not in enums["sentiment"]:
            raise ValueError(f"observation {index} sentiment is invalid")
        recurrence = observation["recurrence"]
        if recurrence not in enums["recurrence"]:
            raise ValueError(f"observation {index} recurrence is invalid")
        mention_count = observation["mention_count"]
        if not _json_int(mention_count) or mention_count < 1:
            raise ValueError(f"observation {index} mention_count must be a positive JSON integer")
        if recurrence == "anecdotal":
            if mention_count != 1:
                raise ValueError(f"observation {index} anecdotal recurrence must be one mention")
        elif mention_count < int(recurrence_min[recurrence]):
            raise ValueError(f"observation {index} understates required mentions for recurrence")
        languages = observation["evidence_languages"]
        if (
            not isinstance(languages, list)
            or not languages
            or any(language not in enums["evidence_languages"] for language in languages)
        ):
            raise ValueError(f"observation {index} evidence_languages are invalid")
        digest = canonical_sha256(observation)
        if digest in seen_observations:
            raise ValueError("dossier contains an exact duplicate observation")
        seen_observations.add(digest)

    conflicts = dossier.get("conflicts")
    if not isinstance(conflicts, list):
        raise ValueError("dossier conflicts must be a list")
    for index, conflict in enumerate(conflicts):
        if not isinstance(conflict, dict):
            raise ValueError(f"conflict {index} is invalid")
        if conflict.get("recurrence") not in enums["recurrence"]:
            raise ValueError(f"conflict {index} recurrence is invalid")

    sample = dossier.get("review_sample")
    _require_fields(
        sample,
        ("strategy", "sampled_total", "sampled_russian", "sampled_non_russian", "sample_ids_sha256", "lanes"),
        "review_sample",
    )
    if sample["strategy"] not in enums["review_sampling_strategy"]:
        raise ValueError("review sampling strategy is invalid")
    for name in ("sampled_total", "sampled_russian", "sampled_non_russian"):
        if not _json_int(sample[name]) or sample[name] < 0:
            raise ValueError(f"review_sample.{name} must be a non-negative JSON integer")
    if sample["sampled_russian"] + sample["sampled_non_russian"] != sample["sampled_total"]:
        raise ValueError("review sample lane counts do not sum to sampled_total")

    lanes = sample.get("lanes")
    expected_scopes = enums["review_lane_language_scope"]
    if not isinstance(lanes, list) or len(lanes) != len(expected_scopes):
        raise ValueError("review_sample must contain exactly two review lanes")
    by_scope = {}
    for lane in lanes:
        _require_fields(lane, ("language_scope", "sampled", "batches", "stop_reason"), "review lane")
        scope = lane["language_scope"]
        if scope not in expected_scopes or scope in by_scope:
            raise ValueError("review lanes must contain each canonical language scope exactly once")
        if not _json_int(lane["sampled"]) or lane["sampled"] < 0:
            raise ValueError("lane sampled count must be a non-negative JSON integer")
        if not _json_int(lane["batches"]) or lane["batches"] < 0:
            raise ValueError("lane batch count must be a non-negative JSON integer")
        if not isinstance(lane["stop_reason"], str) or not lane["stop_reason"]:
            raise ValueError("lane stop_reason is required")
        by_scope[scope] = lane
    if set(by_scope) != set(expected_scopes):
        raise ValueError("review lane identities are incomplete")
    if by_scope["russian"]["sampled"] != sample["sampled_russian"]:
        raise ValueError("Russian lane sampled count does not match sampled_russian")
    if by_scope["non_russian"]["sampled"] != sample["sampled_non_russian"]:
        raise ValueError("non-Russian lane sampled count does not match sampled_non_russian")

    provenance = dossier.get("provenance")
    _require_fields(provenance, ("store_description", "steam_reviews"), "provenance")
    store = provenance["store_description"]
    reviews = provenance["steam_reviews"]
    _require_fields(store, schema_doc["provenance_required_structure"]["store_description"], "provenance.store_description")
    _require_fields(reviews, schema_doc["provenance_required_structure"]["steam_reviews"], "provenance.steam_reviews")
    if not _url_binds_appid(store.get("url"), appid):
        raise ValueError("Steam store description provenance URL does not bind to dossier appid")
    if not _url_binds_appid(reviews.get("url"), appid):
        raise ValueError("Steam review provenance URL does not bind to dossier appid")
    _validate_timestamp_if_present(store, "captured_at_utc", "provenance.store_description")
    _validate_timestamp_if_present(reviews, "captured_at_utc", "provenance.steam_reviews")

    # Preserve all pre-existing compactness, raw-review and personal/commercial guards.
    validate_legacy_dossier(
        dossier,
        contract,
        expected_appid=appid,
        expected_ttl_days=ttl,
    )
    return dossier


def validate_dossiers_against_expected_items(
    dossiers,
    expected_items,
    contract,
    *,
    expected_ttl_days,
    now=None,
    schema_doc=None,
):
    if not isinstance(dossiers, list) or not isinstance(expected_items, list):
        raise ValueError("dossiers and expected items must be lists")
    if len(dossiers) != len(expected_items):
        raise ValueError("dossier count does not match exact prepared item count")
    schema_doc = schema_doc or load_worker_schema()
    validated = []
    for index, (dossier, item) in enumerate(zip(dossiers, expected_items)):
        if not isinstance(item, dict):
            raise ValueError(f"prepared item {index} is malformed")
        validated.append(validate_dossier_strict(
            dossier,
            contract,
            expected_appid=str(item.get("appid") or ""),
            expected_title=item.get("title"),
            expected_ttl_days=expected_ttl_days,
            now=now,
            schema_doc=schema_doc,
        ))
    return validated
