# Worker Report — Taste Pinned Profile Batch Lifecycle Fix 01

- task_id: `taste-pinned-profile-batch-lifecycle-fix-01`
- lifecycle: `in_progress`
- current_utc: `2026-09-10T11:43:31Z`
- implementation_status: `implementation_present_tests_pending`
- next_action: `synchronize necessary Taste contracts, run focused lifecycle/ingest tests, verify existing 10-result grandfathering proof, then finalize this report`

## Scope guardrails

No semantic Taste run, ingest of the existing 10-result package, next-batch analysis, queue/cache mutation, production-data mutation, or Scheduled Task mutation is authorized in this task.

## Work already implemented

The following implementation commits are already present on `main` and are part of this task:

- `887505e28caf8dd89d3b6ad490980063be437bb5` — added `scripts/taste_pinned_work_unit.py`, introducing immutable Git-backed work-unit authority derived from the pre-result parent snapshot.
- `55b91fb098df983fb0e3cf95c17ebb1d5858560a` — changed `scripts/ingest_taste_results.py` so ingest validates against the durable pinned work-unit/profile authority instead of the current live profile at ingest time.
- `b3c8813649ad2238304ce7fc57e39af6cbcaf09f` — added focused lifecycle tests in `tests/test_taste_pinned_work_unit.py` covering A→B profile advancement, next-work-unit rebinding, stale-result rejection, binding/order mismatch rejection, and preservation of strict ingest validation.

## Implemented authority model

For a durable inbox result file, the result-introduction Git commit is identified. Its direct parent is treated as the canonical pre-semantic/pre-result snapshot. The exact projection/profile binding and first canonical ordered Taste work-unit rows from that parent are reconstructed and hashed. The result file must still match its introduction-commit bytes. Validation then requires exact agreement with the pinned profile/model/semantics/source and exact ordered key/appid/fingerprint/context rows.

This deliberately does not search arbitrary historical profile revisions. Copying or reintroducing an old result later binds it to the parent of the new introduction commit, so an old A-bound result introduced after the system has advanced to B cannot reach backward to an unrelated A snapshot.

## Existing 10-result package — current evidence

Candidate disposition pending final verification: `existing_batch_provably_grandfatherable_under_pinned_work_unit_rule`.

Evidence already established:

- pre-semantic checkpoint commit: `0ec1ed0ec10e8950f86e6f600bc360325481ae9b`;
- result-package introduction commit: `f138d5216248c999fde588c47ca5088ff9c076ee`;
- the result commit has the pre-semantic checkpoint as its direct parent;
- the pre-semantic checkpoint records profile blob `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`, exact ordered 10 subjects, and row fingerprint/context identities before semantic results appeared.

This must be rechecked against the implemented canonical invariant before finalizing.

## Tests

Not yet executed after the implementation commits. Required focused execution and final result recording remain pending.

## Contract synchronization

Pending. Only the Taste contracts strictly necessary to describe the pinned work-unit authority and ingest acceptance rule will be changed.
