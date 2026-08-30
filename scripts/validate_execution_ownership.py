#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def fail(message):
    raise SystemExit(f"ARCHITECTURE_OWNERSHIP_INVALID: {message}")


ownership = load_json("config/execution_ownership_contract.json")
daily = load_json("config/daily_execution_contract.json")
steamdb = load_json("config/steamdb_lookup_contract.json")
chat_context = (ROOT / "CHAT_CONTEXT.md").read_text(encoding="utf-8")

if ownership.get("contract") != "PRODUCTION-EXECUTION-OWNERSHIP-V1":
    fail("unexpected ownership contract id")
if ownership.get("status") != "canonical":
    fail("ownership contract must be canonical")

control = ownership.get("github_control_plane") or {}
control_responsibilities = set(control.get("responsibilities") or [])
required_control = {
    "decide the exact current production scope",
    "construct manifests and explicit runtime work inputs",
    "own retry state and unresolved-item state",
    "own checkpoint merge logic and completeness accounting",
    "validate all returned runtime facts against the exact prepared scope",
    "persist validated canonical caches",
    "decide whether the production cycle is complete",
}
if not required_control.issubset(control_responsibilities):
    fail("GitHub control-plane responsibilities are incomplete")

runtime = ownership.get("scheduled_chatgpt_runtime_data_plane") or {}
forbidden = set(runtime.get("forbidden") or [])
required_runtime_forbidden = {
    "invent or redefine production scope",
    "choose a new queue independently of GitHub",
    "turn a checkpoint size into a quota",
    "replace GitHub retry/completeness logic with conversational iteration",
    "treat an interactive chat as the production scheduler or backlog manager",
}
if not required_runtime_forbidden.issubset(forbidden):
    fail("ChatGPT data-plane constraints are incomplete")

interactive = ownership.get("interactive_chat") or {}
interactive_forbidden = set(interactive.get("forbidden") or [])
if "manually process a large production backlog item by item as a substitute for repairing automation" not in interactive_forbidden:
    fail("interactive chat manual-backlog prohibition is missing")

if daily.get("ownership_contract") != "config/execution_ownership_contract.json":
    fail("daily execution contract is not bound to ownership contract")
inv = daily.get("execution_invariants") or {}
if inv.get("github_owns_control_plane") is not True:
    fail("daily execution must declare GitHub control-plane ownership")
if inv.get("interactive_chat_is_production_executor") is not False:
    fail("interactive chat must not be a production executor")
if inv.get("per_day_item_quota_allowed") is not False:
    fail("daily item quota must remain disabled")

if steamdb.get("version") != "1.4":
    fail("unexpected SteamDB lookup contract version")
if steamdb.get("ownership_contract") != "config/execution_ownership_contract.json":
    fail("SteamDB contract is not bound to ownership contract")
steam_owner = steamdb.get("ownership") or {}
if (steam_owner.get("interactive_chat") or {}).get("production_backlog_processing_allowed") is not False:
    fail("SteamDB contract allows interactive backlog processing")
if (steamdb.get("execution_scope") or {}).get("runtime_progress_or_manual_batch_files_are_canonical_scope") is not False:
    fail("manual runtime progress/batches must remain noncanonical")
transport = steamdb.get("transport") or {}
required_transport = {
    "stage_scope_manifest": "data/cache/steamdb_miss_manifest.json",
    "github_derived_runtime_state": "data/cache/steamdb_runtime_state.json",
    "github_derived_runtime_work_input": "data/cache/steamdb_runtime_work.json",
    "runtime_submission_glob": "data/inbox/steamdb_runtime/*.json",
    "prepared_runtime_artifact": "data/cache/steamdb_web_resolutions.json",
    "ingestion_workflow": ".github/workflows/ingest-steamdb-runtime-submissions.yml",
}
for key, value in required_transport.items():
    if transport.get(key) != value:
        fail(f"SteamDB transport mismatch for {key}")
work_contract = steamdb.get("runtime_work_input_contract") or {}
if work_contract.get("produced_only_by_github") is not True or work_contract.get("chatgpt_must_not_recompute_unresolved_set") is not True:
    fail("SteamDB runtime work input is not GitHub-owned")
state_contract = steamdb.get("github_runtime_state_contract") or {}
if state_contract.get("github_alone_decides_complete") is not True:
    fail("SteamDB completeness is not GitHub-owned")

required_context_markers = [
    "config/execution_ownership_contract.json",
    "Обязательный architecture preflight",
    "Интерактивный пользовательский чат нельзя превращать в production worker",
    "поправка пользователя не отменяет preflight",
]
for marker in required_context_markers:
    if marker not in chat_context:
        fail(f"CHAT_CONTEXT.md missing required guardrail: {marker}")

if not (ROOT / ".github/workflows/ingest-steamdb-runtime-submissions.yml").exists():
    fail("GitHub-owned SteamDB ingestion workflow is missing")
if not (ROOT / "scripts/ingest_steamdb_runtime_submissions.py").exists():
    fail("GitHub-owned SteamDB ingestion script is missing")
if (ROOT / ".github/workflows/assemble-steamdb-runtime-resolutions.yml").exists():
    fail("deprecated manual SteamDB assembler workflow still exists")

workflow_dir = ROOT / ".github" / "workflows"
for path in workflow_dir.glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    if "data/cache/steamdb_runtime_batches" in text or "data/cache/steamdb_runtime_progress.json" in text:
        fail(f"production workflow {path.name} depends on noncanonical manual SteamDB recovery artifacts")

print("ARCHITECTURE_OWNERSHIP_VALID")
