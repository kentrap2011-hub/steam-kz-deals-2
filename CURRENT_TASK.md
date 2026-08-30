# CURRENT TASK

## Taste score: детальные нормализованные факторы

Статус: in_progress
Дата: 2026-08-30
Подхвачено новым чатом: 2026-08-30 23:39 Europe/Samara

Цель:
- заменить для активного production scope грубый `legacy_coarse_fit` (`strong/moderate`) детальными price-blind taste factors;
- semantic worker возвращает 5 нормализованных значений `0..100`, независимых от текущих весов;
- GitHub валидирует и хранит factor vector в canonical taste cache;
- `priority_ranking.py` применяет веса только из `config/final_ranking_policy.json`;
- изменение весов не требует новой AI-оценки уже детализированной игры;
- миграция старого cache идёт через существующую taste queue, без новой recurring стадии.

Факторы:
- `gameplay_mastery`
- `development_variety`
- `structure_pacing_direction`
- `identity_hooks`
- `breadth_of_match`

Architecture preflight:
1. GitHub остаётся владельцем scope, queue, binding validation, persistence и downstream rebuild по `config/execution_ownership_contract.json`.
2. Existing scheduled ChatGPT taste worker остаётся constrained semantic data-plane и только расширяет уже разрешённый результат новым factor vector.
3. Новая recurring stage/queue/retry логика не создаётся.
4. Taste factors не содержат цену, скидку, wishlist, SteamDB/history или sale urgency.
5. Для миграции bump `model_version` должен сделать старые cache entries stale и отправить активный scope в существующую queue.

Последний подтверждённый прогресс:
- V3 result/cache contracts, normalized-factor validation, ingestion, propagation в visual feed и ranking regression уже реализованы;
- latest implementation commit перед takeover: `c42bfb68c91bdef20e4fd9d6fb4fa980f7a49378`;
- GitHub Actions на момент takeover: 0 in-progress, 0 queued;
- canonical taste index всё ещё содержит 650 V2 entries и 0 entries с `taste_factors`;
- текущая taste queue содержит один V3 canary: `App_2248760` (`Car For Sale Simulator`).

Следующий шаг:
1. Провести bounded end-to-end V3 canary через существующий `data/ai_inbox/taste/*.json` → `ingest-taste-batch.yml`.
2. После успешного canary выполнить канонический V3 model/semantics cutover, не создавая новую recurring stage.
3. Проверить, что старый active scope стал stale и попал в существующую taste queue.
4. Не обрабатывать массовую очередь вручную в interactive chat; semantic backlog обязан проходить через owning scheduled worker.

Definition of done:
- contracts/result validation/cache поддерживают factor vector;
- current semantic worker contract/prompt требует factor vector;
- старые active entries переоцениваются существующим pipeline;
- final producer получает `taste_factors` и использует их вместо coarse fallback;
- production rebuild проходит;
- bounded проверка показывает детальный `score_precision=normalized_taste_factors` на активном scope или явно фиксирует только допустимые permanent-failure исключения;
- `PROJECT_ROUTES.md` и `PROJECT_DECISIONS.md` синхронизированы, затем `CURRENT_TASK.md` удалён.
