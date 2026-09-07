# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from old chat history alone.
- A worker response cycle ending does not mean its task is durably complete; consume the exact report first.
- All non-trivial workers must obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- Every user-facing closeout must obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md` and explain results in ordinary Russian before technical names.

## Current worker slots

### Chat 1 — paid-list repair response cycle ended, task NOT yet durably complete
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Report:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Report status: `in_progress`.

Plain current state:
- worker confirmed the repair target and existing safe helper;
- worker confirmed Steam collection and the upstream daily data path are not the thing to change;
- actual bounded production wiring, final runtime acceptance, publication proof, and deploy verification are still listed as pending in the report;
- therefore the response cycle ended before the task was finished.

Required action:
- keep the SAME Chat 1;
- do not restart investigation;
- continue only the unfinished implementation/acceptance items already listed in the report;
- update this same report to one of the task's allowed final statuses and re-read it from `main` before closing.

Chat 1 must NOT be deleted yet.

### Chat 2 — completed-task reuse recon DURABLY CLOSED
Task:
`WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report:
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Final status: `blocked_same_id_reuse_unproven`.

Plain result:
- generic ChatGPT product behavior supports rescheduling/editing existing finished tasks;
- worker could not prove exact-id targeting from its read-only control plane;
- no state was changed, no task was created, and no game analysis was run.

Chat 2 worker result is durable. This worker chat can be deleted.

## User control-plane observation for existing Taste Scheduled Task
On 2026-09-07 the user opened the existing completed `Taste Semantic Producer` from ChatGPT Scheduled on Android/web mobile and provided screenshots.

Observed directly:
- task title displayed: `Taste Semantic Producer`;
- state displayed: `Завершено` / `Completed`;
- the task has not been deleted;
- inside the existing task detail panel, under `ПЕРИОДИЧНОСТЬ`, the same card exposes `Дата` and `Время` controls with dropdown indicators (currently showing the prior Sep 6 canary date/time).

Operational conclusion:
- a separate worker is no longer needed merely to discover whether the visible existing task offers in-place schedule controls: the user UI demonstrably exposes them on that existing completed task card;
- this does NOT prove that the mobile UI exposed the immutable backend jawbone id, so do not claim the screenshot itself proves exact id equality;
- do not create a replacement `Taste Semantic Producer`;
- do not delete the existing task.

## Taste next gate
A fresh one-game canary is still NOT started yet.
Reason: Chat 1 is currently finishing a production paid-list publication repair. A semantic canary could also cause downstream production activity and would make acceptance evidence harder to separate while Chat 1 is changing/validating the visual publication workflow.

After Chat 1 reaches a durable final result, Director may authorize a one-time reschedule of this same visible completed `Taste Semantic Producer` through its existing Date/Time controls for exactly one fresh current game, with no new task and no second semantic row until Director review.

## Paid-list publication repair
Still active in Chat 1. Do not call the incident repaired until the same report reaches a final accepted status and the user verifies the site on Android if worker acceptance says it is ready.

## Publication freshness recurrence postmortem
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Status: `queued_after_main_list_refresh_recovery`.

This remains mandatory after recovery to add first-day detection for silent failures and compare the giveaway, paid-list, and ChatGPT-analysis incidents.

## Giveaway publication
User already verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route remains prohibited unless the user explicitly reverses that policy.

## Next decision
1. Existing Chat 1 finishes its current paid-list repair and finalizes the same report.
2. Chat 2 may be deleted; no replacement Chat 2 is needed merely to inspect the schedule UI.
3. Do not change Date/Time on `Taste Semantic Producer` while Chat 1 repair acceptance is still in progress.
4. After Chat 1 final report is consumed, prepare the exactly-one-game canary and tell the user the exact one-time Date/Time to set on this same task card.
5. Do not create or delete any Taste Scheduled Task.
