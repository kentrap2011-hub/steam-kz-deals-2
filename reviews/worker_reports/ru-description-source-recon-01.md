### Task
Read-only source recon for ready-Russian game descriptions before designing a translation stage. Checked the existing Steam Russian source plus IGDB, RAWG, Wikimedia (Wikidata + Russian Wikipedia), GOG, and Microsoft Store source classes. No catalog-wide manual population or translation was performed.

### Verified facts

| Source | Ready Russian description text? | Steam identity / coverage | GitHub-direct access | Constraints / quality | Verdict |
|---|---|---|---|---|---|
| Steam Russian StoreBrowse / Store app data | **Yes.** This is already the dominant working source: the current deterministic audit/validator reports `310/442` visible cards as meaningful Russian and `132/442` unresolved/invalid. | Exact Steam `appid`; best possible catalog identity. Coverage is broad but upstream Russian metadata varies and can be absent, weak, or edition/package-oriented. | **Yes**, already fetched server-side by GitHub producer without browser automation. | Must keep the existing quality gate because Steam can return technical/edition blurbs or non-usable localized text. | **Canonical primary.** |
| IGDB API | **No usable localized summary path found.** `games.summary` / `storyline` are game-level fields; `game_localizations` exposes only localization metadata such as localized `name`, `cover`, and `region`, not localized `summary`. | Strong identity bridge: `external_games` has `uid` and a Steam source/category, so Steam app IDs can be mapped reliably where present. | **Technically yes**, but requires Twitch OAuth client ID/secret; documented limit is 4 requests/sec. | Free non-commercial API; commercial use requires partnership. Good identity database, but it does not solve Russian description text. | **Identity helper only; not a description source.** |
| RAWG API | Descriptions exist, but the public API documentation reviewed does **not document a Russian/locale selector for the game description field**, so there is no evidence of deterministic ready-Russian description retrieval. | Large PC/Steam-oriented database with store links, but the documented API is RAWG-ID centric and does not establish exact Steam appid as the canonical description key. | **Yes with API key.** | Free tier: up to 20,000 requests/month, attribution/backlink required; commercial tiers exist; terms prohibit data redistribution. No proved RU-localized description contract. | **Unsuitable as canonical ready-RU source.** |
| Wikidata `P1733` + Russian Wikipedia intro | **Yes for a subset.** Wikidata provides exact Steam application ID (`P1733`); Russian Wikipedia can return real Russian article intro text through Wikimedia/MediaWiki APIs. Sanity case: Steam appid `954740` maps to `Terminator: Resistance`, whose Russian Wikipedia article has a meaningful Russian game summary. | Exact mapping is possible when a Wikidata item has `P1733` and a Russian Wikipedia sitelink. Wikidata explicitly treats identifier coverage as incomplete; Russian-article coverage is a further subset. Edition identity also needs fail-closed handling (e.g. base game vs Ultimate Edition). | **Yes**, server-side HTTP with no browser automation; Wikimedia documents API access and rate/UA etiquette. | Wikidata structured data is CC0. Wikipedia article text is CC BY-SA and requires attribution/share-alike compliance; text is encyclopedic, not store copy, and article coverage/quality varies. | **Potential conditional secondary only**, if exact identity and licensing/attribution policy are explicitly approved. |
| GOG | GOG supports Russian as a platform/game language, but the official developer documentation reviewed does not document a public arbitrary-catalog product-description API suitable for this use. A product endpoint located during recon is third-party/undocumented rather than an approved GOG catalog contract. | No reliable Steam-appid mapping from the official GOG developer API docs. | Not an approved GitHub-direct arbitrary catalog source under documented public API terms. | Using an undocumented catalog endpoint would create stability/terms risk. | **Reject as canonical source.** |
| Microsoft Store | Microsoft Store listings can have localized descriptions, but the documented APIs are scoped to the current/associated app or to seller-authorized Partner Center submissions, not arbitrary public game-catalog enrichment. | Microsoft Store IDs are separate; no documented exact Steam-appid mapping for arbitrary titles. | Not suitable as unauthenticated GitHub-direct arbitrary catalog read. Seller submission APIs require authorization/account context. | Good localization for owned listings, wrong access/identity model for this project. | **Reject as canonical source.** |

Repo evidence:
- `scripts/build_visual_feed_v2.py` already queries `IStoreBrowseService/GetItems` with `language='russian'`, preserves Steam source text, and keys resolution by Steam appid.
- `scripts/russian_description_quality.py` classifies meaningful RU vs non-RU/weak/technical/missing and leaves unresolved text explicit rather than publishing placeholders.
- `reviews/worker_reports/ru-description-implement-01.md` measured the legacy visible payload as `442` cards: `310 good_ru`, `131 placeholder_or_technical`, `1 weak_ru` -> **132 unresolved/invalid**.
- Ownership remains GitHub-first: `config/execution_ownership_contract.json` assigns GitHub all directly accessible sources and deterministic transforms; interactive chat must not become the catalog collector.

