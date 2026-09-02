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
| `ЧАТ 1` | Компактные раздачи + карточки | Fix failed phone acceptance: collapse giveaways behind a compact control and enrich each giveaway with safe description/pros/cons when exact canonical identity permits | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_UX_FIX_01.md` | `reviews/worker_reports/cross-platform-giveaway-ui-ux-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Пропавшие минусы карточек | Diagnose why cards can reach final output with no grounded negative evidence and define the generic remediation path | `WORKER_TASK_CARD_NEGATIVE_ANALYSIS_GAP_01.md` | `reviews/worker_reports/card-negative-analysis-gap-01.md` | `ready_to_continue_in_existing_chat` |

## Ожидает внешнего prerequisite, worker-слот не занимает

- `card-explanation-production-acceptance-01` remains `blocked` on the already-existing Russian-description runtime. Resume only after the existing prerequisite is produced/ingested, then run visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` remains prepared.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.

## Последние решения

- `cross-platform-giveaway-ui-01` reached production and Pages successfully, but **failed real-device acceptance**. User confirmed the block exists, but it occupies too much vertical space when always expanded and lacks enough per-game decision information.
- Direct Chat 1 continuation is `cross-platform-giveaway-ui-ux-fix-01`: collapsed-by-default compact control is mandatory; expanded giveaway entries should include description + pros + cons only through exact canonical identity/evidence. No title-only/fuzzy Steam binding is allowed. If enrichment lacks a safe canonical route, report the exact architecture gap instead of fabricating content.
- Real-device acceptance remains mandatory after redeploy; Chat 1 must not be deleted before the user approves the revised UI.
- Chat 2 remains on `card-negative-analysis-gap-01`.
- `card-explanation-production-acceptance-01` remains parked on its external RU-description prerequisite.

## Выбор следующей работы

After either worker report, read it first and choose the direct continuation before unrelated backlog work.