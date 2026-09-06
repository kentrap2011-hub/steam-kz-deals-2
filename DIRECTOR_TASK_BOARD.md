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

### Completed canary execution attempt
Task:
`WORKER_TASK_TASTE_EXISTING_SINGLETON_CANARY_EXECUTE_01.md`
Durable report:
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`
Final status: `blocked`.

Accepted Director-level outcome from the durable report:
- exact existing singleton task was reused;
- exactly one durable semantic submission was produced: `App_10150` / `Prototype`;
- producer fence and validation gates passed;
- canonical ingest workflow run `34047485340` failed at `Validate, ingest and rebuild taste consumers atomically`;
- no canonical acceptance, fresh receipt or queue delta occurred;
- no second semantic row was accepted;
- exact Scheduled Task is disabled/fail-closed;
- no second producer/task/generation was created;
- no paid API, Copilot or manual semantic inference was used.

Completed canary worker Chat 2 is deletable.

### Next Chat 2 — atomic ingest failure recon
Task:
`WORKER_TASK_TASTE_CANARY_ATOMIC_INGEST_FAILURE_RECON_01.md`
Expected report:
`reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`
Status: `ready_fresh_chat_2`.

Scope:
- determine exact root cause inside failed atomic ingest/rebuild step for the existing Prototype canary;
- determine whether the existing submission can be safely reprocessed after a minimal fix or must remain rejected;
- define exactly one bounded next IMPLEMENT action;
- do not run another game;
- do not create another task/producer/generation;
- no paid API/Copilot/manual patch/validation weakening.

## Chat 1 — visual header date recon
Task:
`WORKER_TASK_VISUAL_HEADER_DATA_DATE_RECON_01.md`
Expected report:
`reviews/worker_reports/visual-header-data-date-recon-01.md`
Mode: `READ-ONLY / RECON`
Status: `ready_or_running_chat_1`.

Goal: determine exactly why the header still shows `Данные: 31 авг., 00:37` after giveaway publication recovered, and whether that label is misleading under section-level freshness.

## Giveaway publication
User has verified on Android that the free giveaway is visible again. Incident is user-visible recovered.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Fresh Chat 2 investigates only the atomic Taste ingest failure and returns one bounded implement action.
2. Chat 1 continues the header-date recon independently.
3. Do not run another semantic game or widen Taste throughput before the ingest failure is understood and explicitly fixed.
