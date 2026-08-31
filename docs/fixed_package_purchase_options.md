# Fixed Steam package purchase options

Status: production-validated on 2026-08-31.

## Product/architecture decision

Only fixed Steam Store Package (`Sub_`) purchase options are eligible. Dynamic or personalized Complete-the-Set `/bundle/` prices are excluded fail-closed because they are account-dependent and cannot be treated as a stable producer-owned price.

A package is recommended only when:
- it covers at least 2 currently visible base-game families;
- coverage comes from actual included appids / canonical family membership only;
- no original/remaster equivalence is guessed;
- the package current KZT price is strictly below the sum of standalone current KZT prices for those visible families;
- each family is counted once;
- unknown extra content contributes zero assumed value.

Taste and final ranking are unchanged. The producer writes `better_purchase_option` and a `fixed_multi_game_package` offer; UI only displays them.

## Fast route

Contract:
- `config/fixed_package_purchase_option_contract.json`

Discovery / pre-AI producer:
- `scripts/build_fixed_package_purchase_options.py`
- output: `data/production/pre_ai/fixed_package_options.json`

Comparison / visual enrichment:
- `scripts/apply_fixed_package_purchase_options.py`
- output fields: `better_purchase_option`, package entry in `offers`, `purchase_option_enrichment`

Regression:
- `scripts/test_fixed_package_purchase_options.py`
- BioShock regression uses actual current package members `409710`, `409720`, `8870`; originals are deliberately not inferred from remasters.

Workflow integration:
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/build-daily-visual-payload.yml`

## Production validation 2026-08-31

Integration merge:
- PR #1
- main commit `1438d6531062cd884a42177b33151606fc5e5fe9`

Pre-AI build:
- run #65 / `33418890981` — success
- fixed-package regression — success
- real `fixed_package_options.json` built and committed
- artifact: 679 current app candidates, 795 discovered package ids, 19 eligible fixed packages, all 795 classified (`classification_complete=true`)

Visual build:
- run #110 / `33418941938` — success
- `VISUAL_FINAL_BUILD=BUILT ... items=445`
- `FIXED_PACKAGE_OPTIONS=APPLIED qualifying_packages=7 touched_games=17`
- `RANKING_REVIEW_ROWS=445`
- visual commit `5b3b9244e207fb11cd32de22ed866f04ee896df8`

Deploy:
- run #149 / `33418983959` — success

## Diagnostic note

Large generated JSON files can be returned as empty content by the GitHub connector even when the blob is not actually empty. Do not infer production emptiness from that read alone. For this route, use the completed visual-workflow log (`VISUAL_FINAL_BUILD`, `FIXED_PACKAGE_OPTIONS`, `RANKING_REVIEW_ROWS`) plus the visual commit/ranking lookup counts as bounded proof before attempting large-file retrieval.
