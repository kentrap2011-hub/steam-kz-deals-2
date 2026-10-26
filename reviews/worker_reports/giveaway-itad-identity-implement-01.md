# giveaway-itad-identity-implement-01

Date: 2026-10-26  
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`  
Mode: `IMPLEMENT`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/312  
Implementation branch: `implement/giveaway-itad-identity-01`

## Status

**`complete` (implementation and deterministic regression), with explicit live-acceptance limitation.** No main production run, deployed website or live ITAD exact lookup was executed by this PR. Do not claim a current-game live mapping or real-device acceptance.

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

Official API docs/OpenAPI: https://docs.isthereanydeal.com/ and https://github.com/IsThereAnyDeal/API/tree/master/docs/routes/lookup, namely `gid-by-shopid.v1.yaml` and `shopid-by-gid.v1.yaml`. Both lookup POST endpoints document unauthenticated `security: [{}]` as allowed, plus API-key query/header options. `GET /service/shops/map/v1` documents `security: []`. Thus **no secret is required under the current documented endpoints**. Optional `ITAD_API_KEY` env produces `ITAD-API-Key` header if explicitly provisioned for the producer, never hardcoded or logged; normal GitHub Action currently uses documented unauthenticated mode and no new secret is needed. If live endpoint rejects unauthenticated requests despite OpenAPI, that is a follow-up credential/provisioning issue, not proof of authorization failure.

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
- These fixture IDs are deliberately **not production evidence**. Current canonical giveaway snapshot `data/production/giveaways/v1/current.json` blob `a9c77ab39f887aa27767d664f403afecd08852d6`, generated `2026-10-25T22:38:21Z`, is **incomplete**; contains 2 Epic active offers (Home - A Unique Horror Adventure and Sker Ritual), 0 active GOG. There is no proven live ITAD mapping for either current Epic offer, and no fabricated GOG production mapping.
- GitHub PR runs for initial implementation head `6f17a7321b5cce3371b51b264d4a86866cdf28f1`: Steam KZ production shortlist (regression), site publication resilience, Progressive PASS 2 core, package purchase value, task registry/page all **success**. Final amended provenance test head `29383cad6ca2f09b60482e4b127afb05d7334e34` has separate CI run (inspect before merge).
- CI success is deterministic regression, **not** live endpoint proof or user/device acceptance.

## 7. User action and acceptance

- **User secret action required now: no**, official ITAD exact lookup permits unauthenticated use; no key requested.
- **Ready for code review:** yes, PR #312. **Ready to assert live production success / device acceptance:** no. After review and merge, allow the existing GitHub-owned ordinary `Steam KZ production shortlist` run on `main` (no second scheduler) to attempt the two exact Epic ids; verify actual source status, `identity_resolution` including timestamp/Steam appid and cache; verify resulting complete snapshot, visual handoff and real device attribution/analysis behavior. If unmapped/ambiguous: retain unresolved; do not use title fallback. No live ITAD price lookup permitted.
- Production main is not modified by this PR before merge; no manual per-game production writing or semantic worker was performed.

## 8. Boundaries, follow-up notes and navigation

No change to Steam 50% discovery/top100, Dossier V2, director registry/Board, ranking policy, task scheduling or another writer. Shared `CURRENT_TASK.md` and `PROJECT_ROUTES.md` were not edited because concurrent workers must not overwrite one another. Bounded navigation candidate for Director: `config/giveaway_identity_provider.json` -> `scripts/giveaway_identity.py` -> `scripts/giveaway_identity_itad.py` -> `scripts/giveaway_production.py` -> `scripts/giveaway_visual_handoff.py` -> `scripts/giveaway_analysis_reuse.py` -> `scripts/build_final_visual_payload.py` -> `web/giveaway-ui.js`. The shared workflow `.github/workflows/steam-test.yml` has pre-existing path filters; any later broadening for **new provider-only files** should be coordinated with the concurrently active Steam discovery worker rather than edited by this chat.

Time spent: required source-of-truth protocol, exact API OpenAPI request/response/auth verification, concurrent ownership preflight, canonical analysis boundaries and regression checks. The new small config/interface and this route report avoid rediscovery in subsequent ITAD tasks.

## Exact refs

- PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/312
- Branch: `implement/giveaway-itad-identity-01`
- Base main at implementation start: `6709956d5dc1d5b729d48de42ca727d33c149f16`
- Last source/test change before this report: `29383cad6ca2f09b60482e4b127afb05d7334e34`
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

`complete` — implementation and deterministic regression complete; live ITAD mapping / main publication / real-device credit require separate follow-up acceptance.
