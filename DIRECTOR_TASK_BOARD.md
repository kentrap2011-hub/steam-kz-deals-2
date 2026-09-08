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

Runtime result:
- the SAME generation-2 recurring task ran successfully now;
- exactly one result was produced for Chernobylite / AppID 1016800;
- result reached the canonical GitHub Taste inbox;
- no second game/task/backlog processing occurred;
- permanent schedule was restored and task is enabled daily at 01:00 Europe/Samara;
- the new result was not canonically ingested because the active inbox still contains historical generation-1 Prototype file `data/ai_inbox/taste/canary-App_10150-producer-g1.json`;
- whole-inbox producer-fence scanning rejects that historical file before the current gen2 result can be ingested;
- new generation-2 envelope itself was not shown invalid;
- current task remains canary-only.

## USER GOAL — FULL PRODUCTION AT 01:00
User wants the runtime test completed and verified before 01:00 so the 01:00 run can be normal production.
Accepted accelerated sequence now:
1. repair stale historical inbox artifact/lifecycle blocker;
2. canonically ingest the EXISTING Chernobylite gen2 result without semantic rerun if still current;
3. run independent System Audit in a NEW chat;
4. if audit PASS, widen the SAME recurring task before 01:00;
5. verify schedule remains daily 01:00 Europe/Samara.

## AUTHORIZED NEXT — stale inbox repair + existing canary re-ingest
Task: `WORKER_TASK_TASTE_STALE_INBOX_REPAIR_01.md`
Expected report: `reviews/worker_reports/taste-stale-inbox-repair-01.md`
Status: `prepared_for_existing_chat_1`.

Scope:
- confirm exact whole-inbox stale-file blocker;
- preserve old generation-1 evidence, preferably by archive/quarantine/move outside active inbox;
- do not weaken producer validation;
- old-generation files must still fail if present in active inbox;
- re-ingest the EXISTING `canary-app-1016800-gen2.json` through canonical path if still current;
- no ChatGPT semantic rerun;
- no second game/task;
- no backlog widening;
- no paid API/Copilot/external scheduler.

## Next sequence
1. Existing Chat 1 executes `WORKER_TASK_TASTE_STALE_INBOX_REPAIR_01.md`.
2. Director consumes only exact durable report.
3. If `complete_canary_accepted_ready_for_system_audit`, immediately launch NEW independent System Audit worker.
4. If audit PASS, prepare/launch bounded widening of SAME task before 01:00 under already-stated user goal.
5. If repair/audit fails, do not widen; report exact blocker.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
