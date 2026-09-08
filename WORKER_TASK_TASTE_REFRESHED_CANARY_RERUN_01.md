# WORKER TASK — TASTE REFRESHED CANARY RERUN 01

## Task ID
`taste-refreshed-canary-rerun-01`

## Mode
`REFRESH EXACT CANARY BINDING + RUN SAME SCHEDULED TASK NOW + VERIFY ACCEPTANCE`

## Priority
`URGENT_BEFORE_01_00_PRODUCTION`

## Expected report
`reviews/worker_reports/taste-refreshed-canary-rerun-01.md`

## Goal
Obtain one fresh Chernobylite Taste result bound to the current canonical profile, using the SAME active generation-2 recurring ChatGPT Scheduled Task, run it now, and verify canonical acceptance before independent System Audit.

Do not choose another game. Do not create another Scheduled Task. Do not widen to backlog/full production in this task.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_STALE_INBOX_REPAIR_01.md`
- `reviews/worker_reports/taste-stale-inbox-repair-01.md`
- `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
- `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
- current canonical Taste queue/payload/projection/fence/inbox/archive contracts needed for this exact canary.

## Known state
The historical generation-1 blocker has already been repaired and archived safely.

The previous generation-2 Chernobylite result is stale only because its `profile_blob_sha` no longer matches the current canonical profile. It remains unaccepted and must not be forced through the binding guard.

Existing active Scheduled Task:
- title: `Taste Semantic Producer`
- task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- producer generation: `2`
- permanent schedule: DAILY 01:00 Europe/Samara.

Target game only:
- title: `Chernobylite Complete Edition`
- `taste_subject_key`: `App_1016800`
- `appid`: `1016800`.

## Required sequence

### 0. Durable report first
Create `reviews/worker_reports/taste-refreshed-canary-rerun-01.md` with status `in_progress`, persist it to `main`, and re-read before any Scheduled Task or active-inbox mutation.

### 1. Rebuild/freeze the CURRENT exact Chernobylite binding
From current canonical prepared Taste data, confirm AppID 1016800 still genuinely requires a fresh full Taste evaluation.

Freeze and record the exact current tuple immediately before arming the task:
- `taste_subject_key`
- `appid`
- `taste_fingerprint`
- `candidate_context_sha256`
- CURRENT `profile_blob_sha`
- `taste_model_version`
- `taste_semantics_sha256`
- `source_mailing_updated_at_utc`.

If Chernobylite is no longer eligible/current, STOP. Do not choose another game.

### 2. Archive the old stale generation-2 Chernobylite result
The existing stale file `data/ai_inbox/taste/canary-app-1016800-gen2.json` must not remain in the active inbox when a fresh result is submitted.

Preserve it under the explicit `data/ai_archive/taste/` lifecycle created by the preceding repair task, clearly marked as stale due to profile-binding mismatch, then remove only its active inbox copy.

Do not delete historical evidence.
Do not weaken active inbox validation.

### 3. Refresh the SAME Scheduled Task canary binding
Update ONLY task id `6aa032f37e688191a5c9a1a83f91c5d9` so its canary instructions use the exact current tuple frozen in step 1.

Preserve:
- same immutable task id;
- producer id above;
- generation `2`;
- exactly one game: AppID 1016800;
- max one semantic result;
- no fallback;
- no next game;
- no automatic widening;
- canonical GitHub Taste result route only;
- current V5/evidence/price-blind requirements;
- later invocations no-op once this exact current canary has been accepted.

Do not create a second task.

### 4. Trigger the SAME task now
Prefer supported direct/manual run-now if available.

If no safe direct run-now exists, temporarily move the schedule of THIS SAME recurring task to the earliest safe near-term time in Europe/Samara, exactly as permitted in the previous execute-now task.

Requirements:
- same task id;
- same canary-only prompt;
- still recurring, not converted into a disposable one-time task;
- after dispatch, restore DAILY 01:00 Europe/Samara;
- verify final task is enabled and recurring at 01:00 before finishing.

If immediate execution cannot be done safely without risking task identity or recurrence, STOP.

### 5. Verify canonical acceptance
Verify the new run:
- produced exactly one result for AppID 1016800;
- used the current frozen profile binding and all other current tuple fields;
- used producer generation 2 identity;
- passed the producer fence;
- passed current binding validation;
- completed the canonical ingest transaction;
- created/advanced canonical receipt/cache state;
- removed/consumed the accepted active inbox result according to normal lifecycle;
- advanced Chernobylite queue state so that this exact evaluation is no longer pending.

Do not describe it as accepted unless the canonical transaction and receipt/queue evidence prove acceptance.

### 6. Restore/verify containment
Before final response prove:
- SAME task id remains active/enabled;
- permanent schedule is DAILY 01:00 Europe/Samara;
- task remains canary-only/no-op after accepted Chernobylite;
- no second game was processed;
- no second task was created;
- no backlog/full production widening occurred.

## Hard boundaries
- No paid OpenAI API.
- No Copilot.
- No external scheduler/service.
- No new Scheduled Task.
- No other game.
- No mass/backlog semantic analysis.
- No producer-fence weakening.
- No binding-check bypass.
- No semantic V5 weakening.

## Required report
Persist exact report:
`reviews/worker_reports/taste-refreshed-canary-rerun-01.md`

Include:
- exact current frozen Chernobylite tuple;
- archive path of the stale prior gen2 result;
- exact trigger method and actual run time;
- final restored 01:00 schedule proof;
- exact new submission path/commit;
- exact canonical ingest workflow/run outcome;
- receipt/cache/queue acceptance evidence;
- proof no second game/task/widening;
- whether independent System Audit is now ready.

## Final status — exactly one
- `complete_canary_accepted_ready_for_system_audit`
- `needs_followup`
- `blocked`

Do not start System Audit yourself.
Do not widen production.
Do not start another task.
