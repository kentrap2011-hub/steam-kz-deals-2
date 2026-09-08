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

Accepted result of repair:
- historical generation-1 Prototype file was confirmed as the original blocker;
- it was preserved under `data/ai_archive/taste/generation-1/` and removed from active inbox;
- active old-generation or malformed files still fail closed;
- current producer safety was not weakened;
- the existing Chernobylite gen2 result then reached the later normal binding validation;
- it was rejected because the canonical taste-profile blob had changed since that result was produced;
- Chernobylite remains unaccepted/pending;
- no semantic rerun, other game, new task, or backlog processing occurred.

## USER GOAL — FULL PRODUCTION AT 01:00
User wants runtime validation completed before 01:00 so the 01:00 run can be normal production.
The stale inbox problem is repaired. The remaining required runtime step is one fresh Chernobylite result bound to the current profile.

## ACTIVE — refreshed Chernobylite canary rerun
Task: `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`
Expected report: `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`
Status: `same_chat_1_must_continue_report_in_progress`.

The user reported Chat 1 finished, but the exact durable report still has status `in_progress`.
Current durable checkpoint proves only:
- current Chernobylite tuple was frozen;
- no Scheduled Task mutation had occurred yet;
- no new task/game/backlog work occurred;
- canonical acceptance was still pending.

Therefore Chat 1 is NOT considered complete. Do not infer success or failure from the chat ending.
The SAME Chat 1 must continue this exact task and update the SAME report to one allowed final status only after completing or safely stopping the task.

Scope remains:
- only Chernobylite / AppID 1016800;
- same generation-2 Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9`;
- no second task/game;
- no backlog widening;
- restore/verify DAILY 01:00 Europe/Samara schedule before final report;
- no paid API/Copilot/external scheduler.

## Next sequence
1. SAME Chat 1 resumes `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md` from its existing durable checkpoint.
2. Director waits for user to say it finished again.
3. Director fetches only `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`.
4. If final status is `complete_canary_accepted_ready_for_system_audit`, launch NEW independent System Audit worker immediately.
5. If System Audit PASS, widen SAME recurring task before 01:00 under user's already-stated goal.
6. If rerun/audit fails, do not widen; report exact blocker.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
