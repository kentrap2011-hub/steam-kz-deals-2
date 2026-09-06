#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import visual_freshness_receipt as freshness


def run(repo: Path, *args: str) -> str:
    return subprocess.check_output(list(args), cwd=repo, text=True).strip()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n", encoding="utf-8")


def commit_all(repo: Path, message: str) -> str:
    subprocess.check_call(["git", "add", "-A"], cwd=repo)
    subprocess.check_call(["git", "commit", "-m", message], cwd=repo, stdout=subprocess.DEVNULL)
    return run(repo, "git", "rev-parse", "HEAD")


def make_repo(root: Path) -> tuple[Path, dict]:
    repo = root / "repo"
    repo.mkdir()
    subprocess.check_call(["git", "init", "-q", "-b", "main"], cwd=repo)
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=repo)
    subprocess.check_call(["git", "config", "user.name", "test"], cwd=repo)

    write_json(
        repo / freshness.HISTORY_PATH,
        {
            "status": "complete",
            "complete_coverage": True,
            "source_mailing_updated_at_utc": "2026-09-03T00:00:00+00:00",
        },
    )
    write_json(
        repo / freshness.GIVEAWAY_PATH,
        {
            "contract": "CROSS-PLATFORM-GIVEAWAY-V1",
            "schema_version": 1,
            "snapshot_status": "complete",
        },
    )
    write_json(
        repo / freshness.VISUAL_PATH,
        {
            "production_contract": {
                "source_history_snapshot_blob_sha": "old-history",
                "source_giveaway_snapshot_blob_sha": "old-giveaway",
            },
            "giveaways": {"state": "unavailable"},
            "items": [],
        },
    )
    commit_all(repo, "seed")
    intent = freshness.capture_intent(repo)
    return repo, intent


def test_fresh_path() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        history_blob = intent["history_snapshot_blob_sha"]
        write_json(
            repo / freshness.VISUAL_PATH,
            {
                "production_contract": {
                    "source_history_snapshot_blob_sha": history_blob,
                    "source_giveaway_snapshot_blob_sha": "old-giveaway",
                },
                "items": [{"id": 1}],
            },
        )
        commit_all(repo, "fresh visual")
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="101",
            run_attempt="1",
            event_name="workflow_run",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id="77",
            upstream_head_sha="abc123",
            build_reported=True,
            persisted=True,
            history_ready=True,
            reason_override=None,
        )
        assert receipt["fresh_build"] is True
        assert receipt["freshness_scope"] == freshness.FULL_SCOPE
        assert receipt["full_visual_freshness"] is True
        assert receipt["outcome"] == "fresh_build"
        assert receipt["produced_visual"]["blob_sha"] == run(repo, "git", "rev-parse", f"HEAD:{freshness.VISUAL_PATH}")
        staged = repo / "web/data/current.json"
        staged.parent.mkdir(parents=True)
        staged.write_bytes((repo / freshness.VISUAL_PATH).read_bytes())
        assert freshness.verify_receipt(repo, receipt, expected_run_id="101", staged_path=staged) == "fresh"


def test_fresh_giveaway_only_path_does_not_claim_full_visual_freshness() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        giveaway_blob = intent["giveaway_snapshot_blob_sha"]
        write_json(
            repo / freshness.VISUAL_PATH,
            {
                "production_contract": {
                    "source_history_snapshot_blob_sha": "old-history",
                    "source_giveaway_snapshot_blob_sha": giveaway_blob,
                },
                "giveaways": {
                    "state": "active",
                    "generated_at_utc": "2026-09-05T20:45:35Z",
                    "fresh_until_utc": "2026-09-07T02:45:35Z",
                },
                "items": [{"id": 1}],
            },
        )
        commit_all(repo, "fresh giveaway sibling")
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="151",
            run_attempt="1",
            event_name="push",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=False,
            persisted=True,
            history_ready=False,
            reason_override=freshness.GIVEAWAY_REASON,
        )
        assert receipt["fresh_build"] is True
        assert receipt["freshness_scope"] == freshness.GIVEAWAY_SCOPE
        assert receipt["full_visual_freshness"] is False
        assert receipt["reason"] is None
        assert receipt["produced_visual"]["source_giveaway_snapshot_blob_sha"] == giveaway_blob
        staged = repo / "staged.json"
        staged.write_bytes((repo / freshness.VISUAL_PATH).read_bytes())
        assert freshness.verify_receipt(repo, receipt, expected_run_id="151", staged_path=staged) == "fresh"


def test_degraded_no_build() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="202",
            run_attempt="1",
            event_name="workflow_run",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=False,
            persisted=False,
            history_ready=False,
            reason_override=None,
        )
        assert receipt["fresh_build"] is False
        assert receipt["outcome"] == "degraded/no_fresh_build"
        assert receipt["reason"] == "prerequisite_not_ready"
        assert receipt["produced_visual"] is None
        staged = repo / "staged.json"
        staged.write_bytes((repo / freshness.VISUAL_PATH).read_bytes())
        assert freshness.verify_receipt(repo, receipt, expected_run_id="202", staged_path=staged) == "degraded/no_fresh_build"


def test_stale_mismatch_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        history_blob = intent["history_snapshot_blob_sha"]
        write_json(
            repo / freshness.VISUAL_PATH,
            {"production_contract": {"source_history_snapshot_blob_sha": history_blob}, "items": [{"id": 1}]},
        )
        commit_all(repo, "fresh visual")
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="303",
            run_attempt="1",
            event_name="workflow_run",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=True,
            persisted=True,
            history_ready=True,
            reason_override=None,
        )

        write_json(
            repo / freshness.VISUAL_PATH,
            {"production_contract": {"source_history_snapshot_blob_sha": "older-history"}, "items": [{"id": 0}]},
        )
        commit_all(repo, "stale replacement")
        staged = repo / "staged.json"
        staged.write_bytes((repo / freshness.VISUAL_PATH).read_bytes())
        try:
            freshness.verify_receipt(repo, receipt, expected_run_id="303", staged_path=staged)
        except SystemExit as exc:
            assert "stale visual blob mismatch" in str(exc) or "visual commit mismatch" in str(exc)
        else:
            raise AssertionError("stale mismatch was accepted")


def test_giveaway_source_mismatch_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        write_json(
            repo / freshness.VISUAL_PATH,
            {
                "production_contract": {
                    "source_history_snapshot_blob_sha": "old-history",
                    "source_giveaway_snapshot_blob_sha": "wrong-giveaway",
                },
                "items": [{"id": 1}],
            },
        )
        commit_all(repo, "wrong giveaway visual")
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="404",
            run_attempt="1",
            event_name="push",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=False,
            persisted=True,
            history_ready=False,
            reason_override=freshness.GIVEAWAY_REASON,
        )
        assert receipt["fresh_build"] is False
        assert receipt["freshness_scope"] == freshness.GIVEAWAY_SCOPE
        assert receipt["reason"] == "visual_source_giveaway_mismatch"


if __name__ == "__main__":
    test_fresh_path()
    test_fresh_giveaway_only_path_does_not_claim_full_visual_freshness()
    test_degraded_no_build()
    test_stale_mismatch_fails_closed()
    test_giveaway_source_mismatch_fails_closed()
    print("VISUAL_FRESHNESS_RECEIPT_TESTS=PASS cases=fresh_full,fresh_giveaway,degraded,stale_mismatch,giveaway_mismatch")
