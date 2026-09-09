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
- new lightweight current-main preparation worked successfully for AppID 1016800;
- preparation run `34381380867`, job `102566817948`, artifact `10115975634`;
- preparation took about 0.547 seconds and produced exactly one semantic queue row for AppID 1016800;
- repository stayed clean and no canonical write occurred;
- semantic execution was STOPPED before Scheduled Task mutation because prepared profile binding was stale;
- prepared profile blob SHA: `191b6d6c5dec2f9ef2976517f301528740f9bec2`;
- then-current live profile blob SHA: `9c9ef7cdf2d705b8dd10196cec654f16e04341e4`;
- exact equality gate failed;
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` was not mutated or triggered;
- semantic results: 0; ingest attempts: 0; no second game/task/widening/System Audit.

## Current user goal
Run exactly one real Chernobylite semantic acceptance canary, but only after the lightweight preparation path binds to the then-current canonical live Taste profile rather than the stale committed profile snapshot.

## NEXT REQUIRES USER APPROVAL — fix current-live profile binding in lightweight canary preparation
Status: `awaiting_user_implementation_approval`.

Required fix scope, if approved:
- make the lightweight one-AppID preparation resolve the then-current canonical live `gaming_taste_live.json` binding rather than reuse stale committed profile binding;
- preserve read-only one-AppID preparation and all existing producer-fence/binding/V5 safety checks;
- fail closed if the live profile cannot be fetched/proven current;
- no manual SHA substitution;
- no canonical queue/payload hand-edit;
- no semantic execution in the fix task;
- no Scheduled Task mutation;
- no other game/backlog work.

After the fix is independently validated, the existing user authorization for one real Chernobylite semantic canary may be re-used only if the user confirms they still want the real canary at that time.

## Next sequence
1. User approves or declines the live-profile binding fix.
2. If approved, Director prepares a separate bounded IMPLEMENT worker task.
3. After implementation passes, ask/confirm one real Chernobylite canary execution.
4. If canonically accepted, launch NEW independent System Audit worker.
5. Only after System Audit PASS may the SAME recurring producer be widened to normal daily Taste production.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
