#!/usr/bin/env python3
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

DOSSIER_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-V1"
WORK_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-WORK-V1"
SUBMISSION_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-SUBMISSION-V1"
SEMANTIC_INPUT_SCHEMA = "TASTE-SEMANTIC-DOSSIER-INPUT-V1"
PIN_SCHEMA = "TASTE-PINNED-WORK-UNIT-V1"
CONTRACT_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V1"

_ALLOWED_RECURRENCE = {"strong", "moderate", "limited", "anecdotal"}
_ALLOWED_SENTIMENT = {"positive", "negative", "mixed", "neutral"}
_ALLOWED_CATEGORIES = {
    "mechanics", "structure", "pacing", "progression", "repetition", "difficulty",
    "friction", "multiplayer", "coop", "localization", "translation", "voice",
    "font", "encoding", "regional", "other",
}
_ALLOWED_EVIDENCE_LANG = {"russian", "non_russian", "mixed", "store", "store_and_reviews"}
_RAW_REVIEW_KEYS = {"raw_reviews", "review_text", "review_body", "review_bodies", "reviews_raw", "usernames", "authors"}
_FORBIDDEN_PERSONAL_KEYS = {
    "fit_score", "personal_fit", "include", "exclude", "buy_now", "purchase_urgency", "price", "discount",
}
_FORBIDDEN_PERSONAL_PATTERNS = [
    re.compile(r"\bдмитри[йяюем]\b", re.I),
    re.compile(r"\bподойд[её]т\s+(вам|тебе|пользователю)\b", re.I),
    re.compile(r"\bвам\s+(понравится|не понравится)\b", re.I),
    re.compile(r"\buser\s+will\s+(like|dislike)\b", re.I),
    re.compile(r"\bpersonal\s+fit\b", re.I),
    re.compile(r"\bbuy\s+now\b", re.I),
]
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_sha256(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_utc(value):
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp must be a non-empty ISO-8601 string")
    text = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def utc_iso(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _scope_policy(contract):
    scope = contract.get("scope") or {}
    source = scope.get("source")
    markers = scope.get("taste_semantic_work_required_any")
    if source != "full_current_canonical_taste_queue":
        raise ValueError("Dossier contract full Taste backlog scope source is missing or invalid")
    if not isinstance(markers, list) or not markers or any(not isinstance(x, str) or not x for x in markers):
        raise ValueError("Dossier contract Taste semantic work eligibility is missing or invalid")
    return scope


def resolve_checkpoint_size(contract):
    checkpoint = contract.get("checkpointing") or {}
    size = checkpoint.get("checkpoint_size")
    if checkpoint.get("owner") != "github_control_plane":
        raise ValueError("Dossier checkpoint ownership contract is missing or invalid")
    if checkpoint.get("semantics") != "durability_boundary_not_quota":
        raise ValueError("Dossier checkpoint semantics are missing or invalid")
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Dossier checkpoint size is invalid")
    if checkpoint.get("ready_condition") != "remaining_required_count_zero":
        raise ValueError("Dossier checkpoint ready condition is missing or invalid")
    return size


def load_contract(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema") != CONTRACT_SCHEMA or doc.get("version") != 1 or doc.get("status") != "active":
        raise ValueError("Steam review dossier contract is missing, stale or unsupported")
    freshness = doc.get("freshness") or {}
    default_ttl = freshness.get("default_ttl_days")
    if not isinstance(default_ttl, int) or default_ttl <= 0:
        raise ValueError("Dossier contract default TTL is invalid")
    _scope_policy(doc)
    resolve_checkpoint_size(doc)
    return doc


def resolve_ttl_days(contract, requested=None):
    f = contract["freshness"]
    ttl = f["default_ttl_days"] if requested is None else int(requested)
    if ttl < int(f["min_ttl_days"]) or ttl > int(f["max_ttl_days"]):
        raise ValueError("Requested dossier TTL is outside canonical contract bounds")
    return ttl


def _walk(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key, child
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from _walk(child, f"{path}[{i}]")


def _validate_no_raw_or_personal_payload(dossier):
    for path, key, value in _walk(dossier):
        lowered = str(key).lower()
        if lowered in _RAW_REVIEW_KEYS:
            raise ValueError(f"Raw review archive field is forbidden at {path}.{key}")
        if lowered in _FORBIDDEN_PERSONAL_KEYS:
            raise ValueError(f"Personal/commercial decision field is forbidden at {path}.{key}")
        if isinstance(value, str):
            if len(value) > 1200:
                raise ValueError(f"Dossier string is too long for compact synthesis at {path}.{key}")
            for pattern in _FORBIDDEN_PERSONAL_PATTERNS:
                if pattern.search(value):
                    raise ValueError(f"Personalized conclusion is forbidden at {path}.{key}")


def _validate_observation(obs, index):
    if not isinstance(obs, dict):
        raise ValueError(f"observation {index} must be an object")
    if obs.get("category") not in _ALLOWED_CATEGORIES:
        raise ValueError(f"observation {index} has unsupported category")
    statement = obs.get("statement")
    if not isinstance(statement, str) or not 4 <= len(statement.strip()) <= 600:
        raise ValueError(f"observation {index} statement is missing or too long")
    if obs.get("sentiment") not in _ALLOWED_SENTIMENT:
        raise ValueError(f"observation {index} sentiment is invalid")
    if obs.get("recurrence") not in _ALLOWED_RECURRENCE:
        raise ValueError(f"observation {index} recurrence is invalid")
    mention_count = obs.get("mention_count")
    if not isinstance(mention_count, int) or mention_count < 1:
        raise ValueError(f"observation {index} mention_count must be positive")
    languages = obs.get("evidence_languages")
    if not isinstance(languages, list) or not languages or any(x not in _ALLOWED_EVIDENCE_LANG for x in languages):
        raise ValueError(f"observation {index} evidence_languages are invalid")
    if obs["recurrence"] == "strong" and mention_count < 5:
        raise ValueError(f"observation {index} overstates strong recurrence")
    if obs["recurrence"] == "moderate" and mention_count < 3:
        raise ValueError(f"observation {index} overstates moderate recurrence")
    if obs["recurrence"] == "limited" and mention_count < 2:
        raise ValueError(f"observation {index} overstates limited recurrence")
    if obs["recurrence"] == "anecdotal" and mention_count != 1:
        raise ValueError(f"observation {index} anecdotal recurrence must be one mention")


def _validate_review_sample(sample, contract):
    if not isinstance(sample, dict):
        raise ValueError("review_sample must be an object")
    ru = sample.get("sampled_russian")
    non_ru = sample.get("sampled_non_russian")
    total = sample.get("sampled_total")
    for name, value in (("sampled_russian", ru), ("sampled_non_russian", non_ru), ("sampled_total", total)):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"review_sample.{name} must be a non-negative integer")
    if ru + non_ru != total:
        raise ValueError("review sample lane counts do not sum to sampled_total")
    sampling = contract["sampling"]
    if ru > sampling["max_russian_reviews"] or non_ru > sampling["max_non_russian_reviews"] or total > sampling["max_total_reviews"]:
        raise ValueError("review sample exceeds canonical adaptive ceiling")
    lanes = sample.get("lanes")
    if not isinstance(lanes, list) or {x.get("language_scope") for x in lanes if isinstance(x, dict)} != {"russian", "non_russian"}:
        raise ValueError("both Russian and non-Russian review lanes must be attempted and recorded")
    for lane in lanes:
        if not isinstance(lane.get("sampled"), int) or lane["sampled"] < 0:
            raise ValueError("lane sampled count is invalid")
        if not isinstance(lane.get("batches"), int) or lane["batches"] < 0:
            raise ValueError("lane batch count is invalid")
        if not isinstance(lane.get("stop_reason"), str) or not lane["stop_reason"]:
            raise ValueError("lane stop_reason is required")
    if sample.get("strategy") != "adaptive_stability":
        raise ValueError("review sampling strategy must be adaptive_stability")
    digest = sample.get("sample_ids_sha256")
    if not isinstance(digest, str) or not _HEX64.match(digest):
        raise ValueError("review sample identifier digest is required")


def validate_dossier(dossier, contract, *, expected_appid=None, expected_ttl_days=None):
    if not isinstance(dossier, dict) or dossier.get("schema") != DOSSIER_SCHEMA or dossier.get("schema_version") != 1:
        raise ValueError("unsupported Steam review dossier schema")
    appid = str(dossier.get("appid") or "")
    if not appid.isdigit():
        raise ValueError("dossier appid must be numeric")
    if expected_appid is not None and appid != str(expected_appid):
        raise ValueError("dossier appid does not match prepared work scope")
    title = dossier.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > 300:
        raise ValueError("dossier title is missing or invalid")
    ttl = resolve_ttl_days(contract, dossier.get("ttl_days"))
    if expected_ttl_days is not None and ttl != int(expected_ttl_days):
        raise ValueError("dossier TTL does not match prepared work manifest")
    generated = parse_utc(dossier.get("generated_at_utc"))
    expires = parse_utc(dossier.get("expires_at_utc"))
    if expires != generated + timedelta(days=ttl):
        raise ValueError("dossier expiry must equal generated_at + ttl_days")
    summary = dossier.get("summary")
    if not isinstance(summary, str) or not 20 <= len(summary.strip()) <= 1200:
        raise ValueError("dossier neutral summary is missing or too long")
    observations = dossier.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("dossier observations must be a non-empty list")
    for i, obs in enumerate(observations):
        _validate_observation(obs, i)
    conflicts = dossier.get("conflicts")
    if not isinstance(conflicts, list):
        raise ValueError("dossier conflicts must be a list")
    for i, conflict in enumerate(conflicts):
        if not isinstance(conflict, dict) or not isinstance(conflict.get("statement"), str) or not conflict["statement"].strip():
            raise ValueError(f"conflict {i} is invalid")
        if conflict.get("recurrence") not in _ALLOWED_RECURRENCE:
            raise ValueError(f"conflict {i} recurrence is invalid")
    _validate_review_sample(dossier.get("review_sample"), contract)
    provenance = dossier.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("dossier provenance is required")
    store = provenance.get("store_description")
    reviews = provenance.get("steam_reviews")
    if not isinstance(store, dict) or not str(store.get("url") or "").startswith("https://store.steampowered.com/"):
        raise ValueError("Steam store description provenance is required")
    if not isinstance(store.get("content_sha256"), str) or not _HEX64.match(store["content_sha256"]):
        raise ValueError("store description content hash is required")
    if not isinstance(reviews, dict) or not str(reviews.get("url") or "").startswith("https://store.steampowered.com/"):
        raise ValueError("Steam review provenance is required")
    _validate_no_raw_or_personal_payload(dossier)
    return dossier


def dossier_state(dossier, contract, *, now=None, expected_appid=None):
    if dossier is None:
        return "missing"
    validate_dossier(dossier, contract, expected_appid=expected_appid)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    generated = parse_utc(dossier["generated_at_utc"])
    expires = parse_utc(dossier["expires_at_utc"])
    if generated > now + timedelta(minutes=5):
        return "invalid_future"
    return "fresh" if now < expires else "stale"


def dossier_path(store_dir, appid):
    return Path(store_dir) / f"App_{appid}.json"


def load_dossier_if_present(store_dir, appid):
    path = dossier_path(store_dir, appid)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def validate_pin(pin):
    if not isinstance(pin, dict) or pin.get("schema") != PIN_SCHEMA or pin.get("status") != "active":
        raise ValueError("active canonical Taste pin is required")
    rows = pin.get("ordered_rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("active Taste pin has no ordered rows")
    pin_sha = pin.get("ordered_work_unit_sha256")
    if not isinstance(pin_sha, str) or not _HEX64.match(pin_sha):
        raise ValueError("active Taste pin has no canonical ordered_work_unit_sha256")
    for row in rows:
        if not isinstance(row, dict) or not str(row.get("appid") or "").isdigit() or not row.get("key"):
            raise ValueError("active Taste pin row is malformed")
    return pin


def _row_requires_dossier(work_required, contract):
    if not isinstance(work_required, list) or not work_required:
        raise ValueError("canonical Taste queue row has no canonical work_required")
    markers = set(_scope_policy(contract)["taste_semantic_work_required_any"])
    return any(isinstance(item, str) and item in markers for item in work_required)


def canonical_dossier_scope_rows(queue_rows, contract):
    """Project full eligible Taste backlog to one deterministic dossier row per appid."""
    if not isinstance(queue_rows, list):
        raise ValueError("canonical Taste queue rows must be a list")
    out = []
    seen = set()
    for index, row in enumerate(queue_rows):
        if not isinstance(row, dict):
            raise ValueError(f"canonical Taste queue row {index} is malformed")
        appid = str(row.get("appid") or "")
        key = row.get("taste_subject_key") if "taste_subject_key" in row else row.get("key")
        work = row.get("work_required")
        if not appid.isdigit() or not isinstance(key, str) or not key:
            raise ValueError(f"canonical Taste queue row {index} lacks appid/taste subject identity")
        try:
            eligible = _row_requires_dossier(work, contract)
        except ValueError as exc:
            raise ValueError(f"canonical Taste queue row {index} has no canonical work_required") from exc
        if not eligible:
            continue
        if appid in seen:
            continue
        seen.add(appid)
        out.append({
            "key": key,
            "appid": appid,
            "taste_fingerprint": row.get("taste_fingerprint"),
            "candidate_context_sha256": row.get("candidate_context_sha256"),
            "work_required": list(work),
        })
    return out


def build_work_manifest(queue_rows, contract, store_dir, *, now=None, ttl_days=None):
    scope_rows = canonical_dossier_scope_rows(queue_rows, contract)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ttl = resolve_ttl_days(contract, ttl_days)
    checkpoint_size = resolve_checkpoint_size(contract)
    eligible_row_count = sum(
        1 for row in queue_rows
        if isinstance(row, dict) and _row_requires_dossier(row.get("work_required"), contract)
    )
    items = []
    all_required = []
    for row in scope_rows:
        appid = row["appid"]
        path = dossier_path(store_dir, appid)
        existing = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state(existing, contract, now=now, expected_appid=appid)
        except ValueError:
            state = "invalid"
        item = {"key": row["key"], "appid": appid, "dossier_path": path.as_posix(), "state": state}
        if existing and state == "fresh":
            item["generated_at_utc"] = existing["generated_at_utc"]
            item["expires_at_utc"] = existing["expires_at_utc"]
            item["dossier_sha256"] = canonical_sha256(existing)
        else:
            item["reason"] = "refresh_required" if state in {"stale", "invalid", "invalid_future"} else "missing_dossier"
            all_required.append({"key": row["key"], "appid": appid, "dossier_path": path.as_posix(), "reason": item["reason"]})
        items.append(item)

    required = all_required[:checkpoint_size]
    remaining_required_count = len(all_required)
    source_queue_sha256 = canonical_sha256(queue_rows)
    scope_source = _scope_policy(contract)["source"]
    full_required_sha256 = canonical_sha256(all_required)
    checkpoint = {
        "owner": "github_control_plane",
        "semantics": "durability_boundary_not_quota",
        "checkpoint_size": checkpoint_size,
        "item_count": len(required),
        "remaining_required_count": remaining_required_count,
        "remaining_after_checkpoint_count": remaining_required_count - len(required),
        "full_required_sha256": full_required_sha256,
        "continue_same_invocation": remaining_required_count > len(required),
        "is_final_checkpoint": bool(required) and len(required) == remaining_required_count,
        "resume_rule": "rebuild_from_canonical_queue_and_current_dossier_store",
    }
    base = {
        "schema": WORK_SCHEMA,
        "schema_version": 1,
        "status": "work_required" if all_required else "ready_from_fresh_cache",
        "prepared_at_utc": utc_iso(now),
        "ttl_days": ttl,
        "scope_source": scope_source,
        "source_queue_sha256": source_queue_sha256,
        "source_row_count": len(queue_rows),
        "eligible_row_count": eligible_row_count,
        "excluded_row_count": len(queue_rows) - eligible_row_count,
        "unique_appid_count": len(scope_rows),
        "deduplicated_row_count": eligible_row_count - len(scope_rows),
        "ordered_appids": [row["appid"] for row in scope_rows],
        "ordered_keys": [row["key"] for row in scope_rows],
        "items": items,
        "required_total_count": remaining_required_count,
        "full_required_sha256": full_required_sha256,
        "full_backlog_complete": remaining_required_count == 0,
        "required_items": required,
        "checkpoint": checkpoint,
        "sampling_policy": contract["sampling"],
    }
    base["scope_sha256"] = canonical_sha256({
        "schema": base["schema"],
        "ttl_days": ttl,
        "scope_source": scope_source,
        "source_queue_sha256": source_queue_sha256,
        "ordered_appids": base["ordered_appids"],
        "required_total_count": remaining_required_count,
        "full_required_sha256": full_required_sha256,
        "checkpoint_size": checkpoint_size,
        "required_items": required,
    })
    return base


def _validate_manifest_checkpoint(manifest, contract):
    if not isinstance(manifest, dict) or manifest.get("schema") != WORK_SCHEMA or manifest.get("schema_version") != 1:
        raise ValueError("GitHub-prepared dossier work manifest is missing or unsupported")
    checkpoint_size = resolve_checkpoint_size(contract)
    checkpoint = manifest.get("checkpoint")
    required = manifest.get("required_items")
    if not isinstance(checkpoint, dict) or not isinstance(required, list):
        raise ValueError("GitHub-prepared dossier checkpoint metadata is missing")
    if checkpoint.get("owner") != "github_control_plane" or checkpoint.get("semantics") != "durability_boundary_not_quota":
        raise ValueError("GitHub-prepared dossier checkpoint ownership/semantics are invalid")
    if checkpoint.get("checkpoint_size") != checkpoint_size or len(required) > checkpoint_size:
        raise ValueError("GitHub-prepared dossier checkpoint size is invalid")
    required_total_count = manifest.get("required_total_count")
    if not isinstance(required_total_count, int) or required_total_count < len(required):
        raise ValueError("GitHub-prepared dossier full-required count is invalid")
    full_required_sha256 = manifest.get("full_required_sha256")
    if not isinstance(full_required_sha256, str) or not _HEX64.match(full_required_sha256):
        raise ValueError("GitHub-prepared dossier full-required binding is invalid")
    if checkpoint.get("full_required_sha256") != full_required_sha256:
        raise ValueError("GitHub-prepared dossier checkpoint/full-scope binding mismatch")
    if checkpoint.get("item_count") != len(required):
        raise ValueError("GitHub-prepared dossier checkpoint item count mismatch")
    if checkpoint.get("remaining_required_count") != required_total_count:
        raise ValueError("GitHub-prepared dossier remaining-required count mismatch")
    if checkpoint.get("remaining_after_checkpoint_count") != required_total_count - len(required):
        raise ValueError("GitHub-prepared dossier checkpoint remainder mismatch")
    if manifest.get("full_backlog_complete") != (required_total_count == 0):
        raise ValueError("GitHub-prepared dossier full-backlog completion flag mismatch")
    if manifest.get("status") == "work_required":
        if required_total_count <= 0 or not required:
            raise ValueError("work_required manifest must expose a non-empty dossier checkpoint")
    elif manifest.get("status") == "ready_from_fresh_cache":
        if required_total_count != 0 or required:
            raise ValueError("ready dossier manifest cannot expose required checkpoint work")
    else:
        raise ValueError("GitHub-prepared dossier work manifest status is unsupported")
    return required


def validate_submission(submission, manifest, contract):
    if not isinstance(submission, dict) or submission.get("schema") != SUBMISSION_SCHEMA or submission.get("schema_version") != 1:
        raise ValueError("unsupported dossier submission schema")
    required = _validate_manifest_checkpoint(manifest, contract)
    if manifest.get("status") != "work_required":
        raise ValueError("no dossier checkpoint work is currently prepared")
    if submission.get("scope_sha256") != manifest.get("scope_sha256"):
        raise ValueError("dossier submission scope does not match GitHub-prepared work manifest")
    if submission.get("scope_source") != manifest.get("scope_source"):
        raise ValueError("dossier submission scope source mismatch")
    if submission.get("source_queue_sha256") != manifest.get("source_queue_sha256"):
        raise ValueError("dossier submission canonical Taste queue binding mismatch")
    docs = submission.get("dossiers")
    if not isinstance(docs, list):
        raise ValueError("dossier submission must contain a dossiers list")
    expected = [str(x["appid"]) for x in required]
    actual = [str(doc.get("appid") or "") if isinstance(doc, dict) else "" for doc in docs]
    if len(actual) != len(set(actual)):
        raise ValueError("dossier submission contains duplicate appids")
    if actual != expected:
        raise ValueError("dossier submission must exactly cover the GitHub-prepared checkpoint in canonical order")
    validated = []
    for doc, appid in zip(docs, expected):
        validated.append(validate_dossier(doc, contract, expected_appid=appid, expected_ttl_days=manifest["ttl_days"]))
    return validated


def persist_submission(submission, manifest, contract, store_dir):
    docs = validate_submission(submission, manifest, contract)
    persisted = []
    for doc in docs:
        path = dossier_path(store_dir, str(doc["appid"]))
        atomic_write_json(path, doc)
        persisted.append({"appid": str(doc["appid"]), "path": path.as_posix(), "dossier_sha256": canonical_sha256(doc)})
    return persisted


def persist_submission_and_rebuild_work(
    submission,
    manifest,
    contract,
    store_dir,
    queue_rows,
    *,
    manifest_output_path=None,
    now=None,
):
    """Persist one exact checkpoint and deterministically expose the next remaining checkpoint."""
    current_queue_sha256 = canonical_sha256(queue_rows)
    if current_queue_sha256 != manifest.get("source_queue_sha256"):
        raise ValueError("canonical Taste queue changed after dossier work manifest preparation; rebuild work before ingest")
    persisted = persist_submission(submission, manifest, contract, store_dir)
    next_manifest = build_work_manifest(
        queue_rows,
        contract,
        store_dir,
        now=now,
        ttl_days=manifest["ttl_days"],
    )
    if manifest_output_path is not None:
        atomic_write_json(manifest_output_path, next_manifest)
    return persisted, next_manifest


def build_semantic_input(pin, contract, store_dir, *, now=None):
    validate_pin(pin)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    rows = []
    missing = []
    for row in pin["ordered_rows"]:
        appid = str(row["appid"])
        doc = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state(doc, contract, now=now, expected_appid=appid)
        except ValueError as exc:
            state = "invalid"
            missing.append({"key": row["key"], "appid": appid, "state": state, "error": str(exc)})
            continue
        if state != "fresh":
            missing.append({"key": row["key"], "appid": appid, "state": state})
            continue
        rows.append({
            "key": row["key"],
            "appid": appid,
            "taste_fingerprint": row.get("taste_fingerprint"),
            "candidate_context_sha256": row.get("candidate_context_sha256"),
            "work_required": list(row.get("work_required") or []),
            "dossier": doc,
            "dossier_binding": {
                "dossier_sha256": canonical_sha256(doc),
                "generated_at_utc": doc["generated_at_utc"],
                "expires_at_utc": doc["expires_at_utc"],
            },
        })
    if missing:
        raise ValueError("Taste semantic input held: missing/stale/invalid Steam dossier(s): " + json.dumps(missing, ensure_ascii=False))
    out = {
        "schema": SEMANTIC_INPUT_SCHEMA,
        "schema_version": 1,
        "status": "ready_for_taste_semantic_producer",
        "prepared_at_utc": utc_iso(now),
        "pin": {
            "schema": pin["schema"],
            "ordered_work_unit_sha256": pin["ordered_work_unit_sha256"],
            "producer_id": pin.get("producer_id"),
            "producer_generation": pin.get("producer_generation"),
            "profile_identity": pin.get("profile_identity"),
            "bindings": pin.get("bindings"),
        },
        "rows": rows,
    }
    out["semantic_input_sha256"] = canonical_sha256({"pin": out["pin"], "rows": rows})
    return out
