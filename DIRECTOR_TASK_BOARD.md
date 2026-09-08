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
User evidence establishes existing `Taste Semantic Producer` is `Completed`, Date/Time are not editable, and ChatGPT Scheduled filter `Active` is empty.
Therefore there is currently no active recurring ChatGPT Scheduled Taste producer.
Do not delete the completed Scheduled Task yet.

### Silent-stall prevention postmortem — DURABLY CLOSED
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Report: `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Final status: `complete_reliability_action_required`.
Old worker Chat 1 can be deleted.

Accepted analysis remains historical/reference only. The proposed 03:15 independent observer was explicitly declined by the user.

## User-selected freshness visibility policy
User decision:
- do NOT add the 03:15 watchdog/health-only scheduler;
- do NOT add another external monitoring service merely to tell the user about stale data;
- rely on a truthful visible last-successful-update date on the site;
- if data stops updating, that date must remain old so the user can recognize staleness directly.

Required invariant for the visible paid-list date:
- it advances only when a genuine paid/commercial refresh is successfully accepted/published;
- giveaway-only activity must not advance it;
- Taste/ChatGPT activity must not advance it;
- generic deploy/build time must not advance it;
- failed or missing paid refresh must leave the previous successful date intact.

The recent paid-list repair was user-verified to advance the date when current paid data was restored. No additional sentinel implementation is requested at this time.

## Superseded task
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md`
Status: `SUPERSEDED_BY_USER_DECISION_DO_NOT_RUN`.
Do not launch it and do not create its worker report.

## Taste automatic analysis
No active recurring ChatGPT Scheduled Taste producer currently exists.
No fresh canary is authorized yet.
Do not create or delete any Taste Scheduled Task until a bounded redesign is explicitly authorized.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
The silent-stall monitoring branch is closed by user decision. Return to the next active project priority: restore one safe active recurring ChatGPT/Taste producer or another user-selected backlog item, while preserving the completed old Taste task for provenance until the redesign decision is made.
