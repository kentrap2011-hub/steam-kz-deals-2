# WORKER TASK — RUSSIAN TRANSLATION NONBLOCKING PUBLICATION STATISTICS 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch to this repository before continuing.

Task ID: `russian-translation-nonblocking-publication-statistics-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/russian-translation-nonblocking-publication-statistics-01.md`

## User-approved product behavior

The user explicitly requires:

1. Missing Russian translations must NOT block the site from rebuilding/publishing.
2. Untranslated games must remain explicitly observable; do not pretend a translation exists.
3. Statistics must gain a dedicated translation-status block, visually analogous to the existing Statistics blocks, not loose standalone rows.
4. That block must show:
   - current count of games without a valid Russian translation;
   - date/time of the last successful translation;
   - date/time of the last translation attempt.
5. The two dates have distinct semantics so the user can see when translation was attempted but did not succeed.
6. A translation run that finds zero games needing translation counts as a successful translation outcome.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and make the required task checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. Russian translation + final visual + Statistics routes in `PROJECT_ROUTES.md`;
4. current Russian translation contract/worker/persistence schema;
5. current meaningful-Russian validation and final visual build/deploy flow;
6. current Statistics producer/schema/UI;
7. `config/execution_ownership_contract.json`;
8. `config/daily_execution_contract.json`;
9. only the exact workflow/scripts/tests required for this implementation.

Do not reconstruct unrelated history.

## Architecture preflight — mandatory before writes

Prove and record:
1. which GitHub component currently owns translation scope, attempts, accepted translation state, visual build, and publication;
2. which exact validation currently blocks full visual publication when translations are missing;
3. how to make missing translations nonblocking without allowing non-Russian text to masquerade as Russian;
4. where durable attempt/success timestamps belong so the browser only displays producer-owned facts;
5. how the untranslated-game count is derived from current canonical scope rather than browser guesswork;
6. why the change introduces no second scheduler, queue, retry owner, or browser-side authority.

If this cannot be proven from current canonical contracts/state, stop with `needs_user_decision` rather than inventing authority.

## Required behavior

### A. Translation absence no longer blocks publication

A current game lacking a valid meaningful Russian description must not by itself fail the full visual build or prevent GitHub Pages publication.

However:
- untranslated state must remain explicit;
- non-Russian source text must not be relabeled as Russian;
- invalid/stale/wrong-AppID translations remain invalid;
- existing exact binding/provenance rules remain fail-closed;
- the change must not silently drop games merely to make validation pass.

Convert the current release-blocking translation condition into the smallest GitHub-owned nonblocking state/diagnostic consistent with current architecture.

Other unrelated hard validation failures remain blocking.

### B. Durable translation observability

Add GitHub-owned durable facts sufficient for Statistics to display:

- `untranslated_game_count` — current number of games in the relevant current publication/translation scope that do not have a valid accepted Russian translation;
- `last_translation_attempt_at`;
- `last_successful_translation_at`.

Use canonical field names consistent with the repository style if different names are preferable, but preserve these semantics.

The browser must not infer these dates from repository commit time, page load time, current payload age, or card contents.

### C. Exact timestamp semantics

`last_translation_attempt_at`:
- advances whenever the production translation stage actually reaches and executes a translation attempt/check for the current prepared work;
- includes a run that checks the current scope and finds zero games needing translation;
- advances whether the attempted translation work ultimately succeeds or fails.

`last_successful_translation_at`:
- advances when at least one translation is successfully accepted/persisted by the canonical translation path; OR
- advances when the translation stage completes its current check with zero games requiring translation;
- does NOT advance when work requiring translation was attempted but no translation was successfully accepted/persisted.

This allows the user to distinguish:
- attempt timestamp newer than success timestamp => translation was tried but did not produce a successful translation;
- equal/current timestamps with zero missing work => the translation stage ran and had nothing to translate.

If the current canonical architecture has multi-item partial success, preserve honest counts and do not erase unresolved items. The report must document the exact behavior chosen for partial success.

### D. Statistics UI block

Add one dedicated translation block to Statistics, visually aligned with the existing Statistics blocks.

It must display, in Russian:
- `Игр без перевода: N`
- a clear label for the last successful translation date/time;
- a clear label for the last translation-attempt date/time.

Do not implement these as unrelated standalone text rows outside the Statistics block system.

Use existing date/time formatting conventions. Handle never-attempted / no-history state explicitly rather than fabricating a date.

### E. Publication acceptance

After implementation:
- missing translations alone must no longer prevent a fresh full visual build;
- the canonical visual payload must carry the translation statistics/provenance needed by the UI;
- Pages publication must preserve unresolved translation state honestly;
- current browser assets must be eligible to reach Pages through the normal publication path once no other blocker exists.

Do NOT claim the site is fresh if a separate build/deploy problem remains.

## Concurrency with ЧАТ 1

ЧАТ 1 may be producing valid translation outputs concurrently.

Therefore:
- preserve all incoming translation/production writes;
- do not reset or replace current translation data with a stale snapshot;
- rebase/reconcile onto fresh `main` before merge;
- the implementation must work whether ЧАТ 1 finishes before, during, or after this task;
- do not require ЧАТ 1 to finish in order for missing translations to become nonblocking.

## Required regressions

At minimum cover:

1. one or more missing translations => visual build remains publishable and untranslated count is nonzero;
2. invalid/non-Russian text is still not accepted as Russian;
3. failed translation attempt => attempt timestamp advances, success timestamp does not;
4. successful accepted translation => both observable state and remaining untranslated count update correctly;
5. zero work => attempt and success semantics both reflect successful no-work completion;
6. partial success => unresolved count remains honest and timestamp behavior matches the documented rule;
7. Statistics renders the dedicated translation block with all three values;
8. browser does not invent timestamps/counts;
9. existing final visual/ranking/expiry/Fast/Dossier/Deep regressions remain green;
10. no scheduler/queue/retry ownership changes.

## Existing publication issues that must not be confused with this task

Current project history already contains:
- a stale-snapshot rebase-race diagnosis for `data/production/visual/current.json`;
- a proven case where Pages browser assets lagged behind `main`.

Do not reimplement unrelated expiry, ranking, Fast, Dossier, or Deep business logic.

This task may make the normal visual/publication route able to proceed despite untranslated games. If the separate stale-snapshot race or another independent publication defect still prevents fresh publication, report it precisely rather than broadening this task without Director authorization.

## Hard prohibitions

Do not:
- mark untranslated English/non-Russian source as Russian;
- weaken wrong-AppID, stale-binding, or provenance validation;
- hide or remove untranslated games just to pass publication;
- move translation authority into the browser;
- add another scheduler, queue, retry loop, or backlog owner;
- change ChatGPT Scheduled Tasks;
- modify Fast/Dossier/Deep semantic state;
- reimplement expired-sale or RANK-013 logic;
- manually translate production games in this task — that belongs to ЧАТ 1.

## Delivery

Implement on a dedicated branch/PR according to current worker protocol.

Preserve concurrent `main` changes and production data.

Merge only after required checks are green and current worker protocol permits merge.

Write:
`reviews/worker_reports/russian-translation-nonblocking-publication-statistics-01.md`

Required report sections:
1. `Task`
2. `Architecture preflight`
3. `Verified current blocker`
4. `Translation timestamp/count semantics`
5. `Changes`
6. `Statistics block`
7. `Validation`
8. `Publication observation`
9. `Unresolved`
10. `Status`
11. exact PR/commit/run refs
12. `Recommended next step` — exactly one bounded next step
13. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another project task after this one.
