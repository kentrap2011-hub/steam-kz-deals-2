# Normal Taste semantic producer 01 — worker report

Date: 2026-09-12
Worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`

## Final status

`blocked_requires_followup`

## START gate and scope

The worker started from current `main` and completed the repository START gate before task-specific implementation work:
1. `CHAT_PROTOCOL.md`;
2. `CHAT_CONTEXT.md`;
3. `CURRENT_TASK.md`;
4. `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md` as the first task-specific file;
5. `PROJECT_ROUTES.md` and only the Taste-specific contracts/reports required by the worker.

Authorized scope remained limited to the normal Taste semantic producer and linked age-priority ordering. No unrelated repository redesign was performed.

## Architecture preflight

Current control/data-plane ownership remains valid:
- GitHub/repository state owns deterministic queue construction, durable pinning and canonical ingest;
- the single existing Scheduled ChatGPT producer is `Taste Semantic Producer`, id `6aa032f37e688191a5c9a1a83f91c5d9`;
- `scripts/taste_pinned_work_unit.py` is the existing active pinned-work-unit mechanism and already enforces `CANONICAL_BATCH_SIZE = 10`, exact producer id/generation, unique ordered rows and immutable work-unit hash binding;
- `scripts/process_taste_inbox.py` uses that pin for transactional result validation, canonical rebuild and active-pin transition;
- a second producer/scheduler is neither required nor allowed.

The correct implementation surface, once the lifecycle gate is clear, is therefore the existing pinned-work-unit mechanism, not a parallel queue/scheduler.

## Canonical queue/state

Canonical prepared semantic queue:
- `data/production/pre_ai/chatgpt_taste_queue.jsonl`.

Canonical accepted Taste state used for successful-evaluation age:
- `data/cache/taste_fit.json`;
- contract: `config/taste_cache_entry_contract.json`;
- accepted evaluation timestamp: `evaluated_at_utc`.

Canonical active work-unit state:
- `data/production/pre_ai/taste_active_work_unit.json`.

Canonical result handoff/ingest path:
- durable result package under `data/ai_inbox/taste/`;
- `scripts/process_taste_inbox.py` / established Taste ingest path;
- canonical receipts under `data/cache/taste_ingest_receipts/`.

## Required future ordering

The linked age-priority task has a proven timestamp authority. For each newly constructed work-unit, the deterministic selection key must be:
1. no successfully accepted canonical Taste result for the exact Taste subject key;
2. then accepted keys ordered by ascending canonical `evaluated_at_utc` (oldest successful accepted evaluation first);
3. exact Taste subject key as stable deterministic tie-breaker, with exact appid only if another stable tie-break is required.

Queue time, pin time, source-mailing time, inbox arrival, Git commit time, failed/rejected attempts, price, discount, reviews, wishlist, popularity and ChatGPT choice must not affect this order.

The currently active pin is explicitly excluded from reordering; age-priority may apply only when constructing a later new pin.

## Blocking lifecycle proof

The linked task contains a hard implementation gate: do not implement age-priority until the currently in-flight exact 10-item work-unit reaches terminal verified state.

Current `main` still contains an active 10-item pin:
- producer: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`;
- prepared: `2026-09-10T13:46:39+00:00`;
- cardinality: `10`;
- `ordered_work_unit_sha256`: `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`.

The latest terminal receipt is `data/cache/taste_ingest_receipts/ba86bfdcf8365dfa0195.json`. It accepted 10 results from the preceding grandfathered `manual-throughput-drain-01-batch-001.json`, but all ten were non-reusable against newer live identity (`current_reusable_result_count = 0`). Its lifecycle block says:
- `transition_status = prepared_next_active_pin`;
- `next_work_unit_sha256 = 31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`.

Therefore that terminal receipt created the current active pin; it is not a receipt for the current active pin.

`data/cache/taste_ingest_receipts/latest_runtime_status.json` still points to batch `ba86bfdcf8365dfa0195` at `2026-09-10T13:46:39+00:00`. There is no later terminal receipt for the active work-unit and the canonical `data/ai_inbox/taste/` directory is absent on current `main`.

This proves the lifecycle precondition is not yet satisfied. Implementing age-priority now would violate the linked task's explicit active-pin preservation rule.

## Work-unit size and deterministic behavior

The existing pin implementation already bounds a work-unit to at most 10 rows (`CANONICAL_BATCH_SIZE = 10`) and preserves an already-active pin via `ensure_active_pin` instead of constructing a competing unit. The missing authorized change is age-priority selection for the *next newly constructed* pin after the current exact pin reaches terminal verified state.

No Chernobylite/single-game hardcoding was added in this worker.

## Retry/idempotency and persistence

Existing invariants remain unchanged:
- result documents are bound to the exact pinned work-unit SHA and authority commit;
- ordered result identity must match the pin row-for-row;
- duplicate keys are rejected;
- active pin retirement requires proven exact-pin identity;
- canonical consumer rebuild happens after ingest;
- retries cannot legitimately create a second canonical work-unit while the current active pin exists.

No manual queue, cache, receipt or result mutation was performed.

