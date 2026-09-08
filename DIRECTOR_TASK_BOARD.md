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

### Chat 1 — paid-list repair DURABLY CLOSED and USER VERIFIED
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Report:
`reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Final status: `complete_ready_for_user_verification`.
User verification: PASS.

User-observed result on Android/browser:
- stale/non-current discount rows disappeared;
- paid-list update date advanced.

Therefore the user-visible paid-list freshness incident is closed.

Plain implementation result:
- fresh Steam-derived commercial truth now updates the paid list without waiting for new ChatGPT/Taste analysis;
- no second scheduler, Steam collection path, publication writer, or Pages route was introduced;
- protected Taste/semantic fields were not rewritten;
- giveaway state was preserved;
- ordinary GitHub Pages deployment succeeded.

Chat 1 worker result is durable. This worker chat can be deleted.

### Chat 2 — completed-task reuse recon DURABLY CLOSED
Task:
`WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report:
`reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Final status: `blocked_same_id_reuse_unproven`.

Chat 2 worker result is durable. This worker chat can be deleted.

## User control-plane observation for existing Taste Scheduled Task
User directly established:
- existing `Taste Semantic Producer` is `Завершено` / `Completed`;
- Date and Time are visible but not editable;
- Scheduled filter `Активно` / `Active` is empty;
- no future automatic semantic run should be assumed from that completed card.

Do not delete the completed task yet because it remains useful provenance/evidence. Do not create a replacement task without a new bounded design/authorization step.

## Freshness visibility / silent-stall problem
The paid-list repair now exposes a truthful last-update date, but the user correctly identified a remaining reliability/UI gap:
- a timestamp alone does not tell the user that the NEXT expected daily refresh has been missed;
- today the user must manually remember the expected cadence and compare dates;
- this is not sufficient protection against another multi-day silent stall.

Required next reliability outcome:
- each independently refreshed domain must have a visible health state derived from its expected cadence, not only a last-update timestamp;
- at minimum distinguish `current`, `update delayed`, and `stale/not updating` in ordinary user language;
- do not let giveaway freshness mask paid-list staleness, and do not let paid-list freshness mask stalled ChatGPT semantic analysis;
- detection threshold must be based on the actual expected daily schedule plus a bounded grace window, not an arbitrary artifact timestamp;
- backend/system monitoring must also raise a durable failure signal when an expected refresh/progress event is missed, rather than relying on the user to notice the site date.

## Publication freshness recurrence postmortem
Task:
`WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Status: `ready_to_launch_after_user_verified_recovery`.

This task must now explicitly answer how the site and system should show/raise a missed expected refresh within the first day for:
- paid prices/discounts;
- giveaway publication;
- automatic ChatGPT semantic analysis.

After the postmortem, prepare exactly one bounded reliability IMPLEMENT task for the visible stale-state indicator plus automatic missed-refresh detection/escalation.

## Taste next gate
Before restoring automatic ChatGPT analysis, the project needs a bounded design decision for exactly one active recurring producer without overlap and without paid OpenAI API/Copilot.

No fresh one-game canary is authorized yet.

## Giveaway publication
User already verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task:
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route remains prohibited unless the user explicitly reverses that policy.

## Next decision
1. Launch the mandatory publication-freshness recurrence postmortem now that the paid-list repair is user-verified.
2. In parallel only if safe, prepare the bounded Taste control-plane redesign for exactly one active recurring ChatGPT Scheduled Task.
3. After postmortem, implement visible `current/delayed/stale` states and automatic first-day missed-refresh detection rather than relying on timestamps alone.
4. Do not create or delete any Taste Scheduled Task until its bounded design step is explicitly authorized.
