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
The stale inbox problem is now repaired. The remaining required runtime step is one fresh Chernobylite result bound to the current profile.

## AUTHORIZED NEXT — refreshed Chernobylite canary rerun
Task: `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`
Expected report: `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`
Status: `prepared_for_existing_chat_1`.

Scope:
- use only Chernobylite / AppID 1016800;
- freeze current exact binding including current profile SHA;
- preserve/archive the now-stale previous gen2 Chernobylite inbox result before fresh submission;
- update only the SAME generation-2 Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9` to the refreshed canary tuple;
- trigger that SAME task now;
- restore/verify DAILY 01:00 Europe/Samara schedule and enabled state;
- verify exactly one fresh Chernobylite result is canonically accepted and queue/receipt state advances;
- no other game;
- no second task;
- no backlog widening;
- no paid API/Copilot/external scheduler.

The current stale-inbox repair worker Chat 1 may be reused for this immediate follow-up. Do not delete it yet.

## Next sequence
1. Existing Chat 1 executes `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`.
2. Director consumes only the exact durable report.
3. If `complete_canary_accepted_ready_for_system_audit`, launch a NEW independent System Audit worker immediately.
4. If System Audit PASS, widen the SAME recurring task before 01:00 under the user's already-stated goal.
5. If rerun/audit fails, do not widen; report the exact blocker.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
