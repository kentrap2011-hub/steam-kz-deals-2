# WORKER TASK — TASTE POST-CANARY RUNTIME AUDIT STAGE 1

## Task ID
`taste-post-canary-runtime-audit-stage1-01`

## Mode
`READ-ONLY / VERY SMALL CHECK`

## Expected report
`reviews/worker_reports/taste-post-canary-runtime-audit-stage1-01.md`

## Goal
Do only four runtime checks. Do not attempt the rest of the system audit.

## Mandatory execution order
This order is part of the task. Do not reorder it.

### Step 1 — create durable report immediately
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC time;
- `completed_checks: 0/4`;
- next action: check 1.

Commit it immediately BEFORE reading predecessor reports or inspecting Scheduled Task state.

If you cannot create this report, stop and say so. Do not continue gathering evidence.

### Step 2 — read predecessor once
Read `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md` exactly once unless a specific missing fact requires rereading it.

Do not reread broad project protocols in this stage unless a blocking ambiguity appears.

### Step 3 — perform four checks sequentially
After EACH check, immediately update and commit the same report with the evidence found and increment `completed_checks` before starting the next check.

Checks:
1. Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9` still exists.
2. It is enabled.
3. Its permanent schedule is DAILY 01:00 Europe/Samara.
4. No second Scheduled Task exists for the same Taste semantic producer role.

Do not collect all evidence first and postpone writing until the end.

## Efficiency rules
- Inspect the exact Scheduled Task state directly when possible.
- Avoid repeated reads of the same predecessor/task state.
- Do not perform unrelated repository searches.
- Stop searching once a check is proven.

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
After check 4, immediately update and commit the same report with:
- `completed_checks: 4/4`;
- one decision: `PASS_STAGE1_RUNTIME` or `FAIL_STAGE1_RUNTIME`;
- final lifecycle: `complete_stage1_runtime_pass`, `complete_stage1_runtime_fail`, or `blocked`.

Then STOP. Do not continue to any other audit work.
