# CURRENT TASK

## Taste V3 migration: recover interrupted scheduled run

Статус: in_progress
Дата исходной задачи: 2026-08-30
Последнее обновление handoff: 2026-08-31

Цель:
- завершить миграцию active production scope с `legacy_coarse_fit` на пять нормализованных price-blind taste factors `0..100`;
- сохранять уже выполненную semantic работу только если её provenance и exact bindings действительно соответствуют текущему каноническому semantic contract;
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
6. Stale/noncanonical semantic results нельзя relabel/rebind в current model без доказанной semantic equivalence.

Последний подтверждённый прогресс:
- canonical Taste V3 cutover уже завершён; V3 result/cache contracts и штатный ingest path существуют;
- актуальный `data/production/pre_ai/chatgpt_payload.json` перед recovery содержит `ai_queue_count=634`, `ready_without_ai_count=0`, `deterministically_excluded_without_ai_count=25`;
- scheduled worker опубликовал пять submission-файлов `data/ai_inbox/taste/2026-08-31T0630Z-001..005.json`, всего 500 результатов;
- 134 строки текущего GitHub-owned taste scope не получили submission до runtime/tool limit;
- все пять опубликованных файлов имеют одинаковую top-level binding, которая **не совпадает** с текущей canonical `taste_projection.json`: submission использует model `price_blind_taste_v3`, semantic digest `fc0e4846…`, source timestamp `2026-08-30T14:27:39Z`; current canonical projection использует `taste-v3` и другой semantic digest/source snapshot;
- в `001` дополнительно подтверждён отдельный typo `App_1261040.taste_fingerprint`: лишняя завершающая `a` относительно текущей queue;
- первоначальный bounded repair helper попытался исправить только этот typo, но run `33372236792` / job `99425727094` правильно остановился fail-closed на **global binding mismatch до commit/persistence**;
- после этого ошибочное предположение «проблема только в одном fingerprint» отменено; one-shot helper удалён commit `31a3f3e2b84185ab32cf0a4e5bbdf1776681331b`;
- пять submission-файлов сейчас **не считать canonical/ingested** и не переписывать их binding metadata вручную;
- долговечный быстрый маршрут и recovery-инварианты добавлены в `PROJECT_ROUTES.md` → `Taste V3 / normalized factors` commit `ce70e24a674e0bd3288f53d600ed46263ab20acf`;
- SteamDB на отдельном маршруте сейчас имеет 8/9 resolved; `App_901735` остаётся единственным retry с `steamdb_runtime_disabled_error`. Это не переносить в ручной backlog interactive chat.

Следующий шаг — provenance existing scheduled worker:
1. Проверить **конфигурацию/инструкцию существующего scheduled ChatGPT semantic worker**, который создал пять файлов.
2. Установить, почему он записал `price_blind_taste_v3` + старый semantic digest/source binding вместо current canonical `taste-v3` projection.
3. Если worker реально выполнял старый semantic contract — не сохранять 500 результатов посредством relabel; дать существующему worker переоценить нужный GitHub-owned scope под current contract.
4. Если worker фактически выполнял текущий semantic contract, а неверной была только serialization/binding metadata, сначала документально доказать semantic equivalence и только затем делать bounded migration через штатный GitHub validator/ingest.
5. Для простой визуальной проверки настроек scheduled-задачи сначала попросить пользователя открыть её в ChatGPT и прислать prompt/instructions; это предпочтительнее обходных поисков и экономит context budget.
6. Не polling внешнего worker-а. После одного observable check ждать нового события/пользовательского продолжения.

После разрешения provenance:
1. Использовать только `.github/workflows/ingest-taste-batch.yml` → `scripts/process_taste_inbox.py` → `scripts/ingest_taste_results.py`; direct cache writes запрещены.
2. Проверить новый `chatgpt_payload.json`, `taste_projection.json`, bounded cache/index diagnostics и ingest receipts.
3. Оставшийся semantic scope должен закрывать existing scheduled worker; interactive chat не обрабатывает сотни строк вручную.
4. После фактического закрытия очереди проверить downstream rebuild и `score_precision=normalized_taste_factors`, затем синхронизировать `PROJECT_DECISIONS.md` и удалить `CURRENT_TASK.md`.

Коммуникационный инвариант:
- правило «ответ > 1 минуты → в этом же ответе разобрать причину задержки и сделать долговечное ускорение для будущих чатов» уже было в `CHAT_CONTEXT.md`;
- 2026-08-31 оно дополнительно поднято в начало `README.md` как **КРИТИЧЕСКИЙ ИНВАРИАНТ ЭФФЕКТИВНОСТИ**, чтобы новый чат видел его до глубокой навигации;
- пользователь готов выполнять простые визуальные проверки страницы/GitHub Actions/настроек задачи по просьбе ассистента, чтобы не расходовать context budget на обходные retrieval-пути.

Definition of done:
- provenance пяти опубликованных 100-row submissions установлен и не подменён предположением;
- только semantically/current-bound V3 результаты приняты существующим GitHub ingest;
- оставшаяся GitHub-owned taste queue закрыта штатным scheduled semantic worker либо содержит только явно допустимые permanent-failure исключения;
- final producer получает `taste_factors` и active scope использует `score_precision=normalized_taste_factors` там, где нет более сильного direct-user-rating источника;
- production rebuild/validation проходит;
- `PROJECT_ROUTES.md` и `PROJECT_DECISIONS.md` синхронизированы, затем `CURRENT_TASK.md` удалён.
