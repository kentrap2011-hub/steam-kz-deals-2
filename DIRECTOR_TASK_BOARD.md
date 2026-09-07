# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from old chat history alone.
- A worker response cycle ending does not mean its task is durably complete; consume the exact report first.
- All non-trivial workers must obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- Every user-facing closeout must obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md` and explain results in ordinary Russian before technical names.

## Current worker slots

### Chat 1 — paid-list repair DURABLY CLOSED; awaiting user verification
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Report:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Final status: `complete_ready_for_user_verification`.

Plain result:
- fresh Steam-derived commercial truth can now update the paid list without waiting for new ChatGPT/Taste analysis;
- no second scheduler, Steam collection path, publication writer, or Pages route was introduced;
- the ordinary full semantic path remains separate and fail-closed;
- stale paid rows were removed and the accepted paid list was reduced from 442 to 190 current visible items;
- protected Taste/semantic fields were not rewritten;
- giveaway state was preserved;
- ordinary GitHub Pages deployment succeeded;
- accepted paid source lineage is `2026-09-06T21:00:38.938100+00:00`, newer than the stale Aug 30/31 incident state.

User verification required before closing the user-visible incident:
- reload/open the deployed site on Android/browser;
- confirm the main paid list no longer shows the stale August state and prices/discounts/deadlines look current;
- confirm the paid-list freshness indicator reflects the current paid source independently of giveaway/semantic timestamps.

Chat 1 worker result is durable. This worker chat can be deleted.

### Chat 2 — completed-task reuse recon DURABLY CLOSED
Task:
`WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report:
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Final status: `blocked_same_id_reuse_unproven`.

Plain result:
- no state was changed, no task was created, and no game analysis was run;
- worker could not prove exact-id in-place reuse from its read-only control plane.

Chat 2 worker result is durable. This worker chat can be deleted.

## User control-plane observation for existing Taste Scheduled Task
On 2026-09-07 the user inspected the existing completed `Taste Semantic Producer` in ChatGPT Scheduled.

Observed directly by the user:
- state is `Завершено` / `Completed`;
- Date and Time values are visible but not active/editable;
- filtering Scheduled by `Активно` / `Active` returns an empty list;
- the existing completed task has not been deleted.

Operational conclusion:
- correct the prior Director inference: visible Date/Time rows did NOT establish editable in-place schedule controls;
- current user-visible control-plane evidence strongly establishes that there is no active scheduled Taste producer and this completed task is not presently scheduled to run again;
- this evidence does not establish why the product makes the completed task non-editable, and does not by itself prove whether some hidden/API-level same-id reactivation exists;
- for project operation, however, no future automatic semantic run may be assumed from this completed card;
- do not delete the completed task yet because it remains useful provenance/evidence;
- do not create a replacement task without a new bounded design/authorization step.

## Taste next gate
The previous plan to reschedule the same completed card through Date/Time is invalidated by the user's direct UI evidence.

Before restoring automatic ChatGPT analysis, the project needs a new bounded design decision for how to establish exactly one ACTIVE recurring producer without overlap and without paid OpenAI API/Copilot. Any replacement must account for the fact that the prior canary task is completed and non-editable in the user's current Scheduled UI.

No fresh one-game canary is authorized yet.

## Paid-list publication repair
Implementation is complete and deployed. User verification on Android/browser is the remaining closure gate.

## Publication freshness recurrence postmortem
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Status: `queued_after_main_list_refresh_user_verification`.

This remains mandatory after recovery to add first-day detection for silent failures and compare the giveaway, paid-list, and ChatGPT-analysis incidents.

## Giveaway publication
User already verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route remains prohibited unless the user explicitly reverses that policy.

## Next decision
1. User verifies the repaired main paid list on Android/browser.
2. After that verification, run the mandatory publication-freshness recurrence postmortem and keep the automatic-ChatGPT failure in scope.
3. Separately prepare a bounded Taste control-plane redesign for exactly one active recurring ChatGPT Scheduled Task; do not reuse the now-invalid assumption that the completed task's Date/Time can be edited.
4. Do not create or delete any Taste Scheduled Task until that bounded step is explicitly authorized.
