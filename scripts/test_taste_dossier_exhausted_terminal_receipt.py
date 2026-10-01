#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import taste_steam_review_dossier_buffered as buffered
from taste_steam_review_dossier_buffered import plan_buffered_drain
from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_terminal import (
    TERMINAL_RECEIPT_SCHEMA,
    expected_terminal_receipt_path,
    validate_terminal_receipt,
)
from taste_steam_review_dossier_web import build_daily_work_manifest_web
from test_taste_steam_review_dossier_buffered_submission import (
    contract_for,
    queue,
    write_group,
)

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")


def terminal_receipt(work, sequence=1, *, stop_class="existence_established_access_unresolved"):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    receipt = copy.deepcopy(descriptor)
    receipt["schema"] = TERMINAL_RECEIPT_SCHEMA
    receipt["schema_version"] = 1
    receipt.update({
        "execution_status": "semantic_exhaustion_no_valid_dossier",
        "semantic_stop_class": stop_class,
        "valid_dossier_produced": False,
        "normal_first_pass_attempt_consumed": True,
        "blocked_game": {
            "appid": descriptor["items"][0]["appid"],
            "title": descriptor["items"][0]["title"],
        },
        "route_exhaustion": {
            "russian": "exhausted",
            "source_diversification": "exhausted",
            "identity": "not_applicable",
            "temporal": "not_applicable",
            "next_required_step_status": "none_all_required_routes_exhausted",
        },
    })
    return receipt


