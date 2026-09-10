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
- lightweight one-AppID preparation now resolves and freezes the canonical live `gaming_taste_live.json` by immutable commit/blob/content identity;
- profile changes before freeze select the newer proven version;
- profile changes after freeze cannot create a mixed-version tuple;
- continuous churn at the freeze boundary is bounded to three attempts and fails closed without requiring the user to pause profile updates;
- validation for AppID 1016800 passed with exactly one queued subject and no semantic execution/canonical write/Scheduled Task mutation;
- focused tests: 13/13 passed;
- validation run `34391317370`, job `102600034706`, artifact `10119736896`.

## Current user goal
Run exactly one real Chernobylite semantic acceptance result, then move Taste toward normal daily operation.

Permanent operating requirement from the user:
- the live game-taste profile will continue to be updated in parallel while Taste is operating;
- the user must not need to pause profile updates;
- no mixed-version result may be created;
- bounded retry/fail-closed behavior is acceptable, but no unbounded retry loop or manual repair should be required.

## User authorization state
- user has explicitly authorized exactly one real semantic Chernobylite result for AppID `1016800` / `App_1016800`;
- that authorization remains active for the prepared ACCEPTANCE step below;
- no repeat confirmation is required for this same single result;
- authorization does NOT permit a second semantic result, second game, new Scheduled Task, backlog widening, or weakened guards.

## CURRENT NEXT — one real Chernobylite acceptance
Status: `prepared_ready_for_dispatch_under_existing_user_authorization`.

Task:
`WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_ACCEPTANCE_02.md`

Expected report:
`reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`

Required scope:
- exactly one game: Chernobylite Complete Edition, AppID 1016800;
- use fixed immutable live-profile binding route;
- allow at most three pre-semantic preparation attempts if the profile changes before semantic execution;
- never mix versions;
- exactly one semantic result maximum;
- use only existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`, generation 2;
- verify canonical ingest/receipt/cache/queue acceptance;
- restore/verify DAILY 01:00 Europe/Samara;
- no second game/result/task;
- no widening;
- no paid OpenAI API, Copilot, external service or scheduler.

## Next sequence
1. Dispatch `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_ACCEPTANCE_02.md` to a NEW bounded worker chat.
2. Wait for exact durable report `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`.
3. If status is `complete_canary_accepted_ready_for_system_audit`, launch a NEW independent System Audit worker.
4. Only after System Audit PASS may the SAME recurring producer be widened to normal daily Taste production.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
