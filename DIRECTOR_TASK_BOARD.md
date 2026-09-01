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
| `ЧАТ 1` | Блок раздач в UI | Implement the separate production giveaway block from completed UI recon, then deploy and require user verification | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_01.md` | `reviews/worker_reports/cross-platform-giveaway-ui-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Production acceptance объяснений | Prove the already-fixed card explanations reach canonical production payload and Pages, then require user verification | `WORKER_TASK_CARD_EXPLANATION_PRODUCTION_ACCEPTANCE_01.md` | `reviews/worker_reports/card-explanation-production-acceptance-01.md` | `ready_for_new_chat` |

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` remains prepared but is no longer the immediate free-slot choice because card-explanation production acceptance is a direct unfinished continuation.
- Card no-grounded-negative analysis is now a separate high-importance backlog diagnosis; absence of a grounded negative is exceptional incomplete analysis, not a normal fallback.
- Duration connectivity remains blocked on user-provisioned IGDB secrets.
- Russian translation real round-trip remains blocked on an occurrence of the existing Nightly Production Runtime.

## Последние решения

- `cross-platform-giveaway-ui-recon-01` — complete. Exact canonical visual handoff, fail-closed freshness/expiry semantics and safe v1 relevance policy are established; Chat 1 continues directly to bounded implementation with mandatory production deploy + user-device acceptance.
- `card-explanation-fix-01` — code and runner sample pass, but Director closure was premature. Current canonical `data/production/visual/current.json` latest commit is `24b2890d0c85b14213fd0b91256afcfb306eb01e` from `2026-09-01T08:20:42Z`, which predates the final explanation fix. Therefore the fix is not yet production/user-visible accepted; a dedicated production acceptance task is now the direct Chat 2 priority.
- Existing rule 8 already required real-device acceptance for UI work. No new process mechanism is needed; the prior Director decision violated the existing rule and is corrected here.
- `steam-recommendation-count-fix-01` — complete. Canonical giveaway snapshot is live and complete.
- `worker-efficiency-guardrails-01` — complete; no follow-up required.
- `backlog-disposition-validator-01` — complete and validated in GitHub Actions.

## Выбор следующей работы

Do not advance Trine 4 while card-explanation production acceptance is still unfinished. After a worker finishes, read that report first and choose the next step from actual dependencies and priorities.