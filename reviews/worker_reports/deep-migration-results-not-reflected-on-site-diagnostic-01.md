# Deep migration results not reflected on site diagnostic 01

## Task

- Task ID: `deep-migration-results-not-reflected-on-site-diagnostic-01`
- Task file: `WORKER_TASK_DEEP_MIGRATION_RESULTS_NOT_REFLECTED_ON_SITE_DIAGNOSTIC_01.md`
- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2@main`
- Mode: `READ-ONLY / RECON`
- No Deep/Fast/Dossier worker was run.
- No migration, visual state, Scheduled Task, or ЧАТ 1 state was changed.
- The only repository change made by this diagnostic is this durable report.

## Pinned current truth

The diagnosis was completed against current `main` after the parallel ЧАТ 1 merge:

- current `main`: `ebaa18ff406fb9c1744ed559990043570080b7b2`
- that commit is PR #111, `Fix Dossier Deep release-year identity compatibility (#111)`
- PASS 2 state blob: `f4eda46acbece7056df60a18f66f35b6920c5935`
- PASS 2 work blob: `367985f449a663805a596975ac9be4164e865444`
- current visual blob: `fbbf9a37faf7d1479ca030c3a80c0fc49fea8e51`
- current `taste_projection.json` blob: `1e873ecc5ee5d7b17d29b66a429588b8e8f40d5e`

ЧАТ 1 merged while this read-only diagnostic was in progress, but the PASS 2 state blob, PASS 2 work blob, and visual blob remained byte-identical to the already inspected pre-merge values. The diagnosis therefore remains pinned and unchanged by that merge.

## Canonical Deep state

### Durable PASS 2 state

`data/cache/progressive_pass2_state.json` contains 55 durable entries.

Raw durable completed Deep entries, without current-identity filtering:

- authoritative completed: **32**
- `analyzed_fit`: **26**
- `analyzed_not_fit`: **6**

Of those, the PPD-010 legacy full reanalysis migration contributes exactly:

- migration targets: **30**
- accepted: **30**
- accepted completed: **30**
- `analyzed_fit`: **26**
- `analyzed_not_fit`: **4**
- incomplete: **0**
- confirmed-risk results: **23**
- caution results: **7**
- migration last accepted: **2026-09-28T10:36:02+00:00**
- migration complete: **true**

The other two raw authoritative completions belong to older non-migration Deep identities.

### Current exact-bound Deep scope

`data/production/pre_ai/progressive_pass2_work.json` projects the current exact-bound Deep scope as:

- total current coverage target: **399**
- first-pass attempted: **0**
- authoritative completed: **0**
- fit: **0**
- not-fit: **0**
- incomplete/recovery: **0**
- waiting for Dossier: **361**
- ready/pending: **38**
- remaining until all authoritative: **399**
- current Deep last write: **null**
- migration paused flag: **false**
- migration observability still reports **30/30 complete**

All **30/30** migrated families are present again among the current **38** `normal_first_pass` work items. Therefore the migration results are durable, but none is current for the present semantic identity.

## Published site state

The latest successful Pages deployment inspected was:

- build run: **36410679154**, `Build daily visual payload`
- build head before its visual commit: `628179fcf90367d0a79701fd13e98a0e511b864f`
- visual commit produced/deployed: `e6c9cbf925bcb45f54d1c62bf42a05c953623e79`
- Pages deploy run: **36410747696**
- deploy conclusion: **success**
- Pages artifact ID: **10964217340**
- Pages artifact digest: `sha256:bfefef795b78830dd3664251942a6a6d981f4e8bc9b741ade9bedd8f02266319`
- extracted deployed `web/data/current.json` SHA-256: `a61980e9eb6de825afe89d1afba06bfdf03f97156bf170131dd9d6c195eb1e4d`

The deployed artifact itself contains:

- Deep completed: **0**
- fit: **0**
- not-fit: **0**
- incomplete/recovery: **0**
- waiting for Dossier: **361**
- ready/pending: **38**
- remaining: **399**
- Deep last write: **null**
- effective result counts: `deep=0, fast=0, none=399`

The same deployed payload also contains the separate migration observability object showing **30/30 accepted completed**, last accepted **2026-09-28T10:36:02+00:00**.

The deployed payload records the exact current PASS 2 state blob `f4eda46acbece7056df60a18f66f35b6920c5935`. Therefore the user's screenshot is consistent with the current deployed data, not an older Pages state.

The deploy freshness classification was `degraded/no_fresh_build` with reason `deterministic_refresh_preserved_semantic_history`, but the deploy still staged the current canonical `data/production/visual/current.json` into `web/data/current.json`, uploaded artifact 10964217340, and deployed it successfully. This classification is not the source of the zeros.

## First divergence point

The first divergence is **before Statistics, visual generation, Pages, and browser rendering**.

It occurs at:

**durable migration PASS 2 state -> current exact-bound Deep selection**

The migration manifest is frozen to:

- semantic generation: `4596b03979956f78c308551a75fdbe9f432ed3f80925c29b0835bdb052222033`
- profile pin: `cb64c290e037aade65d4269ae2ebe54b681367cad899d7dd9c9838603370f358`
- profile resolved commit: `feb5e74d5d3d95000612ee2888926618001e6424`
- profile blob: `9b9926031889dbd98ba6585c57836d52c739a0bb`
- profile content SHA-256: `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`

Current Progressive identity is:

- semantic generation: `f76f0ed6b470b58f0eaf7a72a9bb0e18d3ed8a6b41a1956a1ff1229776b09e92`
- profile pin: `6a91b6840ccea5729af09475b71d174ab10047e324f27a65e3fab43a4c83e3f4`
- profile resolved commit: `09f4901ff0eef5b6fda15f32ff43d53907df7072`
- profile blob: **the same** `9b9926031889dbd98ba6585c57836d52c739a0bb`
- profile content SHA-256: **the same** `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`

The other semantic-generation inputs are also unchanged:

- `taste_model_version = taste-v3`
- `taste_semantics_sha256 = 0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- `candidate_context_contract_blob_sha = 077dd7cf1f1c300f5029a34be87f056d25d01804`
- profile blob SHA is unchanged

The only semantic-generation material that changed is `profile_pin_sha256`, and the profile pin changed because its immutable `resolved_commit_sha` changed even though the profile file blob/content did not.

The repository history proves the transition:

- `5379362a691657fc9cb05844841ab14016c3b93e` had profile commit `feb5e74...`, blob `9b992...`
- `99120f8c7ae8f14c434eac70b96ff5105a9d2aab` at **2026-09-28T09:53:14Z** refreshed the atomic pre-AI payload to profile commit `09f490...`, while retaining the same profile blob/content
- the migration authority was frozen earlier at `97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a`, **2026-09-28T04:01:33Z**
- migration result acceptance occurred afterward, through **10:36:02Z**

For all 30 migrated families:

- AppID still matches current work
- taste subject still matches current work
- taste fingerprint still matches current work
- candidate-context SHA still matches current work
- semantic generation differs
- profile pin differs
- derived work ID differs

Thus there is no game/content identity drift in those 30 items. They fail current Deep selection because the global semantic/profile pin changed.

`scripts/progressive_pass2.py::matching_state_entry()` requires exact equality for the Progressive identity fields. `scripts/progressive_personalization.py` uses that exact-matching Deep entry for effective Deep selection, cards, stage counters, and `deep_last_write_at_utc`. Once the migrated revision no longer matches the current binding, it is intentionally excluded from all of those current-stage surfaces.

## Why the screenshot shows zeros

The screenshot shows zeros because the current site is reporting **current exact-bound Deep coverage for semantic generation `f76f...`**, not raw historical/durable Deep completions.

The 30 migration completions are still visible in the separate migration observability block, but they belong to frozen generation `4596...`.

Therefore:

1. PASS 2 state correctly retains 30 completed migration revisions.
2. current binding rejects them as non-current.
3. current Deep projection becomes 0 completed / 38 ready.
4. Statistics correctly copies those current-stage values.
5. visual payload correctly copies those values.
6. Pages artifact contains those values.
7. browser displays those values.

There is no Statistics-only, Pages-only, browser-only, or service-worker-first divergence.

## Migration-vs-normal-counter semantics

PPD-010 deliberately separates migration accounting from normal first-pass/recovery accounting. Therefore migration acceptance does **not** imply that `deep_first_pass_attempted_count` must increment.

However PPD-010 also states that a successfully accepted completed migration revision becomes the current authoritative Deep revision for its exact identity, while the old revision is archived. The global Progressive contract separately requires presentation and authority to bind to the **current** semantic generation/work identity.

Those rules are consistent here:

- the 30 migration results are authoritative completed revisions for their frozen exact identities;
- they would be normal current Deep authority only while those identities remain current;
- the later semantic-generation change makes them non-current;
- therefore `deep_authoritative_completed_count=0` and `deep_last_write_at_utc=null` are contract-consistent for the present generation.

So the site's zero normal Deep counters are **not themselves a counter/projection defect**.

The defect exposed by this task is earlier: a provenance-only profile pin change created a new semantic generation even though the actual profile blob and content SHA were unchanged. That made all 30 newly completed migration results immediately stale for current presentation and caused all 30 to be emitted again as ordinary current Deep work.

## Cards/ranking impact

This is broader than the Statistics page.

The exact deployed Pages artifact shows that **all 30 migrated games** currently have:

- `analysis_state = not_analyzed`
- no `progressive_pass2` semantic source
- no current Deep fit
- no current migration negative-assessment/risk projection

Three inspected examples were:

- `Potion Craft: Alchemist Simulator` — `not_analyzed`
- `Despot's Game: Dystopian Battle Simulator` — `not_analyzed`
- `FAITH: The Unholy Trinity` — `not_analyzed`

All four migration `analyzed_not_fit` results are also still present as ordinary unresolved cards:

- `Lifeless Moon` — current card `not_analyzed`, priority rank 228
- `The Complex` — current card `not_analyzed`, priority rank 232
- `小白兔电商~Bunny e-Shop` — current card `not_analyzed`, priority rank 373
- `Tiny Snow` — current card `not_analyzed`, priority rank 384

Therefore:

- cards are **not** using the migrated current-revision semantics;
- the issue is **not** Statistics-only;
- the 23 confirmed-risk and 7 caution migration assessments do not currently feed card risk presentation;
- they also do not feed current personalized score/ranking;
- four migration not-fit outcomes do not currently suppress those games from the unresolved visible catalogue.

Current `effective_result_counts` is `deep=0, fast=0, none=399`.

Further ordinary Deep execution, if/when run by its existing Scheduled Task, would not continue from those 30 migration results as current completions. All 30 are already re-emitted as new-generation `normal_first_pass` items inside the current 38-item Deep work projection, so they would be analyzed again under semantic generation `f76f...`.

That behavior is mechanically correct for the current exact-identity contract, but redundant because the repository proves the profile bytes and all 30 item fingerprints/context hashes are unchanged.

## Interaction with ЧАТ 1

During this diagnostic, ЧАТ 1's PR #111 merged into `main` as:

- `ebaa18ff406fb9c1744ed559990043570080b7b2`
- `Fix Dossier Deep release-year identity compatibility (#111)`

This diagnostic did not modify or rerun that work.

The merge changed the release-year identity compatibility contract/code/tests, but it did **not** change:

- PASS 2 state blob `f4eda46...`
- PASS 2 work blob `367985...`
- visual blob `fbbf9a...`

Therefore PR #111 is separate from the migration/site divergence proven here. A later normal recomputation may change Dossier-ready counts under the repaired release-year compatibility rule, but it cannot make the 30 frozen-generation migration revisions match current semantic generation `f76f...`.

## Changes

Report only:

- created `reviews/worker_reports/deep-migration-results-not-reflected-on-site-diagnostic-01.md`

No product/source/runtime state was changed.

## Unresolved

Within the repository scope, the first divergence and user-facing consequences are fully proven.

One provenance detail intentionally remains outside this task: why the external profile repository's resolved commit advanced from `feb5e74...` to `09f490...` while `gaming_taste_live.json` retained the exact same blob/content. Repository-local evidence is already sufficient to prove that this commit-only pin change caused the semantic-generation reset; inspecting another repository would violate this task's repository scope.

No cache clearing or browser mutation was performed. It is unnecessary for root-cause identification because the downloaded exact Pages artifact itself contains the zero counters and unresolved cards.

## Status

`needs_fix`

The publication chain is functioning as implemented. The actionable defect is the semantic identity churn: an immutable source-commit change for byte-identical profile content produces a new profile pin/global generation, invalidates all current Deep authority, and made the completed 30-item migration immediately non-current.

## Recommended next step

Create exactly one bounded contract-first fix task for **Progressive profile semantic identity stability across byte-identical profile content**: preserve immutable commit provenance/verification, but prevent a resolved-commit-only change with unchanged profile blob/content, taste model, taste semantics, and candidate-context contract from resetting the global semantic generation; include a regression proving completed current Deep/migration authority remains current across that provenance-only refresh.

## Exact commit/run/artifact refs

- Diagnostic pinned current main: `ebaa18ff406fb9c1744ed559990043570080b7b2`
- Initial diagnostic main before parallel merge: `b46c8d959c2307f3091d84cdee3d6b0ea1d77c88`
- ЧАТ 1 merge / PR #111: `ebaa18ff406fb9c1744ed559990043570080b7b2`
- Migration authority: `97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a`
- Migration frozen at: `2026-09-28T04:01:33Z`
- Last migration result commit: `cbb0006b5c22d09f684965ecbe6c3c4c6d29a056`
- Final PASS 2 reconcile: `628179fcf90367d0a79701fd13e98a0e511b864f`
- PASS 2 state blob: `f4eda46acbece7056df60a18f66f35b6920c5935`
- PASS 2 work blob: `367985f449a663805a596975ac9be4164e865444`
- Migration manifest blob: `3604eb8f85fa7778140718766622f0323c987504`
- Pre-refresh projection commit: `5379362a691657fc9cb05844841ab14016c3b93e`
- Profile-pin-changing pre-AI refresh: `99120f8c7ae8f14c434eac70b96ff5105a9d2aab`
- Current projection blob: `1e873ecc5ee5d7b17d29b66a429588b8e8f40d5e`
- Migration profile resolved commit: `feb5e74d5d3d95000612ee2888926618001e6424`
- Current profile resolved commit: `09f4901ff0eef5b6fda15f32ff43d53907df7072`
- Shared unchanged profile blob: `9b9926031889dbd98ba6585c57836d52c739a0bb`
- Shared unchanged profile content SHA-256: `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`
- Migration semantic generation: `4596b03979956f78c308551a75fdbe9f432ed3f80925c29b0835bdb052222033`
- Current semantic generation: `f76f0ed6b470b58f0eaf7a72a9bb0e18d3ed8a6b41a1956a1ff1229776b09e92`
- Current visual blob: `fbbf9a37faf7d1479ca030c3a80c0fc49fea8e51`
- Visual build run: `36410679154`
- Deployed visual commit: `e6c9cbf925bcb45f54d1c62bf42a05c953623e79`
- Pages deploy run: `36410747696`
- Pages artifact: `10964217340`
- Pages artifact digest: `sha256:bfefef795b78830dd3664251942a6a6d981f4e8bc9b741ade9bedd8f02266319`
- Deployed `web/data/current.json` SHA-256: `a61980e9eb6de825afe89d1afba06bfdf03f97156bf170131dd9d6c195eb1e4d`

## Efficiency / reusable lesson

When a completed semantic migration appears in durable state but vanishes from all user-facing current counters, compare **identity material before inspecting UI freshness**.

In this incident, one compact comparison proved the cause:

- durable migration result exists;
- current exact-bound selector rejects it;
- item fingerprint/context is unchanged;
- profile bytes are unchanged;
- only immutable profile commit provenance changed the profile pin/global generation.

That boundary explained Statistics, cards, ranking, Pages, and the apparent need to rerun the same 30 games without requiring any worker execution, rebuild, cache clearing, or manual deployment.
