# Taste Dossier Live Compact Acceptance 01

- Task ID: `taste-dossier-live-compact-acceptance-01`
- Mode: `ACCEPTANCE`
- Date: `2026-09-15`
- Verdict: **rejected**
- Authorized Scheduled Task invocations used by this acceptance: **1**
- Manual GitHub workflow dispatches: **0**
- Runtime/config/code changes: **0**
- Taste Semantic Producer changes: **0**

## Architecture preflight

The pre-run architecture gate was safe.

The current repository contract, persistence bridge, and repository worker prompt all agreed that the active live worker read surface is the GitHub-generated compact projection:

- index: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- immutable descriptors: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/{snapshot_id}/g{sequence:06d}.json`
- buffered transport: immutable create-only files under `data/ai_inbox/taste_steam_review_dossiers/`
- GitHub remains the only owner of canonical validation, contiguous drain, persistence, cleanup, canonical progress, retry/gap/replay interpretation, and completeness.

The active contract explicitly permits local traversal from group N to group N+1 after successful create-only publication of N without waiting for canonical ingest/acceptance of N, while requiring the tiny compact index to be reread only as a snapshot/plan liveness guard.

The deterministic buffered artifacts for canonical expected groups 1 and 2 were absent before the run, so there was no unresolved existing-artifact conflict preventing a safe start.

## Exact pre-run baseline

Captured before the user was asked to run the Scheduled Task:

- repository: `kentrap2011-hub/steam-kz-deals-2`
- `main` HEAD: `a3329f4a31cedf2b587d5f10b9b4b856d33c62d7`
- HEAD message: `director: add live compact dossier acceptance task`
- canonical work manifest: `data/production/pre_ai/taste_steam_review_dossier_work.json`
- canonical manifest blob SHA: `751ba6dce7b5340885398e4500ac4f1cf5c4f1ed`
- snapshot ID: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- prepared required count: `594`
- completed required count: `0`
- remaining required count: `594`
- prepared required SHA-256: `c519c99b165b11f2d64313849517753ca70dbd25ee7910206fd58dd9d929cbd3`
- source queue SHA-256: `116687b59c35629b2f6e74b79fe0c1f467aac605994ddddd5fc84874a339df0d`
- group plan SHA-256: `513a495c947a21b1b7e1958569c76ef67c7dbe76808b0df95ef21be3129676de`
- immutable group count: `60`
- compact worker index path: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- compact worker index blob SHA: `ebd6d9086a77b2b1e51fd129510867dab96d4d45`
- compact worker index `canonical_expected_sequence`: `1`

Latest relevant pre-run canonical-work commit observed for the manifest was `aa57bcfab64cb0eafa6c38d23a8ef3769819e972` (`Refresh atomic pre-AI payload`, `2026-09-15T03:35:51Z`). The most recent previously observed successful dossier ingest workflow was run `34839554711` on commit `f56786cebf346b23b85f0fdb97501bd74f3c79af` from the prior day.

## Compact descriptors N and N+1

Canonical expected sequence N was `1`.

### Descriptor N = 1

- path: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3/g000001.json`
- Git blob SHA: `b4ea1856da717bad674199f116e967d5bccbfca3`
- sequence: `1`
- range: `[0,10)`
- items SHA-256: `0ee433d4124187a4476e29d4722bda90e680e670bcbe67152ec36e349e598b3d`
- group SHA-256: `74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06`
- appids in exact order: `2378500, 1000360, 1003590, 1003890, 1025440, 1034860, 1047010, 1062040, 1071870, 107310`
- deterministic artifact: `data/ai_inbox/taste_steam_review_dossiers/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3--g000001--74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06.json`

### Descriptor N+1 = 2

