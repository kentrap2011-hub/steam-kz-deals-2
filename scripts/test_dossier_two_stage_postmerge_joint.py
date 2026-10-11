#!/usr/bin/env python3
"""Joint post-merge P1/P2 -> fully async Assembly -> strict V2 GitHub writer QA.

All Git commits, descriptors, submissions and canonical writer destinations
exist solely inside independently marked disposable temporary Git repositories.
No real Research, semantic execution, production Git write or network access.
"""
import copy
import json
import unittest

from dossier_two_stage_contract_guard import CONFIG, validate_research
from dossier_two_stage_final_acceptance import (
    STATUS_ACCEPTED, STATUS_GROUP_PENDING, STATUS_GROUP_READY,
    STATUS_INVALID, STATUS_VALID, inspect_original_groups,
    offline_existing_writer_handoff,
)
from dossier_two_stage_staging import receipt_paths
from taste_steam_review_dossier_group_progress import ACCEPTED, PENDING
from test_dossier_two_stage_final_acceptance import FinalAcceptanceOfflineTests
from test_dossier_two_stage_eventual_chain_qa import GitHubEventualChainAcceptanceQA


class PostmergeJointResearchAssemblyAcceptanceQA(unittest.TestCase):
    def fixture(self, *, six=False):
        # Reuse *actual merged* Research/Assembly/git marker + existing strict
        # writer fixture, not a hand-written acceptance mock or forged receipt.
        builder = FinalAcceptanceOfflineTests(
            "test_01_live_paths_fail_closed_and_contract_is_not_authoritative")
        self.addCleanup(builder.doCleanups)
        x, work, contract, path = builder.fixture(six=six)
        return builder, x, work, contract, path

    @staticmethod
    def incompatible_year(d):
        # The other physical source still corroborates the original 2020 year.
        # Distinct copied binding prevents aliasing from hiding the single bad source.
        d["sources"][1]["exact_product_binding"] = copy.deepcopy(
            d["sources"][1]["exact_product_binding"])
        d["sources"][1]["exact_product_binding"]["original_work_release_year"] = 2021

    @staticmethod
    def later_steam_publication(d):
        # Original 2020 != later Steam/port source publication in 2024.
        # Publication date is NOT a claim about original-work release year.
        d["sources"][1]["publication_date"] = "2024-08-09"
        d["sources"][1]["temporal_kind_hint"] = "historical"
        d["identity"]["corroborators"].extend([
            {"kind": "platform", "value": "Steam"},
            {"kind": "version", "value": "Later Steam port"},
        ])

    def test_01_former_xfail_is_real_negative_and_never_reaches_three_game_writer(self):
        self.assertFalse(getattr(
            GitHubEventualChainAcceptanceQA.
            test_known_gap_conflicting_source_original_year_must_be_rejected,
            "__unittest_expecting_failure__", False),
            "Former Research-year XFAIL must be an ordinary test")
        builder, x, work, contract, path = self.fixture(six=True)
        wrong = copy.deepcopy(x.docs[0])
        self.incompatible_year(wrong)
        with self.assertRaisesRegex(ValueError, "rsource-002.*2021.*2020"):
            validate_research(wrong, expected_assignment=x.docs[0]["assignment"])
        # Research result is Git-committed but has NOT been accepted by GitHub;
        # Assembly can already consume its exact bytes without sibling waiting.
        ra = x.research_submit(0, tamper=self.incompatible_year)
        ca = builder.ready(x, 0, ra)
        locators = [builder.locator(x, 0, ca)]
        # B/C are valid Research + strictly ready Assembly despite bad A.
        for i in (1, 2, 3, 4, 5):
            r = x.research_submit(i)
            locators.append(builder.locator(x, i, builder.ready(x, i, r)))
        before_github_ack = builder.inspect(x, work, contract, locators)
        self.assertEqual(before_github_ack["decisions"][0]["status"], STATUS_GROUP_PENDING)
        self.assertEqual(before_github_ack["decisions"][0]["items"][0]["status"], STATUS_INVALID)
        self.assertEqual([p["status"] for p in before_github_ack["decisions"][0]["items"][1:]],
                         [STATUS_VALID, STATUS_VALID])
        self.assertEqual(before_github_ack["decisions"][1]["status"], STATUS_GROUP_READY)
        self.assertEqual([e["sequence"] for e in before_github_ack["ready"]], [2])
        self.assertIs(before_github_ack["canonical_dossier_accepted"], False)
        self.assertIs(before_github_ack["deep_ready_issued"], False)
        # P2 actual GitHub Research validator independently rejects the same
        # committed Research A (not merely our inspector deciding to reject it).
        receipt = x.research_receive(0, ra)
        self.assertEqual(receipt["status"], "rejected_invalid")
        self.assertEqual(receipt["files"][receipt["receipt_path"]]["reason_code"],
                         "invalid_binding")
        self.assertFalse(receipt["files"][receipt["receipt_path"]].get(
            "canonical_acceptance", False))
        outcome = offline_existing_writer_handoff(
            x.f.root, inspection=before_github_ack, manifest_path=path,
            contract=contract, offline_fixture=True)
        self.assertEqual(outcome["existing_writer_result"]["accepted_sequences"], [2])
        self.assertEqual(len(outcome["existing_writer_result"]["persisted"]), 3)
        canonical = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual([p["state"] for p in canonical["group_progress"]["groups"]],
                         [PENDING, ACCEPTED])
        self.assertFalse((x.f.root / "store" / "App_12345.json").exists())
        after = builder.inspect(x, canonical, contract, locators)
        self.assertEqual(after["decisions"][1]["status"], STATUS_ACCEPTED)
        self.assertEqual(after["decisions"][0]["status"], STATUS_GROUP_PENDING)
        self.assertFalse(after["decisions"][0]["canonical_dossier_accepted"])
        self.assertFalse(after["decisions"][0]["deep_ready_issued"])

    def test_02_later_port_date_passes_P1_P2_and_original_group_strict_drain(self):
        builder, x, work, contract, path = self.fixture()
        refs = []
        for i in range(3):
            if i == 0:
                valid = copy.deepcopy(x.docs[i])
                self.later_steam_publication(valid)
                validate_research(valid, expected_assignment=x.docs[i]["assignment"])
                self.assertEqual(valid["identity"]["original_work_release_year"], 2020)
                self.assertEqual(valid["sources"][1]["publication_date"], "2024-08-09")
                r = x.research_submit(i, tamper=self.later_steam_publication)
            else:
                r = x.research_submit(i)
            # First Assembly, only then eventual GitHub P2 classification.
            refs.append(builder.locator(x, i, builder.ready(x, i, r)))
            self.assertEqual(x.research_receive(i, r)["status"],
                             "accepted_structural_evidence")
        inspected = builder.inspect(x, work, contract, refs)
        self.assertEqual(inspected["decisions"][0]["status"], STATUS_GROUP_READY)
        self.assertEqual([d["status"] for d in inspected["decisions"][0]["items"]],
                         [STATUS_VALID] * 3)
        self.assertFalse(inspected["canonical_dossier_accepted"])
        self.assertFalse(inspected["deep_ready_issued"])
        result = offline_existing_writer_handoff(
            x.f.root, inspection=inspected, manifest_path=path, contract=contract,
            offline_fixture=True)
        self.assertEqual(result["writer"], "existing_drain_buffered_groups_only")
        self.assertEqual(result["existing_writer_result"]["accepted_sequences"], [1])
        self.assertEqual(len(result["existing_writer_result"]["persisted"]), 3)
        self.assertEqual(json.loads(path.read_text())["group_progress"]["groups"][0]["state"],
                         ACCEPTED)
        self.assertEqual(builder.inspect(x, json.loads(path.read_text()), contract, refs)[
            "decisions"][0]["status"], STATUS_ACCEPTED)

    def test_03_unrelated_main_movement_does_not_rebind_frozen_marker_or_replay(self):
        builder, x, work, contract, path = self.fixture()
        refs = []
        for i in range(3):
            r = x.research_submit(i)
            refs.append(builder.locator(x, i, builder.ready(x, i, r)))
        initial = builder.inspect(x, work, contract, refs)
        self.assertEqual(initial["decisions"][0]["status"], STATUS_GROUP_READY)
        x.f.save("fixture-only/unrelated-main-movement.json", {"new_main": True})
        x.f.commit("Unrelated moving main must not change frozen Git authority")
        # Immutable original marker/transport remain valid, even after HEAD moves.
        self.assertEqual(builder.inspect(x, work, contract, refs)["ready"],
                         initial["ready"])
        result = offline_existing_writer_handoff(
            x.f.root, inspection=initial, manifest_path=path, contract=contract,
            offline_fixture=True)
        self.assertEqual(result["existing_writer_result"]["accepted_sequences"], [1])
        with self.assertRaisesRegex(ValueError, "stale canonical manifest"):
            offline_existing_writer_handoff(
                x.f.root, inspection=initial, manifest_path=path, contract=contract,
                offline_fixture=True)

    def test_04_rewrite_after_inspection_and_forged_research_receipt_fail_closed(self):
        builder, x, work, contract, path = self.fixture()
        refs = []
        for i in range(3):
            r = x.research_submit(i)
            refs.append(builder.locator(x, i, builder.ready(x, i, r)))
        inspected = builder.inspect(x, work, contract, refs)
        self.assertEqual(len(inspected["ready"]), 1)
        # A forged Research acceptance marker cannot grant strict group readiness.
        fake = receipt_paths(x.docs[0]["assignment"])["accepted"]
        x.f.save(fake, {"schema": "FORGED-RESEARCH-ACCEPTANCE"})
        x.f.commit("Fixture adversarial fabricated Research receipt")
        self.assertEqual(builder.inspect(x, work, contract, refs)[
            "decisions"][0]["items"][0]["status"], STATUS_INVALID)
        # This original inspected handoff must never be trusted at writer boundary.
        with self.assertRaisesRegex(ValueError, "untrusted, forged or stale"):
            offline_existing_writer_handoff(
                x.f.root, inspection=inspected, manifest_path=path, contract=contract,
                offline_fixture=True)
        self.assertEqual(json.loads(path.read_text())["group_progress"]["groups"][0]["state"],
                         PENDING)

    def test_05_contracts_stay_inactive_and_proof_flag_has_no_activation_authority(self):
        for name, false_fields in (
            ("dossier_two_stage_interfaces_contract.json",
             ("active", "authoritative", "authorized_for_semantic_execution",
              "authorized_for_canonical_ingest")),
            ("dossier_two_stage_staging_contract.json",
             ("active", "authoritative", "executable_in_production")),
            ("dossier_two_stage_async_buffer_contract.json",
             ("active", "authoritative", "executable_in_production")),
            ("dossier_two_stage_final_acceptance_bridge_contract.json",
             ("active", "authorized_for_canonical_ingest", "executable_in_production")),
        ):
            with self.subTest(contract=name):
                data = json.loads((CONFIG / name).read_text(encoding="utf-8"))
                for field in false_fields:
                    self.assertIs(data[field], False, (name, field))
        final = json.loads((CONFIG /
            "dossier_two_stage_final_acceptance_bridge_contract.json").read_text())
        self.assertEqual(final["shared_writer"]["concurrency_group"],
                         "taste-steam-review-dossier-canonical-writer")
        self.assertIs(final["shared_writer"]["new_live_workflow"], False)
        self.assertIs(final["safety"]["do_not_replace_one_stage"], True)


    def test_06_proof_metadata_is_boolean_only_and_cannot_open_any_live_gate(self):
        """Both proof values permit only marked disposable Git; unsafe states fail closed."""
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        import dossier_two_stage_final_acceptance as final_bridge

        builder, x, work, contract, path = self.fixture()
        original = json.loads(final_bridge.CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertIs(original["active"], False)
        self.assertIs(original["authorized_for_canonical_ingest"], False)
        self.assertIs(original["executable_in_production"], False)
        self.assertIs(original["shared_writer"]["new_live_workflow"], False)
        self.assertIs(original["safety"]["offline_fixture_only_writer"], True)

        with tempfile.TemporaryDirectory(prefix="dossier-proof-gate-") as td:
            isolated_spec = Path(td) / "bridge.json"
            with patch.object(final_bridge, "CONTRACT_PATH", isolated_spec):
                def check(spec, *, allowed):
                    isolated_spec.write_text(json.dumps(spec), encoding="utf-8")
                    if allowed:
                        self.assertEqual(
                            final_bridge.offline_gate(x.f.root, offline_fixture=True),
                            x.f.root.resolve())
                        # Neither the bridge nor its writer can be invoked as a live API.
                        with self.assertRaisesRegex(ValueError, "disabled"):
                            final_bridge.offline_gate(x.f.root)
                        with self.assertRaisesRegex(ValueError, "disabled"):
                            final_bridge.inspect_original_groups(
                                x.f.root, manifest=work, contract=contract,
                                item_locators=[])
                        with self.assertRaisesRegex(ValueError, "disabled"):
                            final_bridge.offline_existing_writer_handoff(
                                x.f.root, inspection={}, manifest_path=path,
                                contract=contract)
                    else:
                        with self.assertRaisesRegex(ValueError, "not explicitly inactive"):
                            final_bridge.offline_gate(x.f.root, offline_fixture=True)

                for proof in (False, True):
                    with self.subTest(proof=proof, case="valid fixture and live denial"):
                        spec = copy.deepcopy(original)
                        spec["cross_pr_research_original_year_fix_verified"] = proof
                        check(spec, allowed=True)
                    for field in ("active", "authorized_for_canonical_ingest",
                                  "executable_in_production"):
                        for unsafe in (True, None, "false"):
                            with self.subTest(proof=proof, field=field, unsafe=unsafe):
                                spec = copy.deepcopy(original)
                                spec["cross_pr_research_original_year_fix_verified"] = proof
                                spec[field] = unsafe
                                check(spec, allowed=False)
                    with self.subTest(proof=proof, case="writer domain mismatch"):
                        spec = copy.deepcopy(original)
                        spec["cross_pr_research_original_year_fix_verified"] = proof
                        spec["shared_writer"]["concurrency_group"] = "other-writer"
                        check(spec, allowed=False)

                for invalid in (None, 0, 1, "true", "false", [], {}):
                    with self.subTest(case="invalid proof type", invalid=invalid):
                        spec = copy.deepcopy(original)
                        spec["cross_pr_research_original_year_fix_verified"] = invalid
                        check(spec, allowed=False)
                with self.subTest(case="missing proof key"):
                    spec = copy.deepcopy(original)
                    spec.pop("cross_pr_research_original_year_fix_verified")
                    check(spec, allowed=False)

                for proof in (False, True):
                    spec = copy.deepcopy(original)
                    spec["cross_pr_research_original_year_fix_verified"] = proof
                    isolated_spec.write_text(json.dumps(spec), encoding="utf-8")
                    with self.subTest(proof=proof, case="real checkout rejected"):
                        with self.assertRaisesRegex(ValueError, "separate disposable"):
                            final_bridge.offline_gate(Path.cwd(), offline_fixture=True)
                    with self.subTest(proof=proof, case="fixture marker required"):
                        marker = x.f.root / ".dossier-final-offline-fixture"
                        saved = marker.read_bytes()
                        marker.unlink()
                        try:
                            with self.assertRaisesRegex(ValueError, "separate disposable"):
                                final_bridge.offline_gate(x.f.root, offline_fixture=True)
                        finally:
                            marker.write_bytes(saved)

    def test_07_both_proof_values_preserve_full_year_rejection_and_strict_group_chain(self):
        """Proof does not decide P1/P2/Assembly/GitHub decisions or writer authority."""
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        import dossier_two_stage_final_acceptance as final_bridge

        original = json.loads(final_bridge.CONTRACT_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="dossier-proof-joint-") as td:
            isolated_spec = Path(td) / "bridge.json"
            with patch.object(final_bridge, "CONTRACT_PATH", isolated_spec):
                for proof in (False, True):
                    with self.subTest(proof=proof):
                        spec = copy.deepcopy(original)
                        spec["cross_pr_research_original_year_fix_verified"] = proof
                        isolated_spec.write_text(json.dumps(spec), encoding="utf-8")
                        builder, x, work, contract, path = self.fixture(six=True)
                        refs = []
                        for i in range(6):
                            if i == 0:
                                bad = copy.deepcopy(x.docs[i])
                                self.incompatible_year(bad)
                                with self.assertRaisesRegex(
                                        ValueError, "rsource-002.*2021.*2020"):
                                    validate_research(
                                        bad, expected_assignment=x.docs[i]["assignment"])
                                r = x.research_submit(i, tamper=self.incompatible_year)
                            elif i == 1:
                                good = copy.deepcopy(x.docs[i])
                                self.later_steam_publication(good)
                                validate_research(
                                    good, expected_assignment=x.docs[i]["assignment"])
                                r = x.research_submit(
                                    i, tamper=self.later_steam_publication)
                            else:
                                r = x.research_submit(i)
                            # Assembly is allowed to submit before Research receipt.
                            refs.append(builder.locator(x, i, builder.ready(x, i, r)))
                            receipt = x.research_receive(i, r)
                            self.assertEqual(
                                receipt["status"], "rejected_invalid" if i == 0
                                else "accepted_structural_evidence")
                            if i == 0:
                                self.assertEqual(
                                    receipt["files"][receipt["receipt_path"]]["reason_code"],
                                    "invalid_binding")
                        inspected = builder.inspect(x, work, contract, refs)
                        self.assertEqual(
                            [e["sequence"] for e in inspected["ready"]], [2])
                        self.assertEqual(
                            inspected["decisions"][0]["items"][0]["status"], STATUS_INVALID)
                        self.assertEqual(
                            inspected["decisions"][0]["status"], STATUS_GROUP_PENDING)
                        self.assertEqual(
                            inspected["decisions"][1]["status"], STATUS_GROUP_READY)
                        self.assertIs(inspected["canonical_dossier_accepted"], False)
                        self.assertIs(inspected["deep_ready_issued"], False)
                        result = offline_existing_writer_handoff(
                            x.f.root, inspection=inspected, manifest_path=path,
                            contract=contract, offline_fixture=True)
                        self.assertEqual(
                            result["existing_writer_result"]["accepted_sequences"], [2])
                        self.assertEqual(
                            len(result["existing_writer_result"]["persisted"]), 3)
                        self.assertEqual(
                            [e["state"] for e in
                             json.loads(path.read_text())["group_progress"]["groups"]],
                            [PENDING, ACCEPTED])
                        self.assertFalse(
                            (x.f.root / "store" / "App_12345.json").exists())


if __name__ == "__main__":
    unittest.main()
