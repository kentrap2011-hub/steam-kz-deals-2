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

Accepted design result:
- there is no existing safe bounded one-AppID current-main preparation path as-is;
- full pre-AI workflow can use current `main` but is too broad and write-producing for this canary;
- smallest safe design is a new workflow_dispatch-only, read-only current-main canary workflow with one required AppID;
- explicit checkout of `refs/heads/main`;
- bounded one-AppID harness reusing current Taste logic;
- all outputs go to runner temp/artifact only, with no canonical repository writes, commit/push, semantic execution, inbox/ingest/cache/overlay mutation;
- committed current-main snapshots/config are consumed read-only; broad StoreBrowse refresh is excluded from the canary;
- historical workflow reruns are rejected as the normal canary path;
- implementation must prove one-subject bounding, current-main provenance, clean repo tree, exact binding/decision trace, and fail-closed missing context;
- expected preparation runtime is seconds-to-tens-of-seconds after runner startup, to be measured during implementation.

## Current user goal
Restore safe full daily Taste production using the existing generation-2 Scheduled Task, but first implement and validate the lightweight one-game current-main canary path, then run one bounded Chernobylite acceptance canary.

## NEXT REQUIRES USER APPROVAL — implement current-main one-game canary path
Status: `awaiting_user_implementation_approval`.

Implementation scope, once approved:
- add a workflow_dispatch-only read-only current-main canary workflow;
- add bounded one-AppID temporary-output harness reusing current Taste logic;
- add focused tests for one-subject bounding, output isolation, zero/one queue behavior, and fail-closed missing context;
- do not run Chernobylite in the implementation task unless separately authorized;
- do not modify Scheduled Task;
- no paid API/Copilot/external scheduler;
- obey anti-stall protocol.

## Next sequence
1. User explicitly approves or declines IMPLEMENT.
2. If approved, Director prepares a separate IMPLEMENT worker task.
3. After implementation passes, separately authorize/run one bounded Chernobylite acceptance canary.
4. Only after that canary and independent System Audit PASS may normal daily Taste production be widened.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
