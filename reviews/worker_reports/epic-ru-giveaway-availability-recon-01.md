# Epic RU Giveaway Availability Recon 01

Task ID: `epic-ru-giveaway-availability-recon-01`
Mode: `READ-ONLY / RECON`
Observed: `2026-09-04`

## 1. Task

Determine the smallest safe future change such that **Epic Games only** publishes an active free giveaway when the offer is actually claimable for an Epic account in **Russia (`RU`)**, while preserving the current Steam and GOG behavior exactly.

This recon does **not** implement production changes. It intentionally preserves the existing current/active/zero-price/full-game/fail-closed rules and does not touch UI, cache/publication, Taste/ranking, ITAD/IGDB, or semantic runtime.

## 2. Current Epic region semantics

Current Epic collection is in `scripts/giveaway_epic.py`.

Discovery endpoint:

```text
https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions
```

Current parameters:

```python
PARAMS = {"locale": "en-US", "country": "KZ", "allowCountries": "KZ"}
```

The collector separately proves the current free-promotion properties:

1. the offer is in Epic's **current** `promotionalOffers` array, not only `upcomingPromotionalOffers`;
2. `startDate <= observed < endDate`;
3. the current promotion has the existing Epic free-promotion discriminator `discountSetting.discountPercentage == 0`;
4. `price.totalPrice` must exist and be an object;
5. `discountPrice` and `originalPrice` must be strict integers;
6. `discountPrice == 0`;
7. the offer is a `BASE_GAME` before it can be accepted as a game;
8. paid-base claim-to-keep semantics are then set and the shared classifier checks the remaining contract.

Those rules are already guarded by focused tests and must remain unchanged.

The current region decision is weaker. For every qualifying Epic row, the adapter currently writes:

```python
"region_status": "available",
"region_evidence": {
    "requested_country": "KZ",
    "allowCountries": "KZ",
    "endpoint_returned_offer": True,
},
```

So **today Epic region availability means only: the offer was returned by the KZ-scoped `freeGamesPromotions` request.** There is no separate redeemability check in the current Epic adapter.

The shared classifier in `scripts/giveaway_core.py` treats `region_status == "available"` as sufficient region proof; `unknown` becomes unverified and `unavailable` is rejected. The shared contract and reason codes are currently KZ-oriented (`COUNTRY_CODE = "KZ"`, `KZ_REGION_UNKNOWN`, `KZ_UNAVAILABLE`, `KZ_AVAILABLE`).

## 3. Authoritative RU-availability signal

### 3.1 What Epic itself authoritatively says

Epic Games Support establishes the relevant semantics:

- Epic account **country can affect availability of a game that the user purchases or claims**. The account country should match the country of residence.
  - https://www.epicgames.com/help/c-32735058/c-31480328/a14016378?lang=en-US
- Epic's documented storefront statuses say:
  - **`Get`** means the game is available for free to download/play;
  - **`Unavailable`** can mean the account is located in a region where the game is not available to purchase.
  - https://www.epicgames.com/help/epic-games-store-c-202300000001639/tutorials-c-202300000001731/how-to-understand-epic-game-store-offer-statuses-a202300000011822
- Epic also explicitly says that a product can remain visible while being unavailable in the user's region; regional restrictions are controlled by the developer. This is direct evidence that **visibility/presence is not equivalent to acquisition eligibility**.
  - https://www.epicgames.com/help/c-202300000001639/c-202300000001735/lmatha-tudrj-allabh-ala-anha-ghyr-mtwfrh-aw-ghyr-mreyh-fy-epic-games-store-a202300000015687
- Epic's free-offer redemption troubleshooting specifically tells users to verify that the country on the Epic account matches their country.
  - https://www.epicgames.com/help/c-32735058/c-Trending_0/a25505768?lang=en-US

Therefore the authoritative semantic target for this task is:

> An Epic offer is RU-available only when Epic itself evaluates the offer as acquirable for an Epic account whose country is Russia — operationally the free-offer equivalent of storefront status **`Get`**, not `Unavailable` because of region.

### 3.2 What the current source-owned JSON proves — and what it does not

The current source-owned endpoint is real and returns offer/promotion/price data. An inspected Epic-owned response from:

```text
https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?allowCountries=US&country=US&locale=en-US
```

contains the same type of fields used by the collector: offer identity, `status`, `offerType`, `price.totalPrice`, and `promotions.promotionalOffers` / `upcomingPromotionalOffers` with dates and discount settings.

However, in the inspected projection there was **no independently verified machine-readable result whose documented/source-owned semantics are “this account-country may acquire/redeem this offer.”** In particular:

- `status: ACTIVE` is a catalog/offer state, not proven RU acquisition permission;
- `isCodeRedemptionOnly` is not a country eligibility result;
- request parameters named `country` / `allowCountries` demonstrate storefront scoping but, because this backend is undocumented, their presence alone does not prove that a returned row is redeemable by an RU account;
- no authoritative per-offer RU whitelist/blacklist field was proven from a current Epic-owned response during this recon.

