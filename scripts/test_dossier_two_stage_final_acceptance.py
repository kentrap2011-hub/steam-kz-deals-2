#!/usr/bin/env python3
"""Inactive final Research->Assembly->three-game writer integration, Git-only."""
import copy
import json
import subprocess
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
        self.assertIs(type(gate["cross_pr_research_original_year_fix_verified"]), bool)

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



class NotesV2IndividualReadinessTests(unittest.TestCase):
    """Real V2 frozen Git lineage and existing strict validator, synthetic only."""

    def fixture(self):
        import test_dossier_research_notes_v2 as notes_fixture
        f = notes_fixture.NotesV2Tests(
            methodName="test_zero_evidence_research_passes_without_year_sources_or_dimensions")
        f.setUp()
        self.addCleanup(f.doCleanups)
        return f, notes_fixture

    def submit(self, f, helpers, appid, *, result="valid"):
        import dossier_research_notes_v2 as notes
        a = notes.frozen_assignment(
            f.repo, marker_commit=f.marker, trial_id=helpers.TRIAL, appid=appid)
        raw_notes = {
            "schema": "DOSSIER-RESEARCH-NOTES-V2", "schema_version": 2,
            "assignment": a, "notes_text": "", "source_log": [],
            "research_status": "no_verifiable_findings",
        }
        helpers.write(f.repo, notes._path("research", a), raw_notes)
        research = helpers.commit(f.repo, "synthetic per-item Notes " + appid)
        if result == "waiting":
            return {"research_commit": research, "assembly_commit": None}
        work = notes.assembly_work(
            f.repo, marker_commit=f.marker, trial_id=helpers.TRIAL,
            appid=appid, research_commit=research)
        self.assertEqual(work["status"], "ready_for_autonomous_assembly")
        dossier = (
            {"appid": appid, "title": a["title"]}
            if result == "invalid_strict"
            else web_dossier(appid, datetime.now(timezone.utc), title=a["title"])
        )
        document = notes.candidate_assembly(
            work, outcome="assembled_candidate_ready", final_dossier=dossier)
        helpers.write(f.repo, work["output_path"], document)
        assembly = helpers.commit(f.repo, "synthetic per-item Assembly " + appid)
        return {"research_commit": research, "assembly_commit": assembly}

    def inspect_v2(self, f, helpers, locators):
        import dossier_research_notes_v2 as notes
        return notes.individual_final_readiness(
            f.repo, marker_commit=f.marker,
            trial_id=helpers.TRIAL, item_commits=locators)

    def test_v2_a_and_c_ready_b_strict_invalid_no_cross_acceptance(self):
        f, helpers = self.fixture()
        group = helpers.C["original_groups"][0]
        a, b, c = group["appids"]
        locators = {
            a: self.submit(f, helpers, a),
            b: self.submit(f, helpers, b, result="invalid_strict"),
            c: self.submit(f, helpers, c),
        }
        projection = self.inspect_v2(f, helpers, locators)
        rows = projection["items"]
        self.assertEqual(len(rows), 18)
        self.assertEqual([x["appid"] for x in rows],
                         [x for g in helpers.C["original_groups"] for x in g["appids"]])
        self.assertEqual([x["status"] for x in rows[:3]], ["ready", "invalid", "ready"])
        self.assertEqual(rows[1]["source_status"], "final_strict_or_group_rejected")
        self.assertEqual([x["status"] for x in rows[3:]], ["missing"] * 15)
        self.assertEqual([x["strict_item_valid"] for x in rows[:3]],
                         [True, False, True])
        self.assertFalse(projection["canonical_acceptance"])
        self.assertFalse(projection["deep_ready"])
        self.assertTrue(projection["requires_separately_authorized_canonical_writer"])
        self.assertTrue(all(not x["canonical_acceptance"] and not x["deep_ready"]
                            for x in rows))
        self.assertFalse(helpers.v2.original_group_readiness(
            group["group_sequence"],
            {x["appid"]: x["source_status"] for x in rows[:3]})["strict_three_ready"])

    def test_v2_b_missing_does_not_block_a_and_c(self):
        f, helpers = self.fixture()
        a, b, c = helpers.C["original_groups"][0]["appids"]
        projected = self.inspect_v2(f, helpers, {
            a: self.submit(f, helpers, a),
            c: self.submit(f, helpers, c),
        })
        self.assertEqual([x["status"] for x in projected["items"][:3]],
                         ["ready", "missing", "ready"])
        self.assertEqual(sum(x["status"] == "missing" for x in projected["items"]), 16)
        self.assertTrue(all(x["canonical_acceptance"] is False
                            for x in projected["items"]))

    def test_v2_runtime_terminal_error_is_local(self):
        f, helpers = self.fixture()
        import dossier_research_notes_v2 as notes
        a, b, c = helpers.C["original_groups"][0]["appids"]
        good = self.submit(f, helpers, a)
        in_progress = self.submit(f, helpers, b, result="waiting")
        work = notes.assembly_work(
            f.repo, marker_commit=f.marker, trial_id=helpers.TRIAL,
            appid=b, research_commit=in_progress["research_commit"])
        terminal = notes.candidate_assembly(
            work, outcome="runtime_or_tool_interrupted",
            diagnostic="synthetic Git-only tool failure")
        helpers.write(f.repo, work["output_path"], terminal)
        failed = helpers.commit(f.repo, "synthetic B interrupted Assembly")
        projected = self.inspect_v2(f, helpers, {
            a: good, b: {"research_commit": in_progress["research_commit"],
                         "assembly_commit": failed},
        })
        self.assertEqual([x["status"] for x in projected["items"][:3]],
                         ["ready", "error", "missing"])
        self.assertEqual(projected["items"][1]["source_status"], "runtime_or_tool_interrupted")
        self.assertFalse(projected["canonical_acceptance"])

    def test_v2_waiting_errors_bad_locator_and_frozen_scope(self):
        f, helpers = self.fixture()
        import dossier_research_notes_v2 as notes
        a, b, c = helpers.C["original_groups"][0]["appids"]
        projected = self.inspect_v2(f, helpers, {
            a: self.submit(f, helpers, a),
            b: self.submit(f, helpers, b, result="waiting"),
            c: {"research_commit": "not-a-commit", "assembly_commit": "also-invalid"},
        })
        self.assertEqual([x["status"] for x in projected["items"][:3]],
                         ["ready", "waiting", "invalid"])
        self.assertFalse(projected["items"][2]["strict_item_valid"])
        wrong = {a: {"research_commit": None, "assembly_commit": "not-a-commit"}}
        self.assertEqual(self.inspect_v2(f, helpers, wrong)["items"][0]["status"],
                         "invalid")
        with self.assertRaises(notes.NotesV2Error):
            self.inspect_v2(f, helpers, {"123456789": {}})
        with self.assertRaises(notes.NotesV2Error):
            self.inspect_v2(f, helpers, [a])
        self.assertFalse(notes._contract()["authorized_for_canonical_ingest"])


    def test_v2_individual_shared_writer_a_c_persist_b_invalid_and_next_group_continues(self):
        f, helpers = self.fixture()
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        first, second = helpers.C["original_groups"][:2]
        a, b, c = first["appids"]
        d = second["appids"][0]
        locators = {
            a: self.submit(f, helpers, a),
            b: self.submit(f, helpers, b, result="invalid_strict"),
            c: self.submit(f, helpers, c),
            d: self.submit(f, helpers, d),
        }
        (f.repo / ".dossier-final-offline-fixture").write_text("synthetic\n")
        store, receipts = f.repo / "store", f.repo / "accepted"
        def run_writer():
            return drain_buffered_groups(notes_v2={
                "repo": f.repo, "marker_commit": f.marker, "trial_id": helpers.TRIAL,
                "item_commits": locators, "store_dir": store,
                "accepted_dir": receipts, "offline_fixture": True,
            })
        before = helpers.run(f.repo, "rev-parse", "HEAD") if hasattr(helpers, "run") else None
        result = run_writer()
        statuses = {row["appid"]: row["status"] for row in result["items"]}
        self.assertEqual([statuses[x] for x in (a, b, c, d)], [
            "persisted_pending_github_commit", "invalid",
            "persisted_pending_github_commit", "persisted_pending_github_commit",
        ])
        self.assertEqual(len(result["items"]), 18)
        self.assertFalse(result["canonical_acceptance"])
        self.assertTrue(result["requires_existing_github_writer_commit"])
        for appid in (a, c, d):
            self.assertTrue((store / ("App_" + appid + ".json")).is_file())
            self.assertEqual(len(list(receipts.rglob(appid + "--*.json"))), 1)
        self.assertFalse((store / ("App_" + b + ".json")).exists())
        self.assertFalse(list(receipts.rglob(b + "--*.json")))
        second_pass = run_writer()
        replay = {row["appid"]: row["status"] for row in second_pass["items"]}
        self.assertEqual([replay[x] for x in (a, b, c, d)], [
            "already_persisted_same_binding", "invalid",
            "already_persisted_same_binding", "already_persisted_same_binding",
        ])
        self.assertEqual(len(list(receipts.rglob("*.json"))), 3)
        if before is not None:
            self.assertEqual(helpers.run(f.repo, "rev-parse", "HEAD"), before)

    def test_v2_single_writer_collision_and_unauthorized_fail_closed(self):
        f, helpers = self.fixture()
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        a, b, c = helpers.C["original_groups"][0]["appids"]
        locators = {
            a: self.submit(f, helpers, a),
            c: self.submit(f, helpers, c),
        }
        (f.repo / ".dossier-final-offline-fixture").write_text("synthetic\n")
        store, receipts = f.repo / "store", f.repo / "accepted"
        def run_writer(**extra):
            kwargs = dict(repo=f.repo, marker_commit=f.marker,
                          trial_id=helpers.TRIAL, item_commits=locators,
                          store_dir=store, accepted_dir=receipts)
            kwargs.update(extra)
            kwargs.setdefault("offline_fixture", False)
            return drain_buffered_groups(notes_v2=kwargs)
        with self.assertRaisesRegex(ValueError, "disabled"):
            run_writer()
        with self.assertRaisesRegex(ValueError, "subdirectories"):
            run_writer(offline_fixture=True, accepted_dir=store)
        with self.assertRaises(helpers.v2.NotesV2Error):
            run_writer(offline_fixture=True, item_commits={"0": {}})
        first = run_writer(offline_fixture=True)
        self.assertEqual([x["status"] for x in first["items"][:3]],
                         ["persisted_pending_github_commit", "missing",
                          "persisted_pending_github_commit"])
        original_c = (store / ("App_" + c + ".json")).read_bytes()
        # Exact existing canonical dossier must never be replaced by another
        # document or by a forged same-name receipt.
        (store / ("App_" + a + ".json")).write_text('{"appid":"forged"}\n')
        second = run_writer(offline_fixture=True)
        self.assertEqual([x["status"] for x in second["items"][:3]],
                         ["writer_rejected", "missing",
                          "already_persisted_same_binding"])
        self.assertEqual((store / ("App_" + a + ".json")).read_text(),
                         '{"appid":"forged"}\n')
        self.assertEqual((store / ("App_" + c + ".json")).read_bytes(), original_c)
        self.assertEqual(len(list(receipts.rglob("*.json"))), 2)



    def test_v2_writer_storage_error_aborts_github_transaction(self):
        f, helpers = self.fixture()
        from unittest.mock import patch
        import taste_steam_review_dossier_buffered as writer
        a = helpers.C["original_groups"][0]["appids"][0]
        locators = {a: self.submit(f, helpers, a)}
        (f.repo / ".dossier-final-offline-fixture").write_text("synthetic\n")
        stored = f.repo / "store"
        accepted = f.repo / "accepted"
        real_write = writer.atomic_write_json
        def fail_receipt_write(path, data):
            if Path(path).is_relative_to(accepted):
                raise OSError("synthetic receipt storage unavailable")
            return real_write(path, data)
        with patch.object(writer, "atomic_write_json", side_effect=fail_receipt_write):
            with self.assertRaisesRegex(OSError, "receipt storage unavailable"):
                writer.drain_buffered_groups(notes_v2={
                    "repo": f.repo, "marker_commit": f.marker,
                    "trial_id": helpers.TRIAL, "item_commits": locators,
                    "store_dir": stored, "accepted_dir": accepted,
                    "offline_fixture": True,
                })
        self.assertFalse(list(accepted.rglob("*.json")))
        # Existing GitHub writer must treat the raised error as a failed whole
        # transaction, not stage the temporarily written uncommitted cache.
        self.assertFalse((f.repo / "data/control/dossier_notes_v2/canonical_accepted").exists())



    def test_v2_github_writer_hookup_single_transaction(self):
        """Exercise the existing staging shell and Git push in a disposable local remote.

        This proves one Git commit contains A/C cache + receipts, not a real
        GitHub publication. B's failed strict dossier never enters that commit.
        """
        f, helpers = self.fixture()
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        a, b, c = helpers.C["original_groups"][0]["appids"]
        locators = {
            a: self.submit(f, helpers, a),
            b: self.submit(f, helpers, b, result="invalid_strict"),
            c: self.submit(f, helpers, c),
        }
        (f.repo / ".dossier-final-offline-fixture").write_text("synthetic\n")
        # The existing V1 staging helper requires its existing V1 state paths.
        # Create harmless placeholders in this *disposable* test repo only.
        required_files = [
            "data/production/pre_ai/taste_steam_review_dossier_work.json",
            "data/production/pre_ai/taste_steam_review_dossier_worker_index.json",
            "data/production/pre_ai/taste_steam_review_dossier_validation_status.json",
            "data/production/pre_ai/progressive_pass2_work.json",
        ]
        required_dirs = [
            "data/ai_inbox/taste_steam_review_dossiers",
            "data/production/pre_ai/taste_steam_review_dossier_worker_groups",
        ]
        for rel in required_files:
            path = f.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")
        for rel in required_dirs:
            path = f.repo / rel / ".keep"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")
        # The required fixture marker is not canonical output.
        with (f.repo / ".git/info/exclude").open("a", encoding="utf-8") as out:
            out.write("\n.dossier-final-offline-fixture\n")

        result = drain_buffered_groups(notes_v2={
            "repo": f.repo, "marker_commit": f.marker, "trial_id": helpers.TRIAL,
            "item_commits": locators,
            "store_dir": f.repo / "data/cache/taste_steam_review_dossiers",
            "accepted_dir": f.repo / "data/control/dossier_notes_v2/canonical_accepted",
            "offline_fixture": True,
        })
        self.assertEqual([x["status"] for x in result["items"][:3]], [
            "persisted_pending_github_commit", "invalid", "persisted_pending_github_commit"
        ])
        self.assertFalse(result["canonical_acceptance"])

        root = Path(__file__).resolve().parents[1]
        stage = root / "scripts/stage_taste_dossier_canonical_writer.sh"
        subprocess.run(["bash", str(stage), "stage"], cwd=f.repo, check=True)
        staged = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], cwd=f.repo, text=True
        ).splitlines()
        for appid in (a, c):
            self.assertIn("data/cache/taste_steam_review_dossiers/App_" + appid + ".json", staged)
            self.assertEqual(len([x for x in staged if "/canonical_accepted/" in x
                                  and ("/" + appid + "--") in x]), 1)
        self.assertNotIn("data/cache/taste_steam_review_dossiers/App_" + b + ".json", staged)
        self.assertFalse(any("/" + b + "--" in x for x in staged))
        subprocess.run(["git", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm",
                        "Synthetic one-transaction Dossier V2 writer"], cwd=f.repo, check=True)
        subprocess.run(["bash", str(stage), "assert-clean"], cwd=f.repo, check=True)

        with tempfile.TemporaryDirectory(prefix="dossier-v2-local-bare-") as remote:
            bare = Path(remote) / "bare.git"
            subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
            subprocess.run(["git", "push", "-q", str(bare), "HEAD:refs/heads/v2-test"],
                           cwd=f.repo, check=True)
            tree = subprocess.check_output([
                "git", "--git-dir", str(bare), "ls-tree", "-r", "--name-only",
                "refs/heads/v2-test"], text=True).splitlines()
            for appid in (a, c):
                self.assertIn("data/cache/taste_steam_review_dossiers/App_" + appid + ".json",
                              tree)
                self.assertEqual(len([x for x in tree if "/canonical_accepted/" in x
                                      and ("/" + appid + "--") in x]), 1)
            self.assertFalse(any("App_" + b + ".json" in x or "/" + b + "--" in x
                                 for x in tree if x.startswith("data/cache/") or
                                 "/canonical_accepted/" in x))

    def test_v2_hook_uses_same_disabled_dispatch_and_shared_lock(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/"
                    "ingest-taste-steam-review-dossier-checkpoint.yml"
                    ).read_text(encoding="utf-8")
        writer = json.loads((root / "config/dossier_notes_v2_individual_writer_contract.json"
                             ).read_text(encoding="utf-8"))
        self.assertIn("group: taste-steam-review-dossier-canonical-writer", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("notes_v2_writer:", workflow)
        self.assertIn("default: false", workflow)
        self.assertIn('if: github.event_name == \'push\'', workflow)
        self.assertIn('"offline_fixture": False', workflow)
        self.assertIn("drain_buffered_groups(notes_v2=", workflow)
        self.assertIn("bash scripts/stage_taste_dossier_canonical_writer.sh stage", workflow)
        self.assertIn("git push origin HEAD:main", workflow)
        self.assertFalse(writer["active"])
        self.assertFalse(writer["authorized_for_canonical_ingest"])
        self.assertFalse(writer["existing_writer_integration_approved"])
        self.assertFalse(writer["downstream_deep_handoff_approved"])
        self.assertEqual(
            writer["v2_group_policy_precedence"]["scope"], "explicit_notes_v2_mode_only"
        )


if __name__ == "__main__":
    unittest.main()
