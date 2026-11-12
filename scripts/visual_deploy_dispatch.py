#!/usr/bin/env python3
"""Fail-closed run/receipt authority for explicit visual -> Pages dispatch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PRODUCER_WORKFLOW = ".github/workflows/build-daily-visual-payload.yml"
RECEIPT_CONTRACT = "visual-freshness-receipt-v1"
SCOPE_JOB = {
    "full_visual": "build",
    "giveaway_only": "giveaway_refresh",
    "commercial_only": "commercial_refresh",
}
DETERMINISTIC_REASON = "deterministic_refresh_preserved_semantic_history"
ALLOWED_SOURCE_EVENTS = {"workflow_run", "push", "workflow_dispatch"}


def verify_dispatch_authority(
    run: dict,
    jobs: dict,
    receipt: dict,
    *,
    run_id: str,
    attempt: str,
    repository: str,
) -> str:
    """Attest a completed producer job, not an in-progress dispatch job.

    The visual workflow is still running its final dispatch job when this
    check executes, so checking the *whole* run conclusion would race.
    The exact producer job must already have completed successfully.
    The separate visual-freshness verifier checks canonical/staged bytes.
    """
    if not run_id.isdecimal() or int(run_id) <= 0:
        raise ValueError("invalid producer run id")
    if not attempt.isdecimal() or int(attempt) <= 0:
        raise ValueError("invalid producer attempt")
    rid, att = int(run_id), int(attempt)

    if run.get("id") != rid or run.get("run_attempt") != att:
        raise ValueError("GitHub producer run id/attempt mismatch")
    if (run.get("repository") or {}).get("full_name") != repository:
        raise ValueError("foreign producer repository")
    if (run.get("path") or "").split("@", 1)[0] != PRODUCER_WORKFLOW:
        raise ValueError("incorrect producer workflow")
    if run.get("head_branch") != "main":
        raise ValueError("producer is not from main")
    if run.get("event") not in ALLOWED_SOURCE_EVENTS:
        raise ValueError("untrusted producer event")
    if run.get("conclusion") not in (None, "success"):
        raise ValueError("producer workflow finished unsuccessfully")
    head_sha = run.get("head_sha")
    if not isinstance(head_sha, str) or len(head_sha) != 40:
        raise ValueError("missing producer commit identity")

    if receipt.get("contract") != RECEIPT_CONTRACT or receipt.get("schema_version") != 1:
        raise ValueError("invalid producer freshness receipt")
    receipt_run = receipt.get("workflow_run") or {}
    if (
        receipt_run.get("id") != rid
        or receipt_run.get("attempt") != att
        or receipt_run.get("head_sha") != head_sha
        or receipt_run.get("event") != run.get("event")
    ):
        raise ValueError("freshness receipt does not belong to exact producer attempt")

    scope = receipt.get("freshness_scope")
    expected_job = SCOPE_JOB.get(scope)
    if not expected_job:
        raise ValueError("invalid visual producer scope")
    if receipt.get("fresh_build") is True:
        if receipt.get("outcome") != "fresh_build":
            raise ValueError("inconsistent fresh receipt")
    elif not (
        scope == "full_visual"
        and receipt.get("fresh_build") is False
        and receipt.get("outcome") == "degraded/no_fresh_build"
        and receipt.get("reason") == DETERMINISTIC_REASON
        and isinstance(receipt.get("observed_visual"), dict)
        and receipt["observed_visual"].get("blob_sha")
        and receipt["observed_visual"].get("commit_sha")
    ):
        raise ValueError("no validated persisted visual to dispatch")

    producer_jobs = jobs.get("jobs") if isinstance(jobs.get("jobs"), list) else jobs.get("workflow_jobs")
    if not isinstance(producer_jobs, list):
        raise ValueError("missing GitHub producer jobs")
    if jobs.get("total_count", len(producer_jobs)) > len(producer_jobs):
        raise ValueError("incomplete producer job listing")
    matching_jobs = [
        job for job in producer_jobs
        if job.get("name") == expected_job
        and job.get("status") == "completed"
        and job.get("conclusion") == "success"
        and job.get("run_id", rid) == rid
        and job.get("run_attempt", att) == att
    ]
    if len(matching_jobs) != 1:
        raise ValueError("exact successful visual producer job not confirmed")

    return scope


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-json", required=True, type=Path)
    parser.add_argument("--jobs-json", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    scope = verify_dispatch_authority(
        json.loads(args.run_json.read_text(encoding="utf-8")),
        json.loads(args.jobs_json.read_text(encoding="utf-8")),
        json.loads(args.receipt.read_text(encoding="utf-8")),
        run_id=args.run_id,
        attempt=args.attempt,
        repository=args.repository,
    )
    print(
        "VISUAL_DIRECT_DISPATCH_AUTHORITY=verified "
        f"run_id={args.run_id} attempt={args.attempt} scope={scope}"
    )


if __name__ == "__main__":
    main()
