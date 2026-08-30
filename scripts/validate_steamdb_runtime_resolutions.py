#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

CLASSIFICATION = Path("data/cache/steamdb_cache.validation.json")
PREPARED = Path("data/cache/steamdb_web_resolutions.json")
CONTRACT = Path("config/steamdb_lookup_contract.json")
OWNERSHIP = Path("config/execution_ownership_contract.json")
STATE = Path("data/cache/steamdb_runtime_state.json")
OUT = Path("data/cache/steamdb_lookup.validation.json")


def sha(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def die(message):
    raise SystemExit(message)


classification = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
prepared = json.loads(PREPARED.read_text(encoding="utf-8"))
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
ownership = json.loads(OWNERSHIP.read_text(encoding="utf-8"))
state = json.loads(STATE.read_text(encoding="utf-8"))

if classification.get("status") != "complete":
    die("Stage-15 classification is not complete")
if contract.get("contract") != "STEAMDB-TRUE-MISS-LOOKUP-V1" or contract.get("version") != "1.4":
    die("Unexpected SteamDB lookup contract")
if ownership.get("contract") != "PRODUCTION-EXECUTION-OWNERSHIP-V1" or ownership.get("status") != "canonical":
    die("Unexpected production execution ownership contract")
if prepared.get("schema_version") != 1:
    die("Unexpected prepared resolution schema")
if state.get("schema_version") != 1 or state.get("purpose") != "github_derived_steamdb_runtime_state":
    die("Unexpected GitHub-derived SteamDB runtime state")
if state.get("status") == "invalid" or state.get("conflicts"):
    die("GitHub-derived SteamDB runtime state contains conflicts")

steamdb_ownership = contract.get("ownership") or {}
github_ownership = set((steamdb_ownership.get("github_control_plane") or {}).get("owns") or [])
runtime_forbidden = set((steamdb_ownership.get("scheduled_chatgpt_data_plane") or {}).get("must_not_own") or [])
required_github = {
    "exact true-miss manifest and ordering",
    "derived unresolved runtime work input",
    "unresolved/retry state",
    "submission ingestion and conflict detection",
    "completeness accounting",
    "prepared-result validation",
    "canonical steamdb_history persistence",
    "downstream rebuild orchestration",
}
required_runtime_forbidden = {
    "scope discovery",
    "queue construction",
    "ordering policy",
    "retry policy",
    "backlog management",
    "daily quota or batch semantics",
    "canonical cache merge",
    "completion decision",
}
if not required_github.issubset(github_ownership):
    die("SteamDB contract no longer gives GitHub required control-plane ownership")
if not required_runtime_forbidden.issubset(runtime_forbidden):
    die("SteamDB contract no longer constrains ChatGPT runtime ownership")

classification_sha = sha("data/cache/steamdb_cache.validation.json")
if prepared.get("source_validation_blob_sha") != classification_sha:
    die("Prepared SteamDB resolutions are stale versus stage 15")
if state.get("source_validation_blob_sha") != classification_sha:
    die("GitHub runtime state is stale versus stage 15")

misses = classification.get("true_lookup_misses") or []
expected = [x["key"] for x in misses]
expected_set = set(expected)
if len(expected) != len(expected_set):
    die("Duplicate stage-15 true miss key")

state_resolved = state.get("resolved") or {}
state_resolved_keys = set(state_resolved)
state_unresolved = state.get("unresolved_keys") or []
state_unresolved_set = set(state_unresolved)
if len(state_unresolved) != len(state_unresolved_set):
    die("Duplicate unresolved key in GitHub runtime state")
if state_resolved_keys & state_unresolved_set:
    die("GitHub runtime state overlaps resolved and unresolved keys")
if state_resolved_keys | state_unresolved_set != expected_set:
    die("GitHub runtime state does not partition the exact stage-15 scope")
if int(state.get("resolved_count") or 0) != len(state_resolved_keys):
    die("GitHub runtime resolved_count mismatch")
if int(state.get("unresolved_count") or 0) != len(state_unresolved_set):
    die("GitHub runtime unresolved_count mismatch")

expected_scope_status = "complete" if not state_unresolved else "partial"
if prepared.get("scope_status") != expected_scope_status:
    die("Prepared SteamDB scope_status does not match GitHub runtime completeness")
if int(prepared.get("expected_count") or -1) != len(expected):
    die("Prepared SteamDB expected_count mismatch")
if int(prepared.get("resolved_count") or -1) != len(state_resolved_keys):
    die("Prepared SteamDB resolved_count mismatch")
if int(prepared.get("unresolved_count") or -1) != len(state_unresolved_set):
    die("Prepared SteamDB unresolved_count mismatch")
prepared_unresolved = prepared.get("unresolved_keys") or []
if prepared_unresolved != state_unresolved:
    die("Prepared SteamDB unresolved key list does not match GitHub runtime state")

confirmed = prepared.get("confirmed_min_kzt") or {}
previously_free = prepared.get("previously_free") or []
unavailable = prepared.get("unavailable_exact_history") or {}
special = prepared.get("special_evidence") or {}
if not isinstance(confirmed, dict) or not isinstance(previously_free, list) or not isinstance(unavailable, dict) or not isinstance(special, dict):
    die("Prepared SteamDB resolution sections have invalid types")

confirmed_keys = set(confirmed)
free_keys = set(previously_free)
unavailable_keys = set(unavailable)
if len(previously_free) != len(free_keys):
    die("Duplicate previously-free key")
if confirmed_keys & free_keys or confirmed_keys & unavailable_keys or free_keys & unavailable_keys:
    die("Prepared SteamDB status sets overlap")
resolved_set = confirmed_keys | free_keys | unavailable_keys
extra = sorted(resolved_set - expected_set)
if extra:
    die(f"Prepared SteamDB contains non-scope keys: {extra}")
if resolved_set != state_resolved_keys:
    missing_from_prepared = sorted(state_resolved_keys - resolved_set)
    unexpected_prepared = sorted(resolved_set - state_resolved_keys)
    die(
        "Prepared SteamDB resolved set differs from GitHub runtime state: "
        f"missing={missing_from_prepared} unexpected={unexpected_prepared}"
    )
if not set(special).issubset(confirmed_keys):
    die("Special evidence exists for a non-confirmed-min key")

missing = [key for key in expected if key not in resolved_set]
if missing != state_unresolved:
    die("Prepared SteamDB missing set differs from GitHub unresolved order")

registry = []
problems = []
for key in sorted(confirmed_keys):
    try:
        value = float(confirmed[key])
    except Exception:
        value = None
    if value is None or value <= 0:
        problems.append({"key": key, "reason": "confirmed_min_not_positive"})
        continue
    if key.startswith("App_"):
        entity_url = f"https://steamdb.info/app/{key.split('_', 1)[1]}/"
    elif key.startswith("Sub_"):
        entity_url = f"https://steamdb.info/sub/{key.split('_', 1)[1]}/"
    else:
        problems.append({"key": key, "reason": "unsupported_key"})
        continue
    entry = {
        "key": key,
        "provider": "SteamDB",
        "registry_key": f"SteamDB:{key}",
        "result": "confirmed_min",
        "historical_min_kzt": int(value) if value.is_integer() else value,
        "persistable": True,
        "source_url": entity_url,
        "checked_at_utc": prepared.get("checked_at_utc"),
        "resolution_method": "direct_app_kzt_lowest_row",
    }
    if key in special:
        evidence = special[key]
        if not isinstance(evidence, dict) or not evidence.get("method") or not evidence.get("source_urls") or not evidence.get("note"):
            problems.append({"key": key, "reason": "invalid_special_evidence"})
            continue
        entry["resolution_method"] = evidence["method"]
        entry["special_evidence"] = evidence
    registry.append(entry)

for key in sorted(free_keys):
    if not key.startswith("App_"):
        problems.append({"key": key, "reason": "previously_free_non_app_without_special_evidence"})
        continue
    registry.append({
        "key": key,
        "provider": "SteamDB",
        "registry_key": f"SteamDB:{key}",
        "result": "previously_free",
        "historical_min_kzt": 0,
        "persistable": True,
        "source_url": f"https://steamdb.info/app/{key.split('_', 1)[1]}/",
        "checked_at_utc": prepared.get("checked_at_utc"),
        "resolution_method": "direct_app_kzt_lowest_row",
    })

allowed_unavailable_evidence = {
    "exact_sub_public_page_no_lowest_recorded_price",
    "exact_entity_public_page_no_kazakhstan_history",
}
for key in sorted(unavailable_keys):
    evidence_code = unavailable[key]
    if evidence_code not in allowed_unavailable_evidence:
        problems.append({"key": key, "reason": "invalid_unavailable_evidence_code", "evidence_code": evidence_code})
        continue
    kind = "app" if key.startswith("App_") else "sub" if key.startswith("Sub_") else None
    if kind is None:
        problems.append({"key": key, "reason": "unsupported_key"})
        continue
    registry.append({
        "key": key,
        "provider": "SteamDB",
        "registry_key": f"SteamDB:{key}",
        "result": "unavailable_exact_history",
        "historical_min_kzt": None,
        "persistable": True,
        "source_url": f"https://steamdb.info/{kind}/{key.split('_', 1)[1]}/",
        "checked_at_utc": prepared.get("checked_at_utc"),
        "resolution_method": evidence_code,
    })

registry_keys = [x["registry_key"] for x in registry]
duplicate_registry_count = len(registry_keys) - len(set(registry_keys))
result_keys = {x["key"] for x in registry}
registry_missing = sorted(resolved_set - result_keys)
registry_extra = sorted(result_keys - resolved_set)
valid = not problems and duplicate_registry_count == 0 and not registry_missing and not registry_extra and len(registry) == len(resolved_set)
validation_status = ("complete" if not missing else "partial") if valid else "invalid"

out = {
    "schema_version": 1,
    "purpose": "steamdb_true_miss_lookup_ledger",
    "status": validation_status,
    "transport": "github_ingested_runtime_submissions_then_ci_validated",
    "bindings": {
        "steamdb_cache_classification_blob_sha": classification_sha,
        "lookup_contract_blob_sha": sha("config/steamdb_lookup_contract.json"),
        "ownership_contract_blob_sha": sha("config/execution_ownership_contract.json"),
        "github_runtime_state_blob_sha": sha("data/cache/steamdb_runtime_state.json"),
        "prepared_runtime_resolutions_blob_sha": sha("data/cache/steamdb_web_resolutions.json"),
    },
    "expected_true_miss_count": len(expected),
    "runtime_attempted_count": prepared.get("runtime_attempted_count"),
    "validated_resolution_count": len(registry),
    "unresolved_retry_count": len(missing),
    "confirmed_min_count": sum(1 for x in registry if x["result"] == "confirmed_min"),
    "previously_free_count": sum(1 for x in registry if x["result"] == "previously_free"),
    "unavailable_exact_history_count": sum(1 for x in registry if x["result"] == "unavailable_exact_history"),
    "blocked_or_failure_count": 0 if valid else len(problems),
    "duplicate_registry_count": duplicate_registry_count,
    "non_miss_query_count": len(registry_extra),
    "missing_result_count": len(missing),
    "unresolved_keys": missing,
    "lookup_registry": registry,
    "confirmed_min": [x for x in registry if x["result"] == "confirmed_min"],
    "previously_free": [x for x in registry if x["result"] == "previously_free"],
    "unavailable_exact_history": [x for x in registry if x["result"] == "unavailable_exact_history"],
    "problems": problems,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "status": out["status"],
    "expected": out["expected_true_miss_count"],
    "validated": out["validated_resolution_count"],
    "unresolved_retry": out["unresolved_retry_count"],
    "confirmed_min": out["confirmed_min_count"],
    "previously_free": out["previously_free_count"],
    "unavailable": out["unavailable_exact_history_count"],
    "problems": len(problems),
}, ensure_ascii=False, indent=2))
if not valid:
    raise SystemExit("Runtime SteamDB resolution validation failed")
