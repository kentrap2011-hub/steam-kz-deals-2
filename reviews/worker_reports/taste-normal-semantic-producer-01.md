# Normal Taste semantic producer 01 — worker report

Date: 2026-09-12
Worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`
Mode: `IMPLEMENT_AND_MEASURE_THROUGHPUT`

## Current status

`in_progress_throughput_measurement`

Corrected task is active; deferred age-priority work is not executed. GitHub remains control plane. Ten items is a measurement checkpoint only, not a production limit. Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` is unchanged and no second producer exists.

## Normal mechanism / implementation

Canonical path: `queue -> durable active pin -> inbox -> ingest workflow -> V5/transactional validation -> canonical cache/receipt -> next pin`.

Implemented Phase-A fixes:
- `config/execution_ownership_contract.json` — `cc680694cbc2357eef53726b61febdafbc71e015`;
- `config/daily_execution_contract.json` — `fb34396e2b0acd9750b107d373b1a1cc40b0d080`;
- `scripts/normalize_next_taste_semantic_pin.py` — `14db7b32d54bcb71ebc48175d209b16313ee79bf`;
- `scripts/validate_taste_normal_semantic_producer.py` — `f10b6d95187eeee795e376e48cdacb49db76a68b`;
- `.github/workflows/ingest-taste-batch.yml` — `f2e05761c6e949dd8c9506cb3d138b44bf4e8c63`;
- `scripts/process_taste_inbox.py` — `cee58d0c47258fa18f581558c61e1cad3c2cf02c`;
- `scripts/validate_taste_inbox_transactional_proof.py` — `151de78119d78ec4d3cd45bf9c018b938faaeddf`.

The mechanism preserves canonical relative order, filters only non-Taste work from newly prepared pins, never rewrites durable pins, and accepts exact in-flight pins across newer live-state drift without stale resurrection.

## Durable throughput log

| # | Work-unit | Receipt | Items | Full | Negative-only | Cum. items | Cum. full |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` | `cff63983dbb4caba6852` | 10 | 10 | 0 | 10 | 10 |
| 2 | `5d0d4b4f043018bcc8b2686d5f835d888a262f03ec86aaee89213d33ca51d8c0` | `7b6be6476172a4505994` | 10 | 10 | 0 | 20 | 20 |
| 3 | `19b27b85765f2d606d763ac847df6afe3a6ce1dce972b1c1f061374b99668123` | `41197fba99c33118e229` | 10 | 6 | 4 | 30 | 26 |
| 4 | `d9acb34d0de8b7741c51d78af9e693e9b6e4e0e9a102f0d7af3fa8ba0fad7979` | `2c22d02adb44cde8d39f` | 10 | 3 | 7 | 40 | 29 |
| 5 | `b34f801c046ac1d1955b081501c8cb6e92c75db9e2a9d4f10e2d1967dddc54ce` | `c2c7a37f6eed846ab41f` | 10 | 1 | 9 | **50** | **30** |

Every counted row above has a canonical complete receipt with all transactional checks true. Checkpoint 001 had one failed-closed attempt before its canonical bug fix and retry; failed work was not counted. Checkpoints 002–005 completed without retry.

### Checkpoint 005

- workflow run `34692130480`, job `103549136413`: success;
- receipt `c2c7a37f6eed846ab41f`;
- 10 accepted items = 1 full evaluation + 9 negative-only follow-ups;
- current reusable = 10;
- safe cache hits `19 -> 20`;
- AI-required `630 -> 629`;
- queue `609 -> 608`;
- negative-backfill remains **9**;
- all transactional checks true;
- next pin `2c970e1d4b0a6de75dab6d4de933003b9179c670822695405fabbb6b92e274e3`.

## Current factual throughput

- **50** durably accepted Taste semantic game work-items.
- **30** full fit evaluations.
- **20** negative-analysis follow-up executions.

The normal queue is now throughput-constrained by 9 legitimate `incomplete_no_confirmed_negative` rows that cannot be completed without inventing personal negatives. One new full-evaluation slot still survived checkpoint 005, so the real run limit has not yet been reached and measurement must continue.

## Non-changes

Age-priority not executed; Scheduled Task/cadence/prompt/limit not changed; no second producer; no final production limit selected.
