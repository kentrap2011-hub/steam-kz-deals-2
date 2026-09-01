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
| `ЧАТ 1` | Русские описания | Implement GitHub-owned translation scope/result ingestion/cache/resolver against existing nightly ChatGPT runtime | `WORKER_TASK_RU_TRANSLATION_IMPLEMENT_01.md` | `reviews/worker_reports/ru-translation-implement-01.md` | `implementation_committed_report_missing` |
| `ЧАТ 2` | Длительность | IGDB implementation code complete; waiting only for IGDB/Twitch GitHub Secrets and live connectivity acceptance | `WORKER_TASK_DURATION_IGDB_IMPLEMENT_01.md` | `reviews/worker_reports/duration-igdb-implement-01.md` | `blocked_on_user_provisioning` |

## Worker chat lifecycle

- `ЧАТ 1 — Русские описания`: implementation commits are present on `main` (scope producer, ingestion, cache, resolver, workflow and bounded scope build), but the required report `reviews/worker_reports/ru-translation-implement-01.md` is not yet saved. Do not delete or assign a new task; same chat must only save the report/closeout for the work already done.
- `ЧАТ 2 — Длительность`: implementation code/report saved. Do not assign more code until user provisions `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`; then use the existing canonical workflow for bounded connectivity acceptance.

## Отложено / superseded

- `WORKER_TASK_RU_TRANSLATION_PROVIDER_RECON_01.md` — cancelled by user decision.
- Wikimedia ready-Russian secondary source — not approved as production dependency; incomplete coverage + CC BY-SA obligations.

## Последние завершённые worker-этапы

- `duration-igdb-implement-01` — code complete but status `blocked` on missing GitHub Secrets. GitHub-owned IGDB collection/cache/final-builder path implemented and tested synthetically; production collection remains disabled. Expected secrets: `IGDB_CLIENT_ID`, `IGDB_CLIENT_SECRET`.
- `ru-translation-contract-01` — `complete`; canonical translation request/result/cache contracts added, existing nightly scheduled ChatGPT runtime reused, GitHub remains control-plane owner.
- `ru-description-source-recon-01` — `complete`; no broad second ready-Russian source; translation still needed for some unresolved descriptions.
- `duration-contract-01` — `complete`; canonical `DURATION-ENRICHMENT-V1` chooses IGDB `game_time_to_beats`, GitHub-direct, unchanged `unknown = 2/3`.
- `ru-description-implement-01` — deterministic description quality gate implemented; legacy payload has 132/442 invalid descriptions.
- `duration-provider-recon-01` — `complete`; IGDB primary recommendation.
- `duration-source-recon-01` — `complete`.
- `duration-data-diagnosis-01` — root cause proven.
- `detailed-score-user-fixes-01` — `complete`; phone check passed.
- `compact-purchase-options-01` — `complete`; phone check passed.

## Ближайшие задачи

1. Same `ЧАТ 1` saves `reviews/worker_reports/ru-translation-implement-01.md` for the already committed implementation; no rework.
2. Then director reviews whether the repo-side translation implementation is actually complete or requires one scheduled-runtime follow-up.
3. User provisions `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` for Chat 2 connectivity acceptance.
4. Track the separate pre-existing package/UI regression independently.
5. After both data-quality paths are fully live/rebuilt — user spot-check of visible cards.