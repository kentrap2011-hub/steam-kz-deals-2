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

## Активно сейчас — после System Audit baseline-01

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Контроль Taste-автоматики и полноты | Prove operational observability of the existing scheduled semantic worker and whether the published feed exposes material unresolved semantic scope instead of silently looking complete | `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_ACCEPTANCE_01.md` | `reviews/worker_reports/semantic-runtime-completion-acceptance-01.md` | `ready_to_start_new_chat` |
| `ЧАТ 2` | Свежесть опубликованного списка | Prove that a successful daily build/deploy is bound to a fresh intended production cycle, or explicitly reports no-fresh-build/degraded state | `WORKER_TASK_VISUAL_FRESHNESS_CHAIN_ACCEPTANCE_01.md` | `reviews/worker_reports/visual-freshness-chain-acceptance-01.md` | `ready_to_start_new_chat` |

## System Auditor baseline-01 — complete

- Report: `reviews/system_audits/baseline-01.md`, blob `5d3abfd95e84205b999329aa30bc806687d8b9cf`.
- Status: `complete`.
- `DIRECTOR_REVIEW_CHECKPOINTS.md` has reset `system_audit_due: false`, recorded the report, and reset the material-change counter.
- Audit conclusion: deterministic GitHub ownership is relatively strong, but the system is not yet self-proving end to end.
- High-impact proven gaps:
  1. semantic work can be queued while scheduled semantic execution/progress remains operationally unobserved;
  2. unresolved semantic readiness can silently remove valid candidates while the published list still looks authoritative;
  3. a green visual workflow/deploy can represent a no-fresh-build path and redeploy a previously committed payload.
- Medium findings:
  - cross-store giveaway identity still lacks an accepted operational primary route while ITAD permission is pending;
  - legacy dispatchable one-shot Taste write workflows may create ownership ambiguity and need a bounded inventory later.
- Director accepted the auditor's top two next tasks and created them as separate acceptance tasks. Do not expand them into redesigns.

## Previous worker closeout

- Old Trine runtime Chat 1: `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`, blob `85ad9d5cdd26d066dc1996773d4f35bd5de3b9cd`; closed. The old worker chat can be deleted.
- Old ITAD Chat 2: permission-prep report saved; user sent the email. It is now external wait and consumes no worker slot. The old worker chat can be deleted.
- System Auditor baseline chat: report is durable and no immediate continuation belongs in that same audit context. It can be deleted; future audits should normally use a fresh independent auditor chat.

## Taste Reviewer

- Role: `TASTE_REVIEWER_ROLE.md`.
- Durable profile: `USER_TASTE_PROFILE.md`.
- Baseline task: `TASTE_REVIEW_BASELINE_01.md`.
- First report: `reviews/taste_reviews/baseline-01.md`.
- Advisory only; no production code changes.

## Trine 4 state

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Trine 4 reaches the existing Taste queue and is blocked because its current Taste result is unresolved.
- Stop Trine-specific recon. The system-level cause is now handled by `semantic-runtime-completion-acceptance-01`.

## Giveaway identity state

- Twitch/IGDB remains fallback because Twitch 2FA activation is blocked and Support is pending.
- IsThereAnyDeal is the strongest non-Twitch technical route found; bounded Epic proof succeeded 2/2 using exact Epic offer IDs -> ITAD -> exact Steam appids without title matching.
- User sent ITAD permission request on 2026-09-02.
- Follow-up SLA: if no reply by 2026-09-07, send one concise follow-up; if still no reply by 2026-09-09, stop treating ITAD as an operationally available primary route and decide on bounded Wikidata fallback. A later positive ITAD reply may supersede the fallback.
- No ITAD implementation until permission is explicit.

## Audit follow-up not assigned yet

- `Taste canonical write ownership inventory`: audit Finding 5. Bounded future candidate to inventory dispatchable workflows that can write canonical Taste state and retire/constrain obsolete one-shot paths. This is durable but **not next** while the two higher-impact acceptance tasks are active.

## Ожидает внешнего prerequisite, worker-слот не занимает

- ITAD integration: permission email sent; first follow-up threshold 2026-09-07; operational fallback-decision threshold 2026-09-09.
- Twitch/IGDB: waiting for Twitch Support; fallback only.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

Start both new acceptance tasks in fresh worker chats. Read whichever report arrives first. If an acceptance fails, create a bounded IMPLEMENT continuation only after reading the report. Do not start ordinary backlog work ahead of these two audit follow-ups.