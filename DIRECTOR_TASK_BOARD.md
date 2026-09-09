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
- Worker must checkpoint unresolved work at least roughly every 15 minutes.
- Long external runs must be recorded immediately with exact run/job id.
- Worker may poll an external run at most 3 times / roughly 10 minutes in one response cycle.
- If still running, report lifecycle becomes `waiting_external` and worker returns control instead of silently waiting.
- A report older than ~20 minutes with no recorded external run explaining the wait is presumptively stalled and worker may be replaced.
- Replacement worker must first determine whether the stale worker launched anything after its last checkpoint; no blind duplicate retries.

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

### Stale inbox repair — COMPLETE REPAIR, CANARY STILL STALE
Task: `WORKER_TASK_TASTE_STALE_INBOX_REPAIR_01.md`
Report: `reviews/worker_reports/taste-stale-inbox-repair-01.md`
Final status: `needs_followup`.

### Refreshed Chernobylite canary rerun — STOPPED SAFELY
Task: `WORKER_TASK_TASTE_REFRESHED_CANARY_RERUN_01.md`
Report: `reviews/worker_reports/taste-refreshed-canary-rerun-01.md`
Final status: `needs_followup`.

### Pre-AI profile sync + same-canary rerun — ONE ATTEMPT FAILED AT COMMIT/PUSH
Task: `WORKER_TASK_TASTE_PREAI_PROFILE_SYNC_AND_CANARY_RERUN_01.md`
Report: `reviews/worker_reports/taste-preai-profile-sync-and-canary-rerun-01.md`
Final status: `needs_followup`.

Accepted final result:
- exactly one authorized canonical pre-AI synchronization attempt was used;
- rerun job id `102329869100` failed after deterministic generation at commit/push;
- `main` advanced concurrently and the workflow rebase/push path encountered conflicts;
- regenerated state was not durably committed to `main`;
- no manual generated-file/hash patching occurred;
- no second rebuild attempt occurred;
- Chernobylite semantic analysis was NOT started;
- no other game/task/backlog work occurred;
- same generation-2 Scheduled Task remains the only semantic producer with permanent DAILY 01:00 Europe/Samara schedule.

## Current user goal
Restore safe full daily Taste production using the existing generation-2 Scheduled Task. Runtime canary must be canonically accepted before independent System Audit and later widening.

## ACTIVE — bounded sync retry after repository contention, REPLACE STALLED CHAT 1
Task: `WORKER_TASK_TASTE_PREAI_SYNC_RETRY_AFTER_CONTENTION_01.md`
Expected report: `reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md`
Status: `replace_stalled_chat_1_with_new_chat_1_using_same_report`.

Last durable checkpoint from stale Chat 1:
- report lifecycle `in_progress`;
- checkpoint commit time `2026-09-09T08:41:22Z` (12:41:22 Europe/Samara);
- at that checkpoint no active/queued GitHub Actions writer existed;
- live profile and prepared profile still differed;
- the one retry authorized by this task had NOT yet been launched as of that checkpoint;
- no Chernobylite semantic run or Scheduled Task mutation had occurred as of that checkpoint.

Because the old worker then went ~1h45 without another checkpoint and no external run was recorded to explain the wait, user chose to replace it.

Important recovery rule:
- the NEW Chat 1 must NOT assume nothing happened after the stale checkpoint;
- first inspect current GitHub/repository truth for any production/pre-AI retry launched after `2026-09-09T08:41:22Z` that belongs to this task;
- if found, that attempt consumes the single retry authorization and must be consumed/verified; do not launch another;
- only if no such attempt exists may the new worker launch the one authorized retry.

Task file has been hardened to require `WORKER_ANTI_STALL_PROTOCOL.md`:
- checkpoint at least every ~15 minutes;
- external run id saved immediately;
- max ~10 minutes / 3 polls per response cycle;
- then `waiting_external` and return control rather than hanging.

## Next sequence
1. NEW Chat 1 resumes the SAME task/report from repository truth under anti-stall protocol.
2. If an async retry is launched and remains running, worker returns `waiting_external` with exact run/job id rather than staying open.
3. Director later consumes only the exact durable report/status.
4. If `complete_canary_accepted_ready_for_system_audit`, launch NEW independent System Audit worker.
5. Only after System Audit PASS may the SAME recurring producer be widened to normal daily production.
6. If retry is blocked/fails, do not widen and do not create another producer.

## Superseded watchdog
`WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01.md` remains superseded by user decision.

## Giveaway ITAD identity
`WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md` remains queued after the current Taste gate.
