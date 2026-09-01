# Cross-platform giveaway RECON 01

**Date:** 2026-09-01  
**Task:** `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_RECON_01.md`  
**Mode:** RECON only — no collector, UI, scheduling, workflow, or production-pipeline implementation  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`  
**Target region:** Kazakhstan (`KZ`)

## Executive summary

The repository can support a cross-platform `claim-now, keep-forever` giveaway flow, but it should **not** be implemented by letting several new scrapers write the existing Steam-owned `data/production/freebies.tsv` directly.

Recommended first IMPLEMENT scope:

1. **Harden the existing Steam freebie path** so a `100% / 0 KZT` candidate is not accepted until temporary-promotion and ownership semantics are verified.
2. Add **Epic Games Store** as the highest-value non-Steam source.
3. Add **GOG** as the next first-party storefront source.
4. Keep **Amazon Luna / Prime member PC-game entitlements** outside the universal baseline because claiming requires a paid Prime entitlement even when the redeemed PC game can then be kept permanently.
5. Treat itch.io, Fanatical, Humble and publisher-direct giveaways as later/secondary sources until their false-positive and operational costs justify inclusion.
6. If an aggregator such as IsThereAnyDeal is ever used, use it as **candidate discovery only** and revalidate every accepted offer against a first-party store; its current API terms also require care for private use.

The key architectural decision is to create a **single cross-platform giveaway producer and contract** with source adapters feeding one normalization/classification/dedup stage. The future producer should first write a separate `data/production/giveaways/` artifact family (or deliberately take ownership through an explicit ownership-contract migration). It must not silently become a second writer for the current Steam `freebies*` outputs.

The current repo already contains a strong semantic contract in `config/freebies_upcoming_contract.json`, but the implemented Steam producer is weaker: `scripts/steam_production.py` currently selects freebies by `price_kzt == 0 && discount_percent > 0`. Therefore the current artifact is useful as **candidate discovery**, not sufficient evidence by itself that an item is a real temporary free-to-keep giveaway.

## 1. Current repository / Steam path

### 1.1 Existing production ownership

`config/execution_ownership_contract.json` currently assigns collector-owned production output to the Steam production scripts. The current daily execution contract is also Steam-centric. A new cross-platform worker must therefore avoid writing the same canonical paths until ownership is explicitly migrated.

Relevant current artifacts:

- `data/production/freebies.tsv`
- `data/production/freebies_index.json`
- `data/production/manifest.json`
- `data/production/shortlist/index.json`

At recon time, `manifest.json` identifies the source as `Steam Store`, country `kz`, and reports a complete 15,778-item source snapshot. `freebies_index.json` reports one current free item.

### 1.2 Contract vs implementation gap

The existing `config/freebies_upcoming_contract.json` correctly requires a freebie to be a **current limited-time promotion**, with zero final price, positive original price/discount, direct Steam URL, and exclusion of permanent F2P, demos, prologues, playtests, free weekends, trials, DLC, soundtracks, artbooks and utilities. It explicitly says that an unverifiable promotion window must not be treated as a freebie.

The current producer does not yet prove those conditions. In `scripts/steam_production.py`, the final freebie selection is effectively:

```python
price_kzt == 0.0 and discount_percent > 0
```

The persisted TSV fields are only:

```text
appid, title, discount_percent, price_kzt, url
```

So the artifact does not persist start/end time, claim-to-keep evidence, original/base price, license/package identity, content type, or classification confidence. A cross-platform implementation should close this gap rather than copy it to more stores.

### 1.3 Steam source recommendation

Keep the current complete KZ Steam catalog scan as candidate discovery. For the small subset that appears to be `0 KZT + discounted`, perform targeted validation against store/product/package evidence before accepting it as `claim_to_keep`.

Steam has official documentation for normal store discounts and packages, but no public documented giveaway feed that directly emits “free-to-keep” events. Normal discount metadata alone should therefore never be treated as proof of permanent ownership after claim.

Useful official references:

- Steamworks discounts: https://partner.steamgames.com/doc/marketing/discounts
- Steamworks packages: https://partner.steamgames.com/doc/store/application/packages

Recommended Steam identifiers:

- product: `appid`
- actual grant/license where relevant: package/sub ID
- offer instance: a derived promotion-window ID only after the active giveaway window is verified

Region request should continue to use the Kazakhstan storefront (`cc=KZ` / KZ-equivalent route), and the validator should preserve the observed currency/region evidence.

## 2. Source-by-source findings

### 2.1 Epic Games Store — Tier 1 / recommended

**Value:** high. Epic runs frequent temporary giveaways, usually with explicit promotion windows and first-party product metadata.

**First-party consumer surface:**

- https://store.epicgames.com/en-US/free-games

**Machine-readable path:** Epic currently exposes an undocumented store-backend JSON endpoint commonly used by the storefront and ecosystem tooling:

```text
https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=KZ&allowCountries=KZ
```

This is not a public supported API contract, so it must be treated as an unstable backend dependency rather than a guaranteed API.

**Useful fields available in current responses / storefront model:**

- Epic catalog namespace / offer identity
- title and product metadata
- key images
- price / discount metadata
- current and upcoming promotion arrays
- `startDate` / `endDate`
- offer/product mappings used to construct a direct storefront route
- country/locale query parameters

**Auth/key:** no auth/key is normally required for the storefront promotions read path, but account/login can still be required for actual claiming and some age/account restrictions.

**Region:** query explicitly with `country=KZ&allowCountries=KZ`. Do not infer universal availability from an EN-US locale or from a promotion visible in another country.

**Validation:** accept only a current promotional offer whose active window makes the game zero-cost and whose catalog entity is a full game/eligible edition. Reject upcoming-only rows until their start time, mystery placeholders, DLC/extras, permanent free products, and products whose KZ applicability cannot be established.

**Operational risks:** undocumented endpoint/schema changes, promotion-array shape changes, mystery-game placeholders, slug/offer mapping changes, account or age gates, and offer-specific country restrictions.

**Recommendation:** Tier 1 required source for the first cross-platform implementation, with schema contract tests and fail-closed parsing.

### 2.2 GOG — Tier 1 / recommended

**Value:** medium-high. GOG has first-party store data, stable numeric product identity, and temporary 100% promotions.

**First-party consumer discovery:**

- https://www.gog.com/en/games?priceRange=0,0&discounted=true

**Machine-readable path:** GOG currently has an undocumented catalog backend used by its storefront. A useful candidate query shape is:

```text
https://catalog.gog.com/v1/catalog?limit=48&order=desc:score&productType=in:game,pack&discounted=eq:true&price=between:0,0&countryCode=KZ
```

As with Epic, this is storefront infrastructure, not a supported public API guarantee.

**Useful fields:**

- stable GOG product ID
- title / product type
- base/current price and discount data
- product/store links
- images/media
- country-aware catalog query

**Auth/key:** no key is required for public catalog discovery.

**Region:** use `countryCode=KZ` and preserve the response-region evidence. Individual products/redemptions may still have restrictions, so KZ catalog visibility is necessary but should not be the only stored evidence when explicit restriction metadata is available.

**Validation:** `discounted=true + final price 0` is a useful candidate filter but not sufficient by itself. Require base/original price > 0 or explicit first-party giveaway evidence, full-game content type, active limited-time promotion semantics, and an end/deadline where available. Permanently free titles and extras must be excluded.

**Operational risks:** undocumented backend changes, product type ambiguity (`game` vs `pack`/extras), missing promotion-window semantics on some catalog rows, regional differences, and pages that expose price but not enough evidence to prove temporary ownership semantics.

**Recommendation:** Tier 1 after Epic; fail closed when the temporal giveaway semantics cannot be proven.

### 2.3 Steam — Tier 1 / keep and harden

**Value:** already integrated and KZ-complete.

**Machine-readable discovery:** current repository Steam search/catalog route. Do not add a second full Steam crawler merely for giveaways.

**Auth/key:** current discovery does not require a private API key.

**Region:** already KZ-oriented.

**Missing evidence today:** promotion window, package/license grant semantics, full-game classification at the final acceptance step, and persisted evidence explaining why ownership is permanent after claim.

**Recommendation:** keep as Tier 1, but convert the current `0 price + positive discount` output into a candidate step followed by targeted semantic validation.

### 2.4 Amazon Prime Gaming / Amazon Luna — separate subscription-entitlement class

The requested “Prime Gaming” source needs current-state interpretation. Amazon’s gaming benefits have been consolidated under the redesigned **Amazon Luna** experience. Amazon’s current official material says Prime members retain a rotating monthly selection of downloadable PC games, alongside cloud-delivered Luna access.

Official current references:

- Amazon Luna redesign (2025-10-23): https://www.aboutamazon.com/news/entertainment/amazon-luna-redesign-gamenight-prime
- Current Amazon Luna explainer: https://www.aboutamazon.com/news/entertainment/what-is-amazon-luna
- Claiming free games/content with Prime: https://www.aboutamazon.com/news/entertainment/how-to-get-free-games-and-in-game-content-with-your-prime-membership

Amazon notes that many downloadable PC games are fulfilled through stores such as GOG, Epic Games Store, Legacy Games, or Amazon’s own app. These PC grants can be persistent after redemption, but **eligibility to claim them is conditional on an active paid Prime membership**. Cloud Luna titles are rotating access and are not ownership grants at all.

**Machine-readable public feed:** no stable, documented, unauthenticated first-party giveaway API was identified that provides the required product, deadline, region, entitlement and downstream redemption semantics for automation.

**Auth/key:** actual claims commonly require Amazon login/Prime status and may require linking a downstream store account.

**Region:** there are two separate region questions: Prime/Luna benefit eligibility and the downstream GOG/Epic/etc. redemption eligibility. Amazon’s current Luna cloud footprint also does not imply that every Prime downloadable-PC-game offer has identical geography.

**Recommendation:** do **not** include Amazon in the universal `claim_to_keep` baseline. If later desired, model it separately as `subscription_entitlement` with fields such as `requires_subscription=true`, downstream store, linking requirement and redemption region. Never mix Luna cloud access into free-to-keep.

### 2.5 itch.io — later / high semantic noise

itch.io explicitly supports 100% sales, but its ownership model proves why `price == 0` is not enough. Official creator documentation says a normal free download does **not** create ownership; claimable ownership during a 100% sale is a special option that the creator must enable.

References:

- Sales: https://itch.io/docs/creators/sales
- Download keys / ownership: https://itch.io/docs/creators/download-keys
- Claimable 100% sales: https://itch.io/updates/rewards-enhanced-claimable-sales

This makes itch.io a legitimate source of permanent giveaway events but a difficult first-wave automation source. A collector must distinguish “free download” from “claim ownership,” validate that the project is a game rather than an asset/tool/book/soundtrack, handle limited-quantity rewards, and find a reliable public discovery surface.

**Recommendation:** Tier 2/later. Do not ingest generic zero-price itch.io listings.

### 2.6 Fanatical / Humble — later / event-specific

Both stores sometimes run game-key giveaways, but no stable public first-party structured giveaway feed was identified for a robust KZ daily collector. Promotions can involve account requirements, newsletter/marketing conditions, limited key stock, redemption deadlines, external Steam/Epic keys and regional restrictions.

**Recommendation:** later source adapters only when a first-party event page can provide enough evidence. Model finite-key-stock giveaways separately if necessary; never let “landing page says free” bypass region/content/ownership validation.

### 2.7 Ubisoft Connect / EA / publisher-direct — later / publisher event sources

Publishers occasionally run temporary ownership grants, but these are irregular and usually announced through news/store campaign pages rather than a durable machine-readable giveaway feed.

**Recommendation:** use as publisher-specific event sources only after Tier 1 is stable. Each adapter must prove permanent ownership semantics and KZ eligibility from first-party evidence.

### 2.8 IsThereAnyDeal — optional secondary discovery only

IsThereAnyDeal has a documented API and country-aware deal endpoints:

- https://docs.isthereanydeal.com/

However, its current API terms state that private use should be discussed with the provider, most endpoints require an API key/OAuth, and there are restrictions on reuse/competition and modification of supplied data.

**Recommendation:** not a default dependency for this private project. If permission is obtained, it can be a candidate-discovery safety net, but acceptance must still be validated against the first-party store. Do not use an aggregator as the sole source of giveaway truth.

## 3. Anti-false-positive acceptance contract

A normalized offer should be accepted into the baseline giveaway feed only if all mandatory predicates are true:

```text
promotion_type == claim_to_keep
ownership_semantics == permanent_after_claim
starts_at_utc <= observed_at_utc < ends_at_utc
final_price == 0
content_type in {game, explicitly_approved_complete_game_edition}
region_status == available
requires_subscription == false
access_expires_after_claim == false
first_party_claim_url is present
classification_evidence is sufficient
```

Price evidence should additionally satisfy either:

- original/base price > 0 and the active promotion takes the product to zero; or
- an explicit first-party giveaway/free-to-keep marker proves the ownership event even when comparable original-price data is unavailable.

### Mandatory exclusions

Reject or classify outside the baseline:

- permanently free / free-to-play games;
- free weekends / temporary play access;
- demos, prologues, trials, betas and playtests;
- DLC/add-ons unless a future task explicitly expands scope;
- soundtracks, artbooks, tools, assets and utilities;
- subscription-only access and cloud-only access;
- Prime/Luna subscription-gated claims from the universal stream;
- coupon-only/private promotions unless explicitly supported as a different class;
- giveaways with unknown ownership semantics;
- finite-key/lottery promotions whose successful claim is not generally available;
- offers with unknown KZ applicability in a required Tier 1 source.

### Evidence / reason codes

The classifier should emit both positive evidence and deterministic rejection reasons, for example:

```text
accepted: ACTIVE_WINDOW + ZERO_PRICE + PAID_BASE + PERMANENT_GRANT + FULL_GAME + KZ_AVAILABLE
rejected: PERMANENT_F2P
rejected: ACCESS_ONLY_FREE_WEEKEND
rejected: NON_GAME_CONTENT
rejected: REQUIRES_SUBSCRIPTION
rejected: REGION_UNAVAILABLE
unverified: PROMOTION_WINDOW_UNKNOWN
unverified: OWNERSHIP_SEMANTICS_UNKNOWN
```

This is important for auditability and for catching source-schema regressions.

## 4. Kazakhstan / region handling

Region must be a first-class field, not inferred from title, currency or a globally visible marketing page.

Recommended policy:

1. Query the source as KZ whenever the source supports a country parameter.
2. Persist both the requested country and the evidence returned by the source.
3. Represent region as `available | unavailable | unknown`.
4. For **required Tier 1** sources, `unknown` is fail-closed for publication.
5. Preserve explicit allow/deny country lists if provided.
6. Revalidate close to publication/claim time because offer availability can change independently of global promotion timing.
7. For external-key or subscription entitlements, validate both the source entitlement region and the downstream redemption-store region.

Suggested per-source request anchors:

- Steam: KZ storefront / `cc=KZ`
- Epic: `country=KZ&allowCountries=KZ`
- GOG: `countryCode=KZ`
- Amazon/Luna: explicit benefit country + downstream redemption country; do not infer one from the other

## 5. Identity and deduplication

### 5.1 Never deduplicate by title alone

Title normalization is useful for candidate matching but unsafe as the canonical key because remasters, editions, bundles and different games can share or nearly share names.

### 5.2 Store-level identity

Use stable source identifiers whenever available:

```text
Steam: steam:app:{appid}
       plus steam:sub:{subid} when the granted package matters

