# WORKER TASK — PROGRESSIVE PERSONALIZED DEALS PHASE A IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `progressive-personalized-deals-phase-a-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

User authorization:
- explicit approval to implement Phase A was given after Director accepted
  `reviews/worker_reports/progressive-personalized-deals-architecture-amendment-01.md`.

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.

Затем открой этот task-файл из `main`.

Это прямое продолжение ЧАТ 2:
- `WORKER_TASK_PRODUCTION_ARCHITECTURE_SIMPLIFICATION_REVIEW_01.md`
- `WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_ARCHITECTURE_AMENDMENT_01.md`
- `reviews/worker_reports/progressive-personalized-deals-architecture-amendment-01.md`

Не начинай архитектурный аудит заново.

## Phase A objective

Implement the first bounded production slice of Progressive Personalized Deals:

1. publish all current deterministic-eligible candidates immediately, even while semantic analysis is incomplete;
2. project already trustworthy compatible semantic results when they exist;
3. classify the rest into honest progressive states;
4. enforce the user's tier ordering on the site;
5. expose GitHub-owned processing counts/status on the site;
6. keep existing source/business/identity correctness gates strict;
7. do NOT redesign or run the semantic worker yet.

This phase must provide useful current visibility even when PASS 1 has not started.

## Authoritative product semantics

Normal automatic list:

Tier 1 — `analyzed_fit`
- visible;
- existing compatible personalized score/ranking;
- personalized claims only if supported.

Tier 2 — `analysis_incomplete`
- visible;
- explicit “Разбор не завершён” state;
- no fake full personalized score;
- secondary order by existing deterministic purchase/deal signals, with urgency behavior preserved inside tier.

Tier 3 — `not_analyzed`
- visible;
- explicit “Ещё не разобрана” state;
- no fake personalized score;
- secondary order by deterministic purchase/deal signals.

`analyzed_not_fit`
- excluded from normal visible list;
- still counted in aggregate progress.

All deterministic-eligible candidates are visible unless:
- hard deterministic source/business/identity rules exclude them; OR
- a trustworthy compatible semantic result classifies them as `analyzed_not_fit`.

Do not interpret absence of evidence as not-fit.

## Phase A state scope

Phase A does NOT yet create PASS 1/PASS 2 execution.

Canonical durable visible states for Phase A:
- `analyzed_fit`;
- `analyzed_not_fit`;
- `analysis_incomplete`;
- `not_analyzed`.

Do not add durable `analysis_in_progress`.

Projection rules:
- exact-compatible trustworthy fit result -> `analyzed_fit`;
- exact-compatible trustworthy completed not-fit result -> `analyzed_not_fit`;
- existing canonical accepted result/failure may map to `analysis_incomplete` only if current contracts/provenance prove the attempt occurred but did not establish trustworthy fit/not-fit;
- no trustworthy current semantic outcome -> `not_analyzed`;
- incompatible/stale semantic result must NOT be presented as current fit/not-fit.

If existing data cannot reliably distinguish incomplete/error from never-analysed, prefer `not_analyzed`; do not fabricate an error history.

## Architecture preflight / ownership

Preserve:
- GitHub owns candidate scope, state projection, counts, validation, persistence, publication and ordering inputs.
- Browser is read-only presentation.
- Scheduled ChatGPT remains unchanged in Phase A.
- No interactive chat becomes a production worker.
- No new recurring scheduler/queue/retry owner is allowed in Phase A.

If implementation requires a new canonical progressive-personalization contract/state manifest, create it under GitHub ownership as approved by the architecture amendment.

Do not create PASS 1/PASS 2 queue machinery yet.

## Required canonical contract work

Implement the smallest canonical changes necessary for Phase A.

Expected direction:

1. Add a specialized machine-readable progressive-personalization contract defining at least:
   - four durable states;
   - tier precedence;
   - visibility semantics;
   - aggregate count invariants;
   - no durable in-progress state;
   - Tier 1 personalized scoring versus Tier 2/3 deterministic intra-tier ordering;
   - GitHub ownership;
   - Phase A publication semantics;
   - explicit note that PASS 1/PASS 2 execution is not yet activated by Phase A.

2. Amend/reference as needed:
   - `config/daily_execution_contract.json`;
   - `config/mailing_policy.json`;
   - `config/final_ranking_policy.json`;
   - `PROJECT_RULES.md`;
   - `PROJECT_DECISIONS.md`;
   - `config/execution_ownership_contract.json` only if wording must describe the new state model; do not transfer ownership.

Do not weaken taste threshold or hard deal/source rules.

## Required producer/state behavior

Implement GitHub-owned projection for the current deterministic-eligible catalogue.

