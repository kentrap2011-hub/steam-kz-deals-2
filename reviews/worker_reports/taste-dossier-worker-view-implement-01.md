# Worker Report — taste-dossier-worker-view-implement-01

- Task ID: `taste-dossier-worker-view-implement-01`
- Mode: `IMPLEMENT`
- Final status: `complete_ready_for_director_acceptance`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Implementation branch: `worker/taste-dossier-worker-view-implement-01`
- Pull request: `#27` — `Implement compact Taste dossier worker view`
- Implementation branch head before merge: `01ea99000042e94fb3c1338585f4c2272f2f6893`
- Merge commit: `4d8c521cbb30cb91a1bbac1636b7c13647849a02`

## Summary

Implemented the RECON-selected compact worker view without changing runtime ownership. The large canonical Steam review dossier work manifest remains the source of truth for snapshot scope, immutable group plan, canonical progress, validation, persistence, gap/retry/replay interpretation, cleanup, and completion. GitHub now derives a small worker index plus one immutable descriptor file per canonical group. The scheduled dossier worker contract reads that compact projection and may advance locally from group N to N+1 after successful create-only publication without waiting for canonical ingest of N.

The GitHub buffer drain remains authoritative against the full canonical manifest and its immutable group plan. The compact projection is explicitly noncanonical and is not used as drain acceptance authority.

## Architecture preflight

Preflight was completed before implementation against the task, protocol/context, accepted RECON report, current dossier contract/bridge/prompt, execution ownership contract, canonical writers, buffered drain, tests, and workflows.

Result:

- no execution ownership change required;
- no new scheduler required;
- no independent queue required;
- no new retry domain required;
- no Taste Semantic Producer ownership or authority change required;
- existing GitHub canonical-writer serialization remains the correct boundary;
- `config/execution_ownership_contract.json` therefore remained unchanged.

## Implemented files

PR #27 changed exactly these dossier control-plane files:

1. `.github/workflows/build-pre-ai-store-snapshot.yml`
2. `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
3. `.github/workflows/validate-taste-dossier-buffered.yml`
4. `config/taste_steam_review_dossier_contract.json`
5. `config/taste_steam_review_dossier_persistence_bridge.json`
6. `config/taste_steam_review_dossier_worker_prompt.md`
7. `scripts/build_taste_steam_review_dossier_work.py`
8. `scripts/ingest_taste_steam_review_dossier_inbox.py`
9. `scripts/taste_steam_review_dossier_worker_projection.py` — new
10. `scripts/test_taste_steam_review_dossier_daily_snapshot.py`

Not changed by the implementation:

- `config/execution_ownership_contract.json`;
- `scripts/taste_steam_review_dossier_buffered.py` drain logic;
- Taste Semantic Producer;
- active pin/ranker semantic authority;
- live Scheduled Task configuration/UI.

## Compact worker projection

New schemas:

- index: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V1`;
- descriptor: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1`.

Paths:

- index: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`;
- descriptor root: `data/production/pre_ai/taste_steam_review_dossier_worker_groups`;
- descriptor template: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/{snapshot_id}/g{sequence:06d}.json`.

`scripts/taste_steam_review_dossier_worker_projection.py` derives the complete projection only from a validated full canonical manifest and validated immutable group plan. It validates the index and every descriptor against the canonical derivation and canonical hash rules before accepting the projection as valid.

The index contains only bounded snapshot/plan/progress/sampling/address bindings needed by the worker, including:

- snapshot/prepared/group-plan hashes;
- group count;
- canonical expected sequence;
- prepared/completed/remaining counts and completion state;
- TTL and exact review sampling policy;
- scope/source queue bindings;
- descriptor path template.

Each descriptor contains the exact immutable canonical group projection plus projection-level snapshot/plan bindings. Existing descriptors for the same snapshot are required to remain byte-identical; any attempted same-snapshot descriptor rewrite fails closed. Canonical progress updates therefore rewrite only the small index while preserving descriptor bytes.

On daily rollover, GitHub replaces the active projection with the new snapshot projection and removes old snapshot descriptor directories from the current tree.

## Writer integration and serialization

The existing daily manifest writer now synchronizes the compact projection after building or preserving the canonical manifest. Same-day preservation semantics remain unchanged: a current same-day snapshot is preserved rather than rebuilt from current queue/store state.

The existing inbox/drain adapter synchronizes the compact projection only after successful canonical progress persistence. Buffered acceptance still reloads and validates the full canonical manifest before projection synchronization.

Both GitHub writers continue to share:

`concurrency.group = taste-steam-review-dossier-canonical-writer`

with `cancel-in-progress: false`.

The pre-AI workflow stages the canonical manifest, worker index, and worker descriptor tree in the same atomic pre-AI commit. The ingest workflow stages canonical progress, dossier cache/inbox changes, worker index, and worker descriptor tree in the same canonical writer commit.

## Scheduled worker traversal contract

The repository worker prompt now requires the worker to:

1. read the compact worker index;
2. start from its GitHub-owned `canonical_expected_sequence`;
3. read exactly descriptor `gN`;
4. validate descriptor/index snapshot, plan, source, sequence, item and group hash bindings;
5. publish only the deterministic create-only buffered artifact for that group;
6. after successful create-only publication, advance locally only to `N+1` without waiting for canonical ingest of N;
7. re-read the small index between sequential local groups only as a snapshot/plan/binding liveness guard, not as a canonical-progress gate;
8. stop fail-closed on a missing, unreadable, stale, or inconsistent projection.

The prompt explicitly forbids reconstruction of a missing descriptor from partial full-manifest fields. A successful create-only publish remains transport durability only and is not treated as canonical acceptance.

## Canonical drain authority

The actual buffered drain module `scripts/taste_steam_review_dossier_buffered.py` was not changed by this implementation.

Its acceptance source remains the full canonical dossier work manifest and its validated immutable group plan. The contract and persistence bridge explicitly state that the compact projection is not acceptance authority. Gap, malformed-group, wrong-snapshot, replay, duplicate, ordering, scope and dossier validation remain GitHub control-plane responsibilities.

Thus the new worker view changes only worker read ergonomics; it does not weaken canonical GitHub validation.

## Regression validation

PR validator workflow:

- run: `34949403614`
- workflow: `Validate buffered Steam review dossier runtime`
- result: `SUCCESS`

The validator ran:

- `scripts/test_taste_steam_review_dossier_daily_snapshot.py`;
- `scripts/test_taste_steam_review_dossier_buffered_submission.py`;
- `scripts/test_taste_steam_review_dossier_same_day_preservation.py`.

New compact-view regression coverage includes:

- synthetic 25-item snapshot produces exact descriptor sizes `10 / 10 / 5`;
- index canonical pointer advances `1 -> 2 -> 3 -> null/complete` as canonical progress advances;
- all same-snapshot descriptor file bytes remain identical through those progress transitions;
- mismatched index plan binding fails closed;
- descriptor mismatch for snapshot, plan hash, source queue hash, sequence, items hash or group hash fails closed;
- missing descriptor fails closed;
- workflow atomic staging of index/descriptor tree is asserted;
- the buffered drain module is asserted not to reference the compact worker index and still validates the full group plan.

Existing buffered transport and same-day preservation regressions also remained green.

## Merge and automatic post-merge effects

PR #27 was merged through commit:

`4d8c521cbb30cb91a1bbac1636b7c13647849a02`

No manual GitHub workflow dispatch was used.

The merge automatically triggered the existing production workflows. Observed results:

- `Build pre-AI deterministic payload` run `34949449672`: `SUCCESS`;
- `Validate execution ownership` run `34949449447`: `SUCCESS`.

The automatic pre-AI writer successfully ran the normal build/regression path and created bot commit:

`6b5fede0d6f90c5f4b523fe14f6d6ae8b0b87770` — `Refresh atomic pre-AI payload`.

That commit materialized the compact projection for the already-existing current snapshot.

A later unrelated automatic commit became current `main` head:

`c03d34ae7a8f625013601b94582cf439469d2f65` — `automation: refresh commercial visual payload`.

Its parent is `6b5fede0...` and its changes are limited to commercial visual payload/queue files, so it does not alter the landed dossier implementation or compact projection.

## Current snapshot additive adoption proof

Current dossier snapshot bindings after automatic projection adoption:

- snapshot_id: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`;
- prepared_for_date: `2026-09-15`;
- prepared_required_sha256: `c519c99b165b11f2d64313849517753ca70dbd25ee7910206fd58dd9d929cbd3`;
- group_plan_sha256: `513a495c947a21b1b7e1958569c76ef67c7dbe76808b0df95ef21be3129676de`;
- group_count: `60`;
- prepared/completed/remaining: `594 / 0 / 594`;
- canonical_expected_sequence: `1`;
- full_backlog_complete: `false`;
- source_queue_sha256: `116687b59c35629b2f6e74b79fe0c1f467aac605994ddddd5fc84874a339df0d`.

