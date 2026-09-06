# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Review checkpoint
- Latest System Audit: `reviews/system_audits/director-orchestration-phase2a-audit-01.md` — accepted.
- `system_audit_due: false` now; recurring giveaway incident will require audit trigger evaluation after stabilization.
- `material_changes_since_last_system_audit: 1`.
- `taste_integrated_production_verification_pending: true`.

## Taste — zero-cost migration recon COMPLETE
Completed recon:
`WORKER_TASK_TASTE_ZERO_COST_RUNTIME_MIGRATION_RECON_01.md`

Durable report:
`reviews/worker_reports/taste-zero-cost-runtime-migration-recon-01.md`

Final classification:
`ready_for_bounded_implement`.

Accepted Director-level conclusion from the durable report:
- historical ChatGPT producer is absent from the current runnable scheduler surface;
- Copilot Rev02 is not a proven replacement;
- preferred zero-extra-cost path is exactly one replacement ChatGPT Scheduled Task using the existing connected GitHub app;
- GitHub remains the canonical control plane and `TASTE-SEMANTIC-RESULT-V5` remains unchanged;
- before production widening, GitHub needs a producer-instance/generation acceptance fence and exactly one live one-row canary.

Completed recon worker Chat 2 is deletable.

### Next Chat 2 — bounded Taste singleton canary IMPLEMENT
Task:
`WORKER_TASK_TASTE_SCHEDULED_TASK_SINGLETON_CANARY_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`
Mode: `IMPLEMENT`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_2`.

Scope is intentionally bounded:
- add GitHub-owned active producer instance/generation fence to the existing inbox transport envelope;
- create exactly one replacement ChatGPT task instance, never a second producer;
- process at most one current queue row total;
- require canonical GitHub ingest/receipt proof;
- after first attempt, same task instance must be paused/guarded/equivalently unable to process a second row before Director review;
- no throughput widening;
- no paid OpenAI API;
- no Copilot fallback;
- no queue/ranking/product redesign.

## Chat 1 — giveaway recurrence recon DURABLE CLOSEOUT MISSING
Task:
`WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`
Expected report:
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `worker_claimed_finished_but_required_report_missing`.

Director checked only the exact expected report path after the worker completion claim; it is absent from `main`. Director will not reconstruct the diagnosis from commits/logs/Actions. Existing Chat 1 must self-verify and write the required durable report, even if final status is blocked.

Real Android production incident remains open until durable diagnosis and later fix/user verification:
- `Данные: 31 авг., 00:37`
- active `🎁 Раздачи (!)` tab
- warning `Раздачи временно не удалось проверить полностью.`
- no giveaway cards visible.

Existing Chat 1 is not deletable yet.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Existing Chat 1 performs only its own durable closeout and writes the exact missing giveaway recon report.
2. Fresh Chat 2 performs the bounded Taste singleton one-row canary implementation.
3. Do not create any second Taste scheduler/producer and do not widen Taste throughput before Director consumes the canary report.
4. Do not ask the user to verify Taste or giveaways on site until the respective gates are actually ready.
