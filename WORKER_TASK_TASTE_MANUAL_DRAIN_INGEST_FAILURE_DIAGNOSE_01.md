# WORKER TASK — DIAGNOSE TASTE MANUAL DRAIN INGEST FAILURE

## Task ID
`taste-manual-drain-ingest-failure-diagnose-01`

## Mode
`DIAGNOSIS ONLY / READ-ONLY EXCEPT REPORT`

## Expected report
`reviews/worker_reports/taste-manual-drain-ingest-failure-diagnose-01.md`

## Goal
Determine exactly why canonical ingest failed for the already-produced 10-result submission from `taste-manual-throughput-drain-01`, and whether those exact results can be safely accepted later without regenerating them.

## Known failed run
From predecessor report:
- inbox submission: `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`
- submission commit: `f138d5216248c999fde588c47ca5088ff9c076ee`
- ingest run id: `102798215077`
- conclusion: `failure`
- queue remained 566
- submission still present
- no canonical ingest commit/receipt created

## Mandatory execution order
1. Create the expected report FIRST with lifecycle `in_progress` and commit it.
2. Read predecessor report once: `reviews/worker_reports/taste-manual-throughput-drain-01.md`.
3. Inspect the exact failed GitHub Actions run/job/steps/logs for run `102798215077` using available GitHub tooling.
4. Identify the first real failure, not downstream cascade errors.
5. Determine whether the existing 10-result inbox submission is:
   - `safe_to_retry_unchanged`,
   - `safe_after_nonsemantic_repair`,
   - `must_regenerate_semantic_results`, or
   - `invalid_do_not_retry`.
6. State the smallest next action needed.

## What to report
Include:
- exact failing step;
- exact error message / failed invariant;
- root cause in plain terms;
- whether any of the 10 semantic results themselves are invalid;
- whether profile/model/semantics/fingerprint/context bindings remain valid;
- whether the inbox file should remain untouched until repair;
- whether queue state remains safe;
- whether Scheduled Task was unaffected;
- recommended next step.

## Boundaries
- Diagnosis only.
- Do not edit/delete the inbox submission.
- Do not rerun ingest.
- Do not regenerate semantic results.
- Do not modify queue/cache/config/code/workflows/Scheduled Task.
- Do not start batch 2.
- Only the durable diagnosis report may be created/updated.

## Finish
Use one final status:
- `complete_root_cause_found_safe_to_retry_unchanged`
- `complete_root_cause_found_needs_nonsemantic_repair`
- `complete_root_cause_found_requires_regeneration`
- `blocked_insufficient_failure_evidence`

Then STOP.
