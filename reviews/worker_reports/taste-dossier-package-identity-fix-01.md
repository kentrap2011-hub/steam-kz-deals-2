# Taste Dossier Package Identity Fix 01

Task: `WORKER_TASK_TASTE_DOSSIER_PACKAGE_IDENTITY_FIX_01.md`  
Mode: `IMPLEMENT_AND_VALIDATE`  
Status: `complete_ready_for_activation`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Implementation PR: `#31` — `worker/taste-dossier-package-identity-fix-01`  
Validated implementation head: `f66d4629d5f81c74bda78ae14e6638ddb615a73d`

## Architecture preflight

Result: **PASS**.

- Steady-state semantic consumer remains the existing external/Scheduled ChatGPT Steam-review dossier worker. It consumes GitHub-prepared compact descriptors and publishes bounded semantic evidence through the existing persistence bridge.
- GitHub remains the durable control plane for canonical queue scope, deterministic ordering/grouping, validation, checkpoint progress, persistence, and completeness.
- This change adds no second scheduler, poller, queue owner, semantic producer, or competing checkpoint owner.
- The change is authorized by the package-identity worker task and is consistent with `PROJECT_DECISIONS.md` / `TASTE-007`: the worker must receive one exact game/release identity and ambiguity must fail closed before semantic research.
- The PR-only validation workflow remains a test gate; adding this regression to that workflow does not alter production execution ownership or cadence.

## Root cause

The known live blocker was a boundary-conflation bug, not a bad commercial offer.

Current canonical queue evidence for `Sub_87601` is internally coherent on the **offer** side:

- `taste_subject_key = Sub_87601`;
- title = `Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle`;
- source row `appid = 304240`;
- `semantic_condition.ai_condition = bundle_or_package_taste_evaluation_required`;
- `semantic_condition.base_appids = ["304240", "339340"]`;
- package members include at least the independent base games `Resident Evil` (`304240`) and `Resident Evil 0` (`339340`).

The defect appeared downstream:

1. upstream purchase-family / Taste projection correctly preserved the package as a package/Taste subject;
2. the dossier scope path then copied the queue row's `appid` and package title directly as though they were a single-game dossier identity;
3. first-occurrence `appid` dedupe accepted that malformed `Sub_87601` shape under `304240`;
4. the later coherent `App_304240` / `304240` / `Resident Evil` row was therefore shadowed;
5. the worker descriptor exposed the hybrid `bundle title + contained appid`, and the V2 identity gate correctly failed closed during live acceptance.

Thus `304240` was valid data in the commercial/package row but was not sufficient authority to claim that the package itself was the single-game dossier target.

## Identity separation implemented

The active web-evidence work builder now separates two concepts before dossier `appid` dedupe:

### Offer identity

For a package/bundle source row, offer metadata is retained separately as:

- source Taste key;
- `family_id`;
- package/store title;
- original source-row `appid`.

This preserves the commercial/Taste offer identity without asserting that the source-row appid is the package's one game identity.

### Dossier identity

A package may produce single-game dossier work only when GitHub already has one deterministic canonical game mapping:

- `semantic_condition.base_appids` contains exactly one unique numeric appid; and
- `bundle_members` contains exactly one non-empty title for that exact appid.

Only then does the dossier item use that exact game `appid + title`. The original package metadata remains attached separately as `offer_identity`, with `dossier_identity_resolution = single_canonical_base_appid_and_bundle_member_title`.

If there are zero or multiple canonical base games, or the exact member title cannot be resolved uniquely, no single-game identity is fabricated. The row is held before worker projection in `identity_blocked_items` with a machine-readable reason and candidate appids.

For `Sub_87601`, the result is:

- `reason = ambiguous_multi_game_offer_no_single_dossier_identity`;
- candidate game appids = `304240`, `339340`;
- package title and original source-row appid remain in `offer_identity`;
- no worker item is emitted for the package;
- because blocked package rows do not consume dossier `appid` dedupe state, the later coherent `App_304240` remains eligible as `304240 / Resident Evil`.

Ordinary non-package `App_...` rows keep their existing exact dossier identity shape unchanged.

## Manifest / progress safety

The daily web-evidence manifest now records:

- `identity_policy_revision`;
- `identity_blocked_count`;
- `identity_blocked_sha256`;
- `identity_blocked_items`.

The blocked-set digest is included in `snapshot_id` construction, so the fixed prepared snapshot is cryptographically bound to the identity disposition used at preparation time.

Blocked package rows are counted as eligible source rows but are not inserted into `prepared_required_items`, submission groups, or worker descriptors. Therefore they cannot consume or advance dossier completion/checkpoint progress.

Resolved single-game package rows retain their separate offer metadata in manifest/required-item state while the worker-facing `title + appid` remains the exact single-game dossier identity required by the V2 contract.

## Proof bundles/packages are not lost from user-visible discounts

This task does not filter, delete, or rewrite the commercial/package pipeline.

