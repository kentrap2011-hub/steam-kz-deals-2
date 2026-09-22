# WORKER TASK — Progressive Fast / Dossier / Deep Architecture Amendment 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-fast-dossier-deep-architecture-amendment-01
Mode: IMPLEMENT / VALIDATE — CONTRACT / ARCHITECTURE ONLY
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.
Then open this task from main and reconcile it with the latest canonical contracts/reports before writing.

Read at minimum:
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `reviews/worker_reports/progressive-pass2-phase-c-core-implement-01.md`
- `reviews/worker_reports/progressive-pass2-dossier-integration-activation-prep-01.md`
- `DIRECTOR_TASK_BOARD.md`

## User-authoritative target architecture

The old model “PASS 2 is only a recovery attempt after PASS 1 produced analysis_incomplete” is superseded before production activation.

The canonical product model must become three parallel but related stages:

1. **Быстрый разбор** — provisional/fast analysis.
2. **Подготовка досье** — independent evidence/enrichment stage.
3. **Глубокий разбор** — eventual authoritative analysis for every current eligible game.

Internal technical names may remain PASS 1 / Dossier / PASS 2 where useful, but user-facing contracts/fields should support the Russian stage model above.

## Required semantics

### A. Быстрый разбор

- Purpose: give a useful provisional result early while deep analysis is not yet complete.
- It may run for a current eligible game when no authoritative current deep result exists.
- It may produce provisional fit / not-fit / incomplete outcomes under its existing lightweight rules.
- If a trustworthy current deep result already exists, Fast analysis must not spend a new attempt on that item merely to reproduce a weaker result.
- If Deep analysis previously failed/unresolved and Fast has not yet run, Fast remains allowed because it can still provide a useful provisional result.
- Fast analysis remains independent and non-blocking.

### B. Подготовка досье

- Runs independently from Fast and Deep.
- It does not decide fit/not-fit.
- It produces canonically accepted evidence dossiers only.
- Buffered/failed/recovery-owned dossier candidates are not accepted truth.
- A current exact-compatible accepted dossier is the evidence gate for Deep analysis.
- Dossier failures must not block unrelated games.

### C. Глубокий разбор

- This is the eventual authoritative analysis layer.
- It must eventually cover **every current eligible game**, not only Fast-incomplete games.
- Eligibility must not require a prior Fast attempt or Fast `analysis_incomplete`.
- A game becomes normal Deep work when:
  - it is current/eligible under the Progressive semantic generation/work identity;
  - an exact-compatible canonically accepted current Dossier exists;
  - no current authoritative Deep completion already exists for that deep work identity;
  - it is not already in an ineligible/consumed state under the canonical Deep recovery model.
- Deep may therefore run before Fast if the Dossier becomes ready first.
- A completed Deep result supersedes the Fast result for the current effective personalized decision.
- Fast history remains preserved for provenance/statistics and must not be rewritten to pretend Deep produced it.
- Deep must analyze games even when Fast previously said fit or not-fit; Fast success does not remove the game from eventual Deep coverage.
- Deep and Fast must not globally wait for each other.

## Effective-result precedence

Define separate concepts:

1. **stage state/history** — what Fast, Dossier, and Deep each did;
2. **effective current personalized result** — what the site/ranking should currently trust.

Required precedence:
- trustworthy completed Deep fit/not-fit => authoritative effective result;
- otherwise trustworthy completed Fast fit/not-fit may remain the provisional effective result;
- if neither stage has a trustworthy completed result => existing unresolved/not-analyzed projection applies.

Important:
- Deep `incomplete` or technical failure must not erase a still-valid trustworthy Fast fit/not-fit result.
- The site must still expose that the Deep stage itself is incomplete/failed even if the provisional Fast result remains effective.
- When Deep later completes, its result replaces the Fast result as effective truth.

## Deep first-pass and recovery model

The old rule “one Deep attempt and then permanently no more automatic eligibility for that work identity” is incompatible with the target of eventual full Deep coverage.

Amend the architecture so that:

- every current eligible deep work identity gets one normal Deep first-pass attempt once an accepted compatible Dossier is ready;
- a normal Deep success closes that identity;
- a normal Deep unresolved/technical failure does **not** count as permanently complete coverage;
- unresolved/failed Deep work moves into a separate GitHub-owned recovery state/queue and must not block normal first-pass work for other games;
- no unbounded blind retry loop is allowed;
- recovery eligibility must be explicit and GitHub-owned, based on a concrete recovery condition such as materially changed accepted Dossier/evidence, corrected runtime/validation defect, or explicit canonical recovery action;
- recovery attempts and history must be separately accountable from the normal first pass;
- normal first-pass completeness and all-games-deep-complete must be separate metrics;
- the architecture must make eventual all-game Deep completion possible without repeatedly hammering the same failing item.

Do not choose a hidden arbitrary retry quota. If a bounded retry count is needed, encode the rationale and exact reset/eligibility condition canonically.

## Ordering / interaction rules

