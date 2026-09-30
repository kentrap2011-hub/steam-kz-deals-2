# Stale live statistics publication diagnostic 01

## 1. Task

READ-ONLY diagnostic for `kentrap2011-hub/steam-kz-deals-2`, source of truth `main`, executed under the current `CHAT_PROTOCOL.md` START gate and `WORKER_TASK_STALE_LIVE_STATISTICS_PUBLICATION_DIAGNOSTIC_01.md`.

Diagnostic source anchor before this report commit:

- `main`: `96c58e25f33d524fee9e9a942fd6de421e24e37c`
- no workflow was manually started;
- no redeploy was requested;
- no Service Worker, Scheduled Task, Dossier, Deep, source, workflow, or production file was changed;
- this report is the only repository mutation produced by the diagnostic.

Investigated publication chain:

`Dossier / Deep canonical truth -> Statistics / visual producer -> canonical visual payload -> web/data/current.json -> Pages deploy -> browser`.

## 2. User-visible evidence

The user-visible values under investigation were:

- Dossier last record: `30.09.2026 10:25`;
- Dossier counters: `60 / 200 / 6`;
- Deep last record: `30.09.2026 06:07`;
- Deep counters: `41 / 37 / 4 / 7 / 206 / 8 / 221`;
- top label: `Скидки: обновлено 24 сент., 03:12`.

These values are not invented by the browser. They are encoded in the current canonical visual blob on `main`:

- path: `data/production/visual/current.json`
- current blob SHA: `19925553e0fe9e090a012f982552e1bb8891b416`
- `generated_at_utc = 2026-09-30T06:26:28.370489+00:00`
- persisted by commit `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2` (`Refresh daily visual payload`) at `2026-09-30T06:26:31Z`.

The visual payload contains exactly:

- `dossier_last_write_at_utc = 2026-09-30T06:25:51+00:00`
- Dossier `60 accepted / 200 pending / 6 failed-or-recovery`
- `deep_last_write_at_utc = 2026-09-30T02:07:06+00:00`
- Deep `41 authoritative / 37 fit / 4 not-fit / 7 incomplete-or-recovery / 206 waiting-dossier / 8 ready-or-pending / 221 remaining-until-all-authoritative`.

With the +04 display context used by the observed page, these timestamps render as 10:25 and 06:07 respectively.

Therefore the stale statistics are already stale before browser rendering.

## 3. Current canonical Dossier truth

Current canonical Dossier source at the diagnostic anchor:

- `data/production/pre_ai/taste_steam_review_dossier_work.json`
- blob SHA: `c9ff345da7a1eb1180bdc3d7066f8625e5cff119`
- snapshot: `6f796bba9f36cf8090012b26b05bb350a315251f360a0e9c08453de5b6d8717a`
- eligible scope: `266`
- prepared-required scope: `209`
- accepted groups: `9`
- failed/recovery groups: `5`
- pending groups: `56`
- accepted dossiers in prepared-required scope: `27`
- failed/recovery dossiers in prepared-required scope: `15`
- pending dossiers in prepared-required scope: `167`.

The canonical statistics producer formula in `scripts/progressive_personalization.py::_dossier_processing_metrics()` gives:

- already-current accepted outside prepared-required scope: `266 - 209 = 57`;
- current accepted: `57 + 27 = 84`;
- current pending: `167`;
- current failed/recovery: `15`.

So a fresh current Dossier statistics projection is `84 / 167 / 15`, not the published `60 / 200 / 6`.

Latest durable Dossier group transition in the current snapshot:

- workflow: `Ingest Steam review dossier checkpoint`
- run: `36712221923`
- it accepted group sequence 14 and three dossiers;
- canonical commit: `ca28ec36d9be06376ed240750cdee49ba660c54f`
- commit time: `2026-09-30T12:02:25Z`.

That run advanced the current group state to `9 accepted / 5 failed / 56 pending` and dossier counts to `27 / 15 / 167`.

## 4. Current canonical Deep truth

Current canonical Deep projection at the diagnostic anchor:

- `data/production/pre_ai/progressive_pass2_work.json`
- blob SHA: `a4d34b42a950ed236fe4c844a9e4878994d2ccf5`
- semantic generation: `d21e7d0b38be9d16dbd931900610ff8603715150eec3d0e666f5c84a93e52408`
- total current coverage target: `266`
- first-pass attempted: `81`
- authoritative completed: `69`
- completed fit: `62`
- completed not-fit: `7`
- incomplete/recovery: `12`
- waiting for Dossier: `182`
- ready/pending: `3`
- normal first-pass remaining: `185`
- remaining until all authoritative: `197`.

