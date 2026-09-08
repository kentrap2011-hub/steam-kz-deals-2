# WORKER TASK — TASTE CANARY EXECUTE NOW 01

## Task ID
`taste-canary-execute-now-01`

## Mode
`CONTROL-PLANE EXECUTION / ONE-GAME CANARY ONLY`

## Priority
`URGENT_BEFORE_01_00_PRODUCTION`

## Expected report
`reviews/worker_reports/taste-canary-execute-now-01.md`

## Goal
Run the already-armed one-game Taste canary NOW, before the normal 01:00 Europe/Samara production window, using the SAME active recurring Scheduled Task. Do not create another task and do not widen to backlog processing in this task.

The user explicitly wants the canary completed now so that, if it passes independent audit, the same task can be widened before 01:00 and the 01:00 run can be full production rather than the first test.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
- `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
- current Taste producer/queue/result/ingest contracts required to execute and verify this exact canary.

## Known active task
Use only this existing recurring task:
- title: `Taste Semantic Producer`
- task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- normal schedule: DAILY 01:00 Europe/Samara
- producer generation: `2`

Do not create a second Scheduled Task.
Do not delete or modify the old completed generation-1 task.

## Exact canary
The task is already bound to exactly:
- title: `Chernobylite Complete Edition`
- `taste_subject_key`: `App_1016800`
- `appid`: `1016800`
- `taste_fingerprint`: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- `candidate_context_sha256`: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`
- `profile_blob_sha`: `c42a6a5dcf608e04bf86d24be9e1542f1b934456`
- `taste_model_version`: `taste-v3`
- `taste_semantics_sha256`: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- `source_mailing_updated_at_utc`: `2026-09-07T20:45:43.377890+00:00`

No fallback candidate is authorized.

## Required sequence

### 0. Durable report first
Before any Scheduled Task mutation, create the exact report with status `in_progress`, persist it to `main`, and re-read it.

### 1. Revalidate exact canary
Confirm the exact tuple above is still current and eligible. If stale, absent, already accepted, or changed, STOP. Do not select another game.

### 2. Trigger the SAME recurring task now
Prefer a supported direct/manual `run now` mechanism if available for the exact existing task.

If no safe direct run-now capability is available, you may temporarily move the schedule of THIS SAME recurring task to the earliest safe near-term time in Europe/Samara, provided all of the following remain true:
- same immutable task id;
- task remains recurring/editable, not converted into a disposable one-time Completed task;
- no second task is created;
- canary-only prompt remains unchanged;
- after the canary execution completes or clearly starts, restore the SAME task's permanent schedule to DAILY 01:00 Europe/Samara;
- verify the restored 01:00 schedule before finishing.

Do not use a one-time replacement task.
Do not create a temporary second task.
If an immediate trigger cannot be achieved without risking task identity/recurrence, STOP with `blocked` rather than weakening containment.

### 3. Wait for/observe the canary result
Verify whether the exact one-game run:
- actually dispatched;
- produced at most one semantic result;
- used producer generation 2 identity;
- went through canonical GitHub result/ingest route;
- was accepted or rejected for a concrete reason;
- did not select any second game.

### 4. Restore permanent schedule
Before finalizing, prove the SAME task is scheduled DAILY at 01:00 Europe/Samara and remains active/recurring.

### 5. Do not widen
Even on success, do not change the canary-only prompt to backlog/full production here.
Independent System Audit must be the next step.

## Hard boundaries
- no paid OpenAI API;
- no Copilot;
- no external scheduler/service;
- no second active Taste producer;
- no new task identity;
- no backlog/mass semantic processing;
- no fallback candidate;
- old completed task untouched;
- do not weaken producer fence or semantic V5 validation.

## Required report
Persist:
`reviews/worker_reports/taste-canary-execute-now-01.md`

Include:
- exact trigger method used;
- whether schedule was temporarily changed;
- exact actual run time;
- final restored schedule proof;
- exact result/ingest outcome;
- exact accepted/rejected AppID;
- proof no second game processed;
- whether independent System Audit can start immediately;
- any containment action if failure occurred.

## Final status — exactly one
- `complete_canary_accepted_ready_for_system_audit`
- `complete_canary_rejected_needs_diagnosis`
- `blocked`

Do not widen production.
Do not start System Audit yourself.
Do not start another task.
