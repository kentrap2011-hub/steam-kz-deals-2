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
18. **Review checkpoint invariant:** before assigning a new ordinary backlog task whenever a worker slot becomes free, read `DIRECTOR_REVIEW_CHECKPOINTS.md`. If a mandatory review is due, it takes priority unless the user explicitly gives a more urgent time-sensitive task.
19. `TASTE REVIEWER` is a separate advisory chat. It does not implement production changes and therefore does not consume one of the two implementation worker slots while used only in the boundaries of `TASTE_REVIEWER_ROLE.md`.
20. `SYSTEM AUDITOR` is an independent periodic review role governed by `SYSTEM_AUDITOR_ROLE.md`; it must not be forgotten or replaced by ordinary acceptance tests.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Срочно: ускорить ленту | First blank-feed fix deployed and partially successful; follow-up instant last-known-good cache task is prepared but not yet sent to worker | `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md` | `reviews/worker_reports/mobile-feed-instant-cache-fix-01.md` | `prepared_direct_continuation_not_started` |
| `ЧАТ 2` | Свежесть публикации | Final acceptance passed; branch ready for merge/release but release deferred during mobile incident | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md` | `reviews/worker_reports/visual-freshness-chain-acceptance-02.md` | `complete_release_deferred_chat_can_delete` |

## Urgent user-visible incident — mobile feed load latency

- Original symptom: shell/controls interactive but feed blank after load/reload; app-switch/return could make games appear.
- Recon report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`, blob `48700dc77ac17fa031dd129996bef74075d86872`.
- First fix report: `reviews/worker_reports/mobile-page-blank-feed-fix-01.md`, blob `61b23ffc479dff473310b1d7aed0d36d43a11c8f`.
- First production fix ref: `af2c7362743b4fe3d80ea10caee7cb606acab3e5`; Pages run `33766838776` succeeded.
- First fix added visible `Загружаю игры…`, 9-second timeout, max 2 attempts, guarded lifecycle recovery and explicit error state.
- Real-device result on 2026-09-03: **partial success**. Silent blank feed is gone. Sometimes refresh is instant; sometimes `Загружаю игры…` remains visible for several seconds, then games appear. User explicitly says the problem is improved but not solved and asks whether it can be fixed.
- Director decision: yes; do not keep blocking repeat visits on network. Prepared direct continuation `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`.
- Follow-up target behavior: after one successful load on a device, show last-known-good feed locally immediately on future open/reload, then refresh canonical `data/current.json` in background; network failure/latency must not blank or block already-available cards.
- Canonical source remains network `data/current.json`; local browser storage is presentation fallback only, not a second source of truth.
- No service worker, polling, second renderer, ranking/Taste changes, or visual-freshness merge inside this follow-up.
- User has **not yet been given/sent** the follow-up worker command because the conversation paused to prepare a Director replacement. Treat the task as prepared, not started.
- Keep existing Chat 1 until this incident is fully user-verified or a successor Director explicitly reassigns it.

## Semantic runtime completion — accepted

- Follow-up acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Closed.

## Visual freshness — accepted, release deferred

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- All acceptance controls pass and branch `worker/visual-freshness-chain-fix-01` is ready for production merge/release.
- Release remains deferred until mobile feed incident is stabilized and overlap risk is reassessed.
- Chat 2 can be deleted.

## System Auditor checkpoint

- Last report: `reviews/system_audits/baseline-01.md`.
- `system_audit_due: true`.
- Urgent mobile feed incident still pre-empts audit until stabilized.
- After incident stabilization, run due System Audit before ITAD/ordinary implementation work.

## Taste Reviewer — baseline complete

- Dedicated reviewer established.
- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- ITAD permission confirmed.
- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started`, lower priority than mobile incident and due System Audit.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. If user wants to continue the mobile fix now, send existing Chat 1 `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md` and mark it started only after the user actually sends the command.
2. Require real-device verification again after deploy: repeated reloads should normally show cards immediately from last-known-good cache while fresh data updates in background.
3. Do not release the accepted visual-freshness branch during the mobile follow-up unless Director explicitly reassesses overlap risk.
4. After mobile incident stabilization, run due System Audit before ITAD/ordinary backlog implementation.
5. Then schedule accepted visual-freshness release and ITAD provider-switch implementation at the safest bounded point.