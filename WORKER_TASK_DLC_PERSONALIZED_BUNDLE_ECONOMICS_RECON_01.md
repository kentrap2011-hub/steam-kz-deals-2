# WORKER TASK — DLC + PERSONALIZED BUNDLE ECONOMICS RECON 01

Task ID: `dlc-personalized-bundle-economics-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/dlc-personalized-bundle-economics-recon-01.md`

## User request

Expand paid-deal discovery/economics in two related directions.

### A. DLC when the base game is already owned

If the user owns the base game, relevant paid DLC / expansions / season-pass style content should be eligible for deal consideration under explicit ownership/value rules.

The system must not blindly recommend DLC when the required base game is not owned.

### B. A game can be cheaper through a bundle/package even when the standalone game has no useful discount

For a target game, do not inspect only its standalone discount.

If the game is included in a bundle/package whose actual payable price makes acquiring the target materially cheaper, that package route must be considered.

This is especially important when the user already owns other items in a personalized bundle and the storefront actually reduces the payable bundle price because of those owned items.

Example intent:
- standalone target game: no discount or weak discount;
- bundle contains the target plus games/content the user already owns;
- storefront's personalized bundle semantics reduce the actual payable price;
- target can therefore be acquired much more cheaply through the bundle.

## Known current state

`reviews/worker_reports/compact-purchase-options-01.md` confirms current UI/producer contracts already understand:
- standalone purchase options;
- producer-selected `fixed_package` route;
- fixed-package composition/economics;
- `purchase_route` and `package_score_delta_vs_standalone`.

But it also explicitly confirms:
- dynamic/personalized `Complete-the-Set` packages are currently excluded from fixed-package eligibility;
- package economics remain producer-owned, not browser-calculated.

Older Taste/application rules also treated DLC/Season Pass as non-independent candidates unless separate ownership/value rules were defined.

Therefore this request is an extension of existing purchase economics, not a request to redesign the UI from scratch.

## Goal

Map the exact current ownership -> store offer/package -> economics -> candidate -> ranking/output path and define safe bounded implementation(s) for:

1. owned base game -> relevant DLC can become a paid purchase candidate;
2. target game -> standalone versus package/bundle routes are compared using authoritative actual payable economics;
3. owned items reduce bundle cost only when the storefront's real purchase semantics do so.

## Required checks

1. Identify current authoritative Steam ownership source for:
   - owned base apps;
   - owned games/content used in package economics;
   - whether DLC ownership is distinguishable where needed.
2. Identify current source/contract for DLC relationships:
   - DLC -> required base game;
   - expansion/season-pass/package relationships;
   - current price/discount/evidence.
3. Determine the minimum safe rule for DLC candidate eligibility when the required base game is confirmed owned.
4. Distinguish at least these purchase structures:
   - standalone app/DLC;
   - fixed public package/bundle where owning duplicates does **not** necessarily lower payable price;
   - personalized/dynamic `Complete-the-Set` style bundle where storefront semantics can reduce payable price based on ownership.
5. Establish an authoritative source-owned way to obtain the **actual personalized payable price** for the user's region/account context when such a bundle exists. Do not infer it by subtracting list prices unless the storefront contract itself makes that calculation authoritative.
6. Determine whether personalized price is obtainable in current GitHub-owned unattended production flow. If account/session-only access is required, say so explicitly and fail closed rather than inventing economics.
7. Define the correct economic comparison for target acquisition:
   - standalone payable price;
   - package payable price;
   - incremental unowned entitlements acquired;
   - target included with exact identity;
   - ownership already held;
   - no double counting.
8. Handle the user's key case explicitly:
   - standalone target has no/weak sale;
   - package route has a materially lower actual payable acquisition cost;
   - package route must be able to make the target commercially interesting.
9. Do not pretend the entire package price is the price of the target if multiple genuinely unowned valuable items are acquired. Define truthful attribution/explanation semantics.
10. Determine how bundle value interacts with current Taste policy: commercial/package value may affect purchase timing/value, but must not silently rewrite personal fit.
11. Identify exact current files/contracts/producers requiring change.
12. Decide whether implementation should be split into two bounded tasks:
   - DLC candidate discovery/ownership eligibility;
   - personalized bundle/Complete-the-Set economics;
   if their authorities or risks differ materially.

## Required regressions

At minimum specify tests for:

1. base game confirmed owned + relevant discounted DLC -> DLC is eligible for consideration;
2. base game not owned/unknown + DLC alone -> no normal DLC recommendation;
3. target base game has no standalone discount + authoritative package route gives better actual acquisition economics -> package route can surface it;
4. owned items reduce payable price only for package types whose storefront semantics actually support that behavior;
5. fixed package does not receive an invented ownership subtraction;
6. stale/unknown personalized payable price -> fail closed / do not claim savings;
7. owned target itself is not recommended again merely because it is inside a bundle;
8. package containing multiple useful unowned items has truthful value attribution and no double counting;
9. existing standalone/fixed-package behavior remains unchanged when no new personalized/DLC case applies.

## Boundaries

READ-ONLY / RECON only.

Do NOT:
- change production code/data;
- calculate personalized price in the browser;
- assume every Steam bundle is Complete-the-Set;
- subtract owned item list prices from a fixed package as a guess;
- recommend DLC without proving base ownership/dependency;
- change Taste weights/ranking policy in this recon;
- touch Epic/GOG giveaway region logic;
- create account-session scraping or a new scheduler without explicit Director approval.

## Done when

Save:
`reviews/worker_reports/dlc-personalized-bundle-economics-recon-01.md`

Include:
1. Task
2. Current ownership and purchase-economics path
3. Current fixed-package capability
4. DLC gap
5. Personalized Complete-the-Set gap
6. Authoritative personalized-price feasibility
7. Proposed DLC eligibility semantics
8. Proposed package acquisition-economics semantics
9. Ownership/double-count protections
10. Regression plan
11. Exact implementation files/contracts
12. Recommended implementation split/order
13. Status
14. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_user_decision`