Current canonical accepted Deep state:

- `data/cache/progressive_pass2_state.json`
- blob SHA: `f6ca84d43b162f5909242a431630424b68a3bcf4`
- latest accepted entries have `accepted_at_utc = 2026-09-30T12:12:50+00:00`
- examples at that timestamp: `game:2062430` and `game:1793250`, both `analyzed_fit`, `normal_first_pass`.

Therefore the current Deep last-record source is substantially newer than the published `2026-09-30T02:07:06Z`, and the current counters are substantially ahead of the published `41 / 37 / 4 / 7 / 206 / 8 / 221`.

## 5. Dossier last-record semantics

The Dossier UI “last record” is not the Dossier worker generation time and not merely the manifest `prepared_at_utc`.

`scripts/progressive_personalization.py` derives it from Git history for the current Dossier snapshot:

1. read historical versions of `taste_steam_review_dossier_work.json`;
2. retain versions belonging to the same current `snapshot_id`;
3. detect transitions of groups into durable classified states:
   - `accepted`, or
   - `failed_or_invalid_pending_recovery`;
4. use the Git commit timestamp of the latest such transition.

For the current snapshot, group 14 was newly accepted by commit `ca28ec36d9be06376ed240750cdee49ba660c54f` at `2026-09-30T12:02:25Z`.

The old published `2026-09-30T06:25:51Z` was therefore valid for the older source history captured by the 06:26 visual, but it is stale now.

## 6. Deep last-record semantics

The Deep UI “last record” is derived from canonical accepted Deep state, not from a reconciliation commit timestamp.

`scripts/progressive_personalization.py` normalizes each current Deep entry's `accepted_at_utc` and publishes the maximum timestamp among current-scope Deep entries as `deep_last_write_at_utc`.

At the diagnostic anchor the maximum canonical `accepted_at_utc` is:

`2026-09-30T12:12:50+00:00`.

This correctly distinguishes semantic acceptance from later mechanical reconciliation. The stale published value `2026-09-30T02:07:06Z` is the value embedded in the old visual payload, not a bad browser-side calculation.

## 7. Statistics count provenance

Canonical provenance is:

- Dossier:
  `taste_steam_review_dossier_work.json -> progressive_personalization.py::_dossier_processing_metrics() -> processing_status.dossier_* -> visual payload -> browser rendering`;
- Deep:
  current PASS2 work/state -> `progressive_personalization.py` state/progress projection -> `processing_status.deep_*` -> visual payload -> browser rendering.

The browser does not independently count Dossier/Deep files.

The visual producer can calculate newer state. In failed full-build runs it built newer candidates successfully before publication was aborted. Example latest full-build failure:

