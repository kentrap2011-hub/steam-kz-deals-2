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
| `ЧАТ 1` | Срочно: ускорить ленту | Render last-known-good feed immediately on repeat visits and refresh canonical payload in background | `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md` | `reviews/worker_reports/mobile-feed-instant-cache-fix-01.md` | `running_or_ready_in_existing_chat` |
| `ЧАТ 2` | Epic раздачи | Diagnose current Epic giveaway schema change before a bounded parser fix | `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md` | `reviews/worker_reports/epic-giveaway-schema-recon-01.md` | `ready_to_start_new_chat` |

## System Audit 02 — complete

- Report: `reviews/system_audits/system-audit-02.md`.
- Status: `complete`.
- Current due checkpoint is satisfied; `DIRECTOR_REVIEW_CHECKPOINTS.md` reset to `system_audit_due: false`, material count 0.
- Because the mobile incident was still active during the audit, `mobile_post_incident_audit_pending: true`; set the audit due again only after that incident is actually stabilized/user-accepted.
- Baseline Finding 1 semantic heartbeat: closed.
- Baseline Finding 2 semantic incompleteness visibility: partially closed; canonical payload truth is degraded/incomplete but current UI does not visibly surface it.
- Baseline Finding 3 visual stale-success: partially closed; accepted fix is release-ready but not active on production `main`.
- Legacy one-shot Taste write workflows remain a bounded ownership risk hypothesis.
- Audit independently confirms that green Pages deployment does not prove prompt usable mobile feed availability; Chat 1 remains the direct incident owner.

## Urgent user-visible incident — mobile feed load latency

- Recon report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`, blob `48700dc77ac17fa031dd129996bef74075d86872`.
- First fix report: `reviews/worker_reports/mobile-page-blank-feed-fix-01.md`, blob `61b23ffc479dff473310b1d7aed0d36d43a11c8f`.
- First production fix ref: `af2c7362743b4fe3d80ea10caee7cb606acab3e5`; Pages run `33766838776` succeeded.
- Real-device result: partial success; silent blank feed is gone, but some reloads still wait several seconds on `Загружаю игры…` before cards appear.
- Direct continuation: `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`.
- Target behavior: after one successful load on a device, show last-known-good feed locally immediately, then refresh canonical `data/current.json` in background.
- Canonical network payload remains source of truth; local storage is presentation fallback only.
- Real-device verification mandatory after deploy.

## Known production problem — Epic giveaway source schema failure

- Canonical evidence: `data/production/giveaways/v1/current.json`, blob `7354f8769b21bb9dda53910871374a5011af5586`.
- Snapshot: `incomplete`.
- Steam: ok/complete, 0 accepted.
- GOG: ok/complete, 0 accepted.
- Epic: failed/incomplete, `SOURCE_SCHEMA_FAILURE`, `Epic price.totalPrice schema changed`.
- Current result therefore cannot truthfully conclude that there are no active giveaways.
- Failure occurs before ITAD/IGDB identity enrichment.
- Prepared next task: `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md`, creation commit `f4673fecaaab54ae07fe3d795322480c994e2147`.
- Mode is bounded READ-ONLY/RECON first; no parser implementation until exact new schema is localized.

## Operational health watch

- ChatGPT automation `Steam KZ Health Watch` is enabled hourly.
- It notifies only on new/materially worsened canonical problems not already tracked here.
- Current mobile and Epic incidents are known and should not trigger duplicate unchanged alerts.
- Long-term canonical project health signal remains a future bounded design task; do not create a duplicate scheduler/writer.

## Semantic runtime completion — accepted

- Final acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Runtime observability defect is closed.
- Remaining UI truth gap from Audit 02: canonical degraded semantic completeness is not visibly surfaced to user.

## Visual freshness — accepted, release deferred

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- Branch `worker/visual-freshness-chain-fix-01` is ready for production merge/release.
- Audit 02 confirms production `main` still uses the old path, so production closure remains open.
- Release remains deferred until mobile feed incident is stabilized and overlap risk is reassessed.

## Taste Reviewer — baseline complete

- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started`; current Epic discovery failure is earlier in the pipeline and has priority over ITAD identity enrichment.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Existing Chat 1 continues `WORKER_TASK_MOBILE_FEED_INSTANT_CACHE_FIX_01.md`.
2. Replace finished audit Chat 2 with NEW Chat 2 running `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md`.
3. Read exact reports first when workers finish; no broad Director investigation.
4. After mobile incident is user-accepted, set post-incident System Audit due and reassess/release accepted visual-freshness branch.
5. After Epic recon, if IMPLEMENT-ready, fix Epic discovery before ITAD identity enrichment.
6. Later address Audit 02 semantic degraded-state UI visibility and legacy Taste writer cleanup as bounded tasks.