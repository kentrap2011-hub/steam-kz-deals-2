# Worker Report — Retry Existing 10-Result Taste Batch

- task_id: `taste-existing-batch-retry-01`
- lifecycle: `completed`
- started_utc: `2026-09-10T10:42:27Z`
- Last checkpoint UTC: `2026-09-10T10:54:14Z`
- retry_status: `single_attempt_failed_no_second_retry`
- final_status: `blocked_stale_profile_binding`
- inbox_submission: `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`
- inbox_blob_sha_before_retry: `54faa8bc16064b15df8dd781d1988986b05e0e1c`
- inbox_blob_sha_after_retry: `54faa8bc16064b15df8dd781d1988986b05e0e1c`
- expected_result_count: `10`
- queue_count_before_retry: `566`
- queue_count_after_failed_retry: `566`
- queue_delta: `0`
- actions_run_id: `34454681107`
- original_failed_job_id: `102798215077`
- retry_attempt: `2`
- retry_job_id: `102841536663`
- retry_job_conclusion: `failure`
- commit_outcome: `not_accepted`
- receipt_written: `false`
- receipt_batch_id: `none`
- retry_consumed: `true`
- same_existing_batch_safe_to_rerun_again: `false`
- same_existing_results_acceptable_unchanged_under_current_binding: `false`
- next_action: `Do not rerun this existing batch. A new explicitly authorized task must regenerate/revalidate the affected Taste results against the current canonical profile before any future ingest; do not start the next ten as part of this task.`

## Scope

Authorized production retry for the existing untouched 10-result Taste inbox submission only. No semantic regeneration or edits, no next batch, no direct queue/cache edits, no code/config changes, and no Scheduled Task mutation were authorized or performed.

## Initial evidence

- The exact inbox file existed on `main` with the task-bound Git blob SHA `54faa8bc16064b15df8dd781d1988986b05e0e1c`.
- The GitHub-backed canonical `data/production/pre_ai/chatgpt_payload.json` reported `ai_queue_count: 566` before retry.
- The predecessor repair had corrected the earlier transactional-proof defect nonsemantically, so the retry was initially treated as eligible if the existing batch remained current.

## Pre-retry safety verification and gap discovered after failure

The bounded preflight confirmed the exact inbox blob and queue baseline were unchanged and found no accepted transaction for this batch. That was sufficient to prove that the old batch had not already been consumed, but it was not sufficient to prove that the batch was still semantically current.

The missing preflight condition was the live canonical Taste profile binding. The inbox is bound to:

- `profile_blob_sha = b487e62b3fec9f413fb001d96b4894f8ac43e5d5`

The canonical profile is configured as:

- repository: `kentrap2011-hub/stopgame-ratings-data`
- path: `gaming_taste_live.json`

Before the profile update, parent commit `4b75f76f4f9896418770556ab05789668f629d9b` exposes `gaming_taste_live.json` with exactly the old blob SHA `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`.

At `2026-09-10T08:45:53Z`, after the batch had been submitted, commit `fb33d77b7184d73b48bc1d838b3ecb5264bcc4db` (`Apply live gaming taste update`) modified `gaming_taste_live.json`. Its new/current Git blob SHA is:

- `08d569b56ea62f7ec1297320450db24073bbbd38`

The update added new live preference evidence (`Hellblade vs Solar Ash`) and changed the canonical live profile itself, so this is a real semantic profile revision, not a metadata-only rename.

## Single retry execution

Exactly one canonical GitHub Actions rerun request was issued for original failed job `102798215077`.

Identifier reconciliation from the authoritative Actions API:

- workflow: `Ingest context-bound taste batch`
- actual workflow run ID: `34454681107`
- attempt 1 job ID: `102798215077`
- attempt 2 retry job ID: `102841536663`
- attempt 2 started: `2026-09-10T10:50:39Z`
- attempt 2 completed: `2026-09-10T10:50:49Z`
- attempt 2 conclusion: `failure`

No second rerun or alternate launch was issued.

## Retry failure

All guard/regression steps before the actual ingest passed, including:

- singleton producer fence regression;
- active producer fence;
- normalized Taste factor contract validation;
- repaired Taste inbox transactional-proof regression validation.

The failure occurred in step `Validate, ingest and rebuild taste consumers atomically`, while running `python scripts/process_taste_inbox.py`.

