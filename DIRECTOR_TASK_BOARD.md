# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, reconcile current Board -> exact task -> exact preceding report.
- Worker completion means exact durable report is final, not merely that the chat response ended.
- All non-trivial workers obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- All user-facing closeouts obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`.

## Closed worker results

### Paid-list repair — USER VERIFIED CLOSED
Task: `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Report: `reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Result: fresh paid prices/discounts now publish independently of unfinished ChatGPT semantic analysis.
User verification: stale/non-current discounts disappeared and the paid update date advanced.

### Completed Taste task reuse recon — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report: `reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Result: same-id reuse/reactivation of old completed task was not proven.
User evidence establishes existing old `Taste Semantic Producer` is `Completed`, Date/Time are not editable, and ChatGPT Scheduled filter `Active` is empty.
Old identity remains:
- task id `6a9d6fdddc00819193ed670d782045c4`;
- producer `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- generation `1`.
Do not delete old completed task yet.

### Silent-stall prevention postmortem — DURABLY CLOSED
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Report: `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Final status: `complete_reliability_action_required`.
User declined the proposed independent 03:15 watchdog. Date-only freshness visibility remains selected policy.

### Taste active producer restore design — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
Report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
Final status: `complete_restore_plan_ready`.
Accepted design: preserve old completed task; create exactly one new recurring daily Scheduled Task; migrate producer identity to new task id/generation 2; first run limited to one fresh game; same task remains active but canary-locked until independent System Audit PASS; no paid API/Copilot/external scheduler.
Old design worker chat can be deleted.

## ACTIVE — Taste producer restore implementation
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
Expected report: `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
Mode: `IMPLEMENT / CONTROL-PLANE + CONTRACT MIGRATION + CANARY ARMING`
Status: `running`.

User confirmed the implementation command was sent to NEW Chat 1.

Implementation scope:
- create exactly one new recurring ChatGPT Scheduled `Taste Semantic Producer`;
- keep old completed task untouched;
- select exactly one fresh current game for the first test;
- bind the new task to that one game only, no fallback;
- capture new immutable task id and move canonical producer identity to generation 2;
- validate new identity accepted and old generation-1 identity rejected;
- leave the same new task active and recurring but canary-locked/no-op after first success;
- do not widen to normal backlog processing;
- independent System Audit required before widening;
- zero separately billed OpenAI API/Copilot/external automation cost.

Do not inspect intermediate implementation state from Director. Consume only the exact durable report after the user says the worker finished.

## Superseded watchdog implementation
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md`
Status: `SUPERSEDED_BY_USER_DECISION_DO_NOT_RUN`.
Do not launch it.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Wait for user to say Chat 1 finished.
2. Then fetch only `reviews/worker_reports/taste-active-producer-restore-implement-01.md`.
3. If canary is armed or accepted successfully, run independent System Audit before widening the same task.
