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
The intended 2026-09-09 01:00 Europe/Samara widening deadline has now passed. Do not claim full production happened at 01:00 unless a final durable worker report proves it. No blind recovery or new producer is authorized from Director inference.

## ACTIVE — refreshed Chernobylite canary rerun
Task: `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`
Expected report: `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`
Status: `same_chat_1_final_report_still_missing_after_user_completion_signal`.

The user again reported Chat 1 finished, but the exact durable report is unchanged and still has status `in_progress`.
The durable checkpoint proves only:
- current Chernobylite tuple was frozen;
- no Scheduled Task mutation had occurred yet at that checkpoint;
- no new task/game/backlog work had occurred;
- canonical acceptance was still pending.

Because 01:00 has passed, the SAME Chat 1 must now finish by reconciling the actual current state rather than blindly continuing the old timing assumptions. It must explicitly determine and record:
- whether the existing Scheduled Task ran at 01:00;
- what exact prompt/binding it had at that time;
- whether any Chernobylite submission/result occurred;
- whether anything was canonically accepted;
- current active inbox/archive state;
- current queue/receipt state for AppID 1016800;
- current Scheduled Task enabled state and next DAILY 01:00 recurrence;
- whether a safe refreshed one-game rerun is still needed or already occurred;
- one allowed final status only after completing or safely stopping the exact task.

Do not create another Scheduled Task.
Do not process another game.
Do not widen backlog/full production without a later independent System Audit PASS and separate widening task.
Do not rerun blindly if a 01:00 execution already produced a current valid result.

## Next sequence
1. SAME Chat 1 resumes from the existing report and reconciles actual post-01:00 state.
2. It updates the SAME report to one allowed final status: `complete_canary_accepted_ready_for_system_audit`, `needs_followup`, or `blocked`.
3. Director consumes only that exact durable report.
4. If accepted-ready, launch NEW independent System Audit.
5. Only after audit PASS may the SAME recurring producer be widened for future 01:00 runs.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