Comparison of merge commit `4d8c521...` to automatic projection commit `6b5fede...` showed the new worker index and descriptors `g000001` through `g000060`. Crucially:

- `data/production/pre_ai/taste_steam_review_dossier_work.json` was not changed by that automatic same-day adoption commit;
- `data/cache/taste_steam_review_dossiers/**` was not changed by it.

Therefore the current snapshot received the new compact worker files additively without rebuilding dossier scope, resetting canonical progress, or rewriting fresh dossier cache.

The prior full canonical manifest remained the large source of truth (baseline size observed during RECON: `645,708 bytes`); the worker no longer needs it as its routine live read surface.

## Descriptor fidelity readback

Landed `g000001` readback:

- sequence `1`, range `0..10`;
- appids: `2378500, 1000360, 1003590, 1003890, 1025440, 1034860, 1047010, 1062040, 1071870, 107310`;
- items_sha256: `0ee433d4124187a4476e29d4722bda90e680e670bcbe67152ec36e349e598b3d`;
- group_sha256: `74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06`.

Landed `g000002` readback:

- appids: `1077970, 1079800, 1082710, 1083790, 1104380, 1143810, 1147560, 1152300, 1152310, 1157390`;
- items_sha256: `02ff44bad19a5773b6aa9f5af154879d7b4bc07216b2042aa302e462e971ee1f`;
- group_sha256: `f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a`.

These match the accepted RECON bindings, confirming that the production compact descriptors are faithful projections of the canonical group plan rather than newly selected/recomputed work.

## Scope guards observed

This task deliberately did not perform any of the following:

- no Scheduled Task UI inspection or modification;
- no `Run now`;
- no manual GitHub workflow dispatch;
- no Taste Semantic Producer change;
- no execution ownership change;
- no independent scheduler/queue/retry mechanism;
- no live Scheduled Task acceptance.

## Residual / next phase

Live Scheduled Task acceptance is intentionally outside this IMPLEMENT task. A separate acceptance phase may verify that the installed live worker actually consumes the compact index/descriptors and demonstrates sequential publication behavior under the new read surface. No such live invocation was performed here.

## Conclusion

`taste-dossier-worker-view-implement-01` is complete and ready for director acceptance. The compact GitHub-derived worker view is merged, automatically materialized for the existing snapshot without changing canonical scope/progress, protected by regression tests, and leaves the full canonical manifest/drain as the authoritative control plane.