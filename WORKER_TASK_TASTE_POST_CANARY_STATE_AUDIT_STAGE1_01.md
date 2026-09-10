# WORKER TASK — TASTE POST-CANARY STATE AUDIT STAGE 1

## Task ID
`taste-post-canary-state-audit-stage1-01`

## Mode
`READ-ONLY / VERY SMALL CHECK`

## Expected report
`reviews/worker_reports/taste-post-canary-state-audit-stage1-01.md`

## Goal
Do only four checks. Do not attempt the rest of the system audit.

## Mandatory execution order
This order is part of the task. Do not reorder it.

### Step 1 — create durable report immediately
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC time;
- `completed_checks: 0/4`;
- next action: check 1.

Commit it immediately BEFORE reading predecessor reports or searching canonical state.

If you cannot create this report, stop and say so. Do not continue gathering evidence.

### Step 2 — read predecessor once
Read `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md` exactly once unless a specific missing fact requires rereading it.

Do not reread broad project protocols in this stage unless a blocking ambiguity appears.

### Step 3 — perform four checks sequentially
After EACH check, immediately update and commit the same report with the evidence found and increment `completed_checks` before starting the next check.

Checks:
1. `App_1016800` exists exactly once in accepted canonical Taste state.
2. `App_1016800` is absent from the pending Taste queue.
3. The accepted Chernobylite inbox submission is absent because it was consumed.
4. The ingest receipt referenced by the accepted canary report exists and records exactly one accepted result.

Do not collect all evidence first and postpone writing until the end.

## Efficiency rules
- Use one repository tree/list/search pass to locate needed paths when possible.
- Read only exact files needed for the four checks.
- Do not reopen an already-read file without naming the missing fact that requires it.
- Do not perform speculative searches after a check is already proven.
- Prefer direct file fetch over repeated find/search calls on already-loaded content.

## Boundaries
- read-only except this report;
- no Scheduled Task inspection;
- no guardrail/code audit;
- no semantic generation;
- no ingest;
- no production/config/data changes;
- no second game.

## Finish
After check 4, immediately update and commit the same report with:
- `completed_checks: 4/4`;
- one decision: `PASS_STAGE1_STATE` or `FAIL_STAGE1_STATE`;
- final lifecycle: `complete_stage1_state_pass`, `complete_stage1_state_fail`, or `blocked`.

Then STOP. Do not continue to any other audit work.
