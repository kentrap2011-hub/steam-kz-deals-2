# Worker report — Site tasks recent-completion regression fix 01

- Task: `WORKER_TASK_SITE_TASKS_RECENT_COMPLETION_REGRESSION_FIX_01.md`
- Source of truth: `main`; narrow fix branch: `fix/site-tasks-recent-completion-regression-01`.
- Scope: test/fixture expectations for the capped recent-completion task display only.
- Status: implementation complete; PR CI validation and post-merge Pages confirmation are separate gates.

## Root cause and canonical behavior

The builder `scripts/build_site_tasks.py::build_payload()` is already correct: it selects only `status=complete` and `recent_completion=true` records, orders them by precise normalized UTC `updated_at_utc` (with deterministic ID tie-break) and publishes at most three. Its `task_titles` still preserves **all** registry entries and `known_forward_count` covers **all** unfinished entries. The browser `web/tasks.js` consumes those groups and correctly excludes the small completed group from forward counts.

At investigation time `config/director_task_plan.json` had 28 canonical entries: 19 unfinished and 9 completed. The three newest eligible completed IDs were `dossier-throughput-audit`, `historical-backlog-audit`, `deep-ranking`; older IDs such as `site-tasks` and `deep-stage1` rightly aged out of the displayed three. Prior test assertions incorrectly required historical completions to remain visible and assumed `deep-ranking` remained planned / `deep-site` was unassigned.

## Exact change

Only `scripts/test_site_tasks.py` changed. Assertions now derive the expected forward set and latest eligible completions from the actual canonical plan, enforce the cap and precise order, require all canonical titles to remain present, and check that an artificial newer completion displaces the oldest displayed entry without losing registry or forward coverage. A controlled same-day fixture makes timestamp order disagree with lexical ID order, guarding against date-only sorting. Existing negative and UI/safety checks remain.

No generator, plan, task status, task order, UI implementation, publication workflow, Deep, Dossier, Steam, ranking, automation or production semantic contract changed.

## Validation and acceptance

- CI workflow `Validate site task registry and page` executes Python syntax checks, `node --check web/tasks.js`, `node web/tasks.test.js`, the eleven `scripts/test_site_tasks.py` regressions and static build/validate round trip.
- The full publication workflow's additional existing UI regressions can only be truthfully marked passed after the appropriate GitHub Actions execution; a successful task-registry PR check alone does not prove a Pages deployment.
- **PR check outcome:** pending recording from GitHub Actions.
- **Actual merged-main `Deploy visual mailing` / Pages confirmation:** pending merge and later observed GitHub Actions result; this worker must not claim it before it happens.

## Ownership and boundaries

Architecture preflight: GitHub remains control-plane owner of the plan, deterministic builder, validations and static Pages publication; the interactive chat only proposes developer-side test changes. No workflow, recurring responsibility, runtime/scheduler, queue, retry, checkpoint, semantic-worker authority or Scheduled Task has changed.
