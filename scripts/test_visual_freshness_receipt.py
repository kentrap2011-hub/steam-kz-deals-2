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
        repo / freshness.VISUAL_PATH,
        {"production_contract": {"source_history_snapshot_blob_sha": "old-history"}, "items": []},
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
            {"production_contract": {"source_history_snapshot_blob_sha": history_blob}, "items": [{"id": 1}]},
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
        assert receipt["outcome"] == "fresh_build"
        assert receipt["produced_visual"]["blob_sha"] == run(repo, "git", "rev-parse", f"HEAD:{freshness.VISUAL_PATH}")
        staged = repo / "web/data/current.json"
        staged.parent.mkdir(parents=True)
        staged.write_bytes((repo / freshness.VISUAL_PATH).read_bytes())
        assert freshness.verify_receipt(repo, receipt, expected_run_id="101", staged_path=staged) == "fresh"


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


if __name__ == "__main__":
    test_fresh_path()
    test_degraded_no_build()
    test_stale_mismatch_fails_closed()
    print("VISUAL_FRESHNESS_RECEIPT_TESTS=PASS cases=fresh,degraded,stale_mismatch")
