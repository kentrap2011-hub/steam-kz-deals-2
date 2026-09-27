# Dossier visual progress refresh fix 01

## Task

- Task ID: `dossier-visual-progress-refresh-fix-01`
- Source of truth: `kentrap2011-hub/steam-kz-deals-2@main`
- Mode: IMPLEMENT / VALIDATE
- Goal: make canonically accepted Dossier progress propagate automatically into the published visual statistics without browser computation, Scheduled Task changes, or a second scheduler.

## Verified facts

1. The canonical Dossier progress source is `data/production/pre_ai/taste_steam_review_dossier_work.json`.
   - Fresh-main diagnosis and final verification both show current snapshot `81e44a924e2df85dcd3acab12954c12a5b2a04ab42f09405460a53d42ea241ea`.
   - Current scope: `418`.
   - Accepted: `6`.
   - Pending: `412`.
   - Failed/recovery: `0`.
   - Current canonical Git blob: `5c6fc0b71ec9560c4237f03e0696a714ad837d5f`.
2. The statistics page is a read-only consumer of the staged visual artifact:
   - `web/app.js` reads `web/data/current.json`;
   - `.github/workflows/deploy-visual.yml` stages `data/production/visual/current.json` to `web/data/current.json`;
   - `web/progressive-personalization-ui.js` renders Dossier fields from `processing_status`.
3. Dossier statistics are producer-owned:
   - `scripts/progressive_personalization.py::_dossier_processing_metrics()` reads the canonical Dossier work manifest and derives accepted/pending/failed counts;
   - `scripts/build_final_visual_payload.py` stamps those metrics into `processing_status`.
4. Before this fix, `.github/workflows/build-daily-visual-payload.yml` listened to Fast/PASS 1 and Deep/PASS 2 ingest completion, but not to successful `Ingest Steam review dossier checkpoint` completion.
5. Before this fix, visual compatibility/provenance bound Progressive context, contract, PASS 1 state and PASS 2 state, but did not bind the Dossier work-manifest blob even though Dossier counts are part of `processing_status`.
6. Current contracts already authorize GitHub-owned recomputation after canonical Dossier persistence and require browser read-only rendering, so no canonical contract amendment was required.

## Root cause

The defect had two linked parts, not only one missing trigger.

1. **Missing activation:** successful canonical Dossier ingest could persist new accepted progress without starting the existing visual rebuild workflow. GitHub-token commits from the ingest workflow are not a reliable recursive `push` activation path, while Fast/Deep already use `workflow_run`.
2. **Missing freshness binding:** the visual artifact had no provenance field for the exact Dossier work manifest. Therefore a visual with arithmetically valid but stale Dossier counters could still pass the Progressive compatibility check when only Dossier progress changed.

The frontend was not the source of the stale count; it rendered the prepared artifact it received.

## Changes

Merged through PR #100, squash merge commit `2ca0d40d65b13cf02dbc684699d95135f1813bbb`.

- `.github/workflows/build-daily-visual-payload.yml`
  - added existing upstream workflow `Ingest Steam review dossier checkpoint` to the existing `workflow_run` activation list;
  - no schedule, queue, retry loop or new recurring workflow was added.
- `scripts/build_final_visual_payload.py`
  - stamps `source_taste_steam_review_dossier_work_blob_sha` into `production_contract`.
- `scripts/progressive_visual_activation_routing.py`
  - binds compatibility to the current canonical Dossier work-manifest blob;
  - Dossier-only provenance drift now returns `dossier_work_provenance_mismatch` and requires the existing full Progressive visual rebuild path.
- `scripts/test_progressive_visual_activation_routing.py`
  - proves the Dossier ingest workflow remains an existing GitHub-owned activation source;
  - proves Dossier-manifest drift invalidates a stale visual;
  - preserves existing Fast/PASS 1 and Deep/PASS 2 activation checks.
- `scripts/test_progressive_personalization.py`
  - proves a canonical Dossier progress change from accepted/pending `0/4` to `3/1` changes producer-owned Dossier statistics without a semantic rerun.
- `PROJECT_ROUTES.md`
  - documents the reusable Dossier-statistics source → producer → visual activation → deploy route and exact provenance binding.

No frontend file, Scheduled Task configuration, Dossier semantic rule, recovery rule, snapshot identity, candidate state or recovery state was changed by PR #100.

## Validation

### Focused regression

