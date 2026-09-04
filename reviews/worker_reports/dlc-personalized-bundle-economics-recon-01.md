# DLC + Personalized Bundle Economics Recon 01

Task ID: `dlc-personalized-bundle-economics-recon-01`  
Mode: `READ-ONLY / RECON`  
Observed: `2026-09-04`

## 1. Task

Map the existing GitHub-owned Steam purchase-economics path and define the smallest safe future changes for two related user scenarios:

1. paid DLC / expansion / season-pass-like content may be considered when its required base game is **confirmed owned**;
2. a target game may be materially cheaper to acquire through a package/bundle than through its standalone offer, including Steam `Complete The Set` where the **actual account-specific payable price** is reduced because some included items are already owned.

This recon does not modify production code/data, does not create browser-side price logic, does not introduce Steam account-session scraping, and does not change Taste weights.

## 2. Current ownership and purchase-economics path

### 2.1 Current deterministic path

The current paid path is approximately:

```text
Steam KZ sale discovery
  -> shortlist / mailing candidates
  -> IStoreBrowseService/GetItems current Store snapshot
  -> exact content metadata / DLC-parent relationships
  -> mechanical content rules
  -> purchase-family graph
  -> price-blind Taste resolution
  -> commercial/deal scenarios
  -> visual payload
  -> fixed-package enrichment
  -> one final producer-owned ranking pass
  -> display-only UI
```

The existing pre-AI workflow explicitly runs `build_fixed_package_purchase_options.py` as part of the atomic deterministic payload and persists `data/production/pre_ai/fixed_package_options.json`. The daily visual workflow validates the fixed-package route, builds the canonical visual payload, and exports `purchase_route`, `standalone_purchase_score`, `fixed_package_purchase_score`, and `package_score_delta_vs_standalone` in the producer-owned ranking review.

Therefore this request is an extension of the existing purchase route. A second UI/browser calculator or parallel purchase-ranking mechanism would be architecturally wrong.

### 2.2 Current ownership source

There is **no current canonical owned-entitlement snapshot in the production path**.

The current ChatGPT payload producer loads the canonical Steam wishlist as context, and both `config/mailing_policy.json` and `config/content_eligibility_contract.json` explicitly state that wishlist is **not ownership proof**.

The canonical taste/profile repository identifies the Steam profile and wishlist source, but the bounded current paid pipeline has no `GetOwnedGames` producer, no owned-AppID artifact, and no Steam ownership credential wiring in the relevant pre-AI/daily workflow path.

Valve's authoritative generic ownership source for base games is `IPlayerService/GetOwnedGames`: it returns games owned by the player when owned-game visibility permits, and requires a Steamworks Web API authentication key. This is a viable future **base-game ownership** input if credentials are provisioned and the response is complete.

Valve documents stronger per-AppID ownership checks (`ISteamUser/CheckAppOwnership`, `BIsSubscribedApp`) for applications/DLC, but those APIs are publisher/game-context mechanisms, not a proven general consumer API for arbitrary third-party DLC across the user's whole library. Consequently a generic complete DLC-ownership ledger is **not currently proven available** to this unattended project through the existing public path.

### 2.3 Current source-owned DLC relationship

The relationship itself is already strong and deterministic:

- `IStoreBrowseService/GetItems` maps Steam type `4` to `dlc`;
- `related_items.parent_appid` is stored as `fullgame_appid`;
- the older first-party `appdetails` path also exposes `fullgame.appid`;
- `build_pre_ai_content_rules.py` records that exact `base_appid`;
- `build_pre_ai_family_graph.py` attaches DLC to an exact base-game family when the base is present, or creates an `external_base_addon` family with the exact required base AppID when it is not.

Thus **DLC -> required base game is already source-proven**. The missing fact is ownership, not dependency identity.

## 3. Current fixed-package capability

The existing fixed-package producer is intentionally narrow and already has useful safety properties.

### 3.1 Supported structure

`config/fixed_package_purchase_option_contract.json` and `scripts/build_fixed_package_purchase_options.py` support Steam fixed `Sub_` packages only:

- source: `IStoreBrowseService/GetItems`;
- region: KZ;
- exact package membership;
- fixed current package price;
- exact/verified purchase equivalence only;
- verified top-level DLC/content attached to covered base games;
- no guessed value for unknown/unpriced/nonpersonalized content.

Rows are explicitly marked:

```text
fixed_price_semantics = true
personalized_price = false
dynamic_bundle_ids_supported = false
personalized_complete_the_set_supported = false
```

