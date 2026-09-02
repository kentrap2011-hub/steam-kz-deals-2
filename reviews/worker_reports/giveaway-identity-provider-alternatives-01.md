# giveaway-identity-provider-alternatives-01

Date: 2026-09-02

### Twitch/IGDB disposition
Twitch/IGDB remains a fallback while the already-submitted Twitch Support request is pending; this recon does not revisit the Twitch blocker.

### Candidate routes

| Route | Exact provider-ID capability | Exact Steam bridge | Credentials / terms / automation | Failure behavior | Classification |
|---|---|---|---|---|---|
| **IsThereAnyDeal (ITAD) exact shop-ID lookup** | **Yes.** Documented `POST /lookup/id/shop/{shopId}/v1` maps a shop's exact game/product ID to an ITAD game UUID. The current Epic collector already has the exact Epic `offer_id`; the current GOG collector already has the exact numeric GOG catalog product ID. No title is needed. | **Yes.** Documented `POST /lookup/shop/{shopId}/id/v1` maps the same ITAD game UUID back to shop game IDs. For Steam, accept only one exact `app/<digits>` result and strip only the `app/` prefix. | Lookup endpoints are documented stable API endpoints and advertise `None` as an allowed authorization mode; shop IDs can be discovered from documented `/service/shops/map/v1`. No second scheduler/runtime is needed: bounded calls fit the existing GitHub Actions producer. **Terms are the blocker:** ITAD says public commercial apps may use the API, but “If you want to use this API privately contact us.” This project is personal/non-commercial and publishes a public result, but it is not safe to assume ITAD considers the backend use “public”; written clarification is the smallest remaining contract question. | `null`/missing provider ID, no ITAD game UUID, multiple/conflicting identities, no Steam `app/` result, or more than one Steam app result => unresolved; never title fallback. | `blocked_by_credentials_or_terms` (technically strongest candidate; terms clarification only) |
| **Wikidata exact external-ID bridge** | **Yes, when data exists.** Epic can use first-party Epic `pageSlug` -> Wikidata `P6278` (Epic Games Store ID); GOG can use the collector's exact numeric product ID -> `P12727` (GOG product ID). | **Yes, when the same Wikidata item has `P1733` (Steam application ID).** Require one item and one acceptable Steam app ID; otherwise unresolved. | No account or API secret is required for read access. Structured Wikidata data is CC0. GitHub Actions can query MediaWiki/Wikibase or SPARQL with bounded requests and caching; no second runtime. Main weakness is coverage/provenance: both Epic and GOG identifier properties explicitly have incomplete coverage and are community-maintained rather than a purpose-built cross-store product map. | Missing property, zero/multiple Q-items, zero/multiple Steam IDs, or conflicting statements => unresolved. | `viable_secondary` |
| **SteamGridDB external-ID mapping** | **Yes for ingress.** Its documented/client API supports exact `games/egs/{id}` and `games/gog/{id}` lookups and requires an API key/account. | **Not safely enough for this production route.** The documented game lookup returns SteamGridDB game identity, but the stable documented API path inspected here does not provide a documented exact inverse from that canonical game to Steam appid. Available examples of reading `platforms.steam.id` rely on the site's undocumented/public backing endpoint, which is not a durable production contract. | API key is realistic, and GitHub Actions would be easy, but relying on an undocumented reverse endpoint would recreate the stability risk this task is trying to avoid. | Without a documented exact reverse Steam ID, must remain unresolved. | `not_automation_suitable` |
| **PCGamingWiki** | **GOG only.** Current official API documents exact redirect/ID lookup by GOG Product ID and Steam App ID. It does not document an equivalent exact Epic product-ID lookup. | For a page reached by exact GOG ID, Steam app data can be queried, but this does not solve the required Epic path. | August 2026 server migration introduced Bot Password/Cargo permission requirements for arbitrary Cargo queries, custom User-Agent/rate-limit requirements, and temporary redirect-endpoint instability. Content is CC BY-NC-SA (compatible with non-commercial use with obligations). No second runtime needed, but Epic precision is missing. | Epic offers cannot be safely bound by exact provider ID; title/page search is forbidden. | `insufficient_identity_precision` |

