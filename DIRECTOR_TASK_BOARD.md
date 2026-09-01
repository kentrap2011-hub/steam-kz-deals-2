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
| `ЧАТ 1` | Русские описания | Fix pre-existing package/UI regression that blocks pre-AI workflow before translation acceptance | `WORKER_TASK_PACKAGE_UI_BLOCKER_FIX_01.md` | `reviews/worker_reports/package-ui-blocker-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Объяснения карточек | Read-only audit of current “why fits / why may not fit” explanation quality on bounded top sample | `WORKER_TASK_CARD_EXPLANATION_AUDIT_01.md` | `reviews/worker_reports/card-explanation-audit-01.md` | `prepared_for_new_chat` |

## Worker chat lifecycle

- `ЧАТ 1 — Русские описания`: `ru-translation-implement-01` report is saved with status `needs_fix`. Immediate next step is the narrow package/UI blocker fix because that regression stops the canonical pre-AI workflow before translation stages. Keep the same chat for this bounded follow-up.
- Old `ЧАТ 2 — Длительность`: duration implementation state/report is durable in GitHub and waiting only on user-provisioned `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET`. It does not need to occupy a worker slot. The old chat may be deleted if desired. When credentials are ready, duration connectivity acceptance can resume in a fresh Chat 2 or whichever slot is free.
- New `ЧАТ 2 — Объяснения карточек`: independent read-only audit; no writes to shared visual/UI/runtime files except its report, so it may run in parallel with Chat 1.

## Последние завершённые worker-этапы

- `ru-translation-implement-01` — `needs_fix`; scope producer, ingestion, cache, resolver and workflow integration implemented. Remaining acceptance gaps: successful current production translation scope/status publication after final dedupe and end-to-end scheduled ChatGPT round-trip.
- `duration-igdb-implement-01` — code complete but blocked on missing GitHub Secrets; durable state retained in report.
- `ru-translation-contract-01` — `complete`.
- `ru-description-source-recon-01` — `complete`.
- `duration-contract-01` — `complete`.

## Ближайшие задачи

1. `ЧАТ 1`: fix package/UI blocker, then translation runtime acceptance.
2. `ЧАТ 2`: audit explanation quality in parallel.
3. User provisions `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` when convenient; then resume duration connectivity acceptance in a fresh free slot.
4. After both data-quality paths are fully live/rebuilt — user spot-check of visible cards.
5. Russian language availability as ranking factor.
6. YouTube later.