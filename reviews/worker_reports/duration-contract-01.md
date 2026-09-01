### Task

Добавлен canonical duration-source/enrichment contract для будущего структурированного enrichment длительности без API-client implementation, без provider calls и без получения duration конкретных игр.

Закреплён архитектурный выбор из предыдущего provider recon:

- authoritative primary provider: IGDB official API `game_time_to_beats`;
- executor: GitHub/GitHub Actions direct server-side collection;
- GitHub владеет exact scope, identity validation, rate pacing, retry/completeness, normalization, cache merge, freshness и downstream rebuild;
- scheduled/interactive ChatGPT не используется для primary duration collection;
- scoring не меняется, `unknown = 2/3` остаётся fail-safe.

### Verified facts

- Новый canonical contract: `config/duration_enrichment_contract.json`, contract id `DURATION-ENRICHMENT-V1`, status `canonical`, implementation status `provisioning_required`.
- Canonical identity input — Steam appid. IGDB mapping допустим только через `External Game.uid` + текущий `external_game_source`, который должен быть доказан как Steam. Deprecated `category`, hardcoded legacy Steam enum, title-only и fuzzy mapping запрещены fail-closed.
- Raw provider record сохраняет IGDB game id, Steam mapping identity, `hastily_seconds`, `normally_seconds`, `completely_seconds`, submission `count`, fetch timestamp и provider timestamps/checksum where available.
- Canonical normalized estimate выбирает `normally`; conversion deterministic: `normally_seconds / 3600`; canonical cache не требует принудительного rounding и сохраняет raw record + `selected_metric`.
- Числовой confidence threshold не придуман. `count` сохраняется как provenance/evidence-volume field.
- Canonical cache path определён как `data/cache/duration_estimates.json`; в этой задаче сам cache не создавался и не заполнялся.
- Durable unresolved states разделены: `provider_row_missing`, `steam_mapping_missing`, `steam_mapping_ambiguous`, `invalid_values`. Transient operational states разделены: `auth_failure`, `transport_failure`. Ни один unresolved/error state не означает `0 hours`.
- Transient error не может перезаписать confirmed cache entry и не становится durable negative cache. Durable unresolved также не стирает confirmed entry без explicit invalidation.
- Freshness определена как long-lived: first required appearance/missing -> fetch; confirmed soft stale after 180 days; durable unresolved retry after 30 days; full refetch всех known rows каждый nightly cycle запрещён. Commercial daily freshness к duration не применяется.
- Duration enrichment остаётся fail-soft: unresolved duration может передаваться как `unknown` и не превращает duration в новый hard blocker всего visual production.
- Final handoff precedence закреплён: `validated_structured_igdb_normally` -> `legacy_text_explicit_duration_phrase` -> `unknown`. Старый text extraction сохранён только как explicit low-confidence compatibility fallback, не пишет в IGDB cache и не может перекрыть structured IGDB value.
- RAWG average playtime явно не считается completion duration и не является fallback provider.
- HowLongToBeat scraping/unofficial wrappers явно не авторизованы; возможны только после отдельного documented official API/permission и будущего contract change.
- Provider limits закреплены как 4 req/s и <=8 concurrent requests; это access limits, не production quota.
- Existing `config/execution_ownership_contract.json`, `config/daily_execution_contract.json` и `config/final_ranking_policy.json` не менялись: их текущие правила уже достаточны для GitHub-direct source collection и сохраняют duration max `3` / unknown `2`.

### Changes

1. `config/duration_enrichment_contract.json`
   - commit: `b4158c82eddccca7eb29f6230c48b67838b8071a`
2. `scripts/validate_duration_enrichment_contract.py`
   - commit: `742271ae5c3f3a84d11921ef696839804c21630f`
3. `reviews/worker_reports/duration-contract-01.md`
   - report commit is the commit containing this file.

No code for provider collection, cache population, final-builder integration, scoring, UI, Taste, descriptions or package economics was changed.

### Validation

Added `scripts/validate_duration_enrichment_contract.py`.

The validator checks:

- bindings to current ownership/daily/ranking contracts;
- IGDB + GitHub-direct authority/executor;
- ChatGPT collection prohibition and no chat-owned queue/daily quota;
- Steam appid -> current `external_game_source` identity rules and deprecated `category` guard;
- OAuth/secret rules and provider 4 req/s / 8 concurrent limits;
- raw provider record schema and `count` preservation;
- `normally` seconds -> hours normalization;
- canonical cache path/status/merge semantics;
- long-lived freshness and no nightly full-cache refetch;
- structured -> legacy text -> unknown handoff precedence;
- provisioning gates keep production collection disabled;
- cross-contract scoring invariant: duration max `3`, `unknown = 2`.

A synthetic schema fixture only (fake app/game IDs, no provider access) passed the validator logic with:

- deterministic `36000 seconds -> 10.0 hours` conversion;
- `0` or missing selected metric -> unknown;
- `DURATION_ENRICHMENT_CONTRACT_VALIDATION=PASS`.

The current canonical values used by the cross-contract checks were separately re-read from `config/execution_ownership_contract.json`, `config/daily_execution_contract.json` and `config/final_ranking_policy.json` before the contract was written. No real IGDB request, game lookup or catalog sample was performed.

### Provisioning gates

Production collection remains intentionally disabled in the contract until all of these are satisfied:

1. **Credentials — `provisioning_required`**
   - Twitch/IGDB Client ID and Client Secret must be supplied to GitHub Actions through GitHub Secrets/runtime only;
   - no secret/access token may be committed.
2. **Licensing / attribution — `provisioning_required`**
   - actual project commercial/monetization status must be established rather than assumed;
   - current applicable IGDB/Twitch terms must be checked for that status;
   - any required partnership and user-facing attribution obligations must be satisfied before production enablement.
3. **GitHub Actions connectivity — `implementation_acceptance_required`**
   - after secrets exist, a bounded GitHub Actions OAuth/authenticated API connectivity check must pass;
   - interactive ChatGPT lookup cannot substitute for this acceptance test.

### Unresolved

- Twitch/IGDB credentials are not provisioned by this task.
- Project monetization/commercial status and the resulting applicable IGDB partnership/attribution obligations are not established by this task.
- Real GitHub Actions OAuth/connectivity is intentionally not tested until credentials are provisioned.
- Actual `game_time_to_beats` coverage for the project's current Steam scope remains unknown until a later bounded implementation validation; missing coverage must remain `unknown`, not guessed.
- No numerical submission-count confidence threshold is defined because no existing policy authorized one.

### Status

`complete`

### Recommended next step

One bounded **IMPLEMENT** after the provisioning gates are satisfiable: add the GitHub-owned IGDB collection/identity-validation/normalization/cache path for exact missing/stale Steam appids, run the required GitHub Actions OAuth/connectivity acceptance test, then wire validated `data/cache/duration_estimates.json` records into `build_final_visual_payload.py` ahead of the existing explicit-text fallback. Do not change duration scoring or `unknown = 2/3`, do not add a ChatGPT queue, and validate only a bounded implementation sample rather than manually processing the catalog.
