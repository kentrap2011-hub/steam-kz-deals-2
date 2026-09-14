# Taste Dossier Buffered Contract 01

Task ID: `taste-dossier-buffered-contract-01`  
Mode: `IMPLEMENT — CONTRACT ONLY` + bounded read-only side-effect verification  
Date: 2026-09-14  
Repository: `kentrap2011-hub/steam-kz-deals-2`

## Final status

`complete_ready_for_director_acceptance`

The canonical buffered-submission contract is written and remains `authorized_not_activated`. The automatic production refresh caused by the first contract commit was separately verified read-only against current durable GitHub state. It did **not** lose the 40 already persisted dossiers, did **not** recreate work for them, did **not** introduce duplicate dossier work, and does **not** require recovery.

## Architecture preflight

1. **Owner:** `config/execution_ownership_contract.json` unambiguously keeps scope, ordering, retry/unresolved state, checkpoint merge, completeness, validation, canonical persistence and orchestration in GitHub. Scheduled ChatGPT remains a constrained semantic/data worker.
2. **Canonical authorization before this task:** dossier V2 fixed the full daily `prepared_required_items[]`, but authorized only the mutable current-checkpoint submission path. The buffered RECON correctly concluded that future groups before canonical ingest required a contract change.
3. **No control-plane transfer:** the new contract permits only local traversal of exact immutable GitHub-predeclared groups after successful create-only publication. It does not give ChatGPT canonical progress, retry, gap, replay, stale, cleanup or completeness authority.
4. **No new ChatGPT queue/backlog manager:** buffer is transport only. GitHub remains the sole queue/retry/completeness owner. No new recurring stage or production quota is authorized.

Architecture preflight verdict: safe contract-only architecture; `config/execution_ownership_contract.json` did not require modification.

## Files changed by this worker

Contract task implementation:

- `config/taste_steam_review_dossier_contract.json`
  - commit `f208ebbd3009f5085564cf118c9d2841c6e505b0`
- `config/taste_steam_review_dossier_persistence_bridge.json`
  - commit `0c13fe0e7e0035860191841080cbdadcefd49771`
- `PROJECT_DECISIONS.md`
  - commit `bba236f1bcaeb1689d44e839fe4ff8b62e7ebd6e`
- `reviews/worker_reports/taste-dossier-buffered-contract-01.md`

The follow-up side-effect verification changed only this report. No runtime, workflow, manifest generator/schema implementation, production cache/state, Scheduled Task, Taste Semantic Producer, schedule or limits were intentionally edited by the worker.

## What the canonical contract now authorizes

The dossier contract authorizes, but does **not activate**, a buffered mode with these rules:

- GitHub fixes the full daily snapshot and order, then predeclares immutable contiguous groups, normally size 10.
- Every group identity binds `snapshot_id`, `prepared_required_sha256`, `sequence`, `start_index`, `end_index_exclusive`, exact ordered items/appids, `items_sha256`, `group_sha256`, `scope_source` and `source_queue_sha256`.
- Group identity is independent of mutable `remaining_required_items` / current `scope_sha256`.
- After successful create-only publication of group N, the worker may process only predeclared N+1 without waiting for canonical ingest N. This is worker traversal only, not canonical progress.
- Each group is a separate immutable create-only transport artifact; multiple pending groups for one snapshot are allowed.
- Buffer is explicitly not canonical progress, retry state, a ChatGPT queue or completeness authority.
- Alternate retry filenames and worker overwrite/update/delete are forbidden.
- If the deterministic artifact for the current canonical expected group already exists while canonical progress has not advanced, a later worker invocation must not overwrite, rename, skip or invent retry state; it stops and leaves interpretation to GitHub.
- After interruption, a new invocation reloads GitHub canonical progress and starts from GitHub's expected group; it does not scan the buffer to invent resume order.

## GitHub drain / ownership rules

The persistence bridge specifies the future GitHub-owned drain:

- a buffer push is only a wake-up signal;
- GitHub derives `expected_sequence` from canonical progress;
- GitHub validates exact predeclared group identity, order, range, hashes, provenance and every dossier;
- GitHub accepts only the maximal valid contiguous prefix;
- `expected=5; buffer=5,6,7,8` may accept `5,6,7,8`;
- `expected=5; buffer=5,6,8` accepts `5,6` and stops at missing `7`;
- malformed/stale-or-wrong-snapshot/reordered/out-of-scope/wrong-identity/invalid expected groups block later groups;
- stale old-snapshot artifacts cannot mutate the current snapshot;
- replay of an already accepted sequence cannot persist or advance canonical state again;
- cleanup belongs only to GitHub;
- all GitHub processes capable of mutating the dossier canonical manifest must share one serialized canonical-writer boundary, at minimum future buffer drain and daily pre-AI snapshot preparation;
- checkpoint size `10` remains a durability boundary, never a run/day/production quota.

