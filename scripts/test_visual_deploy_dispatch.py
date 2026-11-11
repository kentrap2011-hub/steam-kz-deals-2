#!/usr/bin/env python3
"""Offline positive/negative authority and workflow-wiring regressions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from visual_deploy_dispatch import verify_dispatch_authority

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "42933371526"
ATTEMPT = "1"
REPOSITORY = "kentrap2011-hub/steam-kz-deals-2"
HEAD = "a" * 40
SCOPES = {
    "full_visual": "build",
    "giveaway_only": "giveaway_refresh",
    "commercial_only": "commercial_refresh",
}


def fixture(scope: str = "full_visual", deterministic: bool = False):
    run = {
        "id": int(RUN_ID),
        "run_attempt": int(ATTEMPT),
        "repository": {"full_name": REPOSITORY},
        "path": ".github/workflows/build-daily-visual-payload.yml@refs/heads/main",
        "head_branch": "main",
        "head_sha": HEAD,
        "event": "workflow_run",
        "status": "in_progress",  # Last dispatch job is still running.
        "conclusion": None,
    }
    jobs = {
        "total_count": 1,
        "jobs": [{
            "name": SCOPES[scope],
            "status": "completed",
            "conclusion": "success",
            "run_id": int(RUN_ID),
            "run_attempt": int(ATTEMPT),
        }],
    }
    receipt = {
        "schema_version": 1,
        "contract": "visual-freshness-receipt-v1",
        "fresh_build": not deterministic,
        "freshness_scope": scope,
        "outcome": "degraded/no_fresh_build" if deterministic else "fresh_build",
        "reason": "deterministic_refresh_preserved_semantic_history" if deterministic else None,
        "workflow_run": {
            "id": int(RUN_ID),
            "attempt": int(ATTEMPT),
            "head_sha": HEAD,
            "event": "workflow_run",
        },
    }
    if deterministic:
        receipt["observed_visual"] = {
            "blob_sha": "b" * 40,
            "commit_sha": "c" * 40,
        }
    return run, jobs, receipt


def check(run, jobs, receipt, *, run_id=RUN_ID, attempt=ATTEMPT, repository=REPOSITORY):
    return verify_dispatch_authority(
        run, jobs, receipt, run_id=run_id, attempt=attempt, repository=repository
    )


def reject(change, *, scope="full_visual", deterministic=False, expect=""):
    run, jobs, receipt = fixture(scope, deterministic)
    run_id, attempt, repository = RUN_ID, ATTEMPT, REPOSITORY
    result = change(run, jobs, receipt)
    if isinstance(result, tuple):
        run_id, attempt, repository = result
    try:
        check(run, jobs, receipt, run_id=run_id, attempt=attempt, repository=repository)
    except ValueError as exc:
        if expect and expect not in str(exc):
            raise AssertionError(f"expected {expect!r}; got {exc!r}") from exc
    else:
        raise AssertionError("untrusted visual dispatch was accepted")


def test_positive() -> None:
    for scope in SCOPES:
        run, jobs, receipt = fixture(scope)
        assert check(run, jobs, receipt) == scope
    run, jobs, receipt = fixture("full_visual", deterministic=True)
    assert check(run, jobs, receipt) == "full_visual"
    # A fully completed successful source run is also valid (manual/recovery).
    run["status"] = "completed"
    run["conclusion"] = "success"
    assert check(run, jobs, receipt) == "full_visual"


def test_negative() -> None:
    reject(lambda run, jobs, receipt: ("0", ATTEMPT, REPOSITORY), expect="run id")
    reject(lambda run, jobs, receipt: (RUN_ID, "0", REPOSITORY), expect="attempt")
    reject(lambda run, jobs, receipt: (RUN_ID, "2", REPOSITORY), expect="attempt")
    reject(lambda run, jobs, receipt: (RUN_ID, ATTEMPT, "foreign/other"), expect="repository")
    reject(lambda run, jobs, receipt: run.update(path=".github/workflows/steam-test.yml@refs/heads/main"), expect="workflow")
    reject(lambda run, jobs, receipt: run.update(head_branch="feature"), expect="main")
    reject(lambda run, jobs, receipt: run.update(event="pull_request"), expect="event")
    reject(lambda run, jobs, receipt: run.update(conclusion="failure"), expect="unsuccessfully")
    reject(lambda run, jobs, receipt: run.update(run_attempt=3), expect="attempt")
    reject(lambda run, jobs, receipt: run.update(head_sha="d" * 40), expect="receipt")
    reject(lambda run, jobs, receipt: receipt["workflow_run"].update(head_sha="e" * 40), expect="receipt")
    reject(lambda run, jobs, receipt: receipt["workflow_run"].update(id=2), expect="receipt")
    reject(lambda run, jobs, receipt: receipt["workflow_run"].update(event="push"), expect="receipt")
    reject(lambda run, jobs, receipt: receipt.update(contract="wrong"), expect="receipt")
    reject(lambda run, jobs, receipt: receipt.update(freshness_scope="untrusted"), expect="scope")
    reject(lambda run, jobs, receipt: receipt.update(fresh_build=False), expect="no validated")
    reject(lambda run, jobs, receipt: receipt.update(outcome="aborted_on_material_drift"), expect="receipt")
    reject(lambda run, jobs, receipt: jobs["jobs"][0].update(conclusion="failure"), expect="job")
    reject(lambda run, jobs, receipt: jobs["jobs"][0].update(status="in_progress"), expect="job")
    reject(lambda run, jobs, receipt: jobs["jobs"][0].update(name="scope"), expect="job")
    reject(lambda run, jobs, receipt: jobs["jobs"][0].update(run_attempt=2), expect="job")
    reject(lambda run, jobs, receipt: jobs.update(total_count=2), expect="incomplete")
    reject(lambda run, jobs, receipt: jobs.update(jobs=[]), expect="incomplete")
    reject(lambda run, jobs, receipt: receipt.pop("observed_visual"), deterministic=True, expect="no validated")
    reject(lambda run, jobs, receipt: receipt.update(reason="prerequisite_not_ready"), deterministic=True, expect="no validated")
    reject(lambda run, jobs, receipt: receipt.update(freshness_scope="giveaway_only"), deterministic=True, expect="no validated")
    reject(lambda run, jobs, receipt: jobs["jobs"][0].update(name="commercial_refresh"), scope="giveaway_only", expect="job")


def test_wiring() -> None:
    build = (ROOT / ".github/workflows/build-daily-visual-payload.yml").read_text(encoding="utf-8")
    deploy = (ROOT / ".github/workflows/deploy-visual.yml").read_text(encoding="utf-8")
    assert "  dispatch_deploy:" in build
    assert "    needs: [scope, giveaway_refresh, commercial_refresh, build]" in build
    assert "needs.scope.result == 'success'" in build
    for name in ("build", "giveaway_refresh", "commercial_refresh"):
        assert f"needs.{name}.result == 'success'" in build
    assert "github.ref == 'refs/heads/main'" in build
    assert "actions: write" in build
    assert "gh workflow run deploy-visual.yml" in build
    assert '--field visual_producer_run_id="$PRODUCER_RUN_ID"' in build
    assert '--field visual_producer_run_attempt="$PRODUCER_ATTEMPT"' in build
    assert '- "Build daily visual payload"' not in deploy
    assert '- "Build site current status"' in deploy
    assert "      - name: Validate direct dispatch input pair" in deploy
    assert "scripts/visual_deploy_dispatch.py" in deploy
    assert "scripts/visual_freshness_receipt.py verify-receipt" in deploy
    assert 'elif [ "$EVENT_NAME" = "workflow_run" ] || [ -n "$DIRECT_PRODUCER_RUN_ID" ]; then' in deploy
    assert "      - name: Deploy to GitHub Pages" in deploy


if __name__ == "__main__":
    test_positive()
    test_negative()
    test_wiring()
    print("VISUAL_DIRECT_DEPLOY_DISPATCH_TESTS=PASS")
