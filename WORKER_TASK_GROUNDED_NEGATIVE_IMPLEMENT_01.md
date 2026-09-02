# WORKER TASK — CHAT 2

Task ID: `grounded-negative-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/grounded-negative-implement-01.md`

## Context

Direct continuation of completed contract design:
`reviews/worker_reports/grounded-negative-contract-recon-01.md`

Do NOT repeat the negative-gap diagnosis or contract design.

Approved contract decisions to implement:
- introduce Taste V4-style explicit `negative_analysis_status`;
- structured `negative_findings` with stable category/code/evidence/risk_text_ru;
- normal ready state: `complete_with_confirmed_negative` with >=1 grounded finding;
- truthful unresolved state: `incomplete_no_confirmed_negative`;
- no normal `complete_no_negative` state;
- reuse existing GitHub-owned `chatgpt_taste_queue.jsonl` and scheduled Taste worker;
- work code: `resolve_grounded_negative_analysis`;
- preserve valid existing fit verdict/factors while backfilling only missing negative analysis;
- replace readiness-critical free-text phrase mapper with structured finding mapping;
- unresolved negative analysis is not normal paid-card readiness;
- never fabricate a negative and never promote heuristic-only evidence as grounded fact.

## Goal

Implement the bounded contract/queue/ingest/mapper/readiness changes needed so a normal paid recommendation cannot be considered explanation-complete without an end-to-end grounded Taste negative witness.

## Required implementation

### 1. Taste result/cache contract

Implement V4-compatible result/cache fields:
- `negative_analysis_status` enum:
  - `complete_with_confirmed_negative`
  - `incomplete_no_confirmed_negative`
- `negative_findings[]` entries with:
  - canonical `category`;
  - canonical stable `code`;
  - grounded `evidence`;
  - grounded Russian `risk_text_ru`.

Initial code/category catalog must preserve existing dedicated downstream codes plus the escape hatch:
- `unchanged_repetition`
- `low_active_gameplay`
- `directionlessness`
- `management_routine`
- `difficulty_punishment`
- `stealth_restart_pressure`
- `other_grounded_taste_risk`

`other_grounded_taste_risk` must survive as a visible grounded downside but carry neutral/no ranking penalty unless a deterministic score already exists.

Keep legacy V2/V3 cache compatibility for fit reuse, but legacy entries without the new status are `negative_analysis_ready=false`.

During compatibility period, preserve `negative_evidence` as the ordered projection of `negative_findings[].evidence` for new V4 results.

### 2. Validators

Update the canonical Taste result/cache validators so:
- `complete_with_confirmed_negative` + zero findings => reject;
- incomplete + non-empty findings/evidence => reject;
- invalid category/code pair => reject;
- empty evidence or risk text => reject;
- legacy entry may be read as compatibility input but is never negative-ready merely because old free text exists.

Do not weaken existing identity/profile/context binding validation.

### 3. Projection/index readiness

Extend the existing cache index / pre-AI Taste projection with derived readiness metadata such as:
- `negative_analysis_status`;
- `confirmed_negative_count`;
- `negative_analysis_ready`.

Do not invalidate a valid fit cache hit merely to obtain the new negative fields.

Required behavior:
- old valid V3 INCLUDE stays fit-cache-hit but negative-unresolved;
- V4 complete INCLUDE is both fit-cache-hit and negative-ready.

### 4. Existing Taste queue

Reuse the existing queue/runtime only.

Add exact work code:
`resolve_grounded_negative_analysis`

Queue rules:
- new/stale Taste evaluation requests this work together with existing Taste evaluation work;
- valid INCLUDE cache hit that is not negative-ready re-enters the same queue for this work;
- valid INCLUDE + ready finding does not;
- EXCLUDE does not require negative-readiness backfill for paid-card readiness;
- truthful incomplete result remains unresolved and is requeued by the next GitHub preparation cycle according to existing ownership/retry rules.

No second queue, scheduler, or interactive-chat production backlog.

### 5. Targeted negative-only ingest

