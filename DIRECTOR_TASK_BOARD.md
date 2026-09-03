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
| `ЧАТ 1` | Срочно: исправить пустую ленту | Harden main-feed bootstrap so load/reload cannot remain silently blank; add bounded timeout/retry/lifecycle recovery and diagnostics | `WORKER_TASK_MOBILE_PAGE_BLANK_FEED_FIX_01.md` | `reviews/worker_reports/mobile-page-blank-feed-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Свежесть публикации | Final acceptance passed; branch ready for merge/release but release deferred during incident | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md` | `reviews/worker_reports/visual-freshness-chain-acceptance-02.md` | `complete_release_deferred_chat_can_delete` |

## Urgent user-visible incident — mobile feed content missing

- User real-device evidence: controls/tabs work; feed cards are absent after normal load/refresh; app-switch/return can make them appear.
- Recon report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`, blob `48700dc77ac17fa031dd129996bef74075d86872`.
- Canonical payload inspected by recon is non-empty (`item_count: 442` at recon time), so the incident is not explained by a truly empty feed source.
- Highest-confidence application failure boundary: single-shot unbounded `await fetch('data/current.json', { cache: 'no-store' })` before first feed render. Both card and empty/error surfaces begin hidden, so an unresolved/suspended request can leave an interactive shell with a blank feed indefinitely.
- Exact Android/WebView transport-level cause is not runtime-proven, but the unsafe bootstrap state is concrete and sufficient for a bounded resilience fix.
- No main-feed timeout, bounded retry, or guarded `pageshow` / visible-state recovery currently exists.
- Director decision: proceed directly to `WORKER_TASK_MOBILE_PAGE_BLANK_FEED_FIX_01.md`; no more recon before implementation.
- Required fix behavior: visible loading state, bounded request timeout, one bounded retry, idempotent bootstrap state, guarded foreground recovery, explicit terminal empty/error states, concise diagnostics.
- Real-device user verification remains mandatory after deployment before closure.

## Semantic runtime completion — accepted

- Follow-up acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Closed.

## Visual freshness — accepted, release deferred

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- All acceptance controls pass and branch `worker/visual-freshness-chain-fix-01` is ready for production merge/release.
- Release intentionally deferred until urgent blank-feed incident is stabilized and overlap risk is reassessed.
- Chat 2 can be deleted.

## System Auditor checkpoint

- Last report: `reviews/system_audits/baseline-01.md`.
- `system_audit_due: true`.
- Urgent blank-feed incident explicitly pre-empts audit.
- After incident stabilization, run due System Audit before ITAD/ordinary implementation work.

## Taste Reviewer — baseline complete

- Dedicated reviewer established.
- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- ITAD permission confirmed.
- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started`, lower priority than urgent blank-feed incident and due audit.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Continue existing Chat 1 with `WORKER_TASK_MOBILE_PAGE_BLANK_FEED_FIX_01.md` immediately.
2. Do not release the accepted visual-freshness branch during the blank-feed fix unless Director later confirms no overlap risk.
3. After implementation, deploy the blank-feed fix through the canonical Pages path and require real-device user verification.
4. Once incident is stable, run due System Audit before ITAD/ordinary backlog implementation.