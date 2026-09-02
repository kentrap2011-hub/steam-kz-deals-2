# WORKER TASK — NEW CHAT 2

Task ID: `grounded-negative-contract-recon-01`
Mode: `CONTRACT / RECON`
Report: `reviews/worker_reports/grounded-negative-contract-recon-01.md`

## Context

This is the direct continuation of completed diagnosis:
`reviews/worker_reports/card-negative-analysis-gap-01.md`.

Do NOT repeat that diagnosis.

Established facts from the completed report:
- current Taste semantic contract permits `INCLUDE + negative_evidence=[]`;
- negative concerns can be routed into the wrong semantic field;
- valid free-text `negative_evidence` can be silently lost by the narrow lexical mapper;
- current visible-risk policy correctly rejects heuristic-only negatives and must remain fail-closed;
- in the measured real generated top-30, 28/30 cards had no visible grounded negative;
- this is systemic, not a one-title rendering bug;
- absence of grounded negative must mean `analysis incomplete/unresolved`, never `game has no downside`.

## Goal

Define the smallest canonical contract/readiness change that makes grounded-negative completeness an explicit part of the existing Taste semantic architecture, without incentivizing fabricated negatives and without creating a second worker/runtime.

This task is contract/recon only. Do not implement production code unless the task file is later explicitly changed to IMPLEMENT.

## Read first

- `reviews/worker_reports/card-negative-analysis-gap-01.md`
- `config/taste_result_contract.json`
- current Taste queue/request contract used by the existing scheduled Taste worker
- `scripts/ingest_taste_results.py`
- current negative mapping path in `scripts/refine_visual_ranking.py`
- current final explanation readiness/status fields in `scripts/build_final_visual_payload.py`
- `scripts/card_explanation_policy.py`
- `scripts/validate_card_explanations.py`
- `config/execution_ownership_contract.json`
- relevant `PROJECT_ROUTES.md`
- relevant `KNOWN_WORKER_PITFALLS.md` only if directly triggered

Do not perform broad history archaeology.

## Required decisions

### 1. Normal semantic result contract

Define how a normal included game proves that negative analysis was actually attempted and completed.

Requirements:
- a normal completed `INCLUDE` result should carry at least one grounded downside/negative consideration;
- the contract must not force the worker to invent a criticism when authorized evidence genuinely cannot establish one;
- positive evidence must not be allowed to hide an actual negative concern inside a positive sentence while `negative_evidence=[]` remains accepted as complete.

Decide the minimal schema change: e.g. explicit negative-analysis status + typed negative evidence entries, or another smaller canonical form.

### 2. Exceptional unresolved state

Define an explicit state for the rare case where the worker genuinely cannot establish any grounded downside from authorized evidence.

That state must mean:
- negative analysis is incomplete/exceptional/unresolved;
- not `no negatives exist`;
- not ready as a fully complete explanation;
- eligible for GitHub-owned retry/review according to existing execution ownership.

Specify exact reason/status semantics and whether retry is mandatory, bounded, or terminal after a defined exceptional condition.

### 3. Typed/provenanced negative evidence

The current open-ended free-text -> keyword mapper is not reliable enough for readiness-critical negative evidence.

Define the smallest typed/provenanced contract that prevents valid negative evidence from disappearing silently.

At minimum determine:
- canonical category/code ownership;
- human-readable evidence text;
- provenance/source binding;
- whether category assignment happens in the semantic worker result or deterministically in GitHub;
- how unknown-but-valid negative evidence is preserved instead of dropped;
- how heuristic-only candidates remain separate from grounded semantic negatives.

Do not weaken grounding/provenance.

### 4. GitHub-owned readiness/work state

Define how GitHub records that a visible recommendation still lacks completed negative analysis.

Need one canonical status/work code, not an ad-hoc browser flag.

Determine:
- where the status is persisted;
- how it enters the existing queue/runtime path for `existing_scheduled_chatgpt_taste_worker`;
- how retry/order/completeness remain GitHub-owned;
- how a later valid result clears the incomplete state.

No chat-owned queue or second scheduler.

### 5. Final visual/UI semantics

Define exactly what downstream payload should do when negative analysis is incomplete:
- visible `risks[]` must remain empty unless grounded evidence exists;
- an explicit analysis-status field should distinguish incomplete from complete-with-grounded-negative;
- user-facing text may say analysis is not complete, but may never claim `минусов нет` / `рисков не найдено` as a property of the game;
- ranking/Taste eligibility must remain unchanged unless a separate product decision explicitly changes it.

Decide the smallest field/state needed in the final visual payload.

### 6. Migration / compatibility

Define how existing cached Taste results are handled:
- existing `INCLUDE + negative_evidence=[]` cannot silently become complete under the new contract;
- existing non-empty free-text evidence must not be discarded;
- determine whether a bounded migration can classify old rows, or whether they must be queued for re-analysis;
- preserve fail-closed behavior during migration.

### 7. Acceptance / implementation plan

Produce one bounded IMPLEMENT task specification with:
- exact files/contracts/components to change;
- deterministic contract tests;
- ingestion tests;
- mapper/preservation tests;
- queue/readiness tests;
- generated top-N validation;
- production completeness criteria;
- no requirement for manual item-by-item processing.

## Hard boundaries

Do NOT:
- force workers to invent one negative per game;
- expose heuristic/derived suspicion as fact;
- weaken grounded provenance;
- create a second scheduler/runtime/queue;
- redesign paid ranking/Taste scoring;
- repeat the already-completed incidence diagnosis;
- manually curate production titles;
- use title-only identity shortcuts.

## Report format

Save:
`reviews/worker_reports/grounded-negative-contract-recon-01.md`

### Existing confirmed gap
Compact inherited facts only; no re-audit.

### Proposed semantic contract
Exact normal + exceptional states and evidence schema.

### Provenance/category model
Exact typed evidence behavior.

### GitHub readiness ownership
Persisted state + existing queue/runtime handoff.

### Final payload semantics
Exact user-visible/readiness behavior.

### Migration
Existing-result treatment.

### Recommended IMPLEMENT
One bounded implementation task with exact files/tests/acceptance.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and exact refs.