### Recommendation
Recommended future precedence:
1. **Meaningful Steam Russian description** from the existing exact-appid Store path, through the current quality gate.
2. **Conditional Wikimedia secondary:** only when an exact Wikidata `P1733 = Steam appid` match resolves to the exact game/edition and a Russian Wikipedia article intro exists and passes the same meaningful-Russian/content-quality gate. No title/fuzzy matching. This source should be enabled only if the project explicitly accepts CC BY-SA attribution/share-alike requirements and stores the required provenance/attribution metadata.
3. **Translation fallback** from the preserved non-Russian Steam source when neither approved ready-Russian source yields acceptable text.

Do **not** use IGDB, RAWG, undocumented GOG catalog endpoints, Microsoft Store seller APIs, search-engine snippets, or arbitrary copied web text as Russian-description content sources. IGDB may still be useful later as identity metadata, not description text.

### Translation impact
`translation_still_required`

External ready-Russian text can reduce some translation work, especially via Russian Wikipedia for well-covered titles, but no checked provider combines broad Steam-PC coverage, exact Steam identity, ready Russian descriptions, clean GitHub-direct access, and low-friction reuse terms. Wikimedia coverage is incomplete and legally/provenance-heavy enough that translation cannot be reduced to a guaranteed rare edge case.

### Executor
- Steam Russian source: **GitHub-direct** now.
- Wikidata + Russian Wikipedia: **GitHub-direct** technically; no browser automation or interactive-chat collection required. Must respect Wikimedia API etiquette and preserve attribution/provenance if article text is reused.
- IGDB: GitHub-direct only with Twitch OAuth secrets, but not useful for localized description text.
- RAWG: GitHub-direct only with API key, but not approved for ready-RU because localization is unproved and redistribution/attribution terms are material.
- GOG / Microsoft Store: not suitable as arbitrary GitHub-direct description providers under the documented access models reviewed.
- Translation remains a separate future semantic fallback and was **not** executed or designed in this recon.

### Changes
`none` except report.

### Validation
Canonical repo evidence read:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `scripts/build_visual_feed_v2.py`
- `scripts/russian_description_quality.py`
- `reviews/worker_reports/ru-description-audit-01.md`
- `reviews/worker_reports/ru-description-implement-01.md`

Public documentation/source references checked:
- Steam supported languages / Russian API language: https://partner.steamgames.com/doc/store/localization/languages?language=english
- IGDB API docs, auth/rate limits, `external_games`, `games`, `game_localizations`: https://api-docs.igdb.com/
- RAWG API / key, limits, pricing, attribution and redistribution terms: https://rawg.io/apidocs
- Wikidata Steam application ID `P1733`: https://www.wikidata.org/wiki/Property:P1733
- Wikidata data access / CC0: https://www.wikidata.org/wiki/Wikidata:Data_access and https://www.wikidata.org/wiki/Wikidata:Licensing
- MediaWiki TextExtracts API: https://www.mediawiki.org/wiki/Extension:TextExtracts
- Wikimedia text reuse terms / attribution: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use
- Sanity source pair for exact Steam identity + real Russian text: https://www.wikidata.org/wiki/Q68888832 and https://ru.wikipedia.org/wiki/Terminator:Resistance
- GOG developer docs / supported Russian language: https://docs.gog.com/ and https://docs.gog.com/bc-languages-table/
- Microsoft Store listing/product APIs: https://learn.microsoft.com/en-us/uwp/api/windows.services.store.storeproduct and https://github.com/MicrosoftDocs/windows-dev-docs/blob/docs/hub/apps/publish/store-submission-api.md

### Unresolved
- Exact share of the current 132 unresolved cards that have an exact `P1733` + Russian Wikipedia article was intentionally **not** measured, because the task forbids turning recon into catalog processing. It must be measured later by a GitHub-owned deterministic source pass if Wikimedia is approved.
- Product/legal decision remains whether CC BY-SA Wikipedia text plus visible/recorded attribution is acceptable for the storefront UI. Without that approval, Wikimedia should not be integrated.
- Russian Wikipedia intro text may be too encyclopedic or edition-ambiguous for some cards; the existing content-quality gate must remain fail-closed.

### Status
complete

### Recommended next step
Create one bounded **ready-Russian secondary-source contract** (no production implementation yet) that either explicitly approves or rejects Wikimedia. If approved, require exact `Steam appid -> Wikidata P1733 -> exact Russian Wikipedia sitelink`, intro-only extraction, provenance/attribution fields, edition-identity fail-closed rules, cache/rate etiquette, and the existing Russian quality gate; only after that deterministic source is exhausted should the deferred translation contract handle the remaining unresolved records.