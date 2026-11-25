#!/usr/bin/env python3
"""Read-only authorization/ready gate negative tests (not live writer CI)."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import dossier_lean_writer_auto_ready as ready
from dossier_lean_canonical_dual import SANDBOX_GRANT

GRANT = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))


class LeanAutoReadySourceTests(unittest.TestCase):
    def test_new_owner_approval_is_narrow_but_source_activation_remains_off(self):
        p = ready.policy()
        self.assertFalse(p["activation_enabled"])
        self.assertTrue(p["recovery"]["permission_bound_to_exact_previous_failed_run"])
        self.assertEqual(p["recovery"]["failed_manual_workflow_run_id"], 45540222575)
        self.assertEqual(p["recovery"]["trial_id"], GRANT["trial_id"])
        self.assertFalse(p["automatic_retry_after_failure"])
        self.assertTrue(p["requires_independent_L3_final_head_review"])
        self.assertTrue(p["future_trial_requirements"][
            "eligible_only_with_separate_immutable_owner_issued_auto_writer_grant"])
        self.assertEqual(len(ready.exact_pairs()), 6)

    def test_no_source_event_can_activate_without_separate_contract_change(self):
        with self.assertRaisesRegex(ValueError, "activation pending"):
            ready.verify_source_signal({}, {})
        with self.assertRaisesRegex(ValueError, "no auto-run"):
            ready.validate_ready(".", token="test")

    def test_action_wakeup_trust_and_shared_writer_static_guard(self):
        root = Path(__file__).resolve().parents[1]
        signal = (root / ready.SIGNAL_WORKFLOW).read_text(encoding="utf-8")
        runner = (root / ready.AUTO_WORKFLOW).read_text(encoding="utf-8")
        self.assertIn("contents: read", signal)
        self.assertNotIn("contents: write", signal)
        self.assertIn("sandbox/dossier-notes-v2-assembly-replay-*", signal)
        self.assertIn("data/control/dossier_notes_v2/receipts/**", signal)
        self.assertIn("workflow_run:", runner)
        self.assertIn("'Dossier Lean Writer Ready Signal'", runner)
        self.assertIn("branches: [main]", runner)
        self.assertIn("group: taste-steam-review-dossier-canonical-writer", runner)
        self.assertIn("cancel-in-progress: false", runner)
        self.assertIn("python scripts/dossier_lean_writer_auto_ready.py run", runner)
        self.assertNotIn("schedule:", runner)
        self.assertNotIn("workflow_dispatch:", runner)
        old = (root / ready.batch.WRITER_WORKFLOW).read_text(encoding="utf-8")
        self.assertIn("python scripts/dossier_notes_v2_batch_preflight.py --trial-id", old)
        self.assertIn('test "        valid = {
            "id": 45540222575, "event": "workflow_dispatch",
            "path": ready.batch.WRITER_WORKFLOW,
            "run_attempt": 1, "status": "completed",
            "conclusion": "failure",
            "head_sha": "147be762d217dc1e7dc53a6fbd896f323f6af08c",
            "head_branch": "main",
            "actor": {"id": int(ready.batch.OWNER_ID),
                      "login": ready.batch.OWNER_LOGIN},
            "triggering_actor": {"id": int(ready.batch.OWNER_ID),
                                 "login": ready.batch.OWNER_LOGIN},
        }
        with patch.object(ready, "_github_get", return_value=valid):
            self.assertTrue(ready.authentic_old_failure("offline-token"))
        for key, bad in (("run_attempt", 2), ("conclusion", "success"),
                         ("head_sha", "0" * 40), ("path", "evil.yml"),
                         ("status", "in_progress"),
                         ("actor", {"id": 1, "login": "spoofed"})):
            with self.subTest(key=key):
                altered = dict(valid)
                altered[key] = bad
                with patch.object(ready, "_github_get", return_value=altered):
                    with self.assertRaises(ValueError):
                        ready.authentic_old_failure("offline-token")
        with self.assertRaises(ValueError):
            ready.authentic_old_failure("")

    def test_wakeup_source_requires_specific_github_run_not_untrusted_push(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": ready.batch.REPOSITORY,
            "GITHUB_REPOSITORY_OWNER_ID": ready.batch.OWNER_ID,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": ready.batch.REPOSITORY + "/" +
                                ready.AUTO_WORKFLOW + "@refs/heads/main",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_RUN_ID": "9000",
            "GITHUB_EVENT_NAME": "workflow_run",
        }
        signal = {"workflow_run": {
            "event": "push", "status": "completed", "conclusion": "success",
            "run_attempt": 1, "path": ready.SIGNAL_WORKFLOW,
            "head_branch": "sandbox/" + GRANT["trial_id"],
            "head_sha": GRANT["frozen_sandbox_head"],
            "head_repository": {"full_name": ready.batch.REPOSITORY},
            "id": 98765,
        }}
        with patch.object(ready, "policy", return_value={"activation_enabled": True}):
            self.assertEqual(
                ready.verify_source_signal(signal, env)["source_signal_run_id"],
                98765)
            for key, bad in (
                ("conclusion", "failure"),
                ("run_attempt", 2),
                ("head_branch", "sandbox/dossier-notes-v2-unknown"),
                ("head_sha", "0" * 40),
                ("path", ".github/workflows/malicious.yml"),
                ("head_repository", {"full_name": "attacker/fork"}),
            ):
                with self.subTest(key=key):
                    modified = copy.deepcopy(signal)
                    modified["workflow_run"][key] = bad
                    with self.assertRaises(ValueError):
                        ready.verify_source_signal(modified, env)
            for key, bad in (
                ("GITHUB_REPOSITORY", "attacker/repo"),
                ("GITHUB_WORKFLOW_REF", "attacker/workflow"),
                ("GITHUB_RUN_ATTEMPT", "2"),
                ("GITHUB_REF", "refs/heads/untrusted"),
            ):
                with self.subTest(key=key):
                    modified = dict(env)
                    modified[key] = bad
                    with self.assertRaises(ValueError):
                        ready.verify_source_signal(signal, modified)

    def test_main_catchup_accepts_only_owner_activation_push(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": ready.batch.REPOSITORY,
            "GITHUB_REPOSITORY_OWNER_ID": ready.batch.OWNER_ID,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": ready.batch.REPOSITORY + "/" +
                                ready.AUTO_WORKFLOW + "@refs/heads/main",
            "GITHUB_RUN_ATTEMPT": "1", "GITHUB_RUN_ID": "9000",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_SHA": "f" * 40, "GITHUB_ACTOR_ID": ready.batch.OWNER_ID,
            "GITHUB_TRIGGERING_ACTOR": ready.batch.OWNER_LOGIN,
        }
        event = {
            "ref": "refs/heads/main", "created": False, "deleted": False,
            "forced": False, "after": "f" * 40,
            "repository": {"full_name": ready.batch.REPOSITORY},
            "sender": {"id": int(ready.batch.OWNER_ID)},
            "head_commit": {"modified": [
                "config/dossier_lean_writer_auto_ready_v1.json"
            ], "added": []},
        }
        with patch.object(ready, "policy", return_value={"activation_enabled": True}):
            self.assertEqual(ready.verify_source_signal(event, env)[
                "event_kind"], "owner_activation_catchup")
            for key, bad in (("forced", True), ("after", "0" * 40),
                             ("sender", {"id": 17}),
                             ("head_commit", {"modified": ["README.md"], "added": []})):
                with self.subTest(key=key):
                    modified = dict(event)
                    modified[key] = bad
                    with self.assertRaises(ValueError):
                        ready.verify_source_signal(modified, env)

    def test_exact_ready_validates_year_edition_and_every_terminal_receipt(self):
        # Synthetic dependency stand-ins: validates fail-closed orchestration.
        # Real Git object/writer transaction is exercised by existing sandbox
        # tests; this is NOT a full event -> writer -> push test.
        trial = GRANT["trial_id"]
        original_rows = GRANT["items"]
        pairs = ready.exact_pairs()
        fake_git = [
            SimpleNamespace(stdout=("sandbox/" + trial + "\n").encode()),
            SimpleNamespace(stdout=(GRANT["frozen_sandbox_head"] + "\n").encode()),
            SimpleNamespace(stdout=(GRANT["authorization_commit"] + "\n").encode()),
        ]
        issuer = {
            "authority_origin": "generic_owner_request",
            "semantic_execution_authorized": True,
            "authorization_commit": GRANT["authorization_commit"],
            "github_authorization_run_id": GRANT["owner_source_actions_run_id"],
            "request_commit": GRANT["original_request_commit"],
        }
        frozen = {x["appid"]: x for x in original_rows}
        projection = {"items": [{"appid": x["appid"], "status": "ready"}
                                for x in original_rows]}
        work_by_app = {}
        for r in original_rows:
            assignment = {k: r[k] for k in ("appid", "title",
                                            "assignment_id", "group_sequence")}
            work_by_app[r["appid"]] = {
                "status": "ready_for_autonomous_assembly",
                "assignment": assignment,
                "research_transport": {},
                "output_path": "synthetic/" + r["appid"],
            }

        def work(repo, **kw):
            return work_by_app[kw["appid"]]

        docs = {}
        for r in original_rows:
            a = r["appid"]
            docs[a] = {
                "outcome": "assembled_candidate_ready",
                "assignment": work_by_app[a]["assignment"],
                "research_transport": {},
                "final_dossier": {
                    "game_identity": {"release_year": r["original_release_year"]}
                },
            }

        def doc(repo, sha, path):
            return docs[path.split("/")[-1]]

        with tempfile.TemporaryDirectory() as tmp:
            def call():
                with patch.object(ready, "policy",
                                  return_value={"activation_enabled": True}), \
                     patch.object(ready, "git", side_effect=list(fake_git)), \
                     patch.object(ready.batch, "issuer_structure", return_value=issuer), \
                     patch.object(ready.batch, "authenticated_owner_run", return_value=True), \
                     patch.object(ready.generic, "policy", return_value={}), \
                     patch.object(ready, "authentic_old_failure", return_value=True), \
                     patch("dossier_lean_canonical_dual.require_isolated_sandbox_writer",
                           return_value=frozen), \
                     patch.object(ready.v2, "individual_final_readiness",
                                  return_value=projection), \
                     patch.object(ready, "require_batch_terminal_receipts"), \
                     patch.object(ready.v2, "inspect_assembly",
                                  return_value={
                                      "status": "strict_item_valid_pending_existing_atomic_group_ingest"}), \
                     patch.object(ready.v2, "assembly_work", side_effect=work), \
                     patch.object(ready, "json_at", side_effect=doc), \
                     patch("dossier_lean_canonical_dual.validate_writer_lean"):
                    return ready.validate_ready(tmp, token="synthetic")

            self.assertTrue(call()["ready"])
            self.assertEqual(len(call()["pairs"]), 6)
            projection["items"][0]["status"] = "missing"
            self.assertFalse(call()["ready"])
            projection["items"][0]["status"] = "ready"
            docs[original_rows[0]["appid"]]["final_dossier"][
                "game_identity"]["release_year"] = 1900
            with self.assertRaisesRegex(ValueError, "release year"):
                call()

    def test_future_signed_trial_without_owner_optin_is_suppressed(self):
        from test_dossier_notes_v2_batch_route import git, source_copy
        from test_dossier_notes_v2_generic_replay import issue_fixture
        import dossier_notes_v2_generic_replay as generic
        temp, repo = source_copy()
        try:
            issued = issue_fixture(repo, "bc" * 16, copies=False)
            git(repo, "checkout", "-b", "sandbox/" + issued["trial"])
            with patch.object(ready, "policy",
                              return_value={"activation_enabled": True}):
                result = ready.future_plan(
                    repo, trial_id=issued["trial"], token="synthetic-token")
            self.assertFalse(result["ready"])
            self.assertEqual(result["status"],
                             "suppressed_no_individual_owner_auto_grant")
        finally:
            temp.cleanup()

    def test_future_issuer_binds_baseline_git_blob_not_untrusted_year(self):
        from test_dossier_notes_v2_batch_route import git, source_copy
        from test_dossier_notes_v2_generic_replay import issue_fixture
        temp, repo = source_copy()
        try:
            issued = issue_fixture(
                repo, "de" * 16, lean_auto_writer=True, copies=False)
            git(repo, "checkout", "-b", "sandbox/" + issued["trial"])
            with patch.object(ready, "policy",
                              return_value={"activation_enabled": True}), \
                 patch.object(ready.batch, "authenticated_owner_run",
                              return_value=True):
                # Fixture has merely syntactically-valid baseline SHA strings,
                # not actual original strict evidence blobs. Future auto MUST
                # reject the authorization before it can reach writer/claim.
                with self.assertRaises(ValueError):
                    ready.future_plan(
                        repo, trial_id=issued["trial"], token="synthetic-token")
        finally:
            temp.cleanup()

    def test_claimed_failed_writer_is_suppressed_before_second_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            event_file = Path(temporary) / "event.json"
            event_file.write_text("{}", encoding="utf-8")
            env = {"GITHUB_EVENT_PATH": str(event_file)}
            trial = GRANT["trial_id"]
            signal = {"trial_id": trial, "source_signal_run_id": None,
                      "source_signal_sha": GRANT["frozen_sandbox_head"],
                      "event_kind": "owner_activation_catchup"}
            with patch.object(ready, "policy",
                              return_value={"activation_enabled": True}), \
                 patch.object(ready, "verify_source_signal",
                              return_value=signal), \
                 patch.object(ready, "verify_main_checkout"), \
                 patch.object(ready, "check_claim_ref",
                              return_value="a" * 40), \
                 patch.object(ready, "claim_once") as claim:
                result = ready.run(temporary, env)
            self.assertEqual(result["status"],
                             "suppressed_already_claimed_no_retry")
            self.assertFalse(result["writer_launched"])
            claim.assert_not_called()

    def test_attempt_claim_is_one_per_trial_and_replay_visible(self):
        with patch.object(ready.subprocess, "run",
                          return_value=SimpleNamespace(stdout="", returncode=0)):
            self.assertIsNone(ready.check_claim_ref(".", GRANT["trial_id"]))
        with patch.object(ready.subprocess, "run",
                          return_value=SimpleNamespace(stdout="a" * 40 +
                              "\trefs/heads/dossier-lean-auto-attempts/cdcdb4951e2fc98336729af75b954da4\n",
                              returncode=0)):
            self.assertEqual(ready.check_claim_ref(".", GRANT["trial_id"]), "a" * 40)
        with self.assertRaises(ValueError):
            ready.check_claim_ref(".", "../../spoofed")


if __name__ == "__main__":
    unittest.main()
 + '{GITHUB_ACTOR_ID}" = "315790060"', old)

    def test_actual_failed_manual_attempt_must_be_proven_not_ignored(self):
        valid = {
            "id": 45540222575, "event": "workflow_dispatch",
            "path": ready.batch.WRITER_WORKFLOW,
            "run_attempt": 1, "status": "completed",
            "conclusion": "failure",
            "head_sha": "147be762d217dc1e7dc53a6fbd896f323f6af08c",
            "head_branch": "main",
            "actor": {"id": int(ready.batch.OWNER_ID),
                      "login": ready.batch.OWNER_LOGIN},
            "triggering_actor": {"id": int(ready.batch.OWNER_ID),
                                 "login": ready.batch.OWNER_LOGIN},
        }
        with patch.object(ready, "_github_get", return_value=valid):
            self.assertTrue(ready.authentic_old_failure("offline-token"))
        for key, bad in (("run_attempt", 2), ("conclusion", "success"),
                         ("head_sha", "0" * 40), ("path", "evil.yml"),
                         ("status", "in_progress"),
                         ("actor", {"id": 1, "login": "spoofed"})):
            with self.subTest(key=key):
                altered = dict(valid)
                altered[key] = bad
                with patch.object(ready, "_github_get", return_value=altered):
                    with self.assertRaises(ValueError):
                        ready.authentic_old_failure("offline-token")
        with self.assertRaises(ValueError):
            ready.authentic_old_failure("")

    def test_wakeup_source_requires_specific_github_run_not_untrusted_push(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": ready.batch.REPOSITORY,
            "GITHUB_REPOSITORY_OWNER_ID": ready.batch.OWNER_ID,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": ready.batch.REPOSITORY + "/" +
                                ready.AUTO_WORKFLOW + "@refs/heads/main",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_RUN_ID": "9000",
            "GITHUB_EVENT_NAME": "workflow_run",
        }
        signal = {"workflow_run": {
            "event": "push", "status": "completed", "conclusion": "success",
            "run_attempt": 1, "path": ready.SIGNAL_WORKFLOW,
            "head_branch": "sandbox/" + GRANT["trial_id"],
            "head_sha": GRANT["frozen_sandbox_head"],
            "head_repository": {"full_name": ready.batch.REPOSITORY},
            "id": 98765,
        }}
        with patch.object(ready, "policy", return_value={"activation_enabled": True}):
            self.assertEqual(
                ready.verify_source_signal(signal, env)["source_signal_run_id"],
                98765)
            for key, bad in (
                ("conclusion", "failure"),
                ("run_attempt", 2),
                ("head_branch", "sandbox/dossier-notes-v2-unknown"),
                ("head_sha", "0" * 40),
                ("path", ".github/workflows/malicious.yml"),
                ("head_repository", {"full_name": "attacker/fork"}),
            ):
                with self.subTest(key=key):
                    modified = copy.deepcopy(signal)
                    modified["workflow_run"][key] = bad
                    with self.assertRaises(ValueError):
                        ready.verify_source_signal(modified, env)
            for key, bad in (
                ("GITHUB_REPOSITORY", "attacker/repo"),
                ("GITHUB_WORKFLOW_REF", "attacker/workflow"),
                ("GITHUB_RUN_ATTEMPT", "2"),
                ("GITHUB_REF", "refs/heads/untrusted"),
            ):
                with self.subTest(key=key):
                    modified = dict(env)
                    modified[key] = bad
                    with self.assertRaises(ValueError):
                        ready.verify_source_signal(signal, modified)

    def test_main_catchup_accepts_only_owner_activation_push(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": ready.batch.REPOSITORY,
            "GITHUB_REPOSITORY_OWNER_ID": ready.batch.OWNER_ID,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": ready.batch.REPOSITORY + "/" +
                                ready.AUTO_WORKFLOW + "@refs/heads/main",
            "GITHUB_RUN_ATTEMPT": "1", "GITHUB_RUN_ID": "9000",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_SHA": "f" * 40, "GITHUB_ACTOR_ID": ready.batch.OWNER_ID,
            "GITHUB_TRIGGERING_ACTOR": ready.batch.OWNER_LOGIN,
        }
        event = {
            "ref": "refs/heads/main", "created": False, "deleted": False,
            "forced": False, "after": "f" * 40,
            "repository": {"full_name": ready.batch.REPOSITORY},
            "sender": {"id": int(ready.batch.OWNER_ID)},
            "head_commit": {"modified": [
                "config/dossier_lean_writer_auto_ready_v1.json"
            ], "added": []},
        }
        with patch.object(ready, "policy", return_value={"activation_enabled": True}):
            self.assertEqual(ready.verify_source_signal(event, env)[
                "event_kind"], "owner_activation_catchup")
            for key, bad in (("forced", True), ("after", "0" * 40),
                             ("sender", {"id": 17}),
                             ("head_commit", {"modified": ["README.md"], "added": []})):
                with self.subTest(key=key):
                    modified = dict(event)
                    modified[key] = bad
                    with self.assertRaises(ValueError):
                        ready.verify_source_signal(modified, env)

    def test_exact_ready_validates_year_edition_and_every_terminal_receipt(self):
        # Synthetic dependency stand-ins: validates fail-closed orchestration.
        # Real Git object/writer transaction is exercised by existing sandbox
        # tests; this is NOT a full event -> writer -> push test.
        trial = GRANT["trial_id"]
        original_rows = GRANT["items"]
        pairs = ready.exact_pairs()
        fake_git = [
            SimpleNamespace(stdout=("sandbox/" + trial + "\n").encode()),
            SimpleNamespace(stdout=(GRANT["frozen_sandbox_head"] + "\n").encode()),
            SimpleNamespace(stdout=(GRANT["authorization_commit"] + "\n").encode()),
        ]
        issuer = {
            "authority_origin": "generic_owner_request",
            "semantic_execution_authorized": True,
            "authorization_commit": GRANT["authorization_commit"],
            "github_authorization_run_id": GRANT["owner_source_actions_run_id"],
            "request_commit": GRANT["original_request_commit"],
        }
        frozen = {x["appid"]: x for x in original_rows}
        projection = {"items": [{"appid": x["appid"], "status": "ready"}
                                for x in original_rows]}
        work_by_app = {}
        for r in original_rows:
            assignment = {k: r[k] for k in ("appid", "title",
                                            "assignment_id", "group_sequence")}
            work_by_app[r["appid"]] = {
                "status": "ready_for_autonomous_assembly",
                "assignment": assignment,
                "research_transport": {},
                "output_path": "synthetic/" + r["appid"],
            }

        def work(repo, **kw):
            return work_by_app[kw["appid"]]

        docs = {}
        for r in original_rows:
            a = r["appid"]
            docs[a] = {
                "outcome": "assembled_candidate_ready",
                "assignment": work_by_app[a]["assignment"],
                "research_transport": {},
                "final_dossier": {
                    "game_identity": {"release_year": r["original_release_year"]}
                },
            }

        def doc(repo, sha, path):
            return docs[path.split("/")[-1]]

        with tempfile.TemporaryDirectory() as tmp:
            def call():
                with patch.object(ready, "policy",
                                  return_value={"activation_enabled": True}), \
                     patch.object(ready, "git", side_effect=list(fake_git)), \
                     patch.object(ready.batch, "issuer_structure", return_value=issuer), \
                     patch.object(ready.batch, "authenticated_owner_run", return_value=True), \
                     patch.object(ready.generic, "policy", return_value={}), \
                     patch.object(ready, "authentic_old_failure", return_value=True), \
                     patch("dossier_lean_canonical_dual.require_isolated_sandbox_writer",
                           return_value=frozen), \
                     patch.object(ready.v2, "individual_final_readiness",
                                  return_value=projection), \
                     patch.object(ready, "require_batch_terminal_receipts"), \
                     patch.object(ready.v2, "inspect_assembly",
                                  return_value={
                                      "status": "strict_item_valid_pending_existing_atomic_group_ingest"}), \
                     patch.object(ready.v2, "assembly_work", side_effect=work), \
                     patch.object(ready, "json_at", side_effect=doc), \
                     patch("dossier_lean_canonical_dual.validate_writer_lean"):
                    return ready.validate_ready(tmp, token="synthetic")

            self.assertTrue(call()["ready"])
            self.assertEqual(len(call()["pairs"]), 6)
            projection["items"][0]["status"] = "missing"
            self.assertFalse(call()["ready"])
            projection["items"][0]["status"] = "ready"
            docs[original_rows[0]["appid"]]["final_dossier"][
                "game_identity"]["release_year"] = 1900
            with self.assertRaisesRegex(ValueError, "release year"):
                call()

    def test_future_signed_trial_without_owner_optin_is_suppressed(self):
        from test_dossier_notes_v2_batch_route import git, source_copy
        from test_dossier_notes_v2_generic_replay import issue_fixture
        import dossier_notes_v2_generic_replay as generic
        temp, repo = source_copy()
        try:
            issued = issue_fixture(repo, "bc" * 16, copies=False)
            git(repo, "checkout", "-b", "sandbox/" + issued["trial"])
            with patch.object(ready, "policy",
                              return_value={"activation_enabled": True}):
                result = ready.future_plan(
                    repo, trial_id=issued["trial"], token="synthetic-token")
            self.assertFalse(result["ready"])
            self.assertEqual(result["status"],
                             "suppressed_no_individual_owner_auto_grant")
        finally:
            temp.cleanup()

    def test_future_issuer_binds_baseline_git_blob_not_untrusted_year(self):
        from test_dossier_notes_v2_batch_route import git, source_copy
        from test_dossier_notes_v2_generic_replay import issue_fixture
        temp, repo = source_copy()
        try:
            issued = issue_fixture(
                repo, "de" * 16, lean_auto_writer=True, copies=False)
            git(repo, "checkout", "-b", "sandbox/" + issued["trial"])
            with patch.object(ready, "policy",
                              return_value={"activation_enabled": True}), \
                 patch.object(ready.batch, "authenticated_owner_run",
                              return_value=True):
                # Fixture has merely syntactically-valid baseline SHA strings,
                # not actual original strict evidence blobs. Future auto MUST
                # reject the authorization before it can reach writer/claim.
                with self.assertRaises(ValueError):
                    ready.future_plan(
                        repo, trial_id=issued["trial"], token="synthetic-token")
        finally:
            temp.cleanup()

    def test_attempt_claim_is_one_per_trial_and_replay_visible(self):
        with patch.object(ready.subprocess, "run",
                          return_value=SimpleNamespace(stdout="", returncode=0)):
            self.assertIsNone(ready.check_claim_ref(".", GRANT["trial_id"]))
        with patch.object(ready.subprocess, "run",
                          return_value=SimpleNamespace(stdout="a" * 40 +
                              "\trefs/heads/dossier-lean-auto-attempts/cdcdb4951e2fc98336729af75b954da4\n",
                              returncode=0)):
            self.assertEqual(ready.check_claim_ref(".", GRANT["trial_id"]), "a" * 40)
        with self.assertRaises(ValueError):
            ready.check_claim_ref(".", "../../spoofed")


if __name__ == "__main__":
    unittest.main()
