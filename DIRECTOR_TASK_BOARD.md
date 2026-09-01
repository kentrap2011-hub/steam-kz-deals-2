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
20. User priority override 2026-09-01: **time-limited claim-to-keep free-game giveaways across any reliably supportable storefronts are the highest-priority next product task once either current worker slot becomes free.** They are not Steam-only. Start with bounded RECON; do not let explanation/ranking polish or secondary features take that first free slot.
21. **Task-memory invariant:** any explicit user decision “сделать потом / добавить позже / отложить” must receive a durable destination in the same director step: current active task/board or `BACKLOG.md`. Removing a backlog item requires exact destination evidence: active task+report path, completed evidence, or explicit user cancellation/supersession. Never bulk-delete `needs_user_verification` items merely to shorten backlog.
22. Because `BACKLOG.md` was created on 2026-08-30 without migrating all earlier agreements, a one-time `task-memory-audit-01` is required to reconcile historical orphaned tasks. This audit must not displace the first-free-slot giveaway RECON; use the other next free slot.

## Активно / подготовлено сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Русские описания | One-record real scheduled-runtime acceptance: GitHub queue -> ChatGPT -> ingestion/cache -> visual rebuild | `WORKER_TASK_RU_TRANSLATION_RUNTIME_ACCEPTANCE_01.md` | `reviews/worker_reports/ru-translation-runtime-acceptance-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Объяснения карточек | Read-only audit of current “why fits / why may not fit” explanation quality on bounded top sample | `WORKER_TASK_CARD_EXPLANATION_AUDIT_01.md` | `reviews/worker_reports/card-explanation-audit-01.md` | `prepared_or_active` |

## Подготовлено на следующие свободные слоты

1. **Первый освободившийся слот — максимальный продуктовый приоритет:**
   - task: `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_RECON_01.md`
   - report: `reviews/worker_reports/cross-platform-giveaway-recon-01.md`
   - scope: time-limited permanent-claim giveaways across Steam, Epic Games Store, GOG and any other reliably supportable storefront/source; storefront-neutral architecture; READ-ONLY / RECON.

2. **Другой следующий свободный слот — project-memory integrity:**
   - task: `WORKER_TASK_TASK_MEMORY_AUDIT_01.md`
   - report: `reviews/worker_reports/task-memory-audit-01.md`
   - scope: audit pre-backlog agreements, historical backlog removals and durable destinations; identify any additional orphaned tasks; READ-ONLY / RECON.

## Worker chat lifecycle

- `ЧАТ 1 — Русские описания`: package/UI blocker is complete. Canonical pre-AI workflow publishes real translation scope; immediate step is one real scheduled-runtime round-trip acceptance. Keep the same chat until director reviews that report.
- Old duration state remains durable and blocked only on user-provisioned `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET`; it does not occupy an active slot.
- `ЧАТ 2 — Объяснения карточек`: independent read-only audit; safe in parallel with Chat 1 if the task was actually sent.
- When either active slot finishes, do **not** start explanation fixes or other polish first: launch cross-platform giveaway RECON.
- When the other slot becomes free, launch `task-memory-audit-01` before further secondary backlog work.

## Recovered task-memory findings already known

- Cross-platform free giveaways: product rule existed before `BACKLOG.md`; implementation task was not migrated into backlog. Restored 2026-09-01.
- Old media/screenshots verification: restored to `BACKLOG.md` as `recovered_needs_reconciliation` because historical status required user verification, user later reported the expected visible result still absent, and no later durable positive verification has been established yet.
- Chrome shortcut icon: do not restore solely because it vanished from backlog; user later positively verified the icon looked correct.
- Played-game achievements: removed from backlog but subsequently implemented with dedicated commits.
- Detailed normalized Taste factors: removed from backlog but subsequently implemented/cut over.
- Bundles/packages: explicitly moved into active work and later completed.
- Detailed score UI / misleading wishlist display: later completed and user-verified.

## Последние завершённые worker-этапы

- `package-ui-blocker-fix-01` — `complete`; canonical pre-AI workflow now reaches translation preparation and publishes real queue/status.
- `ru-translation-implement-01` — `needs_fix`; repo-side mechanics implemented; runtime round-trip remained to prove.
- `duration-igdb-implement-01` — code complete but blocked on missing GitHub Secrets.
- `ru-translation-contract-01` — `complete`.

## Ближайшие задачи

1. Current `ЧАТ 1`: finish translation runtime acceptance.
2. Current `ЧАТ 2`: finish explanation-quality audit if already launched.
3. **First freed slot:** `cross-platform-giveaway-recon-01`.
4. **Other next freed slot:** `task-memory-audit-01`.
5. After giveaway recon, prioritize its bounded contract/implementation sequence before explanation/ranking polish because giveaways expire.
6. User provisions IGDB secrets when convenient; resume duration connectivity acceptance in a later free slot unless an active time-limited giveaway issue takes precedence.
7. If translation acceptance passes, GitHub/scheduled runtime owns remaining translation scope; interactive chats do not manually process it.