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
| `ЧАТ 1` | Бесплатные раздачи | Implement Tier-1 cross-platform giveaway data plane: hardened Steam + Epic KZ + GOG KZ | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_IMPLEMENT_01.md` | `reviews/worker_reports/cross-platform-giveaway-implement-01.md` | `active_or_ready` |
| `ЧАТ 2` | Защита памяти задач | Add fail-closed backlog deletion -> durable disposition validator | `WORKER_TASK_BACKLOG_DISPOSITION_VALIDATOR_01.md` | `reviews/worker_reports/backlog-disposition-validator-01.md` | `ready_for_new_chat` |

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_WORKER_EFFICIENCY_AUDIT_01.md` -> `reviews/worker_reports/worker-efficiency-audit-01.md` (`prepared_unscheduled`).
- Explanation-quality implementation remains deferred.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.
- Russian translation real round-trip remains blocked on an occurrence of the existing Nightly Production Runtime.

## Последние решения

- `task-memory-audit-01` — complete; no new unrecovered orphaned/ambiguous tasks found. The only confirmed lifecycle gaps were the already restored cross-platform giveaways and media/screenshots reconciliation tail.
- Direct follow-up chosen for Chat 2: implement the small machine-checkable backlog deletion guard recommended by the audit, rather than start another unrelated prepared task.
- `cross-platform-giveaway-recon-01` completed its source/architecture recon; Chat 1 is now on direct Tier-1 implementation.

## Выбор следующей работы

No unrelated task is precommitted after the current two workers.
When either finishes, read that report first and choose the next step from actual dependencies and priorities.