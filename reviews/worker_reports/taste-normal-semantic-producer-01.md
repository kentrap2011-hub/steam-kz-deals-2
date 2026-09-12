# Normal Taste semantic producer 01 — worker report

Date: 2026-09-12
Worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`
Mode: `IMPLEMENT_AND_MEASURE_THROUGHPUT`

## Current status

`in_progress_throughput_measurement`

Corrected task is active; the deferred age-priority task is not executed.

## Normal mechanism and architecture

One-off benchmark authorization was added canonically without changing normal production ownership:
- `config/execution_ownership_contract.json` — `cc680694cbc2357eef53726b61febdafbc71e015`;
- `config/daily_execution_contract.json` — `fb34396e2b0acd9750b107d373b1a1cc40b0d080`.

GitHub owns queue order/scope/pin/retry/persistence. Chat 1 processes only exact durable pins. Ten is a measurement checkpoint, not a production limit. Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` remains unchanged; no second producer exists.

Canonical path remains:
`queue -> durable active pin -> inbox result -> ingest workflow -> contract/transactional validation -> canonical cache/receipt -> next durable pin`.

Phase-A fixes:
- semantic-only next-pin normalization: `14db7b32d54bcb71ebc48175d209b16313ee79bf`;
- normal producer filtering regression: `f10b6d95187eeee795e376e48cdacb49db76a68b`;
- ingest workflow wiring: `f2e05761c6e949dd8c9506cb3d138b44bf4e8c63`;
- pinned/live queue-drift reconciliation: `cee58d0c47258fa18f581558c61e1cad3c2cf02c`;
- transactional regression for removed-live pinned key: `151de78119d78ec4d3cd45bf9c018b938faaeddf`.

## Throughput checkpoint log

| # | Work-unit | Receipt | Accepted items | Full evaluations | Negative-only | Cumulative items | Cumulative full | State |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` | `cff63983dbb4caba6852` | 10 | 10 | 0 | 10 | 10 | complete |
| 2 | `5d0d4b4f043018bcc8b2686d5f835d888a262f03ec86aaee89213d33ca51d8c0` | `7b6be6476172a4505994` | 10 | 10 | 0 | 20 | 20 | complete |
| 3 | `19b27b85765f2d606d763ac847df6afe3a6ce1dce972b1c1f061374b99668123` | `41197fba99c33118e229` | 10 | 6 | 4 | 30 | 26 | complete |
| 4 | `d9acb34d0de8b7741c51d78af9e693e9b6e4e0e9a102f0d7af3fa8ba0fad7979` | `2c22d02adb44cde8d39f` | 10 | 3 | 7 | **40** | **29** | complete |

## Checkpoint details / validation

Checkpoint 001 first attempt failed closed on a real stale-live reconciliation defect; no progress counted. Same exact unit succeeded after canonical fix. Checkpoints 002–004 then completed without retry. Every successful workflow passed producer fence, V5 contract, transactional regression, normal producer regression, ingest/rebuild, next-pin normalization and commit/push.

Checkpoint 004 receipt `2c22d02adb44cde8d39f`:
- `result_count=10`;
- `full_evaluation_result_count=3`;
- `negative_only_result_count=7`;
- all 10 current-reusable;
- safe cache hits `16 -> 19`;
- AI-required `633 -> 630`;
- queue `610 -> 609`;
- all transactional checks true;
- next pin `b34f801c046ac1d1955b081501c8cb6e92c75db9e2a9d4f10e2d1967dddc54ce`;
- canonical `negative_backfill_queue_count` is now **9**.

## Current throughput observation

Confirmed so far:
- **40** durably accepted semantic game work-items;
- **29** full fit evaluations;
- 11 negative-only follow-up executions.

A concrete mechanism-level pressure is now visible: because the contract correctly forbids invented personal negatives and has no `complete_no_negative` state, INCLUDE games without a provable personal negative remain `incomplete_no_confirmed_negative` and occupy future pins. After checkpoint 004 there are 9 such negative-backfill rows. This is not yet declared the limit because the next pin must be exercised: if it still contains one full-evaluation slot, the uninterrupted run must continue.

## Non-changes

- age-priority: not executed/implemented;
- Scheduled Task: unchanged;
- second producer/scheduler: none;
- queue reordering: none beyond filtering work not owned by Taste semantic worker while preserving relative order;
- final production limit: not selected.
