# Dossier retryable transport reject fix 01

Status: `complete_fix_ready_semantic_retry_required`

Task: `WORKER_TASK_DOSSIER_RETRYABLE_TRANSPORT_REJECT_FIX_01.md`

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Implementation PR: #153 — `Surface head-blocking Dossier transport rejection`

## Scope and ownership

This task changed only the GitHub-owned Dossier transport / ingest observability and workflow outcome path. It did not act as the Dossier semantic worker, did not create or edit semantic Dossier results, did not change Fast / Deep / ranking / translation / Steam discovery / site publication semantics, and did not create, edit, enable, disable, reschedule, or run any ChatGPT Scheduled Task.

Architecture preflight result: PASS.

- Dossier immutable scope/order, validation, persistence, retryable transport quarantine, recovery and completeness remain owned by the GitHub control plane under `config/execution_ownership_contract.json`.
- Strict semantic validation remains fail-closed.
- A later unrelated movement of `main` does not invalidate a legitimate marker-parent frozen invocation.
- Invalid retryable transport consumes zero semantic attempts and remains normal pending work.
- No second queue, scheduler, retry loop, checkpoint owner or semantic authority was introduced.

## Root cause

The production block was not a frozen-authority, marker-parent, binding, sequence, concurrency, replay or stale-snapshot defect. Both existing submissions were authentic, exact-bound transports that correctly failed strict semantic validation.

Common frozen invocation:

- run-start anchor commit: `42afc85d3c9a97b103c2d2526d4f3e974030aa7c`;
- actual single parent / frozen authority: `3c942f78bef9bee68458d0b1c82b036b950525f6`;
- nonce: `0c518ff3afe0c3af6bed17d165c12f6e`;
- marker commit added only the canonical nonce-only run-start marker;
- sequence 20 and 21 candidate descriptors match the exact descriptors read from the marker parent, including snapshot, group plan, evidence binding and group SHA.

### Sequence 20

Submission commit: `d0a6ccd1d13179f52c77ae6071e2aa29184cc892`  
Ingest run: `37345670048`  
Group SHA: `9faef6aee0cc90d81f51a3b887e1dd5ef4322d4d6642459f657cf8657b218563`

Canonical rejection audit:

`route-exhaustion closure basis requires at least one exhausted unavailable dimension`

The failing dossier was `Once Upon a Jester`: it declared `closure_basis=sufficient_after_route_exhaustion` while none of its coverage dimensions was `exhausted_unavailable`. The current strict validator therefore rejected it correctly.

Transport consequences:

- candidate moved to retryable-transport quarantine;
- group state remained `pending`;
- normal first-pass semantic attempt was not consumed;
- no frozen-authority consumption was recorded.

### Sequence 21

Submission commit: `170c80e805769849a08eda1dc932a68a5bb38b5c`  
Ingest run: `37346094306`  
Group SHA: `70d0f6528fd95b6f6403893e26971a76975bc574e3d38a1a0286d78cf3e67e41`

Canonical rejection audit:

`provenance.player_feedback_records[3] acquisition_mode requires concrete_item_collection parent provenance`

The failing record was in `AWAKEN - Astral Blade`: an `inspected_collection_item` record referenced a parent source that did not declare the required `feedback_surface_mode=concrete_item_collection`. The current strict validator therefore rejected it correctly.

Transport consequences are the same: quarantine, pending group, zero semantic-attempt consumption, no force acceptance.

## Why the GitHub Action was green

The canonical state-based ingest intentionally used `--reconcile-nonfatal`. A retryable invalid transport was quarantined and audited, the Python command returned a structured `retryable_transport_rejected` result, and the workflow had no final step that converted the specific production-stopping case into a failed Action conclusion.

This meant a run could be green even when:

- accepted groups this run = 0;
- canonical progress this run = 0;
- the rejected sequence was the current `next_pending_sequence`;
- the head remained pending and the pipeline required a new valid semantic transport.

That was an observability / workflow-outcome defect, not an acceptance-validator defect.

## Implementation

### `scripts/taste_steam_review_dossier_buffered.py`

The drain result now exposes bounded structured retryable rejection details:

- sequence;
- transport kind;
- exact validator error;
- semantic-attempt-consumed flag;
- group-remains-pending flag.

No validation rule was relaxed.

### `scripts/ingest_taste_steam_review_dossier_inbox.py`

The canonical drain now distinguishes:

