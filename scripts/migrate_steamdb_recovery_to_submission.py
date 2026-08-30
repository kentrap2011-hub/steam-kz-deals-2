#!/usr/bin/env python3
import json
from pathlib import Path

MANIFEST = Path("data/cache/steamdb_miss_manifest.json")
RECOVERY = Path("data/cache/steamdb_runtime_progress.json")
OUT_DIR = Path("data/inbox/steamdb_runtime")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
source_sha = manifest.get("source_validation_blob_sha")
if not source_sha or recovery.get("source_validation_blob_sha") != source_sha:
    raise SystemExit("Recovery ledger is not bound to the current SteamDB manifest")
expected = {item["key"] for item in manifest.get("misses") or []}
results = []

for key, value in (recovery.get("confirmed_min_kzt") or {}).items():
    if key not in expected:
        raise SystemExit(f"Recovery confirmed key outside manifest: {key}")
    result = {"key": key, "status": "confirmed_min", "historical_min_kzt": value}
    if key in (recovery.get("special_evidence") or {}):
        result["special_evidence"] = recovery["special_evidence"][key]
    results.append(result)

for key in recovery.get("previously_free") or []:
    if key not in expected:
        raise SystemExit(f"Recovery free key outside manifest: {key}")
    results.append({"key": key, "status": "previously_free", "historical_min_kzt": 0})

for key, code in (recovery.get("unavailable_exact_history") or {}).items():
    if key not in expected:
        raise SystemExit(f"Recovery unavailable key outside manifest: {key}")
    results.append({"key": key, "status": "unavailable_exact_history", "evidence_code": code})

for key, reason in (recovery.get("transient_failures") or {}).items():
    if key not in expected:
        raise SystemExit(f"Recovery transient key outside manifest: {key}")
    if not any(item["key"] == key and item["status"] != "blocked_or_failure" for item in results):
        results.append({"key": key, "status": "blocked_or_failure", "failure_code": reason})

seen = set()
for result in results:
    key = result["key"]
    if key in seen:
        raise SystemExit(f"Recovery migration produced duplicate key: {key}")
    seen.add(key)

submission = {
    "schema_version": 1,
    "purpose": "steamdb_runtime_submission",
    "source_validation_blob_sha": source_sha,
    "submitted_at_utc": recovery.get("updated_at_utc"),
    "producer": "one_time_recovery_migration",
    "migration_source": "data/cache/steamdb_runtime_progress.json",
    "results": results,
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
out = OUT_DIR / f"recovery-migration-{source_sha[:12]}.json"
out.write_text(json.dumps(submission, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "output": str(out),
    "result_count": len(results),
    "resolved_count": len([x for x in results if x["status"] != "blocked_or_failure"]),
    "transient_count": len([x for x in results if x["status"] == "blocked_or_failure"]),
}, ensure_ascii=False, indent=2))
