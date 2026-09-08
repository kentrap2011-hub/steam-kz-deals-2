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

## Silent-stall prevention postmortem — FORMAL STATUS FIXED, FACTUAL CORRECTION STILL REQUIRED
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Report: `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
Current formal status: `complete_reliability_action_required`.

The report's central cycle-aware monitoring conclusion remains useful, but one factual premise is wrong:
- it claims `.github/workflows/build-mailing-feed.yml` has an independent daily 09:17 Europe/Samara schedule;
- direct inspection proves that workflow has NO `schedule:` trigger. It runs via `workflow_dispatch`, successful `workflow_run` of `Steam KZ production shortlist`, and selected pushes.

Separate verified configuration fact:
- `.github/workflows/steam-test.yml` (`Steam KZ production shortlist`) contains `schedule: cron "10 20 * * *"`, documented as 00:10 Europe/Samara;
- this is a GitHub Actions scheduler, NOT a ChatGPT Scheduled Task and therefore cannot appear in the user's ChatGPT Scheduled UI;
- configuration existence has been verified, but Director has NOT proven from recent run history that the scheduled 00:10 run actually executed today/recently. Do not conflate configured cron with proven runtime execution.

ChatGPT distinction:
- the expected 01:00 semantic/Taste producer belongs to ChatGPT Scheduled;
- user UI proves there is currently no active recurring ChatGPT task, so the 01:00 semantic run should be treated as NOT currently scheduled/running.

Required same-worker correction:
1. Correct the false 09:17 claim in the same report.
2. Distinguish GitHub 00:10 configured cron from ChatGPT 01:00 inactive task.
3. Verify, if accessible, whether recent 00:10 GitHub scheduled runs actually occurred; if not provable, mark runtime execution unknown rather than infer it.
4. Recompute the sentinel observation design. A 00:10 producer cannot independently detect its own total non-dispatch and runs before the 01:00 ChatGPT expectation. If no existing independent post-cutoff scheduler is proven, the report must say so plainly and recommend the narrowest safe observer design rather than inventing one.
5. No implementation in this correction.

Chat 1 must NOT be deleted until this factual correction is durably persisted and re-read.

## Existing useful freshness semantics pending corrected observer design
Proposed state windows in Europe/Samara remain subject to report correction but currently are:
- paid/giveaway: normal through 01:10, delayed 01:10-02:10, stale from 02:10;
- ChatGPT/Taste: normal through 02:00, delayed 02:00-03:00, stale from 03:00.

## Taste automatic analysis
No active recurring ChatGPT Scheduled Taste producer currently exists.
No fresh canary is authorized yet.
Do not create or delete any Taste Scheduled Task until a bounded redesign is explicitly authorized.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Existing Chat 1 corrects the postmortem's scheduler facts and observer recommendation, and verifies recent 00:10 GitHub scheduled execution only if evidence is accessible.
2. Director consumes only the corrected durable report.
3. Only then prepare the single bounded freshness-sentinel IMPLEMENT task.
