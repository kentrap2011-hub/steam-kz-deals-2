# EPIC GIVEAWAY SCHEMA RECON 01

STATUS: done

## EVIDENCE

### proven

1. Production uses the Epic endpoint and KZ query semantics required by the task:

   - endpoint: `https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions`
   - `locale=en-US`
   - `country=KZ`
   - `allowCountries=KZ`

   `scripts/giveaway_production.py` passes that payload directly to `giveaway_epic.normalize_payload(...)`.

2. The production snapshot at `data/production/giveaways/v1/current.json` has:

   - `as_of = 2026-09-02T20:13:50Z`
   - Epic `complete = false`
   - Epic `items = []`
   - error: `Epic schema changed: element.price.totalPrice must be object`

3. In `scripts/giveaway_epic.py`, `_require_dict(value, label)` raises the above message for any value that is not a Python `dict`. Because callers use `.get(...)`, the same error is produced for all of these wire cases:

   - key absent (`price.get("totalPrice") -> None`);
   - JSON `null` (`None`);
   - a non-object scalar/list value.

   Therefore the existing production error proves that at least one processed element had an `element.price` object but `element.price.totalPrice` was not an object. It does **not** prove which of missing/null/non-object occurred.

4. The parser currently validates price before it has established that an element is a current giveaway. For every `data.Catalog.searchStore.elements[]` element it currently requires, in this order:

   - `element.price` object;
   - `element.price.totalPrice` object;
   - integer `discountPrice`;
   - integer `originalPrice`;

   Only after those requirements does it inspect `element.promotions` and look for a current 100% promotional offer.

5. Because normalization is fail-closed at source level, one catalog element with a variant/non-object `price.totalPrice` aborts the whole Epic source. `giveaway_production.py` then records Epic as incomplete with an empty item list.

### strongly_supported

1. This is **not** a demonstrated global relocation or rename of `price.totalPrice`. A currently indexed Epic `freeGamesPromotions` response still contains ordinary elements with `price.totalPrice` objects and the familiar `discountPrice`, `originalPrice`, and currency fields.

2. Current consumers of the same Epic endpoint also treat `price` / `totalPrice` as optional or variant while using `promotions.promotionalOffers` to identify giveaway candidates. One recent corroborating implementation is `TeleBoxOrg/TeleBox-Plugins`, `epic/epic.ts`, commit `58e607b7880cf39d7fde65142b695b1f9536eadd` (2026-08-31), where `price?` and `totalPrice?` are optional and promotion data drives giveaway selection.

3. The existing Epic promotion contract remains the relevant discriminator: `promotions.promotionalOffers[*].promotionalOffers[*].discountSetting.discountPercentage == 0`, together with the promotion time window. No evidence found in this recon requires changing that discriminator.

### cannot_determine

1. The exact raw wire value of the offending Sep 2 KZ element's `price.totalPrice` cannot be recovered from the production snapshot because the current helper collapses missing, JSON null, and every wrong type into the same exception text.

2. The exact KZ live response could not be fetched from the available execution environment during this recon. Direct access to the required endpoint was unavailable (network/DNS/tool access failure), so no claim is made that a present-day live element has one specific raw variant.

3. The identity of the offending element and whether it was a current giveaway, upcoming giveaway, or unrelated catalog element cannot be proven from the stored error alone.

4. It cannot be proven from the available evidence that an **active current 100% giveaway candidate itself** may omit or null `price.totalPrice`. That case must remain fail-closed until observed directly.

## ROOT CAUSE

The broken assumption is not "Epic moved the price field". The broken assumption is:

> Every `searchStore.elements[]` item must have object `price.totalPrice` with integer price fields before the item can be tested for giveaway relevance.

That assumption is now invalid for the catalog feed.

`freeGamesPromotions` is a heterogeneous list. A field that is not required for an irrelevant/non-current element is currently treated by our adapter as globally mandatory. Because price validation runs before promotion selection, a single variant element prevents valid giveaway elements later in the same response from being reached and causes the whole Epic source to become incomplete.

Evidence classification for the root cause: **proven** for the ordering/global-requiredness bug; **strongly_supported** that `totalPrice` is variant/optional across the feed rather than globally moved; **cannot_determine** which exact JSON variant triggered the Sep 2 incident.

