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

### Real Chernobylite semantic canary — STOPPED BEFORE SEMANTIC EXECUTION
Task: `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_EXECUTE_01.md`
Report: `reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md`
Final status: `needs_followup`.

Accepted result:
- lightweight current-main preparation worked for AppID 1016800;
- semantic execution stopped safely because prepared profile binding was stale;
- no semantic result or canonical ingest occurred.

### Concurrent live-profile binding fix — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`
Report: `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
Final status: `complete_ready_for_real_canary_acceptance`.

Accepted result:
- lightweight one-AppID preparation now freezes one exact canonical live profile version;
- profile changes before freeze select the newer proven version;
- profile changes after freeze cannot create a mixed-version tuple;
- continuous churn is bounded and does not require the user to pause profile updates;
- focused tests passed 13/13.

### Real Chernobylite acceptance — DURABLY CLOSED AND ACCEPTED
Task: `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_ACCEPTANCE_02.md`
Report: `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
Final status: `complete_canary_accepted_ready_for_system_audit`.

Accepted result:
- exactly one real semantic result was generated for Chernobylite / AppID 1016800;
- result was accepted and canonically ingested;
- canonical receipt/cache/overlay advanced;
- active inbox was consumed;
- App_1016800 left the pending queue;
- no second game or second semantic result was produced;
- existing Scheduled Task remained the only semantic producer and was restored to DAILY 01:00 Europe/Samara;
- no backlog widening occurred;
- System Audit is now ready.

## Current user goal
Move Taste safely to normal daily operation, while allowing the live game-taste profile to keep changing in parallel.

Permanent operating requirement from the user:
- the user must not need to pause profile updates;
- no mixed-version result may be created;
- bounded retry/fail-closed behavior is acceptable;
- no unbounded retry loop or manual repair should be required.

## CURRENT NEXT — post-canary system audit
Status: `prepared_ready_for_dispatch`.

Task:
`WORKER_TASK_TASTE_POST_CANARY_SYSTEM_AUDIT_01.md`

Expected report:
`reviews/worker_reports/taste-post-canary-system-audit-01.md`

Purpose:
- independently verify current production state after the accepted Chernobylite result;
- verify queue/cache/receipt/inbox consistency;
- verify existing Scheduled Task is healthy and restored to DAILY 01:00 Europe/Samara;
- verify no duplicate/second result or second producer exists;
- verify live-profile updates cannot reintroduce the stale-binding failure;
- verify all safety guards remain enabled;
- decide PASS/FAIL for normal daily Taste operation.

Hard boundaries:
- read-only/acceptance only;
- no implementation changes;
- no new semantic result;
- no Scheduled Task trigger or mutation;
- no second game;
- no widening in the audit itself;
- no paid OpenAI API, Copilot, external service or scheduler.

## Next sequence
1. Dispatch `WORKER_TASK_TASTE_POST_CANARY_SYSTEM_AUDIT_01.md` to a NEW independent worker chat.
2. Read exact durable report `reviews/worker_reports/taste-post-canary-system-audit-01.md`.
3. If System Audit returns PASS, Director may prepare the final bounded step to enable normal daily Taste operation using the SAME existing producer.
4. Any IMPLEMENT change still requires separate user approval under the current rules.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