Epic:  epic:{namespace}:{offer_id}
       plus catalog/product mapping as available

GOG:   gog:{product_id}

Amazon/Luna optional:
       amazon:{entitlement_id}
       + downstream-store redemption identity
```

An individual promotion occurrence should have a separate `source_offer_id` / promotion-window identity so repeated giveaways of the same product do not overwrite history.

### 5.3 Cross-store canonical game identity

Create a logical `canonical_game_key` only when evidence is strong. Prefer an explicit known mapping. Otherwise use title + edition + publisher/developer + release evidence as a **matching proposal**, not an irreversible merge.

Suggested confidence:

- `high`: explicit mapping / trusted external canonical ID
- `medium`: strongly matching metadata, same edition
- `low`: fuzzy title-only candidate — do not auto-collapse

Even when two offers resolve to one logical game, preserve separate store claim options. A future UI can show one game with multiple `offers[]`, but the raw normalized layer should not lose store-specific deadlines, URLs or region status.

## 6. Proposed normalized v1 schema

A future IMPLEMENT contract should be versioned and source-agnostic. Recommended core fields:

```yaml
schema_version: 1
observed_at_utc: timestamp

source_id: steam | epic | gog | amazon_luna | itch | ...
source_kind: first_party_store | publisher | aggregator
source_offer_id: string
source_product_id: string
store_product_id: string|null

