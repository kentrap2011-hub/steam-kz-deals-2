# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Before assigning/reassigning a worker slot, Director must reconcile exactly: current Board -> exact task file -> exact durable report from the immediately preceding step. Do not infer slot state from an old chat history alone.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Taste — logic implemented, production materialization still pending
The Taste Steps 1–3 semantic logic and the independent Taste Reviewer maintenance recommendations are already implemented and regression-covered.

Durable implementation/acceptance report:
`reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`

Current blocking truth from that report:
- semantic scope: 701;
- resolved: 0;
- unresolved: 701;
- publication completeness: false;
- current site is not yet a valid verification target for the new Taste behavior.

A singleton replacement ChatGPT Scheduled Task was then implemented:
`reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

Authoritative existing singleton:
- task title: `Taste Semantic Producer`;
- task instance id: `6a9d6fdddc00819193ed670d782045c4`;
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`;
- producer generation: `1`;
- GitHub-owned producer fence is implemented;
- prior durable state: disabled/fail-closed;
- `last_run_time = null`;
- semantic rows processed: 0.

No second producer may be created.

## Chat 1 — current giveaway incident
Task:
`WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`
Expected report:
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`
Mode: `READ-ONLY / RECON`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `running_chat_1`.

Chat 1 is diagnosing the empty/fail-closed giveaway feed. It is NOT yet the implementation fix. Once its durable recon identifies one bounded root cause/action, the immediate next Chat 1 task is the corresponding IMPLEMENT fix before ordinary backlog work.

User-visible incident evidence:
- `Данные: 31 авг., 00:37`;
- active `🎁 Раздачи (!)` tab;
- warning `Раздачи временно не удалось проверить полностью.`;
- no giveaway cards visible.

Do not ask user to re-check giveaways until diagnosis -> bounded fix -> deploy reaches the user verification gate.

## Chat 2 — Taste existing singleton canary execution
Task:
`WORKER_TASK_TASTE_EXISTING_SINGLETON_CANARY_EXECUTE_01.md`
Expected report:
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `ready_fresh_chat_2`.

This task must reuse the SAME existing Scheduled Task instance `6a9d6fdddc00819193ed670d782045c4`.
It may schedule/enable that same task for one bounded near-future execution if no synchronous `run now` exists, but it must process exactly one semantic row total, then disable/pause/guard the same task before a second row can run.

Hard prohibitions:
- no second Scheduled Task;
- no second producer id;
- no new generation;
- no paid OpenAI API;
- no Copilot fallback;
- no manual semantic processing;
- no throughput widening;
- no UI/giveaway/ITAD work.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Status: `queued_after_current_user-visible_recurrence_and_taste_gate`.

## Stopped route
Separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Next decision
1. Chat 1 finishes giveaway recon, then moves immediately to the bounded giveaway IMPLEMENT fix based on its durable diagnosis.
2. Fresh Chat 2 executes exactly one Taste semantic row through the existing singleton producer and canonical GitHub ingest.
3. Do not widen Taste throughput before Director consumes `reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`.
4. Taste site verification waits for legitimate semantic materialization and regenerated production output.
5. Giveaway site verification waits for diagnosis, fix, deploy, then real Android verification.
