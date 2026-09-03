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
| `ЧАТ 1` | Релиз свежести | Release already accepted visual freshness controls onto production main | `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md` | `reviews/worker_reports/visual-freshness-release-01.md` | `ready_to_start_new_chat` |
| `ЧАТ 2` | Epic раздачи | Recon worker says finished, but canonical report is missing; save exact closeout before any new work | `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md` | `reviews/worker_reports/epic-giveaway-schema-recon-01.md` | `needs_report_closeout_existing_chat` |

## Mobile feed incident — systemically closed except deploy regression gate follow-up

- Final production release: `f745dac844213880cd7eb984573877f58803a3f0`; Pages run `33779042331` success.
- Affected Android user acceptance: works.
- Post-incident audit: `reviews/system_audits/mobile-post-incident-audit-01.md`, blob `db07eb4f7848d18e3a8cc62d5cb754e245695db4`, status complete.
- Audit proves canonical `data/current.json` ownership is preserved; Cache Storage is one bounded last-known-good presentation fallback; no second renderer, service worker, polling loop, scheduler or unbounded local data plane was added.
- Remaining proven medium gap: `tests/feed-bootstrap.test.js` is not yet in the canonical Pages deploy regression gate.
- Prepared bounded follow-up: `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`, creation commit `ad279b127ee87d8b1f15313f4d62a565c376b040`.
- This follow-up must not redesign the client; it only wires the existing passing test into the canonical deploy gate.
- System Audit checkpoint is satisfied and reset; no immediate audit is due.

## Visual freshness — release is now top direct continuation

- Accepted implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Final acceptance: `reviews/worker_reports/visual-freshness-chain-acceptance-02.md`, blob `6a691fb29d88b1785accf717752149e027265a2c`.
- Accepted branch: `worker/visual-freshness-chain-fix-01`.
- Mobile post-incident audit explicitly sets `Visual freshness release priority: now`.
- Prepared production task: `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md`, creation commit `629918c320d6c5d4dce617a9aba33f4e8b37b669`.
- Release task must land only the already accepted freshness receipt/deploy-binding mechanism and prove one production cycle; no mobile regression-gate, Epic, ITAD or Taste work may be mixed in.

## Epic giveaway source failure — report closeout required

- Canonical current failure remains: Epic source `SOURCE_SCHEMA_FAILURE`, `Epic price.totalPrice schema changed`; snapshot incomplete.
- Recon task: `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_RECON_01.md`.
- User reports Chat 2 finished, but exact expected report `reviews/worker_reports/epic-giveaway-schema-recon-01.md` is absent.
- One exact-path fetch returned 404 and one bounded task-ID repository search returned no report.
- Director must not investigate the schema itself. Return existing Chat 2 only for report closeout at the exact path; then read that report and decide IMPLEMENT vs blocked.
- Do not delete/reuse Chat 2 until report is saved and Director reads it.

## Operational health watch

- ChatGPT automation `Steam KZ Health Watch` is enabled hourly.
- It alerts only on new/materially worsened canonical problems not already tracked here.

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

1. Finished mobile post-audit chat can be deleted.
2. Start NEW Chat 1 with `WORKER_TASK_VISUAL_FRESHNESS_RELEASE_01.md`.
3. Return SPECIFIC EXISTING Chat 2 only to save `reviews/worker_reports/epic-giveaway-schema-recon-01.md`; do not give it new work yet.
4. After Chat 2 report appears, read it exactly and if IMPLEMENT-ready continue Epic repair before ITAD.
5. After visual freshness release completes, run prepared `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md` at the next safe slot unless a more urgent concrete production defect intervenes.
6. Later address semantic degraded-state UI visibility and legacy Taste writer cleanup as bounded tasks.