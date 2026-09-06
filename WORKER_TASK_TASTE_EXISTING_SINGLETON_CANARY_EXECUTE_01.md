# WORKER TASK — Taste Existing Singleton Canary Execute 01

## Task ID
`taste-existing-singleton-canary-execute-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`

## Context
This task continues the already implemented Taste singleton canary path. It must reuse the exact existing Scheduled Task instance created by the prior worker.

Prior durable report:
`reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

Existing singleton producer — authoritative:
- task title: `Taste Semantic Producer`
- task instance id: `6a9d6fdddc00819193ed670d782045c4`
- canonical producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
- producer generation: `1`
- current durable report state: disabled/fail-closed, `last_run_time = null`

Existing GitHub producer fence is already implemented. Do NOT create another task/producer/generation.

## Goal
Execute exactly one real semantic canary row through the SAME existing Scheduled Task instance and the existing canonical GitHub inbox/ingest path, then stop before any second row is processed.

This task does not widen production throughput.

## Required first checks
1. Read current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - `reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`
   - current `config/taste_result_contract.json`
   - current canonical Taste queue/inbox/ingest contracts.
3. Inspect the Scheduled Tasks service for the EXACT task instance id `6a9d6fdddc00819193ed670d782045c4`.
4. If that exact task instance is missing or cannot be addressed safely: stop `blocked`. DO NOT recreate it.
5. Confirm repository producer fence still expects generation `1` and the exact producer id above. If not, stop `blocked` unless the mismatch is a narrowly proven accidental drift from the prior implementation; do not invent generation `2`.

## Execution rule — SAME TASK ONLY
Use only the existing task instance `6a9d6fdddc00819193ed670d782045c4`.

If the Scheduled Tasks surface still has no synchronous `run now` action, it is allowed to update/enable THIS SAME task for one bounded near-future scheduled execution, provided:
- no second task is created;
- the task prompt remains hard-limited to exactly one current queue row total;
- the schedule is one-shot or otherwise safely guarded so a second semantic row cannot run before Director review;
- after the first attempt, the same task is disabled/paused/guarded before another row can be processed.

Do not guess a permanent recurring cadence. This task is canary-only.

If the tooling cannot safely schedule/enable the same task for one bounded execution, stop `blocked` and report the exact limitation.

## Live canary
At execution time:
1. Read the actual current canonical queue; do not assume the count is still 701.
2. Select exactly one current queued V5 row using the canonical head/eligible order.
3. The existing `Taste Semantic Producer` task performs semantic inference for that row only.
4. It submits only through the existing canonical `data/ai_inbox/taste/*.json` path with:
   - exact producer id `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
   - producer generation `1`
   - unchanged `TASTE-SEMANTIC-RESULT-V5` semantics.
5. Canonical GitHub ingest validates producer fence, V5 semantics, binding/current-scope constraints and then accepts or rejects normally.
6. Prove the result with durable receipt/current queue delta or the exact fail-closed rejection.
7. No second current semantic row may be inferred, submitted or ingested in this task.

## After first attempt
Immediately ensure the SAME task instance cannot process another row before Director review:
- disable/pause it, OR
- preserve an equivalent fail-closed one-shot guard that is explicitly proven in the report.

Do NOT delete the task. We need to retain the same singleton instance for potential later widening.

## Success criteria
Status `complete_canary_accepted` only if all are true:
- exact existing task instance was reused;
- exactly one semantic row was inferred;
- canonical inbox submission used the active producer id/generation;
- canonical GitHub ingest accepted it;
- fresh durable receipt/current queue evidence proves the one-row acceptance;
- no second row was processed;
- same task instance is safely stopped/guarded after the attempt;
- no paid API, Copilot fallback, second producer, direct cache/ranking/product write or manual semantic processing occurred.

## Failure handling
If anything prevents the real one-row chain:
- stop fail-closed;
- do not create another task;
- do not manually perform semantic inference;
- do not fake an inbox submission;
- do not weaken producer fence or V5 validation;
- do not switch providers;
- do not process a second row;
- save `blocked` with exact non-secret reason.

## Forbidden
- second Scheduled Task;
- second producer id;
- generation 2 or any new generation without a separate Director task;
- more than one semantic row;
- manual backlog processing;
- direct writes to ranking/cache/product outputs by the Scheduled Task;
- paid OpenAI API / `OPENAI_API_KEY`;
- Copilot fallback;
- unrelated Taste/ranking changes;
- giveaway/ITAD/UI work;
- automatic throughput widening;
- next major task.

## Required report
Save exactly:
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`

Required contents:
1. Status exactly one of:
   - `complete_canary_accepted`
   - `blocked`
2. Exact existing Scheduled Task id and proof it was reused, not recreated.
3. Pre-run task enabled/schedule/last-run state.
4. Exact bounded schedule/enable action used, if any.
5. Exact current queue count and selected one-row identity at execution time.
6. Scheduled Task execution outcome.
7. Inbox submission path/commit if produced.
8. Canonical ingest run/result.
9. Fresh receipt and exact queue delta if accepted.
10. Proof no second row was processed.
11. Exact final task state after the canary.
12. Explicit confirmation: no second producer, no paid API, no Copilot, no manual semantic inference, no direct product/ranking/cache writes.

Do not claim full Taste production readiness. This task proves only the singleton one-row canary.