During its mandatory baseline synchronization, the runner loaded the current canonical profile and rebuilt the local projection with:

- `current_profile_blob_sha = 08d569b56ea62f7ec1297320450db24073bbbd38`

Then canonical `ingest_taste_results.py` rejected the untouched inbox before acceptance with the exact error:

`Ingest binding mismatch for profile_blob_sha: input='b487e62b3fec9f413fb001d96b4894f8ac43e5d5' current='08d569b56ea62f7ec1297320450db24073bbbd38'`

The diagnostic emitted `taste_ingest_runtime_identity_mismatches: []` and `mismatch_count: 0`; therefore the immediate failure is not an appid/taste_fingerprint/candidate-context row identity mismatch. It is the batch-level canonical profile binding mismatch.

The following commit step was skipped, so no local rebuilt queue/projection state from the failed runner was committed.

## Primary root cause — global root-cause rule

**Primary failure:** canonical ingest correctly failed closed because the existing batch is bound to obsolete canonical profile blob `b487e62...`, while the current canonical profile blob is `08d569b...`.

**Underlying root cause:** the canonical live Taste profile changed after this batch was generated/submitted and before the retry. Commit `fb33d77b7184d73b48bc1d838b3ecb5264bcc4db` at `2026-09-10T08:45:53Z` changed `gaming_taste_live.json` from the exact profile blob used by the batch to a new semantic profile revision.

**Contributing process gap:** the retry preflight verified the untouched inbox SHA, unchanged GitHub-backed queue, and absence of prior acceptance, but did not compare the batch's top-level `profile_blob_sha` against the current canonical profile before consuming the one allowed retry. Under the general root-cause rule, the profile advance is the primary causal change; the ingest error is the protective symptom, and the missing binding-freshness precheck is the process gap that allowed an already-stale batch to be launched.

**Not the root cause:** the previously repaired transactional-proof logic. Its regression validation passed on attempt 2 and the retry failed earlier at canonical binding validation.

## Retry safety and invariant status

- `retry_count_executed = 1`; the retry allowance is exhausted.
- No second retry was launched.
- The existing inbox file remains on GitHub unchanged with blob SHA `54faa8bc16064b15df8dd781d1988986b05e0e1c`.
- GitHub-backed `ai_queue_count` remains `566`; therefore `566 -> 566`, delta `0`.
- The workflow commit step was skipped; no queue/cache/consumer mutation from the failed runner was accepted into `main`.
- Receipt generation was never reached; `receipt_written = false` and there is no receipt for this attempt.
- No semantic results were edited or regenerated.
- No next ten games were started.
- No Scheduled Task, code, configuration, queue, or cache was directly modified by this retry task.

## Disposition of the existing ten results

The ten results remain physically intact, but they are no longer ingestable unchanged under the current canonical contract because their immutable batch binding points to the previous live Taste profile. Accepting them by merely rewriting the binding would bypass the semantic context change and is not authorized by this task.

Therefore this exact existing package must **not** be retried again unchanged. Any future attempt requires a separate authorization to regenerate/revalidate results against the current canonical profile; this task intentionally does not perform that work.

## Checkpoints

### 2026-09-10T10:42:27Z — report created before retry

Lifecycle set to `in_progress`; retry not yet launched.

### 2026-09-10T10:50:11Z — bounded preflight passed

Exact inbox blob and GitHub-backed queue baseline were unchanged, with no accepted prior transaction observed. The later failure analysis identified that canonical profile binding freshness was an additional necessary preflight invariant and was already stale at this point.

### 2026-09-10T10:50:35Z — single retry initiated

GitHub accepted the one job-rerun request. This consumed the single authorized retry allowance.

### 2026-09-10T10:50:49Z — retry failed

Actions run `34454681107`, attempt `2`, job `102841536663` completed with `failure`. Canonical ingest rejected the obsolete profile binding. Commit step skipped. No second launch permitted.

### 2026-09-10T10:54:14Z — root cause and invariants completed

Canonical profile history proves the binding changed after batch submission: old blob `b487e62...` -> current blob `08d569b...` via `stopgame-ratings-data` commit `fb33d77...` at `2026-09-10T08:45:53Z`. GitHub-backed inbox and queue remain unchanged, no receipt exists for the failed attempt, and the task is closed as `blocked_stale_profile_binding`.
