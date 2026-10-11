#!/usr/bin/env python3
"""Inactive final Research->Assembly->three-game writer integration, Git-only."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dossier_two_stage_async_buffer import make_buffer
from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_staging import RESEARCH_MARKER, prepared_path, receipt_paths
from dossier_two_stage_final_acceptance import (
    STATUS_ACCEPTED, STATUS_GAP, STATUS_GROUP_PENDING, STATUS_GROUP_READY,
    STATUS_INVALID, STATUS_MISSING, STATUS_VALID,
    inspect_original_groups, offline_existing_writer_handoff, offline_gate,
)
from taste_steam_review_dossier_buffered import expected_buffer_path
from taste_steam_review_dossier_group_progress import ACCEPTED, PENDING
from taste_steam_review_dossier_web import build_daily_work_manifest_web
from taste_steam_review_dossier_test_fixture import web_dossier
from test_dossier_two_stage_async_buffer import AsyncFixture
import test_taste_steam_review_dossier_buffered_submission as baseline


class FinalAcceptanceOfflineTests(unittest.TestCase):
    def fixture(self, *, six=False):
        temp = tempfile.TemporaryDirectory(prefix="dossier-final-offline-")
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".dossier-final-offline-fixture").write_text("nonproduction\n")
        x = AsyncFixture(root)
        appids = ["12345", "23456", "34567"]
        if six:
            appids += ["45678", "56789", "67890"]
        contract = baseline.contract_for(root)
        contract["paths"]["dossier_store_dir"] = str(root / "store")
        contract["paths"]["work_manifest"] = str(root / "canonical-work.json")
        work = build_daily_work_manifest_web(
            baseline.queue(appids), contract, root / "store", now=baseline.NOW)
        # Reissue a separate, internally consistent immutable authority in this
        # disposable Git ONLY. The original AsyncFixture snapshot is not reused.
        new_docs = []
        paths = []
        for index, appid in enumerate(appids):
            d = copy.deepcopy(x.docs[index] if index < 3 else x.docs[0])
            item = work["submission_group_plan"]["groups"][index // 3]["items"][index % 3]
            group = work["submission_group_plan"]["groups"][index // 3]
            a = d["assignment"]
            a.update({
                "assignment_id": f"research-final-fixture-{index+1:04d}",
                "snapshot_id": work["snapshot_id"],
                "group_sequence": group["sequence"],
                "item_index": index % 3, "appid": appid, "title": item["title"],
                "prepared_required_sha256": work["prepared_required_sha256"],
                "group_plan_sha256": work["submission_group_plan"]["group_plan_sha256"],
                "group_sha256": group["group_sha256"],
                "items_sha256": group["items_sha256"],
                "scope_source": work["scope_source"],
                "source_queue_sha256": work["source_queue_sha256"],
                "web_evidence_contract_binding": copy.deepcopy(
                    work["web_evidence_contract_binding"]),
            })
            old_appid = d["sources"][0]["exact_product_binding"]["appid"]
            d["identity"]["resolved_title"] = item["title"]
            d["identity"]["corroborators"][0]["value"] = appid
            for source in d["sources"]:
                for key in ("normalized_locator", "physical_source_identity"):
                    source[key] = source[key].replace(old_appid, appid)
                source["locator"]["url"] = source["locator"]["url"].replace(old_appid, appid)
                source["exact_product_binding"].update({"appid": appid, "title": item["title"]})
            p = prepared_path(a)
            x.f.save(p, {k: v for k, v in a.items() if k not in (
                "research_marker_anchor_commit", "research_marker_nonce")})
            new_docs.append(d)
            paths.append(p)
        for group in work["submission_group_plan"]["groups"]:
            exact = {
                "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1",
                "schema_version": 1,
                "group_plan_sha256": work["submission_group_plan"]["group_plan_sha256"],
                "group_count": work["submission_group_plan"]["group_count"],
                "web_evidence_contract_binding": copy.deepcopy(
                    work["web_evidence_contract_binding"]),
                **group,
            }
            x.f.save(
                "data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                f"{work['snapshot_id']}/g{group['sequence']:06d}.json", exact)
        x.f.index.update({
            "snapshot_id": work["snapshot_id"],
            "prepared_required_sha256": work["prepared_required_sha256"],
            "group_plan_sha256": work["submission_group_plan"]["group_plan_sha256"],
            "pending_group_sequences": list(range(1, len(appids) // 3 + 1)),
        })
        x.f.save("data/production/pre_ai/taste_steam_review_dossier_worker_index.json",
                 x.f.index)
        source = x.f.commit("Prepare immutable exact 3-game and optional next group")
        x.paths, x.docs = paths, new_docs
        x.rbuffer = make_buffer(x.f.root, source_commit=source, phase="research",
                                ordered_work_paths=x.paths)
        x.f.save(x.rbuffer["path"], x.rbuffer["manifest"])
        x.f.commit("Publish final offline Research buffer")
        x.f.nonce = "f" * 32
        x.f.save(f"{RESEARCH_MARKER}/{x.f.nonce}.json", {
            "schema": "DOSSIER-RESEARCH-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": x.f.nonce,
        })
        x.f.marker = x.f.commit("Final offline Research marker")
        for d in x.docs:
            d["assignment"]["research_marker_anchor_commit"] = x.f.marker
            d["assignment"]["research_marker_nonce"] = x.f.nonce
        x.f.doc, x.f.a = x.docs[0], x.docs[0]["assignment"]
        x.f.source_path = receipt_paths(x.f.a)["candidate"]
        x.preauthorize_assembly(indexes=tuple(range(len(appids))))
        work_path = root / "canonical-work.json"
        work_path.write_text(json.dumps(work), encoding="utf-8")
        x.f.commit("Fixture-only canonical manifest; avoid mixed Git introductions")
        return x, work, contract, work_path

    def locator(self, x, i, c):
        return {
            "sequence": i // 3 + 1, "item_index": i % 3,
            "marker_commit": x.amarker, "buffer_path": x.abuffer["path"],
            "work_path": x.apaths[i], "result_commit": c,
        }

    def ready(self, x, i, r, *, mutate=None):
        game = x.docs[i]["assignment"]
        dossier = web_dossier(game["appid"], datetime.now(timezone.utc),
                              title=game["title"])
        return x.assembly_submit(i, r, mutate=lambda d: (
            d.update(outcome="assembled_candidate_ready", payload={
                "status": "assembled_candidate_ready", "dossier": dossier}),
            mutate(d) if mutate else None,
        ))

    def inspect(self, x, work, contract, refs):
        return inspect_original_groups(x.f.root, manifest=work, contract=contract,
                                       item_locators=refs, offline_fixture=True)

    def test_01_live_paths_fail_closed_and_contract_is_not_authoritative(self):
        x, work, c, path = self.fixture()
        with self.assertRaisesRegex(ValueError, "disabled"):
            offline_gate(x.f.root)
        with self.assertRaisesRegex(ValueError, "disabled"):
            inspect_original_groups(x.f.root, manifest=work, contract=c,
                                    item_locators=[])
        with self.assertRaisesRegex(ValueError, "disabled"):
            offline_existing_writer_handoff(
                x.f.root, inspection={}, manifest_path=path, contract=c)
        with self.assertRaisesRegex(ValueError, "separate disposable"):
            offline_gate(Path.cwd(), offline_fixture=True)
        from dossier_two_stage_final_acceptance import CONTRACT_PATH
        gate = json.loads(CONTRACT_PATH.read_text())
        self.assertFalse(gate["active"])
        self.assertFalse(gate["authorized_for_canonical_ingest"])
        self.assertFalse(gate["cross_pr_research_original_year_fix_verified"])

    def test_02_missing_and_unready_are_local_without_semantic_blocking(self):
        x, work, c, path = self.fixture()
        refs = []
        r = x.research_submit(0)
        ca = x.assembly_submit(0, r)
        refs.append(self.locator(x, 0, ca))
        result = self.inspect(x, work, c, refs)
        self.assertEqual(result["decisions"][0]["status"], STATUS_GROUP_PENDING)
        self.assertEqual([i["status"] for i in result["decisions"][0]["items"]],
                         [STATUS_GAP, STATUS_MISSING, STATUS_MISSING])
        self.assertFalse(result["ready"])
        self.assertFalse(result["canonical_dossier_accepted"])
        self.assertFalse(result["deep_ready_issued"])

    def test_03_three_exact_chains_ready_then_existing_writer_atomically_accepts(self):
        x, work, c, path = self.fixture()
        refs = []
        for i in range(3):
            r = x.research_submit(i)
            refs.append(self.locator(x, i, self.ready(x, i, r)))
        inspected = self.inspect(x, work, c, refs)
        self.assertEqual(inspected["decisions"][0]["status"], STATUS_GROUP_READY)
        self.assertEqual(len(inspected["ready"]), 1)
        self.assertEqual([p["status"] for p in inspected["decisions"][0]["items"]],
                         [STATUS_VALID] * 3)
        result = offline_existing_writer_handoff(
            x.f.root, inspection=inspected, manifest_path=path, contract=c,
            offline_fixture=True)
        self.assertEqual(result["writer"], "existing_drain_buffered_groups_only")
        self.assertEqual(result["existing_writer_result"]["accepted_sequences"], [1])
        self.assertEqual(len(result["existing_writer_result"]["persisted"]), 3)
        canonical = json.loads(path.read_text())
        self.assertEqual(canonical["group_progress"]["groups"][0]["state"], ACCEPTED)
        after = self.inspect(x, canonical, c, refs)
        self.assertEqual(after["decisions"][0]["status"], STATUS_ACCEPTED)
        self.assertFalse(after["ready"])
        self.assertTrue(after["decisions"][0]["canonical_dossier_accepted"])
        with self.assertRaisesRegex(ValueError, "stale canonical manifest"):
            offline_existing_writer_handoff(
                x.f.root, inspection=inspected, manifest_path=path, contract=c,
                offline_fixture=True)

    def test_04_bad_a_quarantined_only_while_valid_next_group_accepts(self):
        x, work, c, path = self.fixture(six=True)
        refs = []
        for i in range(6):
            r = x.research_submit(i, tamper=(lambda d: d["findings"][0].update(
                support_feedback_refs=["rfeedback-999"])) if i == 0 else None)
            ci = x.assembly_submit(i, r) if i == 0 else self.ready(x, i, r)
            refs.append(self.locator(x, i, ci))
        inspected = self.inspect(x, work, c, refs)
        self.assertEqual([d["status"] for d in inspected["decisions"]],
                         [STATUS_GROUP_PENDING, STATUS_GROUP_READY])
        self.assertEqual(inspected["decisions"][0]["items"][0]["status"], STATUS_INVALID)
        self.assertEqual([a["sequence"] for a in inspected["ready"]], [2])
        result = offline_existing_writer_handoff(
            x.f.root, inspection=inspected, manifest_path=path, contract=c,
            offline_fixture=True)
        self.assertEqual(result["existing_writer_result"]["accepted_sequences"], [2])
        self.assertEqual(len(result["existing_writer_result"]["persisted"]), 3)
        canonical = json.loads(path.read_text())
        self.assertEqual([p["state"] for p in canonical["group_progress"]["groups"]],
                         [PENDING, ACCEPTED])

    def test_05_tamper_stale_forgery_wrong_order_and_duplicate_fail_closed(self):
        bad_mutations = [
            lambda d: d["research_transport"].update(
                research_package_raw_sha256="0" * 64),
            lambda d: d["research_transport"].update(
                research_package_blob_sha="0" * 40),
            lambda d: d.update(assembly_prompt_sha256="0" * 64),
            lambda d: d.update(assembly_marker_nonce="0" * 32),
            lambda d: d["original_research_assignment"].update(item_index=2),
            lambda d: d["research_transport"].update(
                research_package_git_commit="a" * 40),
        ]
        for mutate in bad_mutations:
            with self.subTest(mutation=bad_mutations.index(mutate)):
                x, work, c, path = self.fixture()
                r = x.research_submit(0)
                bad = self.ready(x, 0, r, mutate=mutate)
                decision = self.inspect(x, work, c, [self.locator(x, 0, bad)])
                self.assertEqual(decision["decisions"][0]["items"][0]["status"],
                                 STATUS_INVALID)
                self.assertFalse(decision["ready"])
        x, work, c, path = self.fixture()
        r = x.research_submit(0)
        ca = self.ready(x, 0, r)
        ref = self.locator(x, 0, ca)
        duplicated = self.inspect(x, work, c, [ref, copy.deepcopy(ref)])
        self.assertEqual(duplicated["decisions"][0]["items"][0]["status"], STATUS_INVALID)
        foreign = self.inspect(x, work, c, [{**ref, "sequence": 2}])
        self.assertTrue(foreign["unmatched_locators"])
        shifted = self.inspect(x, work, c, [{**ref, "item_index": 1}])
        self.assertEqual(shifted["decisions"][0]["items"][1]["status"], STATUS_INVALID)
        # A claimed GitHub receipt cannot authorize a rejected Research package.
        receipt = receipt_paths(x.docs[0]["assignment"])["accepted"]
        x.f.save(receipt, {"schema": "FORGED-RESEARCH-ACCEPTANCE"})
        x.f.commit("Forged receipt after result")
        self.assertEqual(self.inspect(x, work, c, [ref])["decisions"][0]["items"][0]["status"],
                         STATUS_INVALID)

    def test_06_collision_and_stale_manifest_prevent_double_commit(self):
        x, work, c, path = self.fixture(six=True)
        refs = []
        for i in range(6):
            r = x.research_submit(i)
            refs.append(self.locator(x, i, self.ready(x, i, r)))
        inspected = self.inspect(x, work, c, refs)
        self.assertEqual([e["sequence"] for e in inspected["ready"]], [1, 2])
        desc = work["submission_group_plan"]["groups"][0]
        collision_path = expected_buffer_path(desc, c)
        collision_path.parent.mkdir(parents=True, exist_ok=True)
        collision_path.write_text("{}", encoding="utf-8")
        output = offline_existing_writer_handoff(
            x.f.root, inspection=inspected, manifest_path=path, contract=c,
            offline_fixture=True)
        self.assertEqual(output["collision_sequences"], [1])
        self.assertEqual(output["staged_sequences"], [2])
        self.assertEqual(output["existing_writer_result"]["accepted_sequences"], [2])
        self.assertEqual([p["state"] for p in json.loads(path.read_text())[
            "group_progress"]["groups"]], [PENDING, ACCEPTED])
        self.assertEqual(output["existing_writer_result"]["retryable_transport_rejection_count_this_run"], 1)


    def test_07_final_writer_rechecks_forged_handoff_and_later_transport_rewrite(self):
        x, work, c, path = self.fixture()
        refs = []
        for i in range(3):
            r = x.research_submit(i)
            refs.append(self.locator(x, i, self.ready(x, i, r)))
        inspected = self.inspect(x, work, c, refs)
        self.assertEqual([e["sequence"] for e in inspected["ready"]], [1])
        forged = copy.deepcopy(inspected)
        forged["ready"][0]["artifact"]["dossiers"][0]["game_identity"]["work_title"] = (
            "Unverified replacement")
        with self.assertRaisesRegex(ValueError, "untrusted, forged or stale"):
            offline_existing_writer_handoff(
                x.f.root, inspection=forged, manifest_path=path, contract=c,
                offline_fixture=True)
        # Old introducing Git SHA remains valid, but HEAD no longer carries the
        # immutable Research raw blob. Reinspection MUST fail before any write.
        research_path = receipt_paths(x.docs[0]["assignment"])["candidate"]
        x.f.save(research_path, {"tamper": "after introduction"})
        x.f.commit("Adversarial rewrite of previously create-only Research bytes")
        after = self.inspect(x, work, c, refs)
        self.assertEqual(after["decisions"][0]["items"][0]["status"], STATUS_INVALID)
        self.assertFalse(after["ready"])
        with self.assertRaisesRegex(ValueError, "untrusted, forged or stale"):
            offline_existing_writer_handoff(
                x.f.root, inspection=inspected, manifest_path=path, contract=c,
                offline_fixture=True)
        self.assertFalse((x.f.root / "store" / "App_12345.json").exists())


if __name__ == "__main__":
    unittest.main()
