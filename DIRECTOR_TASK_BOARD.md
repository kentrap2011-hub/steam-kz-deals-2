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
| `ЧАТ 1` | Анализ карточек раздач | Find the safe canonical cross-store identity/analysis route so giveaway detail cards can show real description, pros and grounded cons without title matching | `WORKER_TASK_GIVEAWAY_ANALYSIS_IDENTITY_RECON_01.md` | `reviews/worker_reports/giveaway-analysis-identity-recon-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Свободный слот | — | — | — | `free` |

## Принятый UI раздач

- `cross-platform-giveaway-separate-view-fix-01` — real-device UX accepted by user on 2026-09-02. Compact giveaway button is convenient, separate Wishlist-style view is convenient. Do not revisit this navigation/layout unless a new defect appears.
- Remaining giveaway requirement is only content completeness inside per-game detail: real description + pros + grounded cons.

## Ожидает внешнего prerequisite, worker-слот не занимает

- `grounded-negative-implement-01`: implementation deployed; existing GitHub-owned Taste queue has 599 rows (`576` targeted negative-only backfills + `23` full Taste evaluations) with `resolve_grounded_negative_analysis`. The user deleted Chat 2; no worker context is needed while waiting for the existing scheduled Taste runtime.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime. After prerequisite: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` remains prepared.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.

## Последние решения

- User accepted the giveaway navigation UX but confirmed detail cards still lack real description/pros/cons. This is no longer a UI-layout issue.
- Direct Chat 1 continuation is `giveaway-analysis-identity-recon-01`: find a safe generic cross-store canonical identity route and analysis handoff. Do not repeat UI/source recon, do not map by title, and do not manually whitelist current Epic games.
- `grounded-negative-implement-01` remains parked on the existing Taste runtime; deleting the worker chat does not lose state because report/queue ownership are durable in GitHub.

## Выбор следующей работы

After Chat 1 recon report, choose its exact direct implementation or prerequisite. The free Chat 2 slot may take another independent task only if it does not interfere with the active direct continuation.