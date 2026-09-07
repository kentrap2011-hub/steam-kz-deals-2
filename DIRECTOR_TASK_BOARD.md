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

### Chat 1 — investigate why automatic ChatGPT analysis stopped
Task:
`WORKER_TASK_TASTE_DAILY_AUTOMATION_FAILURE_FORENSIC_RECON_01.md`
Expected report:
`reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
Mode: `READ-ONLY / RECON / FORENSIC`
Priority: `VERY_HIGH_RELIABILITY`
Status: `ready_fresh_chat_1`.

Purpose in plain terms:
- establish the last proven successful automatic ChatGPT analysis;
- determine what happened on the following daily cycles as far as retained evidence allows;
- determine whether the old automation was disabled/deleted/unavailable/failing, without guessing if history cannot prove it;
- explain why unresolved games accumulated for days without an alert;
- identify the missing one-day health/alarm rule;
- determine whether this is actually the same root cause as stale paid-list publication or a separate failure whose effects compounded.

No repair or automation state change in this task.

### Chat 2 — confirm replacement ChatGPT automation is currently off
Task:
`WORKER_TASK_TASTE_SINGLETON_DISABLED_STATE_CONFIRM_01.md`
Expected report:
`reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
Mode: `READ-ONLY / CONTROL-PLANE CONFIRMATION`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_2`.

Exact existing task:
- title `Taste Semantic Producer`;
- task id `6a9d6fdddc00819193ed670d782045c4`;
- generation `1`.

Purpose in plain terms:
confirm only whether this exact existing automation is currently disabled before any future one-game test. Do not change its state and do not run a test.

## Paid-list publication repair
Forensic report is complete and repair is understood, but repair launch is temporarily held while Chat 1 investigates the deeper automatic-ChatGPT failure raised by the user.

Prepared repair task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Status: `needs_bounded_task_correction_before_launch`.

The correction will reuse the existing safe commercial refresh helper, connect it to the existing visual publication workflow, preserve old semantic analysis safely, preserve giveaways, and add proof that paid prices/discounts actually caught up. No second scheduler/writer.

## Taste current state
The deal-rule bug that previously stopped deterministic preparation has been fixed and verified. Fresh prepared data is now saved and aligned with the current mailing source. Old Prototype result was not reused.

A fresh one-game ChatGPT test is still forbidden until Chat 2 positively confirms the exact existing replacement task is disabled.

## Publication freshness recurrence postmortem
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Status: `queued_after_main_list_refresh_recovery`.

This remains required after repair to compare giveaway failure, paid-list failure, and the automatic ChatGPT failure, then define one systemic prevention package.

## Giveaway publication
User verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. User launches fresh Chat 1 with the automatic-analysis failure forensic task.
2. User launches fresh Chat 2 with the exact disabled-state confirmation task.
3. Director consumes both exact reports and explains results in plain Russian before issuing any further worker command.
