### Task

Исследованы на уровне architecture/source-path три реально применимых класса источников duration data без lookup конкретных игр и без catalog sampling:

1. IGDB official API / `game_time_to_beats`;
2. RAWG official API / average playtime;
3. HowLongToBeat как специализированный completion-time источник, но с текущим неофициальным programmatic access.

Для каждого варианта проверены semantics, Steam identity mapping, автоматизируемый access path, пригодность для GitHub Actions, auth/rate/pricing/licensing constraints, maintenance risk, freshness semantics и provenance requirements. Вывод сверялся с canonical ownership проекта: GitHub должен забирать напрямую любой источник, который доступен server-side; scheduled ChatGPT допустим только для явно контрактно назначенного external fact work по GitHub-prepared exact scope.

### Verified facts

| Option | Что измеряет | Steam identity | Automation / GitHub access | Limits / licensing | Project fit |
|---|---|---|---|---|---|
| **IGDB `game_time_to_beats`** | Structured community-average completion times: `hastily` = до титров без заметных extras; `normally` = прохождение с частью extras; `completely` = 100%; также `count` submissions | `external_games` хранит `uid` внешнего сервиса и связь с IGDB game; Steam исторически обозначен как external source. Текущий API мигрировал от deprecated `category` к `external_game_source`, поэтому будущий contract/implementation должен использовать новый source reference, а не старый enum | Официальный server API `api.igdb.com/v4`, OAuth2 client-credentials через Twitch Client ID/Secret. Браузерные запросы ограничены CORS, но server-side GitHub Actions подходит. **GitHub-direct feasible** | 4 req/s, до 8 concurrent requests. Non-commercial usage free; docs также указывают бесплатный API для commercial partnership, с требованием связаться по partnership и user-facing attribution. Local cache прямо разрешён и рекомендован | **Лучшее соответствие**: semantics прямо описывают completion duration, есть sample count/confidence signal, timestamps и structured game identity |
| **RAWG API** | Документация называет `average playtime`, отдельно уточняет `Steam average playtime` как player-activity data. Это не completion-time estimate и может смешивать replay, multiplayer, idle/abandonment | Есть RAWG game IDs и store links (`/games/{game_pk}/stores`), но публичная схема не документирует простой authoritative lookup «Steam appid -> RAWG game» как основной identity path; mapping слабее IGDB | Официальный REST API с API key; **GitHub-direct technically feasible** | Pricing page: Free non-commercial до 20k req/month, Business $149/month до 50k, Enterprise до 1M. Terms также описывают limited free commercial use и запрещают redistribution; pricing/terms формулировки требуют проверки при provisioning | **Не подходит как primary completion duration** из-за semantic mismatch. Техническая доступность не компенсирует то, что метрика отвечает на другой вопрос |
| **HowLongToBeat** | По назначению сервиса/community wrappers: main story, main+extras, completionist/all styles — семантически очень близко к требуемой длительности прохождения | Публичный programmatic ecosystem в основном title/HLTB-ID based; direct authoritative Steam appid mapping не подтверждён | Официальный public API/documented integration path не найден; распространённые wrappers работают через website/unofficial endpoints/scraping. Это создаёт brittle access и anti-bot dependence | HowLongToBeat находится в Gaming & Entertainment portfolio Ziff Davis. Действующие Ziff Davis Terms запрещают robots/scraping/extraction/indexing и dataset/software-process use без express permission. Поэтому canonical scraping нельзя считать разрешённым path | **Семантически сильный, operational/legal path неприемлем** без явной письменной лицензии/официального API. Scheduled ChatGPT не превращает запрещённый scraping в разрешённый источник |

Дополнительные факты по IGDB, существенные для будущего contract:

- `game_time_to_beats` возвращает времена в **seconds**, поэтому canonical normalization в hours может быть полностью deterministic и GitHub-owned.
- `count` — число submissions; его нужно сохранять, а не терять, потому что он позволяет отличать высокий и низкий объём community evidence.
- `created_at`, `updated_at`, `checksum` дают полезную provenance/freshness информацию.
- `external_games.uid` — ID игры у внешнего сервиса; `external_game_source` связывает запись с конкретным внешним источником. Deprecated `category` нельзя закладывать в новый contract: опубликованный IGDB migration period закончился 31 August 2026, после чего old enum fields заявлены к removal.
- API разрешает и предпочитает local caching, что хорошо соответствует GitHub-owned canonical cache вместо daily refetch каждого известного факта.