- No `build_pre_ai_*` family/Taste projection, mailing, visual, ranking, package economics, or discount eligibility code was changed.
- `data/production/pre_ai/chatgpt_taste_queue.jsonl` was not modified.
- The resolver operates on projected dossier scope; its regression asserts the original package queue row remains object-identical after resolution.
- The manifest retains the source row in `source_row_count` / `eligible_row_count` and records the package under machine-readable `identity_blocked_items` rather than pretending it is a game dossier.
- The scope exclusion is therefore only from **single-game dossier work**, not from the store offer, Taste offer, or user-visible discount surfaces.

## Exact post-fix beginning of dossier worker scope

Using the current queue fixture with an empty dossier store, the first three actionable worker items after removing the ambiguous `Sub_87601` dossier identity are exactly:

1. `App_2378500` — appid `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC`
2. `App_1000360` — appid `1000360` — `Hellish Quart`
3. `App_1003590` — appid `1003590` — `Tetris® Effect: Connected`

`Sub_87601 / 304240 / Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle` is absent from worker descriptors. A later coherent `App_304240 / 304240 / Resident Evil` remains actionable and is no longer shadowed by the blocked package row.

The separately published identity edge-case audit correctly notes that item 1 above is a different non-game/addon identity class and is outside this bounded package fix. This task intentionally does not broaden into addon, app-backed collection/hub, or release-year normalization work.

## Files changed in implementation PR

- `scripts/taste_steam_review_dossier_web.py`
  - package/offer vs dossier identity resolution before appid dedupe;
  - fail-closed diagnostics;
  - manifest identity-block binding and separate offer metadata.
- `scripts/test_taste_dossier_package_identity_fix.py`
  - ordinary App identity unchanged;
  - deterministic one-base-game package mapping;
  - concrete `Sub_87601` ambiguous fail-closed behavior;
  - source offer preservation;
  - no malformed worker descriptor;
  - blocked package cannot shadow coherent `App_304240`;
  - exact V2 title/appid identity contract remains intact.
- `.github/workflows/validate-taste-dossier-buffered.yml`
  - includes the new regression in the existing PR-only dossier validation suite and path filter.

Protocol bookkeeping only, directly on `main`:

- `CURRENT_TASK.md` closeout commit `31dcb78bae15e335ec42d2cfa2783d0a1ac7a1a1`.

## Commits / PR

Implementation branch commits relevant to this task:

- `50b181e25b269515767b6fda1a39d24a41935487` — separate package offer and dossier identities;
- `d09f87dce9c30cbfcbd6591b26f1ca11de537153` — initial package identity regression coverage;
- `df5446c3c37c6e52b875247af03399df0ceee4eb` — wire regression into owning PR validation;
- `dd4dd9d9a048aa7308199815078ab3ae0c568ce7` — synchronize latest main audit report into branch;
- `f66d4629d5f81c74bda78ae14e6638ddb615a73d` — prove blocked package cannot shadow coherent app identity.

PR: `#31` — `Fix package identity in Taste dossier work`.

The PR remains open and unmerged. Activation/merge was not performed by this worker.

## Validation

Owning PR workflow: `Validate buffered Steam review dossier runtime`.

Final validated run:

- run: `35051045865`;
- job: `104651285826`;
- Python: `3.12`;
- conclusion: `success`.

Commands executed by the PR gate:

```text
python scripts/test_taste_steam_review_dossier_daily_snapshot.py
python scripts/test_taste_steam_review_dossier_buffered_submission.py
python scripts/test_taste_steam_review_dossier_same_day_preservation.py
python scripts/test_taste_steam_review_dossier_strict_recovery.py
python scripts/test_taste_dossier_package_identity_fix.py
```

Results:

- daily snapshot: `9/9 OK`;
- buffered submission: `8/8 OK`;
- same-day preservation: `3/3 OK`;
- strict recovery: `12/12 OK`;
- package identity fix: `4/4 OK`;
- total: `36/36 OK`.

The package regression specifically proves:

- the concrete hybrid `Sub_87601` descriptor cannot recur;
- ambiguous multi-game package identity is not fabricated;
- the package source object remains preserved;
- a safe synthetic single-base-game package maps to a coherent exact game identity while retaining offer metadata;
- ordinary App-backed rows remain unchanged;
- `Sub_87601` does not consume `304240` dedupe state and therefore does not suppress the coherent `App_304240 / Resident Evil` dossier target;
- V2 exact descriptor title/appid fail-closed contract remains compatible.

## Production side effects

None.

This worker did **not**:

- press Scheduled Task `Run now`;
- change Scheduled Task UI/settings;
- manually dispatch any production GitHub workflow;
- change Taste Semantic Producer;
- rewrite queue/cache/receipt or dossier production state;
- deploy UI/site output;
- merge PR `#31`;
- activate a fresh production daily dossier snapshot.

The only GitHub Actions runs used for validation were automatic PR validation runs triggered by branch/PR updates.

## Residual activation boundary

The current runtime deliberately preserves an already-prepared same-day fixed snapshot. Therefore merging code alone must not be misrepresented as proof that an old prepared production descriptor has already been replaced. A fresh identity-safe preparation/activation belongs to the separate Director-authorized activation step, after review of this report and PR.

## Next step

**Director reviews and activates PR `#31`, including preparation of a fresh identity-safe daily dossier snapshot before the next live V2 acceptance run.**
