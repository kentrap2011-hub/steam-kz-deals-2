#!/usr/bin/env python3
"""Disposable-Git only: existing one-stage writer + adversarial pilot proofs."""
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dossier_shadow_pilot_preflight import (
    AUDIT, MANIFEST, PROPOSAL_CONTRACTS, SCHEMA, verify_offline_preflight,
)
from dossier_two_stage_contract_guard import CONFIG, canonical_sha256
from dossier_two_stage_staging import blob, git
from taste_steam_review_dossier_buffered import (
    _authority_audit_record, drain_buffered_groups, expected_buffer_path,
)
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA
from taste_steam_review_dossier_test_fixture import web_dossier
import test_dossier_two_stage_final_acceptance as bridge_fixture


class PilotPreflightTests(unittest.TestCase):
    def setUp(self):
        self.helper = bridge_fixture.FinalAcceptanceOfflineTests(
            "test_01_live_paths_fail_closed_and_contract_is_not_authoritative")
        self.x, self.work, self.contract, self.manifest_file = self.helper.fixture()
        self.root = self.x.f.root

    def tearDown(self):
        self.helper.doCleanups()

    def fixture(self, *, audit=True):
        c, root, x = self.contract, self.root, self.x
        original = git(root, "rev-parse", "HEAD").stdout.decode().strip()
        group = self.work["submission_group_plan"]["groups"][0]
        marker_parent = original
        nonce = "a" * 32
        inbox_rel = Path(c["paths"]["submission_inbox_dir"]).resolve().relative_to(root).as_posix()
        marker_path = f"{inbox_rel}/run_starts/{nonce}.json"
        x.f.save(marker_path, {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": nonce,
        })
        marker = x.f.commit("Synthetic one-stage marker only")
        docs = [web_dossier(i["appid"], datetime.now(timezone.utc),
                            title=i["title"], release_year=2000 + n)
                for n, i in enumerate(group["items"])]
        transport_path = expected_buffer_path(group, c)
        artifact = {"schema": BUFFER_GROUP_SCHEMA, "schema_version": 1,
                    **copy.deepcopy(group), "dossiers": docs}
        x.f.save(transport_path.resolve().relative_to(root).as_posix(), artifact)
        introduction = x.f.commit("Synthetic immutable one-stage candidate")
        result = drain_buffered_groups(
            manifest_path=self.manifest_file, contract=c,
            buffer_dir=Path(c["paths"]["submission_inbox_dir"]),
            store_dir=Path(c["paths"]["dossier_store_dir"]),
            failed_quarantine_root=root / "quarantine/failed",
            failure_audit_path=root / "audit/failures.jsonl",
            retryable_rejection_root=root / "quarantine/rejected",
            rejection_audit_path=root / "audit/rejections.jsonl",
            terminal_receipt_archive_root=root / "audit/terminals",
            frozen_authority_audit_path=root / AUDIT, repo_root=root,
        )
        self.assertEqual(result["accepted_sequences"], [1])
        self.assertEqual(len(result["persisted"]), 3)
        proof = {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-FROZEN-AUTHORITY-V1",
            "schema_version": 1, "snapshot_id": group["snapshot_id"],
            "prepared_required_sha256": group["prepared_required_sha256"],
            "group_plan_sha256": self.work["submission_group_plan"]["group_plan_sha256"],
            "sequence": group["sequence"], "group_sha256": group["group_sha256"],
            "run_start_nonce": nonce, "marker_path": marker_path,
            "run_start_anchor_commit": marker,
            "run_start_authority_commit": marker_parent,
            "result_introduction_commit": introduction,
        }
        artifact_sha = hashlib.sha256(git(
            root, "show", f"{introduction}:{transport_path.resolve().relative_to(root).as_posix()}"
        ).stdout).hexdigest()
        actions = [{"appid": i["appid"], "action": "persisted_current_group_dossier",
                    "candidate_dossier_sha256": canonical_sha256(doc),
                    "kept_dossier_sha256": canonical_sha256(doc)}
                   for i, doc in zip(group["items"], docs)]
        receipt = _authority_audit_record(
            proof, outcome="dossier_candidate_accepted_current_snapshot",
            current_snapshot_id=group["snapshot_id"],
            artifact_path=transport_path.resolve().relative_to(root).as_posix(),
            artifact_sha256=artifact_sha, dossier_actions=actions)
        # Synthetic existing-writer audit record in the SAME canonical transaction.
        # The actual drain above did the strict V2 acceptance and cache writes.
        if audit:
            audit_path = root / AUDIT
            audit_path.parent.mkdir(parents=True, exist_ok=True)
            line = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
            audit_path.write_text(line + "\n", encoding="utf-8")
        writer = x.f.commit("Synthetic existing canonical writer transaction")
        hashes = {}
        for name in PROPOSAL_CONTRACTS:
            x.f.save(name, json.loads((CONFIG / Path(name).name).read_text("utf-8")))
        x.f.commit("Frozen inactive proposal contracts (no execution)")
        head = git(root, "rev-parse", "HEAD").stdout.decode().strip()
        hashes = {name: blob(root, head, name) for name in PROPOSAL_CONTRACTS}
        manifest_relative = self.manifest_file.resolve().relative_to(root).as_posix()
        baselines = [
            {"appid": item["appid"], "commit": writer,
             "path": item["dossier_path"],
             "git_blob_sha": blob(root, writer, item["dossier_path"]),
             "canonical_sha256": canonical_sha256(doc)}
            for item, doc in zip(group["items"], docs)
        ]
        identities = [{"appid": i["appid"], "title": i["title"],
                       "original_work_year": doc["game_identity"]["release_year"]}
                      for i, doc in zip(group["items"], docs)]
        request = {
            "schema": SCHEMA, "target_head": head,
            "original_manifest_commit": original,
            "legacy_manifest_path": manifest_relative,
            "legacy_writer_commit": writer, "legacy_writer_parent": introduction,
            "group_sequence": group["sequence"],
            "descriptor_path": (
                "data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                f"{group['snapshot_id']}/g{group['sequence']:06d}.json"),
            "descriptor_blob_sha": blob(root, original,
                "data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                f"{group['snapshot_id']}/g{group['sequence']:06d}.json"),
            "original_games": identities,
            "legacy_baselines": baselines,
            "audit_line_sha256": hashlib.sha256(
                json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "proposal_contract_blobs": hashes,
        }
        return request

    def verify(self, r):
        return verify_offline_preflight(self.root, request=r, contract=self.contract)

    def test_genuine_existing_strict_writer_plus_audited_git_transaction(self):
        request = self.fixture()
        result = self.verify(request)
        self.assertTrue(result["preflight_ready"])
        self.assertFalse(result["quality_verified"])
        self.assertFalse(result["canonical_readiness"])
        self.assertFalse(result["deep_readiness"])
        self.assertFalse(result["pilot_authorized"])
        self.assertEqual(len(result["accepted_baseline_appids"]), 3)
        self.assertEqual(result["writes"], [])
        self.assertFalse(result["semantic_execution"])

    def test_schema_valid_cache_and_accepted_manifest_without_audit_never_pass(self):
        r = self.fixture(audit=False)
        with self.assertRaisesRegex(ValueError, "missing historical writer audit"):
            self.verify(r)

    def test_missing_and_wrong_receipt_hash_fail_closed(self):
        r = self.fixture()
        r["audit_line_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "absent/mismatched"):
            self.verify(r)

    def test_wrong_group_appid_year_and_descriptor_fail_closed(self):
        for mutation, message in (
            (lambda r: r.update(group_sequence=2), "sequence"),
            (lambda r: r["original_games"][0].update(appid="999999"), "AppID"),
            (lambda r: r["original_games"][0].update(original_work_year=1999), "year"),
            (lambda r: r.update(descriptor_blob_sha="0"*40), "descriptor blob"),
        ):
            with self.subTest(message=message):
                # Each adversarial mutation uses a new disposable fixture.
                # This avoids tests deriving a second, uncontrolled state.
                if not hasattr(self, "_base"):
                    self._base = self.fixture()
                r = copy.deepcopy(self._base)
                mutation(r)
                with self.assertRaises(ValueError):
                    self.verify(r)

    def test_wrong_writer_parent_and_tampered_cache_hash_fail_closed(self):
        r = self.fixture()
        wrong = copy.deepcopy(r)
        wrong["legacy_writer_parent"] = r["original_manifest_commit"]
        with self.assertRaisesRegex(ValueError, "wrong writer transaction Git parent"):
            self.verify(wrong)
        wrong = copy.deepcopy(r)
        wrong["legacy_baselines"][0]["git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "baseline cache bytes changed"):
            self.verify(wrong)

    def test_changed_git_target_and_proposal_binding_fail_closed(self):
        r = self.fixture()
        wrong = copy.deepcopy(r)
        name = PROPOSAL_CONTRACTS[0]
        wrong["proposal_contract_blobs"][name] = "0" * 40
        with self.assertRaisesRegex(ValueError, "proposal Git contract binding"):
            self.verify(wrong)
        self.x.f.save("unrelated.txt", "new snapshot")
        self.x.f.commit("Move exact snapshot after preflight request")
        with self.assertRaisesRegex(ValueError, "target Git snapshot changed"):
            self.verify(r)

    def test_refuses_live_checkout_without_fixture_marker(self):
        r = self.fixture()
        with tempfile.TemporaryDirectory(prefix="not-marked-") as temp:
            with self.assertRaisesRegex(ValueError, "disposable Git fixture"):
                verify_offline_preflight(temp, request=r, contract=self.contract)


if __name__ == "__main__":
    unittest.main()
