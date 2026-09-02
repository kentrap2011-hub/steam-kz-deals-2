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
17. **Priority discipline:** `prepared` does not mean `next`. When a worker finishes, first read its report, then choose direct continuation vs explicit user priority vs dependencies vs backlog.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Раздачи как отдельный Wishlist-style экран | User verifies deployed separate giveaway view on phone | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_SEPARATE_VIEW_FIX_01.md` | `reviews/worker_reports/cross-platform-giveaway-separate-view-fix-01.md` | `needs_user_verification` |
| `ЧАТ 2` | Подтверждённые минусы | Implementation is complete; wait for existing scheduled Taste runtime to process the grounded-negative backfill, then rerun canonical acceptance | `WORKER_TASK_GROUNDED_NEGATIVE_IMPLEMENT_01.md` | `reviews/worker_reports/grounded-negative-implement-01.md` | `blocked_on_existing_taste_runtime` |

## Ожидает внешнего prerequisite, worker-слот не занимает

- `grounded-negative-implement-01`: implementation is deployed; current GitHub-owned Taste queue has 599 rows (`576` targeted negative-only backfills + `23` full Taste evaluations) with work code `resolve_grounded_negative_analysis`. No manual worker processing and no second scheduler.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime. After prerequisite: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` остаётся подготовленным.
- Duration connectivity остаётся blocked на user-provisioned IGDB secrets.

## Последние решения

- `cross-platform-giveaway-separate-view-fix-01` — implementation and Pages deploy complete; not stuck. Status is `needs_user_verification`. Main feed no longer contains giveaway rows; `🎁 Раздачи (N)` opens a separate compact view and `Подробнее` opens one-game detail.
- `grounded-negative-implement-01` — implementation complete, canonical tests pass, and final visual acceptance now correctly fails closed on legacy/unresolved negative readiness. Existing scheduled Taste runtime must process 599 rows before production can become normal-ready.
- Direct worker work for Chat 2 is currently finished; the external runtime wait should not consume a worker slot.

## Выбор следующей работы

Do not call either track complete until its acceptance condition is met. Chat 1 requires phone verification. Chat 2 resumes only after the existing Taste runtime produces/ingests grounded-negative results.