# WORKER TASK — ENABLE TASTE NORMAL DAILY OPERATION

## Task ID
`taste-normal-daily-operation-enable-01`

## Mode
`IMPLEMENT / BOUNDED PRODUCTION TRANSITION`

## Expected report
`reviews/worker_reports/taste-normal-daily-operation-enable-01.md`

## User authorization
The user explicitly approved transition from the completed one-game canary/audit state to normal daily Taste operation.

This authorizes only the minimum changes required to move the EXISTING Taste Scheduled Task from the consumed Chernobylite-specific canary binding to the already-designed normal daily production behavior.

It does NOT authorize a new Scheduled Task, a second producer, paid API/service use, a backlog-wide immediate run, weakened guards, or unrelated code changes.

## Goal
Make the existing Taste automation ready for ordinary daily operation while preserving all protections proven by the final audit.

## Mandatory execution order

### Step 1 — create durable report first
After reading this task file, the FIRST repository mutation must be creation of the report above with:
- lifecycle: `in_progress`;
- current UTC;
- transition status: `not_started`;
- next action: read predecessor evidence and current production contract.

Commit immediately. If report creation fails, STOP.

### Step 2 — read only the minimum predecessor evidence
Read once unless one named missing fact requires a reread:
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
- `reviews/worker_reports/taste-post-canary-state-audit-stage2-01.md`
- `reviews/worker_reports/taste-post-canary-guardrail-audit-stage2-01.md`

Then inspect only the exact current production ownership/contract/config/task-binding files needed to determine the already-defined normal daily producer behavior. Do not invent a new production policy.

If the repository does NOT define the exact normal daily producer scope well enough to safely replace the canary binding, record `blocked_missing_production_definition` and STOP without changing the Scheduled Task.

### Step 3 — inspect the existing Scheduled Task before change
Target task:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`

Confirm before mutation, using the Scheduled Tasks/Automations tool if available:
- this exact task exists;
- it is enabled;
- it remains the single Taste semantic producer;
- permanent schedule remains DAILY 01:00 Europe/Samara;
- current prompt/binding is still the consumed Chernobylite canary form or otherwise not yet normal-daily production form.

Immediately checkpoint these findings in the report before changing anything.

If tool output becomes unavailable due context compaction, do not guess. Record `blocked_runtime_readback` and STOP without mutation.

### Step 4 — perform the minimum transition
Update ONLY the existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` as needed to use the repository-defined normal daily Taste production behavior.

Required invariants:
- keep the same task ID;
- keep it enabled;
- keep DAILY 01:00 Europe/Samara;
- keep producer generation 2;
- keep V5/result-contract enforcement;
- keep exact current-live-profile freeze/binding behavior;
- keep bounded retry/fail-closed behavior;
- keep evidence sufficiency and normalized-factor checks;
- keep price-blind / no commercial input / no review-sentiment-as-fit evidence rules;
- no user quiet window or profile pause requirement;
- no new paid OpenAI API, Copilot, paid service, or external scheduler;
- no new Scheduled Task;
- do not trigger or run the task now;
- do not process Chernobylite again merely because of this transition;
- do not widen or drain the backlog immediately.

If normal daily behavior has an existing bounded per-run scope in repository contracts, preserve it exactly. Do not increase that scope.

Immediately checkpoint the exact mutation in the report.

### Step 5 — post-change readback
Read back the SAME existing Scheduled Task and verify:
- same ID;
- enabled;
- DAILY 01:00 Europe/Samara;
- normal daily production prompt/binding is active rather than the consumed canary binding;
- no second Taste producer task exists;
- no immediate run was launched.

Checkpoint each result immediately.

If readback tool output is compacted/unavailable after a successful mutation, record exactly that. Do not make a second mutation just to retry.

## Boundaries
Allowed:
- durable report commits;
- minimum update to the existing Scheduled Task required for the production transition.

Not allowed:
- semantic execution now;
- ingest now;
- second game/result now;
- creating another Scheduled Task;
- changing permanent schedule;
- production-data repair;
- unrelated code/config changes;
- weakening any guardrail;
- paid/external services.

## Finish
Final report must state one of:
- `complete_normal_daily_operation_enabled`
- `blocked_missing_production_definition`
- `blocked_runtime_readback`
- `needs_followup`

If complete, explicitly state:
- exact task ID retained;
- schedule retained;
- no immediate execution occurred;
- no second task created;
- canary-specific binding removed/replaced by the already-defined normal daily behavior;
- all audited safety invariants preserved;
- ready for independent acceptance verification.

Then STOP.
