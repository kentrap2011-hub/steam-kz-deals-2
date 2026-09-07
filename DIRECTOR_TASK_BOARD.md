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

### Chat 1 — previous investigation DURABLY CLOSED / NEW TASK PREPARED, NOT YET LAUNCHED
Previous task:
`WORKER_TASK_TASTE_DAILY_AUTOMATION_FAILURE_FORENSIC_RECON_01.md`
Previous report:
`reviews/worker_reports/taste-daily-automation-failure-forensic-recon-01.md`
Final status: `complete_root_cause_bounded`.

The old Chat 1 can be deleted.

Next Chat 1 task prepared:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Status: `prepared_awaiting_user_launch`.

The required forensic bounded correction has now been applied to the task. Repair target is only the missing deterministic `commercial_only` visual handoff. Healthy Steam -> shortlist -> mailing must not be changed, existing `scripts/refresh_visual_commercial_fields.py` must be reused, giveaway state preserved, scoped commercial freshness proof added, and the full semantic ChatGPT-completion fail-closed guard retained unchanged.

### Chat 2 — previous state check DURABLY CLOSED / NEW TASK PREPARED, NOT YET LAUNCHED
Previous task:
`WORKER_TASK_TASTE_SINGLETON_DISABLED_STATE_CONFIRM_01.md`
Previous report:
`reviews/worker_reports/taste-singleton-disabled-state-confirm-01.md`
Final worker status: `blocked_state_unavailable`.

The old Chat 2 can be deleted.

Next Chat 2 task prepared:
`WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Expected report:
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Status: `prepared_awaiting_user_launch`.

Purpose: read-only proof whether the exact completed singleton task id `6a9d6fdddc00819193ed670d782045c4` can be reused/reactivated for a future one-game canary without creating a second Scheduled Task identity. No mutation and no canary in this task.

## Taste Scheduled Task user control-plane confirmation
On 2026-09-07 the user inspected ChatGPT Scheduled on Android and showed the `Taste Semantic Producer` card.
Observed directly in the user UI:
- task title: `Taste Semantic Producer`;
- state label: `Завершено` (`Completed`);
- visible saved result is the known Prototype `App_10150` canary attempt, matching the retained singleton history;
- the task menu exposes only notification settings and delete, with no active pause control or pending-run indication.

Director conclusion for the overlap-safety gate:
- the displayed singleton is not currently active/running and has no next automatic run indicated;
- the risk gate that previously blocked a fresh one-game canary solely because on/off state was unknown is cleared;
- the Scheduled Task itself MUST NOT be deleted, because the project requires preserving the one existing singleton identity and forbids creating a second producer/task/generation.

Important bounded uncertainty:
- the immutable task id is not displayed in this mobile UI, so do not claim the UI exposed the id directly;
- before the fresh canary is launched, confirm the same completed task can be reused/reactivated without creating a replacement task id.

## Paid-list publication repair
Forensic report:
`reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
Final status: `complete_ready_for_repair`.

Prepared repair task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Status: `prepared_awaiting_user_launch`.

## Taste current state
The data-preparation bug that previously blocked the pipeline has been fixed and verified. Fresh prepared data is saved and aligned with the current mailing source. Old Prototype result was not reused.

A fresh one-game test is not yet launched. The remaining pre-canary safety question is whether the exact completed singleton can be reused/reactivated without creating a second task identity. That question now has a dedicated read-only recon task.

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
1. User may delete the old completed worker chats Chat 1 and Chat 2. Do NOT delete the Scheduled Task `Taste Semantic Producer`.
2. Launch a fresh Chat 1 with `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`.
3. Launch a fresh Chat 2 with `WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`.
4. Consume each exact durable report independently before assigning further work.
5. If paid-list repair reaches `complete_ready_for_user_verification`, require user Android/site verification before calling that incident closed.
6. If same-id Taste reuse is proven, prepare a separate explicitly authorized exactly-one-game canary using that same singleton; do not create a replacement task.
7. After paid-list recovery/user verification, run the queued cross-incident reliability postmortem and add automatic first-day failure detection.
