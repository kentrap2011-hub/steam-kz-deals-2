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
User evidence established existing `Taste Semantic Producer` is `Completed`, Date/Time are not editable, and Active filter is empty.
Old worker Chat 2 can be deleted. Do not delete the completed Scheduled Task yet.

## Silent-stall prevention postmortem — substantive result complete, report status malformed
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Report: `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Current report status: `done`.
Task contract allows only:
- `complete_reliability_action_required`
- `complete_no_common_systemic_defect`
- `blocked`

Substantive conclusion clearly corresponds to `complete_reliability_action_required`.
Existing Chat 1 must only change the final report status from `done` to `complete_reliability_action_required`, re-read the same report from `main`, and stop. No new investigation or implementation before this correction.
Chat 1 must NOT be deleted until the corrected report is persisted.

## Accepted substantive findings from the postmortem
The giveaway, paid-list, and ChatGPT incidents are not one shared producer bug. The common systemic defect is missing cycle-aware end-to-end health monitoring for independently refreshed domains.

Exact proposed health windows in Europe/Samara:
- paid prices/discounts: expected start 00:10; normal until 01:10; delayed 01:10-02:10; stale from 02:10;
- giveaways: expected start 00:10; normal until 01:10; delayed 01:10-02:10; stale from 02:10;
- ChatGPT/Taste: expected start 01:00; normal until 02:00; delayed 02:00-03:00; stale from 03:00.

Important semantics:
- state is based on whether the expected daily cycle completed with coherent domain-specific evidence, not raw file age;
- last-known-good data remains readable when stale, but UI clearly marks the affected domain stale;
- paid, giveaway, and Taste freshness must be shown independently;
- zero giveaways counts as current only if the current daily cycle has valid success evidence;
- missing ChatGPT dispatch must be detectable even if ChatGPT never starts and therefore writes no failure receipt.

Recommended single bounded reliability implementation:
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01`

Design:
- one unified read-only freshness evaluator for commercial, giveaways, and Taste;
- reuse existing 09:17 Europe/Samara `Build mailing feed` daily schedule as the observer, adding no new scheduler;
- persist one machine-readable freshness snapshot such as `site/publication_freshness.json`;
- expose per-domain current/delayed/stale status through existing health/status/public UI;
- never rerun or repair producers;
- detect a missed overnight cycle on the first missed local day;
- no paid API.

## Taste automatic analysis
No active recurring `Taste Semantic Producer` exists in the user's current Scheduled view.
No fresh canary is authorized yet.
Do not create or delete any Taste Scheduled Task until a bounded redesign is explicitly authorized.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Existing Chat 1 performs report-only status correction to `complete_reliability_action_required`.
2. After corrected report is consumed, prepare exactly one bounded IMPLEMENT task `WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01`.
3. After implementation, require independent System Audit if material runtime/health behavior changed.
