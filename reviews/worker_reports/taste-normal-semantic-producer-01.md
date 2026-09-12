# Normal Taste semantic producer 01 — worker report

Date: 2026-09-12
Worker task: `WORKER_TASK_TASTE_NORMAL_SEMANTIC_PRODUCER_01.md`
Mode: `IMPLEMENT_AND_MEASURE_THROUGHPUT`

## Current status

`in_progress_throughput_measurement`

The earlier age-priority-based `blocked_requires_followup` is superseded by the corrected worker task. `WORKER_TASK_TASTE_QUEUE_AGE_PRIORITY_ORDER_01.md` is not being executed in this run.

## Corrected architecture preflight

The corrected task explicitly authorizes this one-off interactive throughput benchmark. Canonical ownership was reconciled before Taste writes:

- `config/execution_ownership_contract.json` — `cc680694cbc2357eef53726b61febdafbc71e015`;
- `config/daily_execution_contract.json` — `fb34396e2b0acd9750b107d373b1a1cc40b0d080`.

Invariant: GitHub still owns scope, existing queue order, pin authority, retry/completeness and canonical persistence. This chat may evaluate only exact Git-durable pinned work-units and must persist every counted checkpoint through the canonical inbox/ingest path. Checkpoint size `10` is measurement-only, not a production quota/limit. Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` is unchanged and no second producer exists.

## Normal mechanism implemented/used

Canonical path remains:

1. `data/production/pre_ai/chatgpt_taste_queue.jsonl`;
2. durable `data/production/pre_ai/taste_active_work_unit.json`;
3. exact pin/profile binding under `TASTE-SEMANTIC-RESULT-V5`;
4. result JSON under `data/ai_inbox/taste/`;
5. `.github/workflows/ingest-taste-batch.yml`;
6. producer-fence, V5 and transactional regressions;
7. `scripts/process_taste_inbox.py` / `scripts/ingest_taste_results.py`;
8. canonical receipt/state update and next durable pin.

Phase-A fixes made while exercising this path:

- `scripts/normalize_next_taste_semantic_pin.py` — `14db7b32d54bcb71ebc48175d209b16313ee79bf`: filters shared-AI-queue rows not owned by Taste semantic worker while preserving semantic-row relative order; refuses to rewrite a durable pin.
- `scripts/validate_taste_normal_semantic_producer.py` — `f10b6d95187eeee795e376e48cdacb49db76a68b`: deterministic filtering/first-10/retry regression.
- `.github/workflows/ingest-taste-batch.yml` — `f2e05761c6e949dd8c9506cb3d138b44bf4e8c63`: runs focused regression and normalizes only the newly generated next pin before its durable commit.
- `scripts/process_taste_inbox.py` — `cee58d0c47258fa18f581558c61e1cad3c2cf02c`: allows an exact pre-semantic pinned result to be accepted historically when newer live state removed that key, while forbidding current cache promotion or queue resurrection.
- `scripts/validate_taste_inbox_transactional_proof.py` — `151de78119d78ec4d3cd45bf9c018b938faaeddf`: regression for that live-queue-removal case.

No age-priority ordering or commercial sorting was added.

## Verification

Repeated workflow checks prove:
- producer fence/generation exact;
- ordered pin identity/hash/profile binding exact;
- V5 normalized factors and price-blind evidence contract valid;
- duplicate/resurrection/current-reuse transactional checks pass;
- same failed checkpoint is retryable without selecting different games;
- accepted checkpoint retires exactly its pin and creates the next durable semantic pin;
- mechanism is generic, not Chernobylite-hardcoded.

## Throughput checkpoint log

| Checkpoint | Work-unit SHA | Receipt | Accepted | Cumulative confirmed | State |
|---|---|---|---:|---:|---|
| 1 | `31c86e796e2d433aeb27e727226dc8245ec542650263ff631bc7ae64881c3d20` | `cff63983dbb4caba6852` | 10/10 | **10** | complete |
| 2 | `5d0d4b4f043018bcc8b2686d5f835d888a262f03ec86aaee89213d33ca51d8c0` | `7b6be6476172a4505994` | 10/10 | **20** | complete |

### Checkpoint 001

- input: `throughput-measurement-2026-09-12-checkpoint-001.json`;
- first ingest job `103547484979` failed closed after all pre-ingest regressions passed because newer live state had removed pinned `App_1016800`;
- no progress was counted on that failure;
- root cause fixed with regression coverage;
- same exact checkpoint retried as job `103547957529` and completed successfully;
- receipt `cff63983dbb4caba6852`: 10 full evaluations, all checks true, `current_reusable_result_count=0`, `newer_live_pending_result_count=10`; old pin retired without incorrectly promoting stale results into the newer live cache.

### Checkpoint 002

- input: `throughput-measurement-2026-09-12-checkpoint-002.json`;
- pin: `5d0d4b4f043018bcc8b2686d5f835d888a262f03ec86aaee89213d33ca51d8c0`;
- pin authority: `46ad22acfde006ccda3e77212558c8a3032d24a2`;
- profile blob: `5b8fb3c2571c1be5769b2bd1ce5fb70c90636d0e`;
- workflow run `34691833665`, job `103548334915`: all validation, ingest, next-pin normalization and commit/push steps succeeded;
- receipt `7b6be6476172a4505994`: `result_count=10`, `full_evaluation_result_count=10`, `current_reusable_result_count=10`, `newer_live_pending_result_count=0`;
- safe current cache hits `0 -> 10`;
- current AI-required `649 -> 639`;
- queue `619 -> 613` because four accepted INCLUDE rows legitimately retain grounded-negative/base-support follow-up work;
- every receipt transactional check is true;
- retired pin = `5d0d4b4f...`;
- next pin = `19b27b85765f2d606d763ac847df6afe3a6ce1dce972b1c1f061374b99668123` on the same current profile.

## Cumulative confirmed throughput

**20 real game evaluations durably accepted** in this uninterrupted corrected measurement run.

This remains only a demonstrated lower bound. Measurement continues immediately with the next durable pin; `20` is not the measured limit and must not be installed as a production limit.

## Errors/retries observed

- One local clone attempt failed DNS; GitHub connector remained fully usable.
- Checkpoint 001 first ingest attempt exposed and safely failed on the stale-live membership defect; after canonical fix, retry of the same exact work-unit succeeded.
- Checkpoint 002 completed without retry.

No active canonical blocker after checkpoint 002.

## Explicit non-changes

- Age-priority task: **not executed**.
- Existing semantic queue relative order: **not reordered**.
- Second producer/scheduler: **not created**.
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`: **not changed**.
- Scheduled Task cadence/prompt/limit: **not changed**.
- Final production limit: **not selected**.
