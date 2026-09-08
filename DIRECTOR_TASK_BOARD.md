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

### Taste active producer restore design — SUBSTANTIVELY COMPLETE, STATUS MALFORMED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
Report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
Current report status: `completed`.
Task contract allows only:
- `complete_restore_plan_ready`
- `blocked_product_control_plane`
- `blocked_contract_migration`

Substantive conclusion clearly corresponds to `complete_restore_plan_ready`.
Existing Chat 1 must only correct the final report status to `complete_restore_plan_ready`, re-read the same report from `main`, and stop. No new investigation or implementation before this correction.
Chat 1 must NOT be deleted until corrected report is persisted.

## Accepted substantive restore design
- Old completed task remains untouched for provenance.
- Safe restoration route is exactly one NEW recurring daily ChatGPT Scheduled Task, not a disposable one-time canary.
- New immutable task id becomes canonical producer id `chatgpt_scheduled_task:<NEW_TASK_ID>`.
- Producer generation advances from `1` to `2`.
- Narrowest canonical GitHub identity migration changes only `config/taste_result_contract.json` active producer id/generation fields; fail-closed rejection policy and V5 contract remain unchanged.
- First recurring run remains scheduled for canonical 01:00 Europe/Samara, choosing a sufficiently future date to complete migration before execution.
- Initial instructions authorize exactly one fresh current Taste candidate/binding tuple and no fallback candidate.
- After that canary is accepted, the SAME recurring task remains Active but canary-locked; subsequent runs must no-op rather than process a second game.
- Separate independent System Audit is mandatory before widening the SAME task's instructions to normal daily production.
- No paid OpenAI API/Copilot/external automation service is required.

## Taste constraints retained
- Old completed `Taste Semantic Producer` remains preserved for provenance.
- No second active producer may exist.
- Old Prototype/App_10150 result must not be reused.
- Fresh successful canary makes System Audit due before widening.
- If task creation outcome is ambiguous, do not retry creation blindly; inspect Active tasks first and stop if identity is unclear.
- If migration fails before first run, pause the new task and remain with zero active producers rather than weaken the producer fence.

## Proposed next implementation after status correction
Task name from design:
`WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-active-producer-restore-implement-01.md`
Do not create/start until corrected design report is consumed.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Existing Chat 1 corrects only final report status to `complete_restore_plan_ready` and re-reads report from `main`.
2. Director consumes corrected exact report.
3. Prepare exactly one bounded IMPLEMENT task to create one recurring producer, migrate identity to generation 2, and arm one fresh canary.
4. After canary acceptance, require independent System Audit before widening the same task.