## Files changed

Changed by this worker:
- `reviews/worker_reports/taste-queue-age-priority-order-01.md` — report-first lifecycle/timestamp authority proof; commit `6da7f006497fc6a3d849e14c9b2ed20644d47c44`;
- `reviews/worker_reports/taste-normal-semantic-producer-01.md` — this parent report;
- `CURRENT_TASK.md` — worker lifecycle/status record (final closeout commit recorded there when written).

Production source files changed: **none**.
Runtime queue/cache/receipt/pin files changed: **none**.
Scheduled Task changed: **no**.

## Verification performed

Because the linked lifecycle gate forbids source implementation before the active exact-10 unit is terminal, the implementation-specific regressions (new ordering, next-unit reconstruction, retry after new ordering) were intentionally not created or run. Running them against an unauthorized source change would violate the task.

Read-only canonical verification performed against current `main`:
- active pin exists and validates structurally as a 10-row `TASTE-PINNED-WORK-UNIT-V1` owned by the existing producer;
- active pin SHA is `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`;
- latest terminal receipt `ba86bfdcf8365dfa0195` explicitly records that SHA as the *next* active unit, not the retired/completed unit;
- latest runtime status has no later accepted batch;
- canonical inbox directory has no durable current-pin submission on current `main`;
- age timestamp authority is available as canonical cache `evaluated_at_utc`;
- report-first commit changed only `reviews/worker_reports/taste-queue-age-priority-order-01.md`.

## Proof of singleton producer / no scheduler change

No Scheduled Task create/update operation was invoked. No workflow, cron, scheduler configuration or producer identity was added or modified. The only permitted producer remains task id `6aa032f37e688191a5c9a1a83f91c5d9` / generation `2` in the pinned-work-unit fence.

The existing Scheduled Task must remain on its current canary-era instructions until this worker is rerun successfully and reaches `complete_ready_for_normal_scheduled_producer`.

## Intended future Scheduled Task instructions — NOT YET AUTHORIZED TO INSTALL

The following is the target instruction body for the same task id after the lifecycle blocker is cleared, implementation/regressions pass, and this worker is rerun to the ready status. It is recorded for handoff completeness but MUST NOT be installed while this report status is blocked:

```text
Operate as the single normal Taste Semantic Producer for repository kentrap2011-hub/steam-kz-deals-2.

1. Read the canonical active pinned Taste work-unit from data/production/pre_ai/taste_active_work_unit.json on main. Do not choose games yourself and do not reorder, skip, replace, expand or split the pinned ordered_rows.
2. If there is no valid active pin, do not fabricate work. Stop without producing semantic results; GitHub-owned control-plane preparation must create the next exact work-unit.
3. Process exactly the ordered_rows in that one active pin, with at most 10 games/items total. Use the canonical Taste profile and semantic bindings frozen by the pin. Resolve the exact queue/game context from the same durable Git authority that contains the active pin and verify key, appid, taste_fingerprint and candidate_context_sha256 before evaluating each row.
4. Perform only the work_required listed for each pinned row. Taste evaluation is price-blind: do not use price, discount, deal history, reviews, wishlist, popularity or purchase ranking as Taste evidence or as a work-order signal.
5. Return one result document in the established Taste result format, preserving the exact pinned row order and exact identity fields. Bind the result to the active ordered_work_unit_sha256 and the exact pin authority commit required by the canonical ingest contract.
6. Persist the result only through the established durable data/ai_inbox/taste/ handoff in this repository. Do not edit data/cache/taste_fit.json, queue files, receipts, projection artifacts or active-pin state manually.
7. Do not start a second work-unit in the same invocation. Do not retry with different games. A retry may only reproduce the same exact active pinned work-unit until canonical ingest proves success and GitHub-owned lifecycle advances it.
8. Do not create or modify schedulers, workflows or other producers. This Scheduled Task is the only ChatGPT Taste producer.
9. If any pin/profile/context/result-binding check fails, fail closed and leave canonical state unchanged.
```

## Recommended cadence after readiness

Intended cadence remains **hourly** (`FREQ=HOURLY`) for the same Scheduled Task, as requested by the worker task. No evidence found in this blocked implementation pass justifies a different normal cadence. This cadence is **not authorized to be applied yet** because source implementation and regression acceptance are blocked by the active-pin lifecycle gate.

## Exact unblock / follow-up

1. Let the existing producer complete work-unit `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` through the existing durable result and canonical ingest path. Do not manually synthesize its result in this worker.
2. Require a terminal verified receipt proving successful completion/retirement of that exact active unit.
3. Rerun `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md` / this parent worker.
4. Then implement age-priority only for newly constructed pins in the existing `scripts/taste_pinned_work_unit.py`, add focused deterministic regressions, verify same-state same-unit/max-10/idempotency/provenance preservation, and only then declare `complete_ready_for_normal_scheduled_producer`.
5. Only after that ready status may the Director replace the prompt/cadence on the existing Scheduled Task id; never create a second task.

Blocker: `current_active_exact_10_work_unit_not_terminal_verified`.
