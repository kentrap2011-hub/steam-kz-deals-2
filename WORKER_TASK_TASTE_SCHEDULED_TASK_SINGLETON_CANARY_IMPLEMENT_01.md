# WORKER TASK — Taste Scheduled Task Singleton Canary Implement 01

## Task ID
`taste-scheduled-task-singleton-canary-implement-01`

## Mode
`IMPLEMENT`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Required report
`reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

## Prerequisite recon
`reviews/worker_reports/taste-zero-cost-runtime-migration-recon-01.md`

Final recon classification: `ready_for_bounded_implement`.

## Goal
Restore the missing Taste semantic runtime through **exactly one** replacement ChatGPT Scheduled Task instance at zero additional API/inference cost, but only far enough to prove a one-row production canary through the existing canonical GitHub queue/inbox/ingest path.

Do not widen throughput in this task.

## Hard invariants
- GitHub remains the sole control-plane owner for queue scope, retry/unresolved state, completeness, validation, persistence, checkpoint/merge behavior, downstream rebuild and final ranking.
- Preserve `TASTE-SEMANTIC-RESULT-V5` result semantics.
- Preserve the existing canonical queue and `data/ai_inbox/taste/*.json` submission path.
- Exactly one accepted semantic producer generation/instance may exist at a time.
- The historical task `Taste Semantic Producer` / `0a51664a-af13-5b98-8c25-d589f0d247c9` is absent from the current runnable Tasks surface and must never be accepted in parallel if it unexpectedly reappears.
- No separately billed OpenAI API and no `OPENAI_API_KEY` usage.
- Do not use Copilot as a fallback.

## Required implementation

### A. GitHub-owned singleton acceptance fence
Add the smallest durable GitHub-owned producer-instance/generation fence to the **existing Taste inbox transport envelope**.

Requirements:
- there is one canonical active producer instance/generation identifier owned by repository truth;
- the replacement ChatGPT task must echo that identifier in the top-level inbox submission envelope;
- canonical ingest validates the identifier **before** accepting/persisting any `results[]` rows;
- missing, legacy, stale or wrong producer identifiers fail closed;
- correct current identifier proceeds through all existing V5/binding/appid/fingerprint/context validation unchanged;
- do not put producer identity into V5 result semantics if it can remain transport metadata;
- do not create a second queue, second inbox, alternate store or alternate persistence path.

Add focused regressions proving at minimum:
1. correct active producer id + otherwise valid current batch can be accepted;
2. wrong producer id is rejected before persistence;
3. missing/legacy producer id is rejected before persistence;
4. existing stale binding/current-scope rejection still works;
5. existing V5 semantic validation is unchanged.

### B. Create exactly one replacement ChatGPT Scheduled Task instance
Use the current ChatGPT Scheduled Tasks capability and the already connected GitHub app.

Requirements:
- create **one and only one** replacement task instance;
- never recreate a second task if creation succeeds; record its non-secret task/jawbone identity in the durable report/repository runtime metadata where appropriate;
- bind it to the canonical active producer instance/generation from section A;
- it may read only the GitHub-prepared current Taste work and may submit only through `data/ai_inbox/taste/*.json`;
- it must not write caches, ranking outputs, queue state, completeness state or any product artifact directly;
- it must not choose new project tasks;
- it must not use paid API credentials or ask the user for secrets;
- do not change the user's GitHub app permissions during this task.

For the canary, hard-limit the scheduled producer itself to **exactly one currently queued V5 row total** before Director review. It must not process a second row merely because another recurrence occurs.

Use the same task instance for future production widening; do not create a disposable second canary producer.

If a temporary one-time first-run schedule is the safest way to prove the canary, that is allowed **only if the same task/jawbone instance is retained for later update to the canonical recurring schedule**. Do not invent a permanent cadence. If an exact recurring cadence is needed in this task, derive it from canonical repository/historical durable evidence rather than guessing.

### C. Live one-row canary
Prove the complete real path:
1. select exactly one row from the **current canonical queue** at execution time;
2. the replacement task performs semantic inference for only that row under the existing Taste instructions/contract;
3. it writes exactly one bounded inbox submission carrying the active producer identifier;
4. canonical GitHub ingest processes it;
5. a fresh durable receipt/current queue state proves acceptance of that row (or an honest fail-closed rejection with exact reason);
6. no other current semantic row is processed by this task.

Do not assume the queue remains at 701; bind to the actual current source scope/counts at execution time.

After the first canary attempt, prevent any second semantic row from being processed before Director review. Prefer pausing/guarding the same task instance or an equivalent fail-closed one-shot limit rather than deleting/recreating it.

## Failure handling
If Scheduled Tasks cannot perform the required unattended GitHub read/write on this account/surface, or the task hits an approval/product/tool limitation:
- stop fail-closed;
- do not weaken GitHub permissions/validation;
- do not switch to paid API or Copilot;
- do not create a second producer;
- preserve the one created task instance if safe, but ensure it cannot process another row;
- report exact non-secret blocker.

If the semantic output is invalid or canonical ingest rejects it:
- do not manually patch cache/state;
- do not bypass ingest;
- do not process another row;
- record the exact rejection and close blocked.

## Forbidden
- No second scheduler/task/producer.
- No queue redesign.
- No manual processing of the semantic backlog.
- No more than one current queue row in the live canary.
- No direct cache/ranking/product writes by the ChatGPT task.
- No paid OpenAI API.
- No Copilot fallback.
- No weakening fail-closed validation.
- No unrelated Taste product/ranking changes.
- No autonomous widening after canary success.
- No next major task.

## Required report
Write exactly:
`reviews/worker_reports/taste-scheduled-task-singleton-canary-implement-01.md`

The report must contain enough final evidence for Director acceptance without independent technical re-investigation:
- implementation commits;
- active producer instance/generation identifier (non-secret);
- focused regression results;
- replacement ChatGPT task name and task/jawbone ID (non-secret);
- proof only one replacement task instance was created;
- exact canary queue key/appid or other non-secret row identity;
- scheduled-task execution outcome;
- inbox submission path/commit if created;
- canonical ingest run/result;
- fresh receipt/current queue delta if accepted;
- explicit proof no second semantic row was processed;
- explicit final state of the replacement task after the canary (paused/guarded/otherwise unable to process another row before Director review);
- confirmation no paid API/Copilot/second producer/direct product writer was used;
- exact final status, one of:
  - `complete_canary_accepted`
  - `blocked`

Even on failure, always save this report before stopping.
