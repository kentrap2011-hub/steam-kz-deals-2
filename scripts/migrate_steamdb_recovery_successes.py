#!/usr/bin/env python3
"""One-time safe migration of already-observed SteamDB recovery successes.

This script deliberately does NOT participate in current runtime completeness.
It imports only successful historical facts from the archived recovery submission,
adds only keys absent from the persistent cache, ignores transient failures, and
never weakens current-snapshot binding in the normal ingest path.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

RECOVERY = Path("data/inbox/steamdb_runtime/recovery-migration-11ac4563c927.json")
CACHE = Path("data/cache/steamdb_history.json")
EXPECTED_PRODUCER = "one_time_recovery_migration"
ALLOWED_UNAVAILABLE = {
    "exact_sub_public_page_no_lowest_recorded_price",
    "exact_entity_public_page_no_kazakhstan_history",
}
SUCCESS_STATUSES = {"confirmed_min", "previously_free", "unavailable_exact_history"}


def die(message: str) -> None:
    raise SystemExit(f"STEAMDB_RECOVERY_MIGRATION_INVALID: {message}")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


recovery = load(RECOVERY)
cache = load(CACHE)

if recovery.get("schema_version") != 1 or recovery.get("purpose") != "steamdb_runtime_submission":
    die("unexpected recovery submission schema/purpose")
if recovery.get("producer") != EXPECTED_PRODUCER:
    die("recovery file is not the explicit one-time migration artifact")
if recovery.get("migration_source") != "data/cache/steamdb_runtime_progress.json":
    die("unexpected recovery migration source")

if cache.get("schema_version") != 2:
    die("persistent SteamDB cache must already be schema 2")
entries = cache.get("entries")
if not isinstance(entries, dict):
    die("persistent cache entries are malformed")

results = recovery.get("results")
if not isinstance(results, list):
    die("recovery results must be a list")

seen = set()
success_rows = 0
failure_rows = 0
added = 0
already_present = 0
status_counts = {}

for row in results:
    if not isinstance(row, dict):
        die("recovery result is not an object")
    key = row.get("key")
    status = row.get("status")
    if not isinstance(key, str) or not (key.startswith("App_") or key.startswith("Sub_")):
        die(f"invalid exact SteamDB key {key!r}")
    suffix = key.split("_", 1)[1]
    if not suffix.isdigit():
        die(f"invalid SteamDB numeric id in {key!r}")
    if key in seen:
        die(f"duplicate recovery key {key}")
    seen.add(key)
    status_counts[status] = status_counts.get(status, 0) + 1

    if status == "blocked_or_failure":
        reason = row.get("failure_code") or row.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            die(f"{key}: blocked_or_failure lacks failure reason")
        failure_rows += 1
        continue

    if status not in SUCCESS_STATUSES:
        die(f"{key}: unsupported recovery status {status!r}")
    success_rows += 1

    # Never overwrite a possibly newer persistent observation with archived data.
    if key in entries:
        already_present += 1
        continue

    steam_type = "app" if key.startswith("App_") else "sub"
    steam_id = suffix
    checked_at = recovery.get("submitted_at_utc")
    new_entry = {
        "key": key,
        "steam_type": steam_type,
        "steam_id": steam_id,
        "status": status,
        "historical_min_kzt": None,
        "checked_at_utc": checked_at,
        "source": "SteamDB",
        "resolution_method": "one_time_recovery_migration",
        "migration_source": recovery.get("migration_source"),
        "migration_source_validation_blob_sha": recovery.get("source_validation_blob_sha"),
    }

    if status == "confirmed_min":
        value = row.get("historical_min_kzt")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            die(f"{key}: confirmed_min requires positive exact KZT value")
        new_entry["historical_min_kzt"] = value
    elif status == "previously_free":
        if row.get("historical_min_kzt", 0) not in (0, 0.0):
            die(f"{key}: previously_free requires zero")
        new_entry["historical_min_kzt"] = 0
    else:
        evidence_code = row.get("evidence_code")
        if evidence_code not in ALLOWED_UNAVAILABLE:
            die(f"{key}: invalid unavailable evidence code {evidence_code!r}")
        new_entry["unavailable_reason"] = evidence_code
        new_entry["resolution_method"] = evidence_code

    special = row.get("special_evidence")
    if special is not None:
        if status != "confirmed_min" or not isinstance(special, dict):
            die(f"{key}: invalid special evidence")
        new_entry["special_evidence"] = special

    entries[key] = new_entry
    added += 1

# A recovery file made from the old runtime progress is expected to contain a real
# successful subset. Refuse a no-op file whose only contents are failures.
if success_rows == 0:
    die("recovery artifact contains no successful observations")

cache["schema_version"] = 2
cache["purpose"] = "persistent_kazakhstan_price_history_cache_for_mailing"
cache["source"] = "SteamDB"
cache["country_code"] = "kz"
cache["currency"] = "KZT"
cache["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
cache["entry_count"] = len(entries)
cache["entries"] = dict(sorted(entries.items()))
CACHE.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

print(json.dumps({
    "recovery_total_rows": len(results),
    "success_rows": success_rows,
    "failure_rows_ignored": failure_rows,
    "added_absent_successes": added,
    "already_present_preserved": already_present,
    "result_cache_entry_count": len(entries),
    "status_counts": status_counts,
}, ensure_ascii=False, indent=2))
