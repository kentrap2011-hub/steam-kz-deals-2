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

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Финальная приёмка Taste-контроля | Verify the completed runtime heartbeat/progress and truthful semantic degraded-state implementation | `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_ACCEPTANCE_02.md` | `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Исправление свежести публикации | Worker reports implementation finished, but durable report is still missing | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_FIX_01.md` | `reviews/worker_reports/visual-freshness-chain-fix-01.md` | `awaiting_report_closeout` |

## Semantic runtime completion fix

- Implementation report: `reviews/worker_reports/semantic-runtime-completion-fix-01.md`, blob `b414aa0d41929a8e125833b79caee74a9f022049`.
- Status: `complete`.
- Durable canonical runtime receipt added at `data/cache/taste_ingest_receipts/latest_runtime_status.json` through the existing transactional Taste ingest path.
- Canonical pre-AI/visual publication now distinguishes partition completion from semantic completeness and reports `degraded` while unresolved semantic work remains.
- Current receipt truthfully shows accepted progress belongs to an older semantic scope and therefore does not claim current-scope progress.
- No second scheduler/runtime/queue was created and execution ownership contract remained unchanged.
- Final implementation validation run: `33712250775`, success.
- Director decision: run bounded follow-up acceptance `semantic-runtime-completion-acceptance-02` before closing this incident/chat.

## Visual freshness fix

- Acceptance requiring fix remains: `reviews/worker_reports/visual-freshness-chain-acceptance-01.md`, blob `11f4d2b416d8034646df253df616b44143aade57`.
- User reports Chat 2 completed `visual-freshness-chain-fix-01`, but expected durable implementation report is not yet present.
- Director decision: do not re-run implementation or investigate broadly. Obtain report closeout only, then decide bounded follow-up acceptance.

## System Auditor baseline-01

- Report: `reviews/system_audits/baseline-01.md`, blob `5d3abfd95e84205b999329aa30bc806687d8b9cf`.
- Status: `complete`.
- `DIRECTOR_REVIEW_CHECKPOINTS.md`: `system_audit_due: false`.
- `material_changes_since_last_system_audit: 1` after completed `semantic-runtime-completion-fix-01`.
- Audit Finding 5 (legacy dispatchable Taste write paths) remains a future candidate, not next.

## Taste Reviewer

- Role: `TASTE_REVIEWER_ROLE.md`.
- Durable profile: `USER_TASTE_PROFILE.md`.
- Baseline task: `TASTE_REVIEW_BASELINE_01.md`.
- First report: `reviews/taste_reviews/baseline-01.md`.
- Advisory only; no production code changes.

## Trine 4 state

- Canonical identity: `App_690640`, family `game:690640`.
- Stop Trine-specific recon. Its system-level observability/completeness defect is now implemented and awaiting acceptance-02.

## Giveaway identity state

- Twitch/IGDB remains fallback because Twitch 2FA activation is blocked and Support is pending.
- IsThereAnyDeal remains strongest non-Twitch route; permission request sent 2026-09-02.
- Follow-up SLA: no reply by 2026-09-07 -> one concise follow-up; still no reply by 2026-09-09 -> decide bounded Wikidata fallback.
- No ITAD implementation until permission is explicit.

## Ожидает внешнего prerequisite, worker-слот не занимает

- ITAD integration: permission email sent; first follow-up threshold 2026-09-07; fallback-decision threshold 2026-09-09.
- Twitch/IGDB: waiting for Twitch Support; fallback only.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Continue Chat 1 with `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_ACCEPTANCE_02.md`.
2. Get Chat 2's already-completed implementation saved to `reviews/worker_reports/visual-freshness-chain-fix-01.md`; do not repeat implementation.
3. After Chat 2 report, decide its bounded acceptance continuation.
4. Do not start ordinary backlog work ahead of these direct continuations unless the user explicitly prioritizes a more urgent time-sensitive incident.