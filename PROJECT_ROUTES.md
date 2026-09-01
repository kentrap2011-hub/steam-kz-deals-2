# PROJECT_ROUTES

Практическая карта маршрутов проекта. Это быстрый индекс уже исследованных участков, чтобы будущий чат не восстанавливал структуру проекта заново.

## Как вести карту

- Не описывать весь проект заранее. Добавлять маршрут только тогда, когда он реально понадобился в текущей работе и был найден/проверен.
- Перед широким поиском по репозиторию сначала проверить, есть ли нужная тема здесь.
- Если маршрут есть, начинать с указанных точек входа, state/validation-файлов и workflow, а не перечитывать дерево репозитория и историю коммитов.
- Если во время задачи пришлось заметно разбираться, где находится нужная логика или кто ею владеет, найденный путь нужно сохранить или уточнить здесь до завершения подзадачи.
- Не дублировать здесь канонические business rules: при конфликте contract/policy имеет приоритет.

---

## Исторический минимум SteamDB (KZ / KZT)

**Что ищем:** точный исторический минимум цены SteamDB для текущих primary offer keys.

**Последняя проверка:** 2026-08-31

**Канонический контракт:**
- `config/steamdb_lookup_contract.json`
- `config/steamdb_checkpoint_contract.json`
- ownership: `config/execution_ownership_contract.json`

**Быстрая точка входа:**
1. `data/cache/steamdb_runtime_work.json` — текущая GitHub-derived незакрытая работа.
2. При unresolved/retry проверять GitHub → external runtime → GitHub handoff; не искать исторические минимумы вручную в interactive chat.
3. После runtime submissions проверить ingest/completeness, validation/checkpoint и downstream.

**Маршрут данных:**
1. GitHub определяет true misses → `data/cache/steamdb_miss_manifest.json`.
2. Runtime state → `data/cache/steamdb_runtime_state.json`.
3. Незакрытая работа → `data/cache/steamdb_runtime_work.json`.
4. Внешний runtime-worker возвращает факты в `data/inbox/steamdb_runtime/*.json`.
5. GitHub ingest → `.github/workflows/ingest-steamdb-runtime-submissions.yml` + `scripts/ingest_steamdb_runtime_submissions.py`.
6. После полного resolution → `data/cache/steamdb_web_resolutions.json`.
7. Validation → `scripts/validate_steamdb_runtime_resolutions.py` → `data/cache/steamdb_lookup.validation.json`.
8. Checkpoint → `data/cache/steamdb_history.json`.
9. Downstream → `scripts/build_pre_ai_history_snapshot.py` → `data/production/pre_ai/history_snapshot.json`.

**Текущее состояние:** 9 ожидаемых ключей, 8 resolved, 1 unresolved retry — `App_901735`. Для него сохранены две transient ошибки `steamdb_runtime_disabled_error`; interactive chat не должен подменять runtime ручным lookup.

---

## Taste V3 / normalized factors

**Что ищем:** текущий semantic scope Taste V3, exact bindings, inbox submissions, canonical ingest и downstream propagation пяти нормализованных price-blind факторов.

**Последняя проверка:** 2026-08-31  
**Проверенный recovery ref:** после commit `31a3f3e2b84185ab32cf0a4e5bbdf1776681331b`.

**Канонические контракты:**
- `config/taste_result_contract.json` — допустимый semantic result и exact binding requirements;
- `config/taste_cache_entry_contract.json` — canonical cache entry;
- `config/execution_ownership_contract.json` — GitHub владеет scope/queue/validation/persistence, scheduled ChatGPT только semantic data-plane;
- `config/daily_execution_contract.json` — один nightly production cycle, batch не является суточной квотой.

**Быстрая точка входа — читать в таком порядке:**
1. `data/production/pre_ai/chatgpt_payload.json` — количество текущей AI queue и canonical model/profile binding.
2. `data/production/pre_ai/taste_projection.json` — exact global binding, с которым обязан совпасть submission.
3. `data/production/pre_ai/chatgpt_taste_queue.jsonl` — открывать только конкретный key/строку, а не весь файл без необходимости.
4. `data/ai_inbox/taste/` — только список submission-файлов; полный большой JSON не читать, если достаточно metadata или точечного key.
5. `.github/workflows/ingest-taste-batch.yml` → `scripts/process_taste_inbox.py` → `scripts/ingest_taste_results.py` — единственный штатный ingest path.
6. После ingest проверять компактные `data/cache/taste_fit.entry_index.json`, `data/cache/taste_ingest_receipts/`, новый `chatgpt_payload.json` и только bounded downstream diagnostics.

**Критический recovery-инвариант:**
- submission с несовпадающим top-level `profile_blob_sha` / `taste_model_version` / `taste_semantics_sha256` / source binding нельзя «починить» простым переименованием полей;
- сначала доказать, что semantic worker действительно выполнил **тот же** канонический semantic contract. Без такого доказательства exact binding validator должен остаться fail-closed;
- механическое совпадение отдельных key/fingerprint/context не доказывает semantic equivalence всей оценки;
- не обходить `ingest_taste_results.py` и не писать результаты напрямую в canonical cache.

