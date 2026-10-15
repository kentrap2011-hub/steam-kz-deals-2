#!/usr/bin/env python3
"""Only disposable Git tests: shadow Research→Assembly, no semantic calls."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dossier_shadow_18_assembly_stage_b as stage
from dossier_shadow_18_assembly_sandbox import _decision
from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_staging import blob, git


class ShadowAssemblyStageBTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="dossier-stage-b-git-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.sh("init", "-b", stage.BRANCH)
        self.sh("config", "user.name", "Synthetic test")
        self.sh("config", "user.email", "synthetic@example.invalid")
        prompt = Path(__file__).resolve().parents[1] / stage.PROMPT
        contract = Path(__file__).resolve().parents[1] / stage.CONTRACT
        self.save(stage.PROMPT, prompt.read_text(encoding="utf-8"))
        self.save(stage.CONTRACT, contract.read_text(encoding="utf-8"))
        self.rbuffer = stage.PREFIX + "/research_buffer.json"
        research_manifest = {
            "schema": "SYNTHETIC-RESEARCH-ONLY",
            "research_buffer_id": "e" * 64,
        }
        self.save(self.rbuffer, research_manifest)
        self.commit("Fixture prepared old Research sandbox")
        self.research_parent = self.head()
        self.rnonce = "a" * 32
        self.save(stage.PREFIX + "/run_starts/" + self.rnonce + ".json", {
            "schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
            "schema_version": 1, "trial_id": stage.TRIAL, "nonce": self.rnonce,
        })
        self.research_marker = self.commit("Synthetic Research marker")
        self.items = []
        for g in _decision()["scope"]["groups"]:
            for i, appid in enumerate(g["appids"]):
                self.items.append({
                    "group_sequence": g["sequence"], "item_index": i, "appid": appid,
                    "assignment": {"assignment_id": f"research-fixture-{appid}",
                                   "title": "Synthetic original " + appid,
                                   "web_evidence_contract_binding": {"fixture": 1}},
                })
        self.trial = {
            "marker_commit": self.research_marker,
            "marker_parent": self.research_parent,
            "nonce": self.rnonce,
            "buffer_path": self.rbuffer,
            "buffer_blob_sha": blob(self.root, self.research_parent, self.rbuffer),
            "items": self.items, "sandbox_semantics_authorized": True,
        }
        self.freeze_patch = patch.object(stage, "frozen_trial",
                                         side_effect=lambda *a, **k: self.trial)
        self.freeze_patch.start()
        self.addCleanup(self.freeze_patch.stop)

    def sh(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def save(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value if isinstance(value, str) else json.dumps(value),
                     encoding="utf-8")

    def commit(self, message):
        self.sh("add", "-A")
        self.sh("commit", "-m", message)
        return self.head()

    def head(self):
        return self.sh("rev-parse", "HEAD")

    def issue(self):
        with patch.object(stage, "inactive_assembly_gate"):
            buffer = stage.prepare(self.root,
                                   research_marker_commit=self.research_marker)
        self.save(stage.BUFFER, buffer)
        self.commit("Synthetic GitHub buffer")
        self.anonce = "b" * 32
        self.apath = stage.MARKERS + "/" + self.anonce + ".json"
        self.save(self.apath, {
            "schema": "DOSSIER-SHADOW-ASSEMBLY-RUN-START-V1",
            "schema_version": 1, "trial_id": stage.TRIAL, "nonce": self.anonce,
            "issuer_workflow": "issue-dossier-shadow-18-assembly.yml",
            "issuer_run_id": 12345,
            "buffer_blob_sha": blob(self.root, "HEAD", stage.BUFFER),
        })
        self.amarker = self.commit("Synthetic mock issuer marker")
        return buffer

    def test_01_freeze_is_exact_original_six_by_three_and_no_custom_scope(self):
        with patch.object(stage, "inactive_assembly_gate"):
            buffer = stage.prepare(self.root, research_marker_commit=self.research_marker)
        self.assertEqual(buffer["groups"], [3, 8, 13, 15, 18, 20])
        self.assertEqual(len(buffer["items"]), 18)
        self.assertEqual(buffer["buffer_id"], canonical_sha256({
            k: v for k, v in buffer.items() if k != "buffer_id"}))
        self.assertFalse(buffer["canonical_acceptance"])
        self.assertEqual(buffer["production_writes"], [])
        self.assertEqual(len({x["assembly_assignment_id"] for x in buffer["items"]}), 18)

    def test_02_research_gate_and_original_child_identity_fail_closed(self):
        self.trial["sandbox_semantics_authorized"] = False
        with patch.object(stage, "inactive_assembly_gate"):
            with self.assertRaisesRegex(ValueError, "blocked"):
                stage.prepare(self.root, research_marker_commit=self.research_marker)
        self.trial["sandbox_semantics_authorized"] = True
        self.items[1]["appid"] = "999"
        with patch.object(stage, "inactive_assembly_gate"):
            with self.assertRaisesRegex(ValueError, "original"):
                stage.prepare(self.root, research_marker_commit=self.research_marker)

    def test_03_no_original_research_marker_lineage_cannot_freeze(self):
        with patch.object(stage, "inactive_assembly_gate"):
            with self.assertRaises(ValueError):
                stage.prepare(self.root, research_marker_commit="0" * 40)

    def test_04_assembly_marker_parent_and_workflow_origin_are_strict(self):
        self.issue()
        parent, nonce, source = stage.marker_parent(self.root, self.amarker)
        self.assertEqual(nonce, self.anonce)
        self.assertEqual(parent, self.sh("rev-parse", self.amarker + "^"))
        self.assertEqual(source["issuer_run_id"], 12345)
        self.save("reviews/dossier_shadow_offline/extra.json", {})
        self.save(stage.MARKERS + "/" + "c" * 32 + ".json", {"bad": True})
        bad = self.commit("Synthetic marker plus extra path")
        with self.assertRaises(ValueError):
            stage.marker_parent(self.root, bad)

    def test_05_marker_claim_without_Github_workflow_run_proof_rejected(self):
        self.issue()
        self.save(self.apath, {"schema": "FAKE", "issuer_run_id": 0})
        forged = self.commit("Tamper marker file; do not accept")
        with self.assertRaises(ValueError):
            stage.marker_parent(self.root, forged)
        self.assertNotEqual(blob(self.root, self.amarker, self.apath),
                            blob(self.root, "HEAD", self.apath))

    def test_06_no_research_A_B_and_C_can_be_ready_in_original_order(self):
        self.issue()
        with patch.object(stage, "inactive_assembly_gate"), patch.object(
                stage, "inspect_transport",
                return_value={"result_commit": self.research_marker,
                              "path": self.rbuffer, "git_blob_sha": "c" * 40,
                              "raw_sha256": "d" * 64, "canonical_sha256": "e" * 64}):
            status = stage.inspect(self.root, marker_commit=self.amarker,
                research_commits={
                    self.items[1]["appid"]: self.research_marker,
                    self.items[2]["appid"]: self.research_marker,
                })
        self.assertEqual([r["status"] for r in status["rows"][:3]],
                         ["research_not_submitted", "ready", "ready"])
        self.assertEqual(status["ready_count"], 2)
        self.assertEqual(status["semantic_attempts"], 0)
        self.assertFalse(status["deep_ready"])

    def test_07_invalid_A_is_item_local_and_foreign_commit_map_fails(self):
        self.issue()
        def origin_check(repo, *, trial, item, result_commit):
            if item["item_index"] == 0:
                raise ValueError("wrong child product/original work release-year")
            return {"result_commit": result_commit, "path": self.rbuffer,
                    "git_blob_sha": "c" * 40,
                    "raw_sha256": "d" * 64, "canonical_sha256": "e" * 64}
        with patch.object(stage, "inactive_assembly_gate"), patch.object(
                stage, "inspect_transport", side_effect=origin_check):
            status = stage.inspect(self.root, marker_commit=self.amarker,
                research_commits={x["appid"]: self.research_marker
                                  for x in self.items[:3]})
            with self.assertRaisesRegex(ValueError, "foreign"):
                stage.inspect(self.root, marker_commit=self.amarker,
                              research_commits={"bad": self.research_marker})
        self.assertEqual([r["status"] for r in status["rows"][:3]],
                         ["research_transport_invalid", "ready", "ready"])
        self.assertTrue(all(r["attempt_consumed"] is False for r in status["rows"]))

    def test_08_overwritten_buffer_or_wrong_branch_marker_is_fatal(self):
        self.issue()
        self.save(stage.BUFFER, {"unbound": "latest"})
        self.commit("Rewrite exact sandbox Assembly buffer")
        with patch.object(stage, "inactive_assembly_gate"):
            with self.assertRaises(ValueError):
                stage.frozen(self.root, marker_commit=self.amarker)

    def test_09_assembly_single_candidate_commit_cannot_touch_production(self):
        self.issue()
        appid = self.items[0]["appid"]
        output = stage.result_path(stage.prepare(
            self.root, research_marker_commit=self.research_marker)["items"][0])
        self.save(output, {"fake": True})
        self.save("data/cache/taste_steam_review_dossiers/bad.json", {"bad": True})
        commit = self.commit("Adversarial result plus canonical cache edit")
        row = {"appid": appid, "output_path": output}
        with patch.object(stage, "inspect", return_value={"rows": [row]}):
            with self.assertRaises(ValueError):
                stage.verify_candidate(self.root, marker_commit=self.amarker,
                    research_commits={}, appid=appid, result_commit=commit)

    def test_10_only_explicit_GitHub_dispatch_branch_can_issue(self):
        with patch.dict("os.environ", {"GITHUB_ACTIONS": "true",
                     "GITHUB_EVENT_NAME": "workflow_dispatch",
                     "GITHUB_REF_NAME": "main",
                     "GITHUB_WORKFLOW_REF": "not-an-issuer"}, clear=True):
            with self.assertRaises(ValueError):
                stage._issuer_env()


if __name__ == "__main__":
    unittest.main()