### 3.2 Existing economic comparison

For qualifying fixed packages the producer compares:

```text
current standalone price of each distinct covered visible base-game family
+ verified priced top-level DLC/content attached to those covered games
vs
fixed package final price
```

The fixed route is eligible to drive the purchase score only when the existing ranking rules are satisfied (including strict current-price savings, practical package price ceiling, and minimum visible coverage). The scorer chooses the higher transparent route score between standalone and eligible fixed package; ties remain standalone.

### 3.3 Existing double-count protections

Important protections already exist and should be retained:

- a base-game family is counted once even when several AppIDs map to that family;
- edition/substitution equivalence is never guessed from title;
- unpriced content contributes zero monetary value;
- content for a Taste-excluded/noncovered game is visible as package composition but contributes zero personalized value;
- a DLC entitlement gets a standalone monetary value only when Steam proves a fixed `Sub_` that grants **exactly that one top-level AppID**;
- a Season Pass / shared acquisition package that grants multiple top-level DLC AppIDs is not treated as separate standalone prices for every constituent, preventing recursive constituent double counting.

### 3.4 Important current limitation: package enrichment cannot rescue an absent target

The existing fixed-package enrichment operates over the current mailing/visible game set. Current paid discovery is sale-oriented and requires an active positive discount before a normal app becomes a sale candidate. The fixed-package producer then starts from current mailing AppIDs and its ranking enrichment attaches a package only to already-visible game families.

Therefore the key requested case is **not currently covered**:

```text
target standalone: no useful sale / no sale candidate
package route: materially better acquisition transaction
```

A downstream fixed-package enrichment cannot surface a target that never entered the candidate/family pipeline. The package/bundle implementation must allow a source-proven purchase route to seed the exact contained target AppID into the normal Taste-first candidate path; price may make that target commercially interesting only **after** its independent Taste eligibility is resolved.

## 4. DLC gap

The exact DLC gap is not DLC detection. It is **ownership eligibility**.

Today:

- Steam can identify a row as DLC and identify its exact base AppID;
- the content contract can keep a DLC candidate conditionally;
- the family graph can attach it to a base family or create an external-base-addon family;
- but an external addon is currently resolved using semantic/profile “base support” logic rather than a deterministic proof that the user owns the required base game.

This does not satisfy the new user rule. Liking the base game, having it in the same Taste run, having it on wishlist, or having profile evidence about it is not the same fact as **owning** it.

There is also a second, smaller limitation: the current sale discovery has title heuristics such as `expansion`, `season pass`, `story DLC`, etc. Those heuristics may improve recall, but they cannot be the final authority for dependency/ownership. Final eligibility must use Steam content type + exact parent/package relationships.

## 5. Personalized Complete-the-Set gap

The personalized gap is broader than “one missing price field”.

Current production supports fixed `Sub_` purchase options and explicitly excludes dynamic/personalized bundle IDs. It does not currently model:

- Steam `bundle/<bundleid>` identity/type;
- `Complete The Set` versus `Must Purchase Together` semantics;
- account-owned versus account-unowned included packages/apps;
- account-specific bundle purchase eligibility;
- account-specific payable total;
- a source-bound personalized-price freshness receipt.

Valve's official bundle contract distinguishes two bundle types:

### Complete The Set

The customer pays for and receives only items not already in the account. The bundle discount is applied to packages not already owned. The payable amount is therefore account-dependent.

### Must Purchase Together

The customer can purchase the bundle only if they own **none** of the contained products. Ownership overlap does not create a cheaper personalized price; it makes that bundle unavailable for self-purchase.

This distinction must be proven from Steam-owned source evidence. A bundle name containing words such as “Complete the Set” is not sufficient authority.

Fixed `Sub_` packages are a third structure: they remain fixed-price SKUs/licenses. Existing owned components must **never** be subtracted manually from a fixed `Sub_` price.

## 6. Authoritative personalized-price feasibility

### 6.1 What is authoritative

Valve's Steamworks Bundles documentation is authoritative for the semantics: a Complete The Set purchase is calculated from the packages the purchasing account does not already own, with the bundle discount applied to those remaining packages.

For the **actual payable number**, the authoritative source is Steam's own **account-context storefront purchase offer** for that bundle — the authenticated Steam Store bundle/cart context that renders the account's current payable `Your cost` / purchase amount for that account and region.

A public/logged-out bundle page can prove bundle membership and public prices, but it cannot prove this user's actual Complete The Set payable amount because the amount depends on account ownership.

