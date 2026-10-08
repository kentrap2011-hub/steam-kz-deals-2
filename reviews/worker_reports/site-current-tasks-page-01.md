# Worker report — site current tasks page 01

**Repository:** `kentrap2011-hub/steam-kz-deals-2`  
**Source of truth:** `main`; implementation on `implement/site-current-tasks-page-01`  
**Task:** `WORKER_TASK_SITE_CURRENT_TASKS_PAGE_01.md`  
**Date:** 2026-10-08  
**Status:** `implementation_complete_ready_for_director_acceptance` (PR validation complete; deployment awaits merge)

## Result

Implemented a separate mobile/desktop Russian **Задачи проекта** page at `web/tasks.html`, reachable from the site's top navigation. It displays the **full currently known forward plan**, not just assigned workers or the nearest queue entries. It separates *В работе / Запланировано / Ожидает / заблокировано*; a tiny recently completed block is optional and currently contains two recent entries.

The canonical machine-readable companion `config/director_task_plan.json` contains **24 known task entries: 6 active + 11 planned + 3 blocked + 4 completed** (20 unfinished forward tasks). Planned entries include unassigned items from the product queue, the frozen Deep integration map, the later queue, and follow-ups recorded in Director state. Every item carries the short Russian goal, status, optional worker slot, known ordering/priority, dependency/blocker when known, **трудоёмкость** with reason, **срочность** with reason, and a per-task update timestamp. The page displays the actual plan-curation date and the generated site-snapshot timestamp separately, highlighting when the plan becomes stale.

Completed historical Director archive sections are **not** projected as outstanding tasks. The rejected first-wave/reserve semantic gating is **not** revived. The superseded publication-freshness sentinel does **not** enter the forward backlog.

## Publication and architecture boundaries

- `scripts/build_site_tasks.py` generates the minimal allowlisted public static payload `web/data/tasks.json` only during the **existing** `.github/workflows/deploy-visual.yml` Pages job.
- The browser consumes static JSON; it does not call GitHub APIs, parse long Board prose, compute business eligibility, or manage the task list.
- `DIRECTOR_TASK_BOARD.md` points to the single structured companion; Director/task edits must maintain Board's current sections and registry **together**. The validator rejects missing task references from the forward Board lanes and frozen `config/deep_two_stage_dependency_map.json`, unknown dependencies, cycles, duplicate ordering, invalid/unsafe public fields and missing task artifacts.
- `PROJECT_ROUTES.md` documents the bounded route to registry, validator, UI and Pages.
- No new scheduler, recurring worker, ChatGPT Scheduled Task, semantic engine, Steam/Deep queue, scoring, ranking or production data mutation was added. Discount cards/statistics were not changed beyond the added navigation link.

## Tests and checks

- **Validate site task registry and page**: Actions run **37765202110** — **success** at implementation commit `41de0d1a08d7bd6d6ae83c8e41f727785d8dd1ec` (before report-only closeout).
  - `python -m py_compile scripts/build_site_tasks.py scripts/test_site_tasks.py`
  - `node --check web/tasks.js`
  - `node web/tasks.test.js`
  - `python scripts/test_site_tasks.py`: full known forward backlog, unassigned/later task retention, Deep integration dependencies, malformed/private fields and graph regressions.
  - `python scripts/build_site_tasks.py --output /tmp/site-tasks.json`
  - `python scripts/build_site_tasks.py --validate-current /tmp/site-tasks.json`
- Existing PR checks at the same head: **Validate site publication resilience** run **37765201944**, **Validate package purchase value** **37765201923**, **Validate backlog dispositions** **37765202175**, **Validate Progressive PASS 2 core** **37765202252** — all **success**.
- Initial site-tasks check **37765048852** exposed an incorrect inclusion of the Board's explicitly **superseded** publication-freshness task; the forward-section parser was corrected to omit explicit superseded/cancelled lines. Later check **37765202110** passed.
- Current PR **#162**, `implement/site-current-tasks-page-01` -> `main`: open and mergeable when last checked.

## Remaining acceptance boundary

No claim of deployed/live Pages verification: PR #162 has **not** been merged into `main`. After Director accepts and merges the PR, the existing Pages workflow will generate/deploy `data/tasks.json`; normal live site acceptance should confirm the `Задачи` navigation and timestamp. During Director closeout, mark `site-tasks` complete in `config/director_task_plan.json` (and align current Board) as a subsequent state update, not by pretending this PR is already live.

**Stop boundary:** this worker does not implement any other project task.
