# Fixed Steam package purchase options

Status: production-validated including verified edition equivalence, UI visibility, fresh commercial comparison and ranking value on 2026-09-01.

## Product / architecture decision

Only fixed Steam Store Package (`Sub_`) purchase options are eligible. Dynamic or personalized Complete-the-Set `/bundle/` prices remain excluded fail-closed because they are account-dependent and cannot be treated as a stable producer-owned price.

A package may be surfaced when:
- it covers at least 2 currently visible base-game families;
- coverage comes from an actual included appid, canonical family membership, or an explicit directional purchase-equivalence entry;
- original/remaster equivalence is never inferred from title, franchise, `Remastered` wording or fuzzy similarity;
- each visible family is counted once;
- unknown or nonvisible extra content contributes zero assumed standalone value.

A relevant package does **not** have to be cheaper merely to be shown. `strict_current_price_savings` determines whether it is currently a cheaper route, while ranking policy determines whether the package route actually beats standalone purchase scoring.

## Purchase equivalence

Canonical overrides live in:
- `config/purchase_equivalence_overrides.json`.

They are directional and purchase-only. They do not merge Taste identities or family semantics.

Current verified BioShock mappings:
- `7670 -> 409710`: BioShock -> BioShock Remastered;
- `8850 -> 409720`: BioShock 2 -> BioShock 2 Remastered.

Exact included appid coverage remains preferred. Without an explicit override, original/remaster guessing stays forbidden and regression-tested.

## Fresh commercial value is independent of Taste

Taste remains price-blind and reusable. A price, discount, historical-price classification or package price change must not require a new semantic Taste evaluation.

The deterministic refresh path is:

1. keep the currently accepted semantic/Taste card fields;
2. refresh current standalone commercial fields from the current GitHub-owned `store_snapshot + family_graph + history_snapshot`;
3. compare fixed packages against those refreshed current standalone prices;
4. run the single canonical `FINAL-PRIORITY-RANKING-V2` pass;
5. deploy the resulting payload.

Semantic and commercial provenance are separate:
- `source_mailing_updated_at_utc` remains the accepted semantic snapshot;
- `commercial_source_mailing_updated_at_utc` identifies the current deterministic commercial source;
- `commercial_store_observed_at_utc` identifies when current Store data was observed.

`scripts/refresh_visual_commercial_fields.py` must not rewrite fit, taste factors, semantic explanations or semantic risks. Its regression explicitly verifies `taste_recalculated=false` and `semantic_fields_rewritten=false`.

If an older semantic card is no longer present in the current complete family graph, it is removed from the current storefront rather than retaining stale price data. The removal is recorded in `commercial_refresh.removed_stale_family_*` diagnostics.

## Ranking rule

Packages affect only the purchase/value side of the final score. They never increase Taste.

For every game with a package option, the canonical scorer computes two independent purchase routes:
1. `standalone` — current standalone sale savings, current price and history quality;
2. `fixed_package` — package savings versus buying the currently visible covered games separately, effective package price per covered visible game and count of covered visible games.

The scorer uses the higher transparent purchase route. A tie keeps `standalone`. Package value is therefore an alternative purchase route, not a bonus stacked on top of standalone economics.

A package that is visible but not strictly cheaper remains `purchase_route=standalone` and contributes no package ranking bonus.

## UI rule

A relevant package is rendered as a dedicated highlighted block rather than hidden among ordinary offers.

The UI displays producer-owned facts only:
- package name and package price;
- number and names of currently visible covered games;
- standalone total when source-aligned;
- savings / price delta;
- approximate package price per covered visible game;
- whether the package route currently drives purchase score;
- Steam package action.

Labels:
- strict current saving -> `🎁 Выгодный набор Steam`;
- relevant but not currently cheaper -> `🎁 Набор Steam`.

UI never recomputes coverage, economics or ranking.

## Fast route

Discovery / membership:
- `config/fixed_package_purchase_option_contract.json`
- `config/purchase_equivalence_overrides.json`
- `scripts/build_fixed_package_purchase_options.py`
- `data/production/pre_ai/fixed_package_options.json`

