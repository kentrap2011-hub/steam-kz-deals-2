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

## Superseded watchdog implementation
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md`
Status: `SUPERSEDED_BY_USER_DECISION_DO_NOT_RUN`.
Do not launch it.

## Immediate priority — restore automatic ChatGPT/Taste producer
There is currently no active recurring ChatGPT Scheduled Taste producer.
The user explicitly approved proceeding with restoration.

### Prepared next worker — NOT YET LAUNCHED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
Expected report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
Mode: `READ-ONLY / CONTROL-PLANE + CONTRACT DESIGN`
Priority: `VERY_HIGH_TASTE_RECOVERY`
Status: `prepared_awaiting_user_launch`.

Purpose:
- determine the narrowest safe restoration route now that old completed task is non-editable;
- if replacement task is necessary, design exact migration from old task id/generation 1 to one new active producer identity/generation without weakening fail-closed checks;
- design one-active-task canary strategy so the replacement is not a disposable one-time task that becomes non-editable again;
- design exact no-overlap proof, first-run timing, rollback, and System Audit gate before widening;
- use ChatGPT Scheduled + GitHub only, zero separately billed API/Copilot/external automation cost;
- no Scheduled Task mutation and no game analysis in this design worker.

Do not mark running until user confirms the command was sent/launched.

## Taste constraints retained
- Old completed `Taste Semantic Producer` remains preserved for provenance.
- No second active producer may exist.
- No fresh canary is authorized until restore design is accepted and an explicit IMPLEMENT task is created.
- Old Prototype/App_10150 result must not be reused.
- A fresh successful canary will make System Audit due before widening.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. User launches NEW Chat 1 with `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`.
2. Director consumes only its exact durable report.
3. If `complete_restore_plan_ready`, prepare exactly one bounded IMPLEMENT task for restoring one active producer and arming one fresh canary.
4. If blocked, do not create a replacement Scheduled Task by guesswork.
