# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- `ЧАТ 1` and `ЧАТ 2` are reusable worker slots, not monotonically increasing task numbers.
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

### Concurrent live-profile binding fix — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`
Report: `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
Final status: `complete_ready_for_real_canary_acceptance`.

### Real Chernobylite acceptance — DURABLY CLOSED AND ACCEPTED
Task: `WORKER_TASK_TASTE_CHERNOBYLITE_REAL_CANARY_ACCEPTANCE_02.md`
Report: `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`
Final status: `complete_canary_accepted_ready_for_system_audit`.

Accepted result:
- exactly one real semantic result was generated for Chernobylite / AppID 1016800;
- result was accepted and canonically ingested;
- receipt/cache/overlay advanced;
- active inbox was consumed;
- App_1016800 left the pending queue;
- no second game or second semantic result was produced;
- existing Scheduled Task remained the only semantic producer and was restored to DAILY 01:00 Europe/Samara;
- no backlog widening occurred.

### Taste post-canary audit Stage 1 — CLOSED
State report: `reviews/worker_reports/taste-post-canary-state-audit-stage1-01.md`
Final: `PASS_STAGE1_STATE`.

Runtime report: `reviews/worker_reports/taste-post-canary-runtime-audit-stage1-01.md`
Final: `PASS_STAGE1_RUNTIME`.

Runtime note:
- worker-side `automations.peek()` and explicit task-list output were compacted as `Skipped 1 message` and could not be read by that worker;
- this was not evidence of a Scheduled Task failure;
- user manually verified in ChatGPT Tasks UI that the target task exists, is active, is scheduled DAILY 01:00 Europe/Samara, and there is no second Taste Semantic Producer task;
- Director recorded that verification explicitly as manual UI evidence.

## Current user goal
Move Taste safely to normal daily operation, while allowing the live game-taste profile to keep changing in parallel.

Permanent operating requirement from the user:
- the user must not need to pause profile updates;
- no mixed-version result may be created;
- bounded retry/fail-closed behavior is acceptable;
- no unbounded retry loop or manual repair should be required.

## Interrupted audit history
The original broad post-canary audit was interrupted twice and never reached a final status.

The first split attempt also failed to create durable reports. Subsequent micro-audits use strict transactional execution:
- report created first;
- result persisted after every check;
- no repeated reading without a named reason.

## CURRENT NEXT — two parallel micro-audits, stage 2
Status: `prepared_ready_for_parallel_dispatch`.

### CHAT 1 — saved-result consistency Stage 2
Task:
`WORKER_TASK_TASTE_POST_CANARY_STATE_AUDIT_STAGE2_01.md`

Expected report:
`reviews/worker_reports/taste-post-canary-state-audit-stage2-01.md`

Only four checks:
- accepted App_1016800 bindings exactly match the accepted tuple;
- cache/overlay/index/runtime references are mutually consistent;
- no second/fallback canonical Chernobylite result exists;
- no manual state repair is required for the accepted result.

Final decision:
- `PASS_STAGE2_STATE`, or
- `FAIL_STAGE2_STATE`.

### CHAT 2 — live-profile and guardrails Stage 2
Task:
`WORKER_TASK_TASTE_POST_CANARY_GUARDRAIL_AUDIT_STAGE2_01.md`

Expected report:
`reviews/worker_reports/taste-post-canary-guardrail-audit-stage2-01.md`

Only four checks:
- exact immutable live-profile freeze; stale committed projection is not authority;
- safe behavior under profile changes before/after freeze and bounded fail-closed retry under continuous churn;
- generation 2 / exact binding / V5 acceptance fences remain active;
- evidence, normalized-factor and price-blind/no-commercial-review-sentiment protections remain active.

Final decision:
- `PASS_STAGE2_GUARDRAILS`, or
- `FAIL_STAGE2_GUARDRAILS`.

## Next sequence
1. Run both Stage-2 micro-audits in parallel.
2. Director reads only both exact durable reports.
3. If both PASS, prepare one final short Stage 3 only for any still-uncovered audit criteria (including no paid dependency / no unresolved daily-operation blocker), rather than rerunning prior checks.
4. Only after all required short stages PASS may Director conclude the system audit and prepare the final bounded step toward normal daily Taste operation.
5. Any IMPLEMENT change still requires separate user approval.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
