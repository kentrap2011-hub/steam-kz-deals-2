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

## Активно / подготовлено сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Русские описания | Fix pre-existing package/UI regression that blocks pre-AI workflow before translation acceptance | `WORKER_TASK_PACKAGE_UI_BLOCKER_FIX_01.md` | `reviews/worker_reports/package-ui-blocker-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Длительность | IGDB implementation code complete; waiting only for IGDB/Twitch GitHub Secrets and live connectivity acceptance | `WORKER_TASK_DURATION_IGDB_IMPLEMENT_01.md` | `reviews/worker_reports/duration-igdb-implement-01.md` | `blocked_on_user_provisioning` |

## Worker chat lifecycle

- `ЧАТ 1 — Русские описания`: `ru-translation-implement-01` report is now saved with status `needs_fix`. Repo-side translation mechanics exist, but production scope publication and scheduled-runtime round-trip are not yet proven. Immediate next step is the narrow package/UI blocker fix because that regression stops the canonical pre-AI workflow before translation stages. Keep the same chat for this bounded follow-up.
- `ЧАТ 2 — Длительность`: implementation code/report saved. Do not assign more code until user provisions `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`; then use the existing canonical workflow for bounded connectivity acceptance.

## Последние завершённые worker-этапы

- `ru-translation-implement-01` — `needs_fix`; scope producer, ingestion, cache, resolver and workflow integration implemented. Remaining acceptance gaps: successful current production translation scope/status publication after final dedupe and end-to-end scheduled ChatGPT round-trip. Report `reviews/worker_reports/ru-translation-implement-01.md`.
- `duration-igdb-implement-01` — code complete but blocked on missing GitHub Secrets.
- `ru-translation-contract-01` — `complete`.
- `ru-description-source-recon-01` — `complete`.
- `duration-contract-01` — `complete`.

## Ближайшие задачи

1. Same `ЧАТ 1`: fix the package/UI regression with `WORKER_TASK_PACKAGE_UI_BLOCKER_FIX_01.md`.
2. Then run one bounded Russian translation runtime acceptance: current GitHub scope -> scheduled ChatGPT -> strict ingestion/cache -> visual rebuild.
3. User provisions `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` for Chat 2 connectivity acceptance.
4. After both data-quality paths are fully live/rebuilt — user spot-check of visible cards.