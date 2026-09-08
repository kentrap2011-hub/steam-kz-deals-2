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
User verification: stale/non-current discounts disappeared and the paid update date advanced.

### Completed Taste task reuse recon — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_COMPLETED_SINGLETON_REUSE_RECON_01.md`
Report: `reviews/worker_reports/taste-completed-singleton-reuse-recon-01.md`
Result: same-id reuse/reactivation of old completed task was not proven.
Old completed task remains preserved and inactive.

### Silent-stall prevention postmortem — DURABLY CLOSED
Task: `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`
Report: `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`
User declined the proposed independent 03:15 watchdog. Date-only freshness visibility remains selected policy.

### Taste active producer restore design — DURABLY CLOSED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
Report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
Final status: `complete_restore_plan_ready`.

### Taste active producer restore implementation — COMPLETE, CANARY ARMED
Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
Report: `reviews/worker_reports/taste-active-producer-restore-implement-01.md`
Final status: `complete_canary_armed_system_audit_pending`.

Accepted result:
- exactly one new recurring `Taste Semantic Producer` was created;
- new task id: `6aa032f37e688191a5c9a1a83f91c5d9`;
- schedule: daily 01:00 Europe/Samara;
- first scheduled run: 2026-09-09 01:00 Europe/Samara;
- old completed task remained untouched;
- canonical producer identity moved to the new task and generation 2;
- first run is restricted to exactly one fresh game: `Chernobylite Complete Edition` / AppID `1016800`;
- no fallback to another game;
- after successful canary, later runs remain no-op until separate widening approval;
- no paid OpenAI API/Copilot/external scheduler;
- no backlog processing started.

Current state: `waiting_for_first_canary_run`.
The canary was armed but had not run when the worker finished.
Do not run System Audit before there is first-run evidence unless there is a separate control-plane concern.
After the 01:00 run, use a NEW independent worker chat for System Audit. Do not reuse the implementation worker for the audit.
Implementation worker Chat 1 can be deleted.

## Superseded watchdog implementation
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md`
Status: `SUPERSEDED_BY_USER_DECISION_DO_NOT_RUN`.
Do not launch it.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_reliability_and_taste_gate`.

## Next decision
1. Wait for the first scheduled Taste canary at 2026-09-09 01:00 Europe/Samara.
2. After that run window, assign a NEW independent worker to verify whether the one-game canary ran and was accepted safely.
3. If the canary is accepted and System Audit passes, separately authorize widening the SAME recurring task to normal daily Taste production.
4. If the canary fails or does not run, diagnose that exact failure without creating another producer.