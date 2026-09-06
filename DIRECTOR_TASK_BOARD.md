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
- current Taste blocker: canonical semantic runtime not advancing current V5 scope.

## Chat 1 — Taste semantic runtime recovery recon
Task: `WORKER_TASK_TASTE_SEMANTIC_RUNTIME_RECOVERY_RECON_01.md`
Mode: `READ-ONLY / RECON`
Expected report: `reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`
Status: `ready_or_running_chat_1`.
Stay strictly on Taste unblock path.

## Chat 2 — zero-cost Copilot pilot revision 02
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_02.md`
Expected pilot report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`
Expected semantic report: `reviews/worker_reports/epic-ru-availability-source-probe-02.md`
Status: `worker_claimed_finished_but_durable_closeout_missing`.
Director checked both exact paths after user completion signal; both were absent on `main`. Do not close/delete this chat yet. Send the existing Chat 2 back to self-verify and durably close its current task; Director should not reconstruct logs/commits.

## Fresh user-visible giveaway recurrence
Task prepared: `WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`
Expected report: `reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `queued_next_free_worker_slot`.

User screenshot on 2026-09-06 shows published mobile site:
- `Данные: 31 авг., 00:37`
- active `🎁 Раздачи (!)` tab
- warning `Раздачи временно не удалось проверить полностью.`
- no giveaway cards visible.

Treat as real production recurrence. Exact cause is not yet established. Do not weaken fail-closed behavior or manually patch cache. Once a worker slot is durably free, investigate immediately before ordinary backlog work.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Existing Chat 2 must finish its own durable revision-02 pilot closeout first.
2. First durably free worker slot after that takes `WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md` unless Taste requires an immediate user gate.
3. Chat 1 remains on Taste runtime recovery independently.
4. Do not ask the user to re-check giveaways until recurrence is diagnosed/fixed and published-site verification is warranted.
