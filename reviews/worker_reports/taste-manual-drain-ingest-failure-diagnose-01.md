# Worker Report — TASTE manual drain ingest failure diagnosis

## Task ID
`taste-manual-drain-ingest-failure-diagnose-01`

## Lifecycle
`complete`

## Scope honored
Diagnosis only. No ingest retry was run. No inbox submission, queue, cache, configuration, code, workflow, Scheduled Task, or semantic result was modified. Batch 2 was not started. The only durable writes in this task are this report and its initial `in_progress` version.

## Target
- inbox submission: `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`
- submission commit: `f138d5216248c999fde588c47ca5088ff9c076ee`
- supplied failed identifier: `102798215077`

## Identifier clarification
The supplied identifier `102798215077` is usable by GitHub as the failed Actions **job/check-run ID**, not as the workflow-run ID: querying it as a workflow run returned 404, while querying job steps and decoded job logs for job `102798215077` succeeded. The job name is `ingest` and it checked out submission commit `f138d5216248c999fde588c47ca5088ff9c076ee`.

## Exact failing step
`Validate, ingest and rebuild taste consumers atomically`

Command:
`python scripts/process_taste_inbox.py`

All earlier substantive steps succeeded:
- singleton Taste producer fence regression: PASS;
- active producer fence on canonical inbox: PASS;
- normalized Taste V5 factor contract: PASS;
- transactional-proof regression fixture: PASS.

The following commit step was skipped because the atomic processing step failed:
`Commit processed taste batch and synchronized consumer state`.

## First real failure
The semantic batch itself was accepted by the canonical ingest validator inside `process_taste_inbox.py`:
- `status: validated`;
- `batch_result_count: 10`;
- `full_result_count: 10`;
- `negative_only_result_count: 0`;
- `profile_blob_sha: b487e62b3fec9f413fb001d96b4894f8ac43e5d5`;
- `taste_model_version: taste-v3`;
- `taste_semantics_sha256: 0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`;
- `candidate_context_required: true`.

The first real failure occurred only after ingest had built the temporary post-ingest projection/consumer state and `build_transactional_proof_checks(...)` compared that state with its expected retention model.

Exact terminal error:

`Taste inbox transactional proof failed: ['ingested_key_retention_matches_negative_and_base_support_state', 'ai_queue_count_exact', 'queue_file_count_exact']`

Exact count mismatch:
- expected AI queue: `562`;
- actual rebuilt AI queue: `560`.

Exact retention mismatches:
- `App_2336880`: expected `['resolve_base_support_condition']`, actual queue row absent;
- `Sub_87601`: expected `['resolve_grounded_negative_analysis']`, actual queue row absent.

No later error is the root cause; exit code 1 and the skipped commit step are downstream consequences of this proof failure.

## Root cause
The root cause is a **nonsemantic defect in the transactional proof's expected-retention model**. `process_taste_inbox.py::expected_retained_work(...)` does not model two deterministic consumer-exclusion branches that `build_pre_ai_chatgpt_payload.py` legitimately applies after a valid Taste result is ingested.

### 1. `App_2336880` — stale base-support retention expectation
Baseline work for `App_2336880` included `resolve_base_support_condition`, but the submitted semantic result is a valid final Taste `EXCLUDE` (`below_moderate`, `exclude_insufficient`).

The consumer builder intentionally handles a cached non-`INCLUDE` verdict before normal base-support work construction. With no commercial eligibility bridge, it deterministically excludes the family and does not enqueue further base-support work.

The proof nevertheless preserves `resolve_base_support_condition` solely because that work code existed in the baseline row. It therefore expects a queue row that production consumer logic intentionally removes.

### 2. `Sub_87601` — post-fit deal exclusion omitted from proof
The submitted semantic result for `Sub_87601` is a valid `INCLUDE` with `fit_level: moderate` and incomplete grounded-negative analysis.

Its precomputed deal scenario at the submission commit is:
- current price: about `690 RUB`;
- moderate active price ceiling: `550 RUB`;
- `decision_if_moderate.final_disposition: EXCLUDE`;
- reason: `moderate_absolute_budget_ceiling` / `price_clearly_unreasonable_after_soft_target_evaluation`.

