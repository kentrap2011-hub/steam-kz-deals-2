# WORKER TASK — TASTE POST-CANARY GUARDRAIL AUDIT STAGE 2

## Task ID
`taste-post-canary-guardrail-audit-stage2-01`

## Mode
`READ-ONLY / FINAL RUNTIME-GUARDRAIL AUDIT`

## Expected report
`reviews/worker_reports/taste-post-canary-guardrail-audit-stage2-01.md`

## Goal
Finish ALL remaining runtime/guardrail checks needed for normal daily Taste operation while the live taste profile keeps changing in parallel. If this task PASSes, no further runtime/guardrail audit stage is required.

## Mandatory execution order

### Step 1 — create durable report immediately
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC time;
- `completed_checks: 0/7`;
- next action: check 1.

Commit it immediately BEFORE reading predecessor reports or implementation files.

If you cannot create the report, stop. Do not gather evidence first.

### Step 2 — read predecessors once
Read these once unless one specific missing fact requires a reread:
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
- `reviews/worker_reports/taste-post-canary-runtime-audit-stage1-01.md`

### Step 3 — seven checks, writing after each one
After EACH check, immediately update and commit the report and increment `completed_checks` before starting the next check.

1. The current one-game preparation path freezes `gaming_taste_live.json` from an immutable current repository commit, verifies the exact bytes/blob/hash, and does not treat a stale committed projection as profile authority.
2. Parallel profile changes are handled safely: a change before freeze selects the newer state; a change after freeze cannot mix versions; continuous churn has bounded retries and fails closed rather than looping indefinitely.
3. The semantic producer/ingest path still enforces generation 2, exact tuple/binding checks, and the V5 safety fence before accepting a result.
4. Evidence sufficiency, normalized taste-factor validation, and price-blind/no-commercial-review-sentiment protections remain active for semantic results.
5. The user does not need to pause profile updates, create a quiet window, or manually freeze the profile for normal daily operation.
6. There is no unresolved runtime/guardrail blocker that would require recurring manual repair or an unbounded retry loop in normal daily operation.
7. Normal daily Taste operation does not depend on paid OpenAI API usage, GitHub Copilot, a new paid service, or an external scheduler beyond the already-approved built-in ChatGPT Scheduled Task/GitHub setup.

## Efficiency rules
- Prefer exact implementation/test files already identified by predecessor reports.
- Do not scan the whole repository unless an exact referenced path is missing.
- Do not repeatedly reopen the same file without naming the missing fact.
- Stop searching as soon as a check is proven.
- Do not inspect or modify Scheduled Tasks in this task; Stage 1 already closed that portion by manual UI verification.

## Boundaries
- read-only except this report;
- no semantic generation;
- no ingest;
- no code/config/production-data changes;
- no second game;
- no Scheduled Task changes.

## Finish
After check 7, immediately finalize the same report with:
- `completed_checks: 7/7`;
- decision: `PASS_FINAL_RUNTIME_GUARDRAIL_AUDIT` or `FAIL_FINAL_RUNTIME_GUARDRAIL_AUDIT`;
- lifecycle: `complete_final_runtime_guardrails_pass`, `complete_final_runtime_guardrails_fail`, or `blocked`;
- explicit line: `further_runtime_guardrail_audit_required: no` only if all seven checks PASS.

Then STOP.