### 6.2 What is not sufficient

The following are not acceptable personalized price authorities:

- `fixed package price - prices of owned items`;
- sum of current list prices of apparently unowned items multiplied by the documented discount;
- a browser/UI calculation;
- a cached generic public bundle page;
- assuming that every Steam Bundle is Complete The Set;
- assuming owned AppIDs from titles or wishlist.

Even though Valve documents the mathematical semantics, the task specifically requires the **actual current payable transaction**. The producer must consume the Steam-owned account result, not reproduce a guessed checkout calculation.

### 6.3 Can the current GitHub-owned unattended pipeline obtain it automatically?

**No, not with the current proven contract.**

The current StoreBrowse calls are unauthenticated KZ storefront calls with language/country/realm context and no account/session binding. They can authoritatively return public/fixed purchase options, but they do not prove an account-specific Complete The Set payable result.

No officially documented, account-independent Web API endpoint/field that returns an arbitrary consumer's Complete The Set checkout price was proven during this recon.

Therefore current unattended production must treat personalized payable price as **unknown** and fail closed for personalized savings/ranking.

An authenticated Steam Store account/session integration may be technically capable of obtaining the source-owned price, but introducing/storing/refreshing that account session is a new security/reliability boundary and is explicitly outside this recon. It requires Director approval before an implementation task may design session/cookie/auth handling.

If such access is ever approved, the producer must also prove source alignment:

- correct Steam account;
- intended store country/region;
- currency compatible with the KZ comparison contract;
- observation timestamp in the same commercial cycle;
- exact bundle ID/type;
- exact account-specific payable total.

A region/currency mismatch must make the personalized route ineligible for scoring rather than mixing unrelated prices.

## 7. Proposed DLC eligibility semantics

Minimum safe future rule:

### 7.1 Dependency gate

A normal paid DLC/expansion/season-pass-like candidate is eligible only when:

1. Steam source metadata proves it is relevant game content rather than soundtrack/artbook/cosmetic/non-game content;
2. Steam proves the required base AppID by exact `parent_appid/fullgame_appid`, or a package route proves exact DLC membership attached to that base;
3. the canonical ownership snapshot says that exact required base AppID is **owned = true**;
4. the DLC itself passes the existing price-blind Taste/content relevance rules appropriate for add-on content;
5. the current purchase route/discount is source-proven and commercially eligible.

If required-base ownership is `false` or `unknown`, normal standalone DLC recommendation is excluded/fails closed.

### 7.2 Ownership source

The smallest unattended base-game ownership producer can use Valve's `IPlayerService/GetOwnedGames`, integrated into the existing GitHub pre-AI cycle rather than a new scheduler, provided an approved Steam Web API key is provisioned and owned-game visibility allows complete retrieval.

The artifact should use exact AppIDs and record at minimum:

```text
source = Steam IPlayerService/GetOwnedGames
observed_at_utc
ownership_status = complete | unavailable | failed
owned_game_appids
```

Missing credentials, private/unavailable ownership details, malformed response, or stale snapshot => ownership unknown => DLC gate fails closed.

### 7.3 DLC ownership itself

Do not claim that `GetOwnedGames` is a complete arbitrary-DLC ledger; Valve documents it as a list of owned games. If an authoritative target-DLC ownership signal is independently available, `target_dlc_owned=true` must suppress the purchase recommendation. Otherwise the project must not invent target-DLC ownership from the base-game list.

A later authenticated account/store integration could potentially solve both duplicate-DLC and Complete The Set ownership state, but that is the higher-risk account-session task, not a prerequisite for proving the base-game gate itself.

## 8. Proposed package acquisition-economics semantics

The producer should model purchase routes explicitly, while preserving the existing single purchase-route owner.

### 8.1 Route types

At minimum:

```text
standalone_app_or_dlc
fixed_sub_package
steam_bundle_must_purchase_together
steam_bundle_complete_the_set_personalized
```

Each route must carry source-proven identity/type. Unknown bundle type is not allowed to receive ownership-adjusted economics.

### 8.2 Owned and unowned partition

For a personalized bundle, producer output should keep exact separately auditable sets:

```text
included entitlement/package identities
owned identities
unowned identities newly acquired by this transaction
target AppID exact inclusion evidence
actual account-specific payable total
```

Do not derive the payable total from those sets; they explain the Steam-returned total.

### 8.3 Target acquisition comparison

For an unowned target:

```text
standalone_payable = current source-owned standalone transaction price
route_total_payable = current source-owned package/bundle transaction total
```

