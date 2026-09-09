# WORKER TASK — TASTE CHERNOBYLITE REAL CANARY EXECUTE 01

## Task ID
`taste-chernobylite-real-canary-execute-01`

## Mode
`ACCEPTANCE / ONE REAL SEMANTIC CANARY`

## Expected report
`reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md`

## User authorization
The user explicitly authorized exactly one real semantic Taste canary for:
- title: `Chernobylite Complete Edition`
- AppID: `1016800`
- Taste subject key: `App_1016800`

This authorization does NOT extend to any second game, second semantic result, new Scheduled Task, backlog widening, or architecture redesign.

## Goal
Use the new lightweight current-main one-AppID preparation path to prepare the exact current Chernobylite Taste tuple, prove that the tuple is canonically acceptable against the then-current live Taste profile and canonical queue/binding state, and only then run exactly one real Chernobylite semantic result through the existing generation-2 Scheduled Task and verify canonical ingest/receipt/cache/queue acceptance.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `WORKER_ANTI_STALL_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_IMPLEMENT_01.md`
- `reviews/worker_reports/taste-current-main-canary-path-implement-01.md`
- `.github/workflows/taste-current-main-canary.yml`
- `scripts/build_taste_current_main_canary.py`
- current canonical Taste producer-fence/binding/V5/ingest contracts directly required for acceptance.

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

Obey `WORKER_ANTI_STALL_PROTOCOL.md` throughout.

### 1. Fast current-main preparation preflight
Prepare AppID `1016800` using the new lightweight current-main path only.

Require:
- checked-out HEAD equals resolved current `origin/main` for that run;
- exactly one prepared subject, AppID `1016800`;
- queue cardinality exactly `1` for this canary;
- no other AppID leakage;
- repository remains clean;
- no canonical write occurs;
- exact current tuple is recorded from the proof artifact:
  - AppID / subject key;
  - taste fingerprint;
  - candidate-context digest;
  - profile identity/blob binding;
  - taste model/version;
  - taste semantics version/hash;
  - source mailing timestamp;
  - candidate context/provenance.

If the preparation path fails closed or returns zero queue rows, STOP `needs_followup`; do not force semantic work.

### 2. Mandatory live-profile + canonical acceptance gate
Before mutating/triggering the Scheduled Task, fetch the then-current canonical live Taste profile from its canonical source and compare its exact blob SHA/identity to the prepared tuple binding.

Also verify that the current canonical Taste queue/binding/ingest contract can accept a result for this exact tuple without any manual patch or bypass.

Hard gate:
- if prepared profile binding != then-current live profile binding, STOP `needs_followup` immediately;
- if canonical queue/binding state cannot accept this exact tuple, STOP `needs_followup` immediately;
- if any required producer-fence/V5/evidence/price-blind binding cannot be proven exact, STOP `needs_followup`.

Do NOT manually substitute a profile SHA.
Do NOT hand-edit canonical queue/payload JSON/JSONL.
Do NOT weaken any validation.

This preflight should be fast. Do not start another broad production rebuild or historical rerun.

### 3. Freeze one exact tuple
Only if step 2 fully passes, freeze the exact tuple for AppID `1016800` and persist it in the report before semantic execution.

No fallback candidate.
No second AppID.

### 4. Bind ONLY the existing Scheduled Task to this one canary
Update only Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9` for this exact canary tuple.

Preserve:
- generation 2;
- one game only;
- maximum one semantic result;
- no fallback/next-game behavior;
- existing Taste semantic requirements;
- same canonical ingest route;
- no paid API/Copilot/external scheduler.

After this exact canary is accepted, the canary prompt must not silently proceed to another game.

### 5. Trigger exactly one real semantic canary
Prefer supported direct run-now of the same Scheduled Task.

If direct run-now is unavailable, use the same task only with the smallest safe temporary schedule move and then restore DAILY 01:00 Europe/Samara.

Immediately after triggering:
- persist exact task/run identity and checkpoint;
- do not trigger again;
- if external waiting exceeds anti-stall limits, record `waiting_external` and return control instead of silently waiting.

Exactly one semantic result is authorized.

### 6. Verify canonical acceptance
After the one semantic result exists, prove all of the following:
- result is for AppID `1016800` / `App_1016800` only;
- producer generation 2;
- exact frozen fingerprint/context/profile/model/semantics tuple matches;
- producer fence PASS;
- V5/binding/evidence/price-blind validation PASS;
- canonical ingest transaction committed;
- receipt exists/advanced for this result;
- canonical Taste cache/overlay state advanced normally;
- active inbox result consumed normally;
- the exact pending queue item is no longer pending;
- no duplicate result;
- no second game processed.

Do not call the canary accepted without receipt/cache/queue evidence.

### 7. Restore containment
Before final response verify:
- same Scheduled Task id remains enabled;
- permanent schedule restored/verified as DAILY 01:00 Europe/Samara;
- no new Scheduled Task exists;
- no other game was processed;
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
- no manual canonical queue/payload edit;
- no producer-fence/binding/V5 weakening;
- no full production rebuild;
- no historical workflow rerun;
- no unrelated backlog work;
- no System Audit in this task;
- no widening to normal daily production.

## Required report
`reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md`

Include:
- current-main preparation run/proof and measured runtime;
- exact prepared tuple;
- exact current live profile binding at semantic gate;
- canonical queue/binding acceptability proof or blocker;
- whether Scheduled Task was mutated/triggered;
- semantic task/run identity if triggered;
- exact semantic result identity;
- producer-fence/V5/binding outcome;
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
