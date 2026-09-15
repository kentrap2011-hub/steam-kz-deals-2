# Taste Dossier Worker View Recon 01

Status: `recon_complete_recommended_design_ready`

Task ID: `taste-dossier-worker-view-recon-01`

Mode: `READ-ONLY / RECON`

Date: 2026-09-15

## Result

Recommend **immutable per-group worker descriptor files plus one tiny GitHub-owned current pointer/index**.

The full canonical manifest must remain the sole source of truth for snapshot scope, immutable group plan, canonical expected sequence, progress, retry/gap/replay interpretation, persistence and completeness. The new artifacts are only mechanically derived read projections for the Scheduled Task. GitHub Actions remains the only control plane and the existing state-based maximal-valid-contiguous-prefix drain remains authoritative.

A single bounded `current-worker-view` containing a fixed number of full descriptors is not recommended as the primary design. It can satisfy the two-group acceptance criterion, but any fixed window becomes an artificial same-invocation throughput ceiling unless another paging/traversal mechanism is added. At that point it converges on the per-group-descriptor design anyway.

No existing repository artifact is sufficient as-is.

## Baseline / architecture preflight

Repository baseline immediately before this report write:

- repository: `kentrap2011-hub/steam-kz-deals-2`
- `main`: `edde2aee996db5be5d1ea4ff3c42d03f18b24216`
- canonical work manifest blob: `751ba6dce7b5340885398e4500ac4f1cf5c4f1ed`
- snapshot: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- prepared / completed / remaining: `594 / 0 / 594`
- `prepared_required_sha256`: `c519c99b165b11f2d64313849517753ca70dbd25ee7910206fd58dd9d929cbd3`
- immutable group count: `60`
- current canonical expected sequence: `1`
- `group_plan_sha256`: `513a495c947a21b1b7e1958569c76ef67c7dbe76808b0df95ef21be3129676de`

Architecture preflight:

1. **Current owner:** `config/execution_ownership_contract.json` assigns scope, manifest construction, ordering, retry state, checkpoint merge, persistence and completeness to GitHub. Scheduled ChatGPT is only a constrained semantic/data worker.
2. **Authorization:** TASTE-004/TASTE-005/TASTE-006 and the active dossier contract already authorize a fixed daily snapshot, GitHub-predeclared immutable group plan, create-only buffered transport and same-invocation `N -> N+1` traversal. Adding a GitHub-derived read projection is compatible with those decisions, but IMPLEMENT must first make the new projection explicit in the dossier contract/bridge and worker prompt.
3. **Ownership transfer:** the recommended design does not transfer any control-plane decision to ChatGPT. The worker only reads an exact GitHub-generated descriptor; it never constructs group contents, picks offsets, interprets retry state, or advances canonical progress.
4. **New scheduler/queue/quota/retry loop:** none. No new recurring stage, scheduler, quota, retry manager or backlog manager is required.

Preflight conclusion: `safe_to_recommend_contract_first_additive_read_projection`.

## Confirmed blocker

`reviews/worker_reports/taste-dossier-live-buffered-acceptance-02.md` proves the live blocker:

- the single authorized Scheduled Task invocation could not read far enough into the canonical manifest to reach authoritative `submission_group_plan` plus canonical expected sequence;
- repeated full/blob-style reads were also truncated in that runtime;
- the worker correctly refused to reconstruct a group from partial fields such as `ordered_appids`, `current_checkpoint_items` or checkpoint size;
- it published `0` buffered groups and claimed `0` canonical progress.

Current repository state independently confirms the manifest is large. Git tree metadata reports:

- `data/production/pre_ai/taste_steam_review_dossier_work.json`: **645,708 bytes**.

A bounded observer read shows `submission_group_plan` only after the large scope/progress arrays, and confirms exact groups 1 and 2 from the canonical plan. The exact live-reader byte limit is **unknown** and is not inferred here.

Representative size comparison, using the exact current group-1 descriptor fields:

- current full manifest: **645,708 bytes observed**;
- exact group-1 descriptor in the existing pretty JSON shape: about **2,986 bytes calculated**;
- proposed descriptor wrapper with schema and immutable plan binding: about **3,179 bytes calculated**;
- proposed current pointer/index including snapshot bindings, TTL and sampling policy: about **1.7 KB calculated**.

These proposed sizes are serialization estimates from current canonical data, not undocumented platform limits.

