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
| `ЧАТ 1` | Пост-инцидентный аудит | Short read-only audit after user-accepted mobile incident stabilization | `WORKER_TASK_MOBILE_POST_INCIDENT_AUDIT_01.md` | `reviews/system_audits/mobile-post-incident-audit-01.md` | `ready_to_start_new_chat` |
| `ЧАТ 2` | Epic раздачи | Diagnose current Epic giveaway schema change before a bounded parser fix | `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md` | `reviews/worker_reports/epic-giveaway-schema-recon-01.md` | `running_or_ready` |

## Mobile feed incident — CLOSED by real-device acceptance

- Recon report: `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`, blob `48700dc77ac17fa031dd129996bef74075d86872`.
- First fix report: `reviews/worker_reports/mobile-page-blank-feed-fix-01.md`, blob `61b23ffc479dff473310b1d7aed0d36d43a11c8f`.
- Cache-first follow-up report: `reviews/worker_reports/mobile-feed-instant-cache-fix-01.md`, blob `8c80b9da35057ff6443665468329db37bfc8c8b1`.
- Final production release ref: `f745dac844213880cd7eb984573877f58803a3f0`.
- Pages deploy: `33779042331`, success.
- Final behavior: last-known-good feed payload renders immediately from browser Cache Storage on repeat visits while canonical `data/current.json` refreshes in background; canonical network payload remains source of truth.
- User real-device acceptance on affected Android phone: `works` on 2026-09-03.
- Director decision: mobile user-visible incident is closed.
- Original Chat 1 worker can be deleted.
- Incident stabilization triggers mandatory short System Audit; task prepared as `WORKER_TASK_MOBILE_POST_INCIDENT_AUDIT_01.md`.

## System Audit checkpoint

- Last completed audit: `reviews/system_audits/system-audit-02.md`.
- Mobile incident stabilization now sets `system_audit_due: true` again under the recurring incident trigger.
- Prepared short audit: `WORKER_TASK_MOBILE_POST_INCIDENT_AUDIT_01.md`, creation commit `a85c5e9da19868595ce5fd72a1afd05c2a4f880e`.
- Expected report: `reviews/system_audits/mobile-post-incident-audit-01.md`.
- Do not assign ordinary backlog work before this audit completes unless the user explicitly reprioritizes.

## Known production problem — Epic giveaway source schema failure

- Canonical evidence: `data/production/giveaways/v1/current.json`, blob `7354f8769b21bb9dda53910871374a5011af5586`.
- Snapshot: `incomplete`.
- Steam: ok/complete, 0 accepted.
- GOG: ok/complete, 0 accepted.
- Epic: failed/incomplete, `SOURCE_SCHEMA_FAILURE`, `Epic price.totalPrice schema changed`.
- Current result therefore cannot truthfully conclude that there are no active giveaways.
- Failure occurs before ITAD/IGDB identity enrichment.
- Current task: `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md`.

## Operational health watch

- ChatGPT automation `Steam KZ Health Watch` is enabled hourly.
- It notifies only on new/materially worsened canonical problems not already tracked here.
- Current Epic incident is known; closed mobile incident should no longer be treated as active unless it regresses.

## Visual freshness — accepted, release deferred

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- Branch `worker/visual-freshness-chain-fix-01` is ready for production merge/release.
- Production closure remains open until released on `main`.
- After mobile post-incident audit, reassess release immediately; there is no longer an active mobile incident blocker.

## Semantic runtime completion — accepted

- Final acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Runtime observability defect is closed.
- Remaining Audit 02 gap: canonical degraded semantic completeness is not visibly surfaced to user.

## Taste Reviewer — baseline complete

- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- Advisory only; no automatic Taste/ranking changes.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- Prepared task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture: one provider-neutral identity interface, active `itad`, reserved future `igdb`, no automatic fallback.
- Status: `prepared_not_started`; Epic discovery repair remains earlier in pipeline and higher priority.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Delete old finished Chat 1 mobile implementation worker.
2. Start NEW Chat 1 with `WORKER_TASK_MOBILE_POST_INCIDENT_AUDIT_01.md`.
3. Chat 2 continues Epic giveaway schema recon.
4. After post-incident audit, if closure accepted, release the already accepted visual-freshness branch unless a concrete blocker appears.
5. After Epic recon, if IMPLEMENT-ready, fix Epic discovery before ITAD identity enrichment.
6. Later address semantic degraded-state UI visibility and legacy Taste writer cleanup as bounded tasks.