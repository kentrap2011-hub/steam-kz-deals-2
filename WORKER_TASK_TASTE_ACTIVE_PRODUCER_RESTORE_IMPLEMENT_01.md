# WORKER TASK — TASTE ACTIVE PRODUCER RESTORE IMPLEMENT 01

## Task ID
`taste-active-producer-restore-implement-01`

## Mode
`IMPLEMENT / CONTROL-PLANE + CONTRACT MIGRATION + CANARY ARMING`

## Priority
`VERY_HIGH_TASTE_RECOVERY`

## Expected report
`reviews/worker_reports/taste-active-producer-restore-implement-01.md`

## Preconditions
Read first:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
- `reviews/worker_reports/taste-active-producer-restore-design-01.md`
- `config/taste_result_contract.json`
- `config/daily_execution_contract.json`
- `config/execution_ownership_contract.json`
- current Taste queue/manifest/binding artifacts required to select one fresh canary.

The design report with final status `complete_restore_plan_ready` is authoritative.

## Goal
Restore exactly one ACTIVE recurring ChatGPT Scheduled `Taste Semantic Producer`, migrate its producer identity to generation `2`, and arm exactly one fresh current-game canary while keeping the SAME recurring task active for later widening after System Audit.

This task may create exactly one new Scheduled Task and make the minimal repository identity migration required by the accepted design. It must NOT widen to normal backlog processing.

## Known old producer
- title: `Taste Semantic Producer`
- old jawbone/task id: `6a9d6fdddc00819193ed670d782045c4`
- old producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
- old generation: `1`
- old UI state: `Completed`
- user-established Active filter state before this task: empty.

Do not delete or modify the old completed task.

## Required mutation sequence
Follow this order and fail closed.

### 0. Durable report first
Before expensive work or any control-plane mutation, create:
`reviews/worker_reports/taste-active-producer-restore-implement-01.md`
with status `in_progress`, commit it to `main`, and re-read it.

### 1. Control-plane preflight
- Re-check Scheduled Tasks immediately before creation.
- Prove there are zero active Taste producers.
- Confirm the old `Taste Semantic Producer` is still Completed/inactive if visible.
- If active Taste producer count is not exactly zero, STOP with `blocked` and do not create another task.

### 2. Select exactly one fresh current canary
From current canonical completed GitHub-prepared Taste data, select exactly one row that genuinely requires a fresh full Taste evaluation.

Record exact canary bindings before task creation:
- `taste_subject_key`
- `appid`
- `taste_fingerprint`
- `candidate_context_sha256`
- `profile_blob_sha`
- `taste_model_version`
- `taste_semantics_sha256`
- `source_mailing_updated_at_utc`

Requirements:
- current under the current manifest/projection;
- no reuse of old Prototype/App_10150 result;
- maximum one result;
- no fallback/next candidate if this row becomes invalid.

Do NOT semantically analyze the game in the worker chat itself.

### 3. Choose safe first recurring execution
Normal canonical schedule is:
- DAILY
- 01:00
- Europe/Samara

Create the recurring task only with a first execution far enough in the future to finish task-id capture, GitHub generation-2 migration, validation, and final singleton proof before the first run.

If the next 01:00 leaves insufficient staging time, use the following day's 01:00. Do not invent a different permanent daily time merely for convenience.

### 4. Create exactly one new recurring Scheduled Task
Create exactly one new recurring task serving the `Taste Semantic Producer` role.

The SAME task must be suitable for:
- first singleton canary;
- post-canary no-op hold period;
- later normal daily production after independent System Audit and a separately authorized widening task.

Do NOT create a disposable one-time canary task.

Creation instructions must bind the task to exactly the selected canary tuple and require:
- maximum one semantic result;
- no fallback candidate;
- no automatic widening;
- if exact tuple is stale/not current/already accepted, no-op;
- after successful canary ingest, subsequent scheduled invocations under the same canary prompt no-op instead of selecting another game;
- submission only through the existing canonical GitHub Taste result route;
- producer fields must use the NEW task identity and generation `2` once captured.

