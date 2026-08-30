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

**Что ищем:** где формируется автоматический порядок игр в `data/production/visual/current.json`, почему конкретная игра должна быть выше/ниже другой и где пользовательское локальное состояние может этот порядок переопределить.

**Последняя проверка:** 2026-08-30  
**Проверено относительно commit:** `9e064fd65358de5dabf53f1c4879613020207ef7` (`Refresh daily visual payload` после добавления ranking diagnostics)

**Сначала открыть:**
1. `config/final_ranking_policy.json` — канонический машинный контракт именно финального `priority_rank`.
2. `PROJECT_DECISIONS.md` → `RANK-001..RANK-008`, `UI-001` — почему порядок именно такой и какие альтернативы сознательно отвергнуты.
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
   - `priority_vs_next` — следующая игра в production-порядке и **первый canonical фактор**, на котором текущая игра выигрывает у неё.
6. Итог: `data/production/visual/current.json`; компактный аудит: `data/production/visual/ranking_review.jsonl`. Оба артефакта содержат `priority_factors` и `priority_vs_next`.
7. UI читает готовый порядок и готовую диагностику. `web/app.js::renderPriority()` **только отображает** `priority_factors` / `priority_vs_next` и не должен реконструировать sort key или заново решать, почему игры стоят в таком порядке.
8. `web/app.js` может поверх production-порядка применить только явный локальный override `manual_end_at` («В конец очереди»).

**Текущий автоматический порядок:**
`sale expiry today/tomorrow → priority_bucket → serious confirmed personal/Windows risk → wishlist → discount % → history quality → current price → achievement quality → duration → title`.

Точные machine factor IDs смотреть в `config/final_ranking_policy.json`.

**Ключевые причины, которые нельзя потерять:**
- expiry сегодня/завтра выше автоматического качества, чтобы пользователь не пропустил заканчивающуюся сделку;
- `priority_bucket` остаётся основной qualitative taste+deal матрицей после срочности;
- direct user evidence не сортирует второй раз: оно уже может изменить fit, commercial branch и bucket;
- в ранний risk-layer попадают только серьёзные подтверждённые риски; средние/слабые эвристики сами по себе не должны обгонять wishlist/выгоду;
- Steam XP/7/8 label без внешнего подтверждения нейтрален;
- wishlist заметен, но ограничен;
- **discount идёт раньше history quality**, потому что у новой игры обычные −20% могут быть record только из-за короткой истории цены;
- achievements — поздний фактор близких кандидатов; duration ещё слабее;
- локальное «В конец очереди» абсолютнее любой автоматической срочности и не меняет production `priority_rank`.

Полные объяснения и rejected alternatives: `PROJECT_DECISIONS.md`.

**Regression guard:** `scripts/validate_priority_ranking.py` проверяет:
- точный порядок факторов из canonical contract;
- today → tomorrow → later/unknown;
- bucket precedence после одинаковой срочности;
- голая legacy Steam label нейтральна;
- confirmed Windows friction понижает;
- wishlist precedence;
- 70% `good_vs_history` выше 20% `record` при прочих равных;
- коммерческие признаки раньше achievements;
- direct evidence отсутствует как второй final factor;
- UI `manual_end_at` остаётся абсолютным post-production override;
- `priority_factors` у каждой игры идут строго в canonical порядке и содержат готовые значения;
- `priority_vs_next` правильно находит первый решающий фактор на контролируемой паре и отсутствует у последней игры.

**Последняя фактическая CI-проверка:** GitHub Actions run `33312895688` (`Build daily visual payload`) завершился `success`. Validator прошёл, unified producer выполнил полный build, после чего bot commit `9e064fd65358de5dabf53f1c4879613020207ef7` обновил `data/production/visual/current.json` и `data/production/visual/ranking_review.jsonl` уже с producer-owned ranking diagnostics.

**Открытая граница Windows:** sort-layer уже корректно принимает подтверждённый `modern_windows_friction`, но на 2026-08-30 не подтверждено наличие отдельного автоматического data-source, который надёжно получает такие факты помимо старой Steam system-requirements строки. Не считать Windows-часть E2E закрытой только потому, что sort key умеет обработать поле. Если этот источник отсутствует, его нужно проектировать отдельно по ownership contract.

**Признак завершённости именно ranking-архитектуры и диагностики:**
- dedicated canonical contract существует;
- production workflow имеет один final producer и одну final sort;
- regression guard проходит;
- старые dual-sort mains не участвуют в production;
- `current.json` содержит `FINAL-PRIORITY-RANKING-V1`, `priority_rank`, `priority_factors` и `priority_vs_next`;
- UI показывает готовую producer-owned диагностику и не пересчитывает ranking на клиенте.
