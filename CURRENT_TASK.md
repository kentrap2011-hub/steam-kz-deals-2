# CURRENT TASK

## Taste V3 migration: recover interrupted scheduled run

Статус: in_progress
Дата исходной задачи: 2026-08-30
Последнее обновление handoff: 2026-08-31

Цель:
- завершить миграцию active production scope с `legacy_coarse_fit` на пять нормализованных price-blind taste factors `0..100`;
- использовать только существующий GitHub-owned queue/ingest/downstream pipeline;
- не превращать interactive chat в массовый semantic worker.

Architecture preflight:
1. GitHub владеет scope, queue, exact binding validation, persistence, completeness и downstream rebuild.
2. Existing scheduled ChatGPT taste worker остаётся semantic data-plane.
3. Новая recurring stage/queue/quota/retry-loop не создаётся.
4. Stale/noncanonical semantic results нельзя relabel/rebind без доказанной semantic equivalence.

Подтверждённый provenance вывод:
- `config/taste_result_contract.json` создан commit `e0e687968eacd7f2994a33a6c942ba639e7ec8da` и с тех пор не менялся; именно он задаёт пять normalized factor semantics.
- До canonical V3 cutover projection была `taste-v2` с semantic digest `28177637756ffc4cf51ea8cb7a37b6e3d1173dd11f852deb56966d29261ec13b`.
- Bounded normalized-factor canary commit `9d9e4e4aa044c125048c1922d583a9726e40e4da` тоже был привязан к `taste-v2` / `281776…`, хотя уже содержал `taste_factors`.
- Canonical V3 cutover commit `89b0376b820926369714b748d2404c87dcd88405` перевёл model binding на `taste-v3` и semantic digest `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`; cutover прямо добавил `taste_factor_semantics` из canonical result contract в semantic digest.
- Пять interrupted-run submissions `2026-08-31T0630Z-001..005.json` использовали `price_blind_taste_v3` + digest `fc0e4846…` + stale source binding. Такой canonical binding не найден ни до, ни после V3 cutover.
- Текущий scheduled-task prompt, присланный пользователем для анализа, требует копировать exact bindings из текущего `taste_projection.json`; он не содержит `price_blind_taste_v3` и не объясняет `fc0e…`.
- Поэтому provenance этих 500 результатов недостаточен для безопасного rebind. По fail-closed правилу их нельзя считать current V3 и нельзя сохранять простым переписыванием metadata.

Recovery decision:
- старые 500 результатов должны быть переоценены существующим scheduled semantic worker по текущей GitHub-owned queue;
- пять невалидных submission-файлов удаляются только из active inbox, чтобы не блокировать будущий transactional ingest; Git history остаётся аудитом их содержимого и происхождения;
- canonical cache/projection/payload/queue/ranking вручную не редактируются.

Следующий шаг после очистки inbox:
1. Existing scheduled ChatGPT worker читает текущие `chatgpt_payload.json`, `taste_projection.json`, exact profile blob и `chatgpt_taste_queue.jsonl` и возвращает current-bound `taste-v3` submissions максимум по 100 результатов на файл.
2. Не создавать меньшую дневную квоту: если runtime позволяет, worker продолжает весь GitHub-prepared scope в том же run; hard runtime/tool limit означает partial/incomplete, а не success.
3. Штатный `.github/workflows/ingest-taste-batch.yml` валидирует exact bindings, atomically ingest-ит valid inbox и пересобирает queue.
4. После закрытия queue проверить downstream build и `score_precision=normalized_taste_factors`, затем синхронизировать `PROJECT_ROUTES.md` + `PROJECT_DECISIONS.md` и удалить `CURRENT_TASK.md`.

Коммуникационные инварианты:
- если ответ занимает >1 минуты, в том же ответе объяснить задержку и сделать долговечное ускорение;
- если ассистент сам запросил prompt/log/config для анализа, следующий такой блок — diagnostic material, а не команда на запуск без отдельной явной просьбы пользователя;
- простые визуальные проверки по возможности просить пользователя сделать напрямую, сложную contract/diff диагностику выполнять инструментами.

Definition of done:
- invalid interrupted-run inbox не блокирует ingest;
- current GitHub-owned taste queue закрыта только current-bound V3 submissions;
- downstream production validation проходит;
- final producer использует normalized taste factors там, где это предусмотрено ranking precedence;
- `PROJECT_ROUTES.md` / `PROJECT_DECISIONS.md` синхронизированы, `CURRENT_TASK.md` удалён.