If creation result is ambiguous, DO NOT retry creation blindly. Re-read Scheduled/Active state. If exact new identity cannot be established safely, stop fail-closed without creating another task.

### 5. Capture immutable new task id and define generation 2
After successful creation, capture exact `<NEW_TASK_ID>`.

Canonical new identity becomes:
`chatgpt_scheduled_task:<NEW_TASK_ID>`

Generation becomes:
`2`

Do not reuse generation `1` for a new immutable task.

### 6. Configure/confirm the SAME task canary contract
Ensure the exact newly created task's instructions contain:
- the exact selected canary tuple;
- `producer_id = chatgpt_scheduled_task:<NEW_TASK_ID>`;
- `producer_generation = 2`;
- max one result;
- no fallback candidate;
- no-op after current tuple is no longer eligible/already accepted;
- recurring daily 01:00 Europe/Samara schedule remains intact.

If product behavior requires an edit after creation to insert the returned immutable id, edit ONLY that same new task. Do not create a second task.

### 7. Migrate canonical GitHub producer fence
Change only the canonical active producer identity fields in:
`config/taste_result_contract.json`

Set:
- `producer_fence.active_producer_id = "chatgpt_scheduled_task:<NEW_TASK_ID>"`
- `producer_fence.active_producer_generation = 2`

Keep unchanged:
- `producer_fence.transport_fields`
- `producer_fence.missing_legacy_or_mismatch_policy = "reject_before_ingest"`
- semantic contract `TASTE-SEMANTIC-RESULT-V5`

Do not rewrite historical reports/tasks to generation 2.
Do not weaken producer fencing.

### 8. Validate before first scheduled run
Prove all of the following:
- new id + generation 2 accepted by producer fence;
- old id + generation 1 rejected before ingest;
- wrong id rejected;
- wrong/missing generation rejected;
- V5 semantic contract unchanged;
- current queue/binding validation still passes;
- exactly one active Taste Scheduled Task exists;
- that active task is `<NEW_TASK_ID>`;
- old task remains Completed/inactive;
- new task remains canary-bounded and recurring.

If any check fails before first run:
- pause/disable the new task if needed to prevent execution;
- do not create a replacement task;
- do not roll producer generation backward to 1;
- preserve fail-closed zero-active state if necessary;
- report `blocked` or `needs_followup_fix` truthfully.

### 9. Do NOT widen
This IMPLEMENT task ends with the generation-2 recurring producer safely armed for exactly one fresh canary.

Do not:
- process the full backlog;
- widen instructions to normal production;
- create the System Audit task itself unless the task protocol specifically requires only naming it in the report;
- delete the old completed task.

If the first scheduled canary happens naturally before this worker finishes and is accepted, record that fact, but still do not widen. Independent System Audit remains mandatory.

## Cost / ownership hard boundaries
- No paid OpenAI API.
- No Copilot automation dependency.
- No external paid scheduler/service.
- ChatGPT Scheduled + GitHub only.
- GitHub remains control plane / validator / persistence owner.
- Scheduled ChatGPT remains constrained semantic producer only.
- No GitHub semantic fallback producer.
- No second active Taste producer.

## Required report content
Persist exact report:
`reviews/worker_reports/taste-active-producer-restore-implement-01.md`

Include:
- old task state;
- exact new task id;
- exact new canonical producer id;
- generation 2 confirmation;
- exact canary appid/key/binding tuple;
- exact first scheduled execution time;
- proof active Taste count == 1 after migration;
- proof old generation 1 rejected and new generation 2 accepted;
- exact changed GitHub paths;
- whether the canary has run yet or is only armed;
- any user verification required in ChatGPT Scheduled UI;
- exact rollback/containment state if incomplete;
- whether System Audit is now due.

Before potentially long final verification, checkpoint the same report to `main`.
Before final response, persist final report and re-read it from `main`.

## Final status — exactly one
- `complete_canary_armed_system_audit_pending`
- `complete_canary_accepted_system_audit_due`
- `needs_followup_fix`
- `blocked`

Do not start another task.
