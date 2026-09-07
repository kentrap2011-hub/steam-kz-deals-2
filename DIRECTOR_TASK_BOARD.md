# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not infer that a newly assigned worker task has actually been launched merely because the task command was prepared. Treat a slot as running only after the user says the new chat was created/sent the task or provides equivalent confirmation.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Taste — logic implemented, production materialization still pending
Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

### Chat 2 — pre-AI deal contract guard IMPLEMENT
Task:
`WORKER_TASK_TASTE_PRE_AI_DEAL_CONTRACT_GUARD_FIX_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/taste-pre-ai-deal-contract-guard-fix-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `worker_claimed_finished_but_required_report_missing`.

Director checked only the exact expected report after the user said both chats finished. The report is absent from `main`.

Existing Chat 2 must self-verify its own work and save the exact required report. Director will not reconstruct outcome from commits/logs/Actions.

Hard invariants remain:
- no new Taste canary in this task;
- existing producer remains disabled/fail-closed;
- old Prototype result must not be reused;
- no second task/producer/generation;
- no paid API or Copilot.

## Chat 1 — main list freshness recon
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_FRESHNESS_RECON_01.md`
Expected report:
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `worker_claimed_finished_but_required_report_missing`.

Director checked only the exact expected report after the user said both chats finished. The report is absent from `main`.

Existing Chat 1 must self-verify its own recon and save the exact required report. Director will not reconstruct the diagnosis from code/logs.

User-visible evidence remains:
- giveaway works;
- header shows old date;
- first three visible main-list games show `скидка закончилась`.

Task `WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md` remains SUPERSEDED / DO NOT RUN.

## Giveaway publication
User has verified on Android that the free giveaway is visible again.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Existing Chat 1 performs only durable closeout for `visual-main-list-freshness-recon-01` and writes the exact report.
2. Existing Chat 2 performs only durable closeout for `taste-pre-ai-deal-contract-guard-fix-implement-01` and writes the exact report.
3. Do not delete either worker chat until the exact report exists.
4. Do not start new work in either slot until Director consumes both reports.
