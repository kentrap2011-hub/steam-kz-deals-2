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
| `НОВЫЙ ЧАТ 2` | Анализ карточек раздач | Find the safe canonical cross-store identity/analysis route so giveaway detail cards can show real description, pros and grounded cons without title matching | `WORKER_TASK_GIVEAWAY_ANALYSIS_IDENTITY_RECON_01.md` | `reviews/worker_reports/giveaway-analysis-identity-recon-01.md` | `ready_for_new_chat` |

## Параллельность

- Эти две задачи разрешено выполнять одновременно: Trine 4 трассирует paid Steam/KZ selection path, а giveaway identity recon исследует storefront-neutral identity/analysis handoff для Epic/GOG giveaway details. Они не должны менять общие production runtime/queues в RECON-режиме.
- Trine 4 остаётся временно более срочной из-за активной скидки, но второй worker-slot не должен простаивать, пока giveaway identity recon можно вести независимо.

## Явный временный приоритет пользователя

- Пользователь 2026-09-02 поднял Trine 4 выше остальных текущих задач, потому что игра сейчас находится на скидке. Диагностику нужно выполнить пока live sale state ещё наблюдаем; иначе после окончания акции отсутствие игры может стать объяснимым просто отсутствием скидки и потеряется исходный failure shape.
- `giveaway-analysis-identity-recon-01` выполняется параллельно во втором слоте и не считается отменённым/отложенным до окончания Trine 4.

## Заменённый worker-чат

- Старый `ЧАТ 1` достиг лимита контекста до сохранения `reviews/worker_reports/giveaway-analysis-identity-recon-01.md`. Его больше не использовать.
- Старый `ЧАТ 2` был удалён пользователем после завершения grounded-negative implementation; его состояние сохранено в GitHub и не требуется для новых задач.

## Принятый UI раздач

- `cross-platform-giveaway-separate-view-fix-01` — real-device UX accepted by user on 2026-09-02. Compact giveaway button is convenient, separate Wishlist-style view is convenient. Do not revisit this navigation/layout unless a new defect appears.
- Remaining giveaway requirement is only content completeness inside per-game detail: real description + pros + grounded cons.

## Ожидает внешнего prerequisite, worker-слот не занимает

- `grounded-negative-implement-01`: implementation deployed; existing GitHub-owned Taste queue has 599 rows (`576` targeted negative-only backfills + `23` full Taste evaluations) with `resolve_grounded_negative_analysis`. No worker context is needed while waiting for the existing scheduled Taste runtime.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime. After prerequisite: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- Duration connectivity remains blocked on user-provisioned IGDB secrets.

## Последние решения

- Trine 4 diagnosis is Chat 1 because the active discount is time-sensitive diagnostic evidence.
- Giveaway analysis identity recon moves to NEW CHAT 2 in parallel; no need to leave the second worker slot idle.
- Both are RECON, so neither may introduce production mutations beyond their task's permitted reporting/management evidence.

## Выбор следующей работы

Read whichever report arrives first, but if Trine 4 finds a systemic defect, its bounded direct fix keeps priority while the sale condition remains relevant. Giveaway identity may continue independently if its next step does not overlap that fix.