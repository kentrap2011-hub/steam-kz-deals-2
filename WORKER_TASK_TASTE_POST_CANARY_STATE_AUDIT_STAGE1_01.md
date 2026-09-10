# WORKER TASK — TASTE POST-CANARY STATE AUDIT STAGE 1

## Task ID
`taste-post-canary-state-audit-stage1-01`

## Mode
`READ-ONLY / VERY SMALL CHECK`

## Expected report
`reviews/worker_reports/taste-post-canary-state-audit-stage1-01.md`

## Goal
Do only four checks. Do not attempt the rest of the system audit.

## First action — mandatory
Before reading anything else, create the report above with:
- lifecycle: `in_progress`
- current UTC time
- next action
Commit it immediately.

## Read only
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
- only the exact current canonical Taste files needed for the four checks below.

Do not reread broad project protocols in this stage unless a blocking ambiguity appears.

## Four checks only
1. `App_1016800` exists exactly once in accepted canonical Taste state.
2. `App_1016800` is absent from the pending Taste queue.
3. The accepted Chernobylite inbox submission is absent because it was consumed.
4. The ingest receipt referenced by the accepted canary report exists and records exactly one accepted result.

## Boundaries
- read-only except this report;
- no Scheduled Task inspection;
- no guardrail/code audit;
- no semantic generation;
- no ingest;
- no production/config/data changes;
- no second game.

## Finish
Update the same report with exact evidence for all four checks and one decision:
- `PASS_STAGE1_STATE`
- `FAIL_STAGE1_STATE`

Final lifecycle:
- `complete_stage1_state_pass`
- `complete_stage1_state_fail`
- `blocked`

Stop immediately after writing the final report. Do not continue to any other audit work.
