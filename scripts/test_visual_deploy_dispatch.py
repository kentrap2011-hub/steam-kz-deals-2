#!/usr/bin/env python3
"""Offline positive/negative authority and workflow-wiring regressions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

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


def test_direct_dispatch_main_ref_guard() -> None:
    """Exercise the exact bash guard, including legacy inputless manual use."""
    deploy = (ROOT / ".github/workflows/deploy-visual.yml").read_text(encoding="utf-8")
    section = deploy.split("      - name: Validate direct dispatch input pair\n", 1)[1]
    section = section.split("\n      - name: ", 1)[0]
    script = section.split("        run: |\n", 1)[1]
    script = "\n".join(line.removeprefix("          ") for line in script.splitlines())

    def run(ref: str, run_id: str, attempt: str) -> int:
        env = dict(os.environ, GITHUB_REF=ref, PRODUCER_RUN_ID=run_id, PRODUCER_ATTEMPT=attempt)
        result = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
        return result.returncode

    assert run("refs/heads/main", RUN_ID, ATTEMPT) == 0
    assert run("refs/heads/feature", RUN_ID, ATTEMPT) != 0
    assert run("refs/heads/main", "", "") == 0
    assert run("refs/heads/feature", "", "") == 0  # Existing manual entrypoint.
    assert run("refs/heads/main", RUN_ID, "") != 0
    assert run("refs/heads/main", "", ATTEMPT) != 0


def test_commercial_receipt_on_direct_dispatch() -> None:
    """Run the deploy workflow's *actual* embedded classifier against a tiny Git history."""
    deploy = (ROOT / ".github/workflows/deploy-visual.yml").read_text(encoding="utf-8")
    section = deploy.split("          python - <<'PY' | tee /tmp/visual-scope.txt\n", 1)[1]
    section = section.split("\n          PY\n", 1)[0]
    code = "\n".join(line.removeprefix("          ") for line in section.splitlines())
    receipt_literal = "'/tmp/visual-freshness-artifact/visual-freshness-receipt.json'"
    assert receipt_literal in code

    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        visual_path = temp / "data/production/visual/current.json"
        visual_path.parent.mkdir(parents=True)
        def git(*args: str) -> str:
            return subprocess.check_output(["git", *args], cwd=temp, text=True).strip()

        git("init", "-q")
        git("config", "user.email", "qa@example.invalid")
        git("config", "user.name", "QA fixture")
        visual = {
            "items": [{"id": "game:1", "summary": "Unchanged grounded description", "price": 100}],
            "giveaways": {"schema_version": 1, "source_contract": "CROSS-PLATFORM-GIVEAWAY-V1"},
            "paid_list_freshness": {"status": "published", "scope": "commercial_only"},
            "production_contract": {},
        }
        def commit_visual(message: str) -> str:
            visual_path.write_text(json.dumps(visual), encoding="utf-8")
            git("add", "data/production/visual/current.json")
            git("commit", "-qm", message)
            return git("rev-parse", "HEAD")

        commit_visual("fixture base")
        visual["items"][0]["price"] = 70
        commit_sha = commit_visual("fixture price-only refresh")
        receipt_path = temp / "receipt.json"
        receipt_path.write_text(json.dumps({
            "fresh_build": True,
            "freshness_scope": "commercial_only",
            "full_visual_freshness": False,
            "produced_visual": {"commit_sha": commit_sha},
        }), encoding="utf-8")
        test_code = code.replace(receipt_literal, repr(str(receipt_path)))

        def classify(event: str, producer_id: str = "", trigger: str = "") -> str:
            env = dict(
                os.environ, EVENT_NAME=event, DIRECT_PRODUCER_RUN_ID=producer_id,
                TRIGGER_WORKFLOW=trigger, BEFORE_SHA="", AFTER_SHA="",
            )
            result = subprocess.run(
                [sys.executable, "-c", test_code], cwd=temp, env=env,
                check=True, capture_output=True, text=True,
            )
            return result.stdout

        assert "VISUAL_DEPLOY_SCOPE=commercial_only" in classify("workflow_dispatch", RUN_ID)
        assert "VISUAL_DEPLOY_SCOPE=general" in classify("workflow_dispatch")
        assert "VISUAL_DEPLOY_SCOPE=general" in classify("push")
        assert "VISUAL_DEPLOY_SCOPE=status_only" in classify(
            "workflow_run", trigger="Build site current status"
        )


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
    assert "inputs.visual_producer_run_id == '' ||" in deploy
    assert "github.ref == 'refs/heads/main'" in deploy
    assert 'if [ -n "$PRODUCER_RUN_ID" ] && [ "$GITHUB_REF" != "refs/heads/main" ]; then' in deploy
    assert "DIRECT_PRODUCER_RUN_ID: ${{ inputs.visual_producer_run_id }}" in deploy
    assert "os.environ.get('EVENT_NAME') == 'workflow_dispatch'" in deploy
    assert "scripts/visual_deploy_dispatch.py" in deploy
    assert "scripts/visual_freshness_receipt.py verify-receipt" in deploy
    assert 'elif [ "$EVENT_NAME" = "workflow_run" ] || [ -n "$DIRECT_PRODUCER_RUN_ID" ]; then' in deploy
    assert "      - name: Deploy to GitHub Pages" in deploy


if __name__ == "__main__":
    test_positive()
    test_negative()
    test_wiring()
    test_direct_dispatch_main_ref_guard()
    test_commercial_receipt_on_direct_dispatch()
    print("VISUAL_DIRECT_DEPLOY_DISPATCH_TESTS=PASS")