storefront: string
title: string
edition: string|null
content_type: game | edition | pack | dlc | demo | soundtrack | tool | other
platforms: [windows, mac, linux, ...]
launcher_or_drm: string|null

store_url: url
claim_url: url
image_url: url|null

original_price: number|null
final_price: number|null
currency: string|null
discount_percent: number|null

promotion_type: claim_to_keep | free_to_play | free_weekend | trial | subscription_entitlement | other
ownership_semantics: permanent_after_claim | access_only | unknown
starts_at_utc: timestamp|null
ends_at_utc: timestamp|null
claim_deadline_utc: timestamp|null
access_expires_after_claim: boolean|null

requires_account: boolean
requires_subscription: boolean
requires_external_link: boolean

country_code_requested: KZ
region_status: available | unavailable | unknown
allowed_countries: [string]|null
restricted_countries: [string]|null
region_evidence: object|null

classification_status: accepted | rejected | unverified
classification_reason_codes: [string]
classification_confidence: high | medium | low
source_evidence: object

canonical_game_key: string|null
identity_confidence: high | medium | low
raw_source_revision_or_hash: string|null
```

Implementation may split raw-source evidence from the public compact output, but the evidence must remain reproducible enough to explain every accepted row.

## 7. Recommended architecture

```text
first-party source adapters
    Steam candidate adapter
    Epic promotions adapter
    GOG catalog/promotion adapter
    [later optional adapters]
        |
        v
