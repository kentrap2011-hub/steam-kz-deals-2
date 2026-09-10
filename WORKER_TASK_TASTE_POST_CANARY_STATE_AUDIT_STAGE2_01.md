# WORKER TASK — TASTE POST-CANARY STATE AUDIT STAGE 2

## Task ID
`taste-post-canary-state-audit-stage2-01`

## Mode
`READ-ONLY / SMALL CHECK`

## Expected report
`reviews/worker_reports/taste-post-canary-state-audit-stage2-01.md`

## Goal
Verify the saved Chernobylite result is internally consistent after Stage 1. Do only these four checks.

## Mandatory execution order

### Step 1 — create durable report immediately
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC time;
- `completed_checks: 0/4`;
- next action: check 1.

Commit it immediately BEFORE reading predecessor reports or canonical state.

If you cannot create the report, stop. Do not gather evidence first.

### Step 2 — read predecessor once
Read these once unless one specific missing fact requires a reread:
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
- `reviews/worker_reports/taste-post-canary-state-audit-stage1-01.md`

### Step 3 — four checks, writing after each one
After EACH check, immediately update and commit the report and increment `completed_checks` before starting the next check.

1. The canonical `App_1016800` result has the accepted bindings from the canary report: generation 2, model `taste-v3`, exact profile binding, semantics SHA256, fingerprint, and context SHA256.
2. The canonical cache/overlay/index/runtime references for `App_1016800` are mutually consistent: no stale alternate entry, missing index reference, or contradictory stored state.
3. There is no second or fallback canonical Taste result for Chernobylite / `App_1016800` beyond the single accepted result.
4. Current canonical state does not require manual repair for this accepted result; if any repair is required, state exactly why.

## Efficiency rules
- Locate required paths once, then fetch exact files directly.
- Do not repeatedly reopen the same file without naming the missing fact.
- Stop searching as soon as a check is proven.
- Do not inspect Scheduled Tasks or profile-freeze implementation in this stage.

## Boundaries
- read-only except this report;
- no semantic generation;
- no ingest;
- no code/config/production-data changes;
- no second game;
- no Scheduled Task changes.

## Finish
After check 4, immediately finalize the same report with:
- `completed_checks: 4/4`;
- decision: `PASS_STAGE2_STATE` or `FAIL_STAGE2_STATE`;
- lifecycle: `complete_stage2_state_pass`, `complete_stage2_state_fail`, or `blocked`.

Then STOP.