If `route_total_payable < standalone_payable`, it is truthful to say:

> Spend X total to acquire the target through this route (plus N other new entitlements), versus Y for the target alone.

That can make the target commercially interesting even when its standalone discount is weak or zero, provided the target independently passes Taste/content eligibility.

However, if the bundle acquires multiple genuinely unowned valuable items, **do not label X as “the target's price”** and do not allocate an invented fraction of X to the target.

Recommended semantics:

```text
transaction_outlay_to_acquire_target = X
target_attributed_price = null when >1 new entitlement
additional_unowned_entitlements = [...]
route_total_saving_vs_target_standalone = Y - X   # only when X < Y
```

If the target is the only unowned entitlement in an authoritative Complete The Set transaction, the total personalized payable is also the incremental transaction amount required to acquire that target, and that can be stated explicitly.

If route total is more expensive than standalone target but contains additional useful unowned items, it may be a conditional multi-item value option, but it must not be described as a cheaper way to buy the target.

### 8.4 No-discount target rescue

To satisfy the key scenario, package/bundle purchase discovery must be able to create an exact **target acquisition candidate** before final commercial exclusion when an active source-proven route contains an otherwise absent/no-sale target.

The safe ordering is:

```text
source-owned active purchase route
  -> exact contained target AppID
  -> target enters ordinary content/Taste family pipeline
  -> Taste remains independent of package value
  -> after Taste include, compare standalone vs route economics
  -> producer selects commercial purchase route
  -> one final ranking pass
```

Do not directly inject a package-favored target into the final visual list merely because the route is cheap.

For Steam Bundles specifically, current project support for bundle-ID discovery/membership is not yet established. The Complete The Set implementation task must first prove a bounded Steam-owned bundle discovery/type/membership source; it must not broaden into an all-Steam bundle crawl.

## 9. Ownership / double-count protections

Required invariants:

1. **Exact identities only.** AppID/PackageID/BundleID and explicit purchase-equivalence overrides; never title similarity.
2. **Wishlist is never ownership.** Existing canonical rule remains.
3. **Base ownership is deterministic.** DLC recommendation requires exact base AppID owned=true; false/unknown fails closed.
4. **Owned target suppression.** A target already proven owned must not be surfaced again merely because a package contains it.
5. **Fixed Sub price is never ownership-adjusted manually.** Use the fixed source price exactly as returned.
6. **Must Purchase Together is not Complete The Set.** Any owned member means the account route is unavailable, not discounted by subtraction.
7. **Complete The Set uses only Steam's actual account payable.** No local reconstruction.
8. **Owned items have zero newly-acquired value.** They may explain why Steam's CTS total is lower but are not counted as newly obtained content.
9. **Each unowned entitlement is counted once.** Deduplicate exact grant identity when packages/bundle members overlap.
10. **Season Pass constituent protection remains.** Do not separately monetize constituents through the same multi-entitlement acquisition route.
11. **No target price allocation when several new items are acquired.** Keep transaction outlay and target-attributed price separate.
12. **Source-cycle alignment required.** Standalone and route economics must be current and region/currency aligned before a savings claim or score boost.
13. **Unknown personalized price = zero ranking influence.** It may be retained as non-economic discovery evidence, but no savings claim.
14. **Price cannot rewrite Taste.** Cheap package value changes only purchase/commercial route, timing/value and purchase score; personal fit remains the existing price-blind result.

## 10. Regression plan

Minimum future tests:

### DLC

1. exact base AppID owned=true + relevant discounted DLC + valid dependency -> DLC eligible for consideration;
2. base owned=false -> DLC excluded as normal purchase candidate;
3. base ownership unknown/stale/failed -> fail closed;
4. wishlist/base semantic support without ownership proof -> not sufficient;
5. DLC parent AppID missing/malformed -> fail closed unless independently proven standalone game-like content;
6. obvious soundtrack/artbook/cosmetic addon stays excluded;
7. current game/normal standalone behavior unchanged.

### Fixed package / bundle

