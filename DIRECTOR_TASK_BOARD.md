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

Accepted final result:
- single authorized retry was used: run `34274404165`, attempt `3`, job `102445283223`;
- deterministic collection/validation passed;
- persistence failed because rerunning the historical workflow checked out stale head `d501021...` while current `main` was 31 commits ahead and had changed overlapping generated production/pre-AI files;
- rebase conflicted and no generated commit was pushed;
- prepared Taste profile binding remained stale versus live profile;
- Chernobylite semantic execution did not start;
- no other game, new Scheduled Task, widening, or System Audit occurred;
- another rerun of this same historical workflow path is not authorized or recommended.

## Current user goal
Restore safe full daily Taste production using the existing generation-2 Scheduled Task, but first make one-game canary verification operationally lightweight and based on current `main` rather than historical workflow reruns.

## ACTIVE CLOSEOUT — current-main one-game canary design
Task: `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_DESIGN_01.md`
Report: `reviews/worker_reports/taste-current-main-canary-path-design-01.md`
Status: `design_done_exact_final_status_missing`.

Accepted design substance:
- no existing safe bounded one-AppID current-main preparation path exists as-is;
- full current pre-AI workflow can use current `main` but is too broad and write-producing for this canary;
- smallest safe design is a new workflow_dispatch-only, read-only current-main canary workflow with one required AppID;
- explicit checkout of refs/heads/main;
- bounded one-AppID harness reusing current Taste logic;
- outputs only in runner temp/artifact, no canonical repository writes, no commit/push, no semantic execution;
- current committed snapshots/config are consumed read-only and broad StoreBrowse refresh is not part of the canary;
- historical workflow reruns are explicitly rejected as the normal canary path;
- design expects seconds-to-tens-of-seconds preparation after runner startup rather than a full minutes-class production rebuild, to be measured during implementation.

Protocol closeout issue:
- report lifecycle says `State: done` and commit message says design finished;
- task contract required one exact final status: `complete_design_ready_for_implementation`, `needs_followup`, or `blocked`;
- exact required final status is not present in the durable report.

No IMPLEMENT should start until the same worker updates/re-reads the same report with the exact truthful final status. No further recon is needed.

## Next sequence
1. SAME Chat 1 performs report-only closeout: add exact final status and re-read report.
2. Director consumes only the corrected exact report.
3. If `complete_design_ready_for_implementation`, user may separately authorize IMPLEMENT.
4. After implementation, run one bounded Chernobylite acceptance canary.
5. Only after that canary and independent System Audit PASS may normal daily Taste production be widened.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