source-specific raw candidate snapshots
        |
        v
normalization layer
        |
        v
strict classification / anti-false-positive validator
        |
        +--> region verifier (KZ)
        +--> content-type verifier
        +--> ownership/window verifier
        |
        v
store identity + cross-store dedup resolver
        |
        v
single canonical giveaway producer
        |
        v
versioned giveaway artifacts
```

### Ownership recommendation

For the first IMPLEMENT, prefer a new isolated artifact family, for example:

```text
data/production/giveaways/index.json
data/production/giveaways/current.jsonl   # or TSV + sidecar evidence
```

with one future writer (for example a dedicated `giveaway_production.py`) explicitly named in a new/revised contract.

Only after that route is proven should the project decide whether:

- the cross-platform producer takes over canonical `freebies*` ownership; or
- the Steam artifacts remain source-specific and a single downstream merger owns the cross-platform canonical feed.

What must **not** happen: Steam collector and cross-platform worker both independently write `data/production/freebies.tsv`.

### Required-source completeness

Recommended publication semantics:

- Tier 1 sources = Steam, Epic, GOG.
- A required Tier 1 source failure marks the overall giveaway snapshot incomplete and should prevent publishing a falsely “complete” canonical daily feed.
- Optional Tier 2 sources may fail independently only if the artifact explicitly records their optional status and source completeness; stale optional rows must not be silently retained as current.
- Never substitute yesterday’s active offer without rechecking whether its deadline has passed.

This aligns with the repository’s existing preference for fail-closed freebies rather than partial/stale publication.

## 8. Failure modes and operational risks

| Risk | Effect | Mitigation |
|---|---|---|
| Epic/GOG undocumented backend changes | parser silently drops or misreads promotions | schema assertions, fixture tests, fail closed |
| Store page/A-B/locale changes | missing end time or product type | prefer structured first-party data; targeted page fallback only |
| Upcoming promotion published early | premature freebie | require active time window |
| Time-zone/end-boundary mistakes | expired/early item | normalize all source timestamps to UTC; compare at observation time |
| Permanent F2P mistaken for promo | false positive | require temporal promotion + ownership evidence |
| Free weekend/trial mistaken for ownership | false positive | explicit access-vs-ownership classifier |
| DLC/edition/package ambiguity | wrong content | stable product IDs + content-type validation |
| Region mismatch | KZ user cannot claim | KZ query + persisted regional evidence + fail closed unknown |
| Mystery/placeholder Epic entry | unusable item | do not publish until canonical product identity exists |
| External key stock exhausted | claim failure | separate finite-stock class or revalidate immediately |
| Aggregator stale data | false positive | first-party validation mandatory |
| Auth/403/WAF/rate limit | partial feed | bounded requests, source health, no stale-as-current fallback |
| Title alias/remaster collision | destructive dedup | never title-only dedup; preserve store offers |
| Subscription/cloud offer mixed with giveaway | scope pollution | separate `subscription_entitlement` classification |

## 9. Source priority / implementation decision matrix

| Source | Priority | Machine-readable | KZ handling | End-time quality | Main risk | Decision |
|---|---:|---|---|---|---|---|
| Steam | Tier 1 | existing repo discovery + targeted first-party validation | strong existing KZ route | needs hardening | current semantic gap | KEEP + HARDEN |
| Epic Games Store | Tier 1 | undocumented first-party promotions JSON | explicit country params | strong in promotion arrays | unsupported schema | IMPLEMENT |
| GOG | Tier 1 | undocumented first-party catalog backend | `countryCode=KZ` | variable; may need validation | temporal semantics | IMPLEMENT |
| Amazon Luna / Prime PC grants | separate | no stable public giveaway API identified | entitlement + downstream region | offer-dependent | paid subscription/auth | EXCLUDE BASELINE |
| itch.io | Tier 2 | public pages; ownership semantics special | weak/general | sale-specific | free != owned | LATER |
| Fanatical | Tier 2 | event pages | offer-specific | event-specific | key stock/account | LATER |
| Humble | Tier 2 | event pages | offer-specific | event-specific | keys/account/region | LATER |
| Ubisoft / EA / publisher direct | Tier 2 | irregular campaign pages | offer-specific | event-specific | no durable feed | LATER |
| IsThereAnyDeal | discovery only | documented API, key/OAuth | country-aware | aggregator-dependent | terms + stale data | OPTIONAL, FIRST-PARTY VERIFY |

## 10. Concrete next-step handoff for an IMPLEMENT worker

A later IMPLEMENT task can proceed without new source reconnaissance if it follows this order:

1. Define `config/giveaway_result_contract.json` (name can differ) from the normalized schema and acceptance rules above.
2. Define explicit single-writer ownership for new cross-platform giveaway artifacts; do not modify current Steam-owned outputs implicitly.
3. Add fixtures/contract tests for accepted and rejected examples before live collectors.
4. Harden Steam: treat current zero-price discounted rows as candidates, then verify window/ownership/content/region.
5. Add Epic adapter with KZ promotions query and strict schema guards.
6. Add GOG adapter with KZ catalog discovery plus temporal/promotion validation.
7. Normalize timestamps and region evidence.
8. Implement deterministic rejection reason codes.
9. Implement store identity and non-destructive cross-store grouping.
10. Publish only when all required Tier 1 sources are complete for the run.
11. Integrate into daily flow only after the producer/output ownership decision is explicit and tested.
12. Keep Amazon/Luna subscription benefits and optional Tier 2 sources out of the baseline until separate tasks explicitly expand scope.

### Minimum test fixture set

The first IMPLEMENT should include fixtures for at least:

- active Epic full-game giveaway in KZ;
- upcoming Epic giveaway (must not be current);
- expired Epic giveaway;
- GOG discounted-to-zero game with valid temporary window;
- permanent-free GOG/Steam-like item (reject);
- Steam 100%-looking candidate without ownership/window proof (unverified/reject from published feed);
- free weekend/trial (reject);
- demo/prologue/playtest (reject);
- DLC/soundtrack/artbook (reject);
- region-unavailable KZ offer (reject);
- region-unknown required-source offer (fail closed);
- same logical game simultaneously free on two stores (one canonical game cluster, two preserved claim offers);
- two similarly named editions that must remain separate;
- Prime/Luna downloadable PC grant (classify subscription entitlement, not baseline);
- Luna cloud-only title (access-only, reject);
- itch.io generic free download (reject ownership);
- itch.io explicitly claimable 100% sale (eligible only if all other predicates pass).

## 11. No-go decisions

The following approaches should be explicitly rejected for the first implementation:

1. **No `100% discount == giveaway` shortcut.** Price alone is not ownership semantics.
2. **No title-only dedup.** Stable store IDs are mandatory.
3. **No unknown KZ region treated as available** for required sources.
4. **No subscription benefits in the universal free-to-keep baseline.** Model them separately.
5. **No Reddit/Telegram/Dealabs/aggregator page as primary acceptance evidence.** They may discover candidates only.
6. **No silent second writer for current Steam `freebies*` artifacts.** Ownership must stay singular.
7. **No collector/UI/scheduler changes in this RECON task.** This report is the deliverable.
8. **No stale-as-current fallback** when a required source cannot be refreshed.
9. **No generic itch.io zero-price ingestion.** Free download is not necessarily ownership.
10. **No Amazon Luna cloud catalog ingestion as giveaways.** Rotating cloud access is not claim-to-keep ownership.

## 12. Final recommendation

**Proceed to a later IMPLEMENT task with Steam + Epic + GOG as the required baseline.**

The implementation should create a versioned cross-platform giveaway contract and a single-writer artifact family, reuse the existing KZ Steam scan only for candidate discovery, add strict first-party semantic validation, and preserve store-specific offers under a non-destructive canonical-game grouping.

Amazon’s current Prime/Luna gaming benefits should be modeled separately because they are subscription-gated; itch.io/Fanatical/Humble/publisher events should remain later sources until the Tier 1 path is stable.

This design satisfies the project’s existing false-positive posture, preserves the current production ownership boundary, and gives a later worker enough source, schema, region, dedup and failure-policy detail to accept or reject implementation without another general RECON pass.
