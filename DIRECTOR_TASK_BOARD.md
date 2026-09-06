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

## Taste — historical scheduler absent from current runnable surface
Completed recon: `WORKER_TASK_TASTE_SEMANTIC_RUNTIME_RECOVERY_RECON_01.md`
Report: `reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`

Recovered historical producer:
- name: `Taste Semantic Producer`
- task/jawbone ID: `0a51664a-af13-5b98-8c25-d589f0d247c9`
- historical owner: ChatGPT scheduled-task service
- historically proven recent accepted production through 2026-09-01.

User owner-scope evidence received 2026-09-06 from current ChatGPT Tasks UI:
- `Активно`: no user-created active tasks shown;
- `Приостановленные`: no `Taste Semantic Producer` shown;
- completed screenshot is partial and is not used to claim global deletion.

Operational classification: historical producer is absent from the current runnable scheduler surface. Do not wait for another enabled/disabled screenshot and do not create a duplicate blindly.

Copilot zero-cost Rev02 does not provide a replacement: its durable report is `blocked` before successful semantic inference.

Next Taste task:
`WORKER_TASK_TASTE_ZERO_COST_RUNTIME_MIGRATION_RECON_01.md`
Expected report:
`reviews/worker_reports/taste-zero-cost-runtime-migration-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_2`.
Goal: identify one realistic zero-extra-cost singleton migration/recovery path, or classify the external blocker, while preserving GitHub queue/control plane and `TASTE-SEMANTIC-RESULT-V5`.

## Chat 1 — fresh giveaway recurrence recon
Task: `WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`
Expected report: `reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `running_or_ready_chat_1`.

Real Android production incident:
- `Данные: 31 авг., 00:37`
- active `🎁 Раздачи (!)` tab
- warning `Раздачи временно не удалось проверить полностью.`
- no giveaway cards visible.
Do not request another site verification until diagnosis/fix reaches the user gate.

## Chat 2 — Copilot zero-cost pilot revision 02 — CLOSED BLOCKED
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_02.md`
Durable report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`
Status: `blocked_closed`.

The pilot stopped before successful Copilot semantic inference. The child report `reviews/worker_reports/epic-ru-availability-source-probe-02.md` is absent by design and must not be fabricated. No paid fallback or unauthorized autonomous IMPLEMENT is accepted. This worker chat is durably free/deletable.

Replacement Chat 2 takes the Taste zero-cost runtime migration recon above.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Fresh Chat 2 performs the bounded Taste zero-cost runtime migration recon.
2. Chat 1 continues the giveaway recurrence recon independently.
3. Do not create a Taste replacement scheduler until the migration recon proves a safe singleton route.
4. Do not ask the user to verify Taste or giveaways on site until the respective gates are actually ready.
