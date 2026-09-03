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

## Активно сейчас — IMPLEMENT после audit acceptance

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Исправление Taste-наблюдаемости | Add durable progress/heartbeat evidence for the existing canonical Taste runtime and a truthful semantic incomplete/degraded publication state | `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_FIX_01.md` | `reviews/worker_reports/semantic-runtime-completion-fix-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Исправление свежести публикации | Add a durable build freshness receipt and bind Pages deploy to the exact triggering fresh build / explicit degraded no-build outcome | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_FIX_01.md` | `reviews/worker_reports/visual-freshness-chain-fix-01.md` | `ready_to_continue_in_existing_chat` |

## Acceptance results — complete, both need fixes

### Semantic runtime completion acceptance

- Report: `reviews/worker_reports/semantic-runtime-completion-acceptance-01.md`, blob `95a761898d2a34fc646fde1207bb0b1fa91f6936`.
- Status: `needs_fix`.
- `Semantic runtime observability`: `fail`.
- `Feed semantic completeness visibility`: `fail`.
- Current evidence: 644 of 743 families remain in semantic queue while partition/status can still say `complete`; queue presence is not a runtime heartbeat.
- Director decision: one bounded IMPLEMENT task only; preserve the single existing Taste scheduler/runtime and current Taste semantics.

### Visual freshness chain acceptance

- Report: `reviews/worker_reports/visual-freshness-chain-acceptance-01.md`, blob `11f4d2b416d8034646df253df616b44143aade57`.
- Status: `needs_fix`.
- `Fresh-cycle build proof`: `fail`.
- `Deploy-to-built-cycle binding`: `fail`.
- `Stale-success visibility`: `fail`.
- Current evidence: build can succeed without fresh visual; deploy checks out `main` rather than exact triggering visual; current history blob and visual-declared source-history blob do not match.
- Director decision: one bounded IMPLEMENT task only; add a durable freshness receipt and exact deploy binding without redesigning the pipeline.

## System Auditor baseline-01 — complete

- Report: `reviews/system_audits/baseline-01.md`, blob `5d3abfd95e84205b999329aa30bc806687d8b9cf`.
- Status: `complete`.
- `DIRECTOR_REVIEW_CHECKPOINTS.md`: `system_audit_due: false`, material-change counter reset to 0.
- Audit Finding 5 (legacy dispatchable Taste write paths) remains a durable future candidate, not next while the two higher-impact fixes are active.

## Taste Reviewer

- Role: `TASTE_REVIEWER_ROLE.md`.
- Durable profile: `USER_TASTE_PROFILE.md`.
- Baseline task: `TASTE_REVIEW_BASELINE_01.md`.
- First report: `reviews/taste_reviews/baseline-01.md`.
- Advisory only; no production code changes.

## Trine 4 state

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Stop Trine-specific recon. Its incident is now covered by the system-level semantic runtime completion fix.

## Giveaway identity state

- Twitch/IGDB remains fallback because Twitch 2FA activation is blocked and Support is pending.
- IsThereAnyDeal remains strongest non-Twitch route; bounded Epic proof succeeded 2/2 with exact IDs.
- User sent ITAD permission request on 2026-09-02.
- Follow-up SLA: if no reply by 2026-09-07, send one concise follow-up; if still no reply by 2026-09-09, stop treating ITAD as operationally available primary route and decide on bounded Wikidata fallback. A later positive ITAD reply may supersede the fallback.
- No ITAD implementation until permission is explicit.

## Ожидает внешнего prerequisite, worker-слот не занимает

- ITAD integration: permission email sent; first follow-up threshold 2026-09-07; fallback-decision threshold 2026-09-09.
- Twitch/IGDB: waiting for Twitch Support; fallback only.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

Continue both direct implementation fixes in the existing worker chats. After each implementation report, decide its bounded follow-up acceptance. Do not start ordinary backlog work ahead of these fixes unless the user explicitly prioritizes a more urgent time-sensitive incident.