# Independent L3 QA — Steam post-merge Actions failures (final)

Task: `steam-postmerge-actions-failures-final-l3-qa-01`  
Role: new physical ЧАТ 2, report-only independent review.  
Repository: `kentrap2011-hub/steam-kz-deals-2`; truth: `main`.  
**Verdict: CHANGES_REQUIRED** (do not merge source PR #346 yet).

## Frozen source and live merge/CI evidence

- [Source draft PR #346](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/346), branch `fix/steam-postmerge-actions-failures-01`, exact checked HEAD `8df383752da1b119742702767d780a00580a18a5`; two commits, ten changed files. Source report: `reviews/worker_reports/steam-postmerge-actions-failures-fix-01.md` in that branch.
- At verification, PR was open/draft, `mergeable=true`, `mergeable_state=clean`; base PR SHA `fcbbec1eacdc81cca88193283e97d49e294d1091`. Live `main` observed at `a60f08db6ac33c2685c909b49d2ea6ef63481b88`; compare `main...source`: source ahead 2, behind 4, diverged; this does **not** imply a conflict because the independent GitHub mergeability check is clean.
- Exact-HEAD checks: [Steam shortlist run 40749245771](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40749245771) **success**; regression job [123031175924](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40749245771/job/123031175924) **success**, including `Compile touched Python modules`, `Validate post-merge policy and historical/current offer scope`, and `Run fresh discovery regressions`, all individually success; `collect` job **skipped** by PR isolation. [Backlog dispositions run 40749245878](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40749245878) success. [Site task registry run 40749245738](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40749245738) success. All four reported check runs finished (three success, one intentionally skipped); no pending/failing final-HEAD checks in the returned set.
- Code-specific review covered all changed production workflow files, `scripts/legacy_offer_scope.py`, `scripts/test_legacy_offer_scope.py`, `scripts/validate_mailing_policy.py`, and the changed content-eligibility contract; checked source upstream report, production ownership and daily execution invariants. No source edits, action dispatches, merges, or added schedulers.

## Verified positive findings

1. Policy validation compares current canonical policy version `1.22`; the projection source actually uses `profile_ok = cached['profile_blob_sha'] == profile_blob_sha` (in `scripts/build_pre_ai_taste_projection.py`) and retains the fail-closed cache/profile invalidation predicate. The validator changed its static string check to match this existing exact-SHA expression; did not disable that predicate.
2. Independent bounded recount of `data/production/mailing/index.json`, five mailing TSV chunks, and `data/cache/taste_fit.index.json` on source HEAD: **703 distinct current offers, zero duplicate keys, zero empty/mismatched App IDs, 101 historical INCLUDE, 34 current-feed INCLUDE, 67 historical INCLUDE outside current feed, zero active taste-versus-feed AppID mismatches**. The changes no longer try to classify those 67 historical-only entries as live offers, and they retain explicit sorted out-of-feed keys/counts in metadata and eligibility. No historical verdict deletion.
3. `assert_family_inputs` now checks current mailing-tree SHA, policy blob SHA, metadata blob SHA, mutual metadata/eligibility taste-index SHA, completion, unique eligibility keys, exact metadata key set, current feed membership and eligibility AppID equality before accessing prices. Prices and discounts are consumed from the current mailing TSV; no synthetic/fallback price path was introduced by PR #346. Assignment coverage/uniqueness checks remain in family producer. No new recurring workflow, queue, recovery, or retry logic was added.
4. Source PR test covers representative historical-out-of-feed treatment, missing eligible row, stale mailing/metadata binding, duplicate offer, and taste-versus-feed AppID mismatch. CI green **does not** exercise live production.

## Changes required before Director merge

### CR-1 — Cached metadata entity identity is not checked (source correctness, fail-closed)

`.github/workflows/build-content-metadata.yml` reuses `previous['entries'][key]` when a key is present (lines approximately 169–195) without verifying that the cached entity itself corresponds to its dictionary key. `.github/workflows/build-content-eligibility-validation.yml` classifies `metadata_entries[key]` based on `entity_kind`, `app_type`, `package_apps` and `fullgame_appid` without validating metadata `key/entity_kind/steam_id` against the current row. `scripts/legacy_offer_scope.py::assert_family_inputs` checks eligibility `appid` versus feed `appid`, but **not** the metadata entity `steam_id` and key against the actual App_/Sub_ key.

Concrete negative-case specification: take the passing helper fixture in `scripts/test_legacy_offer_scope.py`, change only `meta['entries']['App_2']['steam_id']` to `'999'` while retaining matching current metadata/eligibility SHA bindings, and the helper's validations still accept it. This allows an internally inconsistent reused metadata row to guide eligibility/family classification. A real upstream fetch could be stale or malformed even when GitHub SHA labels consistently describe that bad content. Require exact identity validation when reusing metadata **and before classifying/consuming it**, with a fail-closed regression. For `App_123`, metadata must identify app 123 and agree with feed AppID; for `Sub_456`, metadata must identify package 456 (the mailing `appid` for a Sub may be a representative app, **not** its package ID).

### CR-2 — Two jointly stale taste sources pass family binding (source authority)

`.github/workflows/build-offer-family-resolution.yml` calls `assert_family_inputs` with HEAD SHAs for policy, mailing tree and metadata blob, but does **not** pass the HEAD `data/cache/taste_fit.index.json` blob SHA. In `scripts/legacy_offer_scope.py`, only `meta.taste_index_blob_sha == elig.bindings.taste_index_blob_sha` is checked. If both persisted artifacts were generated from taste index A and the live index is now B while mailing tree and metadata file remain the same, the helper has no way to notice and can accept old INCLUDE coverage. This is a live producer race/manual-dispatch stale-pair scenario, not cured by the mutual equality check. Compare both bindings to the actual current GitHub taste-index blob SHA at the family read boundary, and add a regression for **both stale together** (not only disagreeing with each other).

### CR-3 — Diagnostic eligibility contract still fixes count to 101

`config/content_eligibility_contract.json#diagnostic_stage_12.pass_requires` now correctly says current-feed INCLUDE rows are classified and historical out-of-feed INCLUDE rows are separately enumerated, but still says `eligible plus excluded equals 101`. The actual current source has 34 current-feed INCLUDE; a hardcoded 101 count contradicts the new authoritative dynamic-scope rule. Replace the stale hardcoded count with `eligible + excluded == current-feed INCLUDE count`, retaining zero-unresolved/completeness and 101 as observed historical evidence only (not a production invariant).

**Scoped follow-up:** address CR-1/2/3 only in original source [PR #346](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/346); add fail-closed negative tests to existing Steam regression workflow, preserve price/source identity and exact-pinned checks, obtain green CI on the new exact HEAD, then request an independent bounded L3 recheck. Do not open another feature implementation PR from this QA report.

## Explicitly unproved / boundaries

- Passing PR-only deterministic tests is **not** proof of a successful live Steam collector, refreshed metadata+eligibility+family producers, normal main publication, or Pages deploy. Existing reported [Steam collector run 40523125746](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125746) had a separate live collect failure; [site status run 40523125745](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125745) had a Git write race; visual/deploy cancellation is not proof of this particular family error.
- No production run/recovery/merge was initiated. The existing GitHub-owned nightly production and read-only site boundary remains in force; live acceptance is a separate post-merge gate.
- No observed current-row loss or price fabrication was found in the source snapshot, but these findings do **not** establish complete robustness against stale or malformed input until CR-1 and CR-2 are fixed.
- This is narrow final-L3 QA of source PR #346 only; no unrelated audits.
