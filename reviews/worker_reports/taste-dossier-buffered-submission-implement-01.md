# taste-dossier-buffered-submission-implement-01

Status: `complete_ready_for_director_acceptance`

Implementation mode: `IMPLEMENT`

Landing date: 2026-09-15

## Summary

The accepted buffered-submission contract is implemented and landed. ChatGPT dossier preparation can now publish multiple immutable sequential group artifacts for one fixed daily snapshot without waiting for GitHub canonical ingest between groups. GitHub remains the control plane: it owns immutable scope/group identity, canonical expected sequence, validation, maximal-contiguous-prefix draining, canonical persistence, cleanup, replay/gap behavior, and writer serialization.

The repository worker prompt is updated for buffered operation, but the live Scheduled Task UI was deliberately not changed. Buffered live mode is therefore **not activated** by this task and still requires a separate live-acceptance task.

## Architecture preflight

Before implementation, the task was routed to `kentrap2011-hub/steam-kz-deals-2` and the required protocol/context/contract/recon material was read, including the current dossier contract, persistence bridge, execution ownership contract, repository worker prompt, current canonical work manifest, dossier preparation/ingest workflows and relevant tests.

Preflight findings that shaped the implementation:

- `data/production/pre_ai/taste_steam_review_dossier_work.json` has two GitHub-side writer paths: daily pre-AI snapshot preparation and dossier ingest/drain. They therefore require one common serialized canonical-writer boundary.
- Existing live Scheduled Task behavior was still legacy current-checkpoint submission. Landing a buffered-only ingest would have broken that task before separate live acceptance, so ingest was made transition-safe: buffered state-based drain is implemented while exact legacy current-checkpoint ingest remains accepted during the activation window.
- The dossier ingest workflow must treat a push as a wake-up signal, not as the authoritative artifact payload. It now checks out current `main` state and derives work from repository state.
- Production `push.paths` were checked before landing. Changes to dossier/pre-AI runtime files necessarily trigger `Build pre-AI deterministic payload`; dossier drain itself triggers only on `data/ai_inbox/taste_steam_review_dossiers/*.json`.
- The current durable snapshot was re-read before landing rather than restoring any historical snapshot. No attempt was made to restore the old `d75f...` snapshot.

## Branch / PR / merge refs

Implementation branch:

- `worker/taste-dossier-buffered-submission-implement-01`

Pull request:

- PR #25 — `Implement buffered Taste dossier submission drain`
- final validated head: `ebac7f25e5748700da48148193b8548aed579a40`

Key continuation commits after the earlier interrupted implementation:

- `bc49d02294b7c2a5504602749cf5e7184201a492` — same-day snapshot preservation / additive migration
- `ac71b4295e9f3641e912326b8242ec1dc9c959f0` — deterministic group-plan test fixture correction
- `f51169d8c57d9ea38ff649767ef67f64327241fd` — same-day preservation regression tests
- `fbb409bf4457382d7bdfd26c046b65c849dc3503` — branch validation runs all dossier suites
- `ebac7f25e5748700da48148193b8548aed579a40` — temporary worker-branch push validation trigger removed

Merge:

- PR #25 merged to `main`
- merge commit: `a9a393cbb2fd394dbc792c870d6e1571138bc369`

Automatic post-merge pre-AI canonical commit:

- `aa57bcfab64cb0eafa6c38d23a8ef3769819e972` — `Refresh atomic pre-AI payload`

A later automated visual-chain commit:

- `ab6b847359c4f873e86b83959c65a6522befd654` — changed only `data/production/visual/current.json`; it did not touch dossier canonical state or dossier cache.

## Files changed by PR #25

- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `.github/workflows/validate-taste-dossier-buffered.yml`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/taste_steam_review_dossier_buffered.py`
- `scripts/taste_steam_review_dossier_daily.py`
- `scripts/test_taste_steam_review_dossier_buffered_submission.py`
- `scripts/test_taste_steam_review_dossier_same_day_preservation.py`

No Taste Semantic Producer prompt/schedule/limits/queue/state/ownership file was changed by this implementation.

## Final immutable group schema

The canonical work manifest may contain:

- schema: `TASTE-STEAM-REVIEW-DOSSIER-GROUP-PLAN-V1`
- `schema_version: 1`
- `snapshot_id`
- `prepared_required_sha256`
- `checkpoint_size`
- `group_count`
- ordered `groups[]`
- `group_plan_sha256`

Each immutable group descriptor contains:

- `snapshot_id`
- `prepared_required_sha256`
- stable `sequence`
- `start_index`
- `end_index_exclusive`
- exact ordered `appids`
- exact ordered `items`
- `items_sha256`
- `group_sha256`
- `scope_source`
- `source_queue_sha256`

The group plan is derived only from immutable `prepared_required_items[]` and its canonical hash. It is independent of mutable canonical progress (`remaining_required_items`, current checkpoint, or current `scope_sha256`). Therefore earlier canonical advancement cannot change later group identity.

Synthetic 25-item coverage proves the required partition is exactly `10 / 10 / 5` and group identities remain stable after progress advancement.

## Buffer path and artifact schema

Buffered artifact schema:

- `TASTE-STEAM-REVIEW-DOSSIER-BUFFERED-GROUP-V1`
- `schema_version: 1`

A buffered artifact copies the complete immutable group descriptor exactly and adds `dossiers[]`, with exactly one valid dossier for each planned appid in canonical order.

Deterministic path:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json`

The worker contract requires GitHub **create-file only** publication. It forbids overwrite/update, alternate retry filenames, direct canonical manifest editing, direct canonical dossier-cache editing, and worker-selected scope/order.

Validation is fail-closed for wrong/current snapshot identity, wrong sequence/range/hash, reordered/missing/extra appids, duplicate/alternate artifacts for an expected sequence, and malformed dossiers.

## State-based drain behavior

`push` of a buffer file is now only a wake-up signal.

Each serialized drain:

1. checks out current `main` rather than the triggering commit as source of truth;
2. reads the current canonical work manifest;
3. validates the immutable group plan;
4. derives the expected sequence from canonical completed progress;
5. inspects buffered artifacts for the current snapshot;
6. validates and accepts the maximal valid contiguous prefix only;
7. stops at the first gap or invalid expected group and never jumps over it;
8. applies the whole accepted prefix to one next canonical manifest state;
9. writes accepted dossier cache entries, writes the manifest once, and removes only buffer artifacts belonging to accepted groups;
10. commits the resulting canonical change as one GitHub commit.

Examples covered by tests:

- expected 4 + buffer 4,5,6,7 => accepts 4,5,6,7;
- expected 4 + buffer 4,5,7 => accepts 4,5 and stops at gap 6;
- expected 4 + valid 4,5 + malformed 6 + valid 7 => accepts 4,5, leaves 6 and 7 pending;
- future group before its gap is durable but inert;
- old-snapshot buffer artifacts are inert against the current snapshot;
- replay of an already accepted earlier sequence does not advance progress again.

## Serialization

Both GitHub writers of `data/production/pre_ai/taste_steam_review_dossier_work.json` now use the same Actions concurrency group:

`taste-steam-review-dossier-canonical-writer`

Minimum covered writers:

- `Build pre-AI deterministic payload` / daily dossier snapshot preparation;
- `Ingest Steam review dossier checkpoint` / state-based buffer drain.

`cancel-in-progress: false` is used so one canonical writer completes before the next enters the boundary. Ingest also re-reads current repository `main` state after it obtains its execution slot rather than trusting event payload state.

## Recovery behavior

The implementation and tests cover the required recovery cases:

- If ChatGPT publishes three sequential groups and GitHub only canonically accepts the first, later group files remain durable. A later drain resumes from repository canonical expected sequence and can accept the remaining contiguous files.
- If a GitHub run fails before canonical push, remote canonical state and remote buffer artifacts remain unchanged; a later run can derive the same drain again from repository state.
- A group after a gap remains pending and cannot advance canonical state until the gap is filled.
- Old-snapshot artifacts cannot mutate a newer current snapshot.
- Worker restart does not authorize overwrite or an alternate filename. The repository worker prompt requires reload of canonical state; if the deterministic current artifact already exists while progress has not moved, the worker stops and leaves recovery to GitHub drain/operator handling.
- Replays are idempotent with respect to progress.
- Multi-group accepted prefixes are validated before application and canonical manifest advancement is performed once for the accepted prefix.

