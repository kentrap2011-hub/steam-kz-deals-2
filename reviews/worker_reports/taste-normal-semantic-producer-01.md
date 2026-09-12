# Normal Taste semantic producer 01 — worker report

Date: 2026-09-12
Worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`
Mode: `IMPLEMENT_AND_MEASURE_THROUGHPUT`

## Current status

`in_progress_throughput_measurement`

The earlier `blocked_requires_followup` conclusion based on the deferred age-priority task/current-active-10 gate is superseded by the corrected worker task. `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md` is not being executed in this run.

## Corrected architecture preflight

The corrected task explicitly authorizes a one-off interactive throughput benchmark, while the previous canonical ownership contract allowed only bounded verification in an interactive chat. Before changing Taste runtime state, that conflict was reconciled canonically:

- `config/execution_ownership_contract.json` — commit `cc680694cbc2357eef53726b61febdafbc71e015`;
- `config/daily_execution_contract.json` — commit `fb34396e2b0acd9750b107d373b1a1cc40b0d080`.

The exception is intentionally narrow:
- GitHub remains control-plane owner for scope, existing queue order, pin authority, retry/completeness and canonical persistence;
- the interactive chat may execute only exact Git-durable pinned Taste work-units for this explicitly authorized one-off measurement;
- each completed checkpoint must be accepted through the existing repository inbox/ingest path before it is counted;
- checkpoint size `10` is measurement-only and is not a production quota or future Scheduled Task limit;
- no second producer/scheduler may be created;
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` must not be changed;
- age-priority ordering remains out of scope.

## Normal mechanism actually used

Existing mechanism is retained rather than creating a parallel producer:

1. GitHub-prepared queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`.
2. Durable active pin: `data/production/pre_ai/taste_active_work_unit.json` (`TASTE-PINNED-WORK-UNIT-V1`).
3. Exact semantic/profile binding: `config/taste_result_contract.json` + pin `profile_identity`/`bindings`.
4. Result handoff: new JSON under `data/ai_inbox/taste/`.
5. Push to that path triggers `.github/workflows/ingest-taste-batch.yml`.
6. Workflow runs producer-fence, V3 contract and transactional-proof validators, then `scripts/process_taste_inbox.py` / `scripts/ingest_taste_results.py`.
7. Accepted results enter canonical Taste state and receipts under `data/cache/taste_ingest_receipts/`; the active pin lifecycle advances to the next GitHub-prepared unit.

No permanent `10`-game ceiling is being added to the future normal producer. The existing `CANONICAL_BATCH_SIZE = 10` is used only as the durable pin/checkpoint unit for this measurement run; final production capacity will be decided separately by the user after the factual measurement.

## Phase A deterministic verification before measurement

Verified against current `main` and exact active pin:

- active producer fence: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`;
- current active work-unit SHA: `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`;
- current active pin cardinality: exactly `10`, all keys unique;
- durable pin authority commit: `ddb1a51b8321997bbbb83505d69cfe4031758619`;
- pinned profile: `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json` at commit `218695966e124e1989faae0be4f8313736b7fad2`, blob `a9d0c40bb57c6b9183a7aa0d1e096837892ca7cc`;
- current live queue has already shifted relative to the active pin, proving that semantic context must come from the queue snapshot at the pin authority commit rather than from the latest first ten rows;
- fetching `chatgpt_taste_queue.jsonl` at `ddb1a51b…` yields the exact 10 pinned identities/context rows in the exact pin order;
- `scripts/taste_pinned_work_unit.py` preserves an existing active pin on retry and requires exact ordered-row/hash/profile bindings;
- `scripts/ingest_taste_results.py` rejects duplicate keys, identity/context/profile/pin mismatches, invalid V5 shapes and non-price-blind evidence;
- `.github/workflows/ingest-taste-batch.yml` is the single canonical persistence path and re-runs singleton-producer, V3 and transactional proof regressions before ingest;
- previous canonical receipt `ba86bfdcf8365dfa0195` proves that durable result submission, transactional ingest, canonical rebuild and preparation of a subsequent active pin have already completed successfully through this same mechanism;
- mechanism is not hardcoded to Chernobylite: the current active pin contains 10 heterogeneous App/Sub subjects and the code operates on generic ordered rows.

Phase A conclusion: the existing pinned-work-unit + canonical inbox/ingest mechanism is the smallest safe normal mechanism. No parallel queue, scheduler or producer code is required for this benchmark.

## Throughput checkpoint log

No checkpoint counted yet in this corrected run.

| Checkpoint | Work-unit SHA | Durably accepted in corrected run | Cumulative confirmed | State |
|---|---|---:|---:|---|
| 1 | `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` | 0/10 | 0 | semantic evaluation pending |

## Cumulative confirmed throughput

`0` real game evaluations durably accepted so far in the corrected measurement run.

## Errors / blockers so far

- Local container clone was attempted once and failed because the container could not resolve `github.com`; no repeated clone attempts were made. Repository work continues through the connected GitHub interface.
- Direct workflow-run listing through the generic GitHub fetch endpoint was not exposed by this connector. Acceptance will therefore be proven from canonical repository artifacts/commits/receipts after each submission, not by relying on UI-only workflow metadata.

Neither issue blocks the canonical inbox/ingest measurement path.

## Explicit non-changes

- Age-priority sorting implementation: **not performed**.
- Existing queue order: **not changed**.
- Second producer/scheduler: **not created**.
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`: **not changed**.
- Final production limit: **not selected**.

The measured maximum from this run will be factual throughput evidence only and will not automatically become the production limit.
