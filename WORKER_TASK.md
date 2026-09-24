# WORKER TASK — PROGRESSIVE DEEP INSUFFICIENT EVIDENCE DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

Task ID: `progressive-deep-insufficient-evidence-diagnostic-01`
Mode: `READ-ONLY DIAGNOSTIC / REPORT`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/progressive-deep-insufficient-evidence-diagnostic-01.md`

## User-approved goal

Determine why current Progressive Deep/PASS 2 completes very few games.

Current observed production state at task creation:
- current Deep coverage target: 465
- first-pass attempted: 49
- authoritative completed: 4
- completed fit: 0
- completed not-fit: 4
- incomplete/recovery: 45
- dominant issue among incomplete results: `insufficient_evidence`
- one observed technical `terminal_execution_failure`

The run-start liveness defect is already fixed and accepted separately. Do NOT reopen run-start confirmation unless direct evidence in this diagnostic proves it is causing the semantic outcomes under review.

## Question to answer

For current `analysis_incomplete / insufficient_evidence` outcomes, classify the dominant cause as one of:

- `DOSSIER_TOO_THIN`
- `DEEP_TOO_CONSERVATIVE`
- `MIXED_DOSSIER_AND_DEEP`
- `SEMANTIC_INPUT_OR_BINDING_DEFECT`
- `NOT_PROVABLE_FROM_AVAILABLE_EVIDENCE`

Do not choose a category by intuition. Prove it from exact current production artifacts and bounded independent comparison.

## START gate

First read current `CHAT_PROTOCOL.md` and complete its START gate.

Then read this task fully.

Read minimally:
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `data/cache/progressive_pass2_state.json`
- `data/production/pre_ai/progressive_pass2_work.json`
- current exact Deep result artifacts / ingest receipts for the sample below
- exact bound accepted Dossier files for the same identities
- exact current pinned profile bytes/reference used by those Deep identities
- candidate semantic context for those identities
- the accepted reports:
  - `reviews/worker_reports/progressive-pinned-live-profile-handoff-fix-01.md`
  - `reviews/worker_reports/progressive-deep-deferred-run-start-confirmation-01.md`
  - `reviews/worker_reports/progressive-fast-deep-zero-completion-diagnostic-01.md` only for historical comparison; do not carry its pre-fix conclusions forward without re-proving them against current identities.

Do not perform broad repository archaeology.

## Fixed bounded sample

### Successful Deep controls — all current completed not-fit

Inspect all four:
- appid `1227280`
- appid `1210320`
- appid `1161590`
- appid `1118240`

### Current insufficient-evidence sample

Inspect these eight current Deep outcomes:
- appid `1227690`
- appid `1244800`
- appid `1206610`
- appid `1239690`
- appid `1244460`
- appid `1222680`
- appid `1173820`
- appid `1196090`

If any listed identity is no longer current by the time the worker begins, do not silently substitute another app. Record it as `sample_identity_no_longer_current` and continue with the remaining exact sample.

### Technical control

Inspect appid `1164940`, currently observed as `terminal_execution_failure`, only to keep technical failure separate from semantic insufficiency. Do not let this one technical case distort the semantic classification.

## Diagnostic method

### A. Exact production-chain reconstruction

For every sampled identity, reconstruct only the exact current chain:

`current Deep work identity -> exact pinned profile -> candidate context -> exact accepted Dossier -> submitted Deep result/terminal receipt -> GitHub ingest receipt/state outcome`

Verify:
- appid/work_id/semantic_generation/profile pin exactness
- dossier path/content SHA/compatibility binding
- result identity and run-start authority
- accepted outcome and issue code
- no stale or cross-release evidence silently substituted

If any binding defect exists, identify it separately before semantic interpretation.

### B. Closed-book semantic sufficiency review

Using ONLY the exact production inputs that Deep had for that identity:
- pinned personalized profile
- candidate context
- accepted Dossier evidence

independently judge whether a competent Deep analysis could reasonably reach:
- `analyzed_fit`,
- `analyzed_not_fit`, or
- genuinely must remain unresolved.

Do not use current web evidence in this phase.

For each of the 8 incomplete cases, record:
- which concrete personalized dimensions are supported;
- which material positive/negative dimensions are missing;
- whether the existing Dossier contains enough candidate-specific evidence for a medium-confidence final verdict under the current PASS 2 contract;
- whether Deep's own submitted `insufficient_evidence` explanation correctly identifies the missing information, if the transport exposes such detail;
- classification: `justified_incomplete` or `final_verdict_was_reasonably_possible`.

Apply the same reasoning standard to the 4 successful not-fit controls. Identify what evidence/property actually allowed them to cross the final-verdict threshold.

### C. Dossier richness comparison

Compare successful controls vs incomplete cases on factual dimensions only, such as:
- number of usable player-feedback observations;
- source diversity;
- Russian evidence status;
- recency/temporal status;
- concrete mechanics/loop/difficulty/repetition/story/technical/performance information;
- presence of evidence relevant to the user's strongest positive and negative profile dimensions;
- whether observations are generic sentiment vs decision-relevant specifics.

Do not invent a numeric quality score unless an existing canonical field already provides it.

### D. Bounded current-public-evidence check

Only for incomplete cases classified in phase B as genuinely under-evidenced, perform a bounded independent current web check to answer:

> Was additional exact-product, decision-relevant player evidence reasonably discoverable, such that the accepted Dossier appears materially under-collected?

Rules:
- this is diagnostic current evidence, not proof of the exact historical retrieval surface seen by the Dossier worker;
- use exact product identity;
- prioritize player feedback/community evidence appropriate to the Dossier contract;
- do not require exhaustive research;
- record whether meaningful missing evidence is readily discoverable or not.

This phase separates:
- Dossier genuinely lacked reasonably available evidence, from
- public evidence itself being weak/ambiguous.

### E. Successful-control contrast

For each of the four completed not-fit controls, explain exactly why final not-fit was possible while most other cases became incomplete.

Check whether the difference is:
- stronger negative evidence,
- clearer conflict with pinned profile,
- richer/more diverse Dossier,
- a lower evidence threshold for negative conclusions,
- or another concrete factor.

Specifically test for asymmetry:
- Is Deep effectively able to finalize `not_fit` from a clear negative conflict while requiring unrealistically broad evidence to finalize `fit` or neutral/moderate cases?

Do not assert asymmetry unless the sample supports it.

## Required final analysis

Report:
1. current sample identities and exact bindings;
2. per-game compact comparison table;
3. successful-control evidence pattern;
4. incomplete-case evidence pattern;
5. whether current Dossiers are materially too thin;
6. whether Deep semantic threshold is materially too conservative;
7. whether fit/not-fit threshold appears asymmetric;
8. whether any semantic-input/profile binding defect remains;
9. whether the one terminal failure is independent technical noise;
10. dominant root-cause classification;
11. exact recommended next fix, but DO NOT implement it.

The recommendation must be one of:
- change Dossier evidence preparation/acceptance;
- change Deep semantic sufficiency/decision rules;
- coordinated Dossier + Deep change;
- repair semantic input/binding;
- no implementation yet because evidence is insufficient.

If recommending a future change, state the smallest bounded change and the regression cases it must preserve.

## Hard boundaries

Do NOT:
- modify PASS 1 or PASS 2 contracts/prompts/runtime;
- modify Dossier contracts/prompts/runtime;
- authorize Deep recovery;
- reset or delete attempts/results/state;
- create replacement semantic results;
- manually process production Deep backlog;
- modify/run/reschedule/enable/disable any Scheduled Task;
- change profile, ranking, UI or visual payload;
- turn current web research into canonical Dossier evidence.

Only task/report/tracking documentation may be written.

## Durable report

Commit:
`reviews/worker_reports/progressive-deep-insufficient-evidence-diagnostic-01.md`

Required final status exactly one:
- `complete_root_cause_proven`
- `complete_mixed_causes_proven`
- `not_provable_from_available_evidence`
- `blocked`

Before completion:
- commit the durable report to `main`;
- reread the exact committed report from fresh `main`;
- do not modify it after that reread unless repeating final commit+reread closeout.