**Anti-stall / экономия контекста:**
- для состояния очереди не считать строки вручную: брать `ai_queue_count` из `chatgpt_payload.json`;
- для provenance сначала сравнить bindings одного submission с `taste_projection.json`, а не читать все 500 результатов;
- при failed ingest открыть один конкретный run → job → log; не polling и не repository-wide search;
- если требуется простая визуальная проверка существующей scheduled-задачи ChatGPT, сначала попросить пользователя открыть её настройки/текст prompt и прислать нужный фрагмент; не тратить контекст на обходные поиски, если пользователь может проверить это напрямую.

**Текущее recovery-состояние:**
- canonical pre-AI snapshot перед ingest: `ai_queue_count=634`;
- опубликовано пять файлов `data/ai_inbox/taste/2026-08-31T0630Z-001..005.json`, по 100 результатов каждый;
- все пять имеют одинаковую stale/noncanonical global binding: model `price_blind_taste_v3`, semantic digest `fc0e4846…`, source timestamp `2026-08-30T14:27:39Z`, тогда как текущая canonical projection использует `taste-v3` и другой semantic digest/source snapshot;
- в `001` дополнительно подтверждён typo `App_1261040.taste_fingerprint`: лишняя завершающая `a`;
- one-shot repair run `33372236792` корректно остановился fail-closed на global binding mismatch до commit/persistence; ошибочный helper затем удалён commit `31a3f3e2b84185ab32cf0a4e5bbdf1776681331b`;
- эти 500 результатов **не считать ingested/canonical** и не relabel-ить без проверки provenance существующего scheduled semantic worker;
- следующий шаг — проверить конфигурацию/инструкцию именно существующего scheduled worker и установить, почему он записал старую binding-метку. Если semantic contract реально был старым — результаты нужно переоценить штатным worker-ом; если contract был текущим, а ошибочна только serialization/binding metadata, эквивалентность нужно доказать до bounded migration.

---

## Финальная сортировка / прозрачный рейтинг 0–100

**Что ищем:** где формируется production ranking, из каких баллов он складывается и как локальная мобильная очередь может его отображать.

**Последняя проверка:** 2026-08-30  
**Последний успешный production build:** GitHub Actions run `33325344781` (`Build daily visual payload`, run 64) — success.  
**Последний успешный deploy:** run `33325360599` (`Deploy visual mailing`, run 100) — success.  
**Production payload commit:** `491b1660dcca7a4b069978c29e9ff46e071252e2`.

**Сначала открыть:**
1. `config/final_ranking_policy.json` — канонический источник весов и production ranking contract.
2. `PROJECT_DECISIONS.md` → `RANK-001..RANK-011`, `UI-001`.
3. `scripts/priority_ranking.py` — config-driven scorer.
4. `scripts/validate_priority_ranking.py` — regression guard production ranking.
5. `web/app.js` — local queue/view overrides поверх готового payload.
6. ownership: `config/execution_ownership_contract.json`.

### Production ranking

**Канонический контракт:** `FINAL-PRIORITY-RANKING-V2`.

Production `priority_rank` по-прежнему строится только GitHub producer-ом:
1. `sale_expiry_urgency_asc` — сегодня → завтра → позже/неизвестно;
2. `total_score_desc` — видимый score 0–100;
3. `title_asc` — deterministic fallback.

Срочность находится вне 100 баллов и не меняет сам score.

`total_score = personal_score + purchase_score`:
- personal: максимум 60;
- purchase: максимум 40.

Personal:
- taste до 50;
- wishlist до +4;
- achievements до +3;
- duration до +3;
- risk до −12.

Purchase:
- `savings` до 20 — `max(0, original_price_rub - current_price_rub)`;
- current price до 12;
- history до 8.

`discount_percent` остаётся отображением/context и не даёт V2 score сам по себе.

### Локальные режимы очереди в UI

Production ranking **не меняется**. В `web/app.js` есть отдельный локальный view-mode:

- кнопка **`⏱ Срочные` выключена (default)** → локальная очередь: `total_score DESC → title`;
- кнопка **`✓ Срочные` включена** → локальная очередь использует готовый production `priority_rank`, то есть `urgency → score → title`;
- выбранный режим хранится в localStorage как `state.settings.urgency_first`;
- `QUEUE_VERSION=5` заставляет старое состояние один раз пересобрать очередь по новому default;
- при переключении `buildQueue()` сохраняет текущую открытую игру, если она остаётся активной;
- UI не пересчитывает semantic score, urgency или ranking factors: он только меняет порядок уже готовых producer-owned полей `total_score` / `priority_rank`.

**Критически:** `manual_end_at` («В конец очереди») остаётся абсолютным локальным override в обоих режимах. `canonicalQueueIds()` сначала формирует automatic order, затем всегда отделяет manual items и ставит их после automatic items; manual items сохраняют порядок по времени отправки в конец.

