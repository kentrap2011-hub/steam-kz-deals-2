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
8. UI-задачи с real-device judgment закрывать только после пользовательской проверки.
9. Worker-чат удалять только после сохранённого report, решения директора и всех ближайших проверок.
10. Для активных задач хранить ожидаемый report path.
11. Task-file не считается запущенной, пока пользователь реально не отправил команду worker-чату.
12. Живые worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
13. Before semantic translation, first check approved ready-Russian sources. Translation is fallback, not default.
14. Current project commercial status: personal/non-commercial; commercial use requires `COMMERCIALIZATION_GUARD.md` review.
15. Task-memory invariant: future user work must have a durable destination; backlog removal requires destination/completion/cancellation evidence.
16. Worker efficiency is important, but prepared work is not automatically next.
17. **Priority discipline:** `prepared` does not mean `next`. When a worker finishes, first read its report, then choose direct continuation vs explicit user priority vs backlog.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Блок раздач в UI | Implement the separate production giveaway block from completed UI recon, then deploy and require user verification | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_01.md` | `reviews/worker_reports/cross-platform-giveaway-ui-01.md` | `status_check_requested` |
| `ЧАТ 2` | Production acceptance объяснений | Wait for the existing Russian-description runtime prerequisite, then rerun bounded production acceptance and require user verification | `WORKER_TASK_CARD_EXPLANATION_PRODUCTION_ACCEPTANCE_01.md` | `reviews/worker_reports/card-explanation-production-acceptance-01.md` | `blocked_on_existing_ru_runtime` |

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` remains prepared but is not advanced while direct unfinished continuations exist.
- Card no-grounded-negative analysis is a separate high-importance backlog diagnosis; absence of a grounded negative is exceptional incomplete analysis, not a normal fallback.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.

## Последние решения

- `card-explanation-production-acceptance-01` — `blocked`. The corrected explanation code and runner sample pass, but canonical production/deploy cannot proceed until the already-existing Russian-description runtime produces and ingests the required translations. Do not weaken the RU gate, add a second scheduler, or ask for user verification before deploy.
- `cross-platform-giveaway-ui-01` — mandatory report is absent and no fresh relevant giveaway-UI commit signal was observed in the one bounded status check. Do not restart or broaden investigation; request a short status report from the existing Chat 1 and continue only from its exact current step/blocker.
- `cross-platform-giveaway-ui-recon-01` — complete. Exact canonical visual handoff, fail-closed freshness/expiry semantics and safe v1 relevance policy are established.
- Existing rule 8 requires real-device acceptance for UI work.
- `steam-recommendation-count-fix-01` — complete. Canonical giveaway snapshot is live and complete.
- `worker-efficiency-guardrails-01` — complete; no follow-up required.
- `backlog-disposition-validator-01` — complete and validated in GitHub Actions.

## Выбор следующей работы

Do not advance unrelated backlog work while Chat 1 status is unresolved and Chat 2 is blocked on its existing prerequisite. After the next worker report/status update, choose from actual dependencies and priorities.