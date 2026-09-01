# Cross-platform giveaway IMPLEMENT 01

Task: `cross-platform-giveaway-implement-01`  
Date: 2026-09-01

## Task

Implemented the first repository-side version of a storefront-neutral Tier-1 claim-to-keep giveaway data plane for Kazakhstan:

- canonical contract: `config/cross_platform_giveaway_contract.json` (`CROSS-PLATFORM-GIVEAWAY-V1`);
- common normalization / classification / freshness / grouping core: `scripts/giveaway_core.py`;
- bounded HTTP helper: `scripts/giveaway_http.py`;
- hardened Steam adapter: `scripts/giveaway_steam.py`;
- Epic Games Store KZ adapter: `scripts/giveaway_epic.py`;
- GOG KZ adapter: `scripts/giveaway_gog.py`;
- canonical aggregator/writer: `scripts/giveaway_production.py`;
- deterministic regression coverage: `scripts/test_giveaway_production.py`;
- production ownership regression extended so the existing Steam collector cannot delete/overwrite `data/production/giveaways/**`.

The intended canonical output family is:

- `data/production/giveaways/index.json`
- `data/production/giveaways/v1/current.json`
- `data/production/giveaways/v1/audit.jsonl`

The existing Steam `data/production/freebies.tsv` / `freebies_index.json` remain owned by the Steam collector and are read only as Steam giveaway candidates. No second writer for those paths was introduced.

## Architecture / ownership

GitHub / GitHub Actions remains the control plane. `scripts/giveaway_production.py` is the intended single writer for `data/production/giveaways/**`. No recurring ChatGPT scheduler was added and paid ranking / Taste semantics were not changed.

## Sources implemented

### Steam

The existing KZ catalog scan is reused only for candidate discovery. `0 KZT + positive discount` is no longer sufficient for cross-platform publication. The new adapter performs bounded first-party Steam appdetails/store-page validation and requires full-game type, KZ availability, permanent-claim evidence, zero final price and a known future promotion deadline before acceptance.

### Epic Games Store

Implemented KZ discovery against the existing first-party storefront promotions backend with explicit `country=KZ`, `allowCountries=KZ`, active-window checks, BASE_GAME-only handling, stable namespace/offer identity, mystery/upcoming/expired rejection and strict schema guards.

### GOG

Implemented bounded KZ zero-price discounted candidate discovery against the first-party catalog backend with stable product identity, full-game/complete-edition classification, first-party product-page deadline validation and fail-closed temporal semantics.

## Production result

A canonical cross-platform production snapshot has **not yet been generated** on `main`.

Current verified repository state:

- `data/production/giveaways/` does not yet exist on `main`;
- therefore there is no accepted current cross-platform KZ offer count to report yet for Steam / Epic / GOG;
- the legacy Steam candidate artifact still exists separately and, at the last inspected snapshot, contained one `100%` candidate (`App_5004030`), but that row is **not** treated as an accepted cross-platform giveaway without the new validator.

Source production status for this implementation report:

- Steam: adapter implemented; live canonical giveaway result not yet produced;
- Epic: adapter implemented; live canonical giveaway result not yet produced;
- GOG: adapter implemented; live canonical giveaway result not yet produced.

No production rows were manually seeded.

## Changes

Implementation commits, in order:

- `99786c2958e1c105b087530bd821e46ffe5b77ee` — canonical contract;
- `9d4056d6902d939199023368807cd1f18cc40682` — normalization/classification core;
- `922793afacfdf0fa6874e22e7750f7be174423f8` — HTTP helper;
- `fe8e36c403ce3d646423762a7f84a75582394415` — Steam hardening adapter;
- `7fd21e92824d21c7c17125388cbe079bb3cd888e` — Epic KZ adapter;
- `a8ebabf16afaa06026eb81bb2226f0f23035f107` — GOG KZ adapter;
- `5a13bb07824006ef7f6c48273b2d13c5ad5a2285` — canonical producer;
- `7e99dd24270175b41c9ee22b8b6472e083a3ee91` — deterministic giveaway tests;
- `5d87c8358014d10c4828c8f94ed591622b671732` — ownership regression update;
- `d902c3fc80c04e4ec13f929cfa5f81730cc673db` — tighter fail-closed classification/freshness validation.

## Validation

Deterministic test file currently contains coverage for:

- true active claim-to-keep fixtures for Steam / Epic / GOG;
- permanent F2P;
- free-weekend/access-only;
- DLC/non-game;
- upcoming and expired offers;
- unknown KZ region;
- source schema failure;
- unknown ownership semantics;
- same-game cross-store grouping without offer loss;
- similar-title non-merge;
- required-source failure => incomplete snapshot;
- stale offer removal.

However, there is **no confirmed GitHub Actions test/run ref yet** for the current giveaway implementation. Repository checks for the current implementation commits did not return a workflow run, and the canonical giveaway artifact path is still absent. Therefore this report does not claim that the deterministic suite or live production path has passed CI.

Workflow/run refs: `none yet for current giveaway implementation`.

## Unresolved

The producer has not yet been integrated/executed far enough in the existing GitHub-owned production workflow to produce and validate the live `data/production/giveaways/v1/current.json` snapshot.

## Status

`needs_fix`

## Recommended next step

Integrate `scripts/giveaway_production.py` plus its deterministic test into the existing GitHub-owned daily production workflow, run that canonical workflow once, and record the real Steam/Epic/GOG source health and accepted-offer count from the generated `data/production/giveaways/v1/current.json`.
