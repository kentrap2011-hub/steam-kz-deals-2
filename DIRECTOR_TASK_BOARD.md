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
10. Для активных задач хранить ожидаемый report path. При фразе `один чат закончил` директор сам проверяет reports и свежие commits.
11. Если expected report не найден, но worker сообщил о завершении, дополнительно проверить свежие commits; если report всё равно отсутствует, считать результат не сохранённым.
12. Task-file не считается запущенной, пока пользователь реально не отправил команду worker-чату.
13. Живые worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
14. Первая строка каждого копируемого сообщения worker-у содержит его метку.
15. Та же метка повторяется во всех follow-up сообщениях этому чату.
16. Before semantic translation, first check approved ready-Russian sources. Translation is fallback, not default.
17. User decision 2026-09-01: when translation is required, prefer ChatGPT semantic translation over generic machine-translation APIs.
18. Current project commercial status: personal/non-commercial. Before any future monetization read `COMMERCIALIZATION_GUARD.md` and re-audit provider rights/terms.
19. Do not leave a worker slot idle solely because an unrelated track is waiting on user provisioning. Durable blocked state stays in GitHub; the slot may be reused for an independent task and later returned to the blocked track in a fresh chat.
20. User priority override 2026-09-01: time-limited claim-to-keep free-game giveaways across any reliably supportable storefronts are a high product priority. They are not Steam-only.
21. Task-memory invariant: any explicit user decision “сделать потом / добавить позже / отложить” must receive a durable destination in the same director step: current active task/board or `BACKLOG.md`.
22. Because `BACKLOG.md` was created without migrating all earlier agreements, a one-time `task-memory-audit-01` is required. This audit belongs to a worker, not the director chat.
23. Worker efficiency is a first-class operational concern, but speed must not replace correctness. A bounded `worker-efficiency-audit-01` is prepared to inspect repeated avoidable detours.
24. **Priority discipline:** `prepared` does not mean `next`. A newly created useful task must not automatically become the next free-slot assignment. By default there is no precommitted next task while both workers are active. When a worker finishes, the director first reads its report and then chooses the next task from direct continuation, user priority, dependencies and backlog. Only an explicit user priority or an obvious time-critical/direct continuation may be predeclared as next.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Бесплатные раздачи | Cross-platform claim-to-keep giveaway source/production architecture recon | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_RECON_01.md` | `reviews/worker_reports/cross-platform-giveaway-recon-01.md` | `active_or_ready` |
| `ЧАТ 2` | Память задач | Audit pre-backlog agreements, historical removals and orphaned tasks | `WORKER_TASK_TASK_MEMORY_AUDIT_01.md` | `reviews/worker_reports/task-memory-audit-01.md` | `active_or_ready` |

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_WORKER_EFFICIENCY_AUDIT_01.md` -> `reviews/worker_reports/worker-efficiency-audit-01.md`
  - purpose: repeated worker dead ends / redundant reads / reruns / closeout rework;
  - status: `prepared_unscheduled`;
  - it does not automatically take the first freed slot.

Other deferred product/operational work stays in `BACKLOG.md` or durable blocked state and is selected only after current worker reports are reviewed.

## Worker chat lifecycle

- `ЧАТ 1 — Бесплатные раздачи`: current high-priority recon.
- `ЧАТ 2 — Память задач`: current one-time integrity audit; director does not duplicate it.
- When either worker finishes, do not blindly launch a prewritten task. Read the report first, determine whether a direct continuation is more important, then select from actual priorities.

## Последние завершённые / blocked worker-этапы

- `card-explanation-audit-01` — audit complete; explanation implementation remains deferred.
- `ru-translation-runtime-acceptance-01` — blocked on a real occurrence of the existing Nightly Production Runtime; no second scheduler.
- `package-ui-blocker-fix-01` — complete.
- `duration-igdb-implement-01` — code complete but blocked on missing GitHub Secrets.

## Выбор следующей работы

No task is globally precommitted as “next” while both current workers are active.

When a slot frees:
1. read that worker report;
2. decide whether its direct continuation is necessary/urgent;
3. compare that continuation against explicit user priorities and current backlog;
4. only then assign the free slot.

Prepared tasks such as `worker-efficiency-audit-01` are candidates, not promises.