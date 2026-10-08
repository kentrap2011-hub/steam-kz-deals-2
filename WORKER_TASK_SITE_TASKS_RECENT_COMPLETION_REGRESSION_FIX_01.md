# WORKER TASK — Site tasks recent-completion regression fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `IMPLEMENT / VALIDATE / NARROW FIX`

## Problem

Current `scripts/test_site_tasks.py` still hard-codes older recently-completed identities such as `deep-stage1` and `site-tasks`.

The public task page intentionally shows only a capped recent-completion block. Since newer tasks have completed, the current canonical top recent completions are newer entries. The stale assertions now fail on current `main`, causing `Validate site task registry and page` and real `Deploy visual mailing` runs to fail even though the registry itself is valid.

## Goal

Make the site-task regression tests validate the intended invariant rather than permanent historical IDs:
- the recent-completion block contains the correct newest eligible completed entries according to canonical timestamps and the documented cap;
- completed tasks remain present in the canonical registry even when they age out of the small recent-completion display;
- the full unfinished forward backlog remains complete;
- no historical task identity is permanently required to stay in the capped recent list.

## Required work

1. Read current:
   - `scripts/build_site_tasks.py`
   - `scripts/test_site_tasks.py`
   - `config/director_task_plan.json`
   - `web/tasks.js` / relevant task page tests
2. Confirm whether the builder is already correct.
3. If the builder is correct, change only brittle tests/fixtures.
4. If an actual builder defect is found, make the smallest compatible fix and explain it.
5. Run the full site-task validation plus relevant existing publication/UI regressions.
6. Prove a real `Deploy visual mailing` / Pages run succeeds on merged main if the task is merged.

## Boundaries

- Do not change task statuses, task ordering, or restore/remove product backlog entries.
- Do not change Deep, Dossier, Steam, translation, ranking, semantic workers, or production business logic.
- Do not create or change Scheduled Tasks / automations.
- Do not make the recent-completion block unbounded merely to satisfy tests.
- Do not hard-code a new set of current recent-completion IDs.

## Deliverable

Report:
`reviews/worker_reports/site-tasks-recent-completion-regression-fix-01.md`

Create a narrow PR and stop after validation. No next task.
