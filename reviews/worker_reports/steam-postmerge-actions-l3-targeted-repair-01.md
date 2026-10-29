# ЧАТ 4 — Steam postmerge Actions L3 targeted repair

Task: `steam-postmerge-actions-l3-targeted-repair-01`. Repository `kentrap2011-hub/steam-kz-deals-2`, source `main`. Source-only changes in existing draft [PR #346](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/346), branch `fix/steam-postmerge-actions-failures-01`; no new implementation PR. Independent finding authority: [QA PR #349](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/349), `reviews/worker_reports/steam-postmerge-actions-failures-final-l3-qa-01.md`. Pre-repair source HEAD `8df383752da1b119742702767d780a00580a18a5`.

## Only CR-1 / CR-2 / CR-3 repaired

1. **CR-1 — cached metadata identity.** `scripts/legacy_offer_scope.py::validate_metadata_identity` rejects absent/mismatched metadata `key`, `entity_kind`, or `steam_id` versus current App_/Sub_ key; App_ checks current mailing AppID. Sub_ checks **package ID**, independent of representative mailing AppID. `build-content-metadata.yml` validates reused cache hits *before* reuse and newly fetched rows before persistence; `build-content-eligibility-validation.yml` validates before classifying; `assert_family_inputs` validates all current metadata before family consumption/prices. Regression explicitly rejects `App_2` metadata `steam_id=999`, wrong metadata key/kind and `Sub_456` incorrect package ID, while permitting `Sub_456` with representative `appid=2` and correct `steam_id=456`.
2. **CR-2 — jointly stale taste bindings.** `assert_family_inputs` now requires an explicit `taste_index_sha`; it verifies both metadata and eligibility embedded taste-index SHAs match the actual `HEAD:data/cache/taste_fit.index.json` blob, **in addition to** their mutual equality. `build-offer-family-resolution.yml` supplies SHA from Git HEAD at read boundary. Regression rejects metadata and eligibility both bound to stale `old_A` when current HEAD is `new_B`.
3. **CR-3 — stage 12 invariant.** `config/content_eligibility_contract.json` now requires `eligible + excluded == current-feed INCLUDE count`, not static 101; zero unresolved, current coverage, exclusions, checkpoint and source evidence remain required. The previous **101 historical INCLUDE / 34 current-feed INCLUDE / 67 historical out-of-feed** counts are observations from independent QA, not a static invariant.

## Verification / release boundary

- **Exact changed-code HEAD** `e84367ce0220fc8460da9622d72b93d2700022cf` (before this report-only commit).
- [Steam KZ production shortlist run 40809446396](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40809446396) **SUCCESS**, including `Compile touched Python modules`, `Validate post-merge policy and historical/current offer scope` and `Run fresh discovery regressions` (includes eight `scripts/test_legacy_offer_scope.py` tests). PR `collect` intentionally **SKIPPED**.
- [Validate backlog dispositions 40809446436](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40809446436) **SUCCESS**; [Validate site task registry and page 40809446445](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40809446445) **SUCCESS**.
- This report is an additional report-only commit, so report-inclusive **final PR HEAD** and its exact-HEAD CI must be recorded after this commit by GitHub PR status/readback; the code-HEAD success must not be misrepresented as final-HEAD CI.

**Preserved:** the complete current mailing offer scope, 67 historical-only records retained as explicit out-of-feed receipt, no invented prices, no unreported eligible-row omission, exact policy/profile/current SHA guardrails and GitHub-owned classification/family responsibility. No pricing, stage owners, scheduler, queue/retry, Deep/Dossier, collector, production, deployment, workflow dispatch or merge changes.

**Not proven by PR CI:** live collection, refreshed metadata/eligibility/family artifacts, main nightly chain, Pages publication. Those are separate existing GitHub-owned post-merge gates; no manual production Actions were triggered.

**Verdict: FIX_READY_FOR_NARROW_L3_DELTA_QA**, subject to successful final report-inclusive PR HEAD CI readback. Director to request independent **only CR-1/CR-2/CR-3** delta QA, then decide merge. No self-merge.
