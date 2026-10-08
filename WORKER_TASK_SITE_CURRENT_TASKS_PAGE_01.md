# WORKER TASK — Site current tasks page 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

## Mode
IMPLEMENT / VALIDATE after START gate and architecture preflight.

## User goal
Add a separate page to the site where the user can see **all current and planned project tasks**.

The page must not be limited to the tasks currently assigned to worker chats or only the next few queue entries. It must expose the full known forward plan currently recorded by the Director/project task state.

## Required page
Russian user-facing page, for example `Актуальные задачи`.

Show the full known forward task list:
- active tasks;
- **all planned tasks**, including tasks not yet assigned to a worker chat;
- queued tasks in their intended order when such order is known;
- blocked/waiting tasks when applicable;
- dependencies / prerequisites between planned tasks;
- short plain-Russian goal;
- status;
- worker slot if assigned;
- priority/order when known;
- dependency/blocker if one exists;
- last update time;
- **трудоёмкость**: низкая / средняя / высокая, with a short reason;
- **срочность**: критическая / высокая / обычная / низкая, with a short reason.

The user must be able to open this page and understand not only “what is being done now” but also **everything already planned next for the project**.

Do not silently omit lower-priority or later planned tasks merely because they are not in the immediate worker queue.

Do not dump the full historical completed-task archive onto this page. A small recently-completed section is optional only if it improves orientation.

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
- page clearly separates active / planned / blocked-waiting work;
- **the complete known planned backlog is visible, not only currently assigned or nearest tasks**;
- future tasks that are known but not yet assigned still appear with an appropriate status;
- intended order/priority and dependencies are visible where known;
- every displayed task shows трудоёмкость and срочность with plain-Russian rationale;
- current queued Steam tasks and the remaining planned Deep/site/project tasks appear from the canonical project plan;
- stale task payload is detectable through a visible update timestamp;
- existing discount cards/statistics remain unchanged except for navigation/task-page additions;
- existing Pages publication route is used;
- no new scheduler/recurring worker is created;
- durable report:
  `reviews/worker_reports/site-current-tasks-page-01.md`.