8. existing fixed `Sub_` package retains exactly the current fixed price even when some contained AppIDs are in the owned set;
9. fixed package never subtracts owned item list prices;
10. Complete The Set with authoritative account payable and exact target inclusion may use that payable total;
11. same bundle with stale/unknown account payable -> no savings claim and no ranking boost;
12. Must Purchase Together with an already-owned member -> unavailable, not personalized cheaper;
13. unknown bundle type -> no ownership-adjusted economics;
14. target already owned -> target not re-recommended through bundle;
15. target standalone has no/weak sale + authoritative route total is lower -> route can seed target for normal Taste evaluation and, after Taste include, become the selected commercial route;
16. target fails Taste -> package price cannot rescue it;
17. route contains target + multiple unowned useful entitlements -> show total transaction outlay and extras, keep target-attributed price null, count each entitlement once;
18. target is the only unowned CTS entitlement -> account payable may be described as the incremental amount to acquire that target;
19. existing Season Pass constituent double-count regression remains green;
20. existing standalone/fixed-package behavior and ranking remain unchanged when no DLC ownership/personalized case applies.

## 11. Exact implementation files / contracts

### Task A — DLC ownership eligibility

Existing files that need bounded changes:

- `config/mailing_policy.json`
  - make ownership, not semantic base support, the purchase-eligibility authority for normal DLC;
  - preserve wishlist-not-ownership and Taste separation.
- `config/content_eligibility_contract.json`
  - add exact owned-base gate / fail-closed ownership status.
- `scripts/build_pre_ai_content_rules.py`
  - carry deterministic ownership requirement for DLC rows.
- `scripts/build_pre_ai_family_graph.py`
  - retain exact DLC-parent family binding but stop treating AI semantic base support as ownership proof.
- `scripts/build_pre_ai_chatgpt_payload.py`
  - ownership must be deterministic producer context, not a semantic `resolve_base_support_condition` substitute.
- `.github/workflows/build-pre-ai-store-snapshot.yml`
  - run ownership snapshot inside the existing nightly/pre-AI owner; no new scheduler.

Small new source artifact/contract is justified because ownership is a new factual input, not a competing purchase mechanism, e.g.:

- `config/steam_ownership_contract.json`;
- `scripts/build_steam_ownership_snapshot.py`;
- `data/production/pre_ai/steam_ownership_snapshot.json`.

The exact naming can be chosen in IMPLEMENT, but ownership must have one GitHub-owned canonical producer and fail-closed freshness/completeness semantics.

### Task B — package/bundle target acquisition + Complete The Set

Extend/migrate the existing purchase-option owner, not a parallel calculator:

- `config/fixed_package_purchase_option_contract.json`
  - evolve from fixed-Sub-only semantics to explicit route types while preserving fixed behavior;
- `scripts/build_fixed_package_purchase_options.py`
  - retain fixed Sub discovery; add source-proven Steam Bundle identity/type/membership only after its endpoint is proven;
  - consume authoritative personalized-price receipt when available;
- `scripts/apply_fixed_package_purchase_options.py`
  - partition owned/unowned entitlements; compare transaction outlay truthfully; preserve existing double-count guards;
- `scripts/steam_production.py` / the current paid candidate producer
  - allow an active exact package/bundle route to seed a contained target that has no useful standalone sale, without bypassing Taste;
- `config/final_ranking_policy.json` + `scripts/priority_ranking.py`
  - extend the existing single purchase-route selector to the new producer-proven route; do not change Taste weights;
- `scripts/test_fixed_package_purchase_options.py`;
- `scripts/test_package_complete_content_value.py`;
- `.github/workflows/build-pre-ai-store-snapshot.yml`;
- `.github/workflows/build-daily-visual-payload.yml` only for the existing producer/test wiring.

Do not add browser pricing code.

## 12. Recommended implementation split / order

**Yes — split into two bounded implementation tasks. Their authorities and risks differ materially.**

### IMPLEMENT A — DLC ownership eligibility first

Scope:

- establish the canonical base-game ownership snapshot using Valve `GetOwnedGames`;
- provision/read the approved Steam Web API credential in the existing GitHub-owned pre-AI workflow;
- enforce exact owned-base DLC eligibility;
- retain existing DLC dependency/content/Taste rules;
- fail closed on missing/private/stale ownership;
- no account-session scraping.

This is the lower-risk task and can be implemented independently once credential provisioning is approved.

### IMPLEMENT B — purchase-route expansion / Complete The Set second

Scope:

1. preserve all current fixed `Sub_` behavior;
2. add package/bundle-derived target seeding so an exact target can be considered even when standalone has no useful sale;
3. prove Steam Bundle ID/type/membership source;
4. for Complete The Set, use only an authoritative account-context payable result;
5. extend the existing producer-owned route comparison and final purchase-route selector;
6. no locally reconstructed personalized price.

This task has a hard decision gate: **current GitHub unattended production has no approved authenticated Steam Store account context that can prove actual Complete The Set payable price.** Before implementing account-personalized pricing, the Director must decide whether authenticated Steam account/session integration is allowed and under what credential/security model. Until then CTS economics stay unknown/fail-closed.

