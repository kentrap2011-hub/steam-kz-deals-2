# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, reconcile current Board -> exact task file -> exact durable report from the immediately preceding step.
- Worker completion means exact durable report is final, not merely that the chat response ended.
- All non-trivial workers obey `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- All user-facing closeouts obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`.

## Closed worker results

### Paid-list repair — USER VERIFIED CLOSED
Task: `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Report: `reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`
Result: fresh paid prices/discounts now publish independently of unfinished ChatGPT semantic analysis.

### Taste restore design — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
Report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
Final status: `complete_restore_plan_ready`.

### Taste restore implementation — COMPLETE, CANARY ARMED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
Report: `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
Final status: `complete_canary_armed_system_audit_pending`.

### Immediate canary execution — RAN, NOT ACCEPTED
Task: `WORKER_TASK_TASTE_CANARY_EXECUTE_NOW_01.md`
Report: `reviews/worker_reports/taste-canary-execute-now-01.md`
Final status: `complete_canary_rejected_needs_diagnosis`.

### Stale inbox repair — COMPLETE REPAIR, CANARY STILL STALE
Task: `WORKER_TASK_TASTE_STALE_INBOX_REPAIR_01.md`
Report: `reviews/worker_reports/taste-stale-inbox-repair-01.md`
Final status: `needs_followup`.

### Refreshed Chernobylite canary rerun — STOPPED SAFELY
Task: `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`
Report: `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`
Final status: `needs_followup`.

### Pre-AI profile sync + same-canary rerun — ONE ATTEMPT FAILED AT COMMIT/PUSH
Task: `WORKER_TASK_TASTE_PREAI_PROFILE_SYNC_AND_CANARY_RERUN_01.md`
Report: `reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`
Final status: `needs_followup`.

Accepted final result:
- exactly one authorized canonical pre-AI synchronization attempt was used;
- rerun job id `102329869100` failed after deterministic generation at commit/push;
- `main` advanced concurrently and the workflow rebase/push path encountered conflicts;
- regenerated state was not durably committed to `main`;
- no manual generated-file/hash patching occurred;
- no second rebuild attempt occurred;
- Chernobylite semantic analysis was NOT started;
- no other game/task/backlog work occurred;
- same generation-2 Scheduled Task remains the only semantic producer with permanent DAILY 01:00 Europe/Samara schedule.

## Current user goal
Restore safe full daily Taste production using the existing generation-2 Scheduled Task. Runtime canary must be canonically accepted before independent System Audit and later widening.

## ACTIVE — bounded sync retry after repository contention
Task: `WORKER_TASK_TASTE_PREAI_SYNC_RETRY_AFTER_CONTENTION_01.md`
Expected report: `reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md`
Status: `same_chat_1_report_in_progress`.

Current durable checkpoint:
- quiescence preflight completed twice;
- no active or queued GitHub Actions writer was observed;
- current live Taste profile was captured;
- current committed prepared payload still does not match live profile;
- exactly one synchronization retry is still pending and has NOT yet been launched in this task;
- no semantic Chernobylite run has started;
- no Scheduled Task mutation has occurred.

User reported Chat 1 finished, but exact durable report remains `in_progress`. Therefore this worker response cycle ended without durable task completion.

The SAME Chat 1 must continue from the existing report/checkpoint. It must not create a new report and must not restart the task from scratch.

Scope remains:
- perform at most the one authorized canonical sync retry;
- if a relevant writer becomes active before retry, stop `needs_followup` rather than launch into contention;
- if retry commits successfully, require committed prepared profile binding == current live profile;
- only then run Chernobylite AppID 1016800 through SAME Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9`;
- no new task, other game, backlog widening, paid API/Copilot/external scheduler;
- restore/verify DAILY 01:00 Europe/Samara;
- require canonical receipt/cache/queue evidence before success.

## Next sequence
1. SAME Chat 1 resumes `WORKER_TASK_TASTE_PREAI_SYNC_RETRY_AFTER_CONTENTION_01.md` from the existing durable checkpoint.
2. It updates the SAME report to one allowed final status.
3. Director consumes only the exact durable report.
4. If `complete_canary_accepted_ready_for_system_audit`, launch NEW independent System Audit worker.
5. Only after System Audit PASS may the SAME recurring producer be widened to normal daily production.
6. If retry is blocked/fails, do not widen and do not create another producer.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
