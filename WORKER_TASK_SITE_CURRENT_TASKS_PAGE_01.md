# WORKER TASK — Site current tasks page 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

## Mode
IMPLEMENT / VALIDATE after START gate and architecture preflight.

## User goal
Add a separate page to the site where the user can see the queue of **current project tasks**.

## Required page
Russian user-facing page, for example `Актуальные задачи`.

Show only current operationally useful task information:
- active tasks;
- queued tasks;
- blocked/waiting tasks when applicable;
- short plain-Russian goal;
- status;
- worker slot if assigned;
- dependency/blocker if one exists;
- last update time;
- **трудоёмкость**: низкая / средняя / высокая, with a short reason;
- **срочность**: критическая / высокая / обычная / низкая, with a short reason.

Do not dump historical completed-task archive onto this page. A small recently-completed section is optional only if it improves orientation.

## Source of truth
Do not make the browser call GitHub APIs and do not manually maintain a second independent task list.

The page must consume a static site payload generated from the repository's canonical Director/task state during the existing GitHub build/publication path.

If `DIRECTOR_TASK_BOARD.md` is not safely machine-readable enough, add the smallest canonical machine-readable companion source and make Director/task tooling update it together, rather than scraping arbitrary prose at runtime.

## Safety
Do not publish:
- secrets or tokens;
- private URLs;
- internal prompts;
- large diagnostic logs;
- personal identifiers not already intended for site display.

## Acceptance
- navigation reaches the new page on mobile and desktop;
- page clearly separates active / queued / blocked;
- every displayed task shows трудоёмкость and срочность with plain-Russian rationale;
- current queued Steam tasks appear after the queue entries are added;
- stale task payload is detectable through a visible update timestamp;
- existing discount cards/statistics remain unchanged except for navigation/task-page additions;
- existing Pages publication route is used;
- no new scheduler/recurring worker is created;
- durable report:
  `reviews/worker_reports/site-current-tasks-page-01.md`.
