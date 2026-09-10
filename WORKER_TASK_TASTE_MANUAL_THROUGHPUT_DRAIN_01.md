# WORKER TASK — ONE-OFF TASTE THROUGHPUT / QUEUE-DRAIN PROBE

## Task ID
`taste-manual-throughput-drain-01`

## Mode
`AUTHORIZED ONE-OFF PRODUCTION EXECUTION / EMPIRICAL CAPACITY PROBE`

## Expected report
`reviews/worker_reports/taste-manual-throughput-drain-01.md`

## User authorization
The user explicitly authorized a one-off worker chat to process real queued Taste games in repeated groups of 10, durably recording progress after every 10 accepted games, continuing without asking for confirmation until it can no longer continue safely or the prepared queue is exhausted.

Purpose:
1. reduce the current real Taste queue;
2. empirically learn how many games one worker-chat execution can safely complete;
3. use that observed number later to choose a practical Scheduled Task per-invocation bound.

This authorization is NOT permission to weaken guards, invent candidate selection, create another Scheduled Task, change the existing daily task, use paid services, or process unprepared/noncanonical games.

## Critical interpretation
This is a **one-off manually authorized capacity experiment**, not a replacement production scheduler and not a new canonical daily quota.

The worker must consume only deterministic GitHub-prepared canonical Taste work in canonical order. ChatGPT must not choose games, reorder them, skip difficult items, or create its own backlog.

## Mandatory durability rule
Because the worker may be interrupted by context/tool/runtime limits, durable progress must exist BEFORE semantic work begins and AFTER EVERY accepted batch.

### Step 1 — create report first
The FIRST repository mutation after reading this task must be creation of the expected report containing at least:
- lifecycle: `in_progress`;
- current UTC;
- starting_queue_count: current verified canonical Taste pending count;
- accepted_batches: `0`;
- accepted_games_total: `0`;
- last_committed_batch: `none`;
- stop_reason: `none`;
- next action: validate and process batch 1.

Commit immediately before semantic evaluation. If report creation fails, STOP.

## Existing safety rules remain authoritative
Preserve all proven current protections:
- GitHub owns candidate selection and canonical queue order;
- generation 2 producer contract;
- V5 semantic-result contract;
- current-live-profile immutable pin/freeze and exact binding;
- exact fingerprint/context/semantics/model/profile checks;
- evidence sufficiency;
- normalized taste factors;
- price-blind / no commercial evidence / no review sentiment as fit evidence;
- one-result-per-input strict validation;
- atomic canonical ingest;
- post-ingest verification;
- bounded retry for the SAME exact work;
- fail closed on mismatch;
- GitHub-only durable state;
- no user profile-update pause or quiet window.

## Batch loop
Repeat the following loop automatically without asking the user after each successful batch.

### A. Select exact next batch
Use only the canonical GitHub-prepared Taste queue and its existing deterministic order.

For each batch:
- select the first up to 10 currently uncommitted canonical prepared Taste items;
- never select item 11 for the current batch;
- if 0 remain, finish with `queue_exhausted`;
- record the exact ordered subject keys/AppIDs and all required immutable bindings for this batch in the report BEFORE semantic execution.

If the currently prepared queue/work bindings are stale relative to the active canonical contracts/profile and the existing system requires regeneration/re-preparation, do NOT improvise or silently mix versions. Use only an already-authorized canonical preparation path if it is clearly defined and safe for this exact queue-drain operation; otherwise stop fail-closed with `stale_prepared_work_requires_separate_refresh`.

### B. Process exactly this batch
Run semantic Taste evaluation only for the exact selected <=10 items using the current canonical result contract.

Do not add/drop/reorder items.
Do not use price, discount, wishlist status, commercial inputs, or review sentiment percentage as Taste-fit evidence.

### C. Validate and ingest exactly this batch
Before accepting:
- pass all current producer/binding/V5/evidence/factor validations;
- require exactly one valid result per exact input;
- reject on missing/extra/duplicate/reordered output;
- ingest atomically through the canonical ingest path;
- verify post-ingest that exactly the accepted items were committed and removed/advanced from pending state as defined by the canonical system.

If validation/ingest/post-ingest verification fails, stop. Do not move to the next batch.

### D. DURABLE CHECKPOINT AFTER EVERY ACCEPTED BATCH
Immediately after successful canonical commit of each batch, update and commit the report before beginning another batch.

Record:
- batch number;
- exact ordered AppIDs/subject keys;
- batch size;
- accepted count;
- rejected/failed count;
- canonical ingest receipt/batch id if applicable;
- queue count before batch;
- queue count after batch;
- cumulative accepted_games_total;
- cumulative accepted_batches;
- current UTC checkpoint;
- current profile/model/semantics binding summary;
- whether another batch is safe to start.

Only after this report checkpoint commit succeeds may the worker start the next batch.

If the report checkpoint cannot be committed, STOP even if semantic ingest succeeded; do not start another batch.

## Retry bound
Use only the canonical existing retry allowance for the SAME exact batch/work unit. Never respond to a failure by selecting a different game, widening the batch, increasing the cap, or restarting the whole backlog.

## Natural stop conditions
Stop immediately and finalize the report when any of these occurs:
- queue exhausted;
- context/runtime/tool limitations prevent safe continuation;
- stale/current-profile or immutable-binding mismatch cannot be resolved through an already-authorized canonical path;
- validation fails after allowed retry;
- ingest/post-ingest verification fails;
- repository contention/lock makes continuation unsafe;
- report checkpoint cannot be written;
- any guardrail cannot be proven.

Do not treat a natural stop as failure if all previously checkpointed batches are canonically accepted and safe.

## Final report
On stop, finalize the same report with:
- lifecycle: `complete` or `stopped_safe` or `failed_closed`;
- starting_queue_count;
- ending_queue_count if verifiable;
- accepted_batches;
- accepted_games_total;
- exact list of committed batches;
- stop_reason;
- last fully durable accepted batch;
- whether the next uncommitted item/batch remains safely resumable;
- observed_games_capacity_this_worker_chat: equal to the number of real games canonically accepted during this worker-chat execution;
- explicit note that this observed capacity is empirical evidence, NOT an automatically adopted production limit.

## Boundaries
Allowed:
- real semantic Taste evaluation of canonical prepared queue items;
- canonical validation and ingest for those exact items;
- durable report/checkpoint commits after every batch of up to 10;
- continuing through multiple 10-item batches in the same worker chat until a safe natural stop.

Not allowed:
- modifying the existing Scheduled Task;
- creating another Scheduled Task;
- changing cadence;
- changing canonical contracts/code/config as part of this run;
- choosing games outside canonical prepared order;
- processing more than 10 items in one batch;
- skipping the report checkpoint between batches;
- auto-adopting the observed capacity as a permanent daily limit;
- paid OpenAI API, Copilot runtime, new paid services, or external schedulers.

Then STOP and return control to Director.
