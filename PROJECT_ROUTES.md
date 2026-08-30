# PROJECT_ROUTES

Практическая карта маршрутов проекта. Это быстрый индекс уже исследованных участков, чтобы будущий чат не восстанавливал структуру проекта заново.

## Как вести карту

- Не описывать весь проект заранее. Добавлять маршрут только тогда, когда он реально понадобился в текущей работе и был найден/проверен.
- Перед широким поиском по репозиторию сначала проверить, есть ли нужная тема здесь.
- Если маршрут есть, начинать с указанных точек входа, state/validation-файлов и workflow, а не перечитывать дерево репозитория и историю коммитов.
- Если во время задачи пришлось заметно разбираться, «где это вообще находится» или «кто это запускает», найденный путь нужно сохранить или уточнить здесь до завершения подзадачи.
- Маршрут должен отвечать минимум на вопросы: где вход, кто владелец, чем запускается, какие state/validation-файлы смотреть, куда сохраняется результат, кто потребляет его дальше и по какому признаку работа завершена.
- Не дублировать здесь бизнес-правила и архитектурные контракты: давать ссылки на канонические файлы.
- Если вопрос не только «где?», но и «почему это правило именно такое?», до чтения Git history открыть соответствующую запись в `PROJECT_DECISIONS.md`.
- У каждого маршрута хранить дату последней проверки и commit/ref, относительно которого структура была проверена. Если реальная структура изменилась, маршрут обновить по ходу этой же работы.

---

## Исторический минимум SteamDB (KZ / KZT)

**Что ищем:** точный исторический минимум цены SteamDB для текущих primary offer keys.

**Последняя проверка:** 2026-08-30  
**Проверено относительно commit:** `bb7bb6c5791cd41036314c6b8c93111c35703365` (`main` на момент фиксации маршрута)

**Канонический контракт:**
- `config/steamdb_lookup_contract.json`
- `config/steamdb_checkpoint_contract.json`
- ownership: `config/execution_ownership_contract.json`

**Быстрая точка входа при продолжении:**
1. Сначала открыть `data/cache/steamdb_runtime_work.json` — это текущая GitHub-derived незакрытая работа.
2. Если есть unresolved/retry, проверить канонический GitHub → external runtime → GitHub handoff; не искать исторические минимумы вручную в interactive chat.
3. После возврата runtime submissions проверить ingest/completeness, затем validation/checkpoint и downstream.

**Маршрут данных:**
1. GitHub определяет true misses и их порядок → `data/cache/steamdb_miss_manifest.json`.
2. GitHub из manifest + уже полученных submissions выводит текущее состояние → `data/cache/steamdb_runtime_state.json`.
3. GitHub выводит только реально незакрытую работу → `data/cache/steamdb_runtime_work.json`.
4. Внешний runtime-worker читает только `steamdb_runtime_work.json` и возвращает наблюдённые факты в `data/inbox/steamdb_runtime/*.json`. Сам worker не решает scope/retry/completeness.
5. GitHub ingest → `.github/workflows/ingest-steamdb-runtime-submissions.yml` + `scripts/ingest_steamdb_runtime_submissions.py`.
6. Когда `unresolved_count == 0`, GitHub создаёт/обновляет подготовленный полный результат → `data/cache/steamdb_web_resolutions.json`.
7. GitHub валидирует полный true-miss набор → `.github/workflows/build-steamdb-true-miss-lookups.yml` + `scripts/validate_steamdb_runtime_resolutions.py` → `data/cache/steamdb_lookup.validation.json`.
8. После успешной валидации GitHub checkpoint-ит канонический кэш истории → `.github/workflows/checkpoint-steamdb-history.yml` → `data/cache/steamdb_history.json`.
9. Downstream использует кэш через `scripts/build_pre_ai_history_snapshot.py` → `data/production/pre_ai/history_snapshot.json`.

**Где считается качество относительно минимума:** `scripts/build_pre_ai_history_snapshot.py`, функция `history_quality()`:
- current <= min → `record`;
- до +10% → `near_record`;
- до +25% → `good_vs_history`;
- выше → `well_above_history`.

**Признак завершения маршрута:**
- `data/cache/steamdb_runtime_work.json`: `unresolved_count == 0`;
- полный true-miss набор успешно прошёл validation;
- `data/cache/steamdb_history.json` обновлён checkpoint-ом GitHub;
- downstream history snapshot успешно пересобран.

**Известная ловушка:** 529 уже имевшихся результатов были перенесены в новую runtime-схему через recovery migration. Сам факт наличия этих 529 записей не доказывает, что текущий GitHub → runtime handoff способен обработать новый retry. При зависших retry сначала проверять именно это звено.

**Важная архитектурная граница:** GitHub владеет очередью, retry-state, completeness, validation, persistence и downstream. Прямой SteamDB lookup из GitHub Actions отключён, потому что SteamDB систематически отвечает GitHub Actions HTTP 403; внешний lookup выполняется ограниченным runtime-worker, а интерактивный чат не должен вручную обрабатывать production backlog.