## Same-day migration / transition

A material landing risk was found during implementation: rebuilding the fixed daily manifest later on the same day from newly changed queue/cache state could erase already accepted same-day progress or change group identity.

`scripts/build_taste_steam_review_dossier_work.py` now implements `build_or_preserve_daily_work`:

- an existing valid manifest for the current Samara date is preserved rather than rebuilt;
- if it is a pre-group-plan V2 manifest, migration is additive via `ensure_submission_group_plan`;
- `snapshot_id`, `prepared_required_items[]`, `prepared_required_sha256`, accepted prefix, remaining exact suffix and existing progress remain unchanged;
- TTL cannot be changed inside an already prepared same-day snapshot;
- a future-dated existing snapshot fails closed;
- a new daily snapshot is built only after the date boundary.

Migration validation requires:

- canonical `prepared_required_sha256` to match the exact prepared list;
- `remaining_required_items[]` to equal the exact prepared suffix after the completed prefix;
- incomplete accepted progress to end on a group boundary;
- no recreation/re-ingest of already accepted groups.

The accepted-prefix migration test includes a 25-item snapshot progressed through 20 items, removes the group plan to model the legacy schema transition, then proves migration preserves the same snapshot/progress and derives expected group 3. A deliberately non-boundary legacy state fails closed.

## Current production transition proof

The durable repository state was re-read immediately before landing. At that time the current snapshot was already the September 15 Samara snapshot:

- `snapshot_id`: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- `prepared_for_date`: `2026-09-15`
- `eligible_scope_count`: 628
- `prepared_required_count`: 594
- `completed_required_count`: 0
- `remaining_required_count`: 594
- current checkpoint count: 10

The merge-triggered pre-AI run then reported:

- `mode = preserved_same_day_snapshot`
- `group_plan_added = true`
- the same `snapshot_id`
- the same source queue binding
- `prepared_required_count = 594`
- `completed_required_count = 0`
- `remaining_required_count = 594`

The resulting canonical manifest now has a 60-group immutable plan: groups 1-59 each contain 10 items, and group 60 covers indices 590..594 with exactly 4 items. `prepared_required_sha256` remained `c519c99b165b11f2d64313849517753ca70dbd25ee7910206fd58dd9d929cbd3`.

The post-merge pre-AI commit changed 13 pre-AI artifacts and **did not change any** `data/cache/taste_steam_review_dossiers/**` file. Thus already-fresh dossier files were not rewritten. The current snapshot had 628 eligible appids and only 594 required, so the already-fresh/non-required suffix outside prepared work was not reintroduced into the dossier work plan.

No historical `d75f...` snapshot was restored.

## Worker prompt

`config/taste_steam_review_dossier_worker_prompt.md` now stages the buffered worker contract:

- reload canonical GitHub state at every invocation;
- use only GitHub-declared immutable group order/scope;
- after successful create-only publish of group N, immediately allow group N+1 without waiting for canonical ingest of N;
- local buffer publish is not canonical acceptance;
- stop on create/write failure;
- do not scan the buffer as a ChatGPT-owned recovery queue;
- on restart, reload canonical state;
- if the deterministic current expected artifact already exists while canonical progress has not advanced, do not overwrite, rename, alternate-retry, or skip it; leave GitHub drain to resolve it.

The live Scheduled Task was **not** edited. Repository prompt landing alone is explicitly not considered buffered live activation.

## Validation and synthetic evidence

PR validation workflow: `Validate buffered Steam review dossier runtime`.

All-green final validation on PR head `ebac7f25e5748700da48148193b8548aed579a40`:

- run `34925468923` — success.

The prior branch validation with the complete three-suite command also passed all tests:

- run `34925393191` — success;
- `test_taste_steam_review_dossier_daily_snapshot.py`: 7/7 passed;
- `test_taste_steam_review_dossier_buffered_submission.py`: 12/12 passed;
- `test_taste_steam_review_dossier_same_day_preservation.py`: 3/3 passed.

Total explicit dossier validation in that run: 22 tests passed.

Buffered test coverage includes:

