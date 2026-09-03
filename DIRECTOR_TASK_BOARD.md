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
| `ЧАТ 1` | Релиз свежести | Accepted freshness fix landed on production main; full dynamic release proof blocked by incomplete upstream ChatGPT payload; report status needs canonical closeout | `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md` | `reviews/worker_reports/visual-freshness-release-01.md` | `needs_report_status_closeout_existing_chat` |
| `ЧАТ 2` | Epic раздачи | Implement proven Epic parser-ordering fix from completed recon | `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_FIX_01.md` | `reviews/worker_reports/epic-giveaway-schema-fix-01.md` | `running_or_ready_existing_chat` |

## Mobile feed incident — systemically closed except deploy regression gate follow-up

- Final production release: `f745dac844213880cd7eb984573877f58803a3f0`; Pages run `33779042331` success.
- Affected Android user acceptance: works.
- Post-incident audit: `reviews/system_audits/mobile-post-incident-audit-01.md`, blob `db07eb4f7848d18e3a8cc62d5cb754e245695db4`, status complete.
- Audit proves canonical `data/current.json` ownership is preserved; Cache Storage is one bounded last-known-good presentation fallback; no second renderer, service worker, polling loop, scheduler or unbounded local data plane was added.
- Remaining proven medium gap: `tests/feed-bootstrap.test.js` is not yet in the canonical Pages deploy regression gate.
- Prepared bounded follow-up: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`, creation commit `ad279b127ee87d8b1f15313f4d62a565c376b040`.
- This follow-up must not redesign the client; it only wires the existing passing test into the canonical deploy gate.

## Visual freshness — IMPLEMENTATION LANDED, dynamic production proof still pending

- Accepted implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance report: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- Release report: `reviews/worker_reports/visual-freshness-release-01.md`, blob `68bdf93bb9ee3a9c2782faaa1715571f38ec9c5e`.
- Release PR: `#13`.
- Accepted fix landed unchanged on `main` at `ddbf25d855f3ed7b86aca5ecbebb834e87178012`.
- Production build run `33788418064` failed upstream at `Build and refresh canonical visual payload once` with `ChatGPT production payload is not complete`.
- Freshness protection itself executed successfully: receipt tests passed, receipt creation/upload succeeded, and production truthfully emitted `fresh_build=false outcome=degraded/no_fresh_build` instead of claiming freshness.
- Receipt artifact: `visual-freshness-receipt`, artifact ID `9906332740`, source run `33788418064`.
- Resulting workflow-run deploy `33788465486` was correctly skipped because its triggering build failed.
- Exact triggering-run receipt download is installed on production `main` but could not be dynamically exercised because deploy never started.
- Current conclusion: the accepted protection is active on `main` and already proves truthful degraded/no-fresh-build behavior; the stronger successful-build -> exact-run deploy binding proof remains pending until a normal canonical build has a complete production payload.
- Do not redesign the accepted freshness fix to manufacture that proof.
- Worker report currently says `STOP`, which violates task-required exact statuses. Existing Chat 1 must only normalize closeout to `blocked` (or another allowed exact status justified by its existing evidence) without new investigation.

## Epic giveaway source failure — FIX READY/RUNNING

- Recon report: `reviews/worker_reports/epic-giveaway-schema-recon-01.md`, blob `32d487e13a916424693bd05d0d0ced41cf688bc2`.
- Proven root cause: parser requires `price.totalPrice` on every catalog element before determining current giveaway relevance; one irrelevant variant element aborts whole Epic source.
- Safe repair: determine current 100% promotion first; only current giveaway candidates must satisfy the existing strict price contract.
- Prepared implementation: `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_FIX_01.md`, creation commit `07bf7fabd0ceda3e3428da2139cc535096b0192f`.
- Existing Chat 2 is the direct continuation; do not mix ITAD/IGDB.

## Operational health watch

- ChatGPT automation `Steam KZ Health Watch` is enabled hourly.
- It alerts only on new/materially worsened canonical problems not already tracked here.

## Semantic runtime / publication completeness

- Runtime observability acceptance: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Runtime heartbeat defect is closed.
- Current visual release evidence exposed an existing upstream readiness condition: canonical visual build could not proceed because `ChatGPT production payload is not complete`.
- Do not diagnose this broadly in Director. Treat the next normal complete canonical build as the preferred opportunity to dynamically close visual freshness proof; if incompleteness persists as a production blocker, delegate a bounded exact recon rather than investigating here.
- Audit 02 also records that canonical degraded semantic completeness is not visibly surfaced to the user; that remains a later bounded UI-truth task.

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

1. Existing Chat 1: normalize `reviews/worker_reports/visual-freshness-release-01.md` to one allowed task status using existing evidence only; no new investigation/change.
2. Existing Chat 2 continues `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_FIX_01.md`.
3. After Chat 1 closeout is canonical, it can be deleted; next new Chat 1 should run `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md` unless a more urgent concrete production defect appears.
4. Re-verify exact-run visual freshness deploy binding on the next normal successful canonical visual build with complete production payload; no redesign required.
5. After Epic fix, if source becomes complete, verify user-visible giveaway result before moving to ITAD identity enrichment.
6. Later address semantic degraded-state UI visibility and legacy Taste writer cleanup as bounded tasks.