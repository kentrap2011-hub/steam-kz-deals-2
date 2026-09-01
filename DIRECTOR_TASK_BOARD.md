# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные: worker-slot, задача, report path, статус, приоритет и пользовательские проверки.

## Правила работы

1. Одновременно по умолчанию работают не больше двух worker-чатов.
2. Нормальная пара: одна главная задача + одна независимая небольшая задача.
3. Перед запуском проверять пересечение областей и canonical ownership.
4. Неясная проблема сначала идёт в bounded `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
5. Bounded sample разрешён только для диагностики/validation. Interactive worker не должен вручную обрабатывать production-каталог item-by-item.
6. Полный production scope, queue, ordering, retries, persistence, completeness и downstream rebuild принадлежат GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
7. Если GitHub не может получить внешний/semantic факт сам, scheduled ChatGPT получает только GitHub-prepared exact scope и возвращает результат через canonical interface; interactive worker не создаёт собственную production-очередь.
8. UI-задачи с реальным-device judgment закрывать только после пользовательской проверки.
9. Worker-чат удалять только после сохранённого report, решения директора и всех ближайших проверок.
10. Для активных задач хранить ожидаемый report path. При фразе `один чат закончил` директор сам проверяет reports и свежие commits.
11. Если expected report не найден, но worker сообщил о завершении, дополнительно проверить свежие commits; если report всё равно отсутствует, считать результат не сохранённым.
12. Task-file не считается запущенной, пока пользователь реально не отправил команду worker-чату.
13. Живые worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
14. Первая строка каждого копируемого сообщения worker-у содержит его метку.
15. Та же метка повторяется во всех follow-up сообщениях этому чату.
16. Before semantic translation, first check approved ready-Russian sources. Translation is fallback, not default.
17. User decision 2026-09-01: when translation is required, prefer ChatGPT semantic translation over generic machine-translation APIs.
18. Current project commercial status: personal/non-commercial. Before any future monetization read `COMMERCIALIZATION_GUARD.md` and re-audit provider rights/terms.
19. Do not leave a worker slot idle solely because an unrelated track is waiting on user provisioning. Durable blocked state stays in GitHub; the slot may be reused for an independent task and later returned to the blocked track in a fresh chat.

## Активно / подготовлено сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Русские описания | One-record real scheduled-runtime acceptance: GitHub queue -> ChatGPT -> ingestion/cache -> visual rebuild | `WORKER_TASK_RU_TRANSLATION_RUNTIME_ACCEPTANCE_01.md` | `reviews/worker_reports/ru-translation-runtime-acceptance-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Объяснения карточек | Read-only audit of current “why fits / why may not fit” explanation quality on bounded top sample | `WORKER_TASK_CARD_EXPLANATION_AUDIT_01.md` | `reviews/worker_reports/card-explanation-audit-01.md` | `prepared_or_active` |

## Worker chat lifecycle

- `ЧАТ 1 — Русские описания`: package/UI blocker is complete. Canonical pre-AI workflow now publishes real translation scope successfully (155 pending translations in the verified run). Immediate next step is one real scheduled-runtime round-trip acceptance. Keep the same chat.
- Old duration Chat 2 state remains durable and blocked only on user-provisioned `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET`; it does not occupy an active slot.
- `ЧАТ 2 — Объяснения карточек`: independent read-only audit, safe to run in parallel with Chat 1.

## Последние завершённые worker-этапы

- `package-ui-blocker-fix-01` — `complete`; stale static regression fixed, canonical pre-AI workflow run passed and produced real Russian translation queue/status. Verified run had `translation_queue_count=155`, `resolved_direct_ru_count=389`, `nontranslatable_blocker_count=26`.
- `ru-translation-implement-01` — `needs_fix`; repo-side mechanics implemented; runtime round-trip remained unproven before blocker fix.
- `duration-igdb-implement-01` — code complete but blocked on missing GitHub Secrets.
- `ru-translation-contract-01` — `complete`.

## Ближайшие задачи

1. `ЧАТ 1`: perform `ru-translation-runtime-acceptance-01` on exactly one deterministic current queue record through the existing scheduled ChatGPT runtime.
2. `ЧАТ 2`: continue explanation-quality audit in parallel.
3. User provisions IGDB secrets when convenient; then resume duration connectivity acceptance in a fresh free slot.
4. If translation acceptance passes, let GitHub/scheduled runtime own the remaining production translation scope; do not manually process the 155 records in interactive chat.
5. After data-quality paths are live/rebuilt — user spot-check of visible cards.