# Worker Report — Taste Transactional Proof Repair 01

- task_id: `taste-transactional-proof-repair-01`
- lifecycle: `complete`
- started_utc: `2026-09-10T09:56:56Z`
- completed_utc: `2026-09-10T10:05:20Z`
- implementation_status: `complete_repair_ready_for_existing_batch_retry`
- next_action: existing 10-result submission may be retried unchanged by the operator; no retry was performed in this task

## Scope

Repaired only the transactional-proof expected-retention model for the two diagnosed canonical exclusion branches. No Taste semantics, consumer gating, ingest contract, queue-count exactness, production data, inbox payload, Scheduled Task, or next-batch state was changed.

## Diagnosis used

The prior diagnosis identified a nonsemantic proof-model mismatch after the valid 10-result batch had already been ingested ephemerally:

1. `App_2336880`: final Taste is non-`INCLUDE`; canonical consumer excludes the family before constructing base-support work, so stale baseline `resolve_base_support_condition` must not be expected after ingest.
2. `Sub_87601`: final Taste is `INCLUDE` with `fit_level=moderate`, but the selected `decision_if_moderate` deal scenario is `EXCLUDE` (`moderate_absolute_budget_ceiling`), so canonical consumer excludes before constructing `resolve_grounded_negative_analysis` work.

## Implementation

Changed `scripts/process_taste_inbox.py` only in transactional-proof expectation/context handling:

- added read-only access to post-rebuild `deal_scenarios.json`;
- mapped each Taste subject to its canonical family `primary_key` using post-rebuild `family_graph.json`;
- for a non-`INCLUDE` cached Taste result, suppress retained work only when that canonical primary key is in the post-rebuild deterministic-exclusion set;
- for an `INCLUDE` result with `strong` or `moderate` fit, select the matching precomputed deal scenario before constructing retained work and expect no retained work when that scenario is not `INCLUDE`;
- left the existing exact expected-queue formula unchanged;
- left `ai_queue_count_exact` and `queue_file_count_exact` unchanged and strict.

Changed `scripts/validate_taste_inbox_transactional_proof.py` only to add focused regression coverage and minimal fixture support:

- `final_taste_exclude_drops_stale_base_support_case()` reproduces the `App_2336880` branch;
- `post_fit_deal_exclude_drops_negative_case()` reproduces the `Sub_87601` branch;
- existing legal retained-base-support case still passes;
- existing illegal-retained-work case still fails closed and explicitly proves `ingested_key_retention_matches_negative_and_base_support_state`, `ai_queue_count_exact`, and `queue_file_count_exact` all reject an unexpected retained row.

## Validation

The execution container cannot clone GitHub directly (`Could not resolve host: github.com`). To avoid touching the real inbox or production state, the exact committed contents of the two changed Python files were staged in an isolated temporary directory. `semantic_runtime_completion.build_runtime_status` was supplied only as an inert import stub; the transactional-proof regression does not call it. No production data or inbox file was staged.

Commands and results:

```text
python -m py_compile scripts/process_taste_inbox.py scripts/validate_taste_inbox_transactional_proof.py
PASS

python scripts/validate_taste_inbox_transactional_proof.py
PASS
TASTE_INBOX_TRANSACTIONAL_PROOF_VALIDATION=PASS
```

Regression output confirmed:

```text
legal_retained_base_support_case = true
final_taste_exclude_drops_stale_base_support_case = true
post_fit_deal_exclude_drops_negative_case = true
illegal_retained_taste_work_failed_checks =
  ingested_key_retention_matches_negative_and_base_support_state
  ai_queue_count_exact
  queue_file_count_exact
```

No broader suite was run because the ingest contract, Taste semantics, consumer implementation, queue generator, and Scheduled Task were not changed; the focused proof regression includes the directly affected fail-closed guardrail behavior.

## Scope verification

Compared with pre-task commit `04bf0aabed9855f25d0a4f475baeb7747b78b5cd`, the implementation before this final report update changed only:

- `reviews/worker_reports/taste-transactional-proof-repair-01.md`
- `scripts/process_taste_inbox.py`
- `scripts/validate_taste_inbox_transactional_proof.py`

The existing inbox file remains present and unchanged:

- `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`
- blob SHA: `54faa8bc16064b15df8dd781d1988986b05e0e1c`

No inbox file was edited or deleted. No retry of `process_taste_inbox.py` or the real ingest was performed. No next games were started. No Scheduled Task was changed.

## Result

`complete_repair_ready_for_existing_batch_retry`

The existing 10-result submission can be retried unchanged. This task intentionally did not perform that retry.
