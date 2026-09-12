# Taste queue age-priority order 01 — worker report

Date: 2026-09-12
Observed at: 2026-09-12T09:02:29Z
Worker task: `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`

## Final status

`failed_closed_root_cause_proven`

## Lifecycle state at implementation gate

The linked task explicitly permits implementation only after the currently active exact 10-item Taste work-unit reaches a terminal verified state. That gate is not satisfied on current `main`.

Canonical active pin:
- path: `data/production/pre_ai/taste_active_work_unit.json`;
- schema: `TASTE-PINNED-WORK-UNIT-V1`;
- producer: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`;
- cardinality: `10`;
- `ordered_work_unit_sha256`: `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`;
- `prepared_at_utc`: `2026-09-10T13:46:39+00:00`.

The latest completed receipt is `data/cache/taste_ingest_receipts/ba86bfdcf8365dfa0195.json`. It is terminal and accepted, but it belongs to the preceding grandfathered `manual-throughput-drain-01-batch-001.json` package. Its `pin_lifecycle.transition_status` is `prepared_next_active_pin`, and its `next_work_unit_sha256` is exactly `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`. Therefore that receipt proves creation of the current active pin; it does not prove completion of that current pin.

`data/cache/taste_ingest_receipts/latest_runtime_status.json` records the previous accepted semantic execution at `2026-09-10T13:46:39+00:00`, batch `ba86bfdcf8365dfa0195`, result count `10`. There is no later terminal receipt proving successful ingestion of the current active pin. The canonical inbox directory is absent on current `main`, so there is also no pending durable result package to ingest for that pin.

Conclusion: the exact current 10-item pin is still the active, not-yet-terminal work-unit. Per the worker task, it must remain byte-for-byte/order-for-order protected from age-priority reordering.

## Canonical last-successful-evaluation timestamp authority

The timestamp authority itself is proven and is not the blocker.

Canonical source:
- state: `data/cache/taste_fit.json`;
- contract: `config/taste_cache_entry_contract.json`;
- field: accepted cache entry `evaluated_at_utc`.

Why this is authoritative:
- `data/cache/taste_fit.json` is the canonical accepted Taste cache used by the production projection/consumer path;
- current accepted cache-entry schemas require `evaluated_at_utc`;
- a game counts as checked only after a successful result is accepted into canonical state;
- queue appearance, pin preparation time, inbox arrival, Git commit time, failed/rejected result, and profile/source timestamps are not used as successful-evaluation age.

Ordering key for a future newly constructed work-unit is therefore:
1. class `0`: no canonical accepted entry exists for the exact Taste subject key;
2. class `1`: canonical accepted entry exists;
3. within class `1`, ascending parsed UTC `evaluated_at_utc` (oldest first);
4. deterministic tie-breaker by exact canonical Taste subject key, then exact appid if required.

No commercial, price, discount, review, wishlist, popularity, or ChatGPT-choice signal is permitted in this key.

## Expected implementation files after lifecycle gate clears

Minimal intended change set:
- `scripts/taste_pinned_work_unit.py` — select a newly constructed pin from the canonical queue using the canonical cache age key, while preserving an already-active pin unchanged;
- one focused regression test file for normal/age-priority producer behavior;
- this report, updated to terminal implementation proof;
- `reviews/worker_reports/taste-normal-semantic-producer-01.md` for the parent worker;
- `CURRENT_TASK.md` lifecycle/status update.

No second scheduler, no second producer, no manual cache/queue/result mutation, and no Scheduled Task edit are part of the implementation.

## Next permitted action

Allow the existing producer `6aa032f37e688191a5c9a1a83f91c5d9` to finish the exact active pin through the established durable result + canonical ingest path. After a terminal verified receipt for work-unit `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` exists and the active-pin lifecycle has advanced/retired it, rerun the age-priority implementation worker before constructing the next new unit under the new ordering policy.

Until then, source implementation is intentionally not started.
