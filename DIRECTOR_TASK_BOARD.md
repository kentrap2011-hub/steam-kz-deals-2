# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, reconcile current Board -> exact task file -> exact durable report from the immediately preceding step.
- Worker completion means exact durable report is final, not merely that the chat response ended.
- All non-trivial workers obey `WORKER_REPORT_DURABILITY_PROTOCOL.md` and `WORKER_ANTI_STALL_PROTOCOL.md`.
- All user-facing closeouts obey `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`.

## Anti-stall policy
- Worker checkpoints unresolved work roughly every 15 minutes.
- Long external runs are recorded immediately with exact run/job id.
- External polling is bounded to roughly 10 minutes / 3 checks per response cycle.
- If still running, worker records `waiting_external` and returns control.
- Report older than ~20 minutes with no recorded external run is presumptively stalled.
- Replacement worker checks for unseen actions before any retry.

## Closed worker results

### Paid-list repair — USER VERIFIED CLOSED
Task: `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
Report: `reviews/worker_reports/visual-main-list-refresh-handoff-implement-01.md`

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

### Pre-AI profile sync + same-canary rerun — FAILED AT COMMIT/PUSH
Task: `WORKER_TASK_TASTE_PREAI_PROFILE_SYNC_AND_CANARY_RERUN_01.md`
Report: `reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`
Final status: `needs_followup`.

### Taste sync retry after contention — FAILED, ROOT CAUSE PROVEN
Task: `WORKER_TASK_TASTE_PREAI_SYNC_RETRY_AFTER_CONTENTION_01.md`
Report: `reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md`
Final status: `needs_followup`.

### Current-main one-game canary design — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_DESIGN_01.md`
Report: `reviews/worker_reports/taste-current-main-canary-path-design-01.md`
Final status: `complete_design_ready_for_implementation`.

### Current-main one-game canary implementation — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_IMPLEMENT_01.md`
Report: `reviews/worker_reports/taste-current-main-canary-path-implement-01.md`
Final status: `complete_implementation_ready_for_canary_execution`.

Accepted implementation result:
- added permanent manual `.github/workflows/taste-current-main-canary.yml`;
- added bounded `scripts/build_taste_current_main_canary.py` and focused tests;
- one-AppID preparation is bounded before projection/payload expansion;
- validation used AppID 1016800 preparation-only, with no semantic execution;
- exactly one queue row for AppID 1016800 was prepared;
- repository remained clean and no canonical production/Taste state was written;
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` was not modified;
- no production rebuild or historical workflow rerun occurred;
- focused tests passed 7/7 locally and on GitHub runner;
- measured preparation wall-time on GitHub runner was 0.580 seconds;
- full validation job including checkout/tests/artifact upload completed in about 12 seconds;
- no paid API/Copilot/external scheduler was used.

## Current user goal
Run exactly one real Chernobylite semantic acceptance canary through the proven lightweight current-main preparation path, then perform an independent System Audit before any widening to normal daily Taste production.

## NEXT REQUIRES USER APPROVAL — one real Chernobylite semantic canary
Status: `awaiting_user_canary_execution_approval`.

Planned scope after approval:
- prepare AppID 1016800 from current `main` using the new lightweight path;
- freeze the exact resulting current tuple;
- use only existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` generation 2;
- execute exactly one Chernobylite semantic result;
- verify unchanged producer fence/binding/V5 checks and canonical ingest/receipt/cache/queue acceptance;
- no second game, no new Scheduled Task, no backlog widening;
- restore/verify permanent DAILY 01:00 Europe/Samara schedule;
- obey anti-stall protocol.

## Next sequence
1. User explicitly approves or declines the real Chernobylite canary execution.
2. If approved, Director prepares a separate bounded ACCEPTANCE worker task.
3. If Chernobylite is canonically accepted, launch NEW independent System Audit worker.
4. Only after System Audit PASS may the SAME recurring producer be widened to normal daily Taste production.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