PR head `8cd879dec257bb83ee55af5534864bb86f80f76b`:
- run `36319092108` — **Validate Progressive PASS 2 core: success**;
  - includes `scripts/test_progressive_personalization.py`;
  - includes `scripts/test_progressive_visual_activation_routing.py`;
  - therefore covers the new Dossier-count projection and Dossier-provenance activation regressions together with the existing Fast/Deep regressions.
- run `36319092066` — **Validate package purchase value: success**.

### Main build and publication

After merge:
- build run `36319121255` / Build daily visual payload #740 — **success**;
- it selected the existing full Progressive build route and produced visual commit `b3ed5ca68619ebcd22b76a05e7c4fd4803343aa1`;
- the build's freshness regression suite passed;
- deploy run `36319154460` / Deploy visual mailing #779 — **success**;
- Pages artifact `10932010682` contained `data/current.json` with:
  - total `418`;
  - Dossier accepted `6`;
  - Dossier pending `412`;
  - Dossier failed/recovery `0`;
  - Dossier provenance blob `5c6fc0b71ec9560c4237f03e0696a714ad837d5f`.

A subsequent normal commercial-only refresh also preserved the corrected Dossier statistics/provenance:
- build run `36319156099` / Build daily visual payload #741 — **success**;
- commercial visual commit `dcfefa09d3f0b903fee5c6ecec232b96119a0240`;
- commercial freshness receipt reported `fresh_build=true scope=commercial_only`;
- deploy run `36319184190` / Deploy visual mailing #780 — **success**;
- latest inspected Pages artifact `10932075636` contains:
  - `item_count=418`;
  - `dossier_total_current_scope=418`;
  - `dossier_accepted_count=6`;
  - `dossier_pending_count=412`;
  - `dossier_failed_or_recovery_count=0`;
  - `source_taste_steam_review_dossier_work_blob_sha=5c6fc0b71ec9560c4237f03e0696a714ad837d5f`.
- That provenance SHA exactly equals the current canonical Dossier work-manifest blob on `main`.

The general full-build freshness receipt was classified `degraded/no_fresh_build` with reason `deterministic_refresh_preserved_semantic_history`; this is an allowed non-semantic classification, not a failed guard. The deploy guard accepted the artifact and both deploy runs completed successfully. No Fast/Dossier/Deep semantic production was manually triggered for validation.

## Unresolved

None for the repository-owned propagation path. The latest inspected deployed artifact already contains the current canonical Dossier counts and exact manifest provenance.

A user's already-open browser may still need an ordinary page refresh to fetch the newly deployed artifact; that is not required for repository acceptance and no browser-side business logic was added.

## Status

`complete_ready_for_director_acceptance`

## Recommended next step

Director performs one bounded acceptance pass against this report and the latest deployed artifact `10932075636`; no additional implementation task is required for this fix.

## Exact refs

- Task: `WORKER_TASK_DOSSIER_VISUAL_PROGRESS_REFRESH_FIX_01.md`
- Report: `reviews/worker_reports/dossier-visual-progress-refresh-fix-01.md`
- PR: `#100`
- Merge: `2ca0d40d65b13cf02dbc684699d95135f1813bbb`
- PR validation runs: `36319092108`, `36319092066`
- Full visual build run: `36319121255`
- Full visual commit: `b3ed5ca68619ebcd22b76a05e7c4fd4803343aa1`
- Deploy run #779: `36319154460`
- Pages artifact #779: `10932010682`
- Follow-up commercial refresh run: `36319156099`
- Latest visual commit inspected: `dcfefa09d3f0b903fee5c6ecec232b96119a0240`
- Latest deploy run: `36319184190`
- Latest Pages artifact inspected: `10932075636`
- Canonical Dossier manifest: `data/production/pre_ai/taste_steam_review_dossier_work.json`
- Canonical/current Dossier blob: `5c6fc0b71ec9560c4237f03e0696a714ad837d5f`
- Published artifact: `web/data/current.json` staged from `data/production/visual/current.json`

## Efficiency / reusable lesson

A genuine reusable route gap was found: Dossier progress statistics crossed canonical persistence, Progressive visual generation and Pages publication, but that exact navigation path was not stated compactly. `PROJECT_ROUTES.md` was updated in PR #100 with the Dossier source → processing-status producer → workflow activation → provenance guard → deploy path, so future diagnosis should not require rediscovering these boundaries.
