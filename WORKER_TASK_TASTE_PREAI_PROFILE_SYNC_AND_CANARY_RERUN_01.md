# WORKER TASK — TASTE PRE-AI PROFILE SYNC AND CANARY RERUN 01

## Task ID
`taste-preai-profile-sync-and-canary-rerun-01`

## Mode
`BOUNDED PRE-AI REGENERATION + SAME-CANARY RERUN`

## Expected report
`reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`

## Goal
Synchronize the canonical pre-AI Taste payload/queue with the then-current live Taste profile, then run exactly one fresh Chernobylite canary using the SAME generation-2 recurring Scheduled Task and verify canonical acceptance.

Do not choose another game. Do not create another Scheduled Task. Do not widen to backlog/full production.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`
- `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`
- current canonical pre-AI generation, queue, payload, producer-fence, inbox/archive and ingest contracts directly needed for this task.

## Known state
Previous task finished `needs_followup` because:
- canonical pre-AI payload profile binding = `191b6d6c5dec2f9ef2976517f301528740f9bec2`;
- live Taste profile later advanced to `705e1f852d91a8a63d8686b37c51ace41c02f4ac`;
- therefore exact binding equality was lost and the canary correctly did not run.

Existing Scheduled Task:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- generation: `2`
- enabled: true at preceding final verification
- permanent schedule: DAILY 01:00 Europe/Samara.

Target game only:
- `Chernobylite Complete Edition`
- `taste_subject_key = App_1016800`
- `appid = 1016800`.

## Required sequence

### 0. Durable report first
Create the exact report with status `in_progress`, persist to `main`, and re-read before any mutation.

### 1. Establish current live profile
Read the current canonical live Taste profile and record its exact blob SHA.

Do not manually substitute this SHA into prepared payload files.
Do not edit generated bindings by hand.

### 2. Canonically regenerate atomic pre-AI state ONCE
Use the existing canonical GitHub-owned/deterministic pre-AI generation path to regenerate the atomic Taste payload/queue against the current live profile.

This is a bounded synchronization attempt, not a new scheduler or retry loop.

After generation finishes, verify:
- canonical payload `canonical_profile_blob_sha` equals the live profile blob SHA that is current at verification time;
- Chernobylite AppID 1016800 remains present and requires fresh full Taste work;
- its fingerprint/context/model/semantics/source bindings are current.

If the live profile changes again before equality is established, STOP fail-closed with `needs_followup`. Do not loop indefinitely and do not bypass the binding guard.

### 3. Freeze exact current Chernobylite tuple
Only after profile equality is proven, record exact:
- `taste_subject_key`
- `appid`
- `taste_fingerprint`
- `candidate_context_sha256`
- `profile_blob_sha`
- `taste_model_version`
- `taste_semantics_sha256`
- `source_mailing_updated_at_utc`.

No fallback candidate.

### 4. Ensure active inbox is clean for this canary
Historical stale Chernobylite results must remain preserved under `data/ai_archive/taste/**` and absent from active inbox before the fresh run.

Do not delete archive history.
Do not weaken active inbox validation.

### 5. Update ONLY the SAME Scheduled Task
Update task id `6aa032f37e688191a5c9a1a83f91c5d9` to the exact tuple from step 3.

Preserve:
- same immutable task id;
- producer generation 2;
- exactly one game (AppID 1016800);
- maximum one result;
- no fallback/next game;
- no automatic widening;
- canonical GitHub Taste route only;
- V5/evidence/price-blind requirements;
- after accepted canary, later runs under this canary prompt no-op.

Do not create another Scheduled Task.

### 6. Trigger SAME task now
Prefer a direct supported run-now mechanism.

If unavailable, temporarily move the schedule of this SAME recurring task to the earliest safe near-term time in Europe/Samara, then restore DAILY 01:00 Europe/Samara after dispatch.

Do not convert it to a disposable one-time task.
Do not create a second task.

Immediately before semantic work, exact current live profile and prepared binding must still match. If they do not, no-op/stop rather than evaluate stale input.

### 7. Verify canonical acceptance
Prove exactly one Chernobylite result:
- was produced under generation 2;
- matched the frozen current tuple;
- passed producer fence and binding validation;
- completed canonical ingest;
- advanced receipt/cache state;
- removed/consumed active inbox result under normal lifecycle;
- removed or otherwise resolved AppID 1016800 from pending Taste queue state.

Do not call it accepted without receipt/queue evidence.

### 8. Restore containment
Before finalizing verify:
- same Scheduled Task id remains enabled;
- permanent schedule is DAILY 01:00 Europe/Samara;
- no other game was processed;
- no second task was created;
- no backlog/full-production widening occurred.

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
- one bounded pre-AI regeneration attempt only; if profile changes again, stop and report.

## Required report
`reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`

Include:
- live profile SHA before regeneration;
- exact canonical regeneration method;
- prepared profile SHA after regeneration;
- proof of equality or exact mismatch if it changes again;
- frozen Chernobylite tuple;
- trigger method and actual run time if run occurs;
- final 01:00 schedule proof;
- exact canonical ingest outcome;
- receipt/cache/queue evidence;
- proof no second game/task/widening;
- whether independent System Audit is ready.

## Final status — exactly one
- `complete_canary_accepted_ready_for_system_audit`
- `needs_followup`
- `blocked`

Do not start System Audit yourself.
Do not widen production.
Do not start another task.