Serious metadata/search APIs that only offer title search were not promoted to candidates: by task contract they cannot authorize identity even if their metadata is otherwise good.

Public evidence used:
- ITAD API 2.10.0 docs and Terms: `https://docs.isthereanydeal.com/`
  - exact provider ID -> ITAD game: `/lookup/id/shop/{shopId}/v1`
  - ITAD game -> provider IDs: `/lookup/shop/{shopId}/id/v1`
  - shop map: `/service/shops/map/v1`
- Wikidata properties:
  - Epic Games Store ID `P6278`: `https://www.wikidata.org/wiki/Property:P6278`
  - GOG product ID `P12727`: `https://www.wikidata.org/wiki/Property:P12727`
  - Steam application ID `P1733`: `https://www.wikidata.org/wiki/Property:P1733`
  - structured-data license: `https://www.wikidata.org/wiki/Wikidata:Licensing`
- SteamGridDB exact external-ID API evidence: official/public client source `SteamGridDB/java-steamgriddb`, `Game.java` (`games/egs/{id}`, `games/gog/{id}`, `games/steam/{id}`).
- PCGamingWiki current API: `https://www.pcgamingwiki.com/wiki/API`.

### Bounded proof

Current canonical sample from `data/production/giveaways/v1/current.json` contains two active Epic games and no active GOG giveaway.

