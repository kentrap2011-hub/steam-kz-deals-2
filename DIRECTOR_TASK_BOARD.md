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

### Chat 2 — completed-task reuse recon DURABLY CLOSED, but same-id reuse remains unproven
Task:
`WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report:
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Final status: `blocked_same_id_reuse_unproven`.

Plain result:
- generic ChatGPT product behavior supports rescheduling/editing existing finished tasks;
- however the worker could not prove that the exact existing task id `6a9d6fdddc00819193ed670d782045c4` can currently be targeted in place;
- no state was changed, no task was created, and no game analysis was run;
- therefore a fresh one-game test is still not authorized;
- the existing `Taste Semantic Producer` task must be preserved and not deleted.

Chat 2 worker result is durable. This worker chat can be deleted.

## User control-plane observation for Taste Scheduled Task
On 2026-09-07 the user showed the `Taste Semantic Producer` task in Android ChatGPT Scheduled:
- displayed state `Завершено` / `Completed`;
- no pending next run shown;
- menu only showed notification settings and delete;
- user has not deleted it.

This clears the earlier overlap concern that it might currently be running, but does not by itself prove that the immutable task id can be reactivated in place.

## Taste next gate
Before any fresh one-game test, the project needs one explicitly authorized control-plane step that can demonstrate an in-place operation against exact task id `6a9d6fdddc00819193ed670d782045c4` without creating a replacement task. If exact-id targeting cannot be demonstrated, stop and redesign rather than creating a second task.

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
2. Chat 2 may be deleted.
3. After explicit authorization, a fresh Chat 2 may perform the narrow exact-id in-place control-plane proof for the completed `Taste Semantic Producer`; no canary yet unless same-id reuse is proven.
4. Consume both durable results independently before any wider rollout.
