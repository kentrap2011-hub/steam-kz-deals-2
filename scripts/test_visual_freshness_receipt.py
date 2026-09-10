#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import visual_freshness_receipt as freshness


SOURCE = "2026-09-03T00:00:00+00:00"


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
            "source_mailing_updated_at_utc": SOURCE,
        },
    )
    write_json(
        repo / freshness.COMMERCIAL_PAYLOAD_PATH,
        {
            "source_mailing_updated_at_utc": SOURCE,
            "fx_binding": {"kzt_per_rub": 5.0},
        },
    )
    write_json(
        repo / freshness.COMMERCIAL_STORE_PATH,
        {
            "status": "complete",
            "discovery_source_updated_at_utc": SOURCE,
            "observed_at_utc": "2026-09-03T01:00:00+00:00",
            "entries": {},
        },
    )
    write_json(
        repo / freshness.COMMERCIAL_FAMILY_PATH,
        {
            "status": "complete",
            "source_updated_at_utc": SOURCE,
            "families": [],
        },
    )
    helper = repo / freshness.COMMERCIAL_HELPER_PATH
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text("# test commercial helper\n", encoding="utf-8")
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
    assert freshness._commercial_intent_ready(intent["commercial_source"])
    return repo, intent


def commercial_contract(commercial: dict) -> dict:
    return {
        contract_key: commercial[intent_key]
        for intent_key, (_, contract_key) in freshness.COMMERCIAL_BLOB_BINDINGS.items()
    }


def paid_freshness(commercial: dict) -> dict:
    return {
        "status": "published",
        "scope": freshness.COMMERCIAL_SCOPE,
        "source_mailing_updated_at_utc": commercial["source_mailing_updated_at_utc"],
        "store_observed_at_utc": commercial["store_observed_at_utc"],
        **{intent_key: commercial[intent_key] for intent_key in freshness.COMMERCIAL_BLOB_BINDINGS},
    }


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


def test_fresh_commercial_only_path_does_not_claim_full_visual_freshness() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        commercial = intent["commercial_source"]
        contract = commercial_contract(commercial)
        contract.update({
            "source_history_snapshot_blob_sha": "old-semantic-history",
            "source_giveaway_snapshot_blob_sha": "old-giveaway",
        })
        write_json(
            repo / freshness.VISUAL_PATH,
            {
                "production_contract": contract,
                "commercial_source_mailing_updated_at_utc": commercial["source_mailing_updated_at_utc"],
                "commercial_store_observed_at_utc": commercial["store_observed_at_utc"],
                "paid_list_freshness": paid_freshness(commercial),
                "giveaways": {"state": "active"},
                "items": [{"id": 1, "fit": "strong"}],
            },
        )
        commit_all(repo, "fresh commercial sibling")
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="181",
            run_attempt="1",
            event_name="push",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=False,
            persisted=True,
            history_ready=False,
            reason_override=freshness.COMMERCIAL_REASON,
        )
        assert receipt["fresh_build"] is True
        assert receipt["freshness_scope"] == freshness.COMMERCIAL_SCOPE
        assert receipt["full_visual_freshness"] is False
        assert receipt["reason"] is None
        assert receipt["produced_visual"]["commercial_source_mailing_updated_at_utc"] == SOURCE
        staged = repo / "commercial-staged.json"
        staged.write_bytes((repo / freshness.VISUAL_PATH).read_bytes())
        assert freshness.verify_receipt(repo, receipt, expected_run_id="181", staged_path=staged) == "fresh"


def test_deterministic_refresh_auto_detects_pending_semantic_queue() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, _ = make_repo(Path(td))
        write_json(
            repo / freshness.COMMERCIAL_PAYLOAD_PATH,
            {
                "source_mailing_updated_at_utc": SOURCE,
                "fx_binding": {"kzt_per_rub": 5.0},
                "status": "degraded",
                "ai_queue_count": 3,
                "complete_family_partition": True,
            },
        )
        commit_all(repo, "open semantic queue")
        intent = freshness.capture_intent(repo)
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="191",
            run_attempt="1",
            event_name="push",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=True,
            persisted=True,
            history_ready=True,
            reason_override=None,
        )
        assert receipt["fresh_build"] is False
        assert receipt["freshness_scope"] == freshness.FULL_SCOPE
        assert receipt["full_visual_freshness"] is False
        assert receipt["reason"] == freshness.DETERMINISTIC_REFRESH_REASON
        assert receipt.get("observed_visual") is None


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


def test_commercial_source_mismatch_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, intent = make_repo(Path(td))
        commercial = intent["commercial_source"]
        contract = commercial_contract(commercial)
        contract["commercial_source_store_snapshot_blob_sha"] = "wrong-store"
        write_json(
            repo / freshness.VISUAL_PATH,
            {
                "production_contract": contract,
                "commercial_source_mailing_updated_at_utc": SOURCE,
                "commercial_store_observed_at_utc": commercial["store_observed_at_utc"],
                "paid_list_freshness": paid_freshness(commercial),
                "items": [{"id": 1}],
            },
        )
        commit_all(repo, "wrong commercial visual")
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="505",
            run_attempt="1",
            event_name="push",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=False,
            persisted=True,
            history_ready=False,
            reason_override=freshness.COMMERCIAL_REASON,
        )
        assert receipt["fresh_build"] is False
        assert receipt["freshness_scope"] == freshness.COMMERCIAL_SCOPE
        assert receipt["full_visual_freshness"] is False
        assert receipt["reason"] == "visual_source_commercial_mismatch"


if __name__ == "__main__":
    test_fresh_path()
    test_fresh_giveaway_only_path_does_not_claim_full_visual_freshness()
    test_fresh_commercial_only_path_does_not_claim_full_visual_freshness()
    test_deterministic_refresh_auto_detects_pending_semantic_queue()
    test_degraded_no_build()
    test_stale_mismatch_fails_closed()
    test_giveaway_source_mismatch_fails_closed()
    test_commercial_source_mismatch_fails_closed()
    print(
        "VISUAL_FRESHNESS_RECEIPT_TESTS=PASS "
        "cases=fresh_full,fresh_giveaway,fresh_commercial,deterministic_preserved,degraded,stale_mismatch,giveaway_mismatch,commercial_mismatch"
    )