## Options compared

### Option 1 — one compact current-worker-view with a bounded multi-group window

Possible shape: one file containing snapshot identity, canonical expected sequence and the next 2/4/8 exact descriptors.

Advantages:

- one simple read at invocation start;
- easy to satisfy the immediate live acceptance requirement of two consecutive groups;
- straightforward GitHub-side derivation from the current manifest.

Material weakness:

- a fixed window becomes a per-invocation throughput ceiling even though `checkpoint_size=10` is explicitly not a run quota;
- after the worker exhausts the window, canonical expected sequence may intentionally still lag because buffered publication does not wait for ingest;
- re-reading the same current view therefore returns the same window and cannot safely reveal the next groups;
- making the window contain all remaining groups recreates a growing large-file reader risk;
- adding immutable pages/continuation files solves this, but then the design is effectively a form of option 2.

Verdict: useful as a short-lived workaround, not the best durable design.

### Option 2 — immutable per-group descriptors + tiny current pointer/index

Advantages:

- each full descriptor read stays bounded to one checkpoint-sized group;
- one invocation can continue `N -> N+1 -> N+2 -> ...` without waiting for canonical ingest;
- no fixed worker window becomes a hidden quota;
- group descriptor content is copied exactly from GitHub's existing immutable `submission_group_plan`;
- current canonical expected sequence remains a tiny mutable GitHub-owned value;
- same-snapshot descriptor files never change when canonical progress advances;
- daily rollover can replace the read projection without changing the canonical manifest model;
- GitHub's existing drain still validates buffered output against the full canonical manifest, not against the projection.

Costs:

- more generated files;
- both existing canonical manifest writers must keep the tiny pointer consistent with manifest progress;
- build and ingest workflows must stage the new projection paths atomically with the canonical changes they already own;
- prompt and regression coverage must be updated.

Verdict: **recommended**.

### Option 3 — reuse an existing repository artifact

No existing small artifact carries the required authority:

- `current_checkpoint_items` / `current_checkpoint_sha256` live inside the oversized manifest and describe only the current checkpoint; they do not provide the immutable buffered group identity or the next groups;
- `taste_active_work_unit.json` belongs to downstream Taste semantic pinning and must not become dossier-group authority;
- `chatgpt_payload.json` does not contain the exact dossier group descriptor/plan;
- dossier inbox files are worker outputs/transport artifacts, may not exist at invocation start, and are explicitly not canonical progress/retry/resume authority;
- contract/bridge/prompt files define rules, not the current snapshot's exact work descriptor.

Verdict: `no_change_needed_existing_surface_sufficient` is not supportable.

## Recommended exact design

### 1. Tiny mutable current pointer/index

Proposed path:

`data/production/pre_ai/taste_steam_review_dossier_worker_index.json`

Proposed schema:

`TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V1`

Required fields:

```json
{
  "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V1",
  "schema_version": 1,
  "work_manifest_path": "data/production/pre_ai/taste_steam_review_dossier_work.json",
  "snapshot_id": "<64 hex>",
  "prepared_for_date": "YYYY-MM-DD",
  "prepared_required_sha256": "<64 hex>",
  "group_plan_sha256": "<64 hex>",
  "group_count": 60,
  "canonical_expected_sequence": 1,
  "completed_required_count": 0,
  "prepared_required_count": 594,
  "remaining_required_count": 594,
  "full_backlog_complete": false,
  "ttl_days": 20,
  "sampling_policy": { "...": "exact snapshot sampling policy" },
  "scope_source": "daily_fixed_snapshot_of_full_current_canonical_taste_queue",
  "source_queue_sha256": "<64 hex>",
  "descriptor_path_template": "data/production/pre_ai/taste_steam_review_dossier_worker_groups/{snapshot_id}/g{sequence:06d}.json"
}
```

For a complete snapshot, `canonical_expected_sequence` must be `null` and `full_backlog_complete=true`.

`ttl_days` and the exact snapshot sampling policy are included because the current worker previously obtained those from the manifest and must not guess them after the manifest is removed from the live read path.

### 2. Immutable per-group descriptor files

Proposed path template:

`data/production/pre_ai/taste_steam_review_dossier_worker_groups/{snapshot_id}/g{sequence:06d}.json`

Proposed schema:

`TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1`

Required fields:

```json
{
  "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1",
  "schema_version": 1,
  "snapshot_id": "<exact canonical snapshot_id>",
  "prepared_required_sha256": "<exact canonical prepared_required_sha256>",
  "group_plan_sha256": "<exact canonical group_plan_sha256>",
  "group_count": 60,
  "sequence": 1,
  "start_index": 0,
  "end_index_exclusive": 10,
  "items": ["<exact canonical ordered group items>"],
  "appids": ["<exact canonical ordered appids>"],
  "items_sha256": "<exact canonical items_sha256>",
  "group_sha256": "<exact canonical group_sha256>",
  "scope_source": "<exact canonical scope_source>",
  "source_queue_sha256": "<exact canonical source_queue_sha256>"
}
```

The canonical group descriptor fields must be copied byte-for-semantic-value from `submission_group_plan.groups[]`; no worker-specific recomputation may change their meaning or identity. `group_plan_sha256` and `group_count` are projection-level bindings added to make wrong-plan/stale-set detection explicit.

The descriptor filename intentionally depends only on GitHub-provided `snapshot_id` and `sequence`. The worker may calculate only the filename for the immediately next integer sequence from the GitHub-provided template. That is address resolution, not descriptor reconstruction: the file content itself is authoritative, and a missing/mismatched file causes a stop.

### 3. Bounded lifecycle

- Same snapshot: descriptor files are immutable and must remain byte-identical while progress advances.
- Canonical progress: only the tiny index changes its expected/progress fields.
- Daily rollover: GitHub generates the new snapshot's descriptor set and new index in the same canonical-writer commit as the new manifest. Old current-tree projection directories should be removed by GitHub so the working tree does not accumulate unbounded historical copies; Git history already preserves old commits.
- Same-day migration/adoption: generate the index/descriptors from the already-preserved current manifest and its existing group plan. Do **not** rebuild queue/store scope, change `snapshot_id`, reorder groups, reset progress or rewrite dossier cache.

## Source of truth and ownership

The source-of-truth hierarchy must remain:

1. `data/production/pre_ai/taste_steam_review_dossier_work.json` = canonical snapshot, immutable plan and canonical progress.
2. Worker index/descriptors = GitHub-generated read projection only.
3. `data/ai_inbox/taste_steam_review_dossiers/*.json` = create-only transport only.
4. `data/cache/taste_steam_review_dossiers/**` = canonical persisted dossier cache after GitHub validation.

GitHub drain must continue reading and validating against the full canonical manifest. It must **not** switch canonical acceptance to trust the compact worker projection.

Scheduled ChatGPT may read the projection and publish exact buffered results, but may never write the index/descriptors, infer a replacement group, scan the buffer as a resume queue, skip a gap, or advance completeness/progress.

`config/execution_ownership_contract.json` does not need an ownership change.

## Same-invocation `N -> N+1` traversal

Required worker algorithm:

1. At invocation start, read the tiny worker index.
2. If complete, stop with no work.
3. Take exactly `canonical_expected_sequence = N` as the starting sequence.
4. Read only descriptor `g{N:06d}.json` under the exact index snapshot.
5. Validate descriptor schema plus exact equality of `snapshot_id`, `prepared_required_sha256`, `group_plan_sha256`, `group_count`, `scope_source`, and `source_queue_sha256` to the index; require descriptor `sequence=N`; recompute/verify `items_sha256` and existing canonical `group_sha256` formula.
6. Process only those exact items and create only the deterministic buffered artifact already defined by the persistence bridge.
7. After successful create-only publication of N, set the local traversal target only to `N+1`; do **not** wait or poll until GitHub changes canonical expected sequence.
8. Re-read the tiny index once as a snapshot/plan liveness guard, not as a progress gate. The same snapshot/plan must still be current. It is valid for canonical expected sequence to remain at N while the worker is already moving to N+1. If canonical state has advanced beyond the local next sequence, or the snapshot/plan has changed, stop rather than skip/reconcile.
9. Read descriptor `g{N+1:06d}.json`, validate it independently, and repeat while healthy and `sequence <= group_count`.

The only sequence arithmetic permitted is `previous_sequence + 1`, already authorized by the buffered contract. The worker never derives items, appids, hashes, ranges or retry meaning from that arithmetic.

## Fail-closed semantics

The worker must stop before publication or before proceeding to a later group when any of the following occurs:

