# itad-terms-permission-prep-01

Date: 2026-09-02

### Current terms point

Current ITAD API docs are version `2.10.0`. The only remaining blocker before implementation is permission interpretation for this personal/non-commercial backend use.

Relevant current Terms/API points:
- Terms say: `You MAY use this API for commercial purposes IF the resulting app is available to public. If you want to use this API privately contact us.`
- Terms also say users should provide a link/mention to IsThereAnyDeal, must not imply affiliation, must not alter provided data, and must not make or help a competing product.
- Docs explicitly say that if unsure about any point, contact ITAD.
- General API contact is `api@isthereanydeal.com`.
- The exact identity endpoints required by this project remain documented:
  - `POST /lookup/id/shop/{shopId}/v1` — exact shop game ID -> ITAD game UUID;
  - `POST /lookup/shop/{shopId}/id/v1` — ITAD game UUID -> shop game IDs.
- Those two lookup endpoints currently list `None`, API-key query parameter, and API-key header as supported authorization modes. The general Access section nevertheless says most endpoints are restricted by API key/OAuth and app registration generates credentials, so asking whether an API key is required or recommended for this use is appropriate.
- Rate-limit guidance explicitly asks clients to cache properly; the intended use here is bounded, cached, and low-frequency daily server-side lookup.

Official source checked: `https://docs.isthereanydeal.com/` (API 2.10.0, Terms / Access / Lookup sections), 2026-09-02.

### Email to send

To: `api@isthereanydeal.com`

Subject: `Permission for low-volume exact game ID lookups in a personal project`

Body:

Hello,

I’m working on a small personal, non-commercial project that publishes a public GitHub Pages page with game giveaway information.

I would like to use the IsThereAnyDeal API only for server-side game identity resolution: exact Epic Games Store or GOG product IDs -> ITAD game ID -> exact Steam store ID, using the documented shop-ID lookup endpoints.

The usage would be low-frequency, bounded and cached (typically a small number of lookups in a daily GitHub Actions run). I would not copy, republish or resell ITAD price/deal data, and the project is not a commercial or competing service. I’m also happy to add attribution/a link to IsThereAnyDeal if required.

Could you please confirm whether this use is permitted under your API Terms? Also, for these exact lookup endpoints, should I register an application/use an API key, or is unauthenticated access acceptable for this use case?

Thank you!

### Reply classification

Use exactly one classification when ITAD replies:

- `permission_confirmed`
  - ITAD clearly confirms this use is permitted with no material extra conditions beyond normal Terms/API limits.
  - Next action: proceed to the bounded implementation task below.

- `permission_confirmed_with_conditions`
  - ITAD permits the use but requires one or more conditions, for example API key/app registration, attribution/link, tighter caching/rate limits, or another explicit operational requirement.
  - Next action: record the conditions first, then implement only if they fit the current architecture and can be satisfied without violating project boundaries.

- `permission_denied`
  - ITAD says this personal/private/backend use is not permitted, or refuses API access for this use case.
  - Next action: do not implement ITAD. Use Wikidata exact external-ID binding as the next non-Twitch route with strict fail-closed incomplete coverage; Twitch/IGDB remains the separate fallback.

- `needs_clarification`
  - The reply is ambiguous, addresses only API-key setup but not permission, or asks for more details before deciding.
  - Next action: answer only the specific missing question; do not start implementation until permission is explicit.

### Next after approval

If classification is `permission_confirmed` or `permission_confirmed_with_conditions` and all stated conditions are acceptable, the next implementation task scope is exactly:

`existing Epic/GOG exact provider IDs -> ITAD exact shop-ID lookup -> one unique Steam appid -> existing canonical Steam family / description / Taste analysis path`

Boundaries for that implementation:
- exact Epic/GOG provider IDs only;
- no title, normalized-title, publisher, slug, fuzzy, web-search, or manual per-game mapping as identity authority;
- zero or ambiguous provider/Steam mappings remain unresolved;
- reuse `scripts/giveaway_production.py` as canonical writer;
- reuse existing canonical description / positive Taste evidence / grounded negative evidence readiness path;
- no ITAD price/deal ingestion;
- no new scheduler, queue, runtime, semantic system, or browser-side fetch.

### Status

`ready_for_user_send`

Efficiency / reusable lesson: `ITAD permission question is narrow: ask only about low-volume exact-ID identity lookup and auth/attribution requirements; do not broaden it into deal-data use.`

Exact refs:
- task blob: `cd2d99e202373e907c3da8d7fdf85683d8ea51ef`
- previous provider-alternatives report blob: `9b800a9a6d06378ecfecfe41068cfaa6a136f2c1`
- current ITAD docs checked: `https://docs.isthereanydeal.com/` (API 2.10.0)