- Fast and Deep may run in parallel on different games.
- If Deep completes first for a game, future Fast work for that same current identity should be skipped/not emitted.
- If Fast completes first, Deep still remains required later.
- Dossier may complete before or after Fast.
- Deep work is unlocked by Dossier readiness, not by Fast completion.
- One stage failure never globally blocks another stage or unrelated games.
- Current generation/work identity changes must invalidate stale stage authorizations under existing exact-binding rules.

## User-facing stage observability

The architecture must expose GitHub-produced presentation fields sufficient for the browser to show, per game, the state of all three stages without inference from history:

- Fast: not_started / completed / incomplete / error as canonically meaningful.
- Dossier: not_ready / accepted / failed_or_recovery (or equivalent exact canonical states).
- Deep: not_started / waiting_for_dossier / eligible_or_pending / completed / incomplete_or_recovery (split only as needed for truthful UX).

Do not make the browser infer these from arbitrary files or timestamps.

### Card indicators

The target UI must support three small pixel-style stage indicators on every game card:
- Fast analysis;
- Dossier;
- Deep analysis.

Architecture only needs to define the machine/user-facing states and labels needed by the UI; do not implement the final visual design in this task.

### Statistics page target

The old large top statistics panel is no longer the target.

The future UI should have one compact `Статистика` control leading to a dedicated statistics page with three sections:

**Быстрый разбор**
- total current scope;
- processed/attempted;
- completed fit;
- completed not-fit;
- incomplete;
- technical/error class if separately meaningful;
- remaining.

**Подготовка досье**
- total current dossier scope;
- canonically accepted;
- pending;
- failed/recovery-owned;
- normal-first-pass complete vs all-accepted/recovered completeness if both matter.

**Глубокий разбор**
- total current Deep coverage target;
- first-pass attempted/completed;
- fit;
- not-fit;
- incomplete/recovery;
- waiting for Dossier;
- ready/eligible now;
- remaining until all current games have authoritative Deep completion.

Do not merge denominators when scopes differ.

## Preserve reusable landed work

The completed old integration task landed useful GitHub-owned recomputation wiring before this architecture change.

Preserve/reuse where compatible:
- recomputation after canonical Dossier persistence;
- recomputation after PASS 1 persistence;
- recomputation after daily/current input changes;
- exact binding / liveness / zero-attempt projection behavior;
- PASS 2 ingest recomputation;
- ownership/concurrency safeguards.

Do not activate the old recovery-only eligibility model.

## Scope / activation guards

This task is contract/architecture amendment only.

Do NOT:
- activate Deep/PASS 2 production;
- create/enable/run a Scheduled Deep worker;
- process any Deep backlog item;
- consume a Deep attempt;
- implement the final statistics page or pixel icons;
- change Dossier evidence semantics;
- change site ranking weights;
- create a new recurring stage beyond the already accepted single Deep worker concept.

Keep Deep/PASS 2 inactive throughout this task.

## Required canonical updates

Amend the minimal canonical set so it is internally consistent, including as necessary:
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/execution_ownership_contract.json`
- relevant compact project decisions/routes if the old recovery-only model is documented there.

Do not change runtime implementation in this task except tiny non-executing metadata/schema scaffolding if strictly necessary to make the canonical architecture machine-readable. Prefer to defer runtime changes to the next implementation task.

## Validation

Prove at minimum:

- ARCH-01: Deep eligibility no longer requires prior Fast/PASS1 incomplete.
- ARCH-02: eventual Deep coverage target is all current eligible games.
- ARCH-03: Fast remains provisional and may run before Deep.
- ARCH-04: completed Deep suppresses future Fast work for the same current identity.
- ARCH-05: Fast success never suppresses eventual Deep work.
- ARCH-06: Deep completed fit/not-fit supersedes Fast as effective result.
- ARCH-07: Deep incomplete/error does not erase a valid Fast provisional result.
- ARCH-08: Dossier is independent evidence preparation and does not decide fit.
- ARCH-09: Deep first-pass failure moves to non-blocking recovery rather than permanent “done”.
- ARCH-10: no unbounded retry loop or hidden arbitrary quota is introduced.
- ARCH-11: normal Deep first-pass completeness is distinct from eventual all-games Deep completeness.
- ARCH-12: per-item Fast/Dossier/Deep stage states are explicitly representable for UI.
- ARCH-13: statistics-page fields/scopes are canonically defined without false shared denominators.
- ARCH-14: reusable old recomputation wiring is preserved conceptually and old activation plan is marked superseded.
- ARCH-15: Deep remains inactive and no production attempt/run occurs.
- ARCH-16: durable report committed and reread from main before completion.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-fast-dossier-deep-architecture-amendment-01.md`

Keep it compact and include:
- old model vs new model;
- exact precedence rules;
- exact normal-first-pass vs recovery semantics;
- UI stage-state contract;
- statistics-page metric contract;
- canonical files changed;
- validation ARCH-01..16;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_architecture_amendment
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
