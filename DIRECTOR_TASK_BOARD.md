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

Accepted final result:
- no new Chernobylite result was produced or accepted;
- no other game/task/backlog processing occurred;
- same generation-2 Scheduled Task remains enabled;
- permanent schedule is DAILY 01:00 Europe/Samara, next recorded start 2026-09-10 01:00;
- old stale Chernobylite gen2 result was preserved in archive and removed from active inbox;
- canonical pre-AI payload and current live Taste profile no longer have the same profile blob;
- prepared pre-AI profile binding was `191b6d6c5dec2f9ef2976517f301528740f9bec2` while live profile had advanced to `705e1f852d91a8a63d8686b37c51ace41c02f4ac`;
- worker correctly stopped rather than bypassing exact binding validation.

## Current user goal
Restore safe full daily Taste production using the existing generation-2 Scheduled Task. Runtime canary must be accepted before independent System Audit and later widening. The missed 2026-09-09 01:00 full-production target is not considered achieved.

## AUTHORIZED NEXT — synchronize pre-AI to current profile and rerun same canary
Task: `WORKER_TASK_TASTE_PREAI_PROFILE_SYNC_AND_CANARY_RERUN_01.md`
Expected report: `reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`
Status: `prepared_for_existing_chat_1`.

Scope:
- canonically regenerate atomic pre-AI state ONCE against the then-current live Taste profile;
- do not manually substitute profile hashes;
- after regeneration prove prepared profile SHA equals current live profile SHA;
- if profile changes again before equality/dispatch, stop fail-closed rather than loop indefinitely;
- use only Chernobylite / AppID 1016800;
- update and run only SAME Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9`;
- no new task, other game, backlog widening, paid API/Copilot/external scheduler;
- restore/verify DAILY 01:00 Europe/Samara schedule;
- require canonical acceptance receipt/cache/queue evidence before calling the canary successful.

The existing Chat 1 may continue this bounded follow-up. Do not delete it yet.

## Next sequence
1. SAME Chat 1 executes `WORKER_TASK_TASTE_PREAI_PROFILE_SYNC_AND_CANARY_RERUN_01.md`.
2. Director consumes only the exact durable report.
3. If `complete_canary_accepted_ready_for_system_audit`, launch a NEW independent System Audit worker.
4. Only after System Audit PASS may the SAME recurring producer be widened to normal daily production.
5. If profile changes again or another blocker occurs, stop and report exact condition; do not create another producer.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
