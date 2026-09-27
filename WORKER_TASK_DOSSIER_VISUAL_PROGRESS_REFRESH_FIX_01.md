# WORKER TASK — DOSSIER VISUAL PROGRESS REFRESH FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2` for this task;
- do not search, read, modify, or use another repository;
- if GitHub/tool opens another repository by default or the target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `dossier-visual-progress-refresh-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/dossier-visual-progress-refresh-fix-01.md`

## User-approved goal

Fix the site statistics refresh so accepted/current Dossier progress is reflected in the published visual statistics automatically.

Observed user symptom:
- the site showed Dossier statistics as `Готово 0 / Ожидает 444`;
- current canonical Dossier state had already advanced beyond zero accepted dossiers.

The Director previously inspected implementation details directly. Do not treat that conversational diagnosis as canonical truth. Re-prove the exact cause from fresh `main` before changing anything.

## Architecture constraints already confirmed by Director

Canonical contracts say:
- GitHub owns aggregate processing counts, downstream orchestration, visual rebuild triggering, validation, persistence and publication;
- the browser/site is a read-only consumer of prepared visual data;
- Scheduled ChatGPT remains only bounded semantic data-plane work;
- this fix must not create a new scheduler, queue, retry loop, recurring stage or browser-side business logic;
- no Scheduled Task configuration change is authorized.

These are constraints, not an implementation prescription. Worker must still perform the required architecture preflight from current canonical files before writes.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully and make the required task checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. relevant route(s) in `PROJECT_ROUTES.md`, especially Fast / Dossier / Deep and visual publication routes;
3. `config/execution_ownership_contract.json`;
4. `config/daily_execution_contract.json`;
5. `config/progressive_personalization_contract.json`;
6. `config/taste_steam_review_dossier_contract.json`;
7. only the exact visual/Dossier workflow or producer files needed to prove and fix the defect.

Do not reconstruct unrelated project history.

## Required diagnosis

Before implementation, prove all of the following from fresh `main`:

1. What exact canonical Dossier state currently contains the accepted/pending/failed counts.
2. What exact artifact the statistics page actually reads.
3. What component computes/stamps Dossier statistics into that artifact.
4. What event currently causes that artifact to rebuild and deploy.
5. Why a successful canonical Dossier progress update can leave the published statistics stale.
6. Whether the defect is only a missing rebuild/activation trigger, or whether another stale-binding/publication problem also exists.

If the Director's provisional cause is wrong or incomplete, do not force the assumed fix. Implement the smallest correct fix supported by current architecture.

## Implementation requirements

Implement the smallest GitHub-owned change that makes canonical Dossier progress propagate automatically to the published statistics.

The fix must:
- preserve GitHub as the control-plane owner;
- keep the browser read-only;
- reuse existing visual production/publication architecture where possible;
- update statistics after relevant canonical Dossier progress changes without requiring the user to manually rebuild the site;
- avoid fresh Steam/SteamDB/web/commercial collection merely because Dossier progress changed;
- avoid starting semantic Dossier/Deep/Fast work from the browser;
- not create a second independent scheduler or recurring pipeline;
- not change Scheduled Task settings;
- not alter Dossier semantic rules, recovery rules, snapshot identity, or current production data merely to demonstrate the fix;
- preserve existing visual freshness/fail-closed protections.

If the correct minimal solution requires amending a canonical contract because current contracts do not authorize the required trigger, update the contract first and explain why. Do not silently bypass it.

## Parallel-work guard

Another worker may still be running a READ-ONLY stale-snapshot reconciliation in `ЧАТ 1`.

This task may proceed in parallel only while:
- it does not modify that worker's task/report;
- it does not perform old-snapshot recovery/reconciliation;
- it does not mutate production Dossier state;
- any source/workflow file is re-read immediately before modification.

If a direct write conflict is detected, stop and report it instead of overwriting concurrent work.

## Validation

Provide focused regression coverage proving at minimum:

1. A current Dossier progress change that increases accepted dossiers causes the visual processing statistics to be rebuilt from canonical state.
2. The published/statistics artifact contains the updated Dossier counts rather than the prior stale counts.
3. The update path does not require a new semantic run, Scheduled Task change, or browser computation.
4. Existing Fast/Deep visual update behavior remains intact.
5. The normal visual/deploy freshness guards still pass.
6. No production Dossier candidate/recovery state was manually altered for the test.

Use the strongest bounded validation available in the repository. If full end-to-end deploy cannot be safely proven without a user action, state the exact remaining acceptance step rather than declaring full completion.

## Hard prohibitions

Do not:
- run or modify any ChatGPT Scheduled Task;
- trigger manual Dossier/Deep/Fast semantic production for validation;
- recover old `g000001`;
- rewrite or delete old snapshot artifacts;
- change current Dossier semantic evidence policy;
- move progress calculation into frontend JavaScript;
- add a new recurring workflow merely to refresh statistics;
- process backlog manually;
- alter unrelated UI design/copy.

## Report

Write only the durable report:
`reviews/worker_reports/dossier-visual-progress-refresh-fix-01.md`

It must contain:
1. `Task`
2. `Verified facts`
3. `Root cause`
4. `Changes`
5. `Validation`
6. `Unresolved`
7. `Status`
8. `Recommended next step` — exactly one bounded next step
9. exact PR/commit/run/file refs
10. `Efficiency / reusable lesson` — `none` unless a genuine route/pitfall candidate was found

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another project task after this one.

## Expected next step

Director reads the compact report and performs acceptance. If implementation is proven and merged, Director decides whether a one-time user refresh/site check is still needed.
