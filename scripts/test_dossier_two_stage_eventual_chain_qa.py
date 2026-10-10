#!/usr/bin/env python3
"""Independent, inactive GitHub Research→Assembly chain QA in disposable Git repos.

All evidence and game identifiers are fixture-only. The tested checker returns
item-local *noncanonical* findings; this test does NOT implement final ingest.
"""
import copy
import json
import tempfile
import unittest

from dossier_two_stage_async_buffer import (
    frozen_buffer, inspect_buffered_assembly_candidate, provisional_assembly_work,
)
from dossier_two_stage_staging import receipt_paths
from taste_steam_review_dossier_buffered import validate_buffer_artifact
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA
from test_dossier_two_stage_async_buffer import AsyncFixture


class GitHubEventualChainAcceptanceQA(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return AsyncFixture(tmp.name)

    def assert_staged_only(self, decision, *, status=None):
        if status is not None:
            self.assertEqual(decision["status"], status)
        self.assertIs(decision["canonical_dossier_accepted"], False)
        self.assertIs(decision["deep_ready"], False)
        self.assertIs(decision["item_local_only"], True)

    def test_a_later_rejected_research_is_local_b_c_survive_github_lag(self):
        x = self.fixture()
        x.preauthorize_assembly()
        ra = x.research_submit(0, tamper=lambda d: d["findings"][0].update(
            support_feedback_refs=["rfeedback-999"]))
        # Assembly can be submitted *before* eventual Research verdict.
        ca = x.assembly_submit(0, ra)
        self.assert_staged_only(x.inspect(0, ca), status="research_rejected_item_chain_quarantined")
        for i in (1, 2):
            ri = x.research_submit(i)
            ci = x.assembly_submit(i, ri)
            self.assert_staged_only(x.inspect(i, ci),
                                    status="typed_assembly_item_pending_github_classification")
        self.assertEqual(len(frozen_buffer(
            x.f.root, marker_commit=x.amarker, buffer_path=x.abuffer["path"],
            phase="assembly")["items"]), 3)

    def test_original_research_commit_path_blob_raw_and_canonical_hash(self):
        for key, replacement in (
            ("research_package_git_commit", "a" * 40),
            ("research_package_path", "data/ai_inbox/dossier_research/" + "a" * 64
             + "/g000001/12345--research-fixture-0001.json"),
            ("research_package_blob_sha", "b" * 40),
            ("research_package_raw_sha256", "b" * 64),
            ("research_package_sha256", "b" * 64),
            ("research_prepared_work_blob_sha", "c" * 40),
            ("assembly_plan_blob_sha", "c" * 40),
            ("research_marker_anchor_commit", "d" * 40),
        ):
            with self.subTest(key=key):
                x = self.fixture()
                x.preauthorize_assembly()
                r = x.research_submit(0)
                c = x.assembly_submit(
                    0, r, mutate=lambda d, k=key, v=replacement:
                    d["research_transport"].update({k: v}))
                with self.assertRaises(ValueError):
                    x.inspect(0, c)

    def test_frozen_plan_prompt_original_assignment_and_assembly_marker(self):
        for field, value in (
            ("assembly_assignment_id", "assembly-foreign-0001"),
            ("assembly_contract_sha256", "1" * 64),
            ("assembly_prompt_sha256", "2" * 64),
            ("assembly_marker_anchor_commit", "3" * 40),
            ("assembly_marker_nonce", "4" * 32),
            ("output_path", "data/ai_inbox/dossier_assembly/" + "a" * 64
             + "/g000001/12345--assembly-foreign-0001.json"),
        ):
            with self.subTest(field=field):
                x = self.fixture()
                x.preauthorize_assembly()
                r = x.research_submit(0)
                c = x.assembly_submit(0, r, mutate=lambda d, k=field, v=value:
                                      d.update({k: v}))
                with self.assertRaises(ValueError):
                    x.inspect(0, c)
        x = self.fixture()
        x.preauthorize_assembly()
        r = x.research_submit(0)
        c = x.assembly_submit(0, r, mutate=lambda d: d[
            "original_research_assignment"].update(appid="999999"))
        with self.assertRaises(ValueError):
            x.inspect(0, c)

    def test_duplicate_stale_and_overwritten_transport_rejected(self):
        x = self.fixture()
        x.preauthorize_assembly()
        r = x.research_submit(0)
        c = x.assembly_submit(0, r)
        self.assert_staged_only(x.inspect(0, c))
        # Later rewrite of the exact file is not a new create-only result.
        path = x.assembly_work(0, r)["output_path"]
        x.f.save(path, {"schema": "tampered"})
        overwrite = x.f.commit("Disallowed duplicate/overwrite of Assembly transport")
        with self.assertRaises(ValueError):
            x.inspect(0, overwrite)
        # Wrong member is never reinterpreted as valid work for another game.
        with self.assertRaises(ValueError):
            x.inspect(1, c)

    def test_foreign_work_and_unauthorized_retry_cannot_expand_frozen_scope(self):
        x = self.fixture()
        x.preauthorize_assembly(indexes=(0,))
        r = x.research_submit(1)
        with self.assertRaises(ValueError):
            provisional_assembly_work(
                x.f.root, marker_commit=x.amarker, buffer_path=x.abuffer["path"],
                work_path=receipt_paths(x.docs[1]["assignment"])["assembly_plan"],
                package_commit=r)
        # Research submission for B cannot be passed off as Research A.
        with self.assertRaises(ValueError):
            x.assembly_work(0, r)

    def test_forged_research_accepted_receipt_is_not_a_valid_chain(self):
        x = self.fixture()
        x.preauthorize_assembly()
        r = x.research_submit(0)
        c = x.assembly_submit(0, r)
        # Untrusted receipt in working Git tree cannot authorize acceptance.
        receipt = receipt_paths(x.docs[0]["assignment"])["accepted"]
        x.f.save(receipt, {"schema": "FORGED-RESEARCH-ACCEPTANCE"})
        x.f.commit("Adversarial forged Research acceptance in disposable history")
        with self.assertRaises(ValueError):
            x.inspect(0, c)

    def test_research_privacy_and_invalid_feedback_are_fail_closed(self):
        for mutate in (
            lambda d: d["sources"][0].update(author="Private User"),
            lambda d: d["findings"][0].update(support_feedback_refs=["rfeedback-999"]),
            lambda d: d["observed_feedback"][0].update(parent_source_ref="rsource-999"),
        ):
            with self.subTest(mutation=str(mutate)):
                x = self.fixture()
                x.preauthorize_assembly()
                r = x.research_submit(0, tamper=mutate)
                c = x.assembly_submit(0, r)
                self.assert_staged_only(x.inspect(0, c),
                                        status="research_rejected_item_chain_quarantined")

    def test_candidate_schema_strictness_and_deep_readiness_forgery(self):
        for mutate in (
            lambda d: d.update(canonical_acceptance=True),
            lambda d: d.update(deep_ready=True),
            lambda d: d.update(staged_only=False),
            lambda d: d.update(outcome="assembled_candidate_ready"),
            lambda d: d["payload"].update(normal_first_pass_attempt_consumed=True),
        ):
            with self.subTest(mutation=str(mutate)):
                x = self.fixture()
                x.preauthorize_assembly()
                r = x.research_submit(0)
                c = x.assembly_submit(0, r, mutate=mutate)
                with self.assertRaises(ValueError):
                    x.inspect(0, c)

    def test_first_parent_marker_cannot_be_swapped(self):
        x = self.fixture()
        x.preauthorize_assembly()
        r = x.research_submit(0)
        c = x.assembly_submit(0, r)
        with self.assertRaises(ValueError):
            inspect_buffered_assembly_candidate(
                x.f.root, marker_commit=x.f.marker,  # Research marker is NOT Assembly marker
                buffer_path=x.abuffer["path"], work_path=x.apaths[0],
                result_commit=c)
        self.assert_staged_only(x.inspect(0, c))

    def test_original_three_item_group_cannot_be_accepted_partially_or_shifted(self):
        # Current strict one-stage buffered ingress: actual group descriptor is
        # three items, and its dossier ID/order boundary is immutable.
        x = self.fixture()
        descriptor = x.f.descriptor
        self.assertEqual(len(descriptor["items"]), 3)
        base = {k: copy.deepcopy(descriptor[k]) for k in (
            "snapshot_id", "prepared_required_sha256", "sequence",
            "start_index", "end_index_exclusive", "items", "appids",
            "items_sha256", "group_sha256", "scope_source", "source_queue_sha256")}
        base.update(schema=BUFFER_GROUP_SCHEMA, schema_version=1)
        for dossiers in (
            [{"appid": "12345"}, {"appid": "23456"}],
            [{"appid": "23456"}, {"appid": "34567"}, {"appid": "12345"}],
            [{"appid": "12345"}, {"appid": "23456"}, {"appid": "23456"}],
            [{"appid": "12345"}, {"appid": "23456"}, {"appid": "99999"}],
        ):
            with self.subTest(ids=[d["appid"] for d in dossiers]):
                artifact = {**base, "dossiers": dossiers}
                with self.assertRaises(ValueError):
                    validate_buffer_artifact(artifact, descriptor, {"ttl_days": 30}, {})
        # Three item-local validator verdicts do not publish any group or Deep flag.
        x.preauthorize_assembly()
        for i in range(3):
            r = x.research_submit(i)
            c = x.assembly_submit(i, r)
            self.assert_staged_only(x.inspect(i, c))

    @unittest.expectedFailure
    def test_known_gap_conflicting_source_original_year_must_be_rejected(self):
        """Activation blocker: source exact-work year conflicts with Research identity.

        Expected-failure tracks current Research validator weakness without
        changing the shared helper owned outside this task. Never treat xfail as
        a proof of safety or as authorization for live ingest.
        """
        x = self.fixture()
        r = x.research_submit(0, tamper=lambda d: [
            source["exact_product_binding"].update(original_work_release_year=2021)
            for source in d["sources"] if source["exact_product_binding"] is not None
        ])
        decision = x.research_receive(0, r)
        self.assertNotEqual(decision["status"], "accepted_structural_evidence")


if __name__ == "__main__":
    unittest.main()