- `group_state_advanced_with_retryable_transport_rejection` — some canonical progress was persisted while another transport was quarantined;
- `retryable_transport_rejected_head_blocked_zero_progress` — zero canonical progress and the rejected sequence is the current pending head;
- `retryable_transport_rejected_nonblocking_zero_progress` — a later sibling was rejected while an earlier head remains pending.

The result also exposes:

- `canonical_progress_made_this_run`;
- `head_retryable_transport_rejected_this_run`.

### `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`

The workflow captures the structured drain status. For a zero-progress current-head rejection it still completes strict validation, PASS 2 recomputation and the canonical atomic quarantine/audit/projection commit first. Only after that durable persistence step does a final workflow step fail the Action.

Therefore:

- quarantine/audit cannot be lost merely to obtain a red Action;
- a head-blocking zero-progress rejection is no longer reported green;
- a non-head sibling rejection stays nonfatal;
- a mixed run with real progress stays successful;
- existing nonblocking group architecture is preserved.

## Regression coverage

`scripts/test_taste_steam_review_dossier_strict_recovery.py` now reproduces both production failure classes:

1. route-exhaustion closure without an `exhausted_unavailable` dimension => exact validator error, zero attempt, pending head, `retryable_transport_rejected_head_blocked_zero_progress`;
2. `inspected_collection_item` without `concrete_item_collection` parent provenance => exact validator error;
3. the same later-group provenance rejection while an earlier head is still pending => nonblocking zero-progress status;
4. a sibling is accepted while another is retryably rejected => persisted progress remains nonfatal;
5. workflow ordering assertion proves the red head-blocking outcome is evaluated only after the canonical commit step.

Existing frozen-authority regressions remain unchanged and continue to prove:

- legitimate marker-parent frozen transport survives unrelated later `main` movement;
- forged historical anchors fail;
- binding drift fails closed;
- consumed replay cannot overwrite newer compatible cache;
- frozen terminal handling remains audit-safe.

Validation initially exposed old date-drifting Dossier fixtures whose September-generated dossiers had naturally exceeded the 20-day TTL by 2026-10-05. Test-only anchors in the affected Dossier regressions were moved to the start of the current Samara day; the production TTL and timestamp validators were not changed. The coalescing test's Deep evaluation time was aligned to the same live fixture time so the test no longer depends on a historical September ordering assumption.

## Validation

Final tested PR head before report closeout: `ccfa76a17301fd64b99c4a0c747f4df3479b7dc0`.

Successful runs:

- Validate buffered Steam review dossier runtime: `37360603655` — success;
  - includes `Validate execution ownership boundaries` — success;
  - exact retryable rejection regressions — success;
  - canonical-writer coalescing liveness — success;
  - frozen invocation rollover — success;
  - atomic staging / terminal receipt / parallel validation regressions — success.
- Validate backlog dispositions: `37360603651` — success.
- Validate Progressive PASS 2 core: `37360603716` — success.

## Canonical production state after diagnosis

Fresh `main` state at report preparation:

- snapshot: `a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`;
- next pending sequence: `20`;
- accepted groups: `19`;
- failed groups: `0`;
- pending groups: `112`;
- accepted dossiers: `57`;
- pending dossiers: `334`.

The deterministic root inbox contains neither the rejected g000020 nor g000021 candidate anymore; both are preserved in retryable quarantine. Their normal semantic attempts remain unconsumed.

## Recovery / retry disposition

Neither quarantined semantic artifact is safe for direct recovery or force acceptance because each contains a real strict semantic-contract violation. They were not edited, rebound or replayed.

No explicit failed-group recovery authorization is needed for g000020: retryable transport rejection intentionally leaves it ordinary `pending` with zero attempt consumption. The canonical worker projection already points to sequence 20. A fresh canonical semantic invocation can therefore:

1. create a fresh run-start marker under the existing runtime contract;
2. freeze the exact marker-parent authority;
3. read current sequence 20 from GitHub-owned projection;
4. produce one new valid create-only g000020 transport at the deterministic path.

Sequence 21 also remains pending and may be produced again only as a new valid semantic transport under the canonical worker rules; its rejected artifact is not reusable.

## Final disposition

`complete_fix_ready_semantic_retry_required`

The technical transport/status defect is fixed without weakening strict validation. Canonical production progress intentionally remains at sequence 20 because this developer task was not authorized to perform Dossier semantics.

Next Director action: allow or manually invoke one normal run of the existing canonical Taste Steam Review Dossier semantic worker, without changing Scheduled Task configuration; it should resume from sequence 20.