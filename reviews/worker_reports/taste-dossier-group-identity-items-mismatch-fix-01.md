# Taste Dossier group identity items mismatch fix 01

**Task:** `taste-dossier-group-identity-items-mismatch-fix-01`  
**Date:** 2026-09-22  
**Status:** `complete_ready_for_director_acceptance`

## Exact live diagnosis

Canonical snapshot at diagnosis and final pre-merge validation:

`9cf59f4d94d1b4c7270bece5464666e3eb2359b87bd74cbefe3883b969f90689`

The immutable descriptors were correct. The two actual submitted buffered candidates were inspected at their exact creation commits:

- g000001 candidate commit `559046f6ae9dd52343bed422b77e9fde7110e24f`;
- g000002 candidate commit `8746ad32e6004b3405eb5699c6dd5a385b18cb4c`.

For both groups, the smallest exact divergence from the immutable descriptor was identical: the candidate completely omitted the top-level `items` field. The candidate still copied `items_sha256`, `appids`, the range, group hash, provenance bindings, and dossiers, so this was not an ordering or normalization mismatch. It was one systematic structural omission.

GitHub's canonical validator was already correct and strict: `scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact` compares every descriptor identity field, including `items`, for exact equality before dossier acceptance. The validator therefore correctly classified both candidates with:

`buffered dossier group identity mismatch: items`

The producer-side cause was an under-specified transport serialization path: the semantic prompt said to copy immutable descriptor fields, but the active runtime/index projection did not expose the exact required field set or a machine-readable construction rule. The observed candidates reconstructed a partial descriptor-shaped payload and omitted the full `items` array while retaining its hash.

## Fix

The fix is producer-side and preserves canonical validation semantics.

- `config/taste_steam_review_dossier_runtime_prompt.md` is now revision `nonblocking-group-progress-v2-exact-buffer-identity`.
- Runtime guidance now requires a verbatim deep copy of the exact current compact group descriptor, replacement of only the top-level descriptor schema marker with `TASTE-STEAM-REVIEW-DOSSIER-BUFFERED-GROUP-V1`, and then addition of `dossiers`.
- Top-level `items` is explicitly mandatory. `items_sha256` never substitutes for `items`.
- `config/taste_steam_review_dossier_contract.json` now declares the canonical source of `buffer_identity_fields` and the exact `buffer_candidate_serialization_rule`.
- `scripts/taste_steam_review_dossier_worker_projection.py` projects those machine-readable instructions into the V2 worker index and provides `buffered_candidate_descriptor_projection`, which deep-copies the exact worker descriptor rather than rebuilding identity from partial fields.
- The active worker index for the current snapshot is updated in-place at the projection level only. Its immutable group descriptors and semantic evidence binding are unchanged.
- The active index lists `items` among the exact buffer identity fields and uses:
  `verbatim_deep_copy_group_descriptor_replace_schema_marker_then_add_dossiers`.
- Runtime-prompt binding remains intentionally outside the semantic evidence binding: `semantic_evidence_binding=false`, `descriptor_binding=false`, `worker_index_binding=true`.

No strict identity comparison was weakened, removed, normalized, or replaced by semantic-equivalence logic.

## Current canonical state preserved

Immediately before the durable report:

- accepted groups: 0;
- failed groups: 2;
- pending groups: 182;
- next pending group: g000003;
- g000001 remains `failed_or_invalid_pending_recovery`;
- g000002 remains `failed_or_invalid_pending_recovery`;
- both failed groups retain their canonical failure metadata and quarantine paths;
- g000003 remains pending and its immutable descriptor is unchanged.

The corrected branch projection for g000003 carries the exact descriptor `items` array:
- App_1085510 — Garfield Kart - Furious Racing;
- App_1086620 — Selfloss;
- App_1087760 — The Gunk.

Its descriptor hashes remain:
- `items_sha256=a98b9b83c3702620d7f80c35dc2805c1be5b4914adc8b04c3276775571b5484b`;
- `group_sha256=189be04eea3512ee3b69fdd3a50af751b396b7bb08110b723783b9a0ca2093a4`.

No failed group was reopened, rewritten, manually accepted, or removed from quarantine.

