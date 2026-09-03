# WORKER TASK — GIVEAWAY IDENTITY PROVIDER IMPLEMENT 01

Task ID: `giveaway-itad-identity-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/giveaway-itad-identity-implement-01.md`

## Source decision

Direct continuation of:
- `reviews/worker_reports/giveaway-identity-provider-alternatives-01.md`
- `reviews/worker_reports/itad-terms-permission-prep-01.md`
- `reviews/worker_reports/giveaway-analysis-identity-recon-01.md`

Provider permission is explicit. User supplied ITAD reply on 2026-09-03:

> Hi, this is permitted. For details about authentication refer to docs.

Director classification: `permission_confirmed`.

User architecture decision: use ITAD now, but make cross-store identity provider selection intentionally switchable so a later accepted IGDB route can replace ITAD without rewiring the giveaway pipeline.

## Architecture requirement — one active provider, simple switch

Introduce one canonical provider-selection setting equivalent to:

`giveaway_identity_provider = "itad"`

The exact config file/location should reuse an existing suitable config surface when possible; if none exists, add one minimal canonical config contract.

Required semantics:
- exactly one active cross-store identity provider at a time;
- active value now: `itad`;
- reserve/recognize `igdb` as the intended future provider name;
- **no automatic fallback**, chaining, voting, or dual-provider resolution;
- selecting an unavailable/unimplemented provider must fail closed with an explicit provider-not-ready/unavailable status;
- browser/UI must not select providers dynamically.

Do **not** implement the IGDB provider route in this task unless it already exists behind the exact same provider-neutral interface with no new credentials/blocker. The purpose now is to make the pipeline provider-independent and implement only the accepted ITAD adapter. Later IGDB work should require adding/accepting its adapter and changing one config value, not changing downstream giveaway identity/analysis code.

## Provider-neutral identity interface

Downstream giveaway production must consume one common result shape independent of ITAD/IGDB. It must carry at minimum:
- source storefront/provider (`epic` / `gog`);
- exact source provider product/offer ID;
- selected identity provider (`itad` now; `igdb` reserved);
- provider-native game identity;
- exact resolved Steam appid when uniquely resolved;
- `resolved | unresolved` status plus reason;
- provenance/auth route/timestamp sufficient for audit.

Downstream code that attaches Steam family, Russian description, Taste positives and grounded negatives must not branch on ITAD-vs-IGDB details. It should consume only this common resolved Steam identity contract.

## Current implementation goal

Implement the smallest safe active route:

`exact Epic/GOG provider ID -> selected provider adapter (ITAD) -> ITAD exact shop-ID lookup -> ITAD game identity -> exact Steam shop ID/appid -> common provider-neutral identity result -> existing canonical Steam family / description / Taste path`

The purpose is only exact identity resolution for giveaway analysis. ITAD price/deal data is out of scope.

## Authentication

Use current official ITAD API documentation as authority.

- Determine the currently documented authentication mode for the exact lookup endpoints used.
- If an API key/app registration is required or recommended for production use, support it through GitHub Actions secrets/config only; never hardcode credentials and never ask the user to paste secrets into chat, repo files, issues, logs or workflow output.
- If exact lookup endpoints are officially allowed unauthenticated, that may be used only if current docs clearly support it.
- Fail closed on missing required credentials.

Record exact auth conclusion and official doc ref in the report.

Future `igdb` selection must use its own already-known GitHub-secret contract when/if later implemented; ITAD credentials must not be reused as generic provider credentials.

## Exact identity rules

Identity authority must remain strict:
- start only from persisted exact Epic/GOG provider IDs already owned by giveaway production;
- use ITAD exact shop-ID lookup(s), not title search;
- require one unambiguous ITAD game identity;
- require one exact Steam shop ID/appid;
- zero, multiple, ambiguous or unsupported mappings remain unresolved;
- never use title, normalized title, publisher, slug, fuzzy matching, general web search or manual per-game exceptions as identity authority.

The same strictness is part of the provider-neutral contract and must apply to any future provider adapter.

## Production ownership

