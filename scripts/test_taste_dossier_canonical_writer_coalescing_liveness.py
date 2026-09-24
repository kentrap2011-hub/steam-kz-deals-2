#!/usr/bin/env python3
"""Regression for coalesced/cancelled Dossier wake-ups inside the shared writer."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import progressive_pass2
import test_progressive_pass2 as deep_core
import test_taste_steam_review_dossier_buffered_submission as fixture
from ingest_taste_steam_review_dossier_inbox import drain_inbox_state
from taste_steam_review_dossier_parallel_validation import write_parallel_validation_status
from taste_steam_review_dossier_web import build_daily_work_manifest_web


ROOT = Path(__file__).resolve().parents[1]
WRITER_GROUP = "group: taste-steam-review-dossier-canonical-writer"
RECONCILE = "python scripts/ingest_taste_steam_review_dossier_inbox.py --reconcile-nonfatal"
VALIDATE = "python scripts/taste_steam_review_dossier_parallel_validation.py"
DEEP_RECOMPUTE = "python scripts/build_progressive_pass2_work.py"
WRITERS = {
    ".github/workflows/build-pre-ai-store-snapshot.yml",
    ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml",
    ".github/workflows/ingest-progressive-pass1.yml",
    ".github/workflows/ingest-progressive-pass2.yml",
    ".github/workflows/authorize-progressive-pass2-recovery.yml",
}


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _isolated_contract(td):
    root = Path(td)
    contract = copy.deepcopy(fixture.BASE_CONTRACT)
    paths = contract["paths"]
    paths["submission_inbox_dir"] = (root / "buffer").as_posix()
    paths["dossier_store_dir"] = (root / "store").as_posix()
    paths["work_manifest"] = (root / "work.json").as_posix()
    paths["worker_index"] = (root / "worker_index.json").as_posix()
    paths["worker_groups_root"] = (root / "worker_groups").as_posix()
    contract["worker_read_projection"]["descriptor_path_template"] = (
        paths["worker_groups_root"].rstrip("/") + "/{snapshot_id}/g{sequence:06d}.json"
    )
    contract_path = root / "contract.json"
    _write_json(contract_path, contract)
    return contract, contract_path


def _setup_candidate(td, *, invalid=False):
    root = Path(td)
    contract, contract_path = _isolated_contract(td)
    store = root / "store"
    work = build_daily_work_manifest_web(
        fixture.queue([1, 2, 3]),
        contract,
        store,
        now=fixture.NOW,
    )
    manifest_path = Path(contract["paths"]["work_manifest"])
    _write_json(manifest_path, work)

    def mutate(artifact):
        if invalid:
            artifact["dossiers"][0]["appid"] = "999999"

    candidate = fixture.write_group(
        work,
        contract,
        1,
        mutate=mutate if invalid else None,
    )
    return {
        "root": root,
        "contract": contract,
        "contract_path": contract_path,
        "manifest_path": manifest_path,
        "store": store,
        "candidate": candidate,
        "work": work,
        "quarantine": root / "quarantine",
        "audit": root / "failures.jsonl",
    }


def _drain(env):
    return drain_inbox_state(
        manifest_path=env["manifest_path"],
        contract_path=env["contract_path"],
        store_dir=env["store"],
        buffer_dir=env["contract"]["paths"]["submission_inbox_dir"],
        failed_quarantine_root=env["quarantine"],
        failure_audit_path=env["audit"],
        fail_on_blocked=False,
    )


def _canonical_dossier_loader(store):
    def load(appid):
        path = Path(store) / f"App_{appid}.json"
        if not path.exists():
            return None
        raw = path.read_bytes()
        return {
            "path": path.as_posix(),
            "doc": json.loads(raw.decode("utf-8")),
            "content_sha256": hashlib.sha256(raw).hexdigest(),
        }
    return load


class CanonicalWriterCoalescingLivenessTests(unittest.TestCase):
    def test_cancelled_wakeup_surviving_writer_classifies_present_candidate_once(self):
        """Durable candidate + lost wake-up is recovered from repository state by writer B."""
        with tempfile.TemporaryDirectory() as td:
            env = _setup_candidate(td)

            # Equivalent causal point after writer A is active and the Dossier
            # wake-up is cancelled before job start: transport exists durably,
            # but canonical progress still says pending.
            before = json.loads(env["manifest_path"].read_text(encoding="utf-8"))
            self.assertEqual(before["group_progress"]["pending_group_count"], 1)
            self.assertTrue(env["candidate"].exists())
            self.assertEqual(list(env["store"].glob("App_*.json")), [])

            # Align the generic Deep semantic fixture to the generic Dossier
            # fixture's release year; this test is about canonical visibility,
            # not historical/current production game identity.
            deep_queue = copy.deepcopy(deep_core.queue())
            for row in deep_queue:
                row["release_date"] = "1 Jan, 2020"

            # Transport alone must not unlock Deep.
            pre_deep = progressive_pass2.recompute_eligibility(
                context_rows=deep_core.contexts(),
                projection_doc=deep_core.projection(),
                queue_rows=deep_queue,
                pass1_state_doc=deep_core.empty_pass1_state(),
                pass2_state_doc=deep_core.empty_pass2_state(),
                current_binding=env["work"]["web_evidence_contract_binding"],
                dossier_loader=lambda _appid: None,
                now=deep_core.NOW,
            )
            self.assertEqual(pre_deep["items"], [])

            # Surviving writer B does not need the original event. It reads the
            # current repository state and classifies the already-present candidate.
            first = _drain(env)
            self.assertEqual(first["accepted_group_count_this_run"], 1)
            self.assertEqual(first["failed_group_count_this_run"], 0)
            self.assertEqual(len(first["persisted"]), 3)
            self.assertFalse(env["candidate"].exists())

            after = json.loads(env["manifest_path"].read_text(encoding="utf-8"))
            self.assertEqual(after["group_progress"]["accepted_group_count"], 1)
            self.assertEqual(after["group_progress"]["pending_group_count"], 0)
            self.assertEqual(after["group_progress"]["groups"][0]["state"], "accepted")

            index = json.loads(Path(env["contract"]["paths"]["worker_index"]).read_text(encoding="utf-8"))
            self.assertIsNone(index["next_pending_sequence"])
            self.assertEqual(index["pending_group_sequences"], [])
            self.assertTrue(index["normal_first_pass_complete"])

            # Downstream Deep projection now sees only the post-reconcile canonical
            # dossier store, never the transport candidate itself.
            post_deep = progressive_pass2.recompute_eligibility(
                context_rows=deep_core.contexts(),
                projection_doc=deep_core.projection(),
                queue_rows=deep_queue,
                pass1_state_doc=deep_core.empty_pass1_state(),
                pass2_state_doc=deep_core.empty_pass2_state(),
                current_binding=env["work"]["web_evidence_contract_binding"],
                dossier_loader=_canonical_dossier_loader(env["store"]),
                now=deep_core.NOW,
            )
            self.assertEqual(
                {item["family_id"] for item in post_deep["items"]},
                {"game:1", "game:2"},
            )

            status_path = env["root"] / "validation_status.json"
            _, status = write_parallel_validation_status(
                manifest_path=env["manifest_path"],
                dossier_contract_path=env["contract_path"],
                buffer_dir=env["contract"]["paths"]["submission_inbox_dir"],
                output_path=status_path,
            )
            self.assertEqual(status["accepted_group_count"], 1)
            self.assertEqual(status["pending_group_count"], 0)
            self.assertEqual(status["candidate_count"], 0)

            # A later surviving writer is idempotent: no double accept, no double
            # persistence, and the semantic worker is not re-authorized.
            second = _drain(env)
            self.assertEqual(second["accepted_group_count_this_run"], 0)
            self.assertEqual(second["failed_group_count_this_run"], 0)
            self.assertEqual(second["persisted"], [])
            self.assertEqual(len(list(env["store"].glob("App_*.json"))), 3)
            index2 = json.loads(Path(env["contract"]["paths"]["worker_index"]).read_text(encoding="utf-8"))
            self.assertIsNone(index2["next_pending_sequence"])
            self.assertEqual(index2["accepted_group_count"], 1)

    def test_invalid_present_candidate_fails_once_and_enters_existing_recovery_state(self):
        with tempfile.TemporaryDirectory() as td:
            env = _setup_candidate(td, invalid=True)
            first = _drain(env)
            self.assertEqual(first["accepted_group_count_this_run"], 0)
            self.assertEqual(first["failed_group_count_this_run"], 1)
            self.assertFalse(env["candidate"].exists())

            after = json.loads(env["manifest_path"].read_text(encoding="utf-8"))
            entry = after["group_progress"]["groups"][0]
            self.assertEqual(entry["state"], "failed_or_invalid_pending_recovery")
            self.assertTrue(entry["failure"]["recovery_eligible"])
            index = json.loads(Path(env["contract"]["paths"]["worker_index"]).read_text(encoding="utf-8"))
            self.assertEqual(index["failed_group_sequences"], [1])
            self.assertEqual(index["pending_group_sequences"], [])
            self.assertIsNone(index["next_pending_sequence"])
            self.assertEqual(len(env["audit"].read_text(encoding="utf-8").splitlines()), 1)

            second = _drain(env)
            self.assertEqual(second["accepted_group_count_this_run"], 0)
            self.assertEqual(second["failed_group_count_this_run"], 0)
            self.assertEqual(len(env["audit"].read_text(encoding="utf-8").splitlines()), 1)

    def test_every_shared_writer_reconciles_state_before_dependent_projection_or_write(self):
        actual = set()
        text_by_path = {}
        for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
            text = path.read_text(encoding="utf-8")
            if "taste-steam-review-dossier-canonical-writer" in text:
                rel = path.relative_to(ROOT).as_posix()
                actual.add(rel)
                text_by_path[rel] = text

        self.assertEqual(actual, WRITERS)
        for rel in sorted(WRITERS):
            workflow = text_by_path[rel]
            self.assertIn(WRITER_GROUP, workflow)
            self.assertIn("cancel-in-progress: false", workflow)
            self.assertEqual(workflow.count(RECONCILE), 1)
            self.assertEqual(workflow.count(VALIDATE), 1)
            self.assertNotIn("schedule:", workflow)
            staging_surface = workflow
            for helper in (
                "scripts/stage_progressive_pass1_canonical_writer.sh",
                "scripts/stage_progressive_pass2_canonical_writer.sh",
            ):
                if helper in workflow:
                    staging_surface += "\n" + (ROOT / helper).read_text(encoding="utf-8")
            for staged in (
                "data/cache/taste_steam_review_dossiers",
                "data/production/pre_ai/taste_steam_review_dossier_work.json",
                "data/production/pre_ai/taste_steam_review_dossier_worker_index.json",
                "data/production/pre_ai/taste_steam_review_dossier_validation_status.json",
                "data/ai_inbox/taste_steam_review_dossiers",
            ):
                self.assertIn(staged, staging_surface)

        for rel in (
            ".github/workflows/build-pre-ai-store-snapshot.yml",
            ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml",
            ".github/workflows/ingest-progressive-pass1.yml",
        ):
            workflow = text_by_path[rel]
            self.assertLess(workflow.index(RECONCILE), workflow.index(DEEP_RECOMPUTE))

        pass1 = text_by_path[".github/workflows/ingest-progressive-pass1.yml"]
        self.assertLess(pass1.index(RECONCILE), pass1.index("python scripts/ingest_progressive_pass1.py"))
        self.assertLess(pass1.index("python scripts/ingest_progressive_pass1.py"), pass1.index(DEEP_RECOMPUTE))

        pass2 = text_by_path[".github/workflows/ingest-progressive-pass2.yml"]
        self.assertLess(
            pass2.index(RECONCILE),
            pass2.index("python scripts/ingest_progressive_pass2.py"),
        )
        pass2_ingest = (ROOT / "scripts/ingest_progressive_pass2.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("build_progressive_pass2_work.build_work_document()", pass2_ingest)

        recovery = text_by_path[".github/workflows/authorize-progressive-pass2-recovery.yml"]
        self.assertLess(recovery.index(RECONCILE), recovery.index("python scripts/authorize_progressive_pass2_recovery.py"))
        recovery_script = (ROOT / "scripts/authorize_progressive_pass2_recovery.py").read_text(encoding="utf-8")
        self.assertIn("build_progressive_pass2_work.build_work_document()", recovery_script)



if __name__ == "__main__":
    unittest.main()