**Текущее состояние на 2026-08-30:** `data/cache/steamdb_runtime_work.json` = 534 ожидаемых, 529 resolved, 5 unresolved retry (`runtime_web_internal_error`). Пользователь отдельно указал, что эти 5 retry сейчас низкоприоритетны.

---

## Финальная сортировка / прозрачный рейтинг 0–100

**Что ищем:** где формируется автоматический порядок игр в `data/production/visual/current.json`, из каких баллов он складывается, почему одна игра выше другой и как безопасно менять веса.

**Последняя проверка:** 2026-08-30  
**Проверено относительно production commit:** `46bd921ed246f7cf2b7fc58211868d2be76d5b8b` (`Refresh daily visual payload`, V2 + bounded score lookup)

**Сначала открыть:**
1. `config/final_ranking_policy.json` — единственный канонический источник всех весов, штрафов, порогов и таблиц начисления V2.
2. `PROJECT_DECISIONS.md` → `RANK-001..RANK-011`, `UI-001` — rationale и superseded V1-решения.
3. `scripts/priority_ranking.py` — config-driven scorer.
4. `scripts/validate_priority_ranking.py` — regression guard.
5. ownership: `config/execution_ownership_contract.json`.

**Канонический контракт:** `FINAL-PRIORITY-RANKING-V2`.

**Главная архитектурная граница:** score, breakdown и final order принадлежат producer/GitHub. UI ничего не пересчитывает. Менять числовые веса нужно в `config/final_ranking_policy.json`, а не в Python/JS и не в параллельном sort-key.

**Текущий автоматический порядок:**
1. `sale_expiry_urgency_asc` — скидка заканчивается сегодня → завтра → позже/неизвестно;
2. `total_score_desc` — итоговый видимый балл 0–100;
3. `title_asc` — только deterministic fallback при полном равенстве.

Срочность намеренно находится **вне 100 баллов**: она отвечает за риск пропустить акцию, а не за качество игры/покупки. Явный локальный `manual_end_at` («В конец очереди») остаётся абсолютным UI override поверх production order.

### Из чего складывается 100

`total_score = personal_score + purchase_score`.

**Personal: максимум 60**
- `taste`: до 50 — насколько сама игра подходит пользователю;
- wishlist: до +4;
- achievements: до +3;
- duration: до +3;
- risk: видимый штраф до −12.

**Purchase: максимум 40**
- `savings`: до 20 — **реальная экономия в рублях** `max(0, original_price_rub - current_price_rub)`;
- `price`: до 12 — текущая цена;
- `history`: до 8 — цена относительно истории.

`discount_percent` остаётся для отображения и eligibility/context, но **не даёт баллов V2 сам по себе**. Например, 60→30 ₽ и 6000→3000 ₽ обе имеют −50%, но экономия 30 ₽ даёт 0/20, а 3000 ₽ — 19/20 по текущей таблице.

### Taste precision

Текущий старый cache в основном хранит только `strong/moderate`, поэтому V2 временно использует явный fallback:
- `strong` → 42/50;
- `moderate` → 34/50;
- `score_precision=legacy_coarse_fit`.

Это не скрывается от пользователя: UI показывает, что вкусовая часть пока грубая. Следующая отдельная ranking-задача в `BACKLOG.md` — расширить существующий semantic taste pipeline нормализованными price-blind факторами `0..100`:
- `gameplay_mastery`;
- `development_variety`;
- `structure_pacing_direction`;
- `identity_hooks`;
- `breadth_of_match`.

Их значения должны быть независимы от весов. Тогда изменение, например, `gameplay_mastery` 18→15 в policy не потребует повторной AI-оценки игры.

### Production-путь

1. `.github/workflows/build-daily-visual-payload.yml` запускает `scripts/validate_priority_ranking.py`.
2. После history readiness единственный final producer — `scripts/build_final_visual_payload.py`.
3. После enrichment/refinement он вызывает `scripts/priority_ranking.py::apply_final_priority_order()`.
4. Scorer читает V2 policy, формирует `score_breakdown`, `total_score`, `personal_score`, `purchase_score`, `savings_rub`, `risk_status`, затем один раз присваивает `priority_rank`.
5. `priority_factors` отражают фактический final order: urgency → total score → title.
6. `priority_vs_next` показывает первый реальный фактор, на котором текущая игра выше следующей.
7. Итог сохраняется в `data/production/visual/current.json`; полный аудит — `ranking_review.jsonl`.
8. Для точечной диагностики использовать **только bounded lookup** `data/production/visual/ranking_lookup/<первая-буква>.json`, а не читать большой audit целиком.
9. `scripts/build_ranking_lookup.py` schema v3 сохраняет rank, total/personal/purchase score и баллы всех компонентов, включая `savings_rub`.
10. `web/app.js::renderPriority()` отображает producer-owned breakdown; `renderRisk()` отображает готовый risk status.

