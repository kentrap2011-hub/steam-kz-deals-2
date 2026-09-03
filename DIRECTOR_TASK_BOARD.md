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
7. Если GitHub не может получить внешний/semantic факт сам, scheduled ChatGPT получает только GitHub-prepared exact scope и возвращает результат через canonical interface; interactive worker не создаёт собственную production-очередь.
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

## Активно / closeout

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Taste-контроль | Final acceptance passed; no further continuation | `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_ACCEPTANCE_02.md` | `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md` | `complete_chat_can_delete` |
| `ЧАТ 2` | Финальная приёмка свежести | Verify completed freshness receipt + exact deploy binding implementation before production merge/release | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md` | `reviews/worker_reports/visual-freshness-chain-acceptance-02.md` | `ready_to_continue_in_existing_chat` |

## Semantic runtime completion — accepted

- Follow-up acceptance report: `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`, blob `5b4a25c89845ab258651a30608658e90d7d1840d`.
- Runtime observability: pass.
- Feed semantic completeness visibility: pass.
- No duplicate scheduler/runtime/queue.
- Director decision: close. Chat 1 can be deleted.

## Visual freshness — implementation complete, acceptance due

- Implementation report: `reviews/worker_reports/visual-freshness-chain-fix-01.md`, blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`.
- Status: `complete`.
- Implementation branch: `worker/visual-freshness-chain-fix-01`.
- Added durable `visual-freshness-receipt-v1` to ordinary build outcomes and exact deploy verification against the triggering build run.
- Focused bounded tests pass for fresh, degraded/no-build and stale-mismatch cases.
- No production deployment was performed by the implementation task.
- Director decision: run `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md` in the same Chat 2 before merge/release decision.

## System Auditor checkpoint

- Last report: `reviews/system_audits/baseline-01.md`.
- `system_audit_due: true` after accepted semantic-runtime control/stabilized incident.
- Existing direct Chat 2 freshness continuation may finish first.
- After that direct continuation is stable, run the due System Audit before ordinary implementation work unless the user explicitly prioritizes a more urgent time-sensitive task.

## Taste Reviewer — baseline complete

- Dedicated reviewer is now established.
- Report: `reviews/taste_reviews/baseline-01.md`, blob `f243047d9bbb3d8515e7929e2962da66688243c4`.
- `taste_baseline_review_due: false`.
- Overall selection pressure: `cannot_determine`; do not globally loosen or tighten Taste from this baseline.
- Strongest evidence: model needs more contextual calibration of role/priority and risk meaning, not a simple threshold change.
- Durable controls include Trine 4 family positive, HighFleet negative start-priority control, Tails of Iron 2 secondary role, High On Life moderate main-game candidate, Sifu strong interest, Batman replay-positive, RDR2 open-world positive.
- Reviewer recommendations remain advisory; no Taste/ranking implementation is auto-assigned from this report.
- Keep this chat as the dedicated Taste Reviewer if convenient; it does not consume an implementation worker slot.

## Giveaway identity — ITAD permission confirmed, provider switch prepared

- ITAD permission reply: `Hi, this is permitted. For details about authentication refer to docs.`
- Classification: `permission_confirmed`.
- Prepared task updated: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Architecture decision: one provider-neutral giveaway identity interface with one canonical active-provider setting equivalent to `giveaway_identity_provider = "itad"`.
- `itad` is active now; `igdb` is reserved for later acceptance/implementation.
- No automatic fallback, dual lookup or provider voting.
- Selecting unavailable `igdb` before its adapter is accepted must fail closed explicitly.
- Downstream Steam family / description / Taste / grounded-negative attachment consumes only the common resolved Steam identity, not provider-specific ITAD/IGDB branches.
- ITAD exact-ID adapter is the only provider implementation in the current task.
- Twitch/IGDB remains potential later replacement through the same interface if Twitch is unblocked.
- Status: `prepared_not_started` because System Audit is currently due and Chat 2 direct freshness continuation is still open.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB: waiting for Twitch Support; potential later provider adapter/switch target.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Continue existing Chat 2 with `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_02.md`.
2. After Chat 2 reaches a stable merge/release decision, run the now-due System Audit.
3. After audit decision, start the prepared switchable-provider ITAD implementation unless a more urgent user priority supersedes it.
4. Do not turn Taste Reviewer baseline recommendations into production ranking/Taste changes without a separate Director decision and required Taste-review checkpoint.