Commonly referenced storefront GraphQL field names such as country whitelist/blacklist were encountered only through non-Epic discovery material. They are therefore **not accepted as authoritative evidence in this report**. They may be a future probe target, but must first be verified directly against an Epic-owned endpoint and against known available/unavailable cases.

### 3.3 Recon conclusion on the authoritative signal

An authoritative **semantic** signal was found: Epic's own account-country-scoped acquisition status (`Get` vs region-caused `Unavailable`).

An authoritative, automation-ready **endpoint/field contract** that exposes that signal for an RU account was **not proven** in this recon.

Because the task explicitly forbids guessing unknown availability, this is a STOP condition for implementation.

## 4. Exact behavior change required

Future Epic acceptance must be the conjunction of two independent gates:

### Existing promotion gate — preserve unchanged

- current promotion exists;
- active now;
- current free-promotion discriminator remains valid;
- final price is exactly zero;
- paid base / explicit giveaway semantics remain valid;
- permanent-after-claim semantics remain valid;
- full game / accepted content type remains valid;
- first-party claim URL remains valid.

### New Epic-only RU acquisition gate

Before an Epic candidate can receive `region_status = "available"`, the adapter must have an Epic-owned signal proving that the offer is acquirable for RU.

Required outcomes:

- **RU available** -> candidate may continue through the existing classifier;
- **RU unavailable** -> reject/skip the Epic candidate according to the existing source contract;
- **RU unknown / source schema changed / verification request failed** -> fail closed; never infer availability from the free-games feed returning the row.

The current shortcut:

```text
country=KZ + allowCountries=KZ + row returned => region_status=available
```

must not simply become:

```text
country=RU + allowCountries=RU + row returned => region_status=available
```

unless Epic-owned evidence first proves that exact endpoint behavior is an acquisition-eligibility guarantee. That proof was not established here.

## 5. Is switching the Epic collector to RU sufficient?

**No, not on the evidence available in this recon.**

Changing the Epic discovery request to:

```text
country=RU
allowCountries=RU
```

would establish RU-scoped catalog/promotion/price context. It would **not yet prove actual claimability**, because:

1. the backend is explicitly treated by the current code as an undocumented storefront backend;
2. Epic's own support docs distinguish product visibility from the account's ability to acquire it;
3. no source-owned contract was found saying that inclusion in `freeGamesPromotions(country=RU, allowCountries=RU)` is itself a redeemability guarantee.

Therefore a **separate, proven RU availability verification is required**, unless a future direct Epic-owned probe proves that the RU-scoped discovery endpoint itself is the authoritative acquisition filter.

## 6. Canonical source metadata after the future change

Do **not** globally change `giveaway_core.COUNTRY_CODE` from KZ to RU. That would silently redefine Steam and GOG and violate the user rule.

For Epic, the canonical candidate/source metadata should instead carry explicit source-scoped region evidence, e.g. conceptually:

```json
{
  "region_status": "available",
  "region_evidence": {
    "target_country": "RU",
    "verification_method": "<verified Epic-owned acquisition signal>",
    "verification_result": "available"
  }
}
```

The source health/details record should also identify Epic's target region as RU. `source_provenance` should retain the exact Epic discovery and verification endpoint/parameters used.

There is a canonical audit checkpoint before implementation: the top-level snapshot currently says `country_code: "KZ"` and shared reason codes say `KZ_*`. Once Epic is RU-scoped, those fields no longer describe all providers uniformly. A bounded consumer audit of those exact giveaway fields is required before choosing the smallest non-breaking representation (for example source-scoped region metadata/reason codes). This is a metadata correctness issue; it is **not** a reason to migrate Steam/GOG to RU.

## 7. Steam/GOG non-impact proof

`scripts/giveaway_production.py` imports and executes three independent collectors:

```python
collectors = {
    "steam": (collect_steam, ...),
    "epic": (collect_epic, EPIC_ENDPOINT),
    "gog": (collect_gog, GOG_ENDPOINT),
}
```

The existing Steam collector remains explicitly KZ-oriented:

- KZ production candidate artifacts;
- `appdetails` with `cc=KZ`;
- store page with `?cc=KZ`;
- KZ store-page region evidence.

The existing GOG collector remains explicitly KZ-oriented:

- catalog `countryCode=KZ`;
- product-page validation with `countryCode=KZ`;
- KZ catalog region evidence.

Therefore the future implementation boundary can be Epic-specific. No Steam or GOG endpoint, country parameter, discovery rule, or validation path needs to change.

The existing `scripts/test_giveaway_production.py` also has separate Steam, Epic, and GOG normalization/acceptance fixtures, so Steam/GOG can be protected with focused regression assertions.

## 8. Regression plan

Focused future tests, in `scripts/test_giveaway_production.py` (plus a tiny helper fixture only if required):

