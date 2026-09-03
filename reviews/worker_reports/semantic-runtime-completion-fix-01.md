# Semantic Runtime Completion Fix 01

Task ID: `semantic-runtime-completion-fix-01`
Status: `complete`

## Required result

### 1. Exact implementation performed

Implemented exactly the two defects identified by `semantic-runtime-completion-acceptance-01` without changing Taste policy, weights, scores, ranking, exclusion thresholds, or fail-closed readiness semantics.

- Added `scripts/semantic_runtime_completion.py` as the shared status contract for:
  - durable accepted-runtime execution/progress evidence;
  - current-scope runtime observability;
  - semantic completeness/degraded state for pre-AI and visual publication.
- Updated `scripts/process_taste_inbox.py` so every successfully validated transactional Taste inbox batch also refreshes one durable canonical runtime receipt at:
  - `data/cache/taste_ingest_receipts/latest_runtime_status.json`
- Updated `scripts/build_pre_ai_chatgpt_payload.py` so the canonical pre-AI manifest applies semantic completeness and runtime-observability state before publication.
- Updated `scripts/build_visual_feed_v2.py` and `scripts/build_final_visual_payload.py` so the visual publication carries the same semantic completeness/degraded truth. Existing visual items and Taste decisions are not modified by this status layer.
- Bootstrapped `latest_runtime_status.json` from the latest already accepted transactional receipt; no production queue item was manually processed.
- Updated the existing `scripts/validate_taste_inbox_transactional_proof.py` test fixture to the current `build_transactional_proof_checks()` interface after the first bounded validation run exposed validator drift. This changed test wiring only, not production Taste semantics.
- `config/execution_ownership_contract.json` was not changed.
- No second scheduler, semantic runtime, queue, or manual Taste path was created.

### 2. Exact durable runtime heartbeat/progress mechanism

Canonical durable receipt:

`data/cache/taste_ingest_receipts/latest_runtime_status.json`

It is generated only from an already successful transactional Taste inbox receipt whose checks all passed. The existing `ingest-taste-batch` persistence path already commits `data/cache/taste_ingest_receipts`, so the new `latest_runtime_status.json` is durable through the existing GitHub control-plane path.

The receipt exposes:

- `runtime_owner = "scheduled ChatGPT production task"`;
- `owner_contract_ref = "config/execution_ownership_contract.json#scheduled_chatgpt_runtime_data_plane"`;
- `last_successful_semantic_execution_at_utc`;
- `last_successful_batch_id` and source scope;
- `last_accepted_semantic_progress_at_utc`;
- `last_accepted_batch_id` and source scope;
- accepted result count;
- queue before / after / delta;
- `transactional_checks_all_passed`;
- `accepted_progress_in_last_execution`;
- `queue_presence_is_not_heartbeat = true`.

A successful zero-result execution may advance the execution heartbeat but does **not** advance `last_accepted_semantic_progress_at_utc`. Accepted progress advances only when the existing canonical runtime successfully contributes accepted results.

Repository-visible platform state is not fabricated: `scheduler_platform_enabled_state` and `expected_cadence_or_next_run_state` are explicitly `not_exposed_to_repository` when those platform fields are unavailable.

`semantic_runtime_observability.current_scope_progress_observed` is true only when the last accepted progress receipt is tied to the same `source_mailing_updated_at_utc` as the current prepared semantic scope.

Current concrete receipt after this fix:

- last successful / accepted progress: `2026-09-01T21:03:08+00:00`;
- accepted batch: `4f99eff1753a8ac9480e`;
- accepted results: `11`;
- queue progress on that accepted scope: `37 -> 26` (`delta = 11`);
- accepted scope source timestamp: `2026-09-01T20:47:04.563817+00:00`.

The current prepared scope is newer (`2026-09-02T20:36:22.419743+00:00`), therefore the canonical pre-AI payload truthfully reports:

- `semantic_runtime_observability.status = "no_current_scope_progress_observed"`;
- `current_scope_progress_observed = false`.

Thus queue presence can no longer masquerade as current runtime progress.

### 3. Exact semantic completeness/degraded contract

Canonical pre-AI payload is now schema version `5` and has a dedicated `semantic_completeness` object.

Its publication state is defined independently from family partition completion:

