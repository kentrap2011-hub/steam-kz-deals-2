# WORKER TASK — TASTE POST-CANARY RUNTIME AUDIT STAGE 1

## Task ID
`taste-post-canary-runtime-audit-stage1-01`

## Mode
`READ-ONLY / VERY SMALL CHECK`

## Expected report
`reviews/worker_reports/taste-post-canary-runtime-audit-stage1-01.md`

## Goal
Do only four runtime checks. Do not attempt the rest of the system audit.

## First action — mandatory
Before reading anything else, create the report above with:
- lifecycle: `in_progress`
- current UTC time
- next action
Commit it immediately.

## Read only
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
- only the exact current Scheduled Task / producer state needed for the four checks below.

Do not reread broad project protocols in this stage unless a blocking ambiguity appears.

## Four checks only
1. Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9` still exists.
2. It is enabled.
3. Its permanent schedule is DAILY 01:00 Europe/Samara.
4. No second Scheduled Task exists for the same Taste semantic producer role.

## Boundaries
- read-only except this report;
- no profile-freeze audit;
- no guardrail/code audit;
- do not modify or trigger any Scheduled Task;
- no semantic generation;
- no ingest;
- no production/config/data changes;
- no second game.

## Finish
Update the same report with exact evidence for all four checks and one decision:
- `PASS_STAGE1_RUNTIME`
- `FAIL_STAGE1_RUNTIME`

Final lifecycle:
- `complete_stage1_runtime_pass`
- `complete_stage1_runtime_fail`
- `blocked`

Stop immediately after writing the final report. Do not continue to any other audit work.
