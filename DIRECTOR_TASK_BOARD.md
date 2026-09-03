# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные: worker-slot, задача, report path, статус, приоритет и пользовательские проверки.

## Правила работы

1. Одновременно по умолчанию работают не больше двух implementation worker-чатов.
2. Нормальная пара: одна главная задача + одна независимая небольшая задача.
3. Перед запуском проверять пересечение областей и canonical ownership.
4. Неясная проблема сначала идёт в bounded `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
5. Bounded sample разрешён только для диагностики/validation. Interactive worker не должен вручную обрабатывать production-каталог item-by-item.
6. Полный production scope, queue, ordering, retries, persistence, completeness и downstream rebuild принадлежат GitHub/GitHub Actions по `config/execution_ownership_contract.json`.
7. Если GitHub не может получить внешний/semantic факт сам, scheduled ChatGPT получает only GitHub-prepared exact scope и возвращает результат через canonical interface; interactive worker не создаёт собственную production-очередь.
8. UI-задачи с real-device judgment закрывать только после пользовательской проверки.
9. Worker-чат удалять только после сохранённого report, решения директора и всех ближайших проверок.
10. Для активных задач хранить ожидаемый report path.
11. Task-file не считается запущенной, пока пользователь реально не отправил команду worker-чату.
12. Живые implementation worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
13. Before semantic translation, first check approved ready-Russian sources. Translation is fallback, not default.
14. Current project commercial status: personal/non-commercial; commercial use requires `COMMERCIALIZATION_GUARD.md` review.
15. Task-memory invariant: future user work must have a durable destination; backlog removal requires destination/completion/cancellation evidence.
16. Worker efficiency is important, but prepared work is not automatically next.
17. **Priority discipline:** `prepared` does not mean `next`. When a worker finishes, first read its report, then choose direct continuation vs explicit user priority vs dependencies vs backlog.
18. **Review checkpoint invariant:** before assigning a new ordinary backlog task whenever an implementation worker slot becomes free, read `DIRECTOR_REVIEW_CHECKPOINTS.md`. If a mandatory review is due, it takes priority unless the user explicitly gives a more urgent time-sensitive task.
19. `TASTE REVIEWER` is a separate advisory chat. It does not implement production changes and therefore does not consume one of the two implementation worker slots while used only in the boundaries of `TASTE_REVIEWER_ROLE.md`.
20. `SYSTEM AUDITOR` is an independent periodic review role governed by `SYSTEM_AUDITOR_ROLE.md`; it must not be forgotten or replaced by ordinary acceptance tests.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Срочно: страница не реагирует | Localize mobile interaction freeze where cold load/reload is non-interactive but app-switch/resume temporarily restores interaction | `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md` | `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md` | `ready_to_start_new_chat` |
| `ЧАТ 2` | Финальная приёмка свежести | Verify completed freshness receipt + exact deploy binding implementation before production merge/release | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md` | `reviews/worker_reports/visual-freshness-chain-acceptance-02.md` | `running_or_ready_in_existing_chat` |

## Urgent user-visible incident — mobile interaction freeze

- User report 2026-09-03: discounts page is currently badly broken; nothing opens/responds after load; switching to another app and returning temporarily restores interaction; after refresh/reload it is broken again.
- Classification: urgent user-visible UI incident; explicitly pre-empts the due System Audit and prepared ITAD implementation until localized/stabilized.
- Task: `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md`.
- Mode: `READ-ONLY / RECON` first because exact mechanism is unknown.
- Required likely lenses: blocking overlay/pointer interception, missing event binding/initialization, mobile visibility/pageshow lifecycle, service-worker/cache asset mismatch, runtime exception.
- No implementation until recon localizes the first failure mechanism.
- Any fix will require real-device user verification before closure.

## Semantic runtime completion — accepted

- Follow-up acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Runtime observability: pass.
- Feed semantic completeness visibility: pass.
- No duplicate scheduler/runtime/queue.
- Director decision: closed; old Chat 1 can be deleted/replaced by the new urgent incident chat.

## Visual freshness — implementation complete, acceptance due

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Status: `complete`.
- Implementation branch: `worker/visual-freshness-chain-fix-01`.
- Added durable `visual-freshness-receipt-v1` and exact deploy verification against triggering build run.
- Focused bounded tests pass for fresh, degraded/no-build and stale-mismatch cases.
- No production deployment was performed by implementation.
- Continue only its bounded acceptance in existing Chat 2; do not merge/release merely because this new UI incident exists unless acceptance explicitly permits and Director decides no overlap/risk.

## System Auditor checkpoint

- Last report: `reviews/system_audits/baseline-01.md`.
- `system_audit_due: true` after accepted semantic-runtime control/stabilized incident.
- The new page-interaction incident is an explicit urgent user priority and may pre-empt the audit.
- After this incident and the direct Chat 2 continuation are stable, run the due System Audit before ordinary implementation work.

## Taste Reviewer — baseline complete

- Dedicated reviewer established.
- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- ITAD permission confirmed.
- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started` and now explicitly lower priority than the urgent page-interaction incident and due audit.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Start NEW Chat 1 with `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md` immediately.
2. Let existing Chat 2 finish only its already-assigned visual-freshness acceptance.
3. When urgent recon finishes, read its exact report first and assign a bounded fix if localized.
4. Real-device user verification is mandatory after any UI fix.
5. After incident stabilization + Chat 2 direct continuation, run due System Audit before ITAD/ordinary backlog implementation.