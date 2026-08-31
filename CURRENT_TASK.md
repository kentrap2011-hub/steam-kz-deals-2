# CURRENT TASK

## Taste V3 migration: recover interrupted scheduled run

Статус: in_progress
Дата исходной задачи: 2026-08-30
Последнее обновление handoff: 2026-08-31

Цель:
- завершить миграцию active production scope с `legacy_coarse_fit` на пять нормализованных price-blind taste factors `0..100`;
- сохранить уже выполненную semantic работу и не переоценивать валидные результаты повторно;
- использовать только существующий GitHub-owned queue/ingest/downstream pipeline, без нового recurring worker или ручной обработки большого backlog в interactive chat.

Факторы:
- `gameplay_mastery`
- `development_variety`
- `structure_pacing_direction`
- `identity_hooks`
- `breadth_of_match`

Architecture preflight:
1. GitHub остаётся владельцем scope, queue, exact binding validation, persistence, completeness и downstream rebuild по `config/execution_ownership_contract.json`.
2. Existing scheduled ChatGPT taste worker остаётся semantic data-plane по `config/taste_result_contract.json`.
3. Interactive chat выполняет только bounded recovery/diagnosis и не становится массовым semantic worker.
4. Новая recurring stage, новая очередь, новая квота или retry-loop не создаются.
5. `config/daily_execution_contract.json` остаётся неизменным: один nightly production cycle, batching — только checkpointing.

Последний подтверждённый прогресс:
- canonical Taste V3 cutover уже завершён; V3 result/cache contracts и ingest path существуют;
- актуальный `data/production/pre_ai/chatgpt_payload.json` перед recovery содержит `ai_queue_count=634`, `ready_without_ai_count=0`, `deterministically_excluded_without_ai_count=25`;
- scheduled worker опубликовал пять submission-файлов `data/ai_inbox/taste/2026-08-31T0630Z-001..005.json`, всего 500 результатов;
- 134 строки текущего GitHub-owned taste scope остались без semantic result после runtime/tool limit;
- в `001` подтверждён единственный известный binding typo: `App_1261040.taste_fingerprint` имеет лишнюю завершающую `a`; canonical queue содержит правильный fingerprint без неё;
- для безопасного bounded recovery создан одноразовый workflow `.github/workflows/repair-interrupted-taste-v3.yml`: он срабатывает на это обновление `CURRENT_TASK.md`, исправляет только доказанный typo, валидирует `001` против текущей queue и удаляет сам себя;
- изменение repaired submission должно штатно запустить существующий `.github/workflows/ingest-taste-batch.yml`, который атомарно валидирует и ingest-ит все пять inbox-файлов, пересобирает taste projection/payload/queue и удаляет обработанные submission-файлы;
- SteamDB на отдельном маршруте сейчас имеет 8/9 resolved; `App_901735` остаётся единственным retry с `steamdb_runtime_disabled_error`. Это не переносить в ручной backlog interactive chat.

Быстрое продолжение без повторного исследования:
1. НЕ перечитывать большие submission JSON целиком и НЕ переоценивать первые 500 игр.
2. Проверить один observable result: появился ли commit `Repair interrupted Taste V3 submission` и затем штатный `Ingest context-bound taste batch`.
3. После ingest читать только `data/production/pre_ai/chatgpt_payload.json`, `data/production/pre_ai/taste_projection.json` и bounded cache/index diagnostics. Ожидаемая taste queue после успешного ingest первых 500 результатов — 134, если current scope/bindings не изменились.
4. Если ingest fail-closed, открыть только конкретный failed run/job/log и исправить причину; не обходить exact binding validation.
5. Оставшиеся semantic rows должен обработать существующий scheduled ChatGPT worker. Interactive chat не обрабатывает 134 строки вручную.
6. После фактического закрытия очереди проверить downstream rebuild и `score_precision=normalized_taste_factors`, затем синхронизировать `PROJECT_ROUTES.md` + `PROJECT_DECISIONS.md` и удалить `CURRENT_TASK.md`.

Коммуникационный инвариант:
- правило «ответ > 1 минуты → в этом же ответе разобрать причину задержки и сделать долговечное ускорение для будущих чатов» уже было в `CHAT_CONTEXT.md`; 2026-08-31 оно дополнительно поднято в начало `README.md` как **КРИТИЧЕСКИЙ ИНВАРИАНТ ЭФФЕКТИВНОСТИ**.

Definition of done:
- известный typo `App_1261040` исправлен через bounded one-shot recovery;
- первые 500 опубликованных V3 результатов приняты существующим GitHub ingest и не пересчитаны вручную;
- оставшаяся GitHub-owned taste queue закрыта штатным scheduled semantic worker либо содержит только явно допустимые permanent-failure исключения;
- final producer получает `taste_factors` и active scope использует `score_precision=normalized_taste_factors` там, где нет более сильного direct-user-rating источника;
- production rebuild/validation проходит;
- `PROJECT_ROUTES.md` и `PROJECT_DECISIONS.md` синхронизированы, затем `CURRENT_TASK.md` удалён.
