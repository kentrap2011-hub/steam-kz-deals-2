# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Taste — logic implemented, production materialization still pending
Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- no second producer may be created.

### Chat 2 — atomic ingest failure recon
Task:
`WORKER_TASK_TASTE_CANARY_ATOMIC_INGEST_FAILURE_RECON_01.md`
Expected report:
`reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_or_running_chat_2`.

Scope:
- determine exact root cause inside failed atomic ingest/rebuild step for the existing Prototype canary;
- determine whether the existing submission can be safely reprocessed after a minimal fix or must remain rejected;
- define exactly one bounded next IMPLEMENT action;
- do not run another game;
- do not create another task/producer/generation;
- no paid API/Copilot/manual patch/validation weakening.

## Chat 1 — header-date recon COMPLETE, label-only fix SUPERSEDED
Completed recon:
`WORKER_TASK_VISUAL_HEADER_DATA_DATE_RECON_01.md`
Durable report:
`reviews/worker_reports/visual-header-data-date-recon-01.md`

The prior recommendation to change `Данные:` -> `Рассылка:` was rejected by the user as insufficient because it does not tell whether the displayed main list is actually current.

User additionally observed on Android that the first three games in the main list already show `скидка закончилась`. This is now treated as stronger evidence of a potential stale/degraded main commercial list, not merely a wording problem.

Task `WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md` is **SUPERSEDED / DO NOT RUN** unless explicitly revived by a later Director decision.

### Next Chat 1 — main list freshness recon
Task:
`WORKER_TASK_VISUAL_MAIN_LIST_FRESHNESS_RECON_01.md`
Expected report:
`reviews/worker_reports/visual-main-list-freshness-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_1`.

Goals:
- establish the real last successful refresh of the displayed discounted-games list;
- inspect why the first three visible rows already say their discounts ended;
- determine whether the main list is stale/degraded and what exact gate is preventing freshness;
- determine a truthful user-facing freshness model/date/status;
- prefer separate main-deals/giveaway freshness or an explicit stale warning if a single global timestamp cannot be truthful;
- define exactly one minimal next IMPLEMENT action;
- no code/data/workflow changes in recon.

## Giveaway publication
User has verified on Android that the free giveaway is visible again. Incident is user-visible recovered.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Fresh Chat 1 investigates actual main-list freshness and expired top rows; do not run the old label-only task.
2. Chat 2 continues only the atomic Taste ingest recon.
3. If the main list is stale, fix real freshness/publication truth before cosmetic timestamp wording.
4. Do not run another semantic game or widen Taste throughput before the ingest failure is understood and explicitly fixed.
