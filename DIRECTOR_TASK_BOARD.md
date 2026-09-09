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
- permanent manual current-main one-AppID path is implemented;
- exactly one AppID can be prepared without canonical writes;
- AppID 1016800 preparation-only validation passed;
- focused tests passed 7/7 locally and on GitHub runner;
- measured preparation wall-time was 0.580 seconds;
- full validation job was about 12 seconds;
- no semantic execution, production write, Scheduled Task mutation, historical rerun, paid API/Copilot/external scheduler occurred.

## Current user goal
Run exactly one real Chernobylite semantic acceptance canary through the proven lightweight current-main preparation path, then perform an independent System Audit before any widening to normal daily Taste production.

## PREPARED — one real Chernobylite semantic canary
Task: `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_EXECUTE_01.md`
Expected report: `reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md`
Status: `prepared_not_launched`.

User explicitly authorized exactly one real semantic Chernobylite result.

Scope:
- prepare AppID 1016800 from current `main` using the new lightweight path;
- require queue cardinality exactly 1;
- hard-gate semantic execution on exact equality between prepared profile binding and then-current canonical live Taste profile;
- hard-gate on canonical queue/binding/producer-fence/V5 acceptability;
- if any gate fails, stop quickly `needs_followup` with no semantic execution and no broad rebuild;
- if gates pass, freeze exact tuple and use ONLY existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`, generation 2;
- generate at most one Chernobylite semantic result;
- verify canonical ingest/receipt/cache/queue acceptance;
- no second game, no new Scheduled Task, no backlog widening;
- restore/verify permanent DAILY 01:00 Europe/Samara schedule;
- obey anti-stall protocol.

## Next sequence
1. NEW Chat 1 executes `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_EXECUTE_01.md`.
2. Director consumes only the exact durable report.
3. If `complete_canary_accepted_ready_for_system_audit`, launch NEW independent System Audit worker.
4. Only after System Audit PASS may the SAME recurring producer be widened to normal daily Taste production.
5. If any acceptance gate fails, do not widen and do not create another producer.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