For queue items whose only Taste work is `resolve_grounded_negative_analysis`:
- current fit verdict, fit level, reason code, normalized factors and bindings are immutable;
- ingest may update only the negative-analysis fields and compatibility projection;
- reject any result that attempts to rewrite unrelated accepted Taste semantics.

For full Taste evaluation items, normal full semantic ingest remains allowed.

### 6. Structured mapper

Replace readiness-critical raw-English keyword parsing with structured negative finding mapping.

Requirements:
- mapper admission based on validated category/code, not phrase match;
- preserve raw evidence and provenance;
- source remains `taste_negative_evidence` for grounded semantic negatives;
- pass through persisted grounded `risk_text_ru` rather than reconstructing it from English substrings;
- valid unfamiliar evidence under `other_grounded_taste_risk` must not disappear;
- existing `derived` heuristic risks remain separate and cannot satisfy the mandatory grounded-negative readiness invariant.

### 7. Paid-card readiness / final validation

A normal paid card explanation is ready only when the end-to-end witness exists:
- current bound Taste verdict INCLUDE;
- `negative_analysis_status == complete_with_confirmed_negative`;
- >=1 valid structured finding;
- mapper emits >=1 grounded `taste_negative_evidence` risk;
- final explanation payload contains at least one visible grounded Taste risk with provenance back to the finding.

If negative analysis is unresolved:
- do not fabricate a risk;
- do not output `минусов нет` / `рисков не найдено` as a game property;
- mark preparation/readiness incomplete through canonical state;
- fail closed according to the approved existing production completeness semantics rather than silently claiming complete coverage.

Do not change paid ranking/Taste scoring semantics beyond replacing the negative mapper input representation and neutral handling of `other_grounded_taste_risk`.

## Deterministic regressions

At minimum cover:
- contract consistency cases above;
- V3 fit-cache-hit remains fit-reusable but negative-unresolved;
- INCLUDE unresolved is queued with `resolve_grounded_negative_analysis`;
- INCLUDE ready is not requeued for negative work;
- EXCLUDE is not requeued for this readiness work;
- negative-only ingest cannot alter verdict/fit/reason/factors/bindings;
- incomplete result persists and requeues;
- unfamiliar valid structured finding survives mapper;
- `other_grounded_taste_risk` survives with neutral/no score;
- heuristic-only risk cannot satisfy readiness;
- final normal-ready card requires grounded Taste negative provenance;
- no generic/fabricated fallback minus.

## Canonical production acceptance

After focused tests pass:
1. run the smallest existing canonical GitHub preparation/build route that exercises the new contract and queue;
2. record queue counts/readiness counts produced by GitHub;
3. do NOT manually process the backfill in this worker;
4. if the existing scheduled Taste worker must process unresolved items, stop with `blocked` / waiting-on-existing-runtime and report exact queue/work state;
5. if the existing runtime has already produced sufficient V4 results, continue through canonical ingestion/build and validate a bounded generated top-N sample.

Success criteria for the eventual production state:
- normal-ready sampled cards have >=1 grounded structured negative;
- unresolved cards are not misrepresented as complete;
- valid negatives no longer disappear because of unfamiliar prose;
- no second scheduler/queue/runtime was introduced.

## Hard boundaries

Do NOT:
- invent one negative per game;
- expose heuristic suspicions as facts;
- weaken provenance/binding checks;
- manually process production games item-by-item;
- create a second Taste worker/scheduler/queue;
- redo Taste verdicts/factors solely for migration;
- redesign paid ranking/discount/wishlist logic;
- repeat the completed diagnosis/contract recon.

## Report format

Save:
`reviews/worker_reports/grounded-negative-implement-01.md`

### Task
What was implemented.

### Contract / compatibility
Exact schema/validator behavior.

### Queue / ingest
Exact work-code routing and targeted merge behavior.

### Structured mapper
Exact no-drop/provenance behavior.

### Readiness gate
Exact final-card semantics.

### Validation
Tests + canonical workflow refs + queue/readiness counts.

### Production state
Complete, or exact existing-runtime blocker/backfill state.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_verification`

### Recommended next step
One bounded next step only.