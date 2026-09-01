# RANK-014 — Commercial freshness is independent of Taste freshness

Date: 2026-09-01
Status: implemented and production-validated

## Decision

The accepted semantic/Taste snapshot and the current commercial snapshot are allowed to have different source timestamps.

A deterministic visual refresh must be able to update current offer state, prices, discount, price-history classification, fixed-package economics and the final purchase/ranking component **without rerunning or rewriting Taste**.

The required producer order is:

1. preserve the accepted semantic/Taste card fields;
2. refresh current standalone commercial fields from the current GitHub-owned commercial artifacts;
3. calculate fixed-package alternatives on that same commercial source;
4. run exactly one canonical final `FINAL-PRIORITY-RANKING-V2` pass;
5. publish/deploy.

## Why

Taste is intentionally price-blind and reusable. A Steam sale or package price can change independently of whether the game itself became a better or worse fit for the user. Requiring a fresh semantic evaluation before a new commercial ranking would couple two independent concerns, delay correct purchase advice and unnecessarily consume semantic work.

Example: a game can remain exactly the same semantic fit while a fixed package changes from worse value to excellent value. The purchase score and rank should react to the price change immediately; the Taste score should not change.

## Provenance boundary

Do not overwrite semantic provenance merely to make source timestamps match.

Canonical fields:
- `source_mailing_updated_at_utc` — semantic/Taste snapshot represented by the card;
- `commercial_source_mailing_updated_at_utc` — current deterministic commercial scope used for offer/package ranking;
- `commercial_store_observed_at_utc` — observation time for current Store data.

Fixed-package source alignment is checked against the **commercial** source when present, not against the older semantic source.

## Commercial refresh scope

`scripts/refresh_visual_commercial_fields.py` may update:
- standalone offers;
- current/original KZT and RUB prices;
- discount percent;
- sale end;
- historical minimum display and history quality;
- current offer links;
- current visibility when an old semantic card no longer exists in the current complete family graph or no longer has an active offer.

It must not recalculate or rewrite:
- `fit` / `source_fit`;
- normalized `taste_factors`;
- semantic reasons / `why_fit`;
- semantic risks;
- semantic model binding.

Regression diagnostics explicitly assert:
- `taste_recalculated=false`;
- `semantic_fields_rewritten=false`.

## Stale-family rule

If an accepted old semantic card is absent from the current **complete** family graph, retaining its old price would be misleading. The card is therefore removed from the current storefront and recorded in:
- `commercial_refresh.removed_stale_family_count`;
- `commercial_refresh.removed_stale_family_ids`.

This is a commercial visibility decision, not a new semantic judgment.

## Fixed packages

After fresh standalone commercial refresh, `scripts/apply_fixed_package_purchase_options.py` calculates package economics using the refreshed current KZT standalone prices.

The scorer then compares:
- `standalone` purchase route;
- eligible `fixed_package` purchase route.

Taste remains unchanged. Package value can change final `purchase_score`, `total_score` and `priority_rank` only through the canonical purchase/ranking policy.

## Rejected alternatives

- Wait for all new Taste work before updating prices/rank: rejected because commercial facts are independent and can become stale while semantic work is queued.
- Rerun Taste whenever price changes: rejected because Taste must remain price-blind and reusable.
- Rewrite semantic source timestamp to current commercial source: rejected because it would falsify provenance.
- Keep stale commercial data for semantic cards missing from the new complete family graph: rejected because the storefront would advertise outdated purchase facts.
- Add a second UI-side or post-ranking package sort: rejected; the UI remains display-only and the final rank remains one producer-owned canonical pass.

## Production proof

Implementation:
- fresh commercial refresh merge `5ba7ef744fb3fd706ae9e1bbf4e114f26278a561`;
- stale-family follow-up merge `9a5ff38ac564c66526c04db6dbb41b09d91f8474`.

Visual run #130 / `33473546907`:
- success;
- `commercial refresh tests: 3 passed`;
- `fixed package purchase option tests: 19 passed`;
- `PRIORITY_RANKING_VALIDATION=PASS`;
- build completed while `ai_queue=147`;
- 442 current cards after removing 3 stale semantic families;
- 19 package-visible cards;
- 15 package ranking drivers.

Visual commit:
- `15db361d25bdb16693bc080f1bdbbb3b71235371`.

Deploy:
- #171 / `33473567370` success;
- Pages artifact `9787352509` inspected.

BioShock acceptance on deployed artifact:
- BioShock 2 74 ₽ + BioShock Infinite 182 ₽ = 256 ₽;
- BioShock: The Collection = 265 ₽;
- package delta = +9 ₽, so it is visible but does not drive ranking now;
- source-aligned comparison is true;
- verified purchase equivalence is true;
- future deterministic price refreshes can change this purchase decision without waiting for Taste.

## Main implementation points

- `scripts/refresh_visual_commercial_fields.py`
- `scripts/apply_fixed_package_purchase_options.py`
- `scripts/build_final_visual_payload.py`
- `scripts/priority_ranking.py`
- `scripts/test_commercial_refresh.py`
- `scripts/test_fixed_package_purchase_options.py`
- `.github/workflows/build-daily-visual-payload.yml`
- `data/production/visual/current.json`
- `data/production/visual/ranking_review.jsonl`
