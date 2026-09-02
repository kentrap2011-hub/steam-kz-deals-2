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
| `ЧАТ 1` | Блок раздач в UI | User verifies the deployed separate giveaway block on the actual phone/site | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_01.md` | `reviews/worker_reports/cross-platform-giveaway-ui-01.md` | `needs_user_verification` |
| `ЧАТ 2` | Пропавшие минусы карточек | Diagnose why cards can reach final output with no grounded negative evidence and define the generic remediation path | `WORKER_TASK_CARD_NEGATIVE_ANALYSIS_GAP_01.md` | `reviews/worker_reports/card-negative-analysis-gap-01.md` | `ready_to_continue_in_existing_chat` |

## Ожидает внешнего prerequisite, worker-слот не занимает

- `card-explanation-production-acceptance-01` remains `blocked` on the already-existing Russian-description runtime. Current canonical status is still `translation_required` with `queue_count=164`. When that prerequisite is produced/ingested, resume only the bounded production acceptance: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` remains prepared.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.

## Последние решения

- `cross-platform-giveaway-ui-01` — technical implementation is deployed and validated. Canonical bounded visual refresh succeeded, Pages deploy succeeded, and current deployed giveaway state is `active` with 2 offers. Task remains `needs_user_verification` until the user confirms the real phone/site UI; do not delete Chat 1 before that confirmation.
- Chat 2's card-explanation production acceptance remains genuinely blocked on the external existing RU-description runtime; this waiting state does not consume the worker slot.
- Chat 2 is assigned the bounded `card-negative-analysis-gap-01` diagnosis because the user explicitly elevated missing grounded negatives as a product defect.
- `cross-platform-giveaway-ui-recon-01` — complete.
- `steam-recommendation-count-fix-01` — complete.
- `worker-efficiency-guardrails-01` — complete.
- `backlog-disposition-validator-01` — complete and validated in GitHub Actions.

## Выбор следующей работы

After the next worker report, read it first. Do not advance Trine 4 ahead of a direct fix produced by the negative-analysis diagnosis unless the diagnosis is complete with no follow-up.