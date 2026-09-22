# WORKER TASK — Progressive Site Progress Header Compaction 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-site-progress-header-compaction-01
Mode: IMPLEMENT / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.
Then open this task from main.

Use the design/mobile route from `CHAT_CONTEXT.md` / `PROJECT_ROUTES.md`.
This task is intentionally parallel to the active PASS 2 Dossier integration task in ЧАТ 1.

## User problem

On mobile, the upper progress/status area is much too tall and consumes a large part of the first screen.

The current large analysis panel is also semantically ambiguous:
- the generic label `Разобрано` no longer tells the user whether it means PASS 1, PASS 2, or Dossier;
- several statistic tiles look like buttons but are not interactive;
- the user wants to immediately see, without opening anything:
  - how many items PASS 1 has processed;
  - how many items PASS 2 has processed;
  - how many Dossiers have been canonically accepted.

## Goal

Redesign the top progress area into a much more compact, mobile-first summary that makes PASS 1 / PASS 2 / Dossier progress explicit and removes false button affordances.

Do not change recommendation semantics, ranking, PASS execution, Dossier execution, or site navigation behavior.

## Required UX

### 1. Explicit three-stage progress

The top summary must visibly expose three distinct progress counters:

- `PASS 1` — number of current Progressive items for which the current PASS 1 attempt has been consumed/recorded, using GitHub-produced canonical count;
- `PASS 2` — number of current Progressive items for which the PASS 2 attempt has been consumed/recorded, using GitHub-produced canonical count;
- `Досье` — number of canonically accepted current Dossiers, using GitHub-owned accepted Dossier count.

Do not use one generic `Разобрано` number as a substitute for these three stages.

If denominators differ, show the correct denominator for each scope rather than pretending all stages share the visible-deal total.

Examples of acceptable compact presentation:
- `PASS 1 55/540`
- `PASS 2 0` or `PASS 2 0/<applicable scope>` only if that denominator is canonically defined
- `Досье 6/550`

The exact visual design is worker-owned, but the three stages must be readable at a glance on a phone.

### 2. Preserve useful outcome counts, but compactly

The user still needs the current overall outcome state such as:
- подходит;
- не подходит;
- не завершено;
- ещё не разобрано.

These may be rendered as one compact secondary row/text cluster rather than a large 2x3 tile panel.

Do not conflate outcome state with pipeline stage.

### 3. Remove false button affordance

Static counters must not visually pretend to be clickable controls.

For every header/stat element that is not interactive:
- no button-like hover/pressed expectation;
- no misleading pointer/click affordance;
- style it as a metric/chip/text summary.

Do not invent click/filter behavior merely to justify existing button styling.

Actual navigation/filter controls that already have behavior should remain clearly interactive.

### 4. Mobile size reduction

On phone-width layouts (roughly 360–430 CSS px), the analysis-progress section must be substantially shorter than the current large 2x3 card panel.

Target: the PASS 1 / PASS 2 / Dossier progress plus compact outcome summary should fit in roughly 120–160 CSS px where practical, without truncating labels or counts.

The first game card/tabs should move materially upward compared with the current layout.

Desktop must remain clean and readable.

## Data / architecture rules

Browser remains read-only presentation. It must not infer PASS 1/PASS 2/Dossier semantics from card history or recalculate pipeline state.

Prefer existing GitHub-produced fields from `data/production/visual/current.json`.

If one or more required display counts are not currently exposed:
- add only the minimum GitHub-produced presentation fields needed by the site;
- source them from canonical GitHub-owned PASS 1, PASS 2, and Dossier state;
- do not make browser code read/interpret mutable internal control-plane state directly;
- Dossier progress is observability/enrichment data only: its absence or failure must never block core deal payload publication.

PASS 2 inactive state must display truthfully (for example count 0 and/or an inactive marker if useful); do not fabricate progress.

## Parallel-work / conflict guard

ЧАТ 1 is concurrently implementing:
`WORKER_TASK_PROGRESSIVE_PASS2_DOSSIER_INTEGRATION_ACTIVATION_PREP_01.md`

Therefore this task must NOT modify:
- `config/progressive_pass2_contract.json`;
- `config/progressive_personalization_contract.json`;
- `config/execution_ownership_contract.json`;
- PASS 2 eligibility/work/result/receipt scripts;
- PASS 1 ingest/runtime semantics;
- Dossier contracts, worker prompts, ingest/recovery logic;
- Scheduled Task configuration;
- PASS 2 activation flags;
- workflows being changed by ЧАТ 1 for recomputation/activation integration.

Web/CSS/presentation files are the preferred scope.

If exposing a missing count requires touching a file that ЧАТ 1 has concurrently modified, do not create a merge race or workaround. Finish the non-conflicting UI work, record the exact missing presentation-field dependency, and stop that narrow part for a follow-up after ЧАТ 1 lands.

## Validation

Prove at minimum:

- UI-PROG-01: no generic ambiguous `Разобрано` metric is used as the primary pipeline-progress number.
- UI-PROG-02: PASS 1 count is visible and canonically sourced.
- UI-PROG-03: PASS 2 count is visible and canonically sourced.
- UI-PROG-04: Dossier accepted count is visible and canonically sourced.
- UI-PROG-05: differing denominators/scopes are not falsely merged.
- UI-PROG-06: fit / not-fit / incomplete / not-analyzed remain available in compact form.
- UI-PROG-07: non-interactive stats no longer look like buttons.
- UI-PROG-08: phone layout is materially shorter and has no overflow/cutoff at common mobile widths.
- UI-PROG-09: desktop remains usable.
- UI-PROG-10: browser performs presentation only; no semantic recomputation added.
- UI-PROG-11: Dossier summary absence cannot block core site publication.
- UI-PROG-12: no active ЧАТ 1 PASS 2 integration/runtime files were modified.
- UI-PROG-13: relevant web/UI regressions pass.
- UI-PROG-14: durable report committed and reread from main before completion.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-site-progress-header-compaction-01.md`

Keep it compact and include:
- before/after UX description;
- exact source fields used for PASS 1 / PASS 2 / Dossier counts;
- exact files changed;
- whether new presentation fields were required;
- validation UI-PROG-01..14;
- mobile/desktop verification;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_ready_for_director_acceptance
- complete_ui_ready_missing_progress_field_dependency
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