A useful fixed-package/no-standalone-sale rescue that does not require account personalization may be implemented within Task B before the authenticated CTS substep, provided membership and fixed payable price are source-proven.

## 13. Status

`needs_user_decision`

Recon itself is complete.

Reason for status: the DLC path has a bounded authoritative base-ownership candidate (`IPlayerService/GetOwnedGames`) but needs approved Web API credential provisioning. More importantly, actual Complete The Set economics are account-specific and the current unattended GitHub pipeline has no proven authenticated Steam storefront price source. The task explicitly prohibits designing account-session scraping without Director approval. Therefore implementation of personalized CTS pricing cannot proceed safely until the Director chooses whether such authenticated account integration is permitted. Until that decision, personalized payable price must remain unknown and cannot affect savings/ranking.

## 14. Exact refs

### Repository

- `WORKER_TASK_DLC_PERSONALIZED_BUNDLE_ECONOMICS_RECON_01.md` @ `4bd145a9bbd4973edee5c22bbfbba3ecf44e6e06`
- `reviews/worker_reports/compact-purchase-options-01.md` @ `e41332ebb11c5f3928ab945ee09bb78cb0de1616`
- `config/mailing_policy.json`
- `config/content_eligibility_contract.json` @ `d9b1710da2f0a323d1be01f722cc929cf27f9472`
- `config/offer_family_contract.json` @ `23eaa92aab468fc0203efb6383004bc0c3a54a90`
- `config/fixed_package_purchase_option_contract.json` @ `2c56ff2efa19ed3d9b0315bbdc3be533df06a823`
- `scripts/steam_production.py` @ `9cc4170a46907f64cb3b907b114150b83974577b`
- `scripts/build_pre_ai_store_snapshot.py` @ `f0454500aa17b49e5e45d8c27535ad62aed3a315`
- `scripts/build_pre_ai_content_rules.py` @ `41dcdcf3d36e526545104519a221a7e1de00d3c7`
- `scripts/build_pre_ai_family_graph.py` @ `d4a1f75744be5254853c32008b38cbf744b0096b`
- `scripts/build_pre_ai_chatgpt_payload.py` @ `bcc225e2d3676ac63edbf7857905e218050b475a`
- `scripts/build_fixed_package_purchase_options.py` @ `7e5b91df27b72c5adff77817502ff729cd65abf5`
- `scripts/apply_fixed_package_purchase_options.py` @ `ed3c335aed6a87d4d0d2175dd537b0143cb112bc`
- `scripts/priority_ranking.py` @ `206fd682fcfe34390f5c7e1bd70710d999ba842b`
- `scripts/test_fixed_package_purchase_options.py` @ `2ccf540c8e513776d3052d8485fda0b5da7bfd14`
- `scripts/test_package_complete_content_value.py` @ `7f4a988f585978df4b448976cfb18a9796e25cf7`
- `.github/workflows/build-pre-ai-store-snapshot.yml` @ `a0eb3ea7e648fe6503f6aa9499d104fa28b6ba78`
- `.github/workflows/build-daily-visual-payload.yml` @ `90452c73f60addce11a7a6fdc1fa475de7ed3cd7`

### Valve / Steam-owned authoritative evidence

- Steamworks Bundles — Complete The Set vs Must Purchase Together, owned-item semantics and account-dependent pricing:
  - `https://partner.steamgames.com/doc/store/application/bundles`
- Steamworks Packages — package is a sold/granted SKU/license with explicit app/depot contents:
  - `https://partner.steamgames.com/doc/store/application/packages`
- Steamworks DLC — DLC has its own AppID, is associated with a base application, and ownership can be checked through Steamworks ownership APIs:
  - `https://partner.steamgames.com/doc/store/application/dlc`
- `IPlayerService/GetOwnedGames` — source-owned list of games owned by a player when visible; requires Web API authentication key:
  - `https://partner.steamgames.com/doc/webapi/IPlayerService`
- User Authentication and Ownership / `CheckAppOwnership` — exact AppID ownership mechanisms and publisher-key scope:
  - `https://partner.steamgames.com/doc/features/auth`
  - `https://partner.steamgames.com/doc/webapi/ISteamUser`
- Steam Store bundle pages — source-owned bundle detail surface that renders bundle composition and purchase cost; actual user-specific CTS amount requires authenticated account context:
  - `https://store.steampowered.com/bundle/<bundleid>/`
