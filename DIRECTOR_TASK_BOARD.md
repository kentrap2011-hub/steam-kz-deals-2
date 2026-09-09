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
Run exactly one real Chernobylite semantic acceptance canary, then move Taste toward normal daily operation.

Permanent operating requirement from the user:
- the live game-taste profile will continue to be updated in parallel while Taste is operating;
- the user must not need to pause profile updates to let Taste work;
- profile updates are normal operation and the binding route must safely tolerate them without mixing versions or becoming permanently stuck.

## Reconciliation — 2026-09-09
Durable GitHub evidence is authoritative over chat handoff when they conflict.

Verified:
- `reviews/worker_reports/taste-current-main-canary-path-implement-01.md` is complete and proves the fast read-only one-AppID path;
- `reviews/worker_reports/taste-chernobylite-real-canary-execute-01.md` is a later durable result and already proves that a real acceptance attempt stopped at the mandatory live-profile equality gate;
- no later durable worker report exists for a current-live profile-binding fix;
- therefore another unchanged ACCEPTANCE rerun must not be dispatched before the binding route is fixed.

User authorization state:
- user has explicitly authorized exactly one real semantic Chernobylite canary for AppID `1016800` / `App_1016800`;
- that authorization remains recorded for the separate real ACCEPTANCE step after the binding fix is independently validated;
- no repeat user confirmation for that same single canary is required after the fix;
- this authorization does NOT waive safety gates or authorize a second game/backlog widening.

## CURRENT NEXT — concurrency-safe live-profile binding fix
Status: `approved_ready_for_dispatch`.

User separately approved this IMPLEMENT on 2026-09-09 and clarified that profile updates will continue in parallel in normal operation.

Task:
`WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`

Expected report:
`reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`

Required scope:
- fix the lightweight one-AppID path so each tuple uses one exact immutable profile version;
- profile changes before the tuple is frozen must select the new version;
- profile changes after freeze must never create a mixed-version tuple;
- if canonical rules make an older frozen result stale after a profile update, it must fail closed cleanly and the next bounded attempt must use the newer profile without manual repair;
- do not require a user-controlled quiet window or paused profile updates;
- preserve one-AppID preparation and all existing producer-fence/binding/V5/evidence/price-blind safety checks;
- no manual SHA substitution;
- no canonical queue/payload/cache/receipt/inbox hand-edit;
- no semantic execution in the fix task;
- no Scheduled Task mutation or trigger;
- no other game/backlog work;
- no paid OpenAI API, Copilot, paid external service, or external scheduler.

## Next sequence
1. Dispatch `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md` to a NEW bounded worker chat.
2. Wait for exact durable report `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`.
3. If status is `complete_ready_for_real_canary_acceptance`, Director prepares a separate bounded ACCEPTANCE task for exactly one Chernobylite and may dispatch it under the already-recorded single-canary authorization without asking again.
4. If the canary is canonically accepted, launch a NEW independent System Audit worker.
5. Only after System Audit PASS may the SAME recurring producer be widened to normal daily Taste production.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