The producer must emit enough machine data for the UI to render:

Per item at minimum:
- stable current item identity/key;
- analysis_state;
- analysis_tier or equivalent producer-owned tier key;
- whether item is visible in normal list;
- existing personalized score/ranking fields only when semantically valid;
- a separate deterministic Tier 2/3 intra-tier sort key, not fake `total_score`;
- safe short issue/status code only when current canonical evidence supports `analysis_incomplete`.

Aggregate at minimum:
- `total_current_candidates`;
- `analyzed_success_count`;
- `analyzed_fit_count`;
- `analyzed_not_fit_count`;
- `analysis_incomplete_count`;
- `not_analyzed_count`;
- `normal_visible_count`;
- `last_accepted_analysis_at_utc` if derivable honestly, else explicit null/unknown;
- optional `pass2_pending_count` must remain absent/zero until Phase C unless already canonically meaningful.

Required invariants:

`total_current_candidates = analyzed_fit_count + analyzed_not_fit_count + analysis_incomplete_count + not_analyzed_count`

`analyzed_success_count = analyzed_fit_count + analyzed_not_fit_count`

`normal_visible_count = analyzed_fit_count + analysis_incomplete_count + not_analyzed_count`

If counts do not reconcile, fail validation. Do not publish contradictory status.

## Required daily publication behavior

Remove the current Phase-A-incompatible global availability condition that waits solely for semantic queue closure.

A current deterministic catalogue may publish while unresolved semantic work remains.

However retain hard global source integrity/freshness gates:
- wrong/incomplete source snapshot;
- invalid region/source identity;
- stale current source beyond canonical allowed freshness;
- malformed deterministic core state.

Do not label stale source data as current merely to get a payload.

Existing last-known-good behavior for source failure remains valid.

## Required visual/current behavior

`data/production/visual/current.json` (or the canonical equivalent consumed by the site) must be able to represent the progressive catalogue.

Initial valid state may be:
- many/all items = `not_analyzed`;
- compatible existing fit results = Tier 1;
- trustworthy existing not-fit = excluded;
- trustworthy current incomplete failures = Tier 2 if provable.

Do not require semantic queue count = 0 for publication.

The visual payload must remain read-only for the browser.

## Required sorting behavior

Automatic order is tier-first.

Urgency toggle OFF:
1. Tier 1 -> existing personalized score/order;
2. Tier 2 -> deterministic purchase/deal sort key;
3. Tier 3 -> deterministic purchase/deal sort key;
4. title or existing stable tie-break inside tier.

Urgency toggle ON:
- tier precedence still comes FIRST;
- within each tier, existing urgency behavior applies before that tier's score/sort key.

Do not allow a Tier 2/3 purchase-only key to numerically compete against Tier 1 personalized `total_score`.

Preserve explicit local `manual_end_at` override unless implementation proves a conflict; if conflict exists, stop and document before changing its semantics.

## Required UI behavior

On each visible card show explicit analysis state.

Required Russian labels:

`analyzed_fit`
- “Разобрана · подходит вам”

`analysis_incomplete`
- “Разбор не завершён”

`not_analyzed`
- “Ещё не разобрана”

Do not render a normal card for `analyzed_not_fit`.

For Tier 2/3:
- no fake personalized score;
- no unsupported `why_fit`;
- no unsupported personal risk conclusion.

## Required site progress summary

Expose a compact visible processing summary sourced entirely from GitHub-produced machine data.

Required:
- Всего;
- Разобрано;
- Подходит;
- Не подходит;
- Ошибки / не завершено;
- Ещё не разобрано.

Also show:
- last successful accepted analysis timestamp when available;
- if unavailable, show a truthful neutral state rather than inventing a time.

Do not calculate hidden processing status from DOM/card counts as the authoritative source.

Optional:
- “Повторный разбор: N” only if canonical value exists and >0. Do not invent it in Phase A.

## Required compatibility with current semantic cache/results

Existing exact-compatible accepted Taste results should be reused when safe.

Do not:
- re-run analysis;
- relabel incompatible results as current;
- mutate accepted Taste semantics;
- manufacture `analyzed_not_fit` from old `insufficient` when insufficiency means evidence missing.

Where current V5 semantics are ambiguous, implement the conservative mapping approved by the amendment:
- insufficient information -> unresolved/not current fit verdict, not hidden not-fit.

If a contract conflict prevents safe classification, update the canonical contract explicitly and cover with regression tests; do not silently reinterpret.

## Required workflow behavior

Normal GitHub daily build/deploy may be updated so Phase A current progressive payload can publish before semantic closure.

