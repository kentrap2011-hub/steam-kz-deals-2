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

## Current two worker slots

### Chat 1 — automatic ChatGPT analysis failure forensic complete, report status needs correction
Task:
`WORKER_TASK_TASTE_DAILY_AUTOMATION_FAILURE_FORENSIC_RECON_01.md`
Report:
`reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
Mode: `READ-ONLY / RECON / FORENSIC`
Priority: `VERY_HIGH_RELIABILITY`
Status: `substantive_complete_report_status_malformed`.

Plain result:
- last proven accepted automatic ChatGPT analysis was 2026-09-01 21:03 UTC / 2026-09-02 01:03 Europe/Samara;
- it accepted 11 game results and reduced the unresolved queue 37 -> 26;
- by the next expected daily cycle, GitHub had successfully prepared a fresh current scope with 644 unresolved items, but no normal ChatGPT output arrived for ingest;
- therefore the first missed cycle is located at the external ChatGPT automation stage, not at Steam data collection, deterministic preparation, or ingest of a produced result;
- repository evidence cannot prove whether the old ChatGPT scheduled task ran and failed, did not run, was disabled, was deleted, became inaccessible, or hit another platform-side state; exact historical scheduler cause remains unreconstructible and must not be guessed;
- the system failed to alert because no durable rule existed at the time that treated “fresh unresolved work exists but no accepted ChatGPT progress by the daily deadline” as an incident;
- paid-list staleness and ChatGPT-analysis outage are separate primary failures that later compounded each other: the paid-list publication problem began earlier, while the later ChatGPT outage prolonged the stale state by preventing full rebuilds.

Report contract issue:
- task required final status exactly `complete_root_cause_bounded` or `blocked`;
- report used `complete_read_only_forensic_recon` instead;
- existing Chat 1 must only correct final status to `complete_root_cause_bounded`, re-read the same report, and stop.

Do not delete Chat 1 until this report-only correction is persisted.

### Chat 2 — replacement ChatGPT automation state check needs report-status correction
Task:
`WORKER_TASK_TASTE_SINGLETON_DISABLED_STATE_CONFIRM_01.md`
Report:
`reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
Mode: `READ-ONLY / CONTROL-PLANE CONFIRMATION`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `result_state_unavailable_report_status_malformed`.

Plain result:
- worker could not reliably see whether exact task `6a9d6fdddc00819193ed670d782045c4` is currently on or off;
- worker did not change task state and did not run a game test;
- therefore Director must not authorize the one-game test yet.

Report contract issue:
- task required one of `complete_confirmed_disabled`, `complete_found_enabled`, `blocked_state_unavailable`;
- report used `verified` instead;
- existing Chat 2 must only correct the final status to `blocked_state_unavailable`, re-read the same report, and stop.

Do not delete Chat 2 until this report-only correction is persisted.

## Paid-list publication repair
Forensic report is complete and repair is understood. Launch remains held until Director converts the now-known combined incident picture into the next bounded repair/reliability order.

Prepared repair task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Status: `needs_bounded_task_correction_before_launch`.

## Taste current state
The data-preparation bug that previously blocked the pipeline has been fixed and verified. Fresh prepared data is saved and aligned with the current mailing source. Old Prototype result was not reused.

A fresh one-game ChatGPT test is still forbidden because current on/off state of the exact replacement automation is not authoritatively known.

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
1. Existing Chat 1 only corrects its report final status to `complete_root_cause_bounded` and stops.
2. Existing Chat 2 only corrects its report final status to `blocked_state_unavailable` and stops.
3. After both report-only corrections, Director chooses the next bounded implementation order using the combined evidence: restore reliable daily ChatGPT execution/alerting and repair independent paid-list publication without conflating the two failures.
