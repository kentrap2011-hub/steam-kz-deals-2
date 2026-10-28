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


    def test_two_marker_old_snapshot_candidate_terminal_collision_is_fail_closed(self):
        """Two valid separately frozen outcomes for one old group cannot coexist."""
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            old, parent = h.commit_snapshot(
                [871001, 871002, 871003, 872001, 872002, 872003],
                "old snapshot with two independent groups",
            )
            _, candidate_anchor, candidate_nonce = h.marker("44444444444444444444444444444444")
            _, terminal_anchor, terminal_nonce = h.marker("55555555555555555555555555555555")
            self.assertEqual(commit_parent(candidate_anchor, h.repo), parent)
            self.assertEqual(commit_parent(terminal_anchor, h.repo), candidate_anchor)

            current, _ = h.commit_snapshot(
                [871001, 871002, 871003, 872001, 872002, 872003, 873001],
                "new compatible snapshot", day_offset=1,
            )
            self.assertNotEqual(old["snapshot_id"], current["snapshot_id"])
            candidate_path, _ = h.candidate(old, candidate_anchor, candidate_nonce, sequence=1)
            terminal_path, _ = h.terminal(old, terminal_anchor, terminal_nonce, sequence=1)
            sibling_path, _ = h.candidate(old, candidate_anchor, candidate_nonce, sequence=2)
            _commit_all(h.repo, "late conflicting transports plus independent sibling")

            result = h.drain()
            self.assertEqual(result["frozen_authority_accepted_count_this_run"], 1)
            self.assertEqual(result["frozen_authority_terminal_count_this_run"], 0)
            self.assertEqual(result["frozen_authority_rejected_count_this_run"], 2)
            self.assertEqual(result["failed_group_count_this_run"], 0)
            self.assertEqual(result["cache_reused_sequences"], [2])
            self.assertFalse(candidate_path.exists())
            self.assertFalse(terminal_path.exists())
            self.assertFalse(sibling_path.exists())
            quarantined = list((h.quarantine / "frozen_authority").glob("*"))
            self.assertEqual(len(quarantined), 2)
            self.assertEqual({p.name.split(".rejected-")[0] for p in quarantined},
                             {candidate_path.name, terminal_path.name})
            rejected = [json.loads(line) for line in h.rejection_audit.read_text(
                encoding="utf-8"
            ).splitlines()]
            self.assertEqual(len(rejected), 2)
            self.assertTrue(all(
                r["validator_error"] == "conflicting_candidate_and_terminal_receipt_for_frozen_group"
                and r["current_snapshot_progress_changed"] is False
                for r in rejected
            ))
            self.assertFalse(h.failure_audit.exists())
            self.assertFalse(list(h.terminal_archive.rglob("*.json")))
            audit = [json.loads(line) for line in h.audit_path.read_text(
                encoding="utf-8"
            ).splitlines()]
            self.assertEqual(len(audit), 1)
            self.assertEqual(audit[0]["authority_sequence"], 2)
            self.assertEqual(audit[0]["outcome"], "dossier_candidate_accepted_after_rollover")
            for appid in (871001, 871002, 871003):
                self.assertFalse((h.store / f"App_{appid}.json").exists())
            for appid in (872001, 872002, 872003):
                self.assertTrue((h.store / f"App_{appid}.json").exists())

            manifest = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["snapshot_id"], current["snapshot_id"])
            self.assertEqual([g["state"] for g in manifest["group_progress"]["groups"]],
                             ["pending", "accepted", "pending"])
            self.assertEqual(result["next_pending_sequence"], 1)

            # The rejected conflict does not return as a consumed attempt on replay.
            replay = h.drain()
            self.assertEqual(replay["frozen_authority_accepted_count_this_run"], 0)
            self.assertEqual(replay["frozen_authority_terminal_count_this_run"], 0)
            self.assertEqual(replay["frozen_authority_rejected_count_this_run"], 0)
            self.assertEqual(replay["cache_reused_sequences"], [])
            self.assertEqual(replay["failed_group_count"], 0)
            self.assertEqual(replay["next_pending_sequence"], 1)


    def _exercise_sequential_old_group_opposites(self, first_kind):
        """The durable old-group ledger, not one scan or marker, owns the outcome."""
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            old, parent = h.commit_snapshot(
                [874001, 874002, 874003, 875001, 875002, 875003],
                "immutable old snapshot with sibling",
            )
            _, first_anchor, first_nonce = h.marker("66666666666666666666666666666666")
            _, second_anchor, second_nonce = h.marker("77777777777777777777777777777777")
            self.assertEqual(commit_parent(first_anchor, h.repo), parent)
            self.assertEqual(commit_parent(second_anchor, h.repo), first_anchor)
            current, _ = h.commit_snapshot(
                [874001, 874002, 874003, 875001, 875002, 875003, 876001],
                "compatible next snapshot", day_offset=1,
            )
            self.assertNotEqual(old["snapshot_id"], current["snapshot_id"])
            first_path, _ = getattr(h, first_kind)(old, first_anchor, first_nonce)
            _commit_all(h.repo, "first old-group outcome")
            first = h.drain()
            first_outcome = (
                "dossier_candidate_accepted_after_rollover"
                if first_kind == "candidate" else "semantic_exhaustion_consumed_after_rollover"
            )
            self.assertEqual(first["frozen_authority_accepted_count_this_run"],
                             int(first_kind == "candidate"))
            self.assertEqual(first["frozen_authority_terminal_count_this_run"],
                             int(first_kind == "terminal"))
            first_audit = [json.loads(line) for line in h.audit_path.read_text(
                encoding="utf-8"
            ).splitlines()]
            self.assertEqual(len(first_audit), 1)
            self.assertEqual(first_audit[0]["outcome"], first_outcome)
            self.assertFalse(first_path.exists())
            saved = {}
            for appid in (874001, 874002, 874003):
                path = h.store / f"App_{appid}.json"
                saved[appid] = path.read_bytes() if path.exists() else None
            archived = sorted(h.terminal_archive.rglob("*.json"))
            self.assertEqual(len(archived), int(first_kind == "terminal"))
            archived_bytes = [path.read_bytes() for path in archived]
            first_manifest = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            first_group_state = first_manifest["group_progress"]["groups"][0]["state"]
            self.assertEqual(first_group_state,
                             "accepted" if first_kind == "candidate" else "pending")

            opposite = "terminal" if first_kind == "candidate" else "candidate"
            opposite_path, _ = getattr(h, opposite)(old, second_anchor, second_nonce)
            sibling_path, _ = h.candidate(old, second_anchor, second_nonce, sequence=2)
            _commit_all(h.repo, "opposite old-group outcome plus independent sibling")
            second = h.drain()
            self.assertEqual(second["frozen_authority_rejected_count_this_run"], 1)
            self.assertEqual(second["frozen_authority_accepted_count_this_run"], 1)
            self.assertEqual(second["frozen_authority_terminal_count_this_run"], 0)
            self.assertEqual(second["failed_group_count_this_run"], 0)
            self.assertEqual(second["cache_reused_sequences"], [2])
            self.assertFalse(opposite_path.exists())
            self.assertFalse(sibling_path.exists())
            self.assertEqual([p.name.split(".rejected-")[0] for p in
                              (h.quarantine / "frozen_authority").glob("*")],
                             [opposite_path.name])
            rejections = [json.loads(line) for line in h.rejection_audit.read_text(
                encoding="utf-8"
            ).splitlines()]
            self.assertEqual(len(rejections), 1)
            self.assertEqual(rejections[0]["validator_error"],
                             "opposite_frozen_group_outcome_already_consumed")
            self.assertIs(rejections[0]["current_snapshot_progress_changed"], False)
            self.assertFalse(h.failure_audit.exists())
            self.assertEqual([p.read_bytes() for p in sorted(
                h.terminal_archive.rglob("*.json")
            )], archived_bytes)
            for appid, before in saved.items():
                path = h.store / f"App_{appid}.json"
                self.assertEqual(path.read_bytes() if path.exists() else None, before)
            for appid in (875001, 875002, 875003):
                self.assertTrue((h.store / f"App_{appid}.json").is_file())
            current_manifest = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current_manifest["snapshot_id"], current["snapshot_id"])
            self.assertEqual([g["state"] for g in current_manifest["group_progress"]["groups"]],
                             [first_group_state, "accepted", "pending"])
            audit = [json.loads(line) for line in h.audit_path.read_text(
                encoding="utf-8"
            ).splitlines()]
            self.assertEqual(len(audit), 2)
            self.assertEqual(audit[0], first_audit[0])
            self.assertEqual(audit[1]["authority_sequence"], 2)
            self.assertEqual(audit[1]["outcome"], "dossier_candidate_accepted_after_rollover")

            replay = h.drain()
            self.assertEqual(replay["frozen_authority_rejected_count_this_run"], 0)
            self.assertEqual(replay["frozen_authority_terminal_count_this_run"], 0)
            self.assertEqual(replay["frozen_authority_accepted_count_this_run"], 0)
            self.assertEqual(replay["cache_reused_sequences"], [])
            # A replay from the original consumed marker is cleanup-only,
            # even if another valid marker published a conflicting outcome.
            replay_path, _ = getattr(h, first_kind)(old, first_anchor, first_nonce)
            replay = h.drain()
            self.assertEqual(replay["frozen_authority_replay_cleanup_count_this_run"], 1)
            self.assertFalse(replay_path.exists())
            self.assertEqual(len(h.audit_path.read_text(
                encoding="utf-8"
            ).splitlines()), 2)

    def test_sequential_candidate_then_terminal_distinct_markers_fail_closed(self):
        self._exercise_sequential_old_group_opposites("candidate")

    def test_sequential_terminal_then_candidate_distinct_markers_fail_closed(self):
        self._exercise_sequential_old_group_opposites("terminal")

    def test_new_snapshot_valid_success_is_not_an_old_group_conflict(self):
        """A fresh legitimately planned success remains allowed after old attempts."""
        from datetime import timedelta

        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            old, _ = h.commit_snapshot([877001, 877002, 877003], "old work")
            _, winner_anchor, winner_nonce = h.marker("88888888888888888888888888888888")
            _, other_anchor, other_nonce = h.marker("99999999999999999999999999999999")
            h.commit_snapshot([877001, 877002, 877003, 877004],
                              "compatible rollover", day_offset=1)
            h.candidate(old, winner_anchor, winner_nonce)
            _commit_all(h.repo, "old candidate")
            h.drain()
            late_terminal, _ = h.terminal(old, other_anchor, other_nonce)
            _commit_all(h.repo, "late opposite old terminal")
            blocked = h.drain()
            self.assertEqual(blocked["frozen_authority_rejected_count_this_run"], 1)
            self.assertFalse(late_terminal.exists())

            # The old cache now exceeds its canonical TTL. GitHub prepares a
            # genuinely new current group and can accept fresh success normally.
            h.now += timedelta(days=25)
            fresh, _ = h.commit_snapshot(
                [877001, 877002, 877003, 877004], "new due review"
            )
            self.assertNotEqual(fresh["snapshot_id"], old["snapshot_id"])
            self.assertEqual(fresh["submission_group_plan"]["groups"][0]["appids"],
                             ["877001", "877002", "877003"])
            _, anchor, nonce = h.marker("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            current_path, _ = h.candidate(fresh, anchor, nonce)
            _commit_all(h.repo, "fresh successful analysis")
            result = h.drain()
            self.assertEqual(result["accepted_group_count_this_run"], 1)
            self.assertEqual(result["frozen_authority_rejected_count_this_run"], 0)
            self.assertFalse(current_path.exists())
            manifest = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["group_progress"]["groups"][0]["state"], "accepted")
            self.assertEqual(manifest["snapshot_id"], fresh["snapshot_id"])


if __name__ == "__main__":
    unittest.main()
