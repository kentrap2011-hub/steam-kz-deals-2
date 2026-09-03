# WORKER TASK — GIVEAWAY ITAD IDENTITY IMPLEMENT 01

Task ID: `giveaway-itad-identity-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/giveaway-itad-identity-implement-01.md`

## Source decision

Direct continuation of:
- `reviews/worker_reports/giveaway-identity-provider-alternatives-01.md`
- `reviews/worker_reports/itad-terms-permission-prep-01.md`

Provider permission is now explicit. User supplied ITAD reply on 2026-09-03:

> Hi, this is permitted. For details about authentication refer to docs.

Director classification: `permission_confirmed`.

Do not re-open provider selection or Twitch/IGDB unless ITAD implementation hits a new concrete blocker.

## Goal

Implement the smallest safe primary cross-store identity route:

`exact Epic/GOG provider ID -> IsThereAnyDeal exact shop-ID lookup -> ITAD game identity -> exact Steam shop ID/appid -> existing canonical Steam family / description / Taste path`

The purpose is only exact identity resolution for giveaway analysis. ITAD price/deal data is out of scope.

## Authentication

Use the current official ITAD API documentation as authority for authentication.

- Determine the currently documented authentication mode for the exact lookup endpoints used by this route.
- If an API key/app registration is required or recommended for production use, support it through GitHub Actions secrets/config only; never hardcode credentials and never ask the user to paste secrets into chat, repo files, issues, logs or workflow output.
- If the exact lookup endpoints are officially allowed unauthenticated, that may be used only if the current docs clearly support it for this use.
- Fail closed on missing required credentials.

Record the exact auth conclusion and official doc ref in the report.

## Exact identity rules

Identity authority must remain strict:
- start only from persisted exact Epic/GOG provider IDs already owned by the giveaway production path;
- use ITAD exact shop-ID lookup(s), not title search;
- require one unambiguous ITAD game identity;
- require one exact Steam shop ID/appid;
- zero, multiple, ambiguous or unsupported mappings remain unresolved;
- never use title, normalized title, publisher, slug, fuzzy matching, general web search or manual per-game exceptions as identity authority.

## Production ownership

Preserve current architecture:
- `scripts/giveaway_production.py` remains the single canonical giveaway writer;
- GitHub/GitHub Actions owns full production scope, persistence, retries/completeness and rebuild;
- browser performs no live ITAD fetch;
- no second scheduler, queue, semantic runtime or giveaway writer;
- reuse existing canonical Steam appid/family path, Russian description, Taste positive evidence and grounded negative readiness once exact Steam identity is resolved.

Do not create a second Taste/description analysis system for giveaways.

## Terms / attribution

The permission blocker is closed by the provider reply above.

Still comply with the current ITAD Terms/docs:
- preserve any required attribution/link if the current Terms require it;
- do not imply affiliation;
- do not ingest or republish ITAD deal/price data under this task;
- keep use bounded, cached and low-frequency.

If current Terms require an attribution change to the published giveaway surface, implement only the smallest compliant attribution required and flag any user-visible change for real-device acceptance. Do not redesign the UI.

## Required implementation behavior

1. Add/reuse one bounded ITAD client/lookup helper appropriate for GitHub production execution.
2. Resolve exact Epic/GOG provider IDs to exact Steam appids through ITAD.
3. Integrate that resolved Steam identity into the existing giveaway production pipeline and canonical analysis reuse path.
4. Persist explicit identity-resolution status/provenance sufficient to audit:
   - source provider + exact source provider ID;
   - ITAD identity;
   - exact Steam appid when resolved;
   - status/reason when unresolved;
   - provider/auth route used.
5. Preserve fail-closed behavior for unresolved/ambiguous mappings.
6. Cache/reuse results appropriately so normal runs do not perform unnecessary repeated lookup traffic.

## Bounded proof

Use the smallest current giveaway sample sufficient to prove the route. The previously observed current Epic sample may be reused if still canonical/current, but do not assume stale giveaway state without checking the current bounded production input.

Prove at least:
- one exact successful Epic -> ITAD -> Steam mapping if a current resolvable item exists;
- unresolved/ambiguous fail-closed behavior;
- no title/fuzzy fallback;
- no ITAD price/deal ingestion;
- canonical giveaway writer remains single owner;
- downstream giveaway card analysis can reuse existing canonical Steam description/Taste/grounded-negative readiness when available.

For GOG, prove the implementation path with current bounded evidence if available; if there is no current GOG giveaway sample, focused fixture/contract validation is acceptable, but do not fabricate a production mapping.

## Validation

Run focused tests plus existing relevant giveaway/production tests.

If authentication requires a user-created ITAD credential that is not available:
- implement all safe credential plumbing/tests that do not require the secret;
- stop as `needs_user_action` with exact steps for creating/storing the credential in GitHub Secrets;
- do not ask for the secret value in chat.

## Boundaries

Do NOT:
- use Twitch/IGDB as primary while ITAD is available;
- add title/fuzzy/manual mapping fallbacks;
- ingest ITAD prices/deals;
- create another giveaway writer/scheduler/queue;
- fetch ITAD from browser JS;
- change Taste/ranking policy;
- process the giveaway catalog manually item-by-item;
- broaden into unrelated visual-freshness or semantic-runtime fixes.

## Required result

Report:
1. exact implementation;
2. exact authentication mode and credential handling;
3. exact identity/provenance contract;
4. bounded current proof and tests;
5. unresolved/fail-closed behavior;
6. whether user action is required;
7. whether production/follow-up acceptance is ready.

Status exactly one:
- `complete`
- `needs_user_action`
- `blocked`
- `needs_followup_fix`

## Completion

Save:
`reviews/worker_reports/giveaway-itad-identity-implement-01.md`

Final answer must state exact report path, status and exact refs.