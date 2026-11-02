# ЧАТ 1 — independent final L3 delta QA: Steam post-merge Actions

**Task:** `steam-postmerge-actions-l3-final-delta-qa-01`  
**Role:** independent narrow delta QA; report-only; source of truth: `main`.  
**Verdict: PASS_FOR_DIRECTOR_MERGE** for **source PR #346** at exact reviewed HEAD `8619ad1dfcd88ea203f6d7e732f335e3597767db`, conditional on the Director rechecking that the source HEAD and its required checks have not changed before merge. **Not** a post-merge runtime/deploy acceptance.

## Exact GitHub evidence and bounded review scope

- Source: [draft PR #346](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/346), branch `fix/steam-postmerge-actions-failures-01`, open, not merged; exact checked HEAD `8619ad1dfcd88ea203f6d7e732f335e3597767db`; GitHub `mergeable=true`. `main` observed as `d24e9427425538600f8b3fb560ea41459658aaa1` during QA. Any later GitHub movement requires fresh pre-merge readback.
- Baseline independent [L3 QA PR #349](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/349): `reviews/worker_reports/steam-postmerge-actions-failures-final-l3-qa-01.md` on branch `qa/steam-postmerge-actions-failures-final-l3-qa-01`, baseline source `8df383752da1b119742702767d780a00580a18a5`, verdict `CHANGES_REQUIRED`.
- Targeted repair report: `reviews/worker_reports/steam-postmerge-actions-l3-targeted-repair-01.md` in source #346, exact code HEAD noted there as `e84367ce0220fc8460da9622d72b93d2700022cf` before report-only commit.
- Independent compare `8df3837...8619ad1` identified **seven and only seven** changed paths in the bounded delta: three workflows `build-content-{metadata,eligibility-validation}.yml`, `build-offer-family-resolution.yml`; `scripts/legacy_offer_scope.py`; `scripts/test_legacy_offer_scope.py`; `config/content_eligibility_contract.json`; and the targeted-repair worker report. No mailing/data cache deletion, collector or scheduler implementation in that delta.
- Checked exact source files, caller ordering, synthetic-negative test cases and relevant `config/{content_eligibility_contract,offer_family_contract,execution_ownership_contract,daily_execution_contract}.json`. Preserved findings from prior L3 QA are not presented as a fresh full audit.

## CR-1 — exact metadata identity before reuse, classification, and family consumption: PASS

- Shared `scripts/legacy_offer_scope.py::validate_metadata_identity(key, entity, offer)` checks a well-formed `App_*/Sub_*` ID, exact `offer.key`, `entity.key`, expected `entity_kind`, and matching `entity.steam_id`. For `App_2`, offer AppID also must be exactly `2`. For `Sub_456`, metadata Steam ID must be **package ID 456**, while a representative mailing `appid=2` is legitimate and not equated with the package ID.
- `build-content-metadata.yml`: reused `entries[key]` are identity-checked **before** being treated as cache hits or used in `missing`; every required row is checked **again after fetch, before writing** `content_metadata.json`. Malformed cached/fetched required entries cause controlled `SystemExit`, not silent reuse.
- `build-content-eligibility-validation.yml`: exact identity validation occurs inside the current-INCLUDE loop **before** `store_name`, entity/type, DLC/package and other classification branches.
- `build-offer-family-resolution.yml` invokes `assert_family_inputs` **before** deriving metadata-dependent families, membership, or primary price comparisons. `assert_family_inputs` checks metadata identity for **every** current eligible or excluded row, plus complete key coverage and matching eligibility AppIDs. Prices originate in current mailing TSV; no synthetic price fallback is introduced.
- Existing `scripts/test_legacy_offer_scope.py` directly rejects `App_2 steam_id=999`, wrong metadata key and `entity_kind`, and invalid `Sub_456 steam_id=2`; it accepts `Sub_456 steam_id=456` with representative `appid=2`. The regression script is run in existing PR CI.

## CR-2 — freshness against actual HEAD taste-index blob at family read boundary: PASS

- `build-offer-family-resolution.yml` checks out `main` with full Git history and calls `assert_family_inputs(..., taste_index_sha=sha('data/cache/taste_fit.index.json'))`, where `sha` resolves `git rev-parse HEAD:<path>` from the checked-out Git tree.
- `assert_family_inputs` requires `meta.taste_index_blob_sha == elig.bindings.taste_index_blob_sha` **and**, independently, **both** to equal the nonempty `taste_index_sha` from the current HEAD. It also retains current `policy_blob_sha`, mailing-tree SHA and metadata blob SHA checks. Errors fail closed with no fallback to the jointly stale pair.
- Negative test `test_both_persisted_taste_bindings_stale_against_head` assigns metadata and eligibility `old_A`, then requires rejection against current `new_B`. Producer metadata and eligibility also bind their sources via `HEAD` Git blob/tree provenance; all current family consumers use the gated metadata.

## CR-3 — dynamic stage-12 complete current-INCLUDE partition: PASS

- `config/content_eligibility_contract.json#diagnostic_stage_12.pass_requires` now requires **eligible + excluded == current-feed INCLUDE count**, rather than fixed historical 101; retains zero unresolved, all current feed INCLUDE rows classified, valid exclusion codes, current complete checkpoint and separate historical out-of-feed accounting.
- `build-content-eligibility-validation.yml`: `active_keys` is the intersection of historical INCLUDE keys with the current  mailing feed; classifier visits exactly those keys. `classified = len(eligible) + len(excluded) + len(unresolved)` must equal `len(include_keys)`; complete status additionally requires `len(unresolved)==0` and no invalid exclusion codes. It serializes current input, historical count, `out_of_current_feed_keys`, and sorted disposition counts. The family boundary further requires `len(eligible)+len(excluded)==input_taste_include_count==classified_count`, exactly one row/key and exact metadata coverage.
- Previously independently observed source snapshot: **703 current offers; 101 historical INCLUDE; 34 current-feed INCLUDE; 67 historical-only INCLUDE**. Current mailing index still declares 703. The delta compare contains no changed mailing rows or taste index; these figures are *observations*, **not hard-coded runtime quotas**. Example inactive historical-only `App_1` remains in a regression receipt without becoming a current-price offer. The previous QA independently established zero duplicate current keys and no current AppID mismatch; this delta does not undo those checks.

## Exact-final-HEAD PR CI and release limits

The following GitHub PR workflow runs are associated with **source HEAD `8619ad1dfcd88ea203f6d7e732f335e3597767db`** and completed successfully:

1. [Steam KZ production shortlist #40809624233](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40809624233): `regression` job **SUCCESS**, including compile, post-merge policy/scope step and fresh discovery regressions. `collect` job **SKIPPED BY DESIGN** for PR events. The scope regression script contains eight unittest methods including the CR-1 and CR-2 negative cases.
2. [Validate backlog dispositions #40809624209](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40809624209): **SUCCESS**.
3. [Validate site task registry and page #40809624195](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40809624195): **SUCCESS**.

The earlier L3 findings that remain preserved: exact policy 1.22 / exact profile-SHA guard, current mailing scope and AppID binding, complete retained historical out-of-feed listing, and no invented KZT price, implicit omission or silent fallback. The delta does not transfer GitHub-owned scope/order/classification/price responsibilities to interactive ChatGPT.

**Unverified and outside this QA:** real Steam collection, refreshed live metadata/eligibility/family artifacts, downstream nightly main completion, visual publication and Pages deployment. Three green deterministic PR workflows are **not** evidence of those post-merge outcomes. No production Actions were dispatched, no retry/recovery performed, and no workflow/source/queue/ownership/semantic changes or merges were made by this QA.

**Director decision:** Source #346 is eligible for Director merge review given `PASS_FOR_DIRECTOR_MERGE` and current exact-HEAD CI. Confirm the source branch has **not advanced**, `mergeable=true`, and all required exact-HEAD PR CI remain green immediately before merge; the existing GitHub-owned post-merge live gate remains a distinct follow-up. No second implementation PR, no additional full QA of unchanged scope.