### Проверенный production-пример

**High On Life** (`ranking_lookup/h.json`):
- rank `220`;
- total `62.5/100`;
- personal `41.5/60`;
- purchase `21/40`;
- taste `34/50` (`legacy_coarse_fit`);
- wishlist `+4`;
- achievements `+1.5`;
- duration `+2`;
- risk `0`;
- original `1316 ₽` → current `460 ₽`, savings `856 ₽` → `+12/20`;
- current-price points `+9/12`;
- history `well_above_history` → `0/8`.

**Seraph's Last Stand** (`ranking_lookup/s.json`):
- rank `348`;
- total `44.5/100`;
- personal `27.5/60`;
- purchase `17/40`;
- taste `34/50` (`legacy_coarse_fit`);
- wishlist `0`;
- achievements `+1.5`;
- duration `+2`;
- serious personal risk `−10`;
- current `39 ₽`, savings всего `17 ₽` → `0/20`;
- current-price points `+12/12`;
- history `good_vs_history` → `+5/8`.

Итог: High On Life выше Seraph не из-за специального исключения, а потому что видимый score отражает wishlist, отсутствие серьёзного риска и существенно большую реальную экономию; дешёвая абсолютная цена Seraph даёт ей +12/12 за цену, но не выдумывает крупную скидочную выгоду из малого процента/малой суммы.

### Risk в V2

`risk_status` остаётся producer-owned пояснением:
- `no_confirmed_risk` — штраф 0;
- `descriptive_risk` — небольшой видимый score-штраф по policy;
- `serious_risk` — сильный видимый score-штраф (стартово персональный −10, confirmed Windows −12).

Отдельного скрытого раннего risk-layer в V2 больше нет: влияние риска видно прямо в personal breakdown. `practical_or_personal_risk_rank` может оставаться диагностическим legacy-полем, но не является V2 sort-factor.

### Что больше не участвует в final sort напрямую

- `priority_bucket` — только eligibility/explanation context;
- `decision` (`БРАТЬ СЕЙЧАС / МОЖНО БРАТЬ / ЛУЧШЕ ЖДАТЬ`) — объясняющая метка, иначе был бы double count ценовых сигналов;
- `taste_rank` — не final factor;
- `discount_percent` — не score factor;
- direct evidence не получает отдельного бонуса поверх taste: точная пользовательская оценка становится источником самого taste-score.

### Regression guard

`scripts/validate_priority_ranking.py` проверяет минимум:
- exact V2 order urgency → score → title;
- personal 60 + purchase 40 = total 100;
- maxima всех компонентов сходятся;
- urgency находится вне score и имеет automatic precedence;
- внутри одинаковой urgency фактический порядок определяется видимым total score;
- direct user rating имеет приоритет как taste source и не double-counted;
- normalized taste factors 0..100 корректно переводятся в configurable points;
- legacy strong/moderate fallback явно помечен coarse;
- wishlist = configured +4;
- risk penalties −1/−3/−10/−12;
- отсутствие achievements не штрафуется второй раз через risk;
- price, history и savings являются отдельными компонентами;
- **60→30 ₽ при −50% = 30 ₽ savings → 0/20; 6000→3000 ₽ при тех же −50% = 3000 ₽ → 19/20**;
- изменение только `discount_percent` при одинаковых original/current prices не меняет V2 score;
- изменение одной таблицы в JSON меняет score без изменения Python и без новой taste evaluation;
- контрольная пара структуры High On Life / Seraph сохраняет ожидаемое направление;
- UI `manual_end_at` остаётся абсолютным post-production override.

**Последняя фактическая CI-проверка:** GitHub Actions run `33320390597` (`Build daily visual payload`, run 63) прошёл полностью: validator, history readiness, unified producer, ranking review, bounded lookup и commit/push — `success`. Production commit: `46bd921ed246f7cf2b7fc58211868d2be76d5b8b`.

**Предыдущая UI/deploy-проверка:** V2 UI build run `33319717957` завершился `success`; `Deploy visual mailing` run `33319734324` завершился `success`.

**Известная workflow-ловушка:** bounded lookup — директория `data/production/visual/ranking_lookup/`, не старый файл `ranking_lookup.json`. Не возвращать удалённый legacy pathspec в `git add`.

**Открытая граница Windows:** scorer умеет применять confirmed Windows penalty, но отдельный надёжный автоматический evidence-source для `modern_windows_friction` остаётся отдельной backlog-задачей.

**Признак завершённости V2:** 
- canonical policy = `FINAL-PRIORITY-RANKING-V2`;
- один final producer и один final sort;
- `current.json` содержит `score_breakdown`, `total_score`, `personal_score`, `purchase_score`, `priority_rank`, `priority_factors`, `priority_vs_next`, `risk_status`;
- UI показывает тот же score, который реально сортирует;
- все числовые веса меняются через один JSON policy;
- bounded lookup позволяет быстро диагностировать конкретную игру без чтения большого audit.