**Semantic mapping recommendation:** canonical provider record должен сохранять все три IGDB значения (`hastily`, `normally`, `completely`) и не уничтожать исходную семантику. Для текущего единственного `estimated_duration_hours` рекомендуется deterministic selection **`normally`**, потому что это оценка обычного прохождения с некоторой дополнительной активностью и она лучше отражает типичную игровую длительность, чем rush-to-credits (`hastily`) или 100% completion (`completely`). Сам выбор `normally` должен быть закреплён будущим canonical contract, а не спрятан в Python.

**Coverage:** IGDB документирует endpoint и mapping, но не публикует гарантированный процент Steam catalog coverage именно для `game_time_to_beats`. Поэтому отсутствие row нельзя трактовать как нулевую/короткую длительность; это должен быть `missing/unresolved duration -> unknown`.

### Recommendation

**Primary option: IGDB `game_time_to_beats`.**

Почему:

- это официальный структурированный API, а не website scraping;
- поля непосредственно описывают completion-time semantics;
- есть три осмысленные completion metrics вместо одного непрозрачного playtime числа;
- есть `count`, `updated_at` и `checksum` для confidence/provenance;
- есть структурированный external-game identity path, включая Steam;
- server-side OAuth API естественно выполняется GitHub Actions;
- local caching разрешён и рекомендован самим provider;
- rate limit достаточно велик для bounded missing/refresh scope, которым всё равно обязан владеть GitHub;
- вариант не требует переносить control plane или ordinary source collection в scheduled ChatGPT.

**Fallback provider:** отдельный внешний fallback сейчас **не рекомендуется**.

- RAWG `Steam average playtime` не должен подменять completion duration: это семантически другая метрика.
- HLTB не должен использоваться через scraping/unofficial wrappers без явно полученного разрешения/официального integration path.
- Если IGDB row отсутствует или identity mapping не доказан, безопасный результат остаётся `unknown`; существующий `unknown = 2/3` не меняется.
- Текущий text extraction из descriptions может остаться только как явно определённый low-confidence compatibility fallback, если будущий contract сознательно сохранит его; это не второй authoritative provider.

### Executor

`GitHub-direct`

IGDB предоставляет обычный authenticated server-side HTTPS API. По `config/execution_ownership_contract.json` GitHub обязан напрямую собирать каждый source, который может получить сам; scheduled ChatGPT предназначен для фактов, недоступных GitHub из-за access/semantic limitations. Для IGDB такой limitation на архитектурном уровне не обнаружен.

Перед IMPLEMENT нужен один bounded connectivity/auth check из GitHub Actions после provisioning Twitch/IGDB credentials. Только если реальный тест докажет, что GitHub Actions системно не может обращаться к API, executor class можно пересматривать через отдельный contract change; заранее переносить IGDB lookup в scheduled ChatGPT оснований нет.

### Contract requirements

Будущий canonical duration-source/enrichment contract должен зафиксировать минимум следующее:

1. **Provider/authority:** primary provider = IGDB; endpoint/schema = `game_time_to_beats`; RAWG playtime не считается эквивалентной completion metric; HLTB scraping запрещён без отдельного доказанного permission path.
2. **Identity:** входная canonical identity = Steam appid; mapping разрешён только через доказанную IGDB External Game запись для Steam source + matching `uid`; ambiguous/title-only fuzzy mapping не должен silently persist duration.
3. **Current IGDB schema:** использовать `external_game_source`, не deprecated `category`; source reference должен валидироваться как Steam.
4. **Raw provider record:** сохранять IGDB game id, Steam appid/source mapping, `hastily`, `normally`, `completely`, `count`, `created_at`, `updated_at`, `checksum`, fetch timestamp и provider/schema identifier.
5. **Normalized field:** deterministic seconds-to-hours conversion; рекомендуемый `estimated_duration_hours` source metric = `normally`; сохранять `selected_metric`, чтобы происхождение числа было видимо.
6. **Confidence:** `count` обязателен в canonical record. Contract должен определить поведение low-sample evidence; до отдельного порога не придумывать числовой confidence. Missing/invalid/ambiguous mapping fail-closed в `unknown`.
7. **Ownership:** GitHub строит exact missing/stale scope, выполняет direct API calls, rate limiting, deterministic normalization, validation, cache merge, conflict handling, completeness accounting и downstream rebuild. Никакая interactive/scheduled ChatGPT queue не нужна для primary path.
8. **Credentials:** Twitch Client ID/Secret и token handling только через GitHub Secrets/ephemeral runtime; credentials не коммитятся. Contract должен учесть OAuth token expiry/refresh.
9. **Rate limits:** соблюдать IGDB 4 req/s и <=8 concurrent requests; batching/request shaping — implementation detail внутри GitHub-owned scope, не daily quota.
10. **Persistence/cache:** создать GitHub-owned canonical duration cache/artifact с provenance. Provider прямо разрешает local caching; known stable rows не требуется refetch каждый nightly cycle.
11. **Freshness semantics:** fetch при первом required appearance/missing record; редкий refresh для существующей duration записи по long-lived freshness policy и/или provider `updated_at`, выбранный contract-ом. Не привязывать duration к commercial daily freshness: completion averages меняются значительно медленнее цены.
12. **Negative state:** provider row missing, mapping missing/ambiguous, invalid values и transport/auth failure должны быть разными состояниями. Ни одно из них не кодируется как `0 hours`.
13. **Final handoff precedence:** validated structured IGDB duration -> optional contract-approved text fallback -> `unknown`. `build_final_visual_payload.py` только потребляет validated normalized field; scoring math не меняется.
14. **Licensing/attribution:** до production provisioning подтвердить non-commercial/commercial status проекта и выполнить актуальные IGDB/Twitch partnership/attribution obligations. Если продукт монетизируется, contact/partnership requirement должен быть закрыт до использования в production.
15. **Schema migration guard:** provider fields/External Game source IDs нельзя hardcode без validation against current API schema; recent IGDB enum-to-table migration должна быть regression-protected.

