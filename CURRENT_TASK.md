# CURRENT TASK

## Taste score: детальные нормализованные факторы

Статус: in_progress
Дата: 2026-08-30
Подхвачено новым чатом: 2026-08-30 23:39 Europe/Samara
Последнее обновление handoff: 2026-08-31

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
5. Миграция делается через model/semantics binding invalidation и существующую queue; interactive chat не становится массовым worker-ом.

Последний подтверждённый прогресс:
- V3 result/cache contracts, normalized-factor validation, ingestion, propagation в visual feed и ranking regression реализованы;
- bounded end-to-end V3 canary успешно прошёл существующий ingest/downstream путь; commit `379b0d41e2df6c0a1f4ac7eb08e78078b9efe0c7` (`Ingest context-bound taste batch`) и следующий refresh `496ce639961c54627c485f4fbaadd24f0ff9220d`;
- canonical V3 cutover завершён commit `89b0376b820926369714b748d2404c87dcd88405` (`Cut over taste evaluation to V3 factors`);
- `config/mailing_policy.json` и taste-cache binding теперь используют `taste-v3`, normalized factor semantics входят в canonical semantic digest;
- one-shot cutover workflow после успешного commit удалён и не является новой recurring стадией;
- `data/production/pre_ai/chatgpt_payload.json` подтверждает `taste_model_version=taste-v3`;
- текущая existing taste queue содержит 624 semantic evaluations; 31 candidate deterministic-excluded без AI; `ready_without_ai_count=0`;
- все 624 queue rows требуют normalized taste factors через существующий semantic pipeline;
- массовую очередь вручную в interactive chat не обрабатывать.

Быстрое продолжение без повторного исследования:
1. НЕ повторять canary и НЕ восстанавливать V3 cutover — он уже завершён в `main`.
2. Сначала открыть раздел `PROJECT_ROUTES.md` → `Taste V3 / normalized factors`.
3. Проверить только существующего owning scheduled semantic worker и факт появления новых V3 submissions/cache entries.
4. Не опрашивать внешнюю автоматизацию в цикле: максимум 1–2 bounded state checks. Если нет нового события/результата, не ждать синхронно в interactive chat и не создавать второй worker.
5. После появления worker output проверить ingest → taste cache → final producer и bounded `score_precision=normalized_taste_factors`.
6. После фактической миграции active scope синхронизировать `PROJECT_ROUTES.md` + `PROJECT_DECISIONS.md`, затем удалить `CURRENT_TASK.md`.

Следующий шаг:
1. Подтвердить, что existing scheduled ChatGPT taste worker подхватывает V3 queue и пишет штатные submissions.
2. После первых/очередных штатных submissions проверить, что factor vectors валидируются и сохраняются без ручного rebind.
3. После завершения backlog запустить downstream rebuild и bounded production verification.

Definition of done:
- contracts/result validation/cache поддерживают factor vector;
- current semantic worker contract/prompt требует factor vector;
- старые active entries переоцениваются существующим pipeline;
- final producer получает `taste_factors` и использует их вместо coarse fallback;
- production rebuild проходит;
- bounded проверка показывает детальный `score_precision=normalized_taste_factors` на активном scope или явно фиксирует только допустимые permanent-failure исключения;
- `PROJECT_ROUTES.md` и `PROJECT_DECISIONS.md` синхронизированы, затем `CURRENT_TASK.md` удалён.
