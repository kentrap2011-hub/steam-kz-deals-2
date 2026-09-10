# WORKER TASK — TASTE POST-CANARY STATE AUDIT STAGE 2

## Task ID
`taste-post-canary-state-audit-stage2-01`

## Mode
`READ-ONLY / FINAL STATE-SIDE AUDIT`

## Expected report
`reviews/worker_reports/taste-post-canary-state-audit-stage2-01.md`

## Goal
Finish ALL remaining state-side post-canary checks for Chernobylite. If this task PASSes, no further state-side audit stage is required.

## Mandatory execution order

### Step 1 — create durable report immediately
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC time;
- `completed_checks: 0/5`;
- next action: check 1.

Commit it immediately BEFORE reading predecessor reports or canonical state.

If you cannot create the report, stop. Do not gather evidence first.

### Step 2 — read predecessors once
Read these once unless one specific missing fact requires a reread:
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
- `reviews/worker_reports/taste-post-canary-state-audit-stage1-01.md`

### Step 3 — five checks, writing after each one
After EACH check, immediately update and commit the report and increment `completed_checks` before starting the next check.

1. The canonical `App_1016800` result has the accepted bindings from the canary report: generation 2, model `taste-v3`, exact profile binding, semantics SHA256, fingerprint, and context SHA256.
2. The canonical cache/overlay/index/runtime references for `App_1016800` are mutually consistent: no stale alternate entry, missing index reference, or contradictory stored state.
3. There is no second or fallback canonical Taste result for Chernobylite / `App_1016800` beyond the single accepted result.
4. Current canonical state does not require manual repair for this accepted result; if any repair is required, state exactly why.
5. There is no unresolved STATE-SIDE blocker that would prevent normal daily Taste operation after the accepted Chernobylite result. Base this only on canonical state evidence; do not inspect Scheduled Tasks or implementation guardrails here.

## Efficiency rules
- Locate required paths once, then fetch exact files directly.
- Do not repeatedly reopen the same file without naming the missing fact.
- Stop searching as soon as a check is proven.
- Do not inspect Scheduled Tasks or profile-freeze implementation in this task.

## Boundaries
- read-only except this report;
- no semantic generation;
- no ingest;
- no code/config/production-data changes;
- no second game;
- no Scheduled Task changes.

## Finish
After check 5, immediately finalize the same report with:
- `completed_checks: 5/5`;
- decision: `PASS_FINAL_STATE_AUDIT` or `FAIL_FINAL_STATE_AUDIT`;
- lifecycle: `complete_final_state_pass`, `complete_final_state_fail`, or `blocked`;
- explicit line: `further_state_audit_required: no` only if all five checks PASS.

Then STOP.