Preserve current architecture:
- `scripts/giveaway_production.py` remains the single canonical giveaway writer;
- GitHub/GitHub Actions owns full production scope, persistence, retries/completeness and rebuild;
- browser performs no live external identity-provider fetch;
- no second scheduler, queue, semantic runtime or giveaway writer;
- reuse existing canonical Steam appid/family path, Russian description, Taste positive evidence and grounded negative readiness once exact Steam identity is resolved.

Do not create a second Taste/description analysis system for giveaways.

## Terms / attribution

The ITAD permission blocker is closed by the provider reply above.

Still comply with current ITAD Terms/docs:
- preserve any required attribution/link if current Terms require it;
- do not imply affiliation;
- do not ingest or republish ITAD deal/price data under this task;
- keep use bounded, cached and low-frequency.

If current Terms require an attribution change to the published giveaway surface, implement only the smallest compliant attribution required and flag any user-visible change for real-device acceptance. Do not redesign the UI.

## Required implementation behavior

1. Add one provider-neutral resolver boundary/interface plus one canonical provider-selection setting.
2. Implement the active `itad` adapter behind that boundary.
3. Resolve exact Epic/GOG provider IDs to exact Steam appids through ITAD.
4. Integrate the common resolved Steam identity into the existing giveaway production pipeline and canonical analysis reuse path.
5. Persist explicit provider-neutral identity-resolution status/provenance sufficient to audit:
   - source provider + exact source provider ID;
   - selected identity provider;
   - provider-native game identity;
   - exact Steam appid when resolved;
   - status/reason when unresolved;
   - auth/provenance route used.
6. Preserve fail-closed behavior for unresolved/ambiguous mappings or unavailable selected provider.
7. Cache/reuse results appropriately so normal runs do not perform unnecessary repeated lookup traffic.
8. Prove downstream analysis code does not need provider-specific ITAD branches after the common identity result is produced.

## Bounded proof

Use the smallest current giveaway sample sufficient to prove the route. The previously observed Epic sample may be reused only if still canonical/current.

Prove at least:
- one exact successful Epic -> ITAD -> Steam mapping if a current resolvable item exists;
- unresolved/ambiguous fail-closed behavior;
- selecting an unavailable `igdb` provider does not silently fall back to ITAD and fails closed explicitly;
- switching back to `itad` restores the active adapter without downstream pipeline changes;
- no title/fuzzy fallback;
- no ITAD price/deal ingestion;
- canonical giveaway writer remains single owner;
- downstream giveaway card analysis can reuse existing canonical Steam description/Taste/grounded-negative readiness when available.

For GOG, prove current bounded evidence if available; otherwise focused fixture/contract validation is acceptable, but do not fabricate a production mapping.

## Validation

Run focused tests plus existing relevant giveaway/production tests.

If ITAD authentication requires a user-created credential that is not available:
- implement all safe provider switch/interface + credential plumbing/tests that do not require the secret;
- stop as `needs_user_action` with exact steps for creating/storing the credential in GitHub Secrets;
- do not ask for the secret value in chat.

## Boundaries

Do NOT:
- implement simultaneous ITAD+IGDB resolution;
- add automatic provider fallback;
- use Twitch/IGDB as primary while `itad` is selected;
- add title/fuzzy/manual mapping fallbacks;
- ingest ITAD prices/deals;
- create another giveaway writer/scheduler/queue;
- fetch providers from browser JS;
- change Taste/ranking policy;
- process the giveaway catalog manually item-by-item;
- broaden into unrelated visual-freshness or semantic-runtime fixes.

## Required result

Report:
1. exact provider-neutral interface and config switch;
2. exact ITAD implementation;
3. exact authentication mode and credential handling;
4. exact identity/provenance contract;
5. bounded proof including unavailable-IGDB fail-closed + ITAD switch behavior;
6. unresolved/fail-closed behavior;
7. whether user action is required;
8. whether production/follow-up acceptance is ready.

Status exactly one:
- `complete`
- `needs_user_action`
- `blocked`
- `needs_followup_fix`

## Completion

Save:
`reviews/worker_reports/giveaway-itad-identity-implement-01.md`

Final answer must state exact report path, status and exact refs.