- `scope_partition_complete` mirrors the existing accounting/partition fact;
- `unresolved_semantic_count = ai_queue_count`;
- `resolved_semantic_count = ready_without_ai_count`;
- `total_relevant_semantic_scope = unresolved + resolved`;
- `unresolved_scope_source_mailing_updated_at_utc` records the canonical source timestamp while unresolved work exists;
- `unresolved_scope_age_seconds` is derived from that existing canonical timestamp;
- `unresolved_age_basis = "source_mailing_updated_at_utc"` makes the age meaning explicit;
- `sufficiently_complete_for_publication = true` only when partitioning is complete **and** unresolved semantic count is zero;
- semantic/top-level publication `status = "complete"` only in that sufficiently complete state; otherwise `status = "degraded"`.

Current canonical state demonstrates the intended distinction:

- `complete_family_partition = true`;
- `ai_queue_count = 644`;
- `semantic_completeness.unresolved_semantic_count = 644`;
- `semantic_completeness.total_relevant_semantic_scope = 644`;
- `semantic_completeness.sufficiently_complete_for_publication = false`;
- top-level `status = "degraded"`.

The visual builders apply the same semantic state to `data/production/visual/current.json`; unresolved semantic scope therefore cannot remain indistinguishable from a fully healthy visual publication merely because partitioning completed.

### 4. Validation evidence

Final bounded validation run:

- GitHub Actions run: `33712250775` — `success`.
- `python scripts/test_semantic_runtime_completion.py` — success, 6 focused tests.
- `python scripts/validate_taste_v3_contract.py` — success / `TASTE_V4_CONTRACT_VALIDATION=PASS`.
- `python scripts/validate_taste_inbox_transactional_proof.py` — success after aligning its stale fixture to the current production helper interface.
- `py_compile` for all touched producer/runtime files — success.
- `git diff --exit-code -- config/execution_ownership_contract.json` — success, proving the single-owner execution contract was unchanged.
- Commit/push stage — success.

Focused tests prove the required cases:

1. partition complete + non-empty unresolved queue => semantic state is `degraded`, not healthy completion;
2. a successful accepted runtime batch advances durable semantic progress and queue delta;
3. zero accepted results do not falsely advance accepted semantic progress;
4. an old accepted receipt does not prove progress for a newer prepared scope;
5. status application preserves the existing Taste contract fields and visual item set;
6. current canonical artifacts with unresolved work must publish degraded state and matching unresolved count.

The first bounded workflow attempt (`33711992125`) correctly passed the new focused tests and Taste V4 contract but exposed pre-existing drift in `validate_taste_inbox_transactional_proof.py`. The validator fixture was aligned to the current helper interface, and the final run above passed all required gates.

### 5. Remaining external/platform blocker

`none` for this implementation.

The repository still cannot directly read the scheduled-ChatGPT platform's enabled/disabled flag or exact next-run field. Per the task contract, those values are not invented; they remain explicitly `not_exposed_to_repository`. The newly persisted transactional execution/progress receipt is the smallest truthful durable equivalent available through the existing canonical interface.

This limitation does not require a second scheduler/runtime and does not block follow-up acceptance of the repo-side observability/completeness fix.

### 6. Follow-up acceptance ready now

`yes`

The repository now contains durable runtime progress evidence, current-scope correlation, an explicit degraded semantic completeness state, current canonical evidence of that state, and focused + existing validation evidence. A follow-up acceptance can evaluate the implemented mechanisms without manually processing the production queue.

## Exact refs

- Task: `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_FIX_01.md`
- Source acceptance: `reviews/worker_reports/semantic-runtime-completion-acceptance-01.md`
- Primary implementation commit: `61d11ee463cba39ff9e904bb6912b3a46e21b5fc`
- Transactional-validator alignment commit: `30552cf50bf73ed044ecdf716e6608033c77c78e`
- Final validation-gate commit: `522cac8b0e758b41fb303c601c1b128cf4bd0443`
- Final status refresh commit: `3bae54eb3c24c1264e6f41c3ec7bfbcf8a030ae0`
- Final successful validation run: `33712250775`
- `scripts/semantic_runtime_completion.py`
- `scripts/process_taste_inbox.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/build_visual_feed_v2.py`
- `scripts/build_final_visual_payload.py`
- `scripts/test_semantic_runtime_completion.py`
- `scripts/validate_taste_inbox_transactional_proof.py`
- `data/cache/taste_ingest_receipts/latest_runtime_status.json`
- `data/production/pre_ai/chatgpt_payload.json`
- `data/production/visual/current.json`
- `config/execution_ownership_contract.json`
- `.github/workflows/patch-semantic-runtime-completion-fix.yml`
