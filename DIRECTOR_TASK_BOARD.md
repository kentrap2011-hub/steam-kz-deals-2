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
22. Because `BACKLOG.md` was created on 2026-08-30 without migrating all earlier agreements, a one-time `task-memory-audit-01` is required to reconcile historical orphaned tasks. This audit belongs to a worker, not the director chat.

## Активно / подготовлено сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Бесплатные раздачи | Cross-platform claim-to-keep giveaway source/production architecture recon | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_RECON_01.md` | `reviews/worker_reports/cross-platform-giveaway-recon-01.md` | `ready_for_new_chat` |
| `ЧАТ 2` | Объяснения карточек | Read-only audit of current “why fits / why may not fit” explanation quality on bounded top sample | `WORKER_TASK_CARD_EXPLANATION_AUDIT_01.md` | `reviews/worker_reports/card-explanation-audit-01.md` | `prepared_or_active` |

## Подготовлено на следующий свободный слот

- task: `WORKER_TASK_TASK_MEMORY_AUDIT_01.md`
- report: `reviews/worker_reports/task-memory-audit-01.md`
- scope: audit pre-backlog agreements, historical backlog removals and durable destinations; identify any additional orphaned tasks; READ-ONLY / RECON.

## Worker chat lifecycle

- Old `ЧАТ 1 — Русские описания`: `ru-translation-runtime-acceptance-01` saved with status `blocked`. Repo-side queue/runtime/ingestion path is ready, but one real result must arrive from the existing Nightly Production Runtime; worker correctly did not create a second scheduler or manually translate. This state is durable; old chat no longer needs to occupy a slot and may be deleted. Resume later in a fresh free slot after a real nightly translation result exists or when the existing runtime binding can be addressed safely.
- New `ЧАТ 1 — Бесплатные раздачи`: launch as a fresh chat because it is independent from Russian descriptions and benefits from clean context.
- `ЧАТ 2 — Объяснения карточек`: independent read-only audit; continue if already launched.
- When the next slot becomes free, launch `task-memory-audit-01`; the director should not perform that historical audit itself.

## Recovered task-memory findings already known

- Cross-platform free giveaways: product rule existed before `BACKLOG.md`; implementation task was not migrated into backlog. Restored 2026-09-01.
- Old media/screenshots verification: restored to `BACKLOG.md` as `recovered_needs_reconciliation`.
- Chrome shortcut icon: later positively user-verified; do not restore solely because it vanished from backlog.
- Played-game achievements: subsequently implemented.
- Detailed normalized Taste factors: subsequently implemented/cut over.
- Bundles/packages: explicitly moved into active work and later completed.
- Detailed score UI / misleading wishlist display: later completed and user-verified.

## Последние завершённые / blocked worker-этапы

- `ru-translation-runtime-acceptance-01` — `blocked`; current queue has 155 pending translations, repo-side binding exists, but no real scheduled-runtime result has yet occurred. Resume only through the existing Nightly Production Runtime.
- `package-ui-blocker-fix-01` — `complete`.
- `ru-translation-implement-01` — repo-side implementation completed; real runtime round-trip remains operationally pending.
- `duration-igdb-implement-01` — code complete but blocked on missing GitHub Secrets.

## Ближайшие задачи

1. **NEW ЧАТ 1:** run `cross-platform-giveaway-recon-01` now.
2. Current `ЧАТ 2`: finish explanation-quality audit if already launched.
3. Next freed slot: `task-memory-audit-01`.
4. After giveaway recon, prioritize its bounded contract/implementation sequence before explanation/ranking polish because giveaways expire.
5. Resume Russian translation acceptance only through the existing Nightly Production Runtime after a real result exists; do not create a second scheduler.
6. User provisions IGDB secrets when convenient; resume duration connectivity acceptance in a later free slot.