#!/usr/bin/env python3
"""Regression coverage for Dossier marker-parent frozen authority across daily rollover."""

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import taste_steam_review_dossier_buffered as buffered
from taste_steam_review_dossier import canonical_sha256
from taste_steam_review_dossier_authority import (
    MARKER_SCHEMA,
    REFERENCE_SCHEMA,
    run_start_marker_path,
)
from taste_steam_review_dossier_buffered import drain_buffered_groups
from taste_steam_review_dossier_terminal import expected_terminal_receipt_path
from taste_steam_review_dossier_worker_projection import write_worker_projection
from taste_steam_review_dossier_web import build_daily_work_manifest_web
from test_taste_dossier_exhausted_terminal_receipt import terminal_receipt
from test_taste_steam_review_dossier_buffered_submission import (
    BASE_CONTRACT,
    buffered_artifact,
    queue,
)
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _git(repo, *args):
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {(proc.stderr or proc.stdout).strip()}")
    return proc.stdout.strip()


def _commit_all(repo, message):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


class FrozenInvocationHarness:
    def __init__(self, td):
        self.repo = Path(td) / "repo"
        self.repo.mkdir(parents=True)
        _git(self.repo, "init", "-b", "main")
        _git(self.repo, "config", "user.name", "steam-kz-bot")
        _git(self.repo, "config", "user.email", "steam-kz-bot@users.noreply.github.com")

        self.contract = copy.deepcopy(BASE_CONTRACT)
        paths = self.contract["paths"]
        paths["submission_inbox_dir"] = (self.repo / "data/ai_inbox/taste_steam_review_dossiers").as_posix()
        paths["dossier_store_dir"] = (self.repo / "data/cache/taste_steam_review_dossiers").as_posix()
        paths["work_manifest"] = (self.repo / "data/production/pre_ai/taste_steam_review_dossier_work.json").as_posix()
        paths["worker_index"] = (self.repo / "data/production/pre_ai/taste_steam_review_dossier_worker_index.json").as_posix()
        paths["worker_groups_root"] = (self.repo / "data/production/pre_ai/taste_steam_review_dossier_worker_groups").as_posix()
        paths["run_start_marker_root"] = (self.repo / "data/ai_inbox/taste_steam_review_dossiers/run_starts").as_posix()
        paths["frozen_invocation_audit"] = (self.repo / "data/audit/taste_steam_review_dossier_frozen_invocations.jsonl").as_posix()

        self.contract["worker_read_projection"]["descriptor_path_template"] = (
            paths["worker_groups_root"].rstrip("/") + "/{snapshot_id}/g{sequence:06d}.json"
        )
        self.contract["frozen_invocation_authority"]["marker_path_template"] = (
            paths["run_start_marker_root"].rstrip("/") + "/{run_start_nonce}.json"
        )
        self.contract["worker_runtime_prompt"]["path"] = (
            self.repo / "config/taste_steam_review_dossier_runtime_prompt.md"
        ).as_posix()

        (self.repo / "config").mkdir(parents=True)
        shutil.copy2(
            ROOT / "config/taste_steam_review_dossier_runtime_prompt.md",
            self.repo / "config/taste_steam_review_dossier_runtime_prompt.md",
        )
        shutil.copy2(
            ROOT / "config/taste_steam_review_dossier_persistence_bridge.json",
            self.repo / "config/taste_steam_review_dossier_persistence_bridge.json",
        )
        _write_json(
            self.repo / "config/taste_steam_review_dossier_contract.json",
            self.contract,
        )

        self.store = Path(paths["dossier_store_dir"])
        self.manifest_path = Path(paths["work_manifest"])
        self.audit_path = Path(paths["frozen_invocation_audit"])
        self.quarantine = self.repo / "data/quarantine/taste"
        self.rejection_audit = self.repo / "data/audit/rejections.jsonl"
        self.failure_audit = self.repo / "data/audit/failures.jsonl"
        self.terminal_archive = self.repo / "data/audit/terminals"
        self.now = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=2)

    def publish_snapshot(self, appids, *, day_offset=0):
        work = build_daily_work_manifest_web(
            queue(appids),
            self.contract,
            self.store,
            now=self.now + timedelta(days=day_offset),
        )
        _write_json(self.manifest_path, work)
        write_worker_projection(work, self.contract)
        return work

    def commit_snapshot(self, appids, message, *, day_offset=0):
        work = self.publish_snapshot(appids, day_offset=day_offset)
        commit = _commit_all(self.repo, message)
        return work, commit

    def marker(self, nonce="0123456789abcdef0123456789abcdef"):
        marker = run_start_marker_path(
            nonce,
            self.contract["paths"]["submission_inbox_dir"],
        )
        _write_json(marker, {
            "schema": MARKER_SCHEMA,
            "schema_version": 1,
            "run_start_nonce": nonce,
        })
        anchor = _commit_all(self.repo, "Dossier frozen invocation marker")
        return marker, anchor, nonce

    @staticmethod
    def reference(anchor, nonce):
        return {
            "schema": REFERENCE_SCHEMA,
            "schema_version": 1,
            "run_start_anchor_commit": anchor,
            "run_start_nonce": nonce,
        }

    @staticmethod
    def frozen_descriptor(work, sequence=1):
        group = copy.deepcopy(work["submission_group_plan"]["groups"][sequence - 1])
        return {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1",
            "schema_version": 1,
            "snapshot_id": work["snapshot_id"],
            "prepared_required_sha256": work["prepared_required_sha256"],
            "group_plan_sha256": work["submission_group_plan"]["group_plan_sha256"],
            "group_count": work["submission_group_plan"]["group_count"],
            "web_evidence_contract_binding": copy.deepcopy(work["web_evidence_contract_binding"]),
            **group,
        }

    def candidate(self, work, anchor, nonce, sequence=1):
        descriptor = self.frozen_descriptor(work, sequence)
        artifact = copy.deepcopy(descriptor)
        artifact["schema"] = "TASTE-STEAM-REVIEW-DOSSIER-BUFFERED-GROUP-V1"
        artifact["schema_version"] = 1
        artifact["dossiers"] = [
            web_dossier(item["appid"], self.now, title=item["title"])
            for item in descriptor["items"]
        ]
        artifact["run_start_authority"] = self.reference(anchor, nonce)
        path = Path(self.contract["paths"]["submission_inbox_dir"]) / (
            f"{descriptor['snapshot_id']}--g{int(sequence):06d}--{descriptor['group_sha256']}.json"
        )
        _write_json(path, artifact)
        return path, artifact

    def terminal(self, work, anchor, nonce, sequence=1):
        descriptor = self.frozen_descriptor(work, sequence)
        receipt = terminal_receipt(work, sequence)
        receipt["group_plan_sha256"] = descriptor["group_plan_sha256"]
        receipt["group_count"] = descriptor["group_count"]
        receipt["web_evidence_contract_binding"] = copy.deepcopy(
            descriptor["web_evidence_contract_binding"]
        )
        receipt["run_start_authority"] = self.reference(anchor, nonce)
        path = expected_terminal_receipt_path(descriptor, self.contract)
        _write_json(path, receipt)
        return path, receipt

    def drain(self):
        return drain_buffered_groups(
            manifest_path=self.manifest_path,
            contract=self.contract,
            buffer_dir=self.contract["paths"]["submission_inbox_dir"],
            store_dir=self.store,
            failed_quarantine_root=self.quarantine,
            failure_audit_path=self.failure_audit,
            retryable_rejection_root=self.quarantine,
            rejection_audit_path=self.rejection_audit,
            terminal_receipt_archive_root=self.terminal_archive,
            frozen_authority_audit_path=self.audit_path,
            repo_root=self.repo,
        )


