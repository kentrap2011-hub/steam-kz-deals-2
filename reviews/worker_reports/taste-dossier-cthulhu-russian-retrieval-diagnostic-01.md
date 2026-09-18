# Taste Dossier Cthulhu Russian Retrieval Diagnostic 01

## 1. Task / repo / mode

- Task: `TASTE DOSSIER CTHULHU RUSSIAN RETRIEVAL DIAGNOSTIC 01`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `READ-ONLY DIAGNOSTIC`.
- Scope was limited to `Cthulhu Saves the World` from current `g000007`.
- No implementation, schema/contract/prompt/validator change, PR, candidate publication, production-progress change or Scheduled Task run was performed.
- The only repository write is this durable report.

## 2. Current snapshot / group / exact appid

Current canonical worker projection on `main`:

- snapshot: `d253b195701e74c9c00fc8b669f84655341601faf11e09a7edfb353a8b7f2bbb`
- canonical expected sequence: `7`
- group: `g000007`
- group SHA256: `4c8e2e491b2797960963e687e4301490e21a2bf3c50c068bd34f14e7e2347bab`
- exact target item: `App_107310`
- exact appid: `107310`
- exact title: `Cthulhu Saves the World`
- reason: `missing_dossier`
- active evidence-contract revision: `contract-contradictions-fix-2026-09-18`
- active worker-prompt revision: `web-evidence-v2-contract-contradictions-fix-v1`

The worker index and exact `g000007` descriptor have the same snapshot, group-plan binding and evidence-contract binding.

## 3. Diagnostic budget actually used

Task diagnostic ceiling: 16 web/search queries and 32 opened/read source pages.

Actually used:

- web/search queries: **16 / 16**
- explicit opened/read page attempts: **12 / 32**
- two page attempts were failed/unusable retrievals and were still counted conservatively.

Search effort covered exact-app Steam Store/Community, Russian query variants, stable-locator discovery, profile/recommendation discovery, general exact-title Russian search, and materially different public player-feedback surfaces.

No production worker was rerun and no production candidate was constructed.

## 4. Russian existence evidence

Russian player-feedback existence is established for exact appid `107310`.

The authoritative task context reported approximately 284 Russian-language Steam user reviews. During this diagnostic, exact-product Steam Store retrievals showed a nonzero Russian review population around **282-284** depending on crawl snapshot. That small crawl-count drift is immaterial to the existence decision.

Safe exact-product existence source:

- `https://store.steampowered.com/app/107310/?l=russian`

This aggregate count is discovery/existence metadata only. It is not a feedback record, mention, observation support or `found_and_used` evidence.

## 5. Candidate ledger

No username, display name, SteamID, profile URL, raw review body or long quote is persisted below.

| ID | Surface / source class | Exact product | Concrete player content visible | Language | Stable neutral item locator | Transient author distinguishable | Valid current parent | Date / recency | Contract usability | First rejection reason | Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CTH-RU-01 | Steam Store exact-app | yes, appid 107310 | no; aggregate review population only in current retrieval | aggregate says Russian population; no item language | no item exists in retrieved representation | no concrete item to dedupe | Store URL would be valid only if concrete cards were actually inspected there | n/a | not usable as feedback | aggregate existence signal without a concrete card | retrieval limitation |
| CTH-RU-02 | Steam Community profile-scoped Review Showcase | yes; exact title and app link resolve to 107310 | **yes**; a concrete Russian player review was readable | **Russian from the item body itself** | **no acceptable neutral locator exposed**; only profile-scoped retrieval context | **yes**, sufficient for transient same-product dedupe | **no** for the inspected item: the exposing surface is profile-scoped and cannot be persisted; the exact-app collection did not expose this Russian card in current retrieval | publication date not exposed | not serializable today | no contract-safe stable locator and no non-profile exact-product collection parent on which this concrete Russian card was actually inspected | retrieval limitation |
| CTH-CTRL-01 | Steam Community exact-app review collection | yes, appid 107310 | yes; multiple concrete cards visible | retrieved cards were non-Russian | no neutral recommendation/item id exposed in parsed cards | yes | exact-app non-profile collection exists | visible card dates included recent items | usable in principle for non-Russian fallback, but not the Russian gate | inspected cards were not Russian | semantically insufficient for Russian gate |
| CTH-ALT-01 | Metacritic PC User Reviews | yes, exact game/product page | yes; concrete user reviews visible | sampled visible items were non-Russian | collection URL is stable; no Russian item found | authors are distinguishable on the page | non-Steam exact-product user-review collection is available | visible samples dated 2024 and older; therefore old on 2026-09-19 | usable as non-Russian player feedback under normal exact-product rules, not as Russian evidence | no Russian/mixed item found | semantically insufficient for Russian gate |
| CTH-ALT-02 | DTF public community post | title-level exact game reference | Russian text mentioning the exact game is visible | Russian | stable post URL exists | not needed | public community post exists | 2025-09; old by the active 365-day boundary | not usable as player-feedback evidence for this gate | the relevant text is explicitly presented as a hypothetical/example contest comment, not a reliable actual player-feedback item | semantically insufficient |

