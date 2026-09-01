# WORKER TASK — CHAT 2

Task ID: `duration-igdb-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/duration-igdb-implement-01.md`
Previous report: `reviews/worker_reports/duration-contract-01.md`

## Goal

Implement the canonical IGDB duration enrichment path defined by `config/duration_enrichment_contract.json` so GitHub/GitHub Actions, not ChatGPT, collects and persists structured duration data and feeds it into final ranking before the legacy text fallback.

Do not manually look up duration for individual games.

## Current project commercial status

The project is currently **personal / non-commercial**. Read `COMMERCIALIZATION_GUARD.md` and treat that file as a hard future monetization stop.

This current non-commercial status may be used only for the present implementation/provisioning review. It must not be generalized to future commercial use.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `COMMERCIALIZATION_GUARD.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/final_ranking_policy.json`
- `config/duration_enrichment_contract.json`
- `reviews/worker_reports/duration-contract-01.md`

## Architecture preflight

Preserve the canonical ownership model:
- GitHub owns exact scope, missing/stale selection, ordering, retries, completeness, cache merge, normalization and downstream rebuild.
- IGDB collection is `GitHub-direct`.
- scheduled/interactive ChatGPT does not collect duration facts.
- provider rate limits are access constraints, not production quotas.
- `unknown = 2/3` scoring is unchanged.

## What to implement

1. **GitHub-owned IGDB client path**
   - OAuth client-credentials flow through runtime secrets only;
   - current IGDB API schema;
   - no committed credentials/tokens.

2. **Exact Steam identity mapping**
   - input key = Steam appid;
   - only validated IGDB External Game mapping for Steam using current `external_game_source` model;
   - no title/fuzzy matching;
   - deprecated `category` assumptions prohibited.

3. **Structured duration retrieval**
   - read `game_time_to_beats`;
   - preserve `hastily`, `normally`, `completely`, `count`, provider IDs/timestamps/checksum where available;
   - normalize `normally_seconds / 3600` as canonical `estimated_duration_hours` without hiding raw values.

4. **Canonical cache**
   - GitHub-owned `data/cache/duration_estimates.json` or exact path specified by the contract;
   - provenance + selected metric + fetch timestamp + provider/schema identity;
   - distinguish confirmed, durable unresolved states, and transient operational failures exactly as contract requires;
   - transient errors must not overwrite confirmed data.

5. **Missing/stale scope generation**
   - GitHub determines exact current required Steam appids;
   - fetch first-required/missing and contract-defined stale records only;
   - no full nightly refetch of known stable rows;
   - no interactive per-game queue.

6. **Final builder integration**
   - validated structured IGDB duration first;
   - legacy explicit-text extraction only as low-confidence compatibility fallback if structured value unavailable;
   - otherwise `unknown`;
   - scoring math/weights/bands remain unchanged.

7. **Tests/validation**
   - exact mapping acceptance/rejection;
   - seconds->hours normalization;
   - cache merge and error-state behavior;
   - structured value precedence over text fallback;
   - unknown fail-safe remains `2/3`;
   - no deprecated IGDB schema assumption.

## Provisioning / live connectivity

Before enabling real production collection, verify current IGDB/Twitch terms for the project's present **personal/non-commercial** use and identify any required attribution even for that use.

### Credentials handling

If the required Twitch/IGDB Client ID / Client Secret are already available to GitHub Actions under suitable secret names, perform one bounded GitHub Actions OAuth + authenticated IGDB connectivity test and continue acceptance.

If credentials are **not** available:
- implement everything that can be completed safely without them;
- do not invent credentials or test with another account;
- do not ask interactive ChatGPT to fetch duration instead;
- report exact credential/account provisioning steps the user must perform and the exact GitHub secret names expected by the implementation;
- leave production collection disabled/fail-safe until credentials exist;
- status should reflect the real remaining block (`needs_user_decision` or `blocked` as appropriate), not claim `complete` production enablement.

## Production handling

Do NOT manually populate duration values for the catalog.

If credentials exist and the canonical GitHub workflow can run, a bounded implementation/acceptance run may fetch data through the implemented GitHub-owned path. The full production scope must still be selected and processed by GitHub automation, not by this worker manually.

Do not introduce a daily game-count quota or ChatGPT backlog.

## Hard boundaries

Do not change:
- duration scoring weights/bands or `unknown = 2/3`;
- Taste;
- Russian descriptions;
- package economics/purchase route;
- UI except strictly necessary field compatibility if canonical producer contract requires it;
- commercial status guard.

Do not use RAWG playtime as duration fallback.
Do not scrape HowLongToBeat.
Do not perform title-based fuzzy mapping.

## Done when

Either:

### Full implementation complete
- deterministic GitHub-owned IGDB collection/cache/final-builder path implemented;
- required credentials were already provisioned;
- bounded GitHub Actions OAuth/API connectivity test passes;
- relevant tests green;
- production path is ready under the current non-commercial assumption;

or:

### Implementation complete but provisioning blocked
- all code/cache/schema/workflow integration possible without secrets is implemented and tested synthetically;
- exact credential/attribution provisioning requirement is documented;
- production collection remains safely disabled until user supplies GitHub Secrets;
- no duration data was manually filled.

## Report format

Save:
`reviews/worker_reports/duration-igdb-implement-01.md`

### Task
What was implemented.

### Verified facts
Current ownership, non-commercial assumption, provider/identity behavior.

### Changes
Exact files and commits.

### Validation
Tests/workflow refs and whether real OAuth/API connectivity ran.

### Provisioning
State clearly:
- terms/attribution conclusion for current personal/non-commercial use;
- expected GitHub secret names;
- whether secrets were present;
- exact user action if still needed.

### Production handling
What GitHub automation did or is ready to do; explicitly state that no manual catalog duration fill was performed.

### Unresolved
`none` or exact remaining provisioning/runtime gap.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and commit refs.