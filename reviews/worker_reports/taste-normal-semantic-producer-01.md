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

## Normal mechanism implemented/used

The existing pinned-work-unit architecture remains the normal mechanism:

1. GitHub-prepared queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`.
2. Durable active pin: `data/production/pre_ai/taste_active_work_unit.json` (`TASTE-PINNED-WORK-UNIT-V1`).
3. Exact semantic/profile binding: `config/taste_result_contract.json` + pin `profile_identity`/`bindings`.
4. Result handoff: new JSON under `data/ai_inbox/taste/`.
5. Push to that path triggers `.github/workflows/ingest-taste-batch.yml`.
6. Workflow runs producer-fence, V3 contract and transactional-proof validators, then `scripts/process_taste_inbox.py` / `scripts/ingest_taste_results.py`.
7. Accepted results enter canonical Taste state and receipts under `data/cache/taste_ingest_receipts/`; the active pin lifecycle advances to the next GitHub-prepared unit.

Two Phase-A defects exposed by the real exercise were fixed without creating a parallel producer:

### A. Non-Taste rows in the shared AI queue

The shared queue can retain `resolve_base_support_condition`-only rows after Taste ingest. Such rows are not valid Taste-semantic work but the previous next-pin builder could include them because it sliced the shared queue blindly.

Fix:
- `scripts/normalize_next_taste_semantic_pin.py` — commit `14db7b32d54bcb71ebc48175d209b16313ee79bf`;
- `scripts/validate_taste_normal_semantic_producer.py` — commit `f10b6d95187eeee795e376e48cdacb49db76a68b`;
- `.github/workflows/ingest-taste-batch.yml` — commit `f2e05761c6e949dd8c9506cb3d138b44bf4e8c63`.

The guard preserves canonical queue order among rows owned by the Taste semantic worker, excludes only rows without `resolve_grounded_negative_analysis`, and may normalize only a newly generated uncommitted next pin. It explicitly refuses to rewrite an already-durable active pin.

### B. Pinned result whose key disappeared from newer live queue

Checkpoint 001 initially failed closed because the live profile/source advanced while the pinned unit was in flight. `App_1016800` was still a valid exact pinned result, but after rebuild it was no longer present in the synchronized current live queue. `process_taste_inbox.py` had an obsolete unconditional membership guard even though the rest of the architecture already distinguishes pinned validity from current reuse.

Fix:
- `scripts/process_taste_inbox.py` — commit `cee58d0c47258fa18f581558c61e1cad3c2cf02c`;
- `scripts/validate_taste_inbox_transactional_proof.py` — commit `151de78119d78ec4d3cd45bf9c018b938faaeddf`.

The corrected rule is:
- exact pre-semantic pinned result may be historically accepted even if newer live state removed its key;
- such a result gets `current_reusable=false`;
- it must not become a current cache hit;
- it must not resurrect the removed key into the live queue;
- live queue counts change only for inbox keys that actually existed in the live baseline.

## Phase A deterministic verification

Verified before and during the first real checkpoint:

- active producer fence: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`;
- pinned profile/queue identity is durable and results bind exact `ordered_work_unit_sha256` + pin authority commit;
- current live queue can move independently from an in-flight pin without redefining that pin;
- normal semantic-row selection preserves deterministic canonical relative order;
- focused normal-producer filtering regression passes;
- producer-fence regression passes;
- V5 normalized-factor contract regression passes;
- transactional-proof regression, including `pinned_key_removed_from_live_queue_case`, passes;
- retry of the same checkpoint does not choose different games or create a second pin;
- canonical ingest is fail-closed: the first attempt failed before persistence and counted zero;
- successful retry atomically accepted the exact same 10 results, retired the exact active pin, wrote a receipt and prepared the next pin;
- mechanism is generic and not hardcoded to Chernobylite.

No permanent `10`-game ceiling is being added to the future normal Scheduled Task. The existing 10-row pin is the durable measurement checkpoint unit only; final production capacity remains a later user decision.

## Throughput checkpoint log

| Checkpoint | Work-unit SHA | Receipt / canonical proof | Accepted | Cumulative confirmed | State |
|---|---|---|---:|---:|---|
| 1 | `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` | `data/cache/taste_ingest_receipts/cff63983dbb4caba6852.json` | 10/10 | **10** | complete |

Checkpoint 001 input file was `throughput-measurement-2026-09-12-checkpoint-001.json` and was removed by canonical ingest after acceptance.

Receipt facts:
- `result_count = 10`;
- `full_evaluation_result_count = 10`;
- `transactional checks = all true`;
- retired pin = `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20`;
- next pin before workflow normalization =/ultimately normalized to durable active semantic pin `5d0d4b4f043018bcc8b2686d5f835d888a262f03ec86aaee89213d33ca51d8c0`;
- next profile blob = `5b8fb3c2571c1be5769b2bd1ce5fb70c90636d0e`;
- `current_reusable_result_count = 0` because the live profile advanced while checkpoint 001 was in flight;
- `newer_live_pending_result_count = 10`;
- no old result was promoted into the newer live cache incorrectly.

## Cumulative confirmed throughput

**10 real game evaluations durably accepted** so far in the corrected uninterrupted measurement run.

This is a lower bound only. Measurement continues immediately with the next durable pin; `10` is not the measured limit.

## Retries / errors / blockers observed

1. Local container clone failed once because the container could not resolve `github.com`; repository work continued through the connected GitHub interface.
2. Checkpoint 001 attempt 1: canonical ingest job `103547484979` failed closed after all pre-ingest regressions passed. Root cause: obsolete current-live queue membership requirement rejected valid pinned `App_1016800` after live queue drift. No canonical semantic progress was recorded; cumulative count remained 0.
3. The guard was fixed with regression coverage, then the same workflow job was retried without changing the checkpoint games/results. Retry job `103547957529` completed successfully through validation, ingest, next-pin normalization and commit/push. Cumulative count advanced to 10 only after this durable success.

No canonical blocker is active after checkpoint 001.

## Explicit non-changes

- `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md`: **not executed**.
- Age-priority sorting: **not implemented**.
- Existing canonical relative queue order: **not reordered**.
- Second producer/scheduler: **not created**.
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`: **not changed**.
- Scheduled Task cadence/prompt/limit: **not changed**.
- Final production limit: **not selected**.

The measured maximum from this run is factual throughput evidence only and must not automatically become the production limit.
