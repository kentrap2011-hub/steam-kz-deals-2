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
| `НОВЫЙ ЧАТ 1` | Trine 4 пропала из списка | Capture the live discounted KZ state now, then find the first canonical stage where Trine 4 disappears from source/catalog to final visual output | `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` | `reviews/worker_reports/trine4-missing-diagnosis-01.md` | `ready_for_new_chat` |
| `ЧАТ 2` | Свободный слот | — | — | — | `free` |

## Явный временный приоритет пользователя

- Пользователь 2026-09-02 поднял Trine 4 выше остальных текущих задач, потому что игра сейчас находится на скидке. Диагностику нужно выполнить пока live sale state ещё наблюдаем; иначе после окончания акции отсутствие игры может стать объяснимым просто отсутствием скидки и потеряется исходный failure shape.
- `giveaway-analysis-identity-recon-01` сохранён и остаётся прямым продолжением карточек раздач после Trine 4; его нельзя забыть или считать отменённым.

## Заменённый worker-чат

- Старый `ЧАТ 1` достиг лимита контекста до сохранения `reviews/worker_reports/giveaway-analysis-identity-recon-01.md`. Его больше не использовать.

## Принятый UI раздач

- `cross-platform-giveaway-separate-view-fix-01` — real-device UX accepted by user on 2026-09-02. Compact giveaway button is convenient, separate Wishlist-style view is convenient. Do not revisit this navigation/layout unless a new defect appears.
- Remaining giveaway requirement is only content completeness inside per-game detail: real description + pros + grounded cons.

## Ожидает внешнего prerequisite, worker-слот не занимает

- `grounded-negative-implement-01`: implementation deployed; existing GitHub-owned Taste queue has 599 rows (`576` targeted negative-only backfills + `23` full Taste evaluations) with `resolve_grounded_negative_analysis`. No worker context is needed while waiting for the existing scheduled Taste runtime.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime. After prerequisite: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_GIVEAWAY_ANALYSIS_IDENTITY_RECON_01.md` remains prepared as the direct giveaway-content continuation after the time-sensitive Trine 4 diagnosis.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.

## Последние решения

- Trine 4 diagnosis supersedes giveaway analysis temporarily because the current discount is a time-sensitive diagnostic condition, not because the giveaway requirement lost priority permanently.
- Trine task now explicitly captures live KZ price/discount/source timestamp before deeper tracing.
- Old Chat 1 limit does not affect Trine work; start a new worker chat from the durable task file.

## Выбор следующей работы

Read `trine4-missing-diagnosis-01` first when it completes. If it finds a systemic defect, its bounded direct fix has priority while the sale condition remains relevant. Otherwise return to `giveaway-analysis-identity-recon-01`.