## LIVE PAYLOAD SHAPE

The shape that can be stated without guessing is:

```text
data
└── Catalog
    └── searchStore
        └── elements[]
            ├── promotions: null | object
            │   ├── promotionalOffers[]
            │   │   └── promotionalOffers[]
            │   │       ├── startDate
            │   │       ├── endDate
            │   │       └── discountSetting.discountPercentage
            │   └── upcomingPromotionalOffers[]
            └── price: object on the incident element
                └── totalPrice: NOT guaranteed to be an object for every element
```

For normal price-bearing elements, the familiar shape still exists:

```text
price.totalPrice = {
  discountPrice: <integer>,
  originalPrice: <integer>,
  currencyCode: <string>,
  ...
}
```

For the exact Sep 2 offending KZ element, only this is proven:

```text
isinstance(element["price"], object) == true
isinstance(element["price"].get("totalPrice"), object) == false
```

The raw JSON subtype (missing vs `null` vs other non-object) is **cannot_determine** from preserved evidence and is intentionally not invented here.

### Can active giveaways still map to the existing giveaway schema?

**strongly_supported: yes, without changing the canonical giveaway output schema**, provided an active 100% candidate has the normal price object.

The existing promotion fields still provide title-independent current-offer discovery, and normal `price.totalPrice` objects still provide the fields the adapter already maps. No evidence in this recon requires an output-schema migration.

Whether an active 100% candidate can itself lack `totalPrice` is **cannot_determine**; the minimal repair below deliberately keeps that case strict rather than adding a speculative fallback.

## MINIMUM SAFE REPAIR

Do not make price parsing globally permissive and do not add a fallback source.

The smallest safe production change is to reorder validation inside `giveaway_epic.normalize_payload`:

1. Parse the element enough to inspect `promotions`.
2. Determine whether the element has a **current 100% promotional offer** using the existing promotion semantics and time-window checks.
3. If the element is not a current giveaway candidate, skip it **without requiring `price.totalPrice`**.
4. Only after an element is confirmed as a current 100% giveaway candidate, require exactly the existing price contract:
   - `element.price` must be an object;
   - `price.totalPrice` must be an object;
   - `discountPrice` and `originalPrice` must be integers;
   - `discountPrice == 0` for the active 100% promotion;
   - retain the existing `originalPrice` sanity check and output mapping.
5. Do not alter the endpoint, KZ parameters, canonical output schema, claim-URL rules, or promotion discriminator.

This changes one assumption only:

```text
before: price.totalPrice is required for every catalog element

after:  price.totalPrice is required for every element that we are actually going to emit as a current giveaway
```

That is the minimum safe repair because it tolerates newly variant fields only where they are irrelevant, while preserving fail-closed behavior for the data used to publish a giveaway.

### Required regression coverage for the repair worker

1. Non-current/no-current-promo element with missing or non-object `price.totalPrice` -> skipped; Epic source continues.
2. Current 100% promo with normal `price.totalPrice` -> maps exactly as before.
3. Current 100% promo with missing/non-object `price.totalPrice` -> still raises/fails closed; do not invent a price fallback.
4. Upcoming/non-current promo with variant price -> does not abort current giveaway extraction.

No production code or tests were changed in this RECON task.

## WHAT REMAINS UNKNOWN

- Exact raw JSON value/type of `price.totalPrice` on the Sep 2 offending KZ element.
- Exact identity and relevance state of that offending element.
- Whether Epic can omit/null `totalPrice` on an actually active current 100% giveaway candidate.
- A fresh raw KZ payload from the exact required endpoint, because live access was unavailable during this recon.

These unknowns do not require a speculative repair. The ordering change above addresses the proven global-requiredness defect while deliberately preserving strict validation for active giveaway candidates.

## SCOPE CHECK

- Production parser changed: **no**.
- Production workflow changed: **no**.
- ITAD/IGDB touched: **no**.
- Editorial/title guessing used as authority: **no**.
- Only task artifact added: `reviews/worker_reports/EPIC_GIVEAWAY_SCHEMA_RECON_01.md`.