1. **Active Epic giveaway + authoritative RU available** -> accepted.
2. **Active Epic giveaway + authoritative RU unavailable** -> not accepted.
3. **Active Epic giveaway + RU availability unknown/malformed** -> fail closed; no guessed acceptance.
4. Existing Epic current-vs-upcoming behavior unchanged.
5. Existing Epic current free discriminator unchanged.
6. Existing Epic strict `price.totalPrice` and strict integer price guards unchanged.
7. Existing Epic non-zero `discountPrice` failure unchanged.
8. Existing Steam true active claim-to-keep test still passes unchanged.
9. Existing GOG true active claim-to-keep test still passes unchanged.
10. Snapshot/source-health test demonstrates that failure of the new Epic RU verifier cannot publish that Epic candidate as accepted.

## 9. Review / audit implications

Required future review checkpoints are bounded to giveaway region semantics:

- prove the exact Epic-owned RU acquisition signal with at least one known RU-available and one known RU-unavailable offer/account-country case before coding against it;
- record the exact endpoint/field/status and its failure semantics in Epic provenance;
- audit only exact consumers of giveaway `country_code` and `KZ_*` region reason codes because the canonical snapshot becomes mixed-provider-region in meaning;
- verify generated audit rows never mark Epic `region_status = available` from discovery-row presence alone;
- verify Steam and GOG source health/details remain KZ and byte/semantic behavior is unchanged apart from incidental timestamps/counts in a live run.

No UI/cache/publication/Taste/ranking/ITAD/IGDB migration is part of this work.

## 10. One bounded IMPLEMENT plan

**Do not execute until the authoritative machine-readable RU acquisition signal is proven.**

1. **Resolve the blocker with one targeted Epic-owned probe.** Identify the exact EGS endpoint/field/status that represents acquisition availability for an RU-account context. Validate it against one known RU-available and one known RU-unavailable offer. If the candidate is an offer country whitelist/blacklist field, prove it directly from Epic-owned responses and prove its acquisition semantics; do not rely on third-party field names.
2. **Patch `scripts/giveaway_epic.py` only for provider behavior.** Preserve all existing promotion/price/content checks. Use RU for Epic discovery context if required by the proven contract, then require the proven RU acquisition signal before setting `region_status = "available"`. Unknown/malformed/failed verification must fail closed. Store explicit RU `region_evidence` and exact provenance.
3. **Make only the minimum canonical metadata adjustment required by the exact consumer audit.** Do not change Steam/GOG target regions and do not globally switch `COUNTRY_CODE` to RU. If source-specific region reason metadata is required, branch it only for Epic while preserving existing Steam/GOG classification behavior.
4. **Update `scripts/test_giveaway_production.py` with the focused RU available/unavailable/unknown cases and Steam/GOG non-regressions.** No UI/cache/publication/Taste/ranking/ITAD/IGDB changes.

## 11. Status

`blocked`

Reason: recon is complete, but implementation is intentionally blocked by the task's STOP rule. Epic-owned documentation proves that account-country acquisition availability is the required truth and that visibility is insufficient, but this recon did not prove a current automation-ready Epic endpoint/field whose source-owned semantics guarantee RU redeemability. Replacing KZ with RU would therefore be an unsupported guess.

## 12. Exact refs

Repository:

- `WORKER_TASK_EPIC_RU_GIVEAWAY_AVAILABILITY_RECON_01.md` @ `66f844d337ff2742865d08a392aedfc571a212d7`
- `scripts/giveaway_epic.py` @ `6fb410a27a0bc40c3fce2eecacc9d09da7aec88e`
- `scripts/giveaway_core.py` @ `b5e6cf5c741139deba58814135e8af5787b07230`
- `scripts/giveaway_production.py` @ `ab94478e5da518b5b8456b64f712bd6219990527`
- `scripts/test_giveaway_production.py` @ `0bf860f3e35e5dc367a82f531be7d55c3abba089`
- `scripts/giveaway_steam.py` @ `87290b4d02c9f39b0e5f65bd5276d3e4f70d23e0`
- `scripts/giveaway_gog.py` @ `343da9cb5eae49c9edee00cd2443d6513fc49dc9`

Epic-owned external evidence:

- Epic account country affects purchase/claim availability:
  - `https://www.epicgames.com/help/c-32735058/c-31480328/a14016378?lang=en-US`
- Epic offer status semantics (`Get` / regional `Unavailable`):
  - `https://www.epicgames.com/help/epic-games-store-c-202300000001639/tutorials-c-202300000001731/how-to-understand-epic-game-store-offer-statuses-a202300000011822`
- Epic regional unavailability can coexist with a visible product page:
  - `https://www.epicgames.com/help/c-202300000001639/c-202300000001735/lmatha-tudrj-allabh-ala-anha-ghyr-mtwfrh-aw-ghyr-mreyh-fy-epic-games-store-a202300000015687`
- Epic free-offer redemption troubleshooting checks account country:
  - `https://www.epicgames.com/help/c-32735058/c-Trending_0/a25505768?lang=en-US`
- Source-owned free-games JSON projection inspected for schema evidence:
  - `https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?allowCountries=US&country=US&locale=en-US`
