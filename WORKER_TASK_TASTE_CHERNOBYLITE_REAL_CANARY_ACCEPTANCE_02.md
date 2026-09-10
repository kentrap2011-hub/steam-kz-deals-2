# WORKER TASK — TASTE CHERNOBYLITE REAL CANARY ACCEPTANCE 02

## Task ID
`taste-chernobylite-real-canary-acceptance-02`

## Mode
`ACCEPTANCE / ONE REAL SEMANTIC RESULT`

## Expected report
`reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`

## User authorization
The user has already explicitly authorized exactly one real semantic Taste result for:
- title: `Chernobylite Complete Edition`
- AppID: `1016800`
- Taste subject key: `App_1016800`

Do not ask for repeat confirmation for this same one-result acceptance.

Authorization does NOT extend to:
- a second game;
- a second semantic result;
- a new Scheduled Task;
- backlog widening;
- architecture redesign;
- paid OpenAI API/Copilot/external service.

## Goal
Run exactly one real semantic Taste acceptance result for Chernobylite using the fixed current-live profile binding route, and prove canonical acceptance end to end.

The user will continue updating `gaming_taste_live.json` in parallel during normal operation. Do not require a user-controlled quiet window.

## Required predecessor
Read first and treat as authoritative predecessor:
- `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`

The predecessor final status must be:
`complete_ready_for_real_canary_acceptance`

Required proven behavior from predecessor:
- each prepared tuple freezes one exact immutable live profile version;
- updates before freeze select the newer profile;
- updates after freeze cannot create a mixed-version tuple;
- continuous churn at the freeze boundary is bounded and fails closed;
- no user-controlled quiet window is required.

If this predecessor proof is not present on current `main`, STOP `blocked`.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `WORKER_ANTI_STALL_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- predecessor task/report above
- `.github/workflows/taste-current-main-canary.yml`
- `scripts/build_taste_current_main_canary.py`
- current canonical Taste producer-fence/binding/V5/evidence/price-blind/ingest contracts directly required for acceptance.

Do not perform broad Git/Actions/history archaeology.

## Existing Scheduled Task
Use only:
- title: `Taste Semantic Producer`
- id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- generation: `2`
- permanent schedule: DAILY 01:00 Europe/Samara.

Do not create another Scheduled Task.

## Required sequence

### 0. Durable report first
Create/update the exact report path with lifecycle `in_progress` before semantic work.

Every checkpoint must include:
- `Last checkpoint UTC`;
- lifecycle state;
- exact next action.

Follow `WORKER_ANTI_STALL_PROTOCOL.md`.

### 1. Prepare only Chernobylite using the fixed route
Use the current-main one-AppID preparation path for AppID `1016800` only.

Require:
- checked-out HEAD equals resolved current `origin/main` for that run;
- exactly one subject `App_1016800`;
- queue cardinality exactly `1`;
- no other AppID leakage;
- repository clean;
- no canonical write;
- exact frozen profile commit/blob/content binding recorded;
- exact model/semantics/fingerprint/context/source tuple recorded.

If preparation returns zero queue rows or fails closed, STOP `needs_followup`; do not force semantic work.

### 2. Current-state gate before semantic execution
Immediately before mutating/triggering the Scheduled Task, prove the exact prepared tuple is still acceptable under the current canonical contracts.

At minimum verify:
- exact immutable frozen profile binding from preparation;
- current canonical profile identity/state required by the active contract;
- canonical queue/binding state can accept this exact tuple;
- producer generation 2;
- producer fence;
- V5/evidence/price-blind bindings.

Concurrency handling:
- Do not mix a newer profile into an already frozen tuple.
- If a profile update before semantic execution makes the frozen tuple stale under the current canonical contract, discard that prepared tuple without semantic execution and re-run the bounded preparation from the newer live profile.
- Maximum acceptance-side preparation attempts: `3` total.
- Never generate more than one semantic result.
- If the profile keeps changing such that no tuple becomes acceptable within three preparation attempts, STOP `needs_followup` with zero semantic results. Do not ask the user to pause profile updates and do not retry indefinitely.

Do NOT manually substitute a profile SHA.
Do NOT hand-edit canonical queue/payload/cache/receipt/inbox.
Do NOT weaken validation.

### 3. Freeze one accepted tuple
Only after step 2 passes, persist the exact one-game tuple in the durable report before semantic execution.

No fallback candidate.
No second AppID.

### 4. Bind ONLY the existing Scheduled Task to this one result
Update only Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9` for the exact accepted Chernobylite tuple.

Preserve:
- generation 2;
- one game only;
- maximum one semantic result;
- no fallback/next-game behavior;
- existing Taste semantic requirements;
- same canonical ingest route;
- no paid API/Copilot/external scheduler.

### 5. Trigger exactly one real semantic result
Prefer supported direct run-now of the same Scheduled Task.

If direct run-now is unavailable, use the same task only with the smallest safe temporary schedule move and restore DAILY 01:00 Europe/Samara afterwards.

Immediately after triggering:
- persist exact task/run identity and checkpoint;
- do not trigger again;
- if waiting exceeds anti-stall limits, record `waiting_external` and return control.

Exactly one semantic result maximum.

### 6. Verify canonical acceptance
After the one semantic result exists, prove all of the following:
- result is for AppID `1016800` / `App_1016800` only;
- producer generation 2;
- exact frozen fingerprint/context/profile/model/semantics tuple matches;
- producer fence PASS;
- V5/binding/evidence/price-blind validation PASS;
- canonical ingest transaction committed;
- receipt exists/advanced;
- canonical Taste cache/overlay state advanced normally;
- active inbox result consumed normally;
- the exact pending queue item is no longer pending;
- no duplicate result;
- no second game processed.

If the live profile advances after semantic execution and the canonical ingest contract rejects the now-stale result, record the rejection exactly and STOP `needs_followup`. Do not trigger a second semantic result under this authorization.

Do not call the result accepted without receipt/cache/queue evidence.

### 7. Restore containment
Before final response verify:
- same Scheduled Task id remains enabled;
- permanent schedule restored/verified as DAILY 01:00 Europe/Samara;
- no new Scheduled Task exists;
- no second game was processed;
- no second semantic result was generated;
- no backlog/full-production widening occurred;
- no production rebuild or historical workflow rerun occurred.

## Hard boundaries
- exactly one real semantic Chernobylite result maximum;
- no second game;
- no second Scheduled Task;
- no paid OpenAI API;
- no Copilot;
- no external scheduler/service;
- no manual profile SHA substitution;
- no manual canonical queue/payload/cache/receipt/inbox edit;
- no producer-fence/binding/V5/evidence/price-blind weakening;
- no full production rebuild;
- no historical workflow rerun;
- no unrelated backlog work;
- no System Audit in this task;
- no widening to normal daily production;
- do not require the user to pause profile updates.

## Required report
`reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`

Include:
- preparation attempt count and exact reason for any discarded pre-semantic tuple;
- exact accepted prepared tuple;
- exact current profile/binding proof at the semantic gate;
- canonical queue/binding acceptability proof;
- whether Scheduled Task was mutated/triggered;
- semantic task/run identity if triggered;
- exact semantic result identity;
- producer-fence/V5/binding/evidence/price-blind outcome;
- ingest/receipt/cache/queue outcome;
- final Scheduled Task schedule/state;
- proof no second game/task/result/widening;
- System Audit readiness.

## Lifecycle states
Non-final:
- `in_progress`
- `waiting_external`

## Final status — exactly one
- `complete_canary_accepted_ready_for_system_audit`
- `needs_followup`
- `blocked`

Do not start System Audit.
Do not widen production.
Do not start another task.
