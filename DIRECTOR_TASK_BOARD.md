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
| `ЧАТ 1` | Срочно: ускорить ленту | Render last-known-good feed immediately on repeat visits and refresh canonical payload in background | `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md` | `reviews/worker_reports/mobile-feed-instant-cache-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | System Audit 02 | Independent bounded end-to-end audit of post-baseline semantic/freshness controls and remaining blind spots | `WORKER_TASK_SYSTEM_AUDIT_02.md` | `reviews/system_audits/system-audit-02.md` | `ready_to_start_new_chat` |

## Urgent user-visible incident — mobile feed load latency

- Original symptom: shell/controls interactive but feed blank after load/reload; app-switch/return could make games appear.
- Recon report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`, blob `48700dc77ac17fa031dd129996bef74075d86872`.
- First fix report: `reviews/worker_reports/mobile-page-blank-feed-fix-01.md`, blob `61b23ffc479dff473310b1d7aed0d36d43a11c8f`.
- First production fix ref: `af2c7362743b4fe3d80ea10caee7cb606acab3e5`; Pages run `33766838776` succeeded.
- First fix added visible `Загружаю игры…`, 9-second timeout, max 2 attempts, guarded lifecycle recovery and explicit error state.
- Real-device result: partial success. Silent blank feed is gone, but some reloads still wait several seconds on `Загружаю игры…` before cards appear.
- Direct continuation: `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`.
- Target behavior: after one successful load on a device, show one last-known-good feed payload locally immediately on future open/reload, then refresh canonical `data/current.json` in background; slow/failed network must not block or blank already available cards.
- Canonical network payload remains source of truth; local browser storage is presentation fallback only.
- No service worker, polling, second renderer, ranking/Taste changes, or visual-freshness merge inside this follow-up.
- Real-device verification mandatory after deployment before incident closure.

## System Audit 02 — ready in parallel

- Task: `WORKER_TASK_SYSTEM_AUDIT_02.md`, creation commit `911c6d6d39d80d3e3b91ee93d06c5545a77a5688`.
- Report: `reviews/system_audits/system-audit-02.md`.
- Mode: `READ-ONLY / AUDIT` under `SYSTEM_AUDITOR_ROLE.md`.
- Purpose: verify how baseline findings changed after accepted semantic-runtime and visual-freshness controls; identify up to 5 significant remaining system-level risks and recommend at most 2 bounded tasks.
- It must not interfere with active Chat 1 mobile implementation or treat that still-active incident as accepted/stable.
- Running this audit in parallel is allowed because it is read-only and uses compact accepted evidence; if the mobile incident stabilizes into a new architecture/user-visible failure class, the auditor must state whether another future audit trigger remains due.

## Semantic runtime completion — accepted

- Follow-up acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Closed.

## Visual freshness — accepted, release deferred

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- All acceptance controls pass and branch `worker/visual-freshness-chain-fix-01` is ready for production merge/release.
- Release remains deferred until mobile feed incident is stabilized and overlap risk is reassessed.
- Old visual-freshness Chat 2 can be deleted; `ЧАТ 2` slot may now be reused for System Audit 02.

## System Auditor checkpoint

- Last completed report: `reviews/system_audits/baseline-01.md`.
- `system_audit_due: true`.
- `WORKER_TASK_SYSTEM_AUDIT_02.md` is now prepared to satisfy the current due checkpoint while the mobile fix continues independently.
- Do not reset the checkpoint until the audit report is complete and Director accepts it.

## Taste Reviewer — baseline complete

- Dedicated reviewer established.
- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- ITAD permission confirmed.
- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started`; do not start while the current mobile incident and System Audit 02 occupy the two active tracks unless user explicitly reprioritizes.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Existing Chat 1: run `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`.
2. New Chat 2: run `WORKER_TASK_SYSTEM_AUDIT_02.md` independently/read-only.
3. Read each exact report when its worker finishes; do not broad-investigate.
4. Mobile track still requires production deploy + real-device user verification before closure.
5. After System Audit 02 completes, update `DIRECTOR_REVIEW_CHECKPOINTS.md` only if accepted; then decide visual-freshness release vs ITAD based on audit findings and mobile incident state.