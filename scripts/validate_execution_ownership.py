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

manual_workers = ownership.get("explicit_manual_semantic_worker_chats") or {}
if manual_workers.get("ordinary_interactive_chat_role_unchanged") is not True:
    fail("manual semantic-worker exception must not broaden ordinary interactive chat")
russian_manual = manual_workers.get("russian_description_one_shot") or {}
if russian_manual.get("allowed") is not True:
    fail("canonical manual Russian semantic worker is not enabled")
if russian_manual.get("canonical_prompt") != "config/russian_description_manual_semantic_worker_prompt.md":
    fail("manual Russian semantic worker prompt path mismatch")
if russian_manual.get("requires_fresh_explicit_user_launch_every_run") is not True:
    fail("manual Russian semantic worker must require explicit launch every run")
if russian_manual.get("recurring_schedule_allowed") is not False:
    fail("manual Russian semantic worker must not become recurring")
if russian_manual.get("may_create_or_modify_scheduled_task") is not False:
    fail("manual Russian semantic worker must not modify Scheduled Tasks")

# Explicit manual Deep is a separate one-shot semantic role, never a broadening of
# the ordinary interactive/developer session or a new scheduler.
deep = load_json("config/progressive_pass2_contract.json")
deep_manual = manual_workers.get("progressive_deep_one_shot") or {}
deep_owner = (deep.get("ownership") or {}).get("explicit_manual_one_shot_chatgpt_data_plane") or {}
deep_phase = ownership.get("progressive_personalization_phase_c_pass2_core") or {}
deep_launcher_path = "config/progressive_pass2_manual_one_shot_prompt.md"
deep_worker_path = "config/progressive_pass2_worker_prompt.md"
deep_launcher = (ROOT / deep_launcher_path).read_text(encoding="utf-8")
deep_worker = (ROOT / deep_worker_path).read_text(encoding="utf-8")

if (deep_manual.get("allowed") is not True
        or deep_manual.get("authorization_source") != "WORKER_TASK_PROGRESSIVE_DEEP_MANUAL_ONE_SHOT_AUTHORIZATION_01.md"
        or deep_manual.get("canonical_launcher_prompt") != deep_launcher_path
        or deep_manual.get("canonical_worker_prompt") != deep_worker_path
        or deep_manual.get("canonical_contract") != "config/progressive_pass2_contract.json"
        or deep_manual.get("role") != "isolated_user_launched_progressive_deep_semantic_data_plane_only"):
    fail("explicit manual Progressive Deep authorization or canonical routes mismatch")
for key, expected in {
    "requires_fresh_explicit_user_launch_every_run": True,
    "recurring_schedule_allowed": False,
    "may_create_or_modify_scheduled_task": False,
}.items():
    if deep_manual.get(key) is not expected:
        fail(f"manual Deep launch boundary broken: {key}")
if "recovery authorization" not in " ".join(deep_manual.get("github_owns") or []):
    fail("manual Deep recovery authorization must stay with GitHub")
if (deep_phase.get("explicit_manual_one_shot_semantic_data_plane")
        != "config/execution_ownership_contract.json#explicit_manual_semantic_worker_chats.progressive_deep_one_shot"):
    fail("Deep active phase not bound to explicit one-shot authorization")
if (deep.get("version", 0) < 16 or deep.get("implemented") is not True
        or deep.get("active") is not True
        or (deep.get("ownership") or {}).get("control_plane") != "github"
        or (deep.get("ownership") or {}).get("interactive_chat") != "development_only_not_production_worker"
        or (deep.get("ownership") or {}).get("scheduled_chatgpt") != "bounded_semantic_data_plane_only"):
    fail("PASS 2 ordinary ownership/activation changed")