The consumer builder selects the moderate deal scenario after applying the valid cached Taste fit. Because that scenario is `EXCLUDE`, it deterministically excludes the purchase family and exits before adding `resolve_grounded_negative_analysis` to the AI queue.

The transactional proof only sees `cached verdict == INCLUDE` plus `negative_analysis_status == incomplete_no_confirmed_negative`; it does not account for the selected deal scenario being deterministically excluded. It therefore expects negative-analysis retention even though the consumer contract intentionally removes that work from the queue.

## Why the regression check passed
`scripts/validate_taste_inbox_transactional_proof.py` covers a retained base-support `INCLUDE` case and an illegal retained Taste-work case. It does not cover:
- a baseline base-support item whose new semantic verdict is `EXCLUDE`;
- an `INCLUDE` + incomplete-negative item whose selected post-fit deal scenario is deterministically `EXCLUDE`.

Therefore the regression fixture passed while the real batch exposed the missing cases.

## Are any of the 10 semantic results invalid?
No evidence of semantic invalidity was found.

All 10 results passed the canonical producer fence and Taste V5 contract and were accepted by `ingest_taste_results.py` as a 10-result full-evaluation batch before the post-ingest proof failed. The two offending keys are mismatches in proof expectations versus deterministic consumer behavior, not rejected semantic rows.

Classification of the existing submission:
`safe_after_nonsemantic_repair`

It is **not** `safe_to_retry_unchanged` against the current unchanged processing code, because the same deterministic proof mismatch would recur. It does **not** require semantic regeneration.

## Binding validity
The existing inbox file is byte-for-byte unchanged from the submission commit at the Git blob level:
- submission-commit inbox blob SHA: `54faa8bc16064b15df8dd781d1988986b05e0e1c`;
- current inbox blob SHA: `54faa8bc16064b15df8dd781d1988986b05e0e1c`.

The run itself reported the same profile/model/semantics bindings carried by the submission. The submission's 10 keys/fingerprints/candidate-context hashes passed canonical ingest validation; no runtime identity mismatch was emitted.

A compare from submission commit `f138d5216248c999fde588c47ca5088ff9c076ee` to this task's initial report commit shows only the diagnosis task/report files and predecessor report changed; no queue/cache/config/code/workflow or production data file changed. Therefore the existing submission's profile/model/semantics/fingerprint/context bindings remain valid for the diagnosed state.

## Inbox and queue safety
The inbox file should remain untouched until the nonsemantic proof repair is made. It is the durable copy of the already-computed 10 results and is still present unchanged.

The canonical queue remains safe and unconsumed. The failed workflow mutated only its ephemeral runner checkout before the proof aborted; the commit/push step was skipped. Current canonical manifest still reports:
- `ai_queue_count: 566`;
- `ready_without_ai_count: 1`;
- `deterministically_excluded_without_ai_count: 26`.

Thus none of these 10 results has been canonically accepted yet, and no queue item was durably removed by the failed run.

## Scheduled Task
Unaffected. The predecessor run explicitly recorded `scheduled_task_touched: false`, the failed GitHub Actions job contains no Scheduled Task mutation, and this diagnosis made no Scheduled Task change. Repository observability does not expose the scheduler platform's enabled/next-run state, but there is no evidence or repository change indicating that the Scheduled Task itself was modified.

## Smallest next action
Create a separate repair task that changes only the transactional-proof expectation/regression coverage so expected retained work is computed consistently with the canonical consumer's post-ingest deterministic gating:
1. do not retain base-support work for a newly cached Taste result that is deterministically excluded by final Taste verdict without an allowed bridge;
2. do not retain grounded-negative work when the selected valid cached-fit deal scenario is deterministically `EXCLUDE`;
3. add regression fixtures for both cases.

After that nonsemantic repair is reviewed, the **same untouched inbox submission** can be retried through canonical ingest. Do not regenerate the 10 semantic results.

No repair or retry was performed in this task.

## Final status
`complete_root_cause_found_needs_nonsemantic_repair`
