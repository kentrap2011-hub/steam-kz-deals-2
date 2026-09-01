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
| `ЧАТ 1` | Блок раздач в UI | Recon the canonical UI handoff, expiry behavior and safe relevance policy for the now-live giveaway snapshot | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_RECON_01.md` | `reviews/worker_reports/cross-platform-giveaway-ui-recon-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Объяснения карточек | Fix the single remaining generated-sample personal-taste-link violation | `WORKER_TASK_CARD_EXPLANATION_FIX_01.md` | `reviews/worker_reports/card-explanation-fix-01.md` | `awaiting_closeout_report` |

## Подготовлено, но НЕ назначено следующим

- Trine 4 missing-game diagnosis remains in `BACKLOG.md`; it is not precommitted ahead of the direct giveaway continuation.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.
- Russian translation real round-trip remains blocked on an occurrence of the existing Nightly Production Runtime.

## Последние решения

- `steam-recommendation-count-fix-01` — complete. The prior recommendation-count blocker attribution was incorrect; canonical rerun `33539362872` attempt 2 succeeded without weakening Steam guards and produced a complete `CROSS-PLATFORM-GIVEAWAY-V1` snapshot with 2 accepted current Epic offers. No data-plane blocker remains.
- Giveaway user requirement is not yet fully closed because the separate visible UI block and safe relevance semantics remain. Direct bounded UI/relevance recon selected for the same Chat 1 context; do not repeat source/data-plane work.
- Chat 2 still awaits its mandatory `card-explanation-fix-01` closeout report.
- `worker-efficiency-guardrails-01` — complete; no follow-up required.
- `backlog-disposition-validator-01` — complete and validated in GitHub Actions.

## Выбор следующей работы

No unrelated task is precommitted after the current two workers.
When either finishes, read that report first and choose the next step from actual dependencies and priorities.