**1. Breathedge**
- Canonical Epic source identity in repo: namespace `08ae29e4f70a4b62aa055e383381aa82`, exact Epic offer ID `8401414902e84f2cb9afa9142f051d32`, first-party page slug `breathedge` (via the collector's structured `catalogNs.mappings[].pageSlug` route).
- ITAD product page proves exact Epic Store Game Id `8401414902e84f2cb9afa9142f051d32` -> ITAD game UUID `018d937f-2102-72e8-947d-71a97f46e99e`.
- ITAD products for that same game prove Steam `app/738520`; the same ITAD game also carries GOG product `2104548474`.
- Wikidata `Q68198904` independently contains Epic Games Store ID `breathedge`, GOG product ID `2104548474`, and Steam application ID `738520` on the same item.
- Result: ITAD exact route = proven; Wikidata exact route = proven for this game.

**2. Rival Stars Horse Racing : Desktop Edition**
- Canonical Epic source identity in repo: namespace `f570d80aa4fe463ca53c4410d1c75e1e`, exact Epic offer ID `8f1fcf01e32e4fd4b2ae0a9737992760`, first-party page slug `rival-stars-horse-racing-dd09de`.
- ITAD product page proves exact Epic Store Game Id `8f1fcf01e32e4fd4b2ae0a9737992760` -> ITAD game UUID `018d937f-409b-739a-b119-9562b5f55a2a`.
- ITAD products for that same game prove Steam `app/1166860`.
- A bounded Wikidata lookup/search did not establish an item carrying the exact current Epic ID/slug together with the Desktop Edition Steam appid, so Wikidata must be unresolved for this sample item rather than use its title.
- Result: ITAD exact route = proven; Wikidata exact route = not proven.

Bounded result:
- **ITAD:** `2/2` current Epic offers can be proven by the exact Epic offer IDs already owned by the canonical collector and bridged to exact Steam appids without title matching.
- **Wikidata:** `1/2` can be proven in the current sample; the other correctly fails closed.
- **SteamGridDB:** no accepted end-to-end proof because the durable documented reverse-to-Steam contract is missing.
- **PCGamingWiki:** no accepted Epic proof because the current API does not provide an exact Epic-ID ingress route.

There is no active GOG giveaway in the current bounded sample. The GOG identity shape is nevertheless directly compatible with the ITAD design: `scripts/giveaway_gog.py` persists the exact numeric GOG catalog product ID, and ITAD's Breathedge product map demonstrates the same numeric GOG product-ID namespace. A production acceptance test should still fail closed until a live GOG giveaway exercises that path.

### Recommended primary route

**`CONTRACT/RECON IsThereAnyDeal private/public API-use permission`**

ITAD is the best non-Twitch technical route found:
1. it consumes the exact provider IDs the project already owns (Epic offer ID / GOG numeric product ID), rather than a title-derived surrogate;
2. it has a documented two-way shop-ID lookup around one canonical ITAD game UUID;
3. it proves both current Epic giveaways end-to-end (`2/2`) to exact Steam appids;
4. the lookup endpoints are documented stable and require no new scheduler, semantic queue, browser fetch, or second Taste system;
5. Wikidata is cleaner on credentials/license but loses one of the two current sample games and is explicitly incomplete/community-maintained;
6. SteamGridDB and PCGamingWiki do not provide an equally clean documented Epic/GOG -> exact Steam end-to-end contract.

The only material blocker is ITAD's Terms sentence requiring contact for private API use. Before implementation, send one concise use-case request to `api@isthereanydeal.com`: personal/non-commercial public GitHub Pages giveaway feed, server-side exact-ID lookup only, cached/bounded daily use, no price/deal replication, no competitor product, with attribution/link as requested. Ask whether this use is permitted under the current Terms and whether an API key is required/recommended for these lookup endpoints. Do not implement until that answer is affirmative or the public-use interpretation is explicitly confirmed.

If ITAD declines, the already-proven fallback among non-Twitch providers is Wikidata exact external-ID binding with strict fail-closed coverage; Twitch/IGDB remains the separate fallback already tracked by Support.

### Implementation ownership

No implementation is performed in this task. If ITAD permission is confirmed, the smallest canonical insertion is:

`existing Epic/GOG collector exact identity -> ITAD exact shop-ID resolver -> exact Steam appid -> existing Steam family/Taste/description analysis path`

Ownership should remain with the existing GitHub production path:
- `scripts/giveaway_epic.py` continues to own Epic `namespace`, exact `epic_offer_id`, and first-party page slug; no title-derived ID is introduced.
- `scripts/giveaway_gog.py` continues to own the exact numeric GOG `source_product_id`.
- `scripts/giveaway_production.py` remains the single writer of `data/production/giveaways/**`; it would call one bounded resolver and persist provider ID, ITAD game UUID, exact Steam appid, resolution status, provenance, and timestamp.
- Resolve ITAD shop IDs from the documented shop map by exact shop title/config acceptance, not hard-coded folklore; persist/validate the accepted IDs in a small contract if needed.
- Epic lookup input is the exact first-party `epic_offer_id` already present in source provenance (or the exact second component of the canonical `namespace:offer_id` product identity), never the title or slug unless an explicitly documented ITAD shop-ID variant requires it.
- GOG lookup input is the exact numeric catalog product ID.
- Reverse lookup to Steam must keep only `app/<digits>` IDs. Accept exactly one canonical app result; zero or multiple base-app results remain `identity_unresolved`.
- No price/deal/ranking state from ITAD enters analysis. Once exact Steam identity exists, reuse only the existing canonical description, positive Taste evidence, and grounded negative evidence/readiness path.
- No browser-side provider fetch, no new scheduler, no second ChatGPT queue/runtime.

### Status
`complete`

Efficiency / reusable lesson: `ITAD exact shop-ID lookup: current Epic offer_id is already the right cross-store key; do not downgrade it to title/slug matching.`

Exact repo refs:
- task blob: `140293b3c646935132f68649888f6b1f3d157862`
- current bounded giveaway snapshot blob: `eae7cb7b978ad9cc05cf7336027bfbfbe9abd1da`
- Epic exact-identity adapter blob: `6891b9e2659403c8f248fb5f9a032dd94617ecce`
- GOG exact-identity adapter blob: `343da9cb5eae49c9edee00cd2443d6513fc49dc9`
- SteamGridDB public client `Game.java` proof blob: `d50f47b14a143a779eabfa7e875c74ae17d0af10`
