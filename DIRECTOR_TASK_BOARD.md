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
Old worker Chat 1 can be deleted.

### Completed Taste task reuse recon — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report: `reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Result: exact same-id reuse was not proven.
User evidence additionally established that existing `Taste Semantic Producer` is `Completed`, Date/Time are not editable, and Active filter is empty.
Old worker Chat 2 can be deleted. Do not delete the completed Scheduled Task yet.

## Immediate priority — silent-stall prevention
The user identified the remaining reliability gap: a last-update timestamp alone does not tell them that the next expected daily refresh was missed.

Required outcome:
- per-domain visible health state derived from expected cadence;
- ordinary-language states at least `current`, `update delayed`, `stale/not updating`;
- separate truth for paid deals, giveaways, and ChatGPT/Taste progress;
- durable backend signal when an expected daily refresh/progress event is missed;
- detection within the first missed day;
- no manual daily checking by the user;
- no paid API requirement;
- no duplicate writers/schedulers.

### Next worker — PREPARED, NOT YET LAUNCHED
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Expected report: `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Mode: `READ-ONLY / RECON / POSTMORTEM`
Priority: `VERY_HIGH_RELIABILITY`
Status: `prepared_awaiting_user_launch`.

The task has been updated to cover all three incidents:
1. giveaway publication;
2. paid-list publication;
3. silent stop of automatic ChatGPT semantic analysis.

It must define exact expected cadence/grace windows, visible current/delayed/stale semantics, durable first-day missed-refresh signaling, and exactly one bounded reliability IMPLEMENT task.

## Taste automatic analysis
No active recurring `Taste Semantic Producer` exists in the user's current Scheduled view.
No fresh canary is authorized yet.
Do not create or delete any Taste Scheduled Task until a bounded redesign is explicitly authorized.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. User launches the silent-stall postmortem worker.
2. Director consumes only its exact durable report.
3. If report recommends reliability action, Director prepares exactly one bounded implementation for visible stale-state indication plus automatic first-day missed-refresh detection.
4. Independent System Audit follows if the report/implementation requires it.