for key, expected in {
    "allowed": True,
    "authorization_source": "config/execution_ownership_contract.json#explicit_manual_semantic_worker_chats.progressive_deep_one_shot",
    "canonical_launcher_prompt": deep_launcher_path,
    "canonical_worker_prompt": deep_worker_path,
    "requires_fresh_explicit_user_launch_every_run": True,
    "ordinary_interactive_developer_chat_role_unchanged": True,
    "uses_same_existing_v2_marker_parent_freeze_and_confirmed_receipt": True,
    "github_only_scope_order_recovery_attempts_validation_and_persistence": True,
    "per_item_mutable_main_refresh_after_freeze_allowed": False,
    "new_recurring_schedule_or_second_queue_allowed": False,
    "may_create_or_modify_scheduled_task": False,
}.items():
    if deep_owner.get(key) != expected:
        fail(f"PASS 2 manual Deep cross-contract mismatch: {key}")

# V2 run-start marker -> ACTUAL marker Git parent -> durable confirmed GitHub
# receipt remains a hard publication gate for BOTH result/terminal transports.
start = ((deep.get("transport") or {}).get("run_start_confirmation") or {})
traversal = deep.get("invocation_traversal") or {}
for key, expected in {
    "marker_contract": "PROGRESSIVE-PASS2-RUN-START-MARKER-V2",
    "confirmation_contract": "PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1",
    "actual_authority_source": "actual_first_parent_of_create_only_v2_run_start_marker_commit_selected_by_github",
    "confirmation_owner": "github_control_plane",
    "confirmation_required_before_first_semantic_artifact_publication": True,
    "missing_confirmation_authorizes_publication": False,
    "rejected_or_inconsistent_confirmation_discards_provisional_work": True,
    "per_item_reconfirmation": False,
}.items():
    if start.get(key) != expected:
        fail(f"Deep V2 marker/receipt boundary changed: {key}")
for key, expected in {
    "marker_parent_is_frozen_authority": True,
    "confirmed_authority_must_equal_v2_marker_parent": True,
    "worker_chosen_authority_field_allowed": False,
    "manifest_dossier_and_recovery_authorization_frozen_once": True,
    "per_item_mutable_manifest_dossier_or_authorization_reread": False,
    "github_run_start_confirmation_required": True,
    "confirmation_required_before_first_artifact_publication": True,
    "same_invocation_retry_after_transport_cleanup": False,
    "existing_transport_implies_canonical_acceptance": False,
    "missing_confirmation_authorizes_publication": False,
}.items():
    if traversal.get(key) != expected:
        fail(f"Deep frozen traversal boundary changed: {key}")
if (start.get("bounded_confirmation_wait") or {}).get("maximum_receipt_reads_after_outcome_ready") != 3:
    fail("Deep receipt wait must stay bounded")
if traversal.get("bounded_confirmation_wait_max_seconds") != 15:
    fail("Deep receipt time budget changed")
for required in (
    "CHAT_PROTOCOL.md", "CHAT_CONTEXT.md", "PROJECT_ROUTES.md",
    "config/execution_ownership_contract.json",
    "config/progressive_pass2_contract.json", deep_worker_path,
    "a fresh, explicit user request",
    "PROGRESSIVE-PASS2-RUN-START-MARKER-V2",
    "actual first Git parent",
    "PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1",
    "Before the first result OR terminal execution receipt",
    "never reread mutable `main` between items",
    "submitted", "canonically accepted",
    "Scheduled Task",
):
    if required not in deep_launcher:
        fail(f"Deep one-shot launcher missing safety instruction: {required}")
for required in (
    "exactly one file", "run_start_anchor_commit",
    "run_start_authority_commit", "actual single Git parent",
    "run_start_marker_parent_commit", "status: \"confirmed\"",
    "publish no Deep terminal execution receipt",
    "Once this one receipt is confirmed",
    "Never revisit an item in the same invocation",
    "pending/unverified",
):
    if required not in deep_worker:
        fail(f"canonical Deep worker lost existing V2/transport guard: {required}")
if (ROOT / "config/russian_description_manual_semantic_worker_prompt.md").is_file() is False:
    fail("pre-existing Russian-description one-shot launcher missing")

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
