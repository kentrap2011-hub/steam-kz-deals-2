# WORKER TASK — Taste Dossier Worker View Implement 01

Task ID: `taste-dossier-worker-view-implement-01`
Mode: `IMPLEMENT`

## Goal
Implement the compact GitHub-owned worker read projection recommended by `taste-dossier-worker-view-recon-01` so the live Scheduled Task no longer needs to read the oversized canonical dossier manifest to obtain exact immutable group descriptors.

The durable design to implement is:
- full canonical manifest remains source of truth;
- one tiny mutable worker index/pointer;
- one immutable small descriptor file per submission group;
- Scheduled Task starts from canonical expected sequence in the index and traverses `N -> N+1 -> N+2...` by reading the next immutable descriptor file, without waiting for canonical ingest of N;
- GitHub drain continues validating against the full canonical manifest and remains authoritative.

Do not redesign this into a bounded multi-group window unless a concrete implementation blocker proves the accepted design impossible. If the accepted design cannot be implemented safely, stop and report `blocked`.

## START gate
Read fully before any write:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-worker-view-recon-01.md`
- `reviews/worker_reports/taste-dossier-buffered-submission-implement-01.md`
- `reviews/worker_reports/taste-dossier-buffered-activation-state-align-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-acceptance-02.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current canonical dossier work manifest
- relevant current dossier builder/runtime/workflow/tests.

Read `PROJECT_ROUTES.md` before broad search if required by protocol.

Perform architecture preflight before source/workflow/runtime changes.

## Required architecture

### Canonical source of truth
Keep this hierarchy:
1. `data/production/pre_ai/taste_steam_review_dossier_work.json` = canonical snapshot, immutable submission group plan and canonical progress.
2. Compact worker index/descriptors = mechanically derived GitHub-owned read projection only.
3. `data/ai_inbox/taste_steam_review_dossiers/*.json` = create-only transport only.
4. dossier cache = canonical persisted dossiers only after GitHub validation.

GitHub ingest/drain MUST continue validating buffered submissions against the full canonical manifest, not merely the compact projection.

### Worker index
Implement the recon design at:
`data/production/pre_ai/taste_steam_review_dossier_worker_index.json`

Schema identifier:
`TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V1`

The index must be O(1) current-state data and include at minimum the exact bindings needed by the worker:
- schema/schema_version
- canonical work manifest path
- snapshot_id
- prepared_for_date
- prepared_required_sha256
- group_plan_sha256
- group_count
- canonical_expected_sequence (null only when canonically complete)
- prepared/completed/remaining counts
- full_backlog_complete
- TTL and exact sampling-policy information the worker previously required from the full manifest
- scope/source queue bindings
- descriptor path template.

Do not introduce an arbitrary platform byte limit as a contract.

### Immutable per-group descriptors
Implement under:
`data/production/pre_ai/taste_steam_review_dossier_worker_groups/{snapshot_id}/g{sequence:06d}.json`

Schema identifier:
`TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1`

Each descriptor must contain the exact canonical immutable group descriptor copied/derived mechanically from `submission_group_plan.groups[]`, plus projection-level binding fields needed to prove correct snapshot/plan identity, including at minimum:
- snapshot_id
- prepared_required_sha256
- group_plan_sha256
- group_count
- sequence
- start_index
- end_index_exclusive
- exact ordered items and appids
- items_sha256
- group_sha256
- scope_source
- source_queue_sha256.

Same-snapshot descriptor files must remain byte-identical as canonical progress advances.

### Same-invocation traversal
Repository worker prompt and contract must define this behavior:
1. Read tiny index at invocation start.
2. Start exactly at `canonical_expected_sequence=N`.
3. Read/validate exact descriptor N.
4. Process/publish N using existing create-only buffered transport.
5. After successful publication, local target may become only `N+1`; do not wait for canonical ingest/progress N.
6. Re-read tiny index only as snapshot/plan liveness guard, not as progress gate.
7. If snapshot/plan remains same and canonical state has not advanced incompatibly beyond the local next sequence, read exact descriptor N+1 and continue.
8. Repeat while healthy and within group_count.

Only `previous_sequence + 1` address traversal is allowed. Worker must never derive/reconstruct descriptor contents.

### Fail-closed behavior
Stop safely on at least:
- missing/unreadable/unsupported index;
- invalid/null/out-of-range expected sequence while work remains;
- missing/unreadable descriptor;
- snapshot/plan/source binding mismatch;
- descriptor sequence mismatch;
- hash validation failure;
- newer snapshot/different group plan observed;
- canonical expected sequence advanced beyond the immediate local next sequence in a way requiring reconciliation;
- deterministic buffered artifact already exists while canonical state has not resolved it;
- create/write failure;
- any dossier validation failure.

