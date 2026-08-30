# PROJECT_ROUTES

Практическая карта маршрутов проекта. Заполняется только по мере реальной работы: если рабочий чат уже нашёл, где находится конкретная логика/пайплайн, он добавляет сюда этот маршрут, чтобы следующий чат не искал его заново.

## Исторический минимум SteamDB (KZ / KZT)

**Что ищем:** точный исторический минимум цены SteamDB для текущих primary offer keys.

**Канонический контракт:**
- `config/steamdb_lookup_contract.json`
- `config/steamdb_checkpoint_contract.json`
- ownership: `config/execution_ownership_contract.json`

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

**Важная архитектурная граница:** GitHub владеет очередью, retry-state, completeness, validation, persistence и downstream. Прямой SteamDB lookup из GitHub Actions отключён, потому что SteamDB систематически отвечает GitHub Actions HTTP 403; внешний lookup выполняется ограниченным runtime-worker, а интерактивный чат не должен вручную обрабатывать production backlog.

**Текущее состояние на 2026-08-30:** `data/cache/steamdb_runtime_work.json` = 534 ожидаемых, 529 resolved, 5 unresolved retry (`runtime_web_internal_error`).
