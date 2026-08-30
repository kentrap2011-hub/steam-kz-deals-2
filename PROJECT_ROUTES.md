# PROJECT_ROUTES

Практическая карта маршрутов проекта. Это быстрый индекс уже исследованных участков, чтобы будущий чат не восстанавливал структуру проекта заново.

## Как вести карту

- Не описывать весь проект заранее. Добавлять маршрут только тогда, когда он реально понадобился в текущей работе и был найден/проверен.
- Перед широким поиском по репозиторию сначала проверить, есть ли нужная тема здесь.
- Если маршрут есть, начинать с указанных точек входа, state/validation-файлов и workflow, а не перечитывать дерево репозитория и историю коммитов.
- Если во время задачи пришлось заметно разбираться, «где это вообще находится» или «кто это запускает», найденный путь нужно сохранить или уточнить здесь до завершения подзадачи.
- Маршрут должен отвечать минимум на вопросы: где вход, кто владелец, чем запускается, какие state/validation-файлы смотреть, куда сохраняется результат, кто потребляет его дальше и по какому признаку работа завершена.
- Не дублировать здесь бизнес-правила и архитектурные контракты: давать ссылки на канонические файлы.
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