No live fallback may reconstruct descriptors from partial fields in the full manifest.

## Writer synchronization
Both canonical manifest writer paths must keep the compact projection consistent under the existing serialized canonical-writer boundary.

### Daily/pre-AI writer
When preparing/preserving a snapshot:
- generate/validate the index and all immutable group descriptors from the canonical manifest/group plan;
- same-day preservation/adoption must NOT rebuild scope, alter snapshot_id, reorder groups, reset progress or rewrite fresh dossiers;
- for the current already-existing snapshot, add the projection from the current preserved manifest/group plan;
- new daily snapshot atomically replaces active projection;
- old active-tree descriptor directories should not accumulate unbounded current copies; Git history may preserve history.

### Ingest/drain writer
When canonical progress advances:
- update the tiny worker index to the new canonical expected/progress state in the same canonical writer commit;
- do not mutate same-snapshot immutable descriptor files;
- legacy compatibility ingest, if it can still advance canonical progress, must also leave index synchronized.

Keep the existing concurrency group/serialization ownership. Do not create a second scheduler, queue, retry manager or writer domain.

## Contract/prompt alignment
Update the minimum necessary canonical surfaces so they agree that the active live worker descriptor source is the compact worker projection:
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`

Keep buffered create-only transport and GitHub drain semantics unchanged.

Do not change `config/execution_ownership_contract.json` unless a genuine contradiction is discovered. If ownership would need to change, stop and report `blocked` rather than broadening scope.

`PROJECT_DECISIONS.md` should change only if a genuinely new durable architecture/policy decision is required; do not add noise for implementation detail already covered by the accepted recon/architecture.

## Expected implementation surfaces
The recon identified this minimum likely change set; verify and adjust only as technically necessary:
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier_daily.py`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- relevant existing dossier regression suites, including daily snapshot and buffered submission tests.

`scripts/taste_steam_review_dossier_buffered.py` should change only if required by correct placement of projection synchronization logic.

## Trigger / production safety
Config/runtime/workflow changes can trigger automatic production workflows on merge to `main`.

Before first write:
- inspect relevant push triggers;
- use a worker branch + PR rather than piecemeal direct-main implementation;
- no manual GitHub workflow dispatch;
- no Scheduled Task `Run now`;
- do not claim automatic runs did not occur if they do.

After merge, observe automatic production effects read-only and prove same-day additive adoption preserves the current canonical snapshot/progress/scope/order and dossier cache.

## Required tests / validation
At minimum prove:
- index/descriptors are mechanically derived from canonical manifest/group plan;
- synthetic 25-item snapshot produces exact 10/10/5 descriptors 1/2/3;
- pointer/index advances 1 -> 2 -> 3 -> complete with canonical progress;
- same-snapshot descriptors remain byte-identical after progress changes;
- missing/stale/mismatched index/descriptor fail closed;
- wrong snapshot/group-plan/source/hash/sequence fail closed;
- current buffer gap/replay/wrong-snapshot/maximal-contiguous-prefix regressions remain green;
- GitHub drain still validates against canonical manifest, not compact projection;
- both canonical writer workflows stage the correct projection paths atomically;
- current production snapshot can adopt the projection additively with same snapshot_id, prepared scope/hash, group plan, completed prefix and remaining suffix;
- no fresh dossier cache entries are rewritten unnecessarily;
- Taste Semantic Producer is untouched.

Do not rely only on unit tests if a safe automatic post-merge production pre-AI run provides the required current-snapshot preservation proof; report both.

## Live Scheduled Task boundary
Do NOT edit or inspect the live Scheduled Task UI in this IMPLEMENT task.
Do NOT ask the user to press Run now.
Do NOT perform live acceptance here.

The repository worker prompt may be updated as part of implementation, but the user-facing live Scheduled Task prompt/UI remains a separate manual/acceptance step after Director accepts this IMPLEMENT.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-worker-view-implement-01.md`

Report must include:
- architecture preflight;
- final design implemented;
- exact files changed;
- branch/PR/merge refs;
- schemas/paths introduced;
- tests and run IDs/results;
- automatic workflow effects after merge;
- production current-snapshot adoption proof;
- exact read-back of index + at least descriptors 1 and 2 on landed `main`;
- proof descriptors are small/bounded compared with the full manifest using observed file sizes only;
- proof prompt/contract/bridge agree;
- proof GitHub remains canonical owner and drain still validates full manifest;
- explicit confirmation no Scheduled Task run/UI edit and no Taste Semantic Producer change occurred;
- one next step only: separate live prompt alignment/manual UI step if needed, then separate live ACCEPTANCE.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `implementation_incomplete`

Stop after durable report. Do not run live acceptance.