class DossierFrozenInvocationRolloverTests(unittest.TestCase):
    def test_unrelated_main_movement_after_marker_does_not_invalidate_current_frozen_group(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, _ = h.commit_snapshot([700001, 700002, 700003], "snapshot A")
            _, anchor_commit, nonce = h.marker()
            unrelated = h.repo / "notes/unrelated.txt"
            unrelated.parent.mkdir(parents=True, exist_ok=True)
            unrelated.write_text("unrelated canonical movement\n", encoding="utf-8")
            _commit_all(h.repo, "unrelated main movement")
            h.candidate(a, anchor_commit, nonce)
            _commit_all(h.repo, "A candidate after unrelated movement")

            result = h.drain()

            self.assertEqual(result["accepted_group_count_this_run"], 1)
            self.assertEqual(result["frozen_authority_accepted_count_this_run"], 0)
            current = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["group_progress"]["groups"][0]["state"], "accepted")

    def test_runtime_contract_requires_per_item_frozen_cache_reuse_before_web_research(self):
        runtime = (ROOT / "config/taste_steam_review_dossier_runtime_prompt.md").read_text(encoding="utf-8")
        self.assertIn("before material web research for each item", runtime)
        self.assertIn("reuse a cached Dossier verbatim", runtime)
        self.assertIn("perform semantic research only for descriptor items not satisfied", runtime)
        self.assertIn("Partial overlap does not make a whole group complete", runtime)

    def test_a_to_b_rollover_persists_old_semantics_then_current_group_advances_only_from_cache(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, _ = h.commit_snapshot([710001, 710002, 710003], "snapshot A")
            _, anchor, nonce = h.marker()
            b, _ = h.commit_snapshot([710001, 710002, 710003, 710004], "snapshot B", day_offset=1)
            self.assertNotEqual(a["snapshot_id"], b["snapshot_id"])
            self.assertNotEqual(
                a["submission_group_plan"]["groups"][0]["group_sha256"],
                b["submission_group_plan"]["groups"][0]["group_sha256"],
            )

            candidate_path, _ = h.candidate(a, anchor, nonce)
            _commit_all(h.repo, "late A candidate")
            result = h.drain()

            self.assertEqual(result["frozen_authority_accepted_count_this_run"], 1)
            self.assertEqual(result["cache_reused_sequences"], [1])
            current = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["snapshot_id"], b["snapshot_id"])
            self.assertEqual(current["group_progress"]["groups"][0]["state"], "accepted")
            self.assertEqual(current["group_progress"]["groups"][1]["state"], "pending")
            self.assertFalse(candidate_path.exists())
            for appid in ("710001", "710002", "710003"):
                self.assertTrue((h.store / f"App_{appid}.json").is_file())

            audit = [json.loads(line) for line in h.audit_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(audit), 1)
            self.assertEqual(audit[0]["authority_snapshot_id"], a["snapshot_id"])
            self.assertEqual(audit[0]["current_snapshot_id_at_ingest"], b["snapshot_id"])
            self.assertEqual(audit[0]["outcome"], "dossier_candidate_accepted_after_rollover")

    def test_partial_overlap_never_rebinds_old_group_to_new_partition(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, _ = h.commit_snapshot([720001, 720002, 720003], "snapshot A")
            _, anchor, nonce = h.marker()
            b, _ = h.commit_snapshot(
                [720001, 720002, 720004, 720003, 720005, 720006],
                "snapshot B repartitioned",
                day_offset=1,
            )
            h.candidate(a, anchor, nonce)
            _commit_all(h.repo, "late A candidate")
            result = h.drain()

            self.assertEqual(result["frozen_authority_accepted_count_this_run"], 1)
            self.assertEqual(result["cache_reused_sequences"], [])
            current = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(all(x["state"] == "pending" for x in current["group_progress"]["groups"]))
            for appid in ("720001", "720002", "720003"):
                self.assertIsNotNone(
                    buffered.compatible_cached_dossier(
                        next(
                            item for item in b["prepared_required_items"]
                            if item["appid"] == appid
                        ),
                        current,
                        h.contract,
                        h.store,
                    )
                )

    def test_forged_historical_commit_is_not_a_run_start_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, authority_parent = h.commit_snapshot([730001, 730002, 730003], "snapshot A")
            _, _, nonce = h.marker()
            b, _ = h.commit_snapshot([730001, 730002, 730003, 730004], "snapshot B", day_offset=1)
            path, artifact = h.candidate(a, authority_parent, nonce)
            _write_json(path, artifact)
            _commit_all(h.repo, "forged historical authority candidate")
            result = h.drain()

            self.assertEqual(result["frozen_authority_accepted_count_this_run"], 0)
            self.assertEqual(result["frozen_authority_rejected_count_this_run"], 1)
            current = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["snapshot_id"], b["snapshot_id"])
            self.assertEqual(current["group_progress"]["groups"][0]["state"], "pending")
            self.assertFalse((h.store / "App_730001.json").exists())

    def test_binding_change_fails_closed_without_cache_or_current_progress_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, _ = h.commit_snapshot([740001, 740002, 740003], "snapshot A")
            _, anchor, nonce = h.marker()
            b, _ = h.commit_snapshot([740001, 740002, 740003, 740004], "snapshot B", day_offset=1)
            h.candidate(a, anchor, nonce)
            _commit_all(h.repo, "late A candidate")
            fake = copy.deepcopy(a["web_evidence_contract_binding"])
            fake["worker_prompt_sha256"] = "f" * 64
            with patch.object(buffered, "_current_web_evidence_binding", return_value=fake):
                result = h.drain()

            self.assertEqual(result["frozen_authority_accepted_count_this_run"], 0)
            self.assertEqual(result["frozen_authority_rejected_count_this_run"], 1)
            current = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["snapshot_id"], b["snapshot_id"])
            self.assertEqual(current["group_progress"]["groups"][0]["state"], "pending")
            self.assertFalse((h.store / "App_740001.json").exists())

    def test_consumed_replay_cannot_overwrite_newer_current_compatible_cache(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, _ = h.commit_snapshot([750001, 750002, 750003], "snapshot A")
            _, anchor, nonce = h.marker()
            h.commit_snapshot([750001, 750002, 750003, 750004], "snapshot B", day_offset=1)
            path, artifact = h.candidate(a, anchor, nonce)
            _commit_all(h.repo, "late A candidate")
            h.drain()

            newer = web_dossier("750001", h.now + timedelta(minutes=1), title="Game 750001")
            _write_json(h.store / "App_750001.json", newer)
            newer_sha = canonical_sha256(newer)
            _write_json(path, artifact)
            replay = h.drain()

            self.assertEqual(replay["frozen_authority_replay_cleanup_count_this_run"], 1)
            current_doc = json.loads((h.store / "App_750001.json").read_text(encoding="utf-8"))
            self.assertEqual(canonical_sha256(current_doc), newer_sha)
            self.assertFalse(path.exists())

    def test_frozen_terminal_after_rollover_is_audited_only_against_old_authority(self):
        with tempfile.TemporaryDirectory() as td:
            h = FrozenInvocationHarness(td)
            a, _ = h.commit_snapshot([760001, 760002, 760003], "snapshot A")
            _, anchor, nonce = h.marker()
            b, _ = h.commit_snapshot([770001, 770002, 770003], "snapshot B unrelated", day_offset=1)
            terminal_path, _ = h.terminal(a, anchor, nonce)
            _commit_all(h.repo, "late A terminal")
            result = h.drain()

            self.assertEqual(result["frozen_authority_terminal_count_this_run"], 1)
            current = json.loads(h.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["snapshot_id"], b["snapshot_id"])
            self.assertTrue(all(x["state"] == "pending" for x in current["group_progress"]["groups"]))
            self.assertFalse(terminal_path.exists())
            audit = [json.loads(line) for line in h.audit_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(audit[0]["outcome"], "semantic_exhaustion_consumed_after_rollover")
            self.assertEqual(audit[0]["authority_snapshot_id"], a["snapshot_id"])
            self.assertEqual(audit[0]["current_snapshot_id_at_ingest"], b["snapshot_id"])


if __name__ == "__main__":
    unittest.main()