Fresh commercial state:
- `scripts/refresh_visual_commercial_fields.py`
- `data/production/pre_ai/store_snapshot.json`
- `data/production/pre_ai/family_graph.json`
- `data/production/pre_ai/history_snapshot.json`

Package comparison:
- `scripts/apply_fixed_package_purchase_options.py`
- producer field: `better_purchase_option`
- diagnostics: `purchase_option_enrichment`.

Final producer / ranking:
- `scripts/build_final_visual_payload.py`
- `config/final_ranking_policy.json`
- `scripts/priority_ranking.py`
- commercial refresh -> package enrichment -> one `apply_final_priority_order()` pass.

Regression:
- `scripts/test_commercial_refresh.py`
- `scripts/test_fixed_package_purchase_options.py`
- `scripts/validate_priority_ranking.py`
- `.github/workflows/validate-package-purchase-value.yml`.

UI:
- `web/package-deal-ui.js`
- `web/app.js`.

Workflow:
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`.

Audit:
- `data/production/visual/ranking_review.jsonl`
- `data/production/visual/ranking_lookup/`.

## Production validation — 2026-09-01

Relevant implementation merges:
- BioShock verified equivalence: `6783029ffe783a3971adaf57d64fa7b6aa76ec8f`;
- deterministic package refresh while Taste is queued: `1aea1408aaf54810101bb296c547999e22f81503`;
- source-mismatch safe package display: `e4b8dbb124c41b3d2ac7c947bab5cc99696c752e`;
- fresh commercial refresh independent of Taste: `5ba7ef744fb3fd706ae9e1bbf4e114f26278a561`;
- stale semantic-family removal: `9a5ff38ac564c66526c04db6dbb41b09d91f8474`.

Visual run #130 / `33473546907`:
- success;
- `commercial refresh tests: 3 passed`;
- `fixed package purchase option tests: 19 passed`;
- `PRIORITY_RANKING_VALIDATION=PASS`;
- `ai_queue=147`, proving commercial/package refresh does not wait for semantic queue completion;
- final item count: `442`;
- package qualifying: `8`;
- strict-saving packages: `7`;
- verified-equivalence packages: `1`;
- cards touched by packages: `19`;
- `PACKAGE_VISIBLE_CARDS=19`;
- `PACKAGE_RANKING_DRIVERS=15`.

Visual commit:
- `15db361d25bdb16693bc080f1bdbbb3b71235371`.

Deploy #171 / `33473567370`:
- success on that exact visual commit;
- actual Pages artifact `9787352509` inspected.

### BioShock acceptance from deployed Pages artifact

Current deployed values:
- BioShock® 2: `74 ₽`;
- BioShock Infinite: `182 ₽`;
- covered standalone total: `256 ₽`;
- BioShock: The Collection: `265 ₽`;
- delta: package `+9 ₽` versus those two covered visible games;
- `savings_rub=-9`;
- `savings_percent_vs_standalone=-3.5`;
- `strict_current_price_savings=false`;
- `comparison_source_aligned=true`;
- `uses_verified_purchase_equivalence=true`;
- both BioShock cards correctly keep `purchase_route=standalone` at this price.

This is intentional: the package is now visible because its membership is relevant, but it does not falsely increase rank when it currently costs more than the two covered visible games separately. If fresh prices later make the package route better, the next deterministic commercial refresh will automatically recalculate its purchase score and rank without waiting for a new Taste run.

## Diagnostic route

For a future report that a package is missing or has stale value:
1. Check current visual workflow log for `commercial refresh tests`, `PACKAGE_VISIBLE_CARDS`, `PACKAGE_RANKING_DRIVERS`, `package_equivalence` and `ai_queue`.
2. For the specific game, inspect bounded ranking lookup first.
3. If package detail is needed and the generated review/current JSON is too large for the GitHub connector, inspect the latest successful `github-pages` artifact; this was the reliable proof route for BioShock.
4. If package membership is absent, check exact appids and `config/purchase_equivalence_overrides.json`; never infer edition equivalence from the title.
5. If package is visible but does not drive ranking, compare `strict_current_price_savings`, standalone/package purchase scores and practical price ceiling before treating it as a bug.
