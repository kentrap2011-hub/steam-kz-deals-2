# Normal Taste semantic producer 01 — worker report

Date: 2026-09-12
Worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`
Mode: `IMPLEMENT_AND_MEASURE_THROUGHPUT`

## Current status

`in_progress_throughput_measurement`

The earlier age-priority-based `blocked_requires_followup` is superseded by the corrected worker task. `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md` is not being executed in this run.

## Architecture / normal mechanism

The corrected one-off interactive benchmark is canonically authorized by:
- `config/execution_ownership_contract.json` — `cc680694cbc2357eef53726b61febdafbc71e015`;
- `config/daily_execution_contract.json` — `fb34396e2b0acd9750b107d373b1a1cc40b0d080`.

GitHub still owns queue order, scope, durable pin authority, retry/completeness and persistence. Chat 1 evaluates only exact durable pinned units. Checkpoint size `10` is measurement-only and is not a production limit/quota. Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` remains unchanged; no second producer exists.

Canonical path:
`chatgpt_taste_queue.jsonl -> taste_active_work_unit.json -> data/ai_inbox/taste/*.json -> ingest-taste-batch.yml -> process_taste_inbox.py/ingest_taste_results.py -> canonical receipt/cache -> next durable pin`.

Phase-A implementation fixes already in this run:
- `scripts/normalize_next_taste_semantic_pin.py` — `14db7b32d54bcb71ebc48175d209b16313ee79bf`;
- `scripts/validate_taste_normal_semantic_producer.py` — `f10b6d95187eeee795e376e48cdacb49db76a68b`;
- `.github/workflows/ingest-taste-batch.yml` — `f2e05761c6e949dd8c9506cb3d138b44bf4e8c63`;
- `scripts/process_taste_inbox.py` — `cee58d0c47258fa18f581558c61e1cad3c2cf02c`;
- `scripts/validate_taste_inbox_transactional_proof.py` — `151de78119d78ec4d3cd45bf9c018b938faaeddf`.

These changes preserve existing semantic relative order, prevent base-support-only rows from becoming Taste pins, preserve immutable durable pins, and allow exact in-flight pinned results to finish safely across live-profile drift without resurrecting stale work.

## Verification

Every accepted checkpoint runs and passes:
- singleton producer fence;
- exact active producer envelope;
- V5 normalized Taste contract;
- transactional proof regression;
- normal semantic producer filtering regression;
- atomic ingest/rebuild;
- newly prepared next-pin normalization;
- commit/push of canonical state.

Failed work is never counted before canonical receipt.

## Throughput checkpoint log

| Checkpoint | Work-unit SHA | Receipt | Accepted work-items | Full fit evaluations | Cumulative work-items | Cumulative full evaluations | State |
|---|---|---|---:|---:|---:|---:|---|
| 1 | `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` | `cff63983dbb4caba6852` | 10/10 | 10 | 10 | 10 | complete |
| 2 | `5d0d4b4f043018bcc8b2686d5f835d888a262f03ec86aaee89213d33ca51d8c0` | `7b6be6476172a4505994` | 10/10 | 10 | 20 | 20 | complete |
| 3 | `19b27b85765f2d606d763ac847df6afe3a6ce1dce972b1c1f061374b99668123` | `41197fba99c33118e229` | 10/10 | 6 | **30** | **26** | complete |

### Checkpoint 001

First attempt job `103547484979` failed closed on an obsolete live-queue membership guard after all pre-ingest regressions passed. No progress was counted. After the canonical pinned/live reconciliation fix, retry job `103547957529` accepted the same exact 10 items. Receipt `cff63983dbb4caba6852`; all transactional checks true.

### Checkpoint 002

Workflow run `34691833665`, job `103548334915`: success. Receipt `7b6be6476172a4505994`; 10 full evaluations, all current-reusable, safe cache hits `0 -> 10`, AI-required `649 -> 639`, queue `619 -> 613`, all checks true.

### Checkpoint 003

Input `throughput-measurement-2026-09-12-checkpoint-003.json`.
Workflow run `34691977045`, job `103548724888`: success through all validation/ingest/normalization/commit steps.
Receipt `41197fba99c33118e229`:
- 10 accepted semantic work-items;
- 6 full evaluations;
- 4 negative-only grounded-negative follow-up items;
- `current_reusable_result_count = 10`;
- safe cache hits `10 -> 16`;
- AI-required `639 -> 633`;
- queue `613 -> 610`;
- one newly evaluated title reached negative-ready state due a grounded personal conflict; other INCLUDE rows without a provable personal negative remain correctly unresolved rather than receiving invented negatives;
- all transactional checks true;
- retired pin `19b27b85765f2d606d763ac847df6afe3a6ce1dce972b1c1f061374b99668123`;
- next pin `d9acb34d0de8b7741c51d78af9e693e9b6e4e0e9a102f0d7af3fa8ba0fad7979`.

## Cumulative confirmed throughput

- **30 real Taste semantic game work-items durably accepted** in this uninterrupted corrected run.
- **26 of those are full fit evaluations**; 4 are required negative-analysis follow-ups on already evaluated games.

Both counters are retained because later pins may legitimately contain follow-up work. The throughput limit is not yet reached; measurement continues immediately. Neither 30 nor 26 is a production limit.

## Errors/retries

- One local clone attempt failed DNS; GitHub connector remained usable.
- Checkpoint 001 first attempt exposed a real pinned/live reconciliation defect and failed safely before canonical progress; the same exact checkpoint succeeded after the canonical fix.
- Checkpoints 002 and 003 completed without retry.

## Explicit non-changes

- Age-priority task: **not executed**.
- Existing semantic queue relative order: **not reordered**.
- Second producer/scheduler: **not created**.
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`: **not changed**.
- Scheduled Task cadence/prompt/limit: **not changed**.
- Final production limit: **not selected**.
