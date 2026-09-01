# WORKER TASK — CHAT 2

Task ID: `duration-contract-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/duration-contract-01.md`
Previous reports:
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- `reviews/worker_reports/duration-source-recon-01.md`
- `reviews/worker_reports/duration-provider-recon-01.md`

## Goal

Добавить canonical duration-source/enrichment contract, выбрав IGDB `game_time_to_beats` как authoritative primary provider и GitHub-direct как executor class, без изменения scoring и без получения конкретных duration values в этой задаче.

## Architecture decision to encode

- Primary provider: IGDB official API, endpoint/schema `game_time_to_beats`.
- Executor: GitHub/GitHub Actions direct server-side collection.
- Scheduled/interactive ChatGPT не используется для primary duration collection.
- GitHub владеет exact scope, identity mapping, rate limiting, retries, completeness, normalization, validation, cache merge, freshness and downstream rebuild.
- Current `unknown = 2/3` remains fail-safe and scoring math is unchanged.
- RAWG average playtime is not equivalent to completion duration and is not a fallback provider.
- HowLongToBeat scraping/unofficial wrappers are not an authorized path without separate documented permission/official API.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/final_ranking_policy.json`
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- `reviews/worker_reports/duration-source-recon-01.md`
- `reviews/worker_reports/duration-provider-recon-01.md`

## Contract requirements

Add a canonical contract/config/schema sufficient for later IMPLEMENT. It must define at minimum:

1. **Authority/provider:** IGDB `game_time_to_beats` primary authoritative provider.
2. **Identity:** canonical input identity = Steam appid; mapping accepted only through proven IGDB External Game mapping to Steam using current `external_game_source` model, not deprecated `category`; ambiguous/title-only fuzzy mapping fails closed.
3. **Raw provider fields:** preserve IGDB game id, Steam mapping identity, `hastily`, `normally`, `completely`, `count`, provider timestamps/checksum where available, fetch timestamp, provider/schema version.
4. **Normalized estimate:** seconds -> hours deterministic conversion; canonical `estimated_duration_hours` selects `normally`; preserve `selected_metric` and raw values.
5. **Confidence/provenance:** `count` preserved. Do not invent a numerical confidence threshold unless existing policy authorizes one. Missing/invalid/ambiguous mapping => unresolved/unknown.
6. **GitHub scope owner:** GitHub determines missing/stale required keys from current production scope. No chat-owned queue or daily item quota.
7. **Rate/access semantics:** GitHub direct HTTPS/OAuth; respect provider 4 req/s and <=8 concurrent requests as provider limits, not production quotas.
8. **Credentials:** Twitch/IGDB Client ID/Secret only in GitHub Secrets/runtime; never committed. OAuth token refresh is GitHub-owned implementation detail.
9. **Canonical cache:** define GitHub-owned durable duration cache/artifact schema/path with provenance, negative/error state distinctions, validation and merge semantics.
10. **Freshness:** long-lived data. Fetch on first required appearance/missing record; refresh under explicit long-lived stale policy and/or provider update evidence. Do not refetch all known rows every nightly cycle.
11. **Negative states:** distinguish provider row missing, Steam mapping missing, ambiguous mapping, invalid values, auth/transport failure. None becomes `0 hours`.
12. **Final handoff precedence:** validated structured IGDB duration -> optional explicitly approved legacy text-extraction compatibility fallback -> unknown. Prefer defining whether text fallback remains and its provenance/low-confidence status rather than leaving implicit behavior.
13. **Scoring:** no change to final ranking weights/bands or `unknown = 2/3`.
14. **Schema migration guard:** validate current IGDB `external_game_source` identity; do not hardcode deprecated enum assumptions.
15. **Licensing/attribution provisioning gate:** contract must require verification of applicable IGDB/Twitch attribution/partnership/commercial-use obligations before enabling production collection. Do not assume project monetization status. This gate may remain `provisioning_required` until explicitly satisfied.
16. **Connectivity gate:** later IMPLEMENT acceptance must include real GitHub Actions auth/connectivity check after secrets are provisioned; contract task itself must not request/commit secrets.

## What may change

Allowed:
- new duration source/enrichment contract/config/schema files;
- minimal route/decision docs;
- minimal daily/execution contract references required to explicitly authorize GitHub-direct duration collection and cache ownership;
- schema/contract tests.

Not in this task:
- IGDB API client implementation;
- GitHub secrets provisioning;
- real provider calls;
- per-game duration lookup/catalog sampling;
- cache population;
- final builder integration code;
- scoring/UI/Taste/descriptions/package changes.

## Done when

- IGDB + GitHub-direct ownership is canonical and unambiguous;
- raw/normalized/cache/freshness/error semantics are explicit;
- provider licensing/provisioning and credentials are explicit gates rather than assumptions;
- no duration values were fetched;
- contract/schema tests pass.

## Report format

Save:
`reviews/worker_reports/duration-contract-01.md`

### Task
What canonical contract was added.

### Verified facts
Provider/executor/identity/freshness decisions.

### Changes
Exact files.

### Validation
Contract/schema consistency tests.

### Provisioning gates
Credentials/licensing/attribution/connectivity conditions still required before production enablement.

### Unresolved
Only real remaining gaps.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded IMPLEMENT for GitHub-owned IGDB collection/cache/final-builder integration after required provisioning gates are satisfiable.

Final response must include report path and commit refs.