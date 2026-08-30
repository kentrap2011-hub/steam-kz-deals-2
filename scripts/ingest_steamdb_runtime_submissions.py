#!/usr/bin/env python3
import glob
import json
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path("data/cache/steamdb_miss_manifest.json")
INBOX_GLOB = "data/inbox/steamdb_runtime/*.json"
STATE = Path("data/cache/steamdb_runtime_state.json")
WORK = Path("data/cache/steamdb_runtime_work.json")
FINAL = Path("data/cache/steamdb_web_resolutions.json")

ALLOWED_UNAVAILABLE = {
    "exact_sub_public_page_no_lowest_recorded_price",
    "exact_entity_public_page_no_kazakhstan_history",
}
ALLOWED_STATUSES = {
    "confirmed_min",
    "previously_free",
    "unavailable_exact_history",
    "blocked_or_failure",
}


def die(message):
    raise SystemExit(f"STEAMDB_RUNTIME_INGEST_INVALID: {message}")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


manifest = load(MANIFEST)
source_sha = manifest.get("source_validation_blob_sha")
misses = manifest.get("misses") or []
expected = [item.get("key") for item in misses]
expected_set = set(expected)
if not source_sha:
    die("manifest has no source_validation_blob_sha")
if manifest.get("count") != len(expected) or len(expected) != len(expected_set) or None in expected_set:
    die("manifest scope is inconsistent")
manifest_by_key = {item["key"]: item for item in misses}

resolved = {}
transient_history = {}
conflicts = []
matching_submissions = []
submission_events = 0
latest_submitted_at = None


def normalized_success(result):
    status = result["status"]
    key = result["key"]
    if status == "confirmed_min":
        value = result.get("historical_min_kzt")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            die(f"{key}: confirmed_min requires positive historical_min_kzt")
        return {
            "status": status,
            "historical_min_kzt": value,
            "special_evidence": result.get("special_evidence"),
        }
    if status == "previously_free":
        value = result.get("historical_min_kzt", 0)
        if value != 0:
            die(f"{key}: previously_free requires zero")
        return {"status": status, "historical_min_kzt": 0}
    if status == "unavailable_exact_history":
        code = result.get("evidence_code")
        if code not in ALLOWED_UNAVAILABLE:
            die(f"{key}: invalid unavailable evidence code {code!r}")
        return {"status": status, "evidence_code": code}
    raise AssertionError(status)


for filename in sorted(glob.glob(INBOX_GLOB)):
    path = Path(filename)
    submission = load(path)
    if submission.get("schema_version") != 1 or submission.get("purpose") != "steamdb_runtime_submission":
        die(f"{path}: unsupported submission schema/purpose")
    # Inbox is durable across cycles. Old, correctly formed submissions remain archived
    # but are ignored unless they bind to the exact current stage-15 scope.
    if submission.get("source_validation_blob_sha") != source_sha:
        continue
    results = submission.get("results")
    if not isinstance(results, list):
        die(f"{path}: results must be a list")
    seen = set()
    matching_submissions.append(str(path))
    submitted_at = submission.get("submitted_at_utc")
    if isinstance(submitted_at, str) and (latest_submitted_at is None or submitted_at > latest_submitted_at):
        latest_submitted_at = submitted_at

    for result in results:
        if not isinstance(result, dict):
            die(f"{path}: each result must be an object")
        key = result.get("key")
        status = result.get("status")
        if key not in expected_set:
            die(f"{path}: key {key!r} is outside current manifest")
        if key in seen:
            die(f"{path}: duplicate key {key}")
        seen.add(key)
        if status not in ALLOWED_STATUSES:
            die(f"{path}: unsupported status {status!r} for {key}")
        submission_events += 1

        if status == "blocked_or_failure":
            reason = result.get("failure_code") or result.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                die(f"{path}: blocked_or_failure for {key} requires failure_code/reason")
            hist = transient_history.setdefault(key, [])
            hist.append({
                "submission": str(path),
                "submitted_at_utc": submitted_at,
                "failure_code": reason.strip(),
            })
            continue

        candidate = normalized_success(result)
        if key not in resolved:
            resolved[key] = candidate
        elif resolved[key] != candidate:
            conflicts.append({
                "key": key,
                "existing": resolved[key],
                "incoming": candidate,
                "submission": str(path),
            })