`renderPriority()` учитывает локальный режим:
- без срочности показывает позицию в текущей очереди и явно пишет, что срочность сейчас не влияет на порядок;
- со срочностью может показывать canonical production comparison;
- у вручную отправленной в конец игры явно пишет про manual override.

### Taste precision

Большинство старых taste-cache записей пока имеют только `strong/moderate`, поэтому V2 использует явный fallback:
- strong → 42/50;
- moderate → 34/50;
- `score_precision=legacy_coarse_fit`.

Следующая отдельная ranking-задача в `BACKLOG.md` — детальные normalized price-blind taste factors 0..100.

### Production-путь

1. `.github/workflows/build-daily-visual-payload.yml` → `scripts/validate_priority_ranking.py`.
2. `scripts/build_final_visual_payload.py` — единственный final producer.
3. `scripts/priority_ranking.py::apply_final_priority_order()` считает score и production rank.
4. Итог → `data/production/visual/current.json`.
5. Full audit → `ranking_review.jsonl`.
6. Bounded diagnostics → `data/production/visual/ranking_lookup/<bucket>.json`.
7. `web/app.js` читает готовые поля и применяет только local queue/view overrides.

### Проверенный пример

**High On Life:** 62.5/100, production rank 220.  
**Seraph's Last Stand:** 44.5/100, production rank 348.

High On Life выше по score благодаря wishlist, отсутствию серьёзного риска и большей реальной экономии. Seraph получает +12/12 за низкую текущую цену, но её экономия 17 ₽ даёт 0/20 и серьёзный риск даёт −10.

### Regression / invariants

Production validator проверяет:
- canonical urgency → score → title;
- 60 + 40 = 100;
- ruble savings вместо discount percentage;
- risk/wishlist/achievements/duration weights;
- `manual_end_at` UI invariant.

Для local UI режима обязательные implementation-инварианты:
- default `urgency_first=false`;
- off-mode сортирует automatic items по `total_score`;
- on-mode использует готовый `priority_rank`;
- mode входит в queue signature, поэтому переключение реально пересобирает очередь;
- manual items всегда добавляются после automatic items;
- `sendCurrentToEnd()` остаётся без изменения семантики.

**Открытые отдельные задачи:**
- детальный taste-factor migration;
- automatic Windows compatibility evidence-source;
- оставшиеся SteamDB retry (пользователь отложил).

---

## Русские описания / semantic translation contract

**Что ищем:** каноническую границу между GitHub-owned unresolved scope и scheduled ChatGPT как constrained semantic translation worker.

**Последняя проверка:** 2026-09-01

**Канонические контракты:**
- `config/russian_description_translation_contract.json` — scope, immutable request identity, runtime reuse, retry/completeness ownership и reserved artifact paths;
- `config/russian_description_translation_result_contract.json` — translation-specific worker result schema и strict echo/quality rules;
- `config/russian_description_translation_cache_entry_contract.json` — GitHub-owned cache-entry binding и invalidation;
- ownership: `config/execution_ownership_contract.json`;
- nightly cycle: `config/daily_execution_contract.json`.

**Быстрая точка входа:**
1. Сначала читать `config/russian_description_translation_contract.json`.
2. Для worker output — `config/russian_description_translation_result_contract.json`.
3. Для cache reuse/invalidation — `config/russian_description_translation_cache_entry_contract.json`.
4. Contract consistency/regression — `scripts/validate_russian_description_translation_contract.py`.
5. Финальный existing quality gate остаётся `scripts/validate_russian_descriptions.py`; классификация текста — `scripts/russian_description_quality.py`.

**Ключевые инварианты:**
- GitHub владеет exact current scope, queue/order, retry, completeness, validation, cache merge и downstream rebuild;
- scheduled ChatGPT только переводит exact immutable requests; новые игры и retry loop не выбирает;
- используется существующий nightly scheduled ChatGPT runtime; отдельный recurring translation schedule запрещён;
- Taste-specific result schema не переиспользуется;
- semantic scope ограничен `needs_translation` / `needs_ru_rewrite` с source quality `non_ru` / `weak_ru`;
- identity: `App_<appid>` + SHA-256 нормализованного source text; source hash одновременно является version binding;
- stale/mismatched/unknown/placeholder/technical/non-Russian result не попадает в cache и остаётся unresolved;
- unchanged source не переводится заново без причины; current direct `ready_ru` source имеет приоритет над cache;
- interactive chat не переводит production catalog item-by-item и не заполняет cache вручную.

**Reserved paths для следующего bounded IMPLEMENT:**
- request work input: `data/production/pre_ai/chatgpt_ru_description_queue.jsonl`;
- status manifest: `data/production/pre_ai/chatgpt_ru_description_status.json`;
- runtime submissions: `data/ai_inbox/russian_descriptions/*.json`;
- canonical cache: `data/cache/russian_description_translations.json`.

**Текущее состояние:** contract/schema wiring завершён. Producer, runtime ingest и production cache population намеренно **не реализованы в этой contract-only задаче**; это следующий отдельный bounded IMPLEMENT согласно `WORKER_TASK_RU_TRANSLATION_CONTRACT_01.md`.
