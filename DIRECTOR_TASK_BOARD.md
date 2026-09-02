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
| `ЧАТ 1` | Trine 4 пропала из списка | RECON complete; no worker continuation. Wait for the existing scheduled Taste runtime to resolve `App_690640`, then canonical ingest/rebuild decides actual feed admission | `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` | `reviews/worker_reports/trine4-missing-diagnosis-01.md` | `complete_waiting_existing_runtime` |
| `ЧАТ 2` | Анализ карточек раздач | Worker says finished, but expected durable report is missing; save the completed result to the exact report path without redoing recon | `WORKER_TASK_GIVEAWAY_ANALYSIS_IDENTITY_RECON_01.md` | `reviews/worker_reports/giveaway-analysis-identity-recon-01.md` | `awaiting_report_closeout` |

## Trine 4 diagnosis result

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Trine 4 is present through store snapshot, shortlist, purchase/deal context and Taste queue.
- First disappearance is semantic Taste readiness -> visual item preparation: `taste_cache_key_missing`, no resolved current Taste fit, so `build_visual_feed_v2.py::get_fit()` returns no admissible strong/moderate fit and the game never reaches ranking.
- Classification: `stale_or_incomplete_data`, not a Trine-specific price/ranking/region defect.
- Existing scheduled semantic runtime owns the needed evaluation. No manual insertion and no second queue/scheduler.

## Giveaway report closeout

- Expected report `reviews/worker_reports/giveaway-analysis-identity-recon-01.md` was not found after the user reported completion.
- One bounded repository search for the exact Task ID also found no saved result.
- Do not investigate implementation/history in Director. Return to the existing Chat 2 only to save its already-completed findings to the exact report path.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Trine 4 / `App_690640`: wait for existing scheduled Taste runtime + normal ingest/rebuild.
- `grounded-negative-implement-01`: same existing GitHub-owned Taste data-plane is processing unresolved semantic work; no worker-owned backfill.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime.

## Принятый UI раздач

- Giveaway navigation UX accepted by user on real device. Only analysis content/identity remains open.

## Выбор следующей работы

First obtain the missing Chat 2 report. After that, choose its bounded direct next step. Trine 4 needs no interactive worker until the existing semantic runtime has produced and ingested the missing Taste result.