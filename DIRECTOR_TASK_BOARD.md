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

Accepted design:
- preserve old completed task for provenance;
- restore via exactly one NEW recurring daily ChatGPT Scheduled Task;
- new immutable task id becomes canonical producer `chatgpt_scheduled_task:<NEW_TASK_ID>`;
- producer generation advances from 1 to 2;
- migrate only canonical producer fence identity fields in `config/taste_result_contract.json`;
- first scheduled run is a one-fresh-current-game canary using exact current binding tuple and no fallback;
- SAME recurring task remains Active after canary but canary-locked/no-op until independent System Audit;
- only after System Audit PASS may the SAME task be widened to normal daily Taste production;
- canonical normal cadence remains daily 01:00 Europe/Samara;
- no paid OpenAI API/Copilot/external automation service.

Old design worker Chat 1 can be deleted.

## Prepared implementation — NOT YET AUTHORIZED/LAUNCHED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
Expected report: `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
Mode: `IMPLEMENT / CONTROL-PLANE + CONTRACT MIGRATION + CANARY ARMING`
Status: `prepared_waiting_for_separate_user_approval`.

This implementation will materially mutate project/control-plane state by:
- creating exactly one new recurring ChatGPT Scheduled Task;
- capturing its immutable id;
- moving canonical Taste producer identity to generation 2;
- arming exactly one fresh canary;
- leaving old completed task untouched;
- requiring independent System Audit before any widening.

Do not mark running until user explicitly approves and confirms the command was sent/launched.

## Superseded watchdog implementation
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md`
Status: `SUPERSEDED_BY_USER_DECISION_DO_NOT_RUN`.
Do not launch it.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Ask user for explicit approval to launch `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`.
2. If approved, assign to NEW Chat 1.
3. After worker report, consume exact durable report only.
4. If canary accepted or armed successfully, require independent System Audit before widening the same task.
