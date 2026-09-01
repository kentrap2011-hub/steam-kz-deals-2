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
| `ЧАТ 1` | Бесплатные раздачи | Finish canonical production wiring/run for Tier-1 cross-platform giveaways | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_PRODUCTION_FIX_01.md` | `reviews/worker_reports/cross-platform-giveaway-production-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Эффективность worker-чатов | Implement minimal durable worker pitfall guardrails from completed efficiency audit | `WORKER_TASK_WORKER_EFFICIENCY_GUARDRAILS_01.md` | `reviews/worker_reports/worker-efficiency-guardrails-01.md` | `ready_to_continue_in_existing_chat` |

## Подготовлено, но НЕ назначено следующим

- Explanation-quality implementation remains deferred.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.
- Russian translation real round-trip remains blocked on an occurrence of the existing Nightly Production Runtime.

## Последние решения

- `cross-platform-giveaway-implement-01` — `needs_fix`: adapters/contract/producer/tests are implemented, but producer/tests are not yet wired into canonical GitHub production/validation and no live versioned giveaway snapshot exists. Direct bounded production-wiring fix selected for Chat 1.
- `worker-efficiency-audit-01` — complete; Chat 2 is on its minimal operational-doc follow-up.
- `backlog-disposition-validator-01` — complete and validated in GitHub Actions.

## Выбор следующей работы

No unrelated task is precommitted after the current two workers.
When either finishes, read that report first and choose the next step from actual dependencies and priorities.