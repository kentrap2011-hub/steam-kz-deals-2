#!/usr/bin/env python3
"""Isolated, offline Dossier V1 manual one-shot authority/security regression."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from taste_steam_review_dossier_authority import (
    commit_parent,
    run_start_marker_path,
    validate_run_start_marker_commit,
)
from test_taste_dossier_frozen_invocation_rollover import (
    FrozenInvocationHarness,
    _commit_all,
)

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = "config/taste_steam_review_dossier_manual_one_shot_prompt.md"
RUNTIME_PATH = "config/taste_steam_review_dossier_runtime_prompt.md"
WORKER_PATH = "config/taste_steam_review_dossier_worker_prompt.md"
DOSSIER_CONTRACT_PATH = "config/taste_steam_review_dossier_contract.json"
SCHEMA_PATHS = [
    "config/taste_steam_review_dossier_schema.json",
    "config/taste_steam_review_dossier_web_evidence_contract.json",
    "config/taste_steam_review_dossier_terminal_receipt_schema.json",
]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate_manual_boundary(owner, launcher):
    """Negative controls deliberately mutate one authorization/guard at a time."""
    manual_workers = owner["explicit_manual_semantic_worker_chats"]
    manual = manual_workers["dossier_v1_one_shot"]
    for key, value in {
        "allowed": True,
        "authorization_source": "WORKER_TASK_DOSSIER_V1_EXPLICIT_MANUAL_ONE_SHOT_AUTHORIZATION_01.md",
        "canonical_launcher_prompt": LAUNCHER_PATH,
        "canonical_runtime_prompt": RUNTIME_PATH,
        "canonical_worker_prompt": WORKER_PATH,
        "canonical_contract": DOSSIER_CONTRACT_PATH,
        "required_evidence_contracts": SCHEMA_PATHS,
        "requires_fresh_explicit_user_launch_every_run": True,
        "recurring_schedule_allowed": False,
        "may_create_or_modify_scheduled_task": False,
        "scheduled_dossier_role_unchanged": True,
        "ordinary_interactive_developer_chat_role_unchanged": True,
        "role": "isolated_user_launched_dossier_v1_semantic_data_plane_only",
    }.items():
        if manual.get(key) != value:
            raise ValueError("manual Dossier boundary broken: " + key)
    if manual_workers.get("ordinary_interactive_chat_role_unchanged") is not True:
        raise ValueError("ordinary interactive role was broadened")
    if not manual_workers["progressive_deep_one_shot"]["allowed"]:
        raise ValueError("pre-existing Deep one-shot authorization lost")
    if not manual_workers["russian_description_one_shot"]["allowed"]:
        raise ValueError("pre-existing Russian one-shot authorization lost")
    guard = manual.get("concurrent_and_stale_invocation_guardrails") or {}
    for key, value in {
        "scheduled_and_manual_invocations_may_overlap": True,
        "manual_exclusive_lease_or_scheduler_lock_created": False,
        "every_invocation_requires_fresh_nonce_marker": True,
        "marker_parent_not_observed_main_is_authority": True,
        "after_marker_mutable_main_rebinding_allowed": False,
        "stale_or_inconsistent_marker_parent_fails_closed": True,
        "deterministic_group_result_path_must_be_create_only": True,
        "group_acceptance_replay_and_recovery_owner": "github_control_plane",
        "no_extra_manual_confirmation_or_receipt_mechanism": True,
    }.items():
        if guard.get(key) != value:
            raise ValueError("Dossier concurrency authority broken: " + key)
    if "stop affected path fail closed" not in guard.get("on_existing_path_or_create_failure", ""):
        raise ValueError("duplicate path retry forbidden")
    for required in (
        "fresh explicit user request", "one immediate invocation",
        "config/execution_ownership_contract.json", RUNTIME_PATH, WORKER_PATH,
        *SCHEMA_PATHS, "data/production/pre_ai/taste_steam_review_dossier_worker_index.json",
        "actual single Git parent", "one fresh nonce-only",
        "pending group", "marker-parent", "create-only",
        "Concurrent scheduled and manually launched runs", "no marker",
        "not canonically accepted", "Scheduled Task",
        "GitHub ingest validates actual marker-parent authority",
    ):
        if required not in launcher:
            raise ValueError("manual Dossier launcher missing gate: " + required)
    if "PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1" in launcher:
        raise ValueError("Deep confirmation was incorrectly imported")


class DossierManualOneShotTests(unittest.TestCase):
    def test_authorization_is_narrow_and_existing_roles_are_preserved(self):
        owner = load("config/execution_ownership_contract.json")
        launcher = (ROOT / LAUNCHER_PATH).read_text(encoding="utf-8")
        validate_manual_boundary(owner, launcher)
        self.assertEqual(owner["interactive_chat"]["role"], "developer/operator session, not a production execution engine")
        self.assertEqual(owner["taste_steam_review_dossier_nonblocking_progress"]["scheduled_chatgpt_role"],
                         "bounded_semantic_candidate_or_exact_exhaustion_terminal_generation_and_create_only_transport_only")
        self.assertTrue(owner["explicit_manual_semantic_worker_chats"]["progressive_deep_one_shot"]["requires_fresh_explicit_user_launch_every_run"])
        self.assertTrue(owner["explicit_manual_semantic_worker_chats"]["russian_description_one_shot"]["requires_fresh_explicit_user_launch_every_run"])
        for p in [LAUNCHER_PATH, RUNTIME_PATH, WORKER_PATH, DOSSIER_CONTRACT_PATH, *SCHEMA_PATHS]:
            self.assertTrue((ROOT / p).is_file(), p)

    def test_negative_authorization_concurrency_and_staleness_controls(self):
        owner = load("config/execution_ownership_contract.json")
        launcher = (ROOT / LAUNCHER_PATH).read_text(encoding="utf-8")
        mutations = [
            ("allowed", False),
            ("requires_fresh_explicit_user_launch_every_run", False),
            ("recurring_schedule_allowed", True),
            ("may_create_or_modify_scheduled_task", True),
            ("canonical_runtime_prompt", "config/noncanonical.md"),
            ("scheduled_dossier_role_unchanged", False),
        ]
        for key, value in mutations:
            modified = copy.deepcopy(owner)
            modified["explicit_manual_semantic_worker_chats"]["dossier_v1_one_shot"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_manual_boundary(modified, launcher)
        for key, value in [
            ("marker_parent_not_observed_main_is_authority", False),
            ("after_marker_mutable_main_rebinding_allowed", True),
            ("deterministic_group_result_path_must_be_create_only", False),
            ("manual_exclusive_lease_or_scheduler_lock_created", True),
            ("no_extra_manual_confirmation_or_receipt_mechanism", False),
        ]:
            modified = copy.deepcopy(owner)
            modified["explicit_manual_semantic_worker_chats"]["dossier_v1_one_shot"]["concurrent_and_stale_invocation_guardrails"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_manual_boundary(modified, launcher)
        with self.assertRaises(ValueError):
            validate_manual_boundary(owner, launcher.replace("Concurrent scheduled and manually launched runs", "Concurrent runs"))

    def test_scheduled_and_manual_share_existing_runtime_without_new_authority(self):
        contract = load(DOSSIER_CONTRACT_PATH)
        manual = load("config/execution_ownership_contract.json")["explicit_manual_semantic_worker_chats"]["dossier_v1_one_shot"]
        runtime = (ROOT / RUNTIME_PATH).read_text(encoding="utf-8")
        worker = (ROOT / WORKER_PATH).read_text(encoding="utf-8")
        self.assertTrue(manual["scheduled_dossier_role_unchanged"])
        self.assertEqual(contract["checkpointing"]["checkpoint_size"], 3)
        self.assertTrue(contract["buffered_submission"]["buffer"]["concurrent_candidate_and_terminal_allowed"] is False)
        self.assertEqual(contract["buffered_submission"]["buffer"]["worker_write_mode"],
                         "immutable_create_only_exactly_one_outcome_transport_per_group_candidate_or_terminal_receipt")
        self.assertEqual(contract["buffered_submission"]["canonical_writer_serialization"]["owner"], "github_control_plane")
        self.assertTrue(contract["worker_read_projection"]["status"] == "active")
        for phrase in ("exactly one create-only marker", "Its actual single Git parent",
                       "pending_group_sequences", "reuse a cached Dossier verbatim",
                       "After a successful create-only candidate or terminal publication",
                       "create-file", "stop fail-closed", "run_start_authority"):
            self.assertIn(phrase, runtime)
        for phrase in ("prepublication.py", "Scheduled ChatGPT runtime gate",
                       "neutral", "found_and_used", "FAIL_CLOSED_EXECUTION_LEDGER_V1"):
            self.assertIn(phrase, worker)
        self.assertIn("not_required_for_scheduled_worker",
                      json.dumps(load(SCHEMA_PATHS[1])["prepublication_validation"]))

    def test_two_markers_have_distinct_actual_parents_and_one_create_only_group_path(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            work, parent = h.commit_snapshot([870001, 870002, 870003], "frozen work")
            _, first, first_nonce = h.marker("11111111111111111111111111111111")
            _, second, second_nonce = h.marker("22222222222222222222222222222222")
            self.assertEqual(commit_parent(first, h.repo), parent)
            self.assertEqual(commit_parent(second, h.repo), first)
            self.assertNotEqual(run_start_marker_path(first_nonce), run_start_marker_path(second_nonce))
            for anchor, nonce in [(first, first_nonce), (second, second_nonce)]:
                marker = run_start_marker_path(nonce, h.contract["paths"]["submission_inbox_dir"])
                doc = json.loads(marker.read_text(encoding="utf-8"))
                proof, view = validate_run_start_marker_commit(
                    anchor, marker, doc, contract=h.contract, sequence=1, repo_root=h.repo
                )
                self.assertEqual(proof["run_start_authority_commit"], commit_parent(anchor, h.repo))
                self.assertEqual(view["descriptor"]["group_sha256"],
                                 work["submission_group_plan"]["groups"][0]["group_sha256"])

            candidate_path, original = h.candidate(work, first, first_nonce)
            # A concurrent manual/scheduled publisher cannot create the same deterministic path.
            with self.assertRaises(FileExistsError):
                with candidate_path.open("x", encoding="utf-8") as out:
                    json.dump(original, out)
            self.assertEqual(json.loads(candidate_path.read_text(encoding="utf-8")), original)
            _commit_all(h.repo, "single winner candidate")
            result = h.drain()
            self.assertEqual(result["accepted_group_count_this_run"], 1)
            self.assertEqual(json.loads(h.manifest_path.read_text(encoding="utf-8"))["group_progress"]["groups"][0]["state"], "accepted")

    def test_candidate_and_terminal_conflict_quarantines_without_consuming_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            work, _ = h.commit_snapshot([870011, 870012, 870013], "prepared")
            _, anchor, nonce = h.marker("33333333333333333333333333333333")
            h.candidate(work, anchor, nonce)
            h.terminal(work, anchor, nonce)
            _commit_all(h.repo, "conflicting transports")
            h.drain()
            manifest = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            group = manifest["group_progress"]["groups"][0]
            self.assertEqual(group["state"], "pending")
            self.assertFalse((h.store / "App_870011.json").exists())


if __name__ == "__main__":
    unittest.main()
