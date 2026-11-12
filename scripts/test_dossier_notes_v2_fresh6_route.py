#!/usr/bin/env python3
"""Synthetic Git adversarial security tests for a fresh-six sandbox issuer.

All commits are in a disposable local repo. No GitHub API calls or semantics.
"""
import itertools
import json
import os
import subprocess
import textwrap
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import dossier_notes_v2_fresh6_preflight as preflight
import dossier_notes_v2_fresh6_route as fresh
import dossier_notes_v2_per_item_receipts as receipts
import dossier_notes_v2_fresh6_issuer as issuer
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import blob, parent


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args],
                       check=True, capture_output=True, text=True)
    return p.stdout.strip()


def add(repo, path, doc, message):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(fresh.canonical(doc) if isinstance(doc, dict) else doc)
    git(repo, "add", "--", path)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


class Fresh6IssuerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="fresh6-gh-control-test-")
        cls.repo = Path(cls.temp.name) / "sandbox"
        subprocess.run(["git", "clone", "--quiet", "--shared", str(ROOT),
                        str(cls.repo)], check=True, capture_output=True)
        git(cls.repo, "config", "user.name", "fixture")
        git(cls.repo, "config", "user.email", "fixture@example.invalid")
        git(cls.repo, "checkout", "-b", "fixture/fresh6")
        cls.base = git(cls.repo, "rev-parse", "HEAD")
        cls.c = fresh.scope(cls.repo)
        cls.bp = fresh.manifest_blueprint(cls.repo)
        cls.items = fresh.rows(cls.repo)
        g = {
            "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-GRANT",
            "schema_version": 1, "trial_id": fresh.TRIAL,
            "base_main_sha": cls.base,
            "source_pins": fresh.pins(cls.c),
            "manifest_path": fresh.MANIFEST_PATH,
            "manifest_blob_sha": cls.bp["blob_sha"],
            "owner_login": fresh.OWNER_LOGIN,
            "owner_actor_id": fresh.OWNER_ID,
            "scope": "one_new_fresh6_issuer_only_not_original18",
            "semantic_execution_approved": False,
            "production_approved": False,
            "canonical_ingest_approved": False,
        }
        cls.grant = add(cls.repo, fresh.GRANT_PATH, g, "fixture grant")
        cls.manifest = add(cls.repo, fresh.MANIFEST_PATH, cls.bp["bytes"], "fixture manifest")
        cls.nonce = "ab" * 16
        cls.marker = add(cls.repo,
                         "data/control/dossier_notes_v2/run_starts/" + cls.nonce + ".json",
                         {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
                          "trial_id":fresh.TRIAL,"nonce":cls.nonce},
                         "fixture marker")
        auth = {
            "schema": "DOSSIER-NOTES-V2-FRESH6-OWNER-AUTHORIZATION",
            "schema_version": 1, "trial_id": fresh.TRIAL,
            "marker_commit": cls.marker,
            "marker_parent": cls.manifest,
            "manifest_blob_sha": cls.bp["blob_sha"],
            "human_grant_commit": cls.grant,
            "human_grant_blob_sha": blob(cls.repo, cls.grant, fresh.GRANT_PATH),
            "owner_actor_id": fresh.OWNER_ID,
            "owner_login": fresh.OWNER_LOGIN,
            "github_authorization_run_id": "1234567",
            "scope": "one_manual_fresh6_research_and_assembly_sandbox_only",
            "semantic_execution_authorized": True,
            "assembly_authorized": True,
            "sandbox_writer_authorized": True,
            "production_authorized": False,
            "canonical_acceptance": False,
        }
        cls.authorizer = add(cls.repo, fresh.AUTH_PATH, auth, "fixture authorization")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_issuer_exact_three_parent_chain_and_real_source_pin(self):
        self.assertEqual(parent(self.repo, self.manifest), self.grant)
        self.assertEqual(parent(self.repo, self.marker), self.manifest)
        self.assertEqual(parent(self.repo, self.authorizer), self.marker)
        self.assertEqual([x["appid"] for x in self.items],
                         ["1000010","102600","1029690","49520","499180","501590"])
        self.assertEqual(len({x["assignment_id"] for x in self.items}), 6)
        evidence = fresh.issuer_structure(
            self.repo, marker_commit=self.marker,
            authorization_commit=self.authorizer)
        self.assertEqual(evidence["github_authorization_run_id"], "1234567")
        self.assertFalse(evidence["github_run_authenticated"])
        self.assertEqual(evidence["manifest_blob_sha"], self.bp["blob_sha"])

    def test_core_v2_manifest_and_transport_delegation_isolated(self):
        m, sha = v2._manifest(self.repo, self.marker, fresh.TRIAL)
        self.assertEqual(m["items"], self.items)
        self.assertEqual(sha, self.bp["blob_sha"])
        evidence = receipts.issuer_structure(
            self.repo, marker_commit=self.marker, trial_id=fresh.TRIAL,
            authorization_commit=self.authorizer)
        self.assertEqual(evidence["authorization_commit"], self.authorizer)
        self.assertEqual(v2.frozen_assignment(
            self.repo, marker_commit=self.marker, trial_id=fresh.TRIAL,
            appid="499180")["title"], "Braid, Anniversary Edition")
        with self.assertRaises(v2.NotesV2Error):
            v2.frozen_assignment(self.repo, marker_commit=self.marker,
                                 trial_id=fresh.TRIAL, appid="2138710")

    def test_prior_original18_marker_and_missing_authority_are_rejected(self):
        with self.assertRaises((ValueError, v2.NotesV2Error)):
            fresh.issuer_structure(self.repo,
                marker_commit="bb63cc291eba5aa8fc56e2920ef84d131ac28a4f",
                authorization_commit=self.authorizer)
        with self.assertRaises((ValueError, v2.NotesV2Error)):
            fresh.issuer_structure(self.repo, marker_commit=self.marker,
                                   authorization_commit=self.marker)

    def test_real_github_owner_run_attestation_no_fake_actor_or_unfinished(self):
        doc = {
            "id":1234567, "event":"workflow_dispatch",
            "head_branch":"main","status":"completed","conclusion":"success",
            "run_attempt":1,"path":fresh.AUTHORIZE_WORKFLOW,
            "actor":{"id":int(fresh.OWNER_ID),"login":fresh.OWNER_LOGIN},
        }
        anchor = fresh.issuer_structure(
            self.repo, marker_commit=self.marker,
            authorization_commit=self.authorizer)
        with patch.object(receipts, "_github_get", return_value=doc):
            result = receipts.verify_scoped_semantic_run(
                self.repo,marker_commit=self.marker,trial_id=fresh.TRIAL,
                authorization_commit=self.authorizer,
                github_repository=fresh.REPOSITORY, github_token="synthetic-only")
            self.assertTrue(result["github_run_authenticated"])
        for wrong in [
            {"actor":{"id":123,"login":"attacker"}},
            {"conclusion":"failure"},
            {"run_attempt":2},
            {"path":".github/workflows/authorize-dossier-shadow-research-feasibility.yml"},
            {"event":"pull_request"},
        ]:
            with self.subTest(wrong=wrong):
                with patch.object(receipts, "_github_get", return_value={**doc, **wrong}):
                    with self.assertRaises(ValueError):
                        fresh.authenticated_owner_run(anchor, "synthetic-only")

    def test_wrong_trial_or_extra_original18_grant_does_not_rebind(self):
        with self.assertRaises(v2.NotesV2Error):
            v2._manifest(self.repo, self.marker, "dossier-notes-v2-original18-first")
        with self.assertRaises(v2.NotesV2Error):
            v2.manifest_blueprint(fresh.TRIAL, v2._original_rows())

    def test_public_transport_fails_wrong_fresh6_remote_branch(self):
        receipts._require_fresh6_target(fresh.TRIAL, fresh.BRANCH)
        with self.assertRaises(v2.NotesV2Error):
            receipts._require_fresh6_target(fresh.TRIAL, "sandbox/dossier-notes-v2-original18-first")
        with self.assertRaises(v2.NotesV2Error):
            receipts._require_fresh6_target(fresh.TRIAL, "sandbox/forged-six")
        receipts._require_fresh6_target("dossier-notes-v2-original18-first",
                                        "sandbox/dossier-notes-v2-original18-first")

    def test_exactly_one_writer_mode_actual_bash_matrix(self):
        workflow = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text()
        section = workflow.split(
            "      - name: Reject ambiguous manual V2 writer selections", 1
        )[1].split("      - name: Drain separately authorized V2 items", 1)[0]
        shell = section.split("        run: |\n", 1)[1]
        shell = textwrap.dedent(shell)
        for flags in itertools.product(("false", "true"), repeat=3):
            with self.subTest(flags=flags):
                environment = {
                    **os.environ,
                    "CANONICAL_WRITER": flags[0],
                    "PILOT_WRITER": flags[1],
                    "FRESH6_WRITER": flags[2],
                }
                executed = subprocess.run(
                    ["bash", "-euc", shell], env=environment,
                    capture_output=True, text=True)
                self.assertEqual(executed.returncode == 0,
                                 flags.count("true") == 1,
                                 executed.stdout + "\n" + executed.stderr)

    def test_fresh6_isolated_writer_rejects_wrong_ref_then_keeps_empty_safe(self):
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        options = {
            "repo": self.repo, "marker_commit": self.marker,
            "trial_id": fresh.TRIAL, "item_commits": {},
            "store_dir": self.repo / "data/control/dossier_notes_v2/fresh6_pilot_store",
            "accepted_dir": self.repo / "data/control/dossier_notes_v2/fresh6_pilot_accepted",
            "offline_fixture": False, "trial_sandbox": True,
        }
        with self.assertRaisesRegex(ValueError, "fresh6 writer needs real owner"):
            drain_buffered_groups(notes_v2=options)
        git(self.repo, "checkout", "-b", fresh.BRANCH)
        env = {
            "GITHUB_ACTIONS":"true",
            "GITHUB_EVENT_NAME":"workflow_dispatch",
            "GITHUB_REF":"refs/heads/main",
            "GITHUB_WORKFLOW_REF":fresh.REPOSITORY + "/.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml@refs/heads/main",
            "GITHUB_REPOSITORY":fresh.REPOSITORY,
            "GITHUB_ACTOR_ID":fresh.OWNER_ID,
            "GITHUB_REPOSITORY_OWNER_ID":fresh.OWNER_ID,
            "GITHUB_ACTOR":fresh.OWNER_LOGIN,
            "GITHUB_TRIGGERING_ACTOR":fresh.OWNER_LOGIN,
            "GITHUB_RUN_ATTEMPT":"1",
            "GITHUB_TOKEN":"synthetic-no-network",
        }
        try:
            with patch.dict(os.environ, env), patch.object(
                    fresh, "authenticated_owner_run", return_value=True):
                result = drain_buffered_groups(notes_v2=options)
            self.assertEqual(len(result["items"]), 6)
            self.assertTrue(all(i["status"] == "missing" for i in result["items"]))
            self.assertIs(result["canonical_acceptance"], False)
            self.assertFalse(options["store_dir"].exists())
            self.assertFalse(options["accepted_dir"].exists())
        finally:
            git(self.repo,"checkout","fixture/fresh6")

    def test_fresh6_mixed_ready_and_incomplete_persists_only_ready_in_sandbox(self):
        """A real strict-ready item survives a sibling's typed incomplete result.

        This is a disposable Git fixture, not actual player evidence or live
        semantic authorization. Test the fresh6-specific writer, not a mock
        of its item selection or persistence.
        """
        from datetime import datetime, timezone
        from taste_steam_review_dossier_test_fixture import web_dossier
        from taste_steam_review_dossier_buffered import drain_buffered_groups

        first, second = self.items[:2]
        # The writer intentionally refuses any branch except the exact sandbox.
        # Reset the dedicated fixture ref, irrespective of test ordering.
        git(self.repo, "checkout", "-B", fresh.BRANCH, self.authorizer)
        try:
            commits = {}
            for item in (first, second):
                appid = item["appid"]
                assignment = v2.frozen_assignment(
                    self.repo, marker_commit=self.marker,
                    trial_id=fresh.TRIAL, appid=appid)
                note = {
                    "schema": "DOSSIER-RESEARCH-NOTES-V2",
                    "schema_version": 2, "assignment": assignment,
                    "notes_text": "", "source_log": [],
                    "research_status": "no_verifiable_findings",
                }
                commits[appid] = {
                    "research_commit": add(
                        self.repo, v2._path("research", assignment), note,
                        "fixture: safe fresh6 Research " + appid),
                    "assembly_commit": None,
                }

            work_first = v2.assembly_work(
                self.repo, marker_commit=self.marker, trial_id=fresh.TRIAL,
                appid=first["appid"],
                research_commit=commits[first["appid"]]["research_commit"])
            self.assertEqual(work_first["status"], "ready_for_autonomous_assembly")
            dossier = web_dossier(
                first["appid"], datetime.now(timezone.utc),
                title=first["title"])
            ready = v2.candidate_assembly(
                work_first, outcome="assembled_candidate_ready",
                final_dossier=dossier)
            commits[first["appid"]]["assembly_commit"] = add(
                self.repo, work_first["output_path"], ready,
                "fixture: strict-ready fresh6 Assembly")

            work_second = v2.assembly_work(
                self.repo, marker_commit=self.marker, trial_id=fresh.TRIAL,
                appid=second["appid"],
                research_commit=commits[second["appid"]]["research_commit"])
            self.assertEqual(work_second["status"], "ready_for_autonomous_assembly")
            incomplete = v2.candidate_assembly(
                work_second, outcome="assembly_missing_evidence",
                diagnostic="Synthetic fixture: independently verified evidence unavailable")
            commits[second["appid"]]["assembly_commit"] = add(
                self.repo, work_second["output_path"], incomplete,
                "fixture: incomplete fresh6 Assembly")

            self.assertEqual(v2.inspect_assembly(
                self.repo, marker_commit=self.marker, trial_id=fresh.TRIAL,
                appid=first["appid"],
                research_commit=commits[first["appid"]]["research_commit"],
                result_commit=commits[first["appid"]]["assembly_commit"])["status"],
                "strict_item_valid_pending_existing_atomic_group_ingest")
            self.assertEqual(v2.inspect_assembly(
                self.repo, marker_commit=self.marker, trial_id=fresh.TRIAL,
                appid=second["appid"],
                research_commit=commits[second["appid"]]["research_commit"],
                result_commit=commits[second["appid"]]["assembly_commit"])["status"],
                "assembly_missing_evidence")

            store = self.repo / "data/control/dossier_notes_v2/fresh6_pilot_store"
            accepted = self.repo / "data/control/dossier_notes_v2/fresh6_pilot_accepted"
            options = {
                "repo": self.repo, "marker_commit": self.marker,
                "trial_id": fresh.TRIAL, "item_commits": commits,
                "store_dir": store, "accepted_dir": accepted,
                "offline_fixture": False, "trial_sandbox": True,
            }
            env = {
                "GITHUB_ACTIONS": "true",
                "GITHUB_EVENT_NAME": "workflow_dispatch",
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_WORKFLOW_REF": fresh.REPOSITORY
                    + "/.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml@refs/heads/main",
                "GITHUB_REPOSITORY": fresh.REPOSITORY,
                "GITHUB_REPOSITORY_OWNER_ID": fresh.OWNER_ID,
                "GITHUB_ACTOR_ID": fresh.OWNER_ID,
                "GITHUB_ACTOR": fresh.OWNER_LOGIN,
                "GITHUB_TRIGGERING_ACTOR": fresh.OWNER_LOGIN,
                "GITHUB_RUN_ATTEMPT": "1",
                "GITHUB_TOKEN": "synthetic-no-network",
            }
            with patch.dict(os.environ, env), patch.object(
                    fresh, "authenticated_owner_run", return_value=True):
                result = drain_buffered_groups(notes_v2=options)

            by_appid = {row["appid"]: row for row in result["items"]}
            self.assertEqual(len(by_appid), 6)
            self.assertEqual(by_appid[first["appid"]]["status"],
                             "persisted_pending_github_commit")
            self.assertEqual(by_appid[second["appid"]]["status"], "invalid")
            self.assertTrue(all(
                row["status"] == "missing" for row in result["items"][2:]))
            self.assertIs(result["canonical_acceptance"], False)

            cache = store / ("App_" + first["appid"] + ".json")
            rejected_cache = store / ("App_" + second["appid"] + ".json")
            receipt = accepted / fresh.TRIAL / "g000001" / (
                first["appid"] + "--" + first["assignment_id"] + ".json")
            self.assertTrue(cache.is_file())
            self.assertEqual(json.loads(cache.read_text(encoding="utf-8")), dossier)
            self.assertTrue(receipt.is_file())
            saved = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(saved["schema"], "DOSSIER-NOTES-V2-ISOLATED-TRIAL-RECEIPT-V1")
            self.assertEqual(saved["assignment"]["appid"], first["appid"])
            self.assertEqual(saved["assembly_commit"],
                             commits[first["appid"]]["assembly_commit"])
            self.assertFalse(rejected_cache.exists())

            # Same two-path atomic sandbox commit as the manual writer workflow.
            git(self.repo, "add", "--", str(store.relative_to(self.repo)),
                str(accepted.relative_to(self.repo)))
            staged = set(git(self.repo, "diff", "--cached", "--name-only").splitlines())
            self.assertEqual(staged, {
                str(cache.relative_to(self.repo)),
                str(receipt.relative_to(self.repo)),
            })
            git(self.repo, "commit", "-m", "fixture: persist one isolated fresh6 item")
            self.assertEqual(set(git(
                self.repo, "diff-tree", "--no-commit-id", "--name-only",
                "-r", "HEAD").splitlines()), staged)
            self.assertEqual(git(self.repo, "status", "--porcelain"), "")

            # The same immutable binding must not generate a second receipt.
            with patch.dict(os.environ, env), patch.object(
                    fresh, "authenticated_owner_run", return_value=True):
                repeated = drain_buffered_groups(notes_v2=options)
            again = {row["appid"]: row for row in repeated["items"]}
            self.assertEqual(again[first["appid"]]["status"],
                             "already_persisted_same_binding")
            self.assertEqual(again[second["appid"]]["status"], "invalid")
            self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        finally:
            git(self.repo, "checkout", "fixture/fresh6")


    def test_full_two_dispatch_issuer_local_bare_git_fixture_only(self):
        # This deliberately invokes the pure issuer functions without the
        # real GitHub Actions dispatch gate. It tests the deterministic Git
        # chain against a disposable local bare remote, never claims consent.
        with tempfile.TemporaryDirectory(prefix="fresh6-bare-issuer-") as tmp:
            origin = Path(tmp) / "origin.git"
            work = Path(tmp) / "work"
            subprocess.run(["git","init","--bare","--quiet",str(origin)],
                           check=True, capture_output=True)
            subprocess.run(["git","clone","--quiet","--shared",str(ROOT),str(work)],
                           check=True, capture_output=True)
            git(work,"config","user.name","fixture")
            git(work,"config","user.email","fixture@example.invalid")
            git(work,"remote","set-url","origin",str(origin))
            git(work,"checkout","-B","main")
            base = git(work,"rev-parse","HEAD")
            git(work,"push","origin","HEAD:refs/heads/main")
            result = issuer.freeze(work, base)
            self.assertFalse(result["semantic_execution_authorized"])
            self.assertIsNone(result["authorization_commit"])
            with self.assertRaises(ValueError):
                issuer.freeze(work, base)
            git(work,"checkout","main")
            authorized = issuer.authorize(
                work, base, result["marker_commit"],
                {"GITHUB_RUN_ID":"22334455"})
            self.assertTrue(authorized["semantic_execution_authorized"])
            self.assertEqual(authorized["github_authorization_run_id"], "22334455")
            self.assertEqual(git(work,"ls-remote","origin",
                                 "refs/heads/" + fresh.BRANCH).split()[0],
                             authorized["authorization_commit"])
            git(work,"checkout","main")
            with self.assertRaises(ValueError):
                issuer.authorize(work, base, result["marker_commit"],
                                 {"GITHUB_RUN_ID":"22334456"})
            fake_env = {
                "GITHUB_ACTIONS":"true", "GITHUB_EVENT_NAME":"workflow_dispatch",
                "GITHUB_REPOSITORY":fresh.REPOSITORY,
                "GITHUB_REPOSITORY_OWNER_ID":fresh.OWNER_ID,
                "GITHUB_ACTOR_ID":fresh.OWNER_ID,
                "GITHUB_ACTOR":fresh.OWNER_LOGIN,
                "GITHUB_TRIGGERING_ACTOR":fresh.OWNER_LOGIN,
                "GITHUB_REF":"refs/heads/main",
                "GITHUB_WORKFLOW_REF":fresh.REPOSITORY + "/" + fresh.ISSUE_WORKFLOW + "@refs/heads/main",
                "GITHUB_SHA":base,
                "GITHUB_RUN_ATTEMPT":"1", "GITHUB_RUN_ID":"123456",
            }
            with self.assertRaisesRegex(ValueError, "canonical GitHub repository"):
                issuer.guard(work,"freeze",base,issuer.FREEZE_CONFIRM,fake_env)

    def test_no_automatic_real_semantic_or_production_power_from_contract(self):
        c = fresh.scope(self.repo)
        for name in preflight.OFF_FLAGS:
            self.assertIs(c[name], False)


if __name__ == "__main__":
    unittest.main()