### Changes

`none` кроме этого report.

### Validation

Canonical repository evidence:

- `WORKER_TASK_DURATION_PROVIDER_RECON_01.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md` / `RANK-008`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- `config/final_ranking_policy.json`
- `scripts/refine_visual_ranking.py`
- `scripts/priority_ranking.py`
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- `reviews/worker_reports/duration-source-recon-01.md`

Public provider/legal documentation checked on 2026-09-01:

- IGDB API Docs — Getting Started / Account Creation / Authentication / Requests / Rate Limits: `https://api-docs.igdb.com/`
- IGDB API Docs — `Game Time To Beat` endpoint (`/v4/game_time_to_beats`)
- IGDB API Docs — `External Game` and `External Game Source` endpoints
- IGDB API Docs — `Migration Enums to Tables`, including migration period ending August 31 and removal of old field names after migration
- IGDB API Docs — Business FAQ / Partnership, including caching and attribution guidance
- RAWG API docs / pricing / Terms: `https://rawg.io/apidocs`, `https://api.rawg.io/docs/`
- Ziff Davis leadership page — Gaming & Entertainment portfolio includes HowLongToBeat: `https://www.ziffdavis.com/about/leadership`
- Ziff Davis Terms of Use, effective March 2026 — automated crawling/scraping/extraction restrictions: `https://www.ziffdavis.com/terms-of-use`
- Third-party HLTB wrapper/API ecosystem was inspected only to establish that current programmatic access is unofficial; no game lookup or real duration value was requested or collected.

No concrete game duration, top-N sample or catalog batch was queried during this task.

### Unresolved

- IGDB does not publish a guaranteed coverage percentage for `game_time_to_beats` across the project's Steam candidate universe. Real coverage must be measured only later as bounded implementation validation against GitHub-prepared scope, not manually in this RECON.
- Exact minimum `count` threshold, if any, for accepting `normally` as confirmed duration is a policy/contract choice; current public docs provide submission count but not a provider-defined confidence grade.
- Project commercial/monetization status was not established by this task. IGDB's current docs allow commercial integration through partnership and request attribution; production must satisfy whichever obligations apply to the actual project status.
- IGDB's enum-to-table migration ended immediately before this task (August 31, 2026). The new `external_game_source` path is documented, but IMPLEMENT must validate current source-table identity rather than relying on the deprecated numeric Steam enum.
- A direct GitHub Actions connectivity/auth test has not yet been run because this task is RECON and no credentials/code/workflow changes are permitted. Public API architecture strongly supports GitHub-direct, but implementation acceptance must include that test.

### Status

`complete`

### Recommended next step

Один bounded **CONTRACT** task: добавить canonical duration-source/enrichment contract, выбрав **IGDB `game_time_to_beats` + `GitHub-direct`** как primary path, закрепить Steam `external_game_source` identity mapping, raw metrics/provenance, `normally` -> `estimated_duration_hours`, confidence/missing semantics, GitHub-owned cache/freshness/auth/rate-limit rules и final-builder precedence. После утверждения contract отдельный IMPLEMENT может создать GitHub-owned collection/normalization/cache path и провести bounded connectivity/coverage validation без изменения scoring и без external ChatGPT queue.