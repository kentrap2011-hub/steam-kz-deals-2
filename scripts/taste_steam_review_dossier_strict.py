#!/usr/bin/env python3
"""Strict V2 validation for neutral multi-source web-evidence Taste dossiers."""
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from taste_steam_review_dossier import (
    _validate_no_raw_or_personal_payload,
    canonical_sha256,
    parse_utc,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = ROOT / "config/taste_steam_review_dossier_schema.json"
DEFAULT_EVIDENCE_CONTRACT_PATH = ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json"
_DOMAIN_RE = re.compile(r"^[a-z0-9.-]+$")
_RAW_BODY_LIKE_KEYS = {
    "raw_reviews", "review_text", "review_body", "review_bodies", "reviews_raw",
    "raw_text", "body", "post_body", "comment_body", "source_text", "content_text",
    "snippet", "excerpt", "quote", "quotes", "full_text", "full_review", "review",
    "usernames", "authors",
}


def load_worker_schema(path=DEFAULT_SCHEMA_PATH):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2"
        or type(doc.get("version")) is not int
        or doc.get("version") != 2
        or doc.get("status") != "active"
        or doc.get("dossier_schema") != "TASTE-STEAM-REVIEW-DOSSIER-V2"
        or doc.get("dossier_schema_version") != 2
    ):
        raise ValueError("worker-facing dossier schema is missing, stale or unsupported")
    return doc


def load_web_evidence_contract(path=DEFAULT_EVIDENCE_CONTRACT_PATH):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V1"
        or type(doc.get("version")) is not int
        or doc.get("version") != 1
        or doc.get("status") != "active"
    ):
        raise ValueError("web evidence dossier contract is missing, stale or unsupported")
    return doc


def current_worker_contract_binding(schema_doc=None, evidence_contract=None):
    schema_doc = schema_doc or load_worker_schema()
    evidence_contract = evidence_contract or load_web_evidence_contract()
    return {
        "evidence_contract_schema": evidence_contract["schema"],
        "evidence_contract_version": evidence_contract["version"],
        "worker_schema": schema_doc["schema"],
        "worker_schema_version": schema_doc["version"],
        "dossier_schema": schema_doc["dossier_schema"],
        "dossier_schema_version": schema_doc["dossier_schema_version"],
        "worker_prompt_revision": evidence_contract["worker_prompt_revision"],
    }


def _json_int(value):
    return type(value) is int


def _require_fields(obj, fields, label):
    if not isinstance(obj, dict):
        raise ValueError(f"{label} must be an object")
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ValueError(f"{label} is missing required fields: {', '.join(missing)}")


def _walk(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key, child
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _validate_no_raw_body_like_payload(dossier):
    for path, key, _ in _walk(dossier):
        if str(key).lower() in _RAW_BODY_LIKE_KEYS:
            raise ValueError(f"raw review/post body-like field is forbidden at {path}.{key}")


def _normalize_domain(value):
    text = str(value or "").strip().lower().rstrip(".")
    if text.startswith("www."):
        text = text[4:]
    return text


def _source_ref(source):
    url = source.get("url")
    public_ref = source.get("public_ref")
    if bool(url) == bool(public_ref):
        raise ValueError("provenance source must contain exactly one of url or public_ref")
    return str(url or public_ref)


def _validate_publication_date(value, generated_date, label):
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}.publication_date must be YYYY-MM-DD or null")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}.publication_date must be YYYY-MM-DD or null") from exc
    if parsed > generated_date + timedelta(days=1):
        raise ValueError(f"{label}.publication_date cannot be materially future-dated")
    return parsed


