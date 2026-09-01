# RANK-013 — Fixed Steam package can determine purchase score

Date: 2026-08-31
Status: implemented and production-validated

## Decision

For a game with an eligible fixed Steam Store Package (`Sub_`), the final scorer evaluates two alternative purchase routes:

1. `standalone` — the normal per-game purchase score;
2. `fixed_package` — the value of buying the eligible fixed package that covers multiple currently visible base-game families.

The final purchase component uses whichever transparent route has the higher score. A tie keeps `standalone`.

The package route affects only purchase/value. It must never increase or rewrite the price-blind Taste score.

## Why

A low standalone game price is useful, but it is not always the best purchase available. If one suitable game costs about 150 ₽ while a fixed package costs about 300 ₽ and contains four suitable/currently visible games, the package can be a materially better use of the same purchase budget. Ranking should reflect that practical multi-game value instead of treating the package as display-only metadata.

## Package route inputs

The package score is derived from package-specific economics rather than adding another bonus on top of standalone economics:
- savings versus the current total price of the covered visible games bought separately;
- effective package price per covered visible game;
- number of currently visible base-game families covered by the package.

The exact numeric maxima/bands and practical package-price ceiling belong only to `config/final_ranking_policy.json`.

## Eligibility boundary

Package scoring is fail-closed and only applies when the purchase option already satisfies the fixed-package contract:
- fixed `Sub_` only;
- at least two currently visible base-game families;
- coverage based on actual included appids/canonical family membership;
- no original/remaster equivalence guessing;
- strictly cheaper than the current standalone total;
- each family counted once;
- unknown extra content contributes zero assumed value;
- dynamic/personalized Complete-the-Set `/bundle/` excluded;
- package total price must also satisfy the practical scoring ceiling in the ranking policy.

## Rejected alternatives

- Display-only package advice: rejected because it hides a real difference in purchase value from ranking.
- Add a package bonus on top of the existing standalone purchase score: rejected because it can double-count price/savings value.
- Let package value affect Taste: rejected because Taste must remain reusable and price-blind.
- Score personalized/dynamic Steam bundles: rejected because their price is account-dependent and not a stable producer-owned fact.

## UI acceptance

A package that exists only in JSON is not sufficient acceptance. The deployed card must show a distinct `🎁 Выгодный набор Steam` block with package price, covered games, standalone total, savings, approximate price per game and an explicit Steam action.

## Production proof

- implementation merge: `a86b0e793b445c5d1af54ac08ba00528be946f6e`;
- visual run #111 / `33423352245`: success;
- fixed-package tests: 12 passed;
- 17 visible cards with package advice; 15 package routes actually drove purchase score;
- example: `FlatOut 2` standalone purchase score 22 -> package score 36 (+14);
- example: `The Night of the Rabbit` 22 -> 40 (+18);
- package-aware visual commit: `66c00e9e389691be885123a9dd4e48663c41d5ad`;
- deploy #151 / `33423389598`: success;
- deployed Pages artifact `9769779423` verified to contain both highlighted package UI and package-aware payload;
- later visual run #113 / `33437077173` kept package regressions green and still reported 17 visible package cards / 15 package ranking drivers.

## Main implementation points

- `config/final_ranking_policy.json` (`RANK-013`, `score_model.purchase.fixed_package`)
- `config/fixed_package_purchase_option_contract.json`
- `scripts/build_fixed_package_purchase_options.py`
- `scripts/apply_fixed_package_purchase_options.py`
- `scripts/build_final_visual_payload.py`
- `scripts/priority_ranking.py`
- `scripts/test_fixed_package_purchase_options.py`
- `scripts/validate_priority_ranking.py`
- `.github/workflows/validate-package-purchase-value.yml`
- `.github/workflows/build-daily-visual-payload.yml`
- `web/app.js`
- `data/production/visual/ranking_review.jsonl`
