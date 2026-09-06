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

### Next Chat 2 — atomic ingest failure recon
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

## Chat 1 — visual header date recon COMPLETE
Completed task:
`WORKER_TASK_VISUAL_HEADER_DATA_DATE_RECON_01.md`
Durable report:
`reviews/worker_reports/visual-header-data-date-recon-01.md`
Status: `complete`.

Accepted Director-level conclusion:
- visible `Данные: ...` comes from `source_mailing_updated_at_utc` embedded in the deployed visual payload;
- that timestamp means the source mailing snapshot time, not universal page freshness, not deploy time and not giveaway freshness;
- giveaway can legitimately be newer because it refreshes independently;
- the timestamp itself is semantically correct;
- the label `Данные:` is misleading for users because it sounds like freshness of the whole page;
- minimal correct UX fix is label-only: `Данные:` -> `Рассылка:` while keeping exactly the same timestamp field.

Completed recon worker Chat 1 is deletable.

### Next Chat 1 — visual header label IMPLEMENT
Task:
`WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md`
Expected report:
`reviews/worker_reports/visual-header-data-label-implement-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `HIGH_USER_VISIBLE`
Status: `ready_fresh_chat_1`.

Scope:
- change only the frontend label from `Данные:` to `Рассылка:`;
- keep `source_mailing_updated_at_utc` unchanged;
- no schema/data/freshness/giveaway/Taste changes;
- deploy normally;
- require Android verification before final UX closure.

## Giveaway publication
User has verified on Android that the free giveaway is visible again. Incident is user-visible recovered.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Fresh Chat 1 implements only the header label correction.
2. Chat 2 continues only the atomic Taste ingest recon.
3. Do not run another semantic game or widen Taste throughput before the ingest failure is understood and explicitly fixed.