Additional inspected alternative surface:

- SteamPrice exposes an exact-product section for player reviews, but no existing concrete player-review items were rendered during this diagnostic.

Safe public surface URLs used for the diagnostic include:

- `https://steamcommunity.com/app/107310/reviews/?browsefilter=mostrecent&p=1`
- `https://steamcommunity.com/app/107310`
- `https://www.metacritic.com/game/cthulhu-saves-the-world/user-reviews/?platform=pc`
- `https://dtf.ru/flood/4019601-konkurs-na-razdachu-kopij-igry-static-dread-the-lighthouse`
- `https://steamprice.ru/cthulhu-saves-the-world`

The profile-scoped Steam locator that exposed the concrete Russian review is intentionally omitted.

## 6. Steam Store concrete review-card result

**CHECK-01 result: concrete Russian Steam Store review cards were not exposed by the current retrieval representation.**

The exact Store page for appid `107310` exposes the Russian review population and review UI metadata, but the web retrieval used here did not expose individual Russian review-card bodies/attribution on that Store surface.

A direct Russian-filter retrieval attempt also failed to provide a usable card-level representation.

Therefore:

- the Store existence signal is real;
- aggregate Store metadata remains correctly non-mention evidence;
- the accepted Store-parent fallback exception cannot be instantiated from the Store retrieval observed here because no concrete Russian card was actually inspected on that parent.

This is a retrieval limitation, not evidence that the contract blocks a visible Store card.

## 7. Stable locator result

**CHECK-03 result: no contract-safe stable neutral locator was obtained for a concrete Russian item.**

For the concrete Russian Steam review that was readable:

- exact product identity was clear;
- item text was clearly Russian;
- the retrieval context was profile-scoped;
- no neutral `recommendationid`, safe item-level `public_ref`, or non-profile direct review URL was exposed.

The exact-app Community collection URL is a collection locator, not an item identity.

The active contract and strict validator correctly reject profile-scoped URLs as persisted provenance. That privacy rule is not the blocker by itself; the blocker is that retrieval did not expose the same concrete item through a safe neutral item locator.

## 8. Transient-author fallback result

**CHECK-02 result: the fallback model is semantically sufficient, but the current retrieval does not satisfy its parent condition for the Russian item actually found.**

For the readable Russian Steam review:

- one concrete individual item was visibly inspectable;
- an author identity was visible strongly enough to distinguish the item transiently for same-product dedupe;
- no author identity needs to persist.

However, the item was exposed on a profile-scoped Steam page. The active fallback requires a non-profile exact-product player-feedback collection/source marked `feedback_surface_mode:"concrete_item_collection"`.

The exact-app Store and exact-app Community collection are both public non-profile product surfaces, but this diagnostic did **not** inspect that Russian card on either of them. Re-parenting the profile-surfaced card to an exact-app collection merely because it is the same host/product would violate the active physical parent/item relationship rule.

Therefore a valid `transient_author_deduped` record cannot be serialized from the currently exposed Russian item.

If the same concrete Russian card were rendered on the exact-app Store or exact-app Community collection, the current accepted fallback model would allow privacy-safe serialization without any contract change.

## 9. Non-Steam / public alternative result

**CHECK-04 result: materially different public player-feedback surfaces are discoverable and readable, but no contract-usable Russian item was found on them within the diagnostic bound.**

- Metacritic exposes an exact-product PC user-review collection with concrete user reviews. The visible sampled items were non-Russian.
- SteamPrice exposes an exact-product player-review section, but no existing concrete player reviews were rendered.
- DTF produced a Russian exact-title community lead, but the relevant passage was explicitly a hypothetical/example contest comment and therefore is not reliable player feedback.

This rules out a Steam-only search strategy as the sole diagnostic method, but the alternative surfaces did not supply a usable Russian/mixed record.

## 10. Exact-product / language / recency checks

**CHECK-05 exact product**

- Canonical target is appid `107310`, `Cthulhu Saves the World`.
- Steam exact-app Store and Community surfaces resolved to appid `107310`.
- The concrete Russian Review Showcase item explicitly identified `Cthulhu Saves the World` and linked back to the exact app.
- Results for other Cthulhu titles, including `Cthulhu Saves Christmas` and unrelated Call of Cthulhu products, were rejected and not used.

