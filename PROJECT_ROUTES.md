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

**Текущее состояние на 2026-08-30:** `data/cache/steamdb_runtime_work.json` = 534 ожидаемых, 529 resolved, 5 unresolved retry (`runtime_web_internal_error`).

---

## Финальная сортировка / priority rank витрины

**Что ищем:** где формируется автоматический порядок игр в `data/production/visual/current.json`, почему конкретная игра должна быть выше/ниже другой, как интерпретировать риск и где пользовательское локальное состояние может этот порядок переопределить.

**Последняя проверка:** 2026-08-30  
**Проверено относительно production commit:** `99907d34442c2470b12a2e318cc4a579ec5fcddb` (`Refresh daily visual payload` после explicit risk status)

**Сначала открыть:**
1. `config/final_ranking_policy.json` — канонический машинный контракт именно финального `priority_rank`.
2. `PROJECT_DECISIONS.md` → `RANK-001..RANK-009`, `UI-001` — почему порядок именно такой и какие альтернативы сознательно отвергнуты.
3. `PROJECT_RULES.md` → «Как выбирать платные игры», «Wishlist Steam при финальной сортировке», «Практическая пригодность покупки».
4. ownership: `config/execution_ownership_contract.json`.

**Важно про старую policy:** старые массивы `sorting` внутри `config/mailing_policy.json` исторически отстали от фактической логики. Для финального `priority_rank` они больше не являются источником истины; dedicated contract `config/final_ranking_policy.json` имеет явный precedence. Если меняется final ranking, менять dedicated contract + rationale/tests, а не создавать новую независимую sort-key рядом.

**Фактический production-путь:**
1. `.github/workflows/build-daily-visual-payload.yml` сначала запускает `scripts/validate_priority_ranking.py`.
2. После history readiness workflow запускает **один** production entrypoint: `scripts/build_final_visual_payload.py`.
3. Этот producer выполняет enrichment/refinement, переиспользуя проверенные helper-функции из `build_daily_visual_payload.py` и `refine_visual_ranking.py`, но **не запускает их старые `main()` и старые независимые final sort-key**.
4. После полного refinement producer вызывает `scripts/priority_ranking.py` → `apply_final_priority_order()`.
5. `priority_ranking.py` читает порядок только из `config/final_ranking_policy.json`, один раз присваивает `priority_rank` и одновременно формирует готовую producer-owned диагностику:
   - `priority_factors` — все canonical факторы в точном canonical порядке с `id`, русской подписью, человекочитаемым `value` и фактическим `sort_value`;
   - `priority_vs_next` — следующая игра в production-порядке и **первый canonical фактор**, на котором текущая игра выигрывает у неё;
   - `risk_status` — явная producer-owned интерпретация риска для UI и аудита.
6. Итог: `data/production/visual/current.json`; полный аудит: `data/production/visual/ranking_review.jsonl`. Аудит включает `risk_status` вместе с ranking diagnostics.
7. Для точечной диагностики конкретной игры **не читать большой `ranking_review.jsonl` целиком**. Использовать `data/production/visual/ranking_lookup/<первая-буква>.json`, который строит `scripts/build_ranking_lookup.py`. Например, `High On Life` → `ranking_lookup/h.json`, `Seraph's Last Stand` → `ranking_lookup/s.json`. `_manifest.json` показывает количество элементов по bucket-файлам.
8. UI читает готовый порядок и готовую диагностику. `web/app.js::renderPriority()` отображает ranking diagnostics, а `renderRisk()` отображает producer-owned `risk_status` и `risks`; frontend не определяет смысл риска самостоятельно.
9. `web/app.js` может поверх production-порядка применить только явный локальный override `manual_end_at` («В конец очереди»).

**Семантика risk-полей:**
- `risks` — человекочитаемые тексты конкретных рисков/ограничений для карточки;
- `risk_codes` — реально обнаруженные структурированные причины риска; пустой список означает, что конкретный описанный персональный риск не найден;
- `risk_level` — описательная тяжесть найденного риска (`low` / `medium` / `high`), но сама по себе `medium`/`low` не означает ранний штраф в final ranking;
- `practical_or_personal_risk_rank` — фактический ранний ranking-штраф; ненулевым становится только для серьёзного персонального риска или подтверждённой существенной Windows-проблемы;
- `risk_status` — готовый статус, который должен видеть UI:
  - `no_confirmed_risk` → «Подтверждённых персональных рисков не найдено»;
  - `descriptive_risk` → «Есть риск — но он не считается серьёзным»;
  - `serious_risk` → «Серьёзный риск — влияет на сортировку».

Таким образом, ситуация «в блоке РИСК описан минус, а серьёзного ranking-штрафа нет» **нормальна**: это `descriptive_risk`, а не противоречие. UI должен явно показывать эту разницу.

**Текущий автоматический порядок:**
`sale expiry today/tomorrow → serious confirmed personal/Windows risk → priority_bucket → wishlist → discount % → history quality → current price → achievement quality → duration → title`.

Точные machine factor IDs смотреть в `config/final_ranking_policy.json`.