resolved_keys = set(resolved)
unresolved = [key for key in expected if key not in resolved_keys]
status = "invalid" if conflicts else ("complete" if not unresolved else "waiting_for_runtime")

state = {
    "schema_version": 1,
    "purpose": "github_derived_steamdb_runtime_state",
    "status": status,
    "source_validation_blob_sha": source_sha,
    "expected_count": len(expected),
    "resolved_count": len(resolved),
    "unresolved_count": len(unresolved),
    "submission_file_count": len(matching_submissions),
    "submission_event_count": submission_events,
    "resolved": {key: resolved[key] for key in expected if key in resolved},
    "unresolved_keys": unresolved,
    "transient_failure_history": {key: transient_history[key] for key in expected if key in transient_history},
    "conflicts": conflicts,
    "derived_at_utc": utc_now(),
}
STATE.parent.mkdir(parents=True, exist_ok=True)
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

work_items = []
for key in unresolved:
    source_item = manifest_by_key[key]
    failures = transient_history.get(key) or []
    work_items.append({
        **source_item,
        "retry": bool(failures),
        "previous_failure_count": len(failures),
        "last_failure_code": failures[-1]["failure_code"] if failures else None,
    })

work = {
    "schema_version": 1,
    "purpose": "steamdb_runtime_work_input",
    "status": "complete" if status == "complete" else ("invalid" if status == "invalid" else "pending"),
    "source_validation_blob_sha": source_sha,
    "expected_count": len(expected),
    "resolved_count": len(resolved),
    "unresolved_count": len(unresolved),
    "items": work_items,
    "derived_at_utc": state["derived_at_utc"],
}
WORK.write_text(json.dumps(work, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Persistence is intentionally independent from stage completion. Every current,
# non-conflicting resolved fact is prepared for validation/checkpoint immediately;
# unresolved keys remain only in GitHub-owned retry state and are never encoded as
# negative cache entries.
if not conflicts and resolved:
    confirmed = {}
    previously_free = []
    unavailable = {}
    special = {}
    for key in expected:
        if key not in resolved:
            continue
        entry = resolved[key]
        if entry["status"] == "confirmed_min":
            confirmed[key] = entry["historical_min_kzt"]
            if entry.get("special_evidence") is not None:
                special[key] = entry["special_evidence"]
        elif entry["status"] == "previously_free":
            previously_free.append(key)
        elif entry["status"] == "unavailable_exact_history":
            unavailable[key] = entry["evidence_code"]
    final = {
        "schema_version": 1,
        "scope_status": "complete" if not unresolved else "partial",
        "source_validation_blob_sha": source_sha,
        "expected_count": len(expected),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "unresolved_keys": unresolved,
        "runtime_attempted_count": len(set(resolved) | set(transient_history)),
        "checked_at_utc": latest_submitted_at or state["derived_at_utc"],
        "confirmed_min_kzt": confirmed,
        "previously_free": previously_free,
        "unavailable_exact_history": unavailable,
        "special_evidence": special,
    }
    FINAL.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "status": status,
    "expected_count": len(expected),
    "resolved_count": len(resolved),
    "unresolved_count": len(unresolved),
    "conflict_count": len(conflicts),
    "submission_file_count": len(matching_submissions),
    "prepared_scope_status": None if conflicts or not resolved else ("complete" if not unresolved else "partial"),
}, ensure_ascii=False, indent=2))

if conflicts:
    raise SystemExit("SteamDB runtime submissions contain conflicting successful outcomes")
