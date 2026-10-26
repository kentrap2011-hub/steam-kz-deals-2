# giveaway-itad-identity-implement-01

Date: 2026-10-26  
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`  
Mode: `IMPLEMENT`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/312  
Implementation branch: `implement/giveaway-itad-identity-01`

## Status

**`complete` (implementation, deterministic regression and bounded live exact-ID API acceptance).** On 2026-10-26 the real ITAD API returned exact unique Steam mappings for both current Epic offers; a separate historical GOG shop-ID diagnostic also resolved, but is NOT a current production giveaway. No main production run, merged PR, deployed website or real-device acceptance was executed.

## 1. Provider-neutral switch / interface

- Canonical `config/giveaway_identity_provider.json`: `giveaway_identity_provider: "itad"`, recognized `itad` and `igdb`, implemented `itad` only; no automatic fallback, dual lookup, chain, voting or frontend provider selection.
- `scripts/giveaway_identity.py::resolve_snapshot(snapshot, session, now, ...)` is the shared boundary. It accepts only already-grouped, accepted giveaways and their persisted exact `source_product_id`.
- Choosing `igdb` writes `unresolved / provider_not_ready` for Epic/GOG and makes zero ITAD calls. Switching back to `itad` restores the original adapter and optionally uses the still-fresh exact-provider cache. Direct first-party Steam appids remain independent of the cross-store provider, without invoking it.
- Future IGDB work requires a separate accepted adapter and explicit credential contract; none is implemented or silently substituted here.

## 2. Active exact ITAD implementation

- `scripts/giveaway_identity_itad.py` uses official `GET /service/shops/map/v1`, selecting only a unique exact store name for Steam/Epic/GOG (no guessed numeric shop identifiers).
- `POST /lookup/id/shop/{shopId}/v1` takes precisely the Epic `offer_id` extracted from the persisted `namespace:offer_id`, or GOG's exact numeric `source_product_id`; requires exactly the request key and one UUID.
- `POST /lookup/shop/{shopId}/id/v1` takes precisely that UUID and accepts only **one** `app/<positive digits>` result. `sub/`, `bundle/` and other IDs never become an appid. Zero/multiple/app-invalid/unsupported/schema-invalid/HTTP-failed replies stay unresolved.
- No title, slug, publisher, normalized name, fuzzy matching, manual game exceptions, search endpoints, ITAD price or deal ingestion.
- Normal calls are bounded to active accepted giveaway offers; cache `data/production/giveaways/v1/identity_cache.json`, TTL: resolved 168h, unresolved 24h. Provider transport failures are not cached.
- `scripts/giveaway_production.py` remains the **only canonical giveaway writer**; no new scheduler, queue or browser-side identity fetch. Only that writer calls `resolve_snapshot` and persists identity/lookup cache with existing `data/production/giveaways/**`.

## 3. Authentication, permission and attribution

Official API docs/OpenAPI: https://docs.isthereanydeal.com/ and https://github.com/IsThereAnyDeal/API/tree/master/docs/routes/lookup, namely `gid-by-shopid.v1.yaml` and `shopid-by-gid.v1.yaml`. Both lookup POST endpoints document unauthenticated `security: [{}]` as allowed, plus API-key query/header options. `GET /service/shops/map/v1` documents `security: []`. Thus **no secret is required under the current documented endpoints**; actual 2026-10-26 unauthenticated live traffic confirmed HTTP 200 on the shop-map and both lookup methods. Optional `ITAD_API_KEY` env produces `ITAD-API-Key` header if explicitly provisioned for the producer, never hardcoded or logged; normal GitHub Action currently uses documented unauthenticated mode and no new secret is needed. If live endpoint rejects unauthenticated requests despite OpenAPI, that is a follow-up credential/provisioning issue, not proof of authorization failure.

Provider permission: affirmative ITAD email 2026-09-03: “Hi, this is permitted. For details about authentication refer to docs.” Director classification `permission_confirmed`; preceding reports: `giveaway-identity-provider-alternatives-01.md`, `itad-terms-permission-prep-01.md`. UI conditionally displays a link **Game identity via IsThereAnyDeal** pointing to https://isthereanydeal.com/ on active giveaway list and details, without implying affiliation or republishing provider deals/prices. Real-device credit acceptance remains outstanding after deployment.

## 4. Exact identity/provenance contract

Persisted for each accepted offer:

```json
{
  "identity_resolution": {
    "schema_version": 1,
    "source_storefront": "epic | gog | steam",
    "source_product_id": "original exact persisted source product identity",
    "source_provider_product_id": "exact Epic offer ID or GOG catalog ID",
    "identity_provider": "itad",
    "provider_game_id": "ITAD UUID or null",
    "steam_appid": null,
    "status": "resolved | unresolved",
    "reason": "explicit resolution or failure reason",
    "provenance": {
      "authority": "source_exact_shop_id",
      "source_shop_id": null,
      "steam_shop_id": null,
      "lookup_forward": "/lookup/id/shop/{shopId}/v1",
      "lookup_reverse": "/lookup/shop/{shopId}/id/v1",
      "shop_map": "/service/shops/map/v1",
      "auth_route": "none_documented | ITAD-API-Key_header",
      "checked_at_utc": "ISO UTC",
      "api_docs": "https://docs.isthereanydeal.com/"
    }
  }
}
```

Values are illustrative **schema**, not a claimed live mapping. `steam_appid` is a positive integer only on successful exact unique resolution. Group-level `analysis_identity` is resolved only if all constituent offers resolve to the **same** exact Steam appid; title/publisher `meta-v1` grouping is explicitly not semantic authority. `giveaway_visual_handoff.py` revalidates per-offer receipts, provider and exact product IDs before projecting a trusted `analysis_identity` to the visual payload. The provider-neutral result is all downstream analysis sees.

## 5. Reuse of existing Steam analysis

- `scripts/giveaway_analysis_reuse.py::attach` reads the **precomputed current canonical Steam cards** from the same final visual producer, keyed by exact `base_appids` only and requiring one unique `analyzed_fit` card; no independent Taste/description/negative semantic producer.
- Projects existing prepared Russian `summary` only when `description_status == ready_ru`; grounded `why_fit` from current canonical Taste explanation; and only negative `risks` whose per-item `risk_provenance.source` is in the existing `card_explanation_policy.GROUNDED_RISK_SOURCES` (otherwise no negative facts and incomplete).
- Explicit `analysis.status = ready | incomplete`, with reason and canonical family/description/pros/cons provenance. Exact Steam identity alone is **not** semantic readiness. If canonical analyzed card is absent or ambiguous, facts remain unavailable, even if the title matches.
- `scripts/build_final_visual_payload.py` attaches it in the existing full and giveaway-only paths without touching paid rankings. `web/giveaway-ui.js` displays only `analysis.status == ready` with exactly matching resolved AppID; incomplete/mismatched cases show the existing incomplete explanation.
- Current acceptance bound: reuses already prepared canonical analyzed cards **when present**. Does not create a separate analysis backlog or claim that all Epic/GOG games have canonical descriptions/Taste; broader semantic intake is owned by the existing producers.

## 6. Bounded proof and regressions

- `scripts/test_giveaway_production.py`: deterministic official-response-shape Epic exact offer-ID -> UUID -> `app/738520` fixture, cache reuse (zero further network), `igdb` switch (zero ITAD calls, explicit `provider_not_ready`), switch back to `itad`, GOG numeric-product fixture, ambiguous/missing/wrong-type/unexpected title input fail closed and no price endpoints.
- `scripts/test_giveaway_visual_handoff.py`: exact receipt acceptance, provider/AppID mismatch rejection, ITAD credit, precomputed canonical Russian description/Taste positives/grounded negatives, title-only nonmatch, duplicate canonical card ambiguity, negative provenance fail closed.
- `web/giveaway-ui.test.js`: ready analysis details only on matching exact appid, explicit unavailable fallback on mismatch/not-ready, ITAD credit and unchanged non-authoritative title data.
- The original deterministic fixtures were not production evidence. **Subsequent live proof is recorded in Section 6A below.** Current canonical giveaway snapshot `data/production/giveaways/v1/current.json` blob `a9c77ab39f887aa27767d664f403afecd08852d6`, generated `2026-10-25T22:38:21Z`, is **incomplete** due to stale Steam candidate input; contains 2 Epic active offers (Home - A Unique Horror Adventure and Sker Ritual), 0 active GOG. These exact Epic IDs were validated live; there is no fabricated current GOG production mapping.
- GitHub PR runs for initial implementation head `6f17a7321b5cce3371b51b264d4a86866cdf28f1`: Steam KZ production shortlist (regression), site publication resilience, Progressive PASS 2 core, package purchase value, task registry/page all **success**. Amended provenance tests are included in the succeeding dedicated PR test run `40351519439`; the superseded general Steam CI on the earlier intermediate commit was cancelled by the next push, not a test failure.
- **Dedicated read-only PR CI added:** `.github/workflows/validate-giveaway-identity.yml`; no schedule, production collection, persistence or secret. Run [40351519439](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40351519439), based on source commit `2301072ab1b85a7b972fb2f22021176a6b478376`: **success**, including actual Python compilation, `scripts/test_giveaway_production.py`, `scripts/test_giveaway_visual_handoff.py`, `scripts/test_giveaway_igdb_identity_probe.py` and `node web/giveaway-ui.test.js`.
- Normal CI success is deterministic regression; the **separate, explicitly bounded live endpoint proof** is evidenced in Section 6A. Neither establishes main-production publication or user/device acceptance.

## 6A. Actual live ITAD exact-ID acceptance — 2026-10-26

**Execution and containment.** GitHub Actions run [40359222508](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40359222508), job `121699813953`, commit `53f96bbae574b7654121ee81406f60a5b0b4a380`: **success**, including all existing Python/Node deterministic regressions and one real, read-only bounded provider probe. UTC receipt: `2026-10-26T16:27:12.058171+00:00`. No application/Steam/GOG production source refresh, no snapshot/cache writing, no browser fetching, no new scheduler, no PR merge and no provider pricing/deal access. One map GET + six lookup POSTs = **7 requests, all HTTP 200**, with `auth_route=official_documented_none` and no credential. Only exact persisted Epic IDs from the existing main giveaway snapshot were production-scope candidates.

**Shop-map discovery and necessary correction.** First bounded attempt [40358787597](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40358787597) returned `HTTP 200` on `/service/shops/map/v1` but failed `shop_id_missing_or_ambiguous:epic`: config incorrectly anticipated `Epic Games Store`. A diagnostic map read [40358968442](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40358968442) confirmed real exact names/IDs `Epic Game Store=16`, `GOG=35`, `Steam=61`. Changed only `config/giveaway_identity_provider.json` and its isolated matching regression fixture (`scripts/test_giveaway_production.py`) to the confirmed exact Epic title. No guessed ID hardcoded in the runtime.

**Live lookups and actual responses:**

| Source / production authority | Exact shop product ID used | ITAD UUID returned via `/lookup/id/shop/{shopId}/v1` | Exact `/lookup/shop/61/id/v1` Steam AppID | Verdict |
|---|---|---|---|---|
| Current Epic giveaway **Home - A Unique Horror Adventure**, `source_product_id=c7e46cce751b40b6937e878abd0fc531:06190191cede42afb633fe89ef08c27e` | Epic offer `06190191cede42afb633fe89ef08c27e`, shop `16` | `018d937e-efe0-70c4-a142-bd045d56c833` | `app/215670` | **resolved / exact_unique**, authenticated by exact provider ID rather than name |
| Current Epic giveaway **Sker Ritual**, `source_product_id=156c17659ff0468bb533eba104a1f19f:6aab3ddef4f84fbc9dd81c60f9d8549c` | Epic offer `6aab3ddef4f84fbc9dd81c60f9d8549c`, shop `16` | `018d937f-65f6-715d-b82a-5cedffbe94c8` | `app/1492070` | **resolved / exact_unique**, authenticated by exact provider ID rather than name |
| **Historical/noncanonical GOG API diagnostic only**, no active GOG giveaway in source snapshot | GOG product `2104548474`, shop `35` (from earlier bounded ITAD provider alternatives evidence) | `018d937f-2102-72e8-947d-71a97f46e99e` | `app/738520` | **resolved / exact_unique** transport proof; **NOT** a production-authorized current GOG giveaway |

The historical GOG lookup is **strictly a disposable diagnostic**. It must not be introduced as an accepted giveaway, hand-mapped special case, durable canonical mapping, analysis authority or claim that GOG has an active giveaway. The only production sample was two exact Epic IDs persisted by the existing canonical writer.

**What remains unproven:** snapshot `snapshot_status=incomplete` (Steam health failed because its discovery source was stale ~1129.9h at 2026-10-25 22:38 UTC); the actual GitHub-owned production writer on `main` has not been run with this branch, canonical cache/receipt persistence on real production is not verified, full refreshed visual delivery and phone browser acceptance are not verified. ITAD API auth/lookup and exact product map **are verified**, including current Epic cases. UI positives/negatives and Russian description depend on availability of a unique ready canonical analyzed Steam card; live mapping alone does not guarantee those facts.

**One-off probe lifecycle.** The live request block was **removed from** `.github/workflows/validate-giveaway-identity.yml` after receiving the durable GitHub Actions receipt, in commit `50c9f28a8c6d970cc99247fb18dcf6061de345cf`. The normal deterministic PR validation remains, with **no further live provider requests or recurring probe**. The complete live evidence remains available in job logs `121699813953` (`ITAD_LIVE_PROBE_RECEIPT`) and in this report.

## 7. User action and acceptance

- **User secret action required now: no**, official ITAD exact lookup permits unauthenticated use; no key requested.
- **Ready for director code review, with current live provider verification:** yes, PR #312. **Ready to assert main production success or device acceptance:** no. After director review and authorized merge, only the existing GitHub-owned ordinary `Steam KZ production shortlist` run on `main` may persist the exact receipts and cache; verify real source health, provider-neutral per-offer `identity_resolution`, group identity, completed snapshot, visual handoff and real device attribution/analysis behavior. Stale or ambiguous cases stay unresolved; no title fallback or ITAD price lookup. No such production action was performed here.
- Production main is not modified by this PR before merge; no manual per-game production writing or semantic worker was performed.

## 8. Boundaries, follow-up notes and navigation

No change to Steam 50% discovery/top100, Dossier V2, director registry/Board, ranking policy, task scheduling or another writer. Shared `CURRENT_TASK.md` and `PROJECT_ROUTES.md` were not edited because concurrent workers must not overwrite one another. Bounded navigation candidate for Director: `config/giveaway_identity_provider.json` -> `scripts/giveaway_identity.py` -> `scripts/giveaway_identity_itad.py` -> `scripts/giveaway_production.py` -> `scripts/giveaway_visual_handoff.py` -> `scripts/giveaway_analysis_reuse.py` -> `scripts/build_final_visual_payload.py` -> `web/giveaway-ui.js`. The shared workflow `.github/workflows/steam-test.yml` has pre-existing path filters; any later broadening for **new provider-only files** should be coordinated with the concurrently active Steam discovery worker rather than edited by this chat.

Time spent: required source-of-truth protocol, exact API OpenAPI request/response/auth verification, concurrent ownership preflight, canonical analysis boundaries and regression checks. The new small config/interface and this route report avoid rediscovery in subsequent ITAD tasks.

## Exact refs

- PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/312
- Branch: `implement/giveaway-itad-identity-01`
- Base main at implementation start: `6709956d5dc1d5b729d48de42ca727d33c149f16`
- Last source/test change before the live probe: `29383cad6ca2f09b60482e4b127afb05d7334e34`
- Verified Epic shop-name fix and matching test: `5a0ba48132e1e8871aaaa8c098f8d1a5f01e9dd5` and `53f96bbae574b7654121ee81406f60a5b0b4a380`
- Real successful live API receipt: run `40359222508`, job `121699813953`, exact UTC `2026-10-26T16:27:12.058171+00:00`
- One-shot external probe removed: `50c9f28a8c6d970cc99247fb18dcf6061de345cf`
- Dedicated PR-only test workflow source commit: `2301072ab1b85a7b972fb2f22021176a6b478376`; passing run `40351519439`
- New provider config: `config/giveaway_identity_provider.json`
- Adapter: `scripts/giveaway_identity_itad.py`
- Neutral boundary: `scripts/giveaway_identity.py`
- Single writer: `scripts/giveaway_production.py`
- Visual boundary: `scripts/giveaway_visual_handoff.py`
- Canonical reuse: `scripts/giveaway_analysis_reuse.py`
- Card producer: `scripts/build_final_visual_payload.py`
- Presentation: `web/giveaway-ui.js`
- Tests: `scripts/test_giveaway_production.py`, `scripts/test_giveaway_visual_handoff.py`, `web/giveaway-ui.test.js`
- Main task file blob: `7cd7741286f08dc61b0e98f59d72632076062837`

## Final status

`complete` — implementation, deterministic regression and bounded **real ITAD mapping** for both current Epic offers plus a non-production GOG transport case are confirmed. Main production writer/cache persistence, complete source snapshot, site publication and real-device credit still require separately authorized director acceptance.