`config/execution_ownership_contract.json` was not changed. GitHub remains control plane; Scheduled ChatGPT remains constrained semantic/data plane. Taste Semantic Producer ownership and behavior were not changed.

## Transition mechanism

The contract-first change deliberately retains the runtime-facing V2/V1 identifiers and current validated legacy values:

- dossier contract remains `TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2`, version `2`, status `active`;
- current manifest remains `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2`;
- current legacy create-only path `{snapshot_id}--{scope_sha256}.json` remains active;
- buffered transport is `authorized_not_activated`;
- current worker prompt remains current-checkpoint-only and was not edited;
- buffered activation requires future manifest group-plan support, validator/drain runtime, shared writer serialization, worker-prompt alignment, regression validation and Director acceptance.

This preserves compatibility with the current strict V2 loader and keeps the current production runtime on the legacy current-checkpoint path until the separate IMPLEMENT task.

## Current snapshot migration rule

The contract authorizes a future IMPLEMENT to migrate an unfinished fixed snapshot without rebuilding scope only when all of the following are proven from the existing manifest:

- preserve the same `snapshot_id`;
- derive the group plan only from existing `prepared_required_items[]`;
- prove `prepared_required_sha256` matches those items;
- prove `completed_required_count = prepared_required_count - remaining_required_count`;
- prove `remaining_required_items[]` is exactly `prepared_required_items[completed_required_count:]`;
- prove the accepted prefix lands on a group boundary unless the snapshot is already complete;
- treat groups fully inside that accepted prefix as already accepted, with no recreate/re-ingest;
- continue from the first unaccepted group;
- fail closed if exact prefix/suffix/order/boundary proof cannot be established.

The automatic daily refresh already converted the old snapshot's accepted work into reusable fresh canonical dossiers, so there is no need to recover or migrate the superseded `d75f...` snapshot itself. A future buffered IMPLEMENT operates on whichever snapshot is current at activation time and applies the migration proof rule only if that current snapshot already has accepted prefix progress.

## Contract/doc validation

Validation performed for the contract change:

- architecture preflight against execution ownership, current dossier contract/bridge, worker prompt, buffered RECON, live-prompt acceptance, TASTE-004/TASTE-005 decisions and relevant worker pitfalls;
- read-back of both changed JSON contracts from `main`;
- per-commit diff inspection of the implementation commits;
- compatibility comparison against `scripts/taste_steam_review_dossier_daily.py` strict V2 loader requirements;
- `config/execution_ownership_contract.json` remained unchanged;
- `config/taste_steam_review_dossier_worker_prompt.md` remained current-checkpoint-only, so buffered traversal was not activated;
- no ingest script, daily snapshot script, runtime manifest generator/schema implementation, GitHub Actions workflow file, live Scheduled Task, Taste Semantic Producer, schedule or limits were edited by this worker.

## Automatic production refresh: read-only verification

### Trigger history

The first contract commit `f208ebbd3009f5085564cf118c9d2841c6e505b0` matched the existing `push.paths` entry for `config/taste_steam_review_dossier_contract.json` and automatically launched `Build pre-AI deterministic payload` run `34855356658`.

That run completed successfully and published `a8095bd96a6a99f8f7addab0cb82dd6b7d5b9c50` (`Refresh atomic pre-AI payload`). The worker did not manually dispatch that workflow, did not press `Run now`, and did not run the live Scheduled Task.

### Current active durable snapshot

Current `data/production/pre_ai/taste_steam_review_dossier_work.json`:

- `snapshot_id = 243b8a97751bebc7a7e7e590ce95bbb9701e0bbebc90ed2a727cb2f8ef94647e`
- `prepared_required_count = 543`
- `completed_required_count = 0`
- `remaining_required_count = 543`
- `checkpoint_size = 10`
- first current checkpoint begins:
  - `1158890`
  - `1159290`
  - `1161580`
  - `1164940`
  - `1167450`
  - `1169040`

`completed_required_count=0` is expected for a newly prepared snapshot. It is **not** evidence that the already persisted dossier files were rolled back: daily preparation first reuses currently fresh canonical dossiers and only then constructs the new `prepared_required_items[]` from remaining missing/stale work.

