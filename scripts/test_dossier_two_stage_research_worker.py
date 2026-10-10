#!/usr/bin/env python3
"""Isolated Research worker V1 tests: disposable Git only, zero real semantics."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from dossier_two_stage_async_buffer import make_buffer
from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_research_worker import (
    PROMPT_PATH, ROOT, frozen_research_batch,
    inspect_existing_research_transport, prepare_research_transport,
)
from dossier_two_stage_staging import (
    RESEARCH_MARKER, blob, bytes_json, prepared_path, receipt_paths,
)
from test_dossier_two_stage_async_buffer import AsyncFixture


class ResearchWorkerTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.x = AsyncFixture(t.name)

    def pin(self, *, add_prompt=True, prompt_contents=None, buffer=None):
        x = self.x
        if add_prompt:
            path = x.f.root / PROMPT_PATH
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / PROMPT_PATH).read_bytes()
                             if prompt_contents is None else prompt_contents)
        if add_prompt:
            x.f.commit("Freeze prompt bytes and GitHub-prepared Research scope")
        nonce = "f" * 32
        x.f.save(f"{RESEARCH_MARKER}/{nonce}.json", {
            "schema": "DOSSIER-RESEARCH-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": nonce,
        })
        marker = x.f.commit("Marker is only create-only change")
        self.marker = marker
        self.buffer = buffer or x.rbuffer["path"]
        self.paths = list(x.paths)
        for doc in x.docs:
            doc["assignment"]["research_marker_anchor_commit"] = marker
            doc["assignment"]["research_marker_nonce"] = nonce
        return marker

    def batch(self):
        return frozen_research_batch(self.x.f.root, marker_commit=self.marker,
                                     buffer_path=self.buffer)

    def prepare(self, i, doc=None):
        x = self.x
        return prepare_research_transport(
            x.f.root, marker_commit=self.marker, buffer_path=self.buffer,
            work_path=self.paths[i],
            document=copy.deepcopy(x.docs[i] if doc is None else doc))

    def inspect(self, i, expected_bytes=None):
        return inspect_existing_research_transport(
            self.x.f.root, marker_commit=self.marker, buffer_path=self.buffer,
            work_path=self.paths[i], expected_bytes=expected_bytes)

    def submit(self, i, *, alter=None, extra=False):
        x = self.x
        doc = copy.deepcopy(x.docs[i])
        if alter:
            alter(doc)
        path = receipt_paths(doc["assignment"])["candidate"]
        x.f.save(path, doc)
        if extra:
            x.f.save("data/test-extra-file.json", {"inert": True})
        return x.f.commit("Create-only Research transport")

    def test_01_inactive_and_exact_prompt_parent_identity(self):
        self.pin()
        b = self.batch()
        self.assertEqual(len(b["items"]), 3)
        self.assertEqual(b["marker_commit"], self.marker)
        self.assertEqual(b["items"][0]["assignment"], self.x.docs[0]["assignment"])
        self.assertEqual(b["items"][0]["work_path"], self.paths[0])
        self.assertEqual(b["buffer_blob_sha"], blob(self.x.f.root, b["marker_parent"], self.buffer))
        self.assertEqual([i["assignment"]["item_index"] for i in b["items"]], [0, 1, 2])
        from dossier_two_stage_async_buffer import inactive_gate
        from dossier_two_stage_contract_guard import check_gate
        self.assertIs(check_gate()["authorized_for_semantic_execution"], False)
        self.assertIs(inactive_gate()["semantic_workers_implemented"], False)
        self.assertIs(inactive_gate()["active"], False)
        self.assertIs(inactive_gate()["executable_in_production"], False)

    def test_02_ready_strict_schema_and_computed_hashes(self):
        self.pin()
        r = self.prepare(0)
        self.assertEqual(r["status"], "ready_for_create_only_submission")
        self.assertEqual(r["transport_bytes"], bytes_json(self.x.docs[0]))
        self.assertEqual(r["expected_canonical_sha256"],
                         canonical_sha256(self.x.docs[0]))
        self.assertEqual(self.inspect(0)["status"], "not_submitted")
        self.assertFalse(r["canonical_acceptance"])

    def test_03_original_git_bytes_replay_is_submitted_not_accepted(self):
        self.pin()
        ready = self.prepare(0)
        c = self.submit(0)
        found = self.inspect(0, expected_bytes=ready["transport_bytes"])
        self.assertEqual(found["research_package_git_commit"], c)
        self.assertEqual(found["status"], "submitted_unaccepted")
        self.assertEqual(found["research_package_blob_sha"],
                         ready["expected_git_blob_sha"])
        self.assertEqual(self.prepare(0)["status"], "submitted_unaccepted")
        self.assertIsNone(self.prepare(0)["transport_bytes"])
        self.assertFalse((self.x.f.root / receipt_paths(
            self.x.docs[0]["assignment"])["accepted"]).exists())

    def test_04_duplicate_different_bytes_fail_closed(self):
        self.pin()
        self.submit(0)
        changed = copy.deepcopy(self.x.docs[0])
        changed["research_audit"]["completeness"] = "research_incomplete"
        with self.assertRaisesRegex(ValueError, "collision"):
            self.prepare(0, changed)

    def test_05_binding_privacy_source_and_dimension_forgery_rejected(self):
        self.pin()
        bad = [
            lambda d: d["assignment"].update(appid="99999"),
            lambda d: d["identity"].update(original_work_release_year=None),
            lambda d: d["sources"][0].update(domain="attacker.invalid"),
            lambda d: d["observed_feedback"][0].update(parent_source_ref="rsource-999"),
            lambda d: d["findings"][0].update(support_feedback_refs=["rfeedback-999"]),
            lambda d: d["research_audit"]["dimension_survey"].pop(),
            lambda d: d["findings"][0].update(safe_neutral_synthesis="author: secret"),
            lambda d: d["sources"][0].update(publication_date="2026-01-01T12:00:00"),
        ]
        for mutate in bad:
            d = copy.deepcopy(self.x.docs[0])
            mutate(d)
            with self.subTest(mutate=str(mutate)), self.assertRaises(ValueError):
                self.prepare(0, d)

    def test_06_local_invalid_item_does_not_wait_for_GitHub_or_block_siblings(self):
        self.pin()
        bad = copy.deepcopy(self.x.docs[0])
        bad["assignment"]["assignment_id"] = "wrong-fixture"
        with self.assertRaises(ValueError):
            self.prepare(0, bad)
        self.assertEqual([self.prepare(i)["status"] for i in (1, 2)],
                         ["ready_for_create_only_submission"] * 2)
        self.assertEqual(self.inspect(0)["status"], "not_submitted")

    def test_07_original_intro_must_be_single_create_only_file(self):
        self.pin()
        self.submit(0, extra=True)
        with self.assertRaisesRegex(ValueError, "create-only"):
            self.inspect(0)
        self.assertEqual(self.prepare(1)["status"],
                         "ready_for_create_only_submission")

    def test_08_original_blob_cannot_be_overwritten(self):
        self.pin()
        self.submit(0)
        self.x.f.save(receipt_paths(self.x.docs[0]["assignment"])["candidate"],
                      {"schema": "tampered"})
        self.x.f.commit("Overwrite Research candidate")
        with self.assertRaisesRegex(ValueError, "overwritten"):
            self.inspect(0)

    def test_09_stale_or_missing_prompt_fails_globally(self):
        self.pin(add_prompt=False)
        with self.assertRaises(ValueError):
            self.batch()
        # Another disposable history: parent prompt exists but differs.
        with tempfile.TemporaryDirectory() as root:
            other = AsyncFixture(root)
            self.x = other
            self.pin(prompt_contents=b"invalid-old-worker-prompt")
            with self.assertRaisesRegex(ValueError, "prompt"):
                self.batch()

    def test_10_frozen_marker_prohibits_reauthorization_or_work_invention(self):
        self.pin()
        path = "data/control/dossier_research_assignments/" + ("e" * 64) + "/invented.json"
        with self.assertRaisesRegex(ValueError, "manifest"):
            prepare_research_transport(self.x.f.root, marker_commit=self.marker,
                                       buffer_path=self.buffer, work_path=path,
                                       document=self.x.docs[0])
        # A later movement of HEAD does not change immutable marker parent.
        self.x.f.save("data/unrelated.json", {"no_new_authority": True})
        self.x.f.commit("Later independent GitHub progress")
        self.assertEqual(len(self.batch()["items"]), 3)

    def test_11_incomplete_honest_package_is_not_misclassified_as_acceptance(self):
        self.pin()
        doc = copy.deepcopy(self.x.docs[0])
        doc["research_audit"]["completeness"] = "research_incomplete"
        p = self.prepare(0, doc)
        self.assertEqual(p["status"], "ready_for_create_only_submission")
        self.assertFalse(p["canonical_acceptance"])

    def extend_twelve(self):
        x = self.x
        paths = list(x.paths)
        for seq in (2, 3, 4):
            items = [{"appid": str(120000 + seq * 10 + j),
                      "title": f"Frozen Group {seq} Game {j}"} for j in range(3)]
            base = x.docs[0]["assignment"]
            fields = {
                "snapshot_id": base["snapshot_id"],
                "prepared_required_sha256": base["prepared_required_sha256"],
                "sequence": seq,
                "start_index": (seq - 1) * 3, "end_index_exclusive": seq * 3,
                "appids": [i["appid"] for i in items],
                "items_sha256": canonical_sha256(items),
                "scope_source": base["scope_source"],
                "source_queue_sha256": base["source_queue_sha256"],
            }
            group_sha = canonical_sha256(fields)
            descriptor = copy.deepcopy(x.f.descriptor)
            descriptor.update(fields)
            descriptor["items"] = items
            descriptor["group_sha256"] = group_sha
            descriptor["group_count"] = 4
            x.f.save("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                     f"{base['snapshot_id']}/g{seq:06d}.json", descriptor)
            for j, itm in enumerate(items):
                d = copy.deepcopy(x.docs[0])
                a = d["assignment"]
                a.update({"assignment_id": f"research-extra-{seq:02d}-{j:02d}",
                          "group_sequence": seq, "item_index": j,
                          "appid": itm["appid"], "title": itm["title"],
                          "group_sha256": group_sha,
                          "items_sha256": fields["items_sha256"]})
                d["identity"]["resolved_title"] = itm["title"]
                d["identity"]["corroborators"][0]["value"] = itm["appid"]
                for s in d["sources"]:
                    for k in ("normalized_locator", "physical_source_identity"):
                        s[k] = s[k].replace("12345", itm["appid"])
                    s["locator"]["url"] = s["locator"]["url"].replace("12345", itm["appid"])
                    s["exact_product_binding"].update(appid=itm["appid"], title=itm["title"])
                p = prepared_path(a)
                x.f.save(p, {k: v for k, v in a.items()
                             if k not in ("research_marker_anchor_commit", "research_marker_nonce")})
                x.docs.append(d)
                paths.append(p)
        x.f.index["pending_group_sequences"] = [1, 2, 3, 4]
        x.f.save("data/production/pre_ai/taste_steam_review_dossier_worker_index.json",
                 x.f.index)
        start = x.f.commit("GitHub prepares twelve exact frozen assignments")
        buf = make_buffer(x.f.root, source_commit=start, phase="research",
                          ordered_work_paths=paths)
        x.f.save(buf["path"], buf["manifest"])
        x.f.commit("Freeze immutable twelve-item buffer")
        x.paths = paths
        return buf

    def test_12_twelve_items_no_eight_slot_limit_ack_or_quota(self):
        b = self.extend_twelve()
        self.pin(buffer=b["path"])
        self.paths = list(self.x.paths)
        work = self.batch()["items"]
        self.assertEqual(len(work), 12)
        self.assertEqual([(i["assignment"]["group_sequence"],
                           i["assignment"]["item_index"]) for i in work],
                         [(seq, index) for seq in (1, 2, 3, 4)
                          for index in (0, 1, 2)])
        for i in range(12):
            with self.subTest(i=i):
                self.assertEqual(self.prepare(i)["status"],
                                 "ready_for_create_only_submission")
        self.assertEqual(self.inspect(11)["status"], "not_submitted")


if __name__ == "__main__":
    unittest.main()
