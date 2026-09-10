# WORKER TASK — TASTE POST-CANARY GUARDRAIL AUDIT STAGE 2

## Task ID
`taste-post-canary-guardrail-audit-stage2-01`

## Mode
`READ-ONLY / SMALL CHECK`

## Expected report
`reviews/worker_reports/taste-post-canary-guardrail-audit-stage2-01.md`

## Goal
Verify the protections needed for safe operation while the live taste profile continues changing in parallel. Do only these four checks.

## Mandatory execution order

### Step 1 — create durable report immediately
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC time;
- `completed_checks: 0/4`;
- next action: check 1.

Commit it immediately BEFORE reading predecessor reports or implementation files.

If you cannot create the report, stop. Do not gather evidence first.

### Step 2 — read predecessor once
Read these once unless one specific missing fact requires a reread:
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`

### Step 3 — four checks, writing after each one
After EACH check, immediately update and commit the report and increment `completed_checks` before starting the next check.

1. The current one-game preparation path freezes `gaming_taste_live.json` from an immutable current repository commit, verifies the exact bytes/blob/hash, and does not treat a stale committed projection as profile authority.
2. Parallel profile changes are handled safely: a change before freeze selects the newer state; a change after freeze cannot mix versions; continuous churn has bounded retries and fails closed rather than looping indefinitely.
3. The semantic producer/ingest path still enforces generation 2, exact tuple/binding checks, and the V5 safety fence before accepting a result.
4. Evidence sufficiency, normalized taste-factor validation, and price-blind/no-commercial-review-sentiment protections remain active for semantic results.

## Efficiency rules
- Prefer exact implementation/test files already identified by predecessor reports.
- Do not scan the whole repository unless an exact referenced path is missing.
- Do not repeatedly reopen the same file without naming the missing fact.
- Stop searching as soon as a check is proven.
- Do not inspect or modify Scheduled Tasks in this stage.

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
- decision: `PASS_STAGE2_GUARDRAILS` or `FAIL_STAGE2_GUARDRAILS`;
- lifecycle: `complete_stage2_guardrails_pass`, `complete_stage2_guardrails_fail`, or `blocked`.

Then STOP.