def _validate_source(source, index, enums, schema_doc, generated_date, evidence_contract):
    label = f"provenance.sources[{index}]"
    _require_fields(source, schema_doc["provenance_source_required_fields"], label)
    allowed = set(schema_doc["provenance_source_allowed_fields"])
    extras = sorted(set(source) - allowed)
    if extras:
        raise ValueError(f"{label} contains unsupported fields: {', '.join(extras)}")

    source_id = source.get("source_id")
    if not isinstance(source_id, str) or not 1 <= len(source_id) <= 80:
        raise ValueError(f"{label}.source_id is invalid")
    source_type = source.get("source_type")
    if source_type not in enums["source_type"]:
        raise ValueError(f"{label}.source_type is invalid")
    domain = _normalize_domain(source.get("domain"))
    if not domain or not _DOMAIN_RE.fullmatch(domain) or "." not in domain:
        raise ValueError(f"{label}.domain is invalid")

    ref = _source_ref(source)
    if source.get("url"):
        parsed = urlparse(source["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"{label}.url must be an HTTPS public URL")
        if _normalize_domain(parsed.hostname) != domain:
            raise ValueError(f"{label}.domain must match URL host")
    elif not isinstance(source.get("public_ref"), str) or not 3 <= len(source["public_ref"]) <= 500:
        raise ValueError(f"{label}.public_ref is invalid")

    _validate_publication_date(source.get("publication_date"), generated_date, label)
    if source.get("language") not in enums["source_language"]:
        raise ValueError(f"{label}.language is invalid")
    if source.get("freshness") not in enums["source_freshness"]:
        raise ValueError(f"{label}.freshness is invalid")
    role = source.get("evidence_role")
    if role not in enums["source_evidence_role"]:
        raise ValueError(f"{label}.evidence_role is invalid")
    if role == "current_state" and source.get("freshness") != "recent":
        raise ValueError(f"{label} current_state evidence must be classified recent")
    if type(source.get("player_feedback")) is not bool:
        raise ValueError(f"{label}.player_feedback must be JSON boolean")

    player_types = set(evidence_contract["source_policy"]["player_feedback_source_types"])
    context_types = set(evidence_contract["source_policy"]["context_only_source_types"])
    if source_type in player_types and source["player_feedback"] is not True:
        raise ValueError(f"{label} player-feedback source type must be marked player_feedback=true")
    if source_type in context_types and source["player_feedback"] is not False:
        raise ValueError(f"{label} context-only source cannot be marked player feedback")
    return source_id, ref


def _validate_game_identity(identity, dossier, source_map, enums, schema_doc, generated):
    _require_fields(
        identity,
        ("work_title", "release_year", "resolution_status", "identity_source_ids", "corroborators"),
        "game_identity",
    )
    if identity["work_title"] != dossier["title"]:
        raise ValueError("game_identity.work_title must exactly equal dossier title")
    release_year = identity["release_year"]
    rule = schema_doc["integer_rules"]["release_year"]
    if not _json_int(release_year) or not rule["minimum"] <= release_year <= rule["maximum"]:
        raise ValueError("game_identity.release_year must be a canonical JSON integer in range")
    if release_year > generated.year + 1:
        raise ValueError("game_identity.release_year is implausibly future-dated")
    if identity["resolution_status"] not in enums["identity_resolution_status"]:
        raise ValueError("game identity is not resolved")

    source_ids = identity["identity_source_ids"]
    if not isinstance(source_ids, list) or not source_ids or len(source_ids) != len(set(source_ids)):
        raise ValueError("game_identity.identity_source_ids must be a non-empty unique list")
    if any(source_id not in source_map for source_id in source_ids):
        raise ValueError("game identity references unknown provenance source")
    if not any(source_map[source_id].get("evidence_role") == "identity" for source_id in source_ids):
        raise ValueError("game identity requires an identity-role provenance source")

    corroborators = identity["corroborators"]
    if not isinstance(corroborators, list) or not corroborators:
        raise ValueError("game identity requires at least one corroborator")
    seen = set()
    has_appid = False
    for index, item in enumerate(corroborators):
        _require_fields(item, ("kind", "value"), f"game_identity.corroborators[{index}]")
        kind = item["kind"]
        value = item["value"]
        if kind not in enums["identity_corroborator_kind"] or not isinstance(value, str) or not value.strip():
            raise ValueError("game identity corroborator is invalid")
        key = (kind, value)
        if key in seen:
            raise ValueError("game identity contains duplicate corroborator")
        seen.add(key)
        if kind == "appid" and value == dossier["appid"]:
            has_appid = True
    if not has_appid:
        raise ValueError("game identity must corroborate the exact work-item appid")


def _validate_observations(dossier, source_map, enums, schema_doc):
    observations = dossier.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("dossier observations must be a non-empty list")
    seen = set()
    recurrence_min = schema_doc["observation_invariants"]["recurrence_minimum_mentions"]
    for index, observation in enumerate(observations):
        _require_fields(
            observation,
            ("category", "statement", "sentiment", "recurrence", "mention_count", "evidence_languages", "evidence_status", "source_ids"),
            f"observation {index}",
        )
        if observation["category"] not in enums["observation_category"]:
            raise ValueError(f"observation {index} has unsupported category")
        statement = observation["statement"]
        if not isinstance(statement, str) or not 4 <= len(statement.strip()) <= 600:
            raise ValueError(f"observation {index} statement is missing or too long")
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
        if not isinstance(languages, list) or not languages or any(x not in enums["evidence_languages"] for x in languages):
            raise ValueError(f"observation {index} evidence_languages are invalid")
        source_ids = observation["source_ids"]
        if not isinstance(source_ids, list) or not source_ids or len(source_ids) != len(set(source_ids)):
            raise ValueError(f"observation {index} source_ids must be a non-empty unique list")
        if any(source_id not in source_map for source_id in source_ids):
            raise ValueError(f"observation {index} references unknown provenance source")
        referenced = [source_map[source_id] for source_id in source_ids]

        status = observation["evidence_status"]
        if status not in enums["evidence_status"]:
            raise ValueError(f"observation {index} evidence_status is invalid")
        if status == "current" and not any(s["evidence_role"] == "current_state" and s["freshness"] == "recent" for s in referenced):
            raise ValueError(f"observation {index} current claim lacks recent current-state evidence")
        if status == "historical":
            if not any(s["evidence_role"] == "historical" for s in referenced):
                raise ValueError(f"observation {index} historical claim lacks historical evidence")
            if not any(s["evidence_role"] == "current_state" and s["freshness"] == "recent" for s in referenced):
                raise ValueError(f"observation {index} historical/fixed claim lacks recent current-state check")
        if status == "durable" and not any(s["evidence_role"] == "durable_trait" for s in referenced):
            raise ValueError(f"observation {index} durable claim lacks durable-trait evidence")

        source_languages = {s["language"] for s in referenced}
        if "russian" in languages and not source_languages.intersection({"russian", "mixed"}):
            raise ValueError(f"observation {index} claims Russian evidence without Russian source")
        if "non_russian" in languages and not source_languages.intersection({"non_russian", "mixed"}):
            raise ValueError(f"observation {index} claims non-Russian evidence without non-Russian source")

        digest = canonical_sha256(observation)
        if digest in seen:
            raise ValueError("dossier contains an exact duplicate observation")
        seen.add(digest)
    return observations


def _validate_conflicts(dossier, source_map, enums):
    conflicts = dossier.get("conflicts")
    if not isinstance(conflicts, list):
        raise ValueError("dossier conflicts must be a list")
    for index, conflict in enumerate(conflicts):
        _require_fields(conflict, ("statement", "recurrence", "source_ids"), f"conflict {index}")
        if not isinstance(conflict["statement"], str) or not 4 <= len(conflict["statement"].strip()) <= 600:
            raise ValueError(f"conflict {index} statement is invalid")
        if conflict["recurrence"] not in enums["recurrence"]:
            raise ValueError(f"conflict {index} recurrence is invalid")
        source_ids = conflict["source_ids"]
        if not isinstance(source_ids, list) or not source_ids or len(source_ids) != len(set(source_ids)):
            raise ValueError(f"conflict {index} source_ids are invalid")
        if any(source_id not in source_map for source_id in source_ids):
            raise ValueError(f"conflict {index} references unknown provenance source")


def validate_dossier_strict(
    dossier,
    contract,
    *,
    expected_appid=None,
    expected_title=None,
    expected_ttl_days=None,
    now=None,
    schema_doc=None,
    evidence_contract=None,
):
    """Validate the active V2 web-evidence dossier and all prior hardening invariants."""
    schema_doc = schema_doc or load_worker_schema()
    evidence_contract = evidence_contract or load_web_evidence_contract()
    if schema_doc.get("evidence_contract") != evidence_contract["schema"] or schema_doc.get("evidence_contract_version") != evidence_contract["version"]:
        raise ValueError("worker schema and web evidence contract binding mismatch")
    _require_fields(dossier, schema_doc["required_top_level_fields"], "dossier")
    if "review_sample" in dossier:
        raise ValueError("legacy review_sample payload is forbidden by the active web-evidence schema")

    if dossier.get("schema") != schema_doc["dossier_schema"]:
        raise ValueError("unsupported web evidence dossier schema")
    if not _json_int(dossier.get("schema_version")) or dossier["schema_version"] != schema_doc["dossier_schema_version"]:
        raise ValueError("dossier schema_version must be canonical JSON integer 2")

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

    summary = dossier.get("summary")
    if not isinstance(summary, str) or not 20 <= len(summary.strip()) <= 1200:
        raise ValueError("dossier neutral summary is missing or too long")

    provenance = dossier.get("provenance")
    _require_fields(provenance, ("sources",), "provenance")
    if set(provenance) != {"sources"}:
        raise ValueError("provenance may contain only compact source records")
    sources = provenance["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("provenance.sources must be a non-empty list")
    enums = schema_doc["enums"]
    source_map = {}
    refs = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"provenance.sources[{index}] must be an object")
        source_id, ref = _validate_source(source, index, enums, schema_doc, generated.date(), evidence_contract)
        if source_id in source_map:
            raise ValueError("provenance source_id values must be unique")
        if ref in refs:
            raise ValueError("duplicate provenance source reference is forbidden")
        refs.add(ref)
        source_map[source_id] = source

    _validate_game_identity(dossier.get("game_identity"), dossier, source_map, enums, schema_doc, generated)
    observations = _validate_observations(dossier, source_map, enums, schema_doc)
    _validate_conflicts(dossier, source_map, enums)

    evidence = dossier.get("evidence")
    _require_fields(
        evidence,
        ("strategy", "research_state", "source_mix_status", "single_source_reason", "russian_attempt", "overall_strength", "stop_reason"),
        "evidence",
    )
    if set(evidence) != {"strategy", "research_state", "source_mix_status", "single_source_reason", "russian_attempt", "overall_strength", "stop_reason"}:
        raise ValueError("evidence contains unsupported fields")
    if evidence["strategy"] not in enums["research_strategy"]:
        raise ValueError("evidence strategy is invalid")
    if evidence["research_state"] not in enums["research_state"]:
        raise ValueError("only semantically sufficient evidence may be persisted")
    if evidence["source_mix_status"] not in enums["source_mix_status"]:
        raise ValueError("source_mix_status is invalid")
    if evidence["russian_attempt"] not in enums["russian_attempt_status"]:
        raise ValueError("russian_attempt status is invalid")
    if evidence["overall_strength"] not in enums["overall_strength"]:
        raise ValueError("overall_strength is invalid")
    if evidence["stop_reason"] not in enums["research_stop_reason"]:
        raise ValueError("evidence stop_reason is invalid")

    player_sources = [source for source in sources if source["player_feedback"] is True]
    if not player_sources:
        raise ValueError("at least one player-feedback source is required")
    player_refs = {_source_ref(source) for source in player_sources}
    if evidence["source_mix_status"] == "multi_source":
        if len(player_refs) < 2:
            raise ValueError("multi_source evidence requires at least two distinct player source references")
        if evidence["single_source_reason"] is not None:
            raise ValueError("multi_source evidence must not carry a single-source reason")
    else:
        reason = evidence["single_source_reason"]
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
            raise ValueError("single_source_only evidence requires a compact reason")

    if evidence["russian_attempt"] == "found_and_used":
        ru_ids = {
            source["source_id"] for source in player_sources
            if source["language"] in {"russian", "mixed"}
        }
        if not ru_ids:
            raise ValueError("russian found_and_used requires Russian player-feedback provenance")
        if not any(ru_ids.intersection(set(observation["source_ids"])) for observation in observations):
            raise ValueError("russian found_and_used requires Russian evidence used by an observation")

    _validate_no_raw_body_like_payload(dossier)
    _validate_no_raw_or_personal_payload(dossier)
    return dossier


def dossier_state_strict(dossier, contract, *, now=None, expected_appid=None, expected_title=None, expected_ttl_days=None):
    if dossier is None:
        return "missing"
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    validate_dossier_strict(
        dossier,
        contract,
        expected_appid=expected_appid,
        expected_title=expected_title,
        expected_ttl_days=expected_ttl_days,
        now=now_utc,
    )
    expires = parse_utc(dossier["expires_at_utc"])
    return "fresh" if now_utc < expires else "stale"


def validate_dossiers_against_expected_items(
    dossiers,
    expected_items,
    contract,
    *,
    expected_ttl_days,
    now=None,
    schema_doc=None,
    evidence_contract=None,
):
    if not isinstance(dossiers, list) or not isinstance(expected_items, list):
        raise ValueError("dossiers and expected items must be lists")
    if len(dossiers) != len(expected_items):
        raise ValueError("dossier count does not match exact prepared item count")
    schema_doc = schema_doc or load_worker_schema()
    evidence_contract = evidence_contract or load_web_evidence_contract()
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
            evidence_contract=evidence_contract,
        ))
    return validated