### Previously accepted 40 dossiers are preserved

Before the automatic refresh, the accepted snapshot `d75f0b64dc983883a3d97a29c1ba1e0f25c679060ffdb5de269c10fadf05a180` had:

- `prepared_required_count = 584`
- `completed_required_count = 40`
- `remaining_required_count = 544`
- next checkpoint beginning with `1158890, 1159290, 1161580, 1164940, 1167450, 1169040, ...`.

Durable history contains four successful `Ingest Steam review dossier checkpoint` commits for that snapshot:

- `71c7e9b428a0b27f31722266470312e448ecbbd1`
- `72f73703f3a09813370caaf0f46163a4da1162dd`
- `d9aecc014a9298cf10dab5f0a6de5ebb7707dfec`
- `aa14b6444110f40f0d46eb8fb19ab90c4d5ff51a`

Each checkpoint canonically persisted ten dossier files, giving the accepted 40.

The current refreshed manifest reads those canonical dossier files and records them as `state = fresh` with their existing `generated_at_utc`, `expires_at_utc` and `dossier_sha256`. Examples cover every persisted checkpoint generation period (`04:40`, `04:46`, `04:50`, `11:38` UTC). The manifest remains continuously `fresh` through `App_1156990`; the very next item, `App_1158890`, is `missing` and becomes the new first checkpoint.

Therefore:

- the 40 canonically persisted dossiers are still present and valid;
- they are being reused as fresh;
- they are not present in `prepared_required_items[]` and will not be reprocessed merely because the snapshot was refreshed;
- there is no progress rollback hidden by the new snapshot's `completed_required_count=0`.

### Scope comparison and the `544 -> 543` change

Old snapshot / source:

- source rows: `594`
- unique eligible appids: `592`
- after 40 accepted: `544` required remained.

New snapshot / source:

- source rows: `593`
- unique eligible appids: `591`
- new required work: `543`.

The one removed scope item is `App_2788520` (`Cozy Caravan`):

- it existed in the old canonical Taste queue and old ordered dossier scope;
- it is absent from the current canonical Taste queue;
- it is correspondingly absent from the new ordered dossier scope.

This is a current control-plane scope change, not an accidental dossier-progress loss. It is well after the accepted 40-item prefix and therefore does not invalidate or reinterpret any persisted checkpoint.

Arithmetic is exact:

- old remaining after persisted progress: `544`;
- one item no longer in current canonical scope: `544 - 1 = 543`;
- new prepared/remaining required count: `543`.

### Duplicate / replay / rollback assessment

- **Repeated work for the accepted 40:** none. They are fresh reuse, not new required items.
- **Lost accepted dossiers:** none observed; the new manifest validates and hashes them as fresh canonical files.
- **Accidental scope loss:** none. The only scope decrease is the one appid removed from the current canonical Taste queue.
- **Duplicate work:** none observed. The refreshed manifest keeps canonical appid dedupe (`eligible_row_count=593`, `unique_appid_count=591`, `deduplicated_row_count=2`) and starts required work exactly at the old post-40 next checkpoint.
- **Incorrect progress rollback:** none. The numeric per-snapshot progress counter resets because this is a new snapshot, while persisted dossier facts survive in the canonical dossier store and are excluded from new required work.
- **Replay of the first 40:** no evidence; current checkpoint is `1158890...`, not any already persisted checkpoint.

### Safety verdict

The new snapshot is a **safe rebuild of the current canonical scope**. The automatic run changed snapshot identity because it performed a normal daily fixed-scope preparation against the then-current canonical Taste queue, but it correctly reused the 40 already persisted dossiers as fresh canonical cache entries.

No recovery task is required.

## Acceptance / next step

The previous blocker is resolved by durable read-only verification. The buffered contract can be accepted by the Director.

Recommended next step after Director acceptance: a **separate buffered-submission IMPLEMENT task** implementing:

- immutable group-plan representation in the work manifest/runtime schema;
- current-snapshot migration/proof logic when needed;
- buffered group validator and maximal-contiguous-prefix drain;
- shared serialized canonical-writer rule for all dossier-manifest writers;
- state-based workflow wake-up behavior;
- worker prompt activation only after runtime support exists;
- synthetic/regression acceptance before any separately authorized production activation.

This worker stops here and does not proceed to runtime IMPLEMENT.

Efficiency / reusable lesson: contract-only writes to production-triggered config paths require trigger-awareness/isolation; the unintended refresh was safe here because canonical dossier freshness reuse preserved accepted work, but trigger behavior must still be accounted for explicitly in future contract tasks.