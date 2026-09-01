# Fixed Steam package purchase options

Status: production-validated including UI visibility and ranking value on 2026-08-31.

## Product/architecture decision

Only fixed Steam Store Package (`Sub_`) purchase options are eligible. Dynamic or personalized Complete-the-Set `/bundle/` prices are excluded fail-closed because they are account-dependent and cannot be treated as a stable producer-owned price.

A package is considered only when:
- it covers at least 2 currently visible base-game families;
- coverage comes from actual included appids / canonical family membership only;
- no original/remaster equivalence is guessed;
- the package current KZT price is strictly below the sum of standalone current KZT prices for those visible families;
- each family is counted once;
- unknown extra content contributes zero assumed value.

### Ranking rule

Packages are no longer display-only.

Taste remains completely price-blind and unchanged. Package economics affect only the purchase/value side of the final score.

For every game with an eligible `better_purchase_option`, the canonical scorer computes two independent purchase routes:
1. `standalone` — the existing purchase score from absolute sale savings, current game price and history quality;
2. `fixed_package` — a package purchase score from savings versus buying the currently visible covered games separately, effective package price per covered visible game, and number of covered visible games.

The scorer uses the higher of those two transparent purchase scores. A tie keeps `standalone`. The package score is therefore an alternative purchase route, not a bonus stacked on top of standalone economics; this avoids double-counting the same commercial value.

The fixed-package route currently has the same 40-point purchase ceiling as standalone. Its numeric bands and practical package-price ceiling are owned by `config/final_ranking_policy.json`, not hard-coded product prose.

Product intent: one suitable game for ~150 ₽ can be a good purchase, but a fixed package around ~300 ₽ containing several suitable/currently visible games can be materially better value and should be able to raise the final ranking.

### UI rule

A qualifying package is not hidden among normal offers. `web/app.js` renders a dedicated highlighted `🎁 Выгодный набор Steam` block with:
- package name and total price;
- number and names of currently visible covered games;
- standalone total;
- absolute savings and savings percentage versus those standalone current prices;
- approximate package price per covered visible game;
- explicit explanation when the package route is currently driving the purchase score;
- a button opening the package in Steam.

UI never recomputes package eligibility, economics or score; it displays producer-owned fields.

## Fast route

Contract / discovery:
- `config/fixed_package_purchase_option_contract.json`
- `scripts/build_fixed_package_purchase_options.py`
- output: `data/production/pre_ai/fixed_package_options.json`

Package comparison/enrichment:
- `scripts/apply_fixed_package_purchase_options.py`
- producer field: `better_purchase_option`
- also creates `fixed_multi_game_package` offer metadata and `purchase_option_enrichment` diagnostics.

Final ranking:
- `config/final_ranking_policy.json` -> `score_model.purchase.fixed_package`
- `scripts/priority_ranking.py` -> standalone/package route comparison
- `scripts/build_final_visual_payload.py` -> package enrichment happens before the single final `apply_final_priority_order()` pass.

Regression:
- `scripts/test_fixed_package_purchase_options.py`
- `scripts/validate_priority_ranking.py`
- `.github/workflows/validate-package-purchase-value.yml`
- BioShock regression uses actual package members `409710`, `409720`, `8870`; originals are deliberately not inferred from remasters.

UI:
- `web/app.js` -> `renderPackageDeal(g)` / highlighted package block.

Workflow integration:
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`

Audit output:
- `data/production/visual/ranking_review.jsonl` exports purchase route, standalone/package scores, score delta, package price/count/savings and `better_purchase_option`.

## Production validation after ranking-aware reopening

Implementation merge:
- main commit `a86b0e793b445c5d1af54ac08ba00528be946f6e`
- message: `Make fixed Steam packages visible and ranking-aware`.

Visual build #111:
- run `33423352245` — success;
- `PRIORITY_RANKING_VALIDATION=PASS`;
- fixed-package regression: `12 passed`;
- `VISUAL_FINAL_BUILD=BUILT ... items=445 ... package_qualifying=7 package_touched=17`;
- `PACKAGE_VISIBLE_CARDS=17`;
- `PACKAGE_RANKING_DRIVERS=15`;
- visual commit `66c00e9e389691be885123a9dd4e48663c41d5ad`.

Examples from the production ranking review log:
- `FlatOut 2` -> `Flatout Complete Pack`, ~272 ₽, 3 visible games: standalone purchase score `22`, package score `36`, delta `+14`;
- `The Night of the Rabbit` -> `The Daedalic Armageddon Bundle`, ~120 ₽, 7 visible games: `22 -> 40`, delta `+18`;
- `Penumbra: Black Plague Gold Edition` -> `Penumbra Collectors Pack`, ~134 ₽, 2 visible games: `18 -> 32`, delta `+14`;
- `The Dark Eye: Memoria` -> `The Daedalic Armageddon Bundle`, ~120 ₽, 7 visible games: `27 -> 40`, delta `+13`.

Deploy acceptance:
- initial code deploy could race the visual rebuild, so it is not sufficient proof by itself;
- downstream deploy #151 / run `33423389598` completed successfully on package-aware visual commit `66c00e9...`;
- actual GitHub Pages artifact #151 (`9769779423`) was inspected, not just source files: the same deployed artifact contains the highlighted package UI and package-aware `data/current.json` with 17 package cards / 15 package ranking drivers.

Later non-regression:
- visual run #113 / `33437077173` completed success;
- package regression still `12 passed`;
- ranking review still reported `PACKAGE_VISIBLE_CARDS=17` and `PACKAGE_RANKING_DRIVERS=15` with the same example deltas.

## Diagnostic / acceptance route

For a future report that “packages are missing”:
1. Do not start from the old feature branches; main already owns the feature.
2. Check one current visual workflow log for `PACKAGE_VISIBLE_CARDS` and `PACKAGE_RANKING_DRIVERS`.
3. Check the specific game's `better_purchase_option` / package fields in bounded ranking review or current payload.
4. If producer data exists but the user cannot see the block, inspect the deployed Pages artifact / `web/app.js` path rather than re-debugging discovery.
5. If producer data is absent for that game, inspect package membership/price eligibility; not every game should have a package block.

Large generated JSON files can occasionally be surfaced poorly by the GitHub connector. Prefer bounded workflow diagnostics and a specific game lookup before attempting a full huge-file read.