- path: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3/g000002.json`
- Git blob SHA: `3a4168481f698a9ed56cdcbe967be9662797236d`
- sequence: `2`
- range: `[10,20)`
- items SHA-256: `02ff44bad19a5773b6aa9f5af154879d7b4bc07216b2042aa302e462e971ee1f`
- group SHA-256: `f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a`
- appids in exact order: `1077970, 1079800, 1082710, 1083790, 1104380, 1143810, 1147560, 1152300, 1152310, 1157390`
- deterministic artifact: `data/ai_inbox/taste_steam_review_dossiers/c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3--g000002--f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a.json`

Both descriptors matched the index snapshot, prepared hash, group-plan hash, source binding, group count, and canonical plan.

## User manual-run confirmation

After the safe preflight, the user manually pressed `Run now` exactly once on the existing `Taste Steam Review Dossier` Scheduled Task and replied `Запустил` in the acceptance chat.

No second `Run now` was requested or performed by this acceptance.

## Live compact-read / same-invocation evidence

The compact multi-group behavior itself was proven.

The live invocation reported that it used the compact index and descriptors, rereading the compact index as a liveness guard before moving to group 2 and again before beginning group 3. During those rereads the snapshot/plan bindings remained unchanged and `canonical_expected_sequence` remained `1`, which is explicitly permitted by the compact worker contract while local traversal proceeds sequentially after successful create-only publication.

Durable GitHub ordering corroborates the same behavior:

1. Group 1 publication commit: `a7e2eef48ab8766630211cb8acf1a217bdab06ba`, timestamp `2026-09-15T11:24:18Z`, message `Publish Steam review dossier buffered group 1`.
2. Group 2 publication commit: `60d0c0b76ec25e9a9e926f62c9b26ab10dc4e8ac`, timestamp `2026-09-15T11:25:07Z`, message `Publish Steam review dossier buffered group 2`.
3. Group 1 commit's parent is exactly the captured pre-run baseline `a3329f4a31cedf2b587d5f10b9b4b856d33c62d7`.
4. Group 2 commit's parent is exactly group 1 publication commit `a7e2eef48ab8766630211cb8acf1a217bdab06ba`.
5. Therefore there is no canonical ingest/progress commit between publication of group 1 and publication of group 2.
6. The first group-1 GitHub ingest run had already failed without canonical commit before group 2 was published.
7. Dossiers in both published groups use the same `generated_at_utc` value `2026-09-15T11:22:00+00:00`, consistent with one live evidence-preparation invocation.

The live invocation then began descriptor sequence 3 after another compact-index liveness reread, but stopped evidence work before publishing group 3 because the available Steam/web surface did not provide sufficient store evidence for all ten planned items. No group-3 artifact was published.

This proves the requested behavior that N+1 traversal/publication did not wait for canonical acceptance of N. It also proves the live worker was no longer blocked by reconstruction of the oversized full manifest.

## Published artifact identity and ordering

Transport identity/order for the two published groups is correct:

- group 1 used the exact deterministic path and exact immutable descriptor identity for sequence 1;
- group 2 used the exact deterministic path and exact immutable descriptor identity for sequence 2;
- group 2 directly follows group 1 in Git history;
- no alternate retry filename was created;
- no duplicate group-1 or group-2 transport artifact was observed;
- no sequence was skipped or reordered;
- snapshot/prepared/source/group identities match the current canonical compact projection.

A compare from baseline `a3329f4a...` to post-publication `60d0c0b...` contains exactly two added files: the deterministic group-1 and group-2 buffered artifacts. No code, config, canonical manifest, worker index, descriptor, dossier store, or Taste Semantic Producer path changed in those two commits.

## GitHub Actions drain outcomes

### Run 9 — group 1 wake-up

- workflow: `Ingest Steam review dossier checkpoint`
- run ID: `34963101572`
- head SHA: `a7e2eef48ab8766630211cb8acf1a217bdab06ba`
- created: `2026-09-15T11:24:21Z`
- job ID: `104361110881`
- conclusion: `failure`
- failing step: `Drain maximal valid contiguous dossier prefix from current repository state`
- exact logged result: `TASTE_STEAM_REVIEW_DOSSIER_INBOX_INVALID: buffered drain blocked at sequence 1: invalid_expected_group`
- canonical commit step: skipped

### Run 10 — group 2 wake-up

- workflow: `Ingest Steam review dossier checkpoint`
- run ID: `34963178057`
- head SHA: `60d0c0b76ec25e9a9e926f62c9b26ab10dc4e8ac`
- created: `2026-09-15T11:25:10Z`
- job ID: `104361353235`
- conclusion: `failure`
- failing step: `Drain maximal valid contiguous dossier prefix from current repository state`
- exact logged result: `TASTE_STEAM_REVIEW_DOSSIER_INBOX_INVALID: buffered drain blocked at sequence 1: invalid_expected_group`
- canonical commit step: skipped

The second wake-up correctly rederived repository state and remained blocked at the same canonical expected sequence rather than skipping to group 2.

## Exact validation defect

The GitHub drain failure is not an ordering race and not a compact-projection defect. It is a contract-invalid dossier payload in expected group 1.

The first dossier in group 1, appid `2378500`, contains this observation category:

- `category: "content"`

The canonical runtime dossier validator defines the allowed observation categories as:

- `mechanics`
- `structure`
- `pacing`
- `progression`
- `repetition`
- `difficulty`
- `friction`
- `multiplayer`
- `coop`
- `localization`
- `translation`
- `voice`
- `font`
- `encoding`
- `regional`
- `other`

`content` is not allowed. `validate_buffer_artifact()` validates every dossier through the canonical `validate_dossier()` path, so group 1 is correctly classified by GitHub as `invalid_expected_group` and the contiguous drain fails closed at sequence 1.

Because the expected group is invalid, GitHub correctly does not inspect group 2 as an independently acceptable canonical unit, does not skip sequence 1, and does not advance progress.

## Canonical before/after state

Before the run:

- prepared: `594`
- completed: `0`
- remaining: `594`
- expected sequence: `1`
- index blob SHA: `ebd6d9086a77b2b1e51fd129510867dab96d4d45`

After both publication commits and both failed drain runs:

- prepared: `594`
- completed: `0`
- remaining: `594`
- expected sequence: `1`
- compact worker index blob SHA: `ebd6d9086a77b2b1e51fd129510867dab96d4d45`
- canonical snapshot remains `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`

Canonical progress advanced by exactly `0`, which is correct for an invalid expected group but fails this acceptance's required canonical-acceptance criterion.

## Compact index and descriptor after-state

The compact worker index is byte-identical to the pre-run index and still points to canonical expected sequence `1`.

Same-snapshot descriptor files were not mutated. The baseline-to-post-publication compare contains only the two buffer files, and the current sequence-1 descriptor still carries the original immutable bindings and group identity.

Thus compact projection immutability behaved correctly; it did not falsely claim progress after failed canonical validation.

## Accepted-buffer cleanup state

No buffered group was canonically accepted, so no accepted-buffer cleanup occurred.

Both deterministic buffered artifacts remain in the inbox. This is consistent with fail-closed behavior: GitHub did not delete invalid/unaccepted transport artifacts and the worker did not overwrite, rename, delete, or invent retry files.

## Duplicate / reorder / scope-drift assessment

- duplicate transport publication: **not observed**
- alternate retry filename: **not observed**
- sequence reorder: **not observed**
- sequence skip: **not observed**
- snapshot drift: **not observed**
- prepared/group-plan/source binding drift: **not observed**
- direct canonical mutation by worker: **not observed**
- direct worker-index/descriptor mutation by worker: **not observed**
- semantic dossier validity: **failed in group 1** because of unsupported observation category `content`

Therefore transport identity/order/scope behavior was correct, but the expected group's dossier content was invalid under the canonical validator.

## Taste Semantic Producer unchanged

Confirmed unchanged for this acceptance.

The baseline-to-post-publication compare includes only the two buffered transport files. No Taste Semantic Producer, Taste pin, Taste ingest authority, runtime, config, workflow, script, or code path was changed by the live invocation or by this acceptance observer before this report.

## PASS criteria assessment

1. Compact worker index used instead of full-manifest reconstruction: **proven**.
2. Exact immutable descriptor N published to deterministic create-only path: **proven**.
3. Worker proceeded to N+1 without waiting for canonical acceptance of N: **proven**.
4. N+1 deterministic artifact published in same invocation: **proven**.
5. Descriptor/group identities/order match compact projection/canonical plan: **proven**.
6. GitHub accepts correct maximal contiguous valid prefix: **not satisfied**; expected group 1 is invalid and drain correctly rejects it.
7. Canonical progress advances by exact accepted count without skip/reorder/duplicate: accepted count is zero and progress correctly remains zero, but the required successful advancement is **not satisfied**.
8. Accepted buffered artifacts cleaned up: **not exercised**, because nothing was accepted.
9. Compact index advances consistently with canonical progress and descriptors remain immutable: descriptors remain immutable; index correctly does not advance because canonical progress did not advance.
10. Taste Semantic Producer unchanged: **proven**.

## Final verdict

**rejected**

The main compact-read objective was successfully demonstrated: one and only one user-triggered Scheduled Task invocation published at least two consecutive deterministic buffered groups, and durable commit ordering plus the live trace prove group 2 traversal/publication did not wait for canonical acceptance of group 1. The worker also began descriptor 3 through the same compact traversal path before stopping without publishing it.

However, this task's PASS criteria also require GitHub to accept the correct contiguous prefix and advance canonical progress. That did not happen. Group 1 contains a contract-invalid dossier observation category (`content`), both GitHub drain attempts correctly failed closed with `invalid_expected_group` at sequence 1, canonical progress remained `594 / 0 / 594` with expected sequence 1, and both unaccepted transport artifacts remain in the inbox.

### Explicit same-invocation compact-read statement

**YES — multi-group same-invocation compact-read traversal/publication was proven.**

**NO — end-to-end acceptance was not achieved because the canonical validator correctly rejected group 1, so the overall task verdict is `rejected`.**

No second Scheduled Task run is authorized or required by this report. Stop here.