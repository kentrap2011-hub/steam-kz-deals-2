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

Current active task:
- `Taste Semantic Producer`
- task id `6aa032f37e688191a5c9a1a83f91c5d9`
- daily 01:00 Europe/Samara
- generation 2
- currently canary-bound to `Chernobylite Complete Edition` / AppID `1016800`
- old generation-1 task remains Completed/inactive.

## USER DECISION — FULL PRODUCTION SHOULD RUN AT 01:00
User explicitly does not want the 01:00 occurrence to be the first canary. User wants the test executed now, then independent audit, then (only if PASS) widening of the SAME recurring task before 01:00 so that 01:00 is normal full production.

Do not skip safety validation and blindly widen before a runtime canary. The accepted accelerated sequence is:
1. execute existing one-game canary now using SAME task;
2. independent System Audit immediately after accepted canary;
3. if audit PASS, separately widen SAME task to normal production before 01:00;
4. verify final schedule remains daily 01:00 Europe/Samara.

## AUTHORIZED NOW — immediate canary execution
Task: `WORKER_TASK_TASTE_CANARY_EXECUTE_NOW_01.md`
Expected report: `reviews/worker_reports/taste-canary-execute-now-01.md`
Status: `authorized_waiting_for_user_launch_confirmation`.

Scope:
- same active task id only;
- exact existing Chernobylite canary only;
- prefer direct run-now if available;
- otherwise temporary near-term reschedule of SAME recurring task is allowed only if identity/recurrence remain safe;
- restore permanent DAILY 01:00 Europe/Samara schedule before finalizing;
- no second task;
- no fallback game;
- no widening here;
- no paid API/Copilot/external scheduler.

## Next sequence
1. User launches immediate-canary worker.
2. Director consumes only exact report.
3. If `complete_canary_accepted_ready_for_system_audit`, immediately prepare/launch NEW independent System Audit worker.
4. If audit PASS, use already-given user authorization to prepare and launch bounded widening before 01:00; do not ask the user to re-approve the same stated goal unless a new risk/scope appears.
5. If canary or audit fails, do not widen at 01:00; report exact blocker.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
