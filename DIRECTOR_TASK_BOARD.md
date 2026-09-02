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
| `ЧАТ 1` | Раздачи как отдельный Wishlist-style экран | Replace inline/expandable giveaway UX with a compact nav control that opens a separate giveaway view; per-game analysis stays in a separate detail card | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_SEPARATE_VIEW_FIX_01.md` | `reviews/worker_reports/cross-platform-giveaway-separate-view-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Реализация подтверждённых минусов | Implement the approved V4 negative-analysis contract, existing Taste queue work-code, structured mapper and paid-card readiness gate | `WORKER_TASK_GROUNDED_NEGATIVE_IMPLEMENT_01.md` | `reviews/worker_reports/grounded-negative-implement-01.md` | `ready_to_continue_in_existing_chat` |

## Завершённый direct predecessor Chat 2

- `grounded-negative-contract-recon-01` — complete design/recon. Approved implementation direction: explicit `negative_analysis_status`, structured `negative_findings`, existing queue work code `resolve_grounded_negative_analysis`, targeted negative-only backfill, structured no-drop mapping and end-to-end grounded-negative readiness witness.

## Заменённые / superseded UI-направления Chat 1

- `cross-platform-giveaway-ui-ux-fix-01` — deployed but failed user preference: inline expanded list remained too bulky.
- `cross-platform-giveaway-ui-detail-card-fix-01` — superseded before acceptance by the user's clearer preference for the existing Wishlist-style separate view. Do not continue nested expandable-list UX as the final design.

## Заменённый worker-чат

- Старый `ЧАТ 2` (`card-negative-analysis-gap-01`) больше не используется; его report сохранён и diagnosis complete.

## Ожидает внешнего prerequisite, worker-слот не занимает

- `card-explanation-production-acceptance-01` остаётся `blocked` на существующем Russian-description runtime. После появления prerequisite: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` остаётся подготовленным.
- Duration connectivity остаётся blocked на user-provisioned IGDB secrets.

## Последние решения

- `grounded-negative-contract-recon-01` produced an implementation-grade contract. Direct continuation is `grounded-negative-implement-01`; do not repeat diagnosis/design.
- Normal ready INCLUDE must have `complete_with_confirmed_negative` plus at least one structured grounded finding that survives to a visible grounded Taste risk. `incomplete_no_confirmed_negative` is truthful but unresolved and must not masquerade as a complete card.
- Existing GitHub-owned Taste queue/runtime is reused; no second scheduler/queue.
- Chat 1 remains on Wishlist-style separate giveaway view until successful phone acceptance.

## Выбор следующей работы

After either worker report, read it first. Direct continuations have priority over unrelated backlog work.