**Ключевые причины, которые нельзя потерять:**
- expiry сегодня/завтра выше автоматического качества, чтобы пользователь не пропустил заканчивающуюся сделку;
- серьёзный подтверждённый персональный/практический риск идёт **раньше** смешанной taste+deal группы, чтобы дешёвая формально выгодная игра с сильным личным конфликтом не поднималась выше заметно более безопасного кандидата;
- ранний risk-layer использует только действительно серьёзные подтверждённые риски; средние/слабые эвристики остаются нейтральными на этом уровне;
- `priority_bucket` после срочности и серьёзного риска остаётся основной qualitative taste+deal матрицей;
- direct user evidence не сортирует второй раз: оно уже может изменить fit, commercial branch и bucket;
- Steam XP/7/8 label без внешнего подтверждения нейтрален;
- wishlist заметен, но ограничен и сам по себе не является доказательством taste fit;
- **discount идёт раньше history quality**, потому что у новой игры обычные −20% могут быть record только из-за короткой истории цены;
- низкая цена, новизна или короткая история сами по себе **не получают штраф**: проблема решается precedence реальных факторов, а не искусственным порогом;
- achievements — поздний фактор близких кандидатов; duration ещё слабее;
- локальное «В конец очереди» абсолютнее любой автоматической срочности и не меняет production `priority_rank`.

**Проверенный пример `High On Life` / `Seraph's Last Stand`:**
- `High On Life`: rank `274`, taste_rank `248`, `priority_group=6`, `risk_status=no_confirmed_risk`, wishlist `true`, скидка `65%`, history `well_above_history`, цена `460 ₽`;
- `Seraph's Last Stand`: rank `347`, taste_rank `344`, `priority_group=5`, `risk_status=serious_risk`, serious risk `2` / `risk_level=high`, wishlist `false`, скидка `30%`, history `good_vs_history`, цена `39 ₽`;
- то есть историческая цена не была корневой причиной старой ошибки. Более ранняя коммерческая группа Seraph раньше могла выиграть до того, как учитывался её высокий персональный риск. После `RANK-009` серьёзный риск сравнивается раньше группы, поэтому High On Life корректно оказывается выше, несмотря на более дорогую и менее выгодную по истории текущую цену.

**Граница более тонкой «интересности»:** текущий semantic taste слой даёт в основном `strong/moderate`, а `taste_rank` в refiner не является независимой точной шкалой интересности — он также учитывает риск/ачивки/длительность. Поэтому не использовать `taste_rank` как новый скрытый final factor только ради отдельных примеров. Если независимый taste-review покажет, что системе системно не хватает градации «насколько интересно» внутри одного fit-класса, сначала улучшить upstream taste evidence/model и только затем согласованно менять canonical ranking contract.

Полные объяснения и rejected alternatives: `PROJECT_DECISIONS.md`.

**Regression guard:** `scripts/validate_priority_ranking.py` проверяет:
- точный порядок факторов из canonical contract;
- today → tomorrow → later/unknown;
- три explicit risk-state: no risk / descriptive risk / serious ranking risk;
- `descriptive_risk` не получает ранний ranking-штраф;
- `serious_risk` получает ранний штраф, включая confirmed Windows friction;
- serious confirmed risk precedence перед `priority_bucket`;
- контрольную пару структуры `High On Life` / `Seraph's Last Stand`;
- голая legacy Steam label нейтральна;
- wishlist precedence внутри одинаковых более ранних факторов;
- 70% `good_vs_history` выше 20% `record` при прочих равных;
- коммерческие признаки раньше achievements;
- direct evidence отсутствует как второй final factor;
- пользовательские подписи ranking diagnostics не содержат `Production`, `bucket` или `tie-break`;
- UI читает `g.risk_status` и не придумывает semantic status сам;
- UI `manual_end_at` остаётся абсолютным post-production override;
- `priority_factors` у каждой игры идут строго в canonical порядке и содержат готовые значения;
- `priority_vs_next` правильно находит первый решающий фактор на контролируемой паре и отсутствует у последней игры.

**Последняя фактическая CI-проверка:** GitHub Actions run `33317006394` (`Build daily visual payload`) завершился `success`: validator, unified producer, ranking audit, bounded lookup и commit/push прошли полностью. Production commit `99907d34442c2470b12a2e318cc4a579ec5fcddb` содержит новый `risk_status`.

**Известная workflow-ловушка:** bounded lookup заменил старый файл `data/production/visual/ranking_lookup.json` директорией `data/production/visual/ranking_lookup/`. Не добавлять удалённый legacy-файл как обязательный pathspec в `git add`: это ломает commit-step после успешного build. Исправлено в commit `7f3d91ebb3faae2c7aec9242f2dedb092076e409`.

**Открытая граница Windows:** sort-layer уже корректно принимает подтверждённый `modern_windows_friction`, но на 2026-08-30 не подтверждено наличие отдельного автоматического data-source, который надёжно получает такие факты помимо старой Steam system-requirements строки. Не считать Windows-часть E2E закрытой только потому, что sort key умеет обработать поле. Если этот источник отсутствует, его нужно проектировать отдельно по ownership contract.

**Признак завершённости именно ranking-архитектуры и диагностики:**
- dedicated canonical contract существует;
- production workflow имеет один final producer и одну final sort;
- regression guard проходит;
- старые dual-sort mains не участвуют в production;
- `current.json` содержит `FINAL-PRIORITY-RANKING-V1`, `priority_rank`, `priority_factors`, `priority_vs_next` и `risk_status`;
- точечная диагностика конкретных игр доступна через bounded `ranking_lookup/<bucket>.json` без чтения большого audit JSONL;
- UI показывает готовую producer-owned ranking/risk диагностику и не пересчитывает смысловые поля на клиенте.