def write_terminal(work, contract, sequence=1, mutate=None, *, path_override=None):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    receipt = terminal_receipt(work, sequence)
    if mutate:
        mutate(receipt)
    path = Path(path_override) if path_override else expected_terminal_receipt_path(descriptor, contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, receipt


class ExhaustedTerminalReceiptTests(unittest.TestCase):
    def _work(self, td, start=610000, count=9, day_offset=0):
        contract = contract_for(td)
        store = Path(td) / "store"
        work = build_daily_work_manifest_web(
            queue(range(start, start + count)),
            contract,
            store,
            now=NOW + timedelta(days=day_offset),
        )
        return contract, store, work

    def _apply(self, td, work, store, plan):
        manifest_path = Path(td) / "work.json"
        manifest_path.write_text(json.dumps(work), encoding="utf-8")
        buffered.apply_buffered_drain(
            plan,
            manifest_path=manifest_path,
            store_dir=store,
            failure_audit_path=Path(td) / "failure.jsonl",
            rejection_audit_path=Path(td) / "rejection.jsonl",
        )
        return manifest_path

    def test_semantic_exhaustion_consumes_exact_group_once_and_later_group_continues(self):
        with tempfile.TemporaryDirectory() as td:
            contract, store, work = self._work(td)
            terminal_path, _ = write_terminal(work, contract, 1)
            candidate2 = write_group(work, contract, 2)
            plan = plan_buffered_drain(
                work,
                contract,
                contract["paths"]["submission_inbox_dir"],
                terminal_receipt_archive_root=Path(td) / "terminal-archive",
                retryable_rejection_root=Path(td) / "retryable",
            )
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["failed"]], [1])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [2])
            self.assertEqual(plan["rejected_count"], 0)
            manifest_path = self._apply(td, work, store, plan)
            current = json.loads(manifest_path.read_text(encoding="utf-8"))
            first = current["group_progress"]["groups"][0]
            second = current["group_progress"]["groups"][1]
            third = current["group_progress"]["groups"][2]
            self.assertEqual(first["state"], "failed_or_invalid_pending_recovery")
            self.assertEqual(first["failure"]["failure_class"], "semantic_exhaustion")
            self.assertTrue(first["failure"]["normal_first_pass_attempt_consumed"])
            self.assertFalse(first["failure"]["valid_dossier_produced"])
            self.assertEqual(second["state"], "accepted")
            self.assertEqual(third["state"], "pending")
            self.assertFalse(terminal_path.exists())
            self.assertFalse(candidate2.exists())

    def test_malformed_or_unexhausted_terminal_is_retryable_pending_zero_attempt(self):
        for name, mutate in (
            ("malformed", lambda r: r.__setitem__("semantic_stop_class", "worker_failure")),
            ("unexhausted", lambda r: r["route_exhaustion"].__setitem__("next_required_step_status", "blocked")),
            ("pending_route", lambda r: r["route_exhaustion"].__setitem__("source_diversification", "pending")),
            ("unresolved_identity", lambda r: r["route_exhaustion"].__setitem__("identity", "exhausted")),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                contract, store, work = self._work(td)
                path, _ = write_terminal(work, contract, 1, mutate)
                plan = plan_buffered_drain(
                    work,
                    contract,
                    contract["paths"]["submission_inbox_dir"],
                    retryable_rejection_root=Path(td) / "retryable",
                )
                self.assertEqual(plan["failed_count"], 0)
                self.assertEqual(plan["rejected_count"], 1)
                self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][0]["state"], "pending")
                manifest_path = self._apply(td, work, store, plan)
                self.assertFalse(path.exists())
                current = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(current["group_progress"]["groups"][0]["state"], "pending")

    def test_wrong_group_identity_terminal_is_retryable_pending(self):
        with tempfile.TemporaryDirectory() as td:
            contract, _, work = self._work(td)
            descriptor = work["submission_group_plan"]["groups"][0]
            wrong_path = (
                Path(contract["paths"]["submission_inbox_dir"])
                / f"{work['snapshot_id']}--g000001--{'0' * 64}--terminal.json"
            )
            path, _ = write_terminal(work, contract, 1, path_override=wrong_path)
            plan = plan_buffered_drain(
                work,
                contract,
                contract["paths"]["submission_inbox_dir"],
                retryable_rejection_root=Path(td) / "retryable",
            )
            self.assertEqual(plan["failed_count"], 0)
            self.assertEqual(plan["rejected_count"], 1)
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][0]["state"], "pending")
            self.assertNotEqual(path, expected_terminal_receipt_path(descriptor, contract))

    def test_stale_snapshot_terminal_cannot_consume_current_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            contract, _, old = self._work(td, start=620000, day_offset=0)
            _, _, current = self._work(td, start=630000, day_offset=1)
            stale, _ = write_terminal(old, contract, 1)
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(plan["failed_count"], 0)
            self.assertEqual(plan["rejected_count"], 0)
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][0]["state"], "pending")
            self.assertTrue(stale.exists())

    def test_invalid_dossier_candidate_is_retryable_transport_not_semantic_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            contract, _, work = self._work(td)
            path = write_group(
                work,
                contract,
                1,
                lambda a: a["dossiers"][0].__setitem__("schema_version", True),
            )
            plan = plan_buffered_drain(
                work,
                contract,
                contract["paths"]["submission_inbox_dir"],
                retryable_rejection_root=Path(td) / "retryable",
            )
            self.assertEqual(plan["failed_count"], 0)
            self.assertEqual(plan["rejected_count"], 1)
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][0]["state"], "pending")
            self.assertTrue(path.exists())

    def test_terminal_receipt_rejects_ledger_or_raw_evidence_payload_fields(self):
        with tempfile.TemporaryDirectory() as td:
            contract, _, work = self._work(td)
            descriptor = work["submission_group_plan"]["groups"][0]
            receipt = terminal_receipt(work)
            validate_terminal_receipt(receipt, descriptor)
            for field, value in (
                ("material_attempts", [{"observable_result": "raw text"}]),
                ("review_body", "raw review body"),
                ("username", "author"),
            ):
                bad = copy.deepcopy(receipt)
                bad[field] = value
                with self.assertRaises(ValueError):
                    validate_terminal_receipt(bad, descriptor)

    def test_exact_terminal_replay_is_cleanup_only_no_second_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            contract, store, work = self._work(td, count=6)
            path, receipt = write_terminal(work, contract, 1)
            archive = Path(td) / "terminal-archive"
            plan = plan_buffered_drain(
                work,
                contract,
                contract["paths"]["submission_inbox_dir"],
                terminal_receipt_archive_root=archive,
            )
            manifest_path = self._apply(td, work, store, plan)
            current = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["group_progress"]["failed_group_count"], 1)

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            replay_plan = plan_buffered_drain(
                current,
                contract,
                contract["paths"]["submission_inbox_dir"],
                terminal_receipt_archive_root=archive,
            )
            self.assertEqual(replay_plan["failed_count"], 0)
            self.assertEqual(len(replay_plan["terminal_replays"]), 1)
            buffered.apply_buffered_drain(
                replay_plan,
                manifest_path=manifest_path,
                store_dir=store,
                failure_audit_path=Path(td) / "failure.jsonl",
                rejection_audit_path=Path(td) / "rejection.jsonl",
            )
            after = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(after["group_progress"]["failed_group_count"], 1)
            self.assertEqual(after["group_progress"]["groups"][0]["state"], "failed_or_invalid_pending_recovery")
            self.assertFalse(path.exists())

    def test_runtime_and_workflow_preserve_existing_scheduler_and_writer_boundary(self):
        runtime = (ROOT / "config/taste_steam_review_dossier_runtime_prompt.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text(encoding="utf-8")
        ownership = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))
        self.assertIn("must never enable, disable, pause, delete, reschedule, or edit its own Scheduled Task", runtime)
        self.assertIn("group: taste-steam-review-dossier-canonical-writer", workflow)
        dossier = ownership["taste_steam_review_dossier_nonblocking_progress"]
        self.assertFalse(dossier["new_queue_retry_loop_or_scheduler_created"])
        self.assertFalse(dossier["scheduled_worker_may_edit_own_schedule"])


if __name__ == "__main__":
    unittest.main()