- Build daily visual payload run `36713360722` (#1094)
- build job `109881628838`
- producer reached:
  `visual progressive items=255 total=262 fit=58 incomplete=15 not_analyzed=182`.

Thus fresh upstream data reaches the producer. The first stale boundary is later.

## 8. Visual payload provenance

Current canonical visual is stale against multiple current material sources.

Current visual blob:
`19925553e0fe9e090a012f982552e1bb8891b416`.

Its bound material includes:

- Dossier work: `a40a70e9208004f71377c374adf07d6ea7147e5c`
  - current: `c9ff345da7a1eb1180bdc3d7066f8625e5cff119`;
- PASS2 state: `33c69cd9d22c1aadfd9b5a0aa595b1cb934216cc`
  - current: `f6ca84d43b162f5909242a431630424b68a3bcf4`;
- commercial/chatgpt payload: `d90e2747c1670269231a66896d39ac461b8dcfd0`
  - current: `13a225124ee0233329ed99ccddd750a7a88c1527`;
- store snapshot: `4322978e98914f1552f2b86cf3d9dbf1678d6d3b`
  - current: `4dc4efd6f8ed194bdc659d102a4434c9b8884f4b`;
- family graph: `1fef3c2480327639c0b3523bf7f3117f94f3135a`
  - current: `7520db09b6902467c2e34035535f570274a7113c`;
- history snapshot: `555871fb0b854b0fb41ca6c73b2fa105c2762bc6`
  - current: `dde196cd59344135441fa6013b8fd2d739efa997`;
- Russian description status: `c01d7c9afe6353e98e202f2684ed80c687f3854b`
  - current: `9b55bffb219d8d67c1d6c266ffe5b65e734a8f03`.

Routing detects this correctly. Example build run `36712315248` scope job:

`PROGRESSIVE_SCOPE source_integrity_ok=true compatible=false full_progressive_build_required=true reason=dossier_work_provenance_mismatch`

followed by:

`VISUAL_SCOPE full_progressive_build=true reason=progressive_visual_incompatible`.

Therefore freshness detection is not silently accepting the old payload.

### Exact publication failure

Last successful complete full visual build:

- run `36678188514` (#1007), started `2026-09-30T06:25:58Z`;
- build job `109767728233`;
- generated candidate: `visual progressive items=258 total=262 fit=37 incomplete=10 not_analyzed=211`;
- `CARD_EXPLANATION_VALIDATION=PASS`;
- `VISUAL_MATERIAL_BINDING=pass`;
- commit: `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2`;
- persisted visual blob: `19925553e0fe9e090a012f982552e1bb8891b416`;
- push succeeded at approximately `06:26:33Z`.

The first next observed complete build failure:

- run `36678293360` (#1012), started `2026-09-30T06:27:12Z`;
- build job `109768049452`;
- visual candidate generation succeeded;
- step `Validate generated card explanations` failed;
- examples:
  - `MY HERO ONE'S JUSTICE 2: positive lacks explicit personal-taste link`
  - `Orcs Must Die!: positive lacks explicit personal-taste link`
  - `Severed Steel: positive lacks explicit personal-taste link`
  - `Crown Trick: positive lacks explicit personal-taste link`
  - `Astalon: Tears of the Earth: positive lacks explicit personal-taste link`;
- `CARD_EXPLANATION_VALIDATION=FAIL count=8`.

Latest observed full-build failure:

- run `36713360722` (#1094)
- build job `109881628838`
- step 17 `Build and refresh canonical visual payload once`: success
- step 18 `Validate generated card explanations`: failure
- `CARD_EXPLANATION_VALIDATION=FAIL count=60`
- examples include `TrackMania² Stadium`, `Thymesia`, `Isonzo`, `Wingspan`, `Orcs Must Die!`, `Severed Steel`, `FINAL FANTASY V`, `Far Cry 3 - Blood Dragon`, and others;
- subsequent exact material binding, ranking export, and canonical commit/persistence steps were skipped.

The receipt later says:

`FRESHNESS_RECEIPT fresh_build=false scope=full_visual outcome=degraded/no_fresh_build reason=canonical_persistence_failed`.

For this run that receipt reason is secondary/fallback observability. The job-step evidence proves the earlier causal failure: card explanation validation failed before the persistence step was allowed to execute.

Current validator rule in `scripts/validate_card_explanations.py` requires every visible positive `why_fit` reason to contain the substring `теб`; otherwise it emits exactly `positive lacks explicit personal-taste link`.

## 9. Pages/deploy provenance

`web/data/current.json` is a deployment staging file, not a tracked canonical file in current `main`.

`.github/workflows/deploy-visual.yml` stages publication by:

`cp data/production/visual/current.json web/data/current.json`.

The latest successful Pages deploy found in the diagnostic window is:

- workflow: `Deploy visual mailing`
- run `36679517410` (#1087)
- created `2026-09-30T06:41:09Z`
- deploy job `109771692537`
- detected visual commit:
  `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2`
- explicitly copied:
  `data/production/visual/current.json -> web/data/current.json`
- uploaded Pages artifact ID: `11081251996`
- deployed Pages build version:
  `43a95562cca0431eb25d785e91e1c1068356bb7c`
- evaluated environment URL:
  `https://kentrap2011-hub.github.io/steam-kz-deals-2/`.

That deploy therefore staged the same old canonical visual payload, not a fresh Dossier/Deep projection.

Later `Deploy visual mailing` workflow_run invocations corresponding to failed/cancelled builds were skipped rather than publishing a newer visual.

This proves Pages is downstream of the already-stale canonical visual. Pages is not the first stale boundary.

## 10. Browser/service-worker provenance, if relevant

Browser cache is not needed to explain the defect and is not the first stale boundary.

Current browser code reads the deployed artifact with explicit no-cache requests:

- `web/app.js`:
  `fetch(DATA_URL, {cache:'no-store'})`
- `web/paid-freshness-ui.js`:
  `fetch('data/current.json', { cache: 'no-store' })`.

The observed Dossier/Deep numbers exactly equal the canonical visual values and the Pages deploy copied that canonical file into the artifact.

No current `web/sw.js` or `web/service-worker.js` exists at those canonical paths. No Service Worker change is required for this diagnosis.

Therefore attributing the stale statistics to browser cache would be incorrect.

### Top `Скидки: обновлено 24 сент., 03:12` semantics

This label is a separate semantic timestamp, not the visual-build timestamp.

`web/paid-freshness-ui.js` renders:

`paid_list_freshness.source_mailing_updated_at_utc`

as `Скидки: обновлено ...`.

The current stale visual contains:

`source_mailing_updated_at_utc = 2026-09-23T23:12:47.031485+00:00`

which is 24 September 03:12 in +04 display time.

Importantly, the current upstream `data/production/pre_ai/chatgpt_payload.json` still has the same `source_mailing_updated_at_utc = 2026-09-23T23:12:47.031485+00:00`.

So this top label is not, by itself, proof that the current store observation or visual publication is from September 24. It is the mailing-source update timestamp. The wording can be misleading as an apparent “site freshness” indicator, but that is separate from the Dossier/Deep publication defect diagnosed here.

## 11. First stale boundary

**First proven stale boundary: after fresh visual candidate generation, at the `Validate generated card explanations` gate, before canonical visual persistence.**

Fresh Dossier/Deep truth reaches:

1. GitHub canonical state: yes;
2. progressive routing/freshness detection: yes;
3. full visual rebuild selection: yes;
4. fresh visual candidate generation: yes;
5. card explanation validation: **fails**;
6. canonical `data/production/visual/current.json` replacement: no;
7. Pages staging of fresh payload: no;
8. browser receipt of fresh payload: impossible because the fresh payload never became canonical.

## 12. Root cause

The current live statistics are stale because full visual publication is fail-closed by a **card-explanation producer/validator incompatibility**.

The generated current visual candidate contains positive `why_fit` texts that do not satisfy the current validator's literal personal-link rule. `scripts/validate_card_explanations.py` requires the reason text to include `теб`; current generated Deep-derived positive explanations can reach the candidate without that literal, producing repeated:

`positive lacks explicit personal-taste link`.

The failure aborts the workflow before exact material binding validation and before the canonical visual commit. Consequently the last successfully persisted visual remains the 06:26 payload and all later canonical Dossier/Deep progress stays upstream.

This is not a browser-cache root cause and not a failure of Dossier/Deep ingestion.

The number of violations grew from 8 in the first observed post-06:26 failing full build to 60 in the latest observed full build, so repeated semantic progress increases the amount of incompatible generated card text while publication remains blocked.

## 13. Scope of stale publication

The stale boundary affects more than the Statistics tab.

Proven stale or potentially stale relative to current canonical sources:

- Dossier counts and last-record time;
- Deep counts and last-record time;
- Deep-derived personalized card content;
- ranking/order or card fields that depend on current Deep state;
- current commercial/store material, because the current store/payload/family/history blobs no longer match the bound visual blobs;
- Russian-description publication observability, because the current translation-status blob is newer than the visual-bound blob.

Commercial/expiry nuance:

- current browser code filters existing payload rows by known `sale_ends_at_utc` at render time, so a known expired timestamp can disappear without a new visual build;
- however current store snapshot blob `4dc4efd...` is newer than visual-bound store blob `4322978...`, so commercial changes that require new canonical store data cannot be assumed to be represented by the stale visual.

Top `Скидки: обновлено 24 сент., 03:12` is not the visual age. It is specifically the mailing-source timestamp and currently remains the same in the fresh upstream commercial payload.

## 14. Relation to prior stale-snapshot fix

PR #126:

- title: `Fix full visual stale-snapshot persistence race`
- merged: `2026-09-29T16:19:11Z`
- merge commit: `f57d5b922ee333759c951de38686eb448a8c10fd`.

PR #126 added exact material binding, one rebuild after material drift, and fail-closed behavior on repeated material drift.

The present defect does **not** prove that PR #126 was bypassed or regressed.

Evidence:

- the last successful full build #1007 executed `VISUAL_MATERIAL_BINDING=pass` and persisted through the PR #126 guard path;
- the current failed full builds stop earlier at card explanation validation;
- in latest run #1094 the later `Validate exact full visual material binding` and canonical commit/persistence steps are skipped because step 18 already failed.

Therefore the current root cause is a different gate that precedes the stale-snapshot persistence protection.

PR #128:

- title: `Align Deep score evidence with card explanations`
- merged: `2026-09-30T06:08:06Z`
- merge commit: `d6221868a5e78b9852a0720319de036f76e6ec68`.

The 06:26 full visual built successfully after PR #128 was merged. The first observed failure appears after subsequent Deep score-explainability migration/state updates. This establishes a temporal association with newly accepted/generated explanation content, but not enough evidence to claim that the PR #128 merge alone is the root cause. The directly proven defect is producer/validator parity for the newly generated positive explanation text.

## 15. Exact evidence / commits / runs / artifacts

Canonical/source SHAs at diagnostic anchor:

- diagnostic `main`: `96c58e25f33d524fee9e9a942fd6de421e24e37c`
- current visual blob: `19925553e0fe9e090a012f982552e1bb8891b416`
- visual commit: `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2`
- current Dossier work blob: `c9ff345da7a1eb1180bdc3d7066f8625e5cff119`
- current Deep work blob: `a4d34b42a950ed236fe4c844a9e4878994d2ccf5`
- current Deep state blob: `f6ca84d43b162f5909242a431630424b68a3bcf4`
- current store snapshot blob: `4dc4efd6f8ed194bdc659d102a4434c9b8884f4b`
- current family graph blob: `7520db09b6902467c2e34035535f570274a7113c`
- current history snapshot blob: `dde196cd59344135441fa6013b8fd2d739efa997`
- current chatgpt payload blob: `13a225124ee0233329ed99ccddd750a7a88c1527`
- current Russian-description status blob: `9b55bffb219d8d67c1d6c266ffe5b65e734a8f03`.

Dossier evidence:

- ingest run `36712221923`
- group 14 accepted
- canonical commit `ca28ec36d9be06376ed240750cdee49ba660c54f`
- commit time `2026-09-30T12:02:25Z`.

Last successful full visual:

- build run `36678188514` (#1007)
- build job `109767728233`
- commit `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2`
- `CARD_EXPLANATION_VALIDATION=PASS`
- `VISUAL_MATERIAL_BINDING=pass`.

First observed failing full visual after that:

- build run `36678293360` (#1012)
- build job `109768049452`
- `CARD_EXPLANATION_VALIDATION=FAIL count=8`.

Latest observed failing full visual:

- build run `36713360722` (#1094)
- build job `109881628838`
- fresh candidate generated;
- `CARD_EXPLANATION_VALIDATION=FAIL count=60`;
- canonical commit/persistence step skipped.

Representative no-build/degraded routing evidence:

- build run `36712315248` (#1070)
- routing detects `dossier_work_provenance_mismatch`;
- actual build job skipped because prerequisite not ready;
- receipt:
  `degraded/no_fresh_build reason=upstream_prerequisite_not_ready`.

Pages evidence:

- last successful deploy found: `36679517410` (#1087)
- deploy job: `109771692537`
- visual commit used: `2aca7915028057a9e8a7f0126c2d9d3d1744f7a2`
- Pages artifact ID: `11081251996`
- Pages build version: `43a95562cca0431eb25d785e91e1c1068356bb7c`
- deployed URL: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`.

Relevant merged PRs:

- PR #126 merge: `f57d5b922ee333759c951de38686eb448a8c10fd`
- PR #128 merge: `d6221868a5e78b9852a0720319de036f76e6ec68`.

## 16. Recommended fix

Do not fix this by forcing a workflow run, manually redeploying, weakening freshness checks, changing browser cache behavior, or bypassing the card explanation gate.

Create a bounded implementation task for **card-explanation producer/validator parity in full visual publication**.

The implementation should make the canonical producer and validator agree on the required representation of an explicit personal-taste link for Deep-derived positive explanations, while preserving the exact Deep score-finding provenance and existing fail-closed validation intent.

Acceptance should include regression coverage from the first failing post-06:26 result shape and prove that, with current canonical Dossier/Deep state:

1. full visual candidate builds;
2. generated card explanation validation passes;
3. exact material binding passes;
4. the canonical visual is persisted with current source blob bindings;
5. normal downstream deploy stages that new visual into `web/data/current.json`;
6. Pages publication receives that current payload without a manual redeploy.

The implementation task should not transfer retry/scheduling ownership to the browser and should not add a new recurring loop.

## 17. Status

`diagnosed_needs_fix`

## 18. Recommended next step

Exactly one bounded next action:

**Assign one developer worker to fix and regression-test the card-explanation producer/validator parity that currently blocks full visual publication, without manually triggering deployment or changing Dossier/Deep/Scheduled Tasks.**
