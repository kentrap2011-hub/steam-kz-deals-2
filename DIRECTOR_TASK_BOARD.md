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

Accepted corrected findings:
- `.github/workflows/build-mailing-feed.yml` has no independent daily schedule; previous 09:17 claim was false and was removed.
- `.github/workflows/steam-test.yml` has GitHub Actions cron nominally 00:10 Europe/Samara.
- GitHub Actions history proved recent scheduled producer runs around 00:21–00:22, so configuration and execution are now distinguished.
- corrected deterministic freshness window: normal through 01:30, delayed 01:30–02:30, stale from 02:30.
- Taste contractual target remains 01:00, normal through 02:00, delayed 02:00–03:00, stale from 03:00, but there is currently no active ChatGPT Scheduled task.
- no verified existing independent execution exists after the latest 03:00 cutoff that can serve as the observer.
- narrowest safe remedy is one independent health-only daily observer around 03:15 Europe/Samara; it must only read evidence and report health, never rerun/repair producers or invoke ChatGPT.

## Prepared reliability implementation — NOT LAUNCHED
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md`
Expected report: `reviews/worker_reports/publication-freshness-sentinel-implement-01.md`
Status: `prepared_waiting_for_user_approval`

Scope:
- one unified independent health-only observer after latest stale cutoff, target about 03:15 Europe/Samara;
- per-domain `current` / `delayed` / `stale` plus diagnostic reason;
- one canonical machine-readable health snapshot/status truth;
- preserve last-known-good publications;
- no producer rerun/retry/recovery;
- no Steam/giveaway collection;
- no ChatGPT invocation or Scheduled Task mutation;
- no OpenAI API/Copilot/separately paid service;
- final status must be `complete_ready_for_system_audit`, `needs_followup_fix`, or `blocked`.

Do not mark this task running until the user explicitly approves/launches it.
If completed successfully, independent System Audit is required before acceptance because runtime/health behavior changes materially.

## Taste automatic analysis
No active recurring ChatGPT Scheduled Taste producer currently exists.
No fresh canary is authorized yet.
Do not create or delete any Taste Scheduled Task until a bounded redesign is explicitly authorized.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Ask user whether to launch the prepared bounded freshness-sentinel IMPLEMENT task.
2. If approved, assign it to a NEW Chat 1 and mark running only after user confirms it was sent/launched.
3. After successful implementation, require independent System Audit before acceptance.