Allowed:
- normal GitHub Actions build/test/validation;
- normal deployment/activation needed to expose Phase A;
- bounded synthetic fixtures/tests;
- production-safe rebuild from already canonical deterministic inputs if the implementation architecture requires it.

Forbidden:
- running Scheduled ChatGPT;
- processing semantic backlog manually;
- creating PASS 1 or PASS 2 attempts;
- manual Taste/Dossier decisions;
- recovery/quarantine surgery unrelated to Phase A;
- changing source/business eligibility rules.

## Activation requirement

This task is IMPLEMENT / ACTIVATE / VALIDATE, not code-only.

After implementation:
1. merge/activate through the repository's normal path;
2. run the relevant deterministic build/validation/deploy path;
3. verify the deployed/current payload/site surface actually exposes Phase A behavior if the normal activation path supports it;
4. do not claim live acceptance from tests alone if runtime/deploy is required.

If an external deployment/runtime layer is not available to the worker, report that exact boundary and do not claim full live acceptance.

## Required validation scenarios

At minimum test/prove:

A. Zero semantic results:
- current deterministic candidates publish;
- all eligible items Tier 3;
- counts reconcile.

B. Mixed state:
- fit + incomplete + untouched + not-fit;
- visible order = Tier 1 -> Tier 2 -> Tier 3;
- not-fit absent;
- counts reconcile.

C. Semantic queue remains nonzero:
- current progressive payload still publishes.

D. Incompatible/stale Taste:
- must not classify current fit/not-fit;
- item visible unresolved.

E. Current `insufficient` due missing evidence:
- not silently excluded as not-fit.

F. Hard source-integrity failure:
- no falsely current Phase A payload published.

G. Urgency OFF:
- tier-first preserved.

H. Urgency ON:
- tier-first still preserved; urgency operates only inside tier.

I. Tier 2/3:
- no fake total personalized score / why_fit.

J. Manual end override:
- existing semantics preserved.

K. Aggregate arithmetic:
- all invariants enforced by validation.

L. Existing fully personalized path:
- valid Tier 1 cards retain existing score and supported explanations.

## Acceptance checks

PHASEA-01 — dedicated canonical progressive state/tier/count semantics exist.

PHASEA-02 — current deterministic catalogue can publish with semantic queue open.

PHASEA-03 — all unresolved deterministic-eligible candidates are visible as Tier 2 or Tier 3, never silently dropped for lack of analysis.

PHASEA-04 — trustworthy compatible not-fit is excluded and counted.

PHASEA-05 — tier-first ordering is implemented in producer/UI.

PHASEA-06 — urgency toggle cannot move lower analysis tier above higher tier.

PHASEA-07 — Tier 2/3 do not expose fake personalized score/explanation.

PHASEA-08 — site shows required GitHub-owned progress counts.

PHASEA-09 — count invariants are machine-validated.

PHASEA-10 — source/business/identity hard gates remain strict.

PHASEA-11 — existing compatible accepted Taste is reused without reanalysis.

PHASEA-12 — incompatible/ambiguous old semantic state is mapped conservatively, not hidden as not-fit.

PHASEA-13 — no PASS 1/PASS 2 worker redesign or semantic backlog processing occurs.

PHASEA-14 — relevant tests/regressions pass.

PHASEA-15 — normal activation/deploy path succeeds or exact external blocker is documented.

PHASEA-16 — durable report committed to exact path and reread from `main`.

## Durable report

Write:
`reviews/worker_reports/progressive-personalized-deals-phase-a-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight confirmation.
3. Implemented canonical semantics.
4. Implemented state projection.
5. Implemented publication behavior.
6. Implemented sorting.
7. Implemented UI/status counters.
8. Semantic cache compatibility mapping.
9. Files/components changed.
10. Validation A-L.
11. PHASEA-01..16.
12. Activation/deploy evidence.
13. User-visible resulting behavior.
14. Explicitly not implemented (PASS 1/PASS 2).
15. Unresolved.
16. Status.
17. Exactly one recommended next step.
18. Exact commit/PR/run/deploy refs.
19. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_director_acceptance`
- `complete_code_waiting_external_live_acceptance`
- `needs_fix`
- `blocked_external`
- `needs_user_decision`

## Completion rule

Do not present the task as complete until:
- report exists at the exact path in `main`;
- report is reread from `main`;
- all claimed commits/runs are exact;
- live/deploy status is described truthfully.

## Exactly one next step

If fully successful:
- return to Director for acceptance before Phase B item-level PASS 1 implementation.

If activation is externally blocked:
- return exact blocker only; do not start Phase B.

Do not implement Phase B/C/D inside this task.