- index missing/unreadable/unsupported;
- index says work exists but `canonical_expected_sequence` is null/out of range;
- descriptor missing/unreadable;
- descriptor snapshot/plan/source bindings differ from the index;
- requested sequence differs from descriptor sequence;
- `items_sha256` or canonical `group_sha256` recomputation fails;
- same invocation observes a newer snapshot or different group plan;
- canonical expected sequence has moved beyond the worker's immediate local next sequence;
- create-only buffer write fails or deterministic artifact already exists;
- any dossier validation requirement cannot be met.

There must be **no live fallback that reconstructs a descriptor from the full manifest's partial fields**. Once the compact read surface is activated in the live prompt, missing/inconsistent projection is a GitHub-side defect and the worker stops.

GitHub-side generation must also validate the complete projection against the canonical manifest before commit. A projection-generation failure must fail the writer before push, leaving remote canonical state unchanged.

## Migration / compatibility

This is additive with respect to business architecture, but it is **not** a data-file-only change.

Required alignment in future IMPLEMENT:

- canonical contract: declare worker read projection ownership, schemas, paths and fail-closed semantics;
- persistence bridge: declare compact worker read surface as the active descriptor source while preserving existing create-only buffer transport;
- repository worker prompt: stop requiring a full-manifest read; use index + per-group descriptors and the same-invocation algorithm above;
- GitHub builder/runtime: generate and validate the projection from the canonical manifest and keep the pointer synchronized after canonical progress;
- workflows: stage the new files in the same commits as their owning canonical writer.

The current snapshot can adopt the projection additively. Its `snapshot_id`, `prepared_required_items`, group plan, completed prefix and remaining suffix do not need to change. The current 60 descriptors can be projected from the existing immutable plan. The current index would start at sequence 1.

No change is required to:

- Taste Semantic Producer prompt/schedule/limits/state;
- Taste semantic pin authority;
- buffered inbox naming/schema;
- maximal-contiguous-prefix drain semantics;
- `config/execution_ownership_contract.json`.

## Trigger / production analysis

Current `Build pre-AI deterministic payload` push paths already include:

- `config/taste_steam_review_dossier_contract.json`;
- `scripts/taste_steam_review_dossier_daily.py`;
- `scripts/taste_steam_review_dossier_buffered.py`;
- `scripts/build_taste_steam_review_dossier_work.py`;
- the two existing dossier regression suites;
- its own workflow file.

Therefore landing IMPLEMENT changes to those files on `main` will automatically trigger production pre-AI preparation. IMPLEMENT should use a branch/PR and perform a pre-merge trigger audit; no manual workflow dispatch is required.

The current pre-AI workflow stages `taste_steam_review_dossier_work.json` explicitly but does not stage the proposed index/group directory, so its atomic commit step must be updated.

The dossier ingest workflow triggers only on `data/ai_inbox/taste_steam_review_dossiers/*.json` and currently stages dossier cache, canonical manifest and inbox. It must additionally stage the worker index when canonical progress advances. Updating the index in a drain commit will not self-trigger the ingest workflow because the index path is outside the inbox trigger.

Both writers already share concurrency group `taste-steam-review-dossier-canonical-writer` with `cancel-in-progress: false`; the new projection must stay inside that same serialized writer boundary. No new scheduler/concurrency domain is needed.

A post-merge automatic pre-AI run should prove same-day additive adoption by generating the new projection from the preserved current manifest without changing current snapshot identity/scope/order/progress. Any unexpected manifest reset/rebuild is a failure.

## Exact files expected to change in IMPLEMENT

Minimum expected repository change set:

1. `config/taste_steam_review_dossier_contract.json`
2. `config/taste_steam_review_dossier_persistence_bridge.json`
3. `config/taste_steam_review_dossier_worker_prompt.md`
4. `scripts/taste_steam_review_dossier_daily.py`
5. `scripts/build_taste_steam_review_dossier_work.py`
6. `scripts/ingest_taste_steam_review_dossier_inbox.py`
7. `.github/workflows/build-pre-ai-store-snapshot.yml`
8. `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
9. `scripts/test_taste_steam_review_dossier_daily_snapshot.py`
10. `scripts/test_taste_steam_review_dossier_buffered_submission.py`

Generated outputs added by those changes:

- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `data/production/pre_ai/taste_steam_review_dossier_worker_groups/{snapshot_id}/gNNNNNN.json`

A separate helper module is not required; the projection builder/validator can live with the existing daily dossier control-plane helpers. `scripts/taste_steam_review_dossier_buffered.py` only needs modification if IMPLEMENT chooses to place pointer refresh directly inside the buffered apply primitive rather than in the canonical inbox adapter; that is an implementation placement choice, not a new architectural requirement.

`PROJECT_DECISIONS.md` and `config/execution_ownership_contract.json` should not require change because TASTE-006 and the current ownership contract already authorize the relevant ownership/transport semantics.

## IMPLEMENT definition of done

Future IMPLEMENT is done only when all of the following are proven:

- contract/bridge/prompt agree on the new active worker read surface;
- projection is mechanically derived from the canonical manifest/group plan only;
- current snapshot additive migration produces all 60 exact descriptor projections without rebuilding or reordering scope;
- the manifest remains canonical and GitHub drain still validates against it;
- worker index reports the exact canonical expected sequence derived from manifest progress;
- same-snapshot canonical progress changes only mutable pointer/progress fields; every per-group descriptor remains byte-identical;
- new daily snapshot atomically replaces the active projection and old-snapshot projection cannot authorize current publication;
- legacy compatibility ingest, while retained, also leaves the worker pointer synchronized after any canonical progress advancement;
- missing/stale/mismatched projection tests fail closed;
- synthetic 25-item `10/10/5` tests prove descriptor sequences 1/2/3, unchanged descriptor identity after progress and pointer advancement 1 -> 2 -> 3 -> complete;
- existing buffered gap/replay/wrong-snapshot/maximal-contiguous-prefix regressions remain green;
- pre-AI and ingest workflow commits include the correct projection paths under the existing canonical-writer serialization;
- no Taste Semantic Producer file/state/schedule/limit is changed;
- no manual production workflow dispatch is needed;
- post-merge automatic pre-AI read-back proves current production snapshot/progress preservation.

No arbitrary byte threshold should be added as a fake platform contract. The structural size guarantee is instead: pointer contains O(1) current state and each descriptor contains exactly one checkpoint-sized canonical group.

## Live ACCEPTANCE definition of done

After IMPLEMENT is landed and the new repository prompt is separately installed into the live Scheduled Task, a live acceptance must:

1. capture baseline `main`, canonical manifest, worker index, exact descriptor N and descriptor N+1, and prove the two deterministic inbox artifacts are absent;
2. authorize exactly one user `Run now`;
3. observe in that single invocation that the worker starts from index `canonical_expected_sequence=N`, reads exact descriptor N, creates N, then moves to exact descriptor N+1 without polling/waiting for canonical progress to advance;
4. prove the second group is created by the same invocation and no full-manifest reconstruction/fallback occurred;
5. use the invocation's tool/action trace to prove there was no wait-for-ingest gate between successful create of N and acquisition/start of N+1; if GitHub happens to ingest N quickly before N+1 finishes, that natural race does not count as waiting, but the trace must still show the worker did not depend on that advancement;
6. verify GitHub drain accepts only the correct maximal contiguous prefix, persists exact dossiers, removes only accepted transport artifacts and advances canonical progress by exactly the accepted group item count;
7. verify no duplicate, alternate filename, reorder, scope drift, wrong-snapshot application or skipped sequence;
8. require at least two consecutive groups from the one invocation for PASS.

If the live worker cannot read the new compact index/descriptor, if it falls back to guessing, or if only one group is published because it waits for canonical advancement, acceptance remains blocked/fail-closed.

## Efficiency / context note

This recon took longer than a simple code lookup because the START gate required multiple canonical contracts/reports plus bounded reconstruction of the oversized production manifest and workflow writer paths. The durable speed improvement is exactly the recommended compact worker read surface: future live Scheduled Task invocations should not need the 645 KB manifest at all. A future `PROJECT_ROUTES.md` entry could also point dossier-worker investigations directly to contract -> bridge -> worker prompt -> work manifest -> daily/buffered helpers -> the two canonical-writer workflows; this READ-ONLY task intentionally did not modify route documentation.

## One next step

Create and execute one bounded **IMPLEMENT** task for the recommended per-group descriptor + current pointer/index read projection, including contract/bridge/prompt alignment, GitHub writer synchronization, regression coverage and same-day additive migration proof. Do not run live acceptance until that IMPLEMENT has landed and been read back from `main`.

## Final status

`recon_complete_recommended_design_ready`
