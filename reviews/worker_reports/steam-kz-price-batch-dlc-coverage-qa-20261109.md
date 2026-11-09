# QA: Steam KZ DLC completeness vs price-only batching

## Authority and inputs
- User request: "Убедись" following approved bounded 30-AppID price comparison; QA only, no implementation/cutover permission.
- Repository: kentrap2011-hub/steam-kz-deals-2; base main SHA d99ce24fce32ecab076f02c6039353d3be1de343.
- [Prior live canary PR #423](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/423); [successful Action 42612198610](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42612198610).
- Baseline complete real source: [main run 42601207552](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42601207552), production code SHA 9b4b0668438c20b39a48302acd27ddb3250ff41c.
- Source of exact current behavior: [scripts/steam_targeted_paid_lanes.py](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/d99ce24fce32ecab076f02c6039353d3be1de343/scripts/steam_targeted_paid_lanes.py#L389-L585). Existing regression cases in scripts/test_steam_targeted_paid_lanes.py, especially check_nested_dlc_exact_parent_proof.

## Frozen confirmed real observations
Production manifest from completed collector: complete=true; 365 verified eligible bases; 1,385 unique related DLC candidate AppIDs, 1,386 full child appdetails lookups including one canonical-game alias; **one genuinely observed nested intermediate, one nested relation edge, one nested child**; 528 accepted sale DLC; 857 excluded DLC; relation_complete=true. The manifest is aggregate and does not persist 1,751 full raw responses: it **cannot** prove which actual nested item would be omitted by an alternative that was not run.

Prior live canary: 30 full individual HTTP200 GETs and 1 batched price_overview HTTP200 GET with cc=kz; 27/27 KZT-priced offers matched exactly on initial, final and discount; three IDs 235960, 488140, 2819760 had no price but *different response shapes* (full data object without price vs batch lacking data object). Strict normalization was 27/30. The batch did not return the type, child dlc list or fullgame parent fields required to establish ancestry. Thirty paced individual requests consumed 26.244 seconds, one filtered batch service time was 0.234 seconds; this is NOT a measured whole-collector acceleration.

## Deterministic source-level counterexample and CI acceptance
This PR adds one deterministic test to scripts/test_steam_targeted_paid_lanes.py and invokes the unmodified real targeted.discover_dlc_for_bases through in-memory fake fetch. No Steam request. Synthetic records:

- Root App_2820 has two direct children, App_201310 and App_600.
- App_201310 is an **unpriced** DLC with immediate fullgame parent 2820 and lists App_601.
- App_600 is an eligible direct discounted DLC (KZT, 85% discount).
- App_601 is an eligible nested discounted DLC (KZT, 85%) whose immediate fullgame parent is App_201310.

Assertions:
1. Full metadata returns App_600 and App_601, and verified chain 2820 -> 201310 -> 601.
2. A lossy intermediate that retains **every other metadata field** but omits only App_201310 child dlc relation returns **only App_600**. The eligible App_601 silently disappears. This is a stronger counterexample than simply omitting the entire unpriced item.
3. An otherwise priced nested App_601 without its fullgame identity fails closed with missing nested parent proof.
4. An App_601 claiming an unrelated fullgame 999999 is excluded, rather than attributed to the listed root.
5. A third-hop child beyond the allowed two-hop boundary fails closed instead of silently passing.

All these checks are entirely synthetic but execute the **real unmodified production discovery function**. They prove price-only response fields cannot supply the current relation/identity information, even when price fields match exactly, and demonstrate that one missing child relation is enough to lose an eligible paid DLC. The real complete main snapshot's one nested descendant confirms nested topology is present today; it does NOT prove that an actual offer was lost during the previous price canary (the trial did not change production).

## Safety decision
**QA_VERDICT: BLOCKED_UNSAFE_TO_REPLACE_FULL_DLC_APPDETAILS_WITH_PRICE_ONLY_BATCH.**

Safely keeping all obligatory full metadata GETs and adding batch prefetch is possible in principle, but saves **zero** mandatory DLC relationship GETs and adds network work. To achieve actual request reduction, a separately verified current and complete relation graph source or a deliberately revised completeness contract is needed. A safe future proposal must account for games, Sub packages, the entire authorized DLC depth, exact fullgame chains, aliases, missing/unpriced intermediates, currency KZT/price/discount, third-hop detection, unknown/errors and source date drift. It requires full old/new frozen-snapshot A/B of all App_/Sub_/DLC IDs, not just 30 prices.

**What this QA cannot certify:** the exact loss count of a hypothetical optimized collector for the current live production day; no raw full response corpus was archived, and no new full A/B collection was authorized. No claim of zero lost games or successful optimization is made.

## Change scope
Only one deterministic regression change in scripts/test_steam_targeted_paid_lanes.py and this QA report; existing PR-only steam-test.yml regression executes with collector disabled. No collector, cache, manifest, KZ validation, parent rules, 180 starts/300s, scheduler, state, data, semantic workers, production or main modification.