- deterministic immutable group plan;
- exact 25-item `10/10/5` partition;
- group identity unchanged after progress;
- future buffered group before canonical advancement;
- contiguous 4,5,6,7 drain;
- gap 4,5,7;
- malformed group before a later valid group;
- wrong/stale snapshot;
- replay/idempotency;
- atomic multi-group drain;
- interruption/restart before apply/push;
- migration proof and group-boundary fail-closed behavior;
- 40 already-fresh synthetic dossiers not being recreated/re-ingested in new work scope;
- no Taste Semantic Producer ownership takeover;
- synthetic 25-item demonstration with three simultaneous buffer artifacts followed by one drain accepting all 25 in one contiguous prefix.

Same-day preservation tests additionally prove:

- legacy same-day progress is additively migrated without reset despite queue/store drift;
- an already-buffered same-day manifest is preserved exactly;
- the next daily boundary rebuilds from current queue/store state as intended.

The merge-triggered production pre-AI run independently reran the existing dossier suites and passed 7/7 daily-snapshot tests and 12/12 buffered tests while performing the real additive same-day migration.

## GitHub Actions caused by landing

Before merge, production `push.paths` were explicitly rechecked.

Merge commit `a9a393cbb2fd394dbc792c870d6e1571138bc369` automatically triggered exactly two push workflows observed for that head:

1. `Validate execution ownership`
   - run `34925559357`
   - conclusion: success
   - no canonical dossier mutation.

2. `Build pre-AI deterministic payload`
   - run `34925559470`
   - conclusion: success
   - this was an automatic landing consequence, not a manual dispatch;
   - it performed the additive same-day dossier group-plan migration described above;
   - it committed `aa57bcfab64cb0eafa6c38d23a8ef3769819e972` (`Refresh atomic pre-AI payload`);
   - the commit contained no `data/cache/taste_steam_review_dossiers/**` changes.

The dossier ingest workflow did **not** run from the merge because its push trigger is limited to dossier inbox JSON artifacts.

After the pre-AI chain, automated commercial visual output advanced `main` to `ab6b847359c4f873e86b83959c65a6522befd654`; comparison against `aa57bcf...` shows only `data/production/visual/current.json` changed. `Deploy visual mailing` run `34925637016` completed successfully. This chain did not alter the canonical dossier manifest or dossier cache.

No `workflow_dispatch` / `Run now` was invoked for production by this task.

## Safety-system note during implementation

The first earlier attempt to write the same-day preservation fix had been blocked by the OpenAI safety system. Under TPI-001, exactly one retry of the same `scripts/build_taste_steam_review_dossier_work.py` write, with the same path/branch/meaning/write method, was authorized. That exact retry succeeded (`bc49d022...`).

Later, an optional attempt to add the separate same-day regression file to the permanent pre-AI workflow test list was independently safety-blocked. It was **not retried or bypassed**. This did not block required validation: the PR validation workflow ran the same-day suite all-green, and the real merge-triggered pre-AI run itself proved same-day preservation in production state. The production workflow still runs the established daily-snapshot and buffered-submission dossier suites.

## What was not changed or run

- Live Scheduled Task UI: not edited.
- Production acceptance: not run.
- Manual workflow dispatch / `Run now`: not used.
- Taste Semantic Producer prompt: not changed.
- Taste Semantic Producer schedule: not changed.
- Taste Semantic Producer limits: not changed.
- Taste Semantic Producer queue/state ownership: not changed.
- `config/execution_ownership_contract.json`: not changed.
- Existing fresh dossier cache entries were not rewritten by landing migration.
- Old historical snapshot was not restored.
- Worker was not given authority to select dossier scope/order or mutate the canonical manifest.

## Remaining work for live activation

Implementation is landed and ready for director acceptance, but buffered live mode must remain considered inactive until the separate acceptance task:

1. update the **live Scheduled Task UI** to the accepted buffered worker prompt;
2. perform the separately authorized live acceptance/observation;
3. verify live create-only sequential publishing and GitHub drain behavior under the installed prompt;
4. only then declare buffered live mode activated.

No part of that live-activation sequence was performed in this IMPLEMENT task.

## Final status

`complete_ready_for_director_acceptance`