**CHECK-06 language**

- Russian existence was not inferred from `?l=russian` UI alone.
- The concrete Russian Steam lead was classified Russian from its actual visible item text.
- Exact-app Community cards shown in the ordinary retrieved review collection were classified non-Russian from their item bodies.
- The Store aggregate Russian population was used only as an existence signal.

**CHECK-07 recency**

- The concrete Russian Steam Review Showcase item did not expose a publication date in the retrieved representation. No date was invented.
- Its visible content concerns durable gameplay/story/dialogue/music traits, not a current technical/localization state.
- Metacritic concrete examples observed were 2024 or older and therefore are old under the active 365-day rule as of 2026-09-19.
- No old or undated item was treated as sufficient current technical/localization evidence.

## 11. Primary blocker classification

Primary blocker: **`retrieval_limitation`**.

Reason:

1. exact-product Russian player-feedback existence is proven;
2. at least one concrete Russian Steam player-review item is actually readable through current web search/open tooling;
3. therefore this is not a pure source-access case;
4. the readable item is exposed only through a profile-scoped path and current retrieval does not expose a neutral stable item locator;
5. exact-app Store/Community collection retrieval does not expose that Russian card, so the accepted transient-author fallback lacks a valid inspected non-profile parent;
6. the contract already permits both the preferred stable path and the privacy-safe fallback when their retrieval prerequisites are met.

The first blocker occurs in retrieval/item-parent exposure before valid serialization.

## 12. Is the current contract internally consistent for this case?

**Yes. No remaining contract contradiction was found for this case.**

Current schema, evidence contract, worker prompt and targeted strict-validator checks agree that:

- Store aggregate counts are not feedback items;
- Store exact-app may parent fallback children only when concrete cards are actually inspected there;
- stable locator remains preferred;
- profile-scoped persisted URLs are forbidden;
- transient-author identity may be used only ephemerally for dedupe;
- fallback children persist no item/profile locator;
- fallback requires a concrete-item collection parent;
- stable Steam parent/child exact-product and physical-container rules remain fail-closed.

The current failure is exactly the intended boundary between unsafe profile-scoped retrieval and safe item/collection provenance. No active rule was found that rejects an otherwise fully contract-qualified Russian item.

## 13. Is a contract change justified?

**No.**

A new contract relaxation is not justified by this diagnostic.

Weakening profile privacy, allowing aggregate Store counts to become mentions, permitting collection URLs to stand in for item identity, or allowing a profile-surfaced item to be rebound to an uninspected exact-app collection would remove safeguards without solving the actual retrieval defect.

The already accepted Store-parent/transient-author model is sufficient once retrieval exposes a concrete Russian card on an exact-product non-profile collection or exposes a neutral stable item locator.

## 14. Minimal next-step design direction

The minimal design direction is retrieval-only:

- make the retrieval layer able to render/read the exact-app Steam Russian review collection at concrete-card level;
- preserve exact appid `107310`;
- expose, when available, a neutral recommendation/item locator for the stable path;
- otherwise expose enough ephemeral card structure to distinguish a concrete author transiently while keeping the persisted parent as the exact-product non-profile collection;
- do not persist profile identity and do not change recurrence/privacy/parent rules.

No evidence-contract redesign is needed.

## 15. Unresolved

The diagnostic did not establish which underlying transport detail prevents current web retrieval from surfacing the Russian card on the exact-app Store/Community collection: dynamic client-side loading, unsupported language-filter parameters, search-index representation differences, or another retrieval adapter limitation.

That distinction is implementation-level retrieval work and was intentionally not fixed here.

No semantic uncertainty remains about the primary blocker classification.

## 16. Status

`complete_retrieval_limitation`

## 17. Exactly one recommended next step

Open one bounded **retrieval-improvement** task for the existing web/retrieval layer: make exact-app Steam Russian review collections expose concrete card-level data for appid `107310`, yielding either a neutral stable item locator or a concrete item plus transient-dedupe signal under a non-profile exact-product collection parent, while leaving the current dossier contract unchanged.

## 18. Efficiency / reusable lesson

Once an exact-product Russian review population is proven, repeated aggregate/list searches have sharply diminishing value. The efficient diagnostic sequence is:

1. prove one concrete item is readable;
2. test whether a neutral item locator is exposed;
3. if not, test whether the same concrete item is visible on an accepted non-profile exact-product collection parent;
4. only then diversify to another public player-feedback class.

This case also shows why a profile search hit should trigger a retrieval-path investigation rather than a privacy-contract relaxation: the content exists, but the tooling must bridge it to safe item/parent provenance.