## Regression coverage

`scripts/test_taste_steam_review_dossier_prepublication.py` now proves:

- an exact descriptor-bound `items` copy is accepted by the same canonical buffered validator path;
- missing `items` is rejected;
- extra item is rejected;
- reordered items are rejected;
- normalized/coerced appid value inside `items` is rejected;
- extra field inside an item is rejected.

`scripts/test_taste_steam_review_dossier_parallel_validation.py` now proves:

- the runtime/index transport binding is outside semantic evidence binding;
- the active committed worker-index runtime hash equals the actual runtime prompt bytes;
- the active index exposes the canonical exact identity field list including `items`;
- the current pending descriptor can be projected by exact deep copy without schema-marker leakage;
- existing non-blocking progress and schedule-ownership rules remain intact.

During CI, an existing package-identity regression was found to depend on volatile live queue/family-graph membership for historical `Sub_87601`. Only that test fixture was made deterministic; package-identity implementation behavior was not changed.

## Validation

Final successful PR validation:

- PR: #85 — `Fix Taste Dossier exact group items serialization`;
- implementation head before durable-report-only closeout: `21d12d908fbbdc38a9e383237c74678c8b690c88`;
- workflow: `Validate buffered Steam review dossier runtime`;
- run: `35745448678` (#132);
- job: `106805768169`;
- conclusion: `success`.

The successful run passed all workflow stages, including:

- compile/focused regressions;
- execution ownership validation;
- daily snapshot regression;
- buffered submission regression;
- same-day preservation regression;
- strict recovery regression;
- prepublication parity regression;
- contract-gap regression;
- language binding;
- semantic consistency;
- transient-author fallback;
- Steam Store review-card parent;
- contract contradiction closeout;
- identity provenance generation;
- validator-generator parity;
- package identity;
- Story DLC semantic scope;
- parallel candidate validation and non-blocking per-group progress.

Earlier PR runs #129–#131 failed only while hardening newly exercised test fixtures; the final canonical validation is #132 and is green.

## Acceptance ITEM-ID-01..ITEM-ID-11

- **ITEM-ID-01 PASS** — exact first divergence for both g000001 and g000002 is proven: missing top-level `items`.
- **ITEM-ID-02 PASS** — producer path now deep-copies exact descriptor identity and exposes the canonical machine-readable field set.
- **ITEM-ID-03 PASS** — exact synthetic descriptor-bound candidate passes the canonical buffered validator/prepublication parity path.
- **ITEM-ID-04 PASS** — missing/extra/reordered/normalized/extra-field `items` mutations remain fail-closed.
- **ITEM-ID-05 PASS** — strict validator semantics were not weakened or changed.
- **ITEM-ID-06 PASS** — non-blocking per-group progress regression remains green.
- **ITEM-ID-07 PASS** — active-index regression validates the current pending descriptor through the corrected serialization path.
- **ITEM-ID-08 PASS** — g000001/g000002 remain failed/recovery and are not treated as accepted evidence.
- **ITEM-ID-09 PASS** — this worker did not run, edit, enable, disable, pause, delete, or reschedule the existing Scheduled Task; the separate user-triggered live validation run remains unconsumed.
- **ITEM-ID-10 PASS** — no PASS 1, PASS 2, or Taste Semantic Producer behavior was changed.
- **ITEM-ID-11 PASS on merge/reread** — this durable report is committed with the implementation and must be reread from `main` immediately before the final response.

## Files changed by implementation

- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_runtime_prompt.md`
- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `scripts/taste_steam_review_dossier_worker_projection.py`
- `scripts/test_taste_steam_review_dossier_prepublication.py`
- `scripts/test_taste_steam_review_dossier_parallel_validation.py`
- `scripts/test_taste_dossier_package_identity_fix.py` — deterministic fixture only; no package behavior change
- this durable report

No immutable worker-group descriptor, strict buffered validator implementation, semantic worker prompt, PASS 1/PASS 2 code, Taste Semantic Producer code, or Scheduled Task configuration was changed.

## Recommended next step

Director reviews and accepts this implementation. Do not consume the separate user-triggered `Run now` validation inside this worker task.
