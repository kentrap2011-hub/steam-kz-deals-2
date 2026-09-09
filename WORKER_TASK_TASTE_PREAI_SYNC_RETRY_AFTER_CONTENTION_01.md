# WORKER TASK — TASTE PRE-AI SYNC RETRY AFTER CONTENTION 01

## Task ID
`taste-preai-sync-retry-after-contention-01`

## Mode
`QUIESCENCE PREFLIGHT + ONE CANONICAL PRE-AI RETRY + SAME CHERNOBYLITE CANARY`

## Expected report
`reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md`

## Goal
Retry the canonical Taste pre-AI synchronization exactly once after confirming there is no concurrent repository writer likely to collide with the generated production/pre-AI commit, then — only if the synchronized state is durably committed and exactly bound to the current live Taste profile — run only the same Chernobylite canary through the same generation-2 Scheduled Task and verify canonical acceptance.

Do not choose another game. Do not create another Scheduled Task. Do not widen to backlog/full production.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_PREAI_PROFILE_SYNC_AND_CANARY_RERUN_01.md`
- `reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`
- current canonical production/pre-AI generation workflow and only the contracts directly required for this retry.

## Known prior outcome
The immediately preceding task finished `needs_followup`.

Its one authorized synchronization attempt:
- reused production workflow run `34274404165`;
- rerun job id `102329869100`;
- deterministic collection/generation ran;
- commit/push failed because `main` advanced concurrently and the workflow rebase/push path encountered conflicts;
- refreshed generated state was not durably committed;
- no Chernobylite semantic run occurred;
- no second rebuild occurred.

That previous task is closed. This new task authorizes one fresh bounded retry only after a quiescence preflight.

## Existing semantic Scheduled Task
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- generation: `2`
- permanent schedule: DAILY 01:00 Europe/Samara.

Target game only:
- `Chernobylite Complete Edition`
- `taste_subject_key = App_1016800`
- `appid = 1016800`.

## Required sequence

### 0. Durable report first
Create `reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md` with status `in_progress`, persist to `main`, and re-read before mutation.

### 1. Quiescence preflight
Before launching any new regeneration, inspect the current GitHub-owned workflows/runs that can write the same production/pre-AI generated state or otherwise advance `main` in the relevant path.

Required decision:
- if a relevant writer is currently active/in-progress/queued and collision risk is real, DO NOT launch the retry; stop `needs_followup` and record the exact active writer/run;
- if there is no relevant active writer and repository state is suitable for one clean attempt, continue.

Do not wait indefinitely inside this task.
Do not disable unrelated workflows.
Do not edit workflow concurrency/locking architecture in this task.

### 2. Capture current live profile
Read the current canonical live Taste profile immediately before the retry and record its exact blob SHA.

Do not manually substitute this SHA into generated payload files.
Do not hand-edit generated bindings.

### 3. Run exactly ONE canonical synchronization retry
Use the existing GitHub-owned deterministic production/pre-AI path.

This new task authorizes exactly one regeneration/rerun attempt.

After it finishes, require all of the following before semantic work:
- regenerated production/pre-AI state is durably committed to `main`;
- committed canonical `canonical_profile_blob_sha` equals the live profile SHA current at verification time;
- Chernobylite AppID 1016800 remains the required selected fresh Taste row;
- its fingerprint/context/model/semantics/source bindings are current.

If commit/push conflicts again, STOP `needs_followup`; do not launch a second retry.
If live profile changes again before equality is established, STOP `needs_followup`; do not chase it.

### 4. Freeze exact committed Chernobylite tuple
Only after the committed profile-binding equality passes, record exact:
- `taste_subject_key`
- `appid`
- `taste_fingerprint`
- `candidate_context_sha256`
- `profile_blob_sha`
- `taste_model_version`
- `taste_semantics_sha256`
- `source_mailing_updated_at_utc`.

No fallback candidate.

### 5. Active inbox safety
Confirm stale historical Chernobylite results remain preserved under `data/ai_archive/taste/**` and are absent from active inbox before a fresh result.

Do not delete archive history.
Do not weaken producer validation.

### 6. Update ONLY the SAME Scheduled Task
Update task id `6aa032f37e688191a5c9a1a83f91c5d9` to the exact committed tuple from step 4.

Preserve:
- same immutable task id;
- producer generation 2;
- exactly one game AppID 1016800;
- maximum one semantic result;
- no fallback/next game;
- no automatic widening;
- canonical GitHub Taste route only;
- V5/evidence/price-blind requirements;
- later runs under canary prompt no-op after this exact canary is accepted.

Do not create another Scheduled Task.

### 7. Trigger SAME task now
Prefer supported direct run-now.

If unavailable, temporarily move the schedule of THIS SAME recurring task to the earliest safe near-term time in Europe/Samara and then restore DAILY 01:00 Europe/Samara.

Immediately before semantic work, re-check that current live profile still equals the committed prepared binding. If not, no-op/stop.

### 8. Verify canonical acceptance
Prove exactly one Chernobylite result:
- producer generation 2;
- exact committed current tuple;
- producer fence PASS;
- binding/V5 validation PASS;
- canonical ingest transaction committed;
- receipt/cache state advanced;
- active inbox result consumed normally;
- AppID 1016800 no longer remains pending for this exact evaluation.

Do not call it accepted without receipt/queue evidence.

### 9. Restore containment
Before final response verify:
- same Scheduled Task id remains enabled;
- permanent schedule is DAILY 01:00 Europe/Samara;
- no other game processed;
- no second task created;
- no backlog/full-production widening;
- only one synchronization retry was attempted in this task.

## Hard boundaries
- no paid OpenAI API;
- no Copilot;
- no external scheduler/service;
- no new Scheduled Task;
- no other game;
- no mass/backlog semantic analysis;
- no producer-fence weakening;
- no profile-binding bypass/manual SHA substitution;
- no V5 weakening;
- no workflow locking/concurrency redesign in this task;
- exactly one canonical synchronization retry maximum.

## Required report
`reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md`

Include:
- quiescence preflight result and any relevant active writers;
- live profile SHA before retry;
- exact canonical retry mechanism/run/job;
- whether regenerated state committed to `main`;
- prepared profile SHA after commit;
- proof of profile equality or exact blocker;
- frozen Chernobylite tuple if equality passes;
- semantic trigger/run details if executed;
- canonical ingest/receipt/cache/queue outcome;
- final 01:00 schedule proof;
- proof no second game/task/widening and only one sync retry;
- System Audit readiness.

## Final status — exactly one
- `complete_canary_accepted_ready_for_system_audit`
- `needs_followup`
- `blocked`

Do not start System Audit yourself.
Do not widen production.
Do not start another task.
