# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not infer that a newly assigned worker task has actually been launched merely because the task command was prepared. Treat a slot as running only after the user says the new chat was created/sent the task or provides equivalent confirmation.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.
- All future non-trivial worker tasks must obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`: create the exact report path early with `in_progress`, checkpoint it before long verification, and never claim completion before the report is committed and re-read from `main`.
- Every user-facing worker closeout must obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`: explain in ordinary Russian what was wrong, what the worker actually did, why, what succeeded, what remains unresolved, and what the next stage is and why. Internal technical labels are never a substitute for explanation.

## Current worker slots

### Chat 1 — automatic ChatGPT analysis failure investigation DURABLY CLOSED
Task:
`WORKER_TASK_TASTE_DAILY_AUTOMATION_FAILURE_FORENSIC_RECON_01.md`
Report:
`reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
Final status: `complete_root_cause_bounded`.

Plain result:
- last proven accepted automatic ChatGPT analysis was 2026-09-01 21:03 UTC / 2026-09-02 01:03 Europe/Samara;
- it accepted 11 game results and reduced unresolved work 37 -> 26;
- by the next expected daily cycle, GitHub had successfully prepared fresh work with 644 unresolved items, but no normal ChatGPT output arrived;
- the break is at the external ChatGPT automation stage, not Steam collection or data preparation;
- retained evidence cannot prove whether the old scheduled task failed, did not run, was disabled, was deleted, became inaccessible, or hit another platform-side state;
- no automatic rule existed that turned “fresh unresolved work exists but no accepted ChatGPT progress by the daily deadline” into an incident;
- stale paid-list publication and ChatGPT-analysis outage are separate primary failures that later compounded each other.

Chat 1 result is durable. This worker chat can be deleted.

### Chat 2 — replacement ChatGPT automation state check DURABLY CLOSED
Task:
`WORKER_TASK_TASTE_SINGLETON_DISABLED_STATE_CONFIRM_01.md`
Report:
`reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
Final status: `blocked_state_unavailable`.

Plain result:
- worker could not reliably prove whether exact replacement ChatGPT automation `6a9d6fdddc00819193ed670d782045c4` is currently on or off;
- worker changed nothing and ran no game test;
- therefore one-game testing is still not authorized because we cannot rule out an overlapping run.

Chat 2 result is durable. This worker chat can be deleted.

## Paid-list publication repair
Forensic report is complete and repair is understood. The repair is still pending a bounded task correction before launch.

Prepared repair task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Status: `needs_bounded_task_correction_before_launch`.

## Taste current state
The data-preparation bug that previously blocked the pipeline has been fixed and verified. Fresh prepared data is saved and aligned with the current mailing source. Old Prototype result was not reused.

A fresh one-game ChatGPT test is still held only because the current on/off state of the exact replacement automation is not authoritatively known. User can inspect the task state in ChatGPT Scheduled without changing it.

## Publication freshness recurrence postmortem
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Status: `queued_after_main_list_refresh_recovery`.

## Giveaway publication
User verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Obtain authoritative current on/off state of exact replacement ChatGPT task `6a9d6fdddc00819193ed670d782045c4`, preferably from the user's Scheduled UI if tool-side state remains unreadable.
2. If confirmed off, prepare exactly one one-game test using the same existing task; if confirmed on, do not overlap runs and decide whether to pause it first.
3. Separately correct and run the paid-list publication repair so fresh prices/discounts do not depend on ChatGPT analysis completion.
4. After recovery and user verification, run the required cross-incident reliability postmortem and add automatic first-day failure detection.
