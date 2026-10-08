# Worker report — Site tasks recent-completion regression fix 01

- Task: `WORKER_TASK_SITE_TASKS_RECENT_COMPLETION_REGRESSION_FIX_01.md`
- Source of truth: `main`; narrow fix branch: `fix/site-tasks-recent-completion-regression-01`.
- Scope: test/fixture expectations for the capped recent-completion task display only.
- Status: implementation complete; focused PR CI validated; post-merge Pages confirmation is a separate gate.

## Root cause and canonical behavior

The builder `scripts/build_site_tasks.py::build_payload()` is already correct: it selects only `status=complete` and `recent_completion=true` records, orders them by precise normalized UTC `updated_at_utc` (with deterministic ID tie-break) and publishes at most three. Its `task_titles` still preserves **all** registry entries and `known_forward_count` covers **all** unfinished entries. The browser `web/tasks.js` consumes those groups and correctly excludes the small completed group from forward counts.

At investigation time `config/director_task_plan.json` had 28 canonical entries: 19 unfinished and 9 completed. The three newest eligible completed IDs were `dossier-throughput-audit`, `historical-backlog-audit`, `deep-ranking`; older IDs such as `site-tasks` and `deep-stage1` rightly aged out of the displayed three. Prior test assertions incorrectly required historical completions to remain visible and assumed `deep-ranking` remained planned / `deep-site` was unassigned.

## Exact change

Only `scripts/test_site_tasks.py` changed. Assertions now derive the expected forward set and latest eligible completions from the actual canonical plan, enforce the cap and precise order, require all canonical titles to remain present, and check that an artificial newer completion displaces the oldest displayed entry without losing registry or forward coverage. A controlled same-day fixture makes timestamp order disagree with lexical ID order, guarding against date-only sorting. Existing negative and UI/safety checks remain.

No generator, plan, task status, task order, UI implementation, publication workflow, Deep, Dossier, Steam, ranking, automation or production semantic contract changed.

## Validation and acceptance

- CI workflow `Validate site task registry and page` executes Python syntax checks, `node --check web/tasks.js`, `node web/tasks.test.js`, the eleven `scripts/test_site_tasks.py` regressions and static build/validate round trip.
- The full publication workflow's additional existing UI regressions can only be truthfully marked passed after the appropriate GitHub Actions execution; a successful task-registry PR check alone does not prove a Pages deployment.
- **PR check outcome: PASS** for head `ac1060a5083660f29ff28317858135d37ebc7d71`: `Validate site task registry and page` run `37785564554` succeeded (11 Python tests, JavaScript UI test, syntax checks, build `forward=19`, validate round trip); `Validate backlog dispositions` run `37785564790` succeeded.
- **Before-fix main reproduction:** `Deploy visual mailing` run `37784813107` failed at `Run UI regressions` with four old Python assertions (`test_full_forward_backlog_and_mobile_nav`, `test_stage1_merged_and_next_deep_task_planned_with_full_backlog`, `test_closeout_does_not_evict_recent_deep_stage1`, `test_recent_completion_uses_precise_time_not_same_day_id`). Its subsequent static tasks generation / Pages steps were skipped. PR check now passes those replacement invariants.
- **Actual merged-main `Deploy visual mailing` / Pages confirmation:** pending merge and later observed GitHub Actions result; this worker must not claim it before it happens.

## Ownership and boundaries

Architecture preflight: GitHub remains control-plane owner of the plan, deterministic builder, validations and static Pages publication; the interactive chat only proposes developer-side test changes. No workflow, recurring responsibility, runtime/scheduler, queue, retry, checkpoint, semantic-worker authority or Scheduled Task has changed.

## Continuation — lifecycle assertions after PR #170 merged (2026-10-08)

PR #170 is merged and the initial capped-recents fix is accepted. Subsequent canonical plan updates following merged Deep site PR #168 exposed two further historical assertions, both in `test_full_forward_backlog_and_mobile_nav`: `deep-site` was permanently required in the forward set, and `deep-cutover` was permanently required to be `blocked`.

Verified current `main` canonical registry: `deep-site.status=complete`; `deep-cutover.status=planned`, with an empty blocker and the original four canonical dependencies. These are valid lifecycle transitions, not registry/builder defects.

Narrow follow-up `fix/site-tasks-lifecycle-regression-02`: in `scripts/test_site_tasks.py`, do not require those two mutable lifecycle IDs to be forever unfinished; instead compare display membership, status, dependencies and blocker against each task's **current canonical plan**. If a completed entry ages out of the three newest, it remains in `task_titles` rather than in rendered cards. All pre-existing all-forward coverage and safety invariants stay. No task registry/status, application logic, Deep/Dossier/Steam/ranking, workflow or Scheduled Task changed.

### Follow-up acceptance

- **Focused PR and CI:** pending.
- **Actual merged-main Pages deploy:** pending.
