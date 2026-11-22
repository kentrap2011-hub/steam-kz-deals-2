#!/usr/bin/env python3
"""Default-OFF, disposable-Git canonical Lean writer -> reader -> Deep E2E.

All Research and Assembly inputs are synthetic immutable local fixtures.
This is NOT a GitHub owner grant, actual semantic Research/Assembly, or Deep run.
"""
import copy
import hashlib
import json
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from pathlib import Path

import dossier_lean_canonical_dual as dual
import progressive_pass2 as deep
import test_dossier_two_stage_final_acceptance as writer_tests
import test_dossier_research_notes_v2 as helpers
import test_progressive_pass2 as pass2_fixture
from taste_steam_review_dossier import canonical_sha256
from taste_steam_review_dossier_buffered import drain_buffered_groups
from taste_steam_review_dossier_test_fixture import web_dossier
from taste_steam_review_dossier_web import build_semantic_input_strict

APPID = "2124120"
TITLE = "SULFUR"
NOW = datetime.now(timezone.utc).replace(microsecond=0)


class CanonicalLeanDualIntegrationTests(unittest.TestCase):
    def fixture(self, *, accepted=True):
        fixture_case = writer_tests.NotesV2IndividualReadinessTests(
            methodName="test_v2_github_writer_hookup_single_transaction"
        )
        f, _ = fixture_case.fixture()
        self.addCleanup(fixture_case.doCleanups)
        pair = fixture_case.submit(f, helpers, APPID, result="lean")
        (f.repo / ".dossier-final-offline-fixture").write_text("synthetic\n")
        with (f.repo / ".git/info/exclude").open("a", encoding="utf-8") as handle:
            handle.write("\n.dossier-final-offline-fixture\n")
        store = f.repo / dual.STORE
        receipt_dir = f.repo / dual.RECEIPTS
        result = drain_buffered_groups(notes_v2={
            "repo": f.repo,
            "marker_commit": f.marker,
            "trial_id": helpers.TRIAL,
            "item_commits": {APPID: pair},
            "store_dir": store,
            "accepted_dir": receipt_dir,
            "offline_fixture": True,
        })
        self.assertEqual(next(i for i in result["items"] if i["appid"] == APPID)["status"], "persisted_pending_github_commit")
        raw = (store / ("App_" + APPID + ".json")).read_bytes()
        doc = json.loads(raw)
        receipt_path = next(receipt_dir.rglob(APPID + "--*.json"))
        record = {
            "path": (dual.STORE / ("App_" + APPID + ".json")).as_posix(),
            "doc": doc,
            "content_sha256": hashlib.sha256(raw).hexdigest(),
        }
        if accepted:
            helpers.commit(f.repo, "fixture: atomic Lean cache and owner-shaped receipt")
        return f, pair, record, receipt_path, result

    def verify(self, f, record, **kwargs):
        return dual.inspect_accepted_lean(
            record, repo_root=f.repo, now=NOW, expected_appid=APPID,
            expected_title=TITLE, offline_fixture=True, **kwargs,
        )

    def test_a_real_writer_read_semantic_deep_projection_and_score_negative(self):
        f, pair, record, receipt_path, result = self.fixture()
        self.assertFalse(result["canonical_acceptance"])
        self.assertEqual(record["doc"]["schema"], dual.LEAN_SCHEMA)
        self.assertNotIn("provenance", record["doc"])
        self.assertNotIn("player_feedback_records", record["doc"])
        self.assertNotIn("evidence", record["doc"])
        changed = helpers.run(f.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines()
        self.assertIn(record["path"], changed)
        self.assertIn(receipt_path.relative_to(f.repo).as_posix(), changed)
        with patch.object(deep, "DOSSIER_STORE", f.repo / dual.STORE):
            # Real Deep loader SHA is raw JSON bytes, not writer's object SHA.
            loaded = deep.canonical_dossier_loader(APPID)
            self.assertEqual(loaded["content_sha256"], record["content_sha256"])
            self.assertEqual(loaded["doc"], record["doc"])
            self.assertTrue(loaded["path"].endswith(record["path"]))
        verified = self.verify(f, record)
        self.assertEqual(verified["binding"]["quality_binding"], dual.quality_binding())
        self.assertEqual(verified["receipt"]["research_commit"], pair["research_commit"])
        self.assertEqual(verified["receipt"]["assembly_commit"], pair["assembly_commit"])
        self.assertEqual(verified["receipt"]["dossier_sha256"], canonical_sha256(record["doc"]))
        self.assertNotEqual(verified["receipt"]["dossier_sha256"], record["content_sha256"])
        policy = json.loads(dual.POLICY_PATH.read_text(encoding="utf-8"))
        self.assertFalse(policy["lean_writer_enabled"])
        self.assertFalse(policy["lean_reader_enabled"])
        self.assertFalse(policy["lean_deep_enabled"])
        with self.assertRaisesRegex(ValueError, "disabled"):
            dual.inspect_accepted_lean(record, repo_root=f.repo)

        contract = json.loads(
            (dual.ROOT / "config/taste_steam_review_dossier_contract.json").read_text(encoding="utf-8")
        )
        state, binding = dual.versioned_dossier_state(
            record["doc"], contract, store_dir=f.repo / dual.STORE,
            appid=APPID, now=NOW, expected_title=TITLE, expected_ttl_days=20,
            offline_fixture=True,
        )
        self.assertEqual(state, "fresh")
        self.assertEqual(binding, verified["binding"])
        pin = {
            "schema": "TASTE-PINNED-WORK-UNIT-V1",
            "status": "active",
            "ordered_work_unit_sha256": "a" * 64,
            "ordered_rows": [{"appid": APPID, "key": "App_" + APPID,
                              "work_required": ["taste"]}],
        }
        with self.assertRaisesRegex(ValueError, "missing/stale/invalid"):
            build_semantic_input_strict(pin, contract, f.repo / dual.STORE, now=NOW)
        semantic = build_semantic_input_strict(
            pin, contract, f.repo / dual.STORE, now=NOW, lean_offline_fixture=True,
        )
        self.assertEqual(semantic["rows"][0]["dossier_binding"]["quality_binding"], binding)
        self.assertEqual(semantic["rows"][0]["dossier_binding"]["dossier_format"], dual.LEAN_SCHEMA)
        self.assertEqual(semantic["rows"][0]["dossier"], record["doc"])

        contexts = pass2_fixture.contexts()[:1]
        queue = pass2_fixture.queue()[:1]
        project = pass2_fixture.projection()
        contexts[0]["taste_subject_key"] = "App_" + APPID
        queue[0]["taste_subject_key"] = "App_" + APPID
        queue[0]["appid"] = APPID
        queue[0]["title"] = TITLE
        queue[0]["release_year"] = 2024
        project["entries"]["App_" + APPID] = project["entries"].pop("App_1")
        projected = deep.recompute_eligibility(
            context_rows=contexts, projection_doc=project, queue_rows=queue,
            pass1_state_doc=pass2_fixture.empty_pass1_state(),
            pass2_state_doc=deep.empty_state(),
            current_binding=web_dossier(APPID, NOW, title=TITLE)["web_evidence_contract_binding"],
            dossier_loader=lambda appid: record if appid == APPID else None,
            now=NOW, lean_offline_fixture=True, lean_repo_root=f.repo,
        )
        self.assertEqual(len(projected["items"]), 1, projected.get("reasons"))
        work = projected["items"][0]
        self.assertEqual(work["dossier_compatibility_binding"], binding)
        self.assertEqual(work["dossier_content_sha256"], record["content_sha256"])
        self.assertEqual(work["dossier_path"], record["path"])
        self.assertEqual(work["work_mode"], "normal_first_pass")
        self.assertTrue(work["authorization_id"])
        ok, reason = deep.dossier_is_eligible(
            binding=work, semantic_input=work["semantic_input"],
            dossier_record=record, current_binding=binding, now=NOW,
            lean_offline_fixture=True, lean_repo_root=f.repo,
        )
        self.assertEqual((ok, reason), (True, "eligible"))
        work["_dossier_record"] = record
        work["_lean_offline_fixture_root"] = f.repo
        factors = {name: 75 for name in deep.SCORE_FACTOR_IDS}
        finding = {
            "finding_id": "sulfur-mastering-01",
            "text_ru": "Активные перестрелки дают освоение навыка, хотя повторяемость маршрутов ограничивает разнообразие.",
            "candidate_evidence_refs": [
                {"kind": "observation", "index": 0},
                {"kind": "observation", "index": 1},
            ],
            "profile_evidence_refs": [{
                "json_pointer": "/preferences/movement",
                "profile_value_sha256": "a" * 64,
                "match_text_ru": "Важны освоение управления и движение",
            }],
            "factor_impacts": [
                {"factor_id": name, "effect": "supports", "normalized_value": 75}
                for name in deep.SCORE_FACTOR_IDS
            ],
        }
        scored = deep.normalize_score_findings([finding], work, factors)
        self.assertEqual(len(scored), 1)
        negative = deep.normalize_negative_assessment({
            "status": "completed",
            "evaluated_candidate_refs": [{"kind": "observation", "index": 1}],
            "findings": [{
                "disposition": "caution", "risk_code": None,
                "text_ru": "Повторение знакомых игровых маршрутов может уменьшать разнообразие.",
                "evidence_refs": [{"kind": "observation", "index": 1}],
            }],
        }, work)
        self.assertEqual(negative["status"], "completed")
        self.assertEqual(negative["findings"][0]["disposition"], "caution")
        without_fixture = copy.copy(work)
        without_fixture.pop("_lean_offline_fixture_root")
        with self.assertRaisesRegex(ValueError, "cannot be consumed as canonical"):
            deep.normalize_score_findings([finding], without_fixture, factors)

    def test_uncommitted_is_not_acceptance_and_duplicate_write_is_idempotent(self):
        f, pair, record, receipt_path, first = self.fixture(accepted=False)
        with self.assertRaisesRegex(ValueError, "not committed"):
            self.verify(f, record)
        helpers.commit(f.repo, "fixture: commit cache and receipt atomically")
        self.verify(f, record)
        second = drain_buffered_groups(notes_v2={
            "repo": f.repo, "marker_commit": f.marker, "trial_id": helpers.TRIAL,
            "item_commits": {APPID: pair},
            "store_dir": f.repo / dual.STORE,
            "accepted_dir": f.repo / dual.RECEIPTS,
            "offline_fixture": True,
        })
        self.assertEqual(next(i for i in second["items"] if i["appid"] == APPID)["status"], "already_persisted_same_binding")
        self.verify(f, record)

    def test_wrong_appid_edition_year_digest_path_and_deep_binding_fail_closed(self):
        f, _, record, _, _ = self.fixture()
        bad = copy.deepcopy(record)
        bad["doc"]["title"] = "SULFUR: Deluxe Edition"
        self.assertRaises(ValueError, self.verify, f, bad)
        bad = copy.deepcopy(record)
        bad["doc"]["game_identity"]["release_year"] = None
        self.assertRaises(ValueError, self.verify, f, bad)
        bad = copy.deepcopy(record)
        bad["doc"]["game_identity"]["release_year"] = 1901
        self.assertRaises(ValueError, self.verify, f, bad)
        bad = copy.deepcopy(record)
        bad["doc"]["appid"] = "99999"
        self.assertRaises(ValueError, self.verify, f, bad)
        bad = copy.deepcopy(record)
        bad["content_sha256"] = "0" * 64
        self.assertRaisesRegex(ValueError, "digest mismatch", self.verify, f, bad)
        bad = copy.deepcopy(record)
        bad["path"] = "data/control/dossier_notes_v2/batch_pilot_store/trial/App_" + APPID + ".json"
        self.assertRaisesRegex(ValueError, "sandbox", self.verify, f, bad)
        self.assertEqual(
            deep.dossier_is_eligible(
                binding={"appid": APPID}, semantic_input={"title": TITLE, "release_year": 2024},
                dossier_record=record, current_binding={"contract": "forged"}, now=NOW,
                lean_offline_fixture=True, lean_repo_root=f.repo,
            )[0], False,
        )
        self.assertEqual(
            deep.dossier_is_eligible(
                binding={"appid": APPID}, semantic_input={"title": TITLE, "release_year": 2024},
                dossier_record=record, current_binding={"contract": "forged"}, now=NOW,
            )[1], "lean_dossier_is_not_canonical_deep_evidence",
        )

    def test_receipt_and_git_binding_tampering_fail_closed(self):
        f, _, record, receipt_path, _ = self.fixture()
        raw = receipt_path.read_bytes()
        doc = json.loads(raw)
        for field, value in (
            ("dossier_sha256", "0"*64),
            ("assembly_commit", "0"*40),
            ("marker_commit", "0"*40),
            ("schema", "FORGED-ACCEPTANCE"),
            ("dossier_format", "TASTE-STEAM-REVIEW-DOSSIER-V2"),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(doc)
                changed[field] = value
                receipt_path.write_text(json.dumps(changed), encoding="utf-8")
                self.assertRaises(ValueError, self.verify, f, record)
                receipt_path.write_bytes(raw)
        self.verify(f, record)
        extra = receipt_path.with_name(APPID + "--duplicate.json")
        extra.write_bytes(raw)
        self.assertRaisesRegex(ValueError, "unambiguous", self.verify, f, record)
        extra.unlink()
        self.verify(f, record)
        disk = f.repo / dual.STORE / ("App_" + APPID + ".json")
        original = disk.read_bytes()
        disk.write_text(json.dumps(record["doc"], indent=2), encoding="utf-8")
        self.assertRaisesRegex(ValueError, "uncommitted", self.verify, f, record)
        disk.write_bytes(original)
        self.verify(f, record)

    def test_lean_quality_negatives_privacy_dates_pros_cons_and_expiry(self):
        f, _, record, _, _ = self.fixture()
        for mutate in (
            lambda d: [r.update(sentiment="negative") for r in d["observations"]],
            lambda d: [r.update(sentiment="positive") for r in d["observations"]],
            lambda d: d["sources"][0].update(url="http://insecure.example/app/" + APPID),
            lambda d: d["sources"][0].update(url="https://example.org/users/private"),
            lambda d: d["observations"][0].update(evidence_status="current", as_of=None),
            lambda d: d["observations"][0].update(evidence_status="current", as_of="2020-01-01"),
            lambda d: d["game_identity"].update(release_year=None),
        ):
            d = copy.deepcopy(record["doc"])
            mutate(d)
            with self.subTest(mutation=mutate.__code__.co_firstlineno):
                self.assertRaises(
                    ValueError, dual.validate_writer_lean,
                    d, appid=APPID, title=TITLE, now=NOW,
                )
        d = copy.deepcopy(record["doc"])
        d["expires_at_utc"] = d["generated_at_utc"]
        self.assertRaises(ValueError, dual.validate_writer_lean, d, appid=APPID, title=TITLE, now=NOW)
        d = copy.deepcopy(record["doc"])
        d["generated_at_utc"] = "2022-01-01T00:00:00Z"
        self.assertRaises(ValueError, dual.validate_writer_lean, d, appid=APPID, title=TITLE, now=NOW)

    def test_strict_legacy_still_uses_original_binding_and_no_lean_receipts(self):
        dossier = web_dossier(APPID, NOW, title=TITLE, release_year=2024)
        contract = json.loads(
            (dual.ROOT / "config/taste_steam_review_dossier_contract.json").read_text(encoding="utf-8")
        )
        state, binding = dual.versioned_dossier_state(
            dossier, contract, store_dir=Path("/unused/legacy/store"),
            appid=APPID, now=NOW, expected_title=TITLE,
        )
        self.assertEqual((state, binding), ("fresh", None))
        self.assertEqual(
            deep.dossier_is_eligible(
                binding={"appid": APPID}, semantic_input={"title": TITLE},
                dossier_record={
                    "path": "data/cache/taste_steam_review_dossiers/App_" + APPID + ".json",
                    "doc": dossier, "content_sha256": deep.canonical_sha256(dossier),
                }, current_binding=dossier["web_evidence_contract_binding"], now=NOW,
            ), (True, "eligible"),
        )
        self.assertEqual(dossier["schema"], "TASTE-STEAM-REVIEW-DOSSIER-V2")
        self.assertNotIn("dossier_format", dossier)
        self.assertNotIn("quality_binding", dossier)


if __name__ == "__main__":
    unittest.main()
