# WORKER TASK — PROGRESSIVE SITE STAGE ICONS + STATISTICS UI 01

Repository: `kentrap2011-hub/steam-kz-deals-2`

Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository. If GitHub/tool opens another repository by default or the target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2` before doing any work.

Task ID: `progressive-site-stage-icons-statistics-ui-01`

Mode: `IMPLEMENT / VALIDATE`

Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

## User authorization

The user explicitly authorized moving on to the website update after the current PASS 2 ingest/recovery path was verified healthy.

Implement the already accepted site presentation direction below. This is a fresh task. Do **not** execute or revive the stale draft `WORKER_TASK_PROGRESSIVE_SITE_PROGRESS_HEADER_COMPACTION_01.md`.

## START

First open the current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Use the existing design/mobile route from `CHAT_CONTEXT.md` / `PROJECT_ROUTES.md`. Read only the minimum current web/presentation files and producer projection surfaces needed for this task.

At minimum inspect:
- `config/progressive_personalization_contract.json`;
- `config/execution_ownership_contract.json`;
- the current `web/**` files that render the main recommendation view/navigation/card/status/statistics surfaces;
- a bounded sample / schema-relevant portion of `data/production/visual/current.json`;
- the producer code that writes the stage/statistics presentation fields only if those fields are not already exposed in the visual payload;
- relevant existing UI/web regression tests.

Do not perform repository-wide redesign research.

## Architecture preflight

Record before editing:

1. GitHub remains owner of Fast/Dossier/Deep state projection, aggregate counts, effective-result provenance and publication.
2. Browser remains `read_only_presentation`; it must not infer semantic stage truth, personalized fit, scores, retry/recovery state or denominators from history/control-plane data.
3. This task creates no scheduler, queue, retry loop, checkpoint, production worker or new semantic owner.
4. Existing producer-owned stage/statistics fields from `config/progressive_personalization_contract.json` are the source of truth.
5. If a display field is genuinely missing from `data/production/visual/current.json`, add only the minimum GitHub-produced presentation projection needed; do not change Fast/Dossier/Deep business semantics.

## Accepted product design

### A. Main page: remove the large always-visible statistics panel

The main recommendation page must no longer devote a large block of the first screen to the old statistics/status panel.

Replace it with a compact entry/control labeled:

`Статистика`

This opens a dedicated statistics page/view.

The main page should prioritize the recommendation cards and navigation, especially on mobile.

### B. Dedicated Statistics page

Create a dedicated Statistics page/view using producer-owned aggregate fields.

It must present the three stages separately:

1. `Быстрый разбор` — Fast / PASS 1
2. `Подготовка досье` — Dossier
3. `Глубокий разбор` — Deep / PASS 2

Use the canonical statistics contract from `config/progressive_personalization_contract.json`.

Critical rule: each section uses its own canonical denominator/scope. Never fake a common denominator.

Display useful current progress/outcome metrics from the existing producer fields, including the meaningful completion/incomplete/pending/recovery distinctions already defined by the contract.

Do not reinterpret Dossier as personalized fit/not-fit.

### C. Recommendation cards: three small stage indicators

Each normal visible game card must render three small visual indicators, preferably compact pixel-style/icons consistent with the existing site style:

- Fast — `Быстрый разбор`
- Dossier — `Подготовка досье`
- Deep — `Глубокий разбор`

The icon/state must come **directly** from producer-owned fields:

- `fast_stage_state` + `fast_stage_outcome`
- `dossier_stage_state`
- `deep_stage_state` + `deep_stage_outcome`
- use `deep_recovery_state` only where needed to faithfully represent the Deep stage state already projected by GitHub.

The UI may choose icons/tooltips/compact labels, but must not infer or synthesize semantic state.

The three indicators should communicate progress/result without taking over the card.

### D. Remove large textual status labels from cards

Do not show large generic card-status text such as:

- `Подходит вам`
- `Не подходит`
- `Нужен дополнительный разбор`
- `Ещё не проверена`

The stage indicators replace this large status treatment.

A trustworthy `analyzed_not_fit` game is excluded from the normal visible list by producer-owned semantics and must not be shown merely to display a not-fit badge.

### E. Personalized score and explanation remain meaningful

For a game with a trustworthy current personalized analyzed-fit result:

- keep/show the existing personalized score where canonically supported;
- keep/show the existing supported explanation / why-fit fields;
- preserve existing personalized ranking authority and score ordering within the analyzed-fit tier.

For unresolved / not-yet-analyzed games:

- do not fabricate personalized scores;
- do not fabricate personalized explanation;
- preserve their lower-tier semantics/order from the producer.

Deep authoritative completion continues to supersede Fast as defined by the canonical contract. UI must display the effective producer-owned result, not recompute precedence.

### F. Mobile-first presentation

The accepted target is substantially more compact on phone layouts.

At common mobile widths (roughly 360–430 CSS px):

- the main page should get to the recommendation card content materially sooner than the old large-statistics layout;
- the three stage icons must not overflow or force a tall status block;
- the `Статистика` entry must remain easy to find;
- card score/reasons/navigation must remain readable.

Desktop/tablet should remain clean and usable.

## Scope boundaries

Preferred change scope:
- `web/**`;
- existing presentation tests;
- minimum producer projection/payload code only if a required canonical field is not currently published.

Do **not** change:
- Fast/PASS 1 semantic execution, eligibility, attempt semantics, retry behavior or scheduler;
- Dossier evidence/identity/retrieval/persistence/recovery semantics or scheduler;
- Deep/PASS 2 eligibility, ordering, attempt/recovery semantics, worker prompt or scheduler;
- `config/progressive_personalization_contract.json` business semantics;
- `config/progressive_pass1_contract.json`;
- `config/progressive_pass2_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/execution_ownership_contract.json`;
- ranking policy/score formulas;
- production control-plane ownership.

Do not add frontend fallbacks that guess stage state from older generic status fields.

## Validation / acceptance

Prove at minimum:

- SITE-01: old large always-visible statistics/status panel is removed from the main page.
- SITE-02: compact `Статистика` entry exists and opens a dedicated statistics page/view.
- SITE-03: Statistics presents Fast, Dossier and Deep separately.
- SITE-04: each Statistics section uses its correct canonical denominator/scope; no false shared denominator.
- SITE-05: every visible recommendation card renders three compact Fast/Dossier/Deep stage indicators from producer-owned fields.
- SITE-06: indicator states faithfully map current canonical stage fields; browser does not infer semantic state.
- SITE-07: large textual card statuses `Подходит вам`, `Не подходит`, `Нужен дополнительный разбор`, `Ещё не проверена` are removed from the normal card presentation.
- SITE-08: analyzed-not-fit remains excluded from the normal list; no new not-fit display path is added.
- SITE-09: analyzed-fit cards preserve existing supported personalized score and explanation/why-fit presentation.
- SITE-10: unresolved/not-analyzed/incomplete cards do not receive fake personalized score or explanation.
- SITE-11: existing tier/ranking/manual-end behavior remains unchanged.
- SITE-12: mobile widths around 360, 390, 412/430 px have no horizontal overflow/cutoff and main content is materially more compact.
- SITE-13: desktop remains usable and visually coherent.
- SITE-14: relevant web/UI regressions pass.
- SITE-15: if producer projection was touched, only minimum presentation fields were added and existing semantic/control-plane contracts remain unchanged.
- SITE-16: normal visual payload build/validation succeeds, or an exact unrelated pre-existing blocker is isolated.
- SITE-17: no Scheduled Task action or semantic production run is performed by this worker.
- SITE-18: durable report is committed and reread from fresh `main`.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-site-stage-icons-statistics-ui-01.md`

Keep it compact and include:
1. Task.
2. Verified facts.
3. Changes.
4. Exact producer fields used.
5. Validation SITE-01..18.
6. Mobile/desktop verification.
7. Any unresolved item.
8. Status.
9. One recommended next step.
10. Exact commit/run/file refs.
11. Efficiency / reusable lesson: `none` unless a real route/pitfall candidate was found.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Before completion, reread the committed report from fresh `main`.
