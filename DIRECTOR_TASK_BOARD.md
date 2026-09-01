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
| `ЧАТ 1` | Русские описания | Canonical GitHub-owned translation contract with constrained scheduled ChatGPT fallback | `WORKER_TASK_RU_TRANSLATION_CONTRACT_01.md` | `reviews/worker_reports/ru-translation-contract-01.md` | `prepared_for_new_chat` |
| `ЧАТ 2` | Длительность | Implement GitHub-direct IGDB duration collection/cache/final-builder path; stop cleanly if credentials absent | `WORKER_TASK_DURATION_IGDB_IMPLEMENT_01.md` | `reviews/worker_reports/duration-igdb-implement-01.md` | `active_in_existing_chat` |

## Worker chat lifecycle

- Old `ЧАТ 1 — Русские описания` reached maximum context; report saved; may be deleted. Slot `ЧАТ 1` is reused by a fresh translation-contract chat.
- `ЧАТ 2 — Длительность`: implementation task was sent to the existing chat rather than a fresh chat. This is acceptable; the task re-reads canonical GitHub state. Do **not** delete it mid-task. Switch to a fresh chat only if it reaches context limit or becomes confused/stale.

## Отложено / superseded

- `WORKER_TASK_RU_TRANSLATION_PROVIDER_RECON_01.md` — cancelled by user decision.
- Wikimedia ready-Russian secondary source — not approved as production dependency; incomplete coverage + CC BY-SA obligations.

## Последние завершённые worker-этапы

- `ru-description-source-recon-01` — `complete`; no broad second ready-Russian source; translation still needed for some unresolved descriptions.
- `duration-contract-01` — `complete`; canonical `DURATION-ENRICHMENT-V1` chooses IGDB `game_time_to_beats`, GitHub-direct, unchanged `unknown = 2/3`.
- `ru-description-implement-01` — deterministic description quality gate implemented; legacy payload has 132/442 invalid descriptions.
- `duration-provider-recon-01` — `complete`; IGDB primary recommendation.
- `duration-source-recon-01` — `complete`.
- `duration-data-diagnosis-01` — root cause proven.
- `detailed-score-user-fixes-01` — `complete`; phone check passed.
- `compact-purchase-options-01` — `complete`; phone check passed.

## Ближайшие задачи

1. `ЧАТ 1`: translation contract.
2. `ЧАТ 2`: IGDB implementation; if credentials missing, return exact provisioning steps and expected secret names without manual duration lookup.
3. After both data-quality paths are implemented/rebuilt — user spot-check of visible cards.
4. Ranking/card explanation quality audit — bounded recon top-30.
5. Russian language availability as ranking factor.
6. YouTube later.