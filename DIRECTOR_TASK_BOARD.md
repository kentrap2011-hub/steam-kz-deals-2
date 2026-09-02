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
| `ЧАТ 1` | Точный запуск проверки Trine 4 | Exact runtime/cadence/manual-trigger recon reportedly finished by worker; user has requested report closeout | `WORKER_TASK_TASTE_RUNTIME_EXACT_TRIGGER_RECON_01.md` | `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md` | `awaiting_report_closeout` |
| `ЧАТ 2` | Разрешение ITAD API | Permission request prepared and sent by user; integration now waits only for provider reply | `WORKER_TASK_ITAD_TERMS_PERMISSION_PREP_01.md` | `reviews/worker_reports/itad-terms-permission-prep-01.md` | `external_wait_no_worker_slot` |

## System Auditor — due now

- Role: `SYSTEM_AUDITOR_ROLE.md`.
- Task: `SYSTEM_AUDIT_BASELINE_01.md`.
- Expected report: `reviews/system_audits/baseline-01.md`.
- Status: `ready_for_new_auditor_chat`.
- This checkpoint is mandatory before the next ordinary backlog implementation unless the user explicitly prioritizes a more urgent time-sensitive incident.

## Taste Reviewer

- Role: `TASTE_REVIEWER_ROLE.md`.
- Durable profile: `USER_TASTE_PROFILE.md`.
- Baseline task: `TASTE_REVIEW_BASELINE_01.md`.
- First report: `reviews/taste_reviews/baseline-01.md`.
- Advisory only; no production code changes.

## Trine 4 state

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Trine 4 reaches the existing Taste queue and is blocked only because its Taste result is unresolved.
- `taste-runtime-trigger-status-01` proved queue presence but not exact runtime cadence/manual trigger.
- The follow-up exact-runtime recon was reportedly completed by Chat 1; Director waits only for its durable report before deciding next action.

## Giveaway identity state

- Twitch/IGDB remains fallback because Twitch 2FA activation is blocked and Support is pending.
- IsThereAnyDeal is the strongest non-Twitch technical route found; bounded current Epic proof succeeded 2/2 using exact Epic offer IDs -> ITAD -> exact Steam appids without title matching.
- `itad-terms-permission-prep-01` prepared the permission request to `api@isthereanydeal.com` and the user reports it has now been sent on 2026-09-02.
- Status is external wait, not an active worker task. Chat 2 does not need to remain occupied while waiting.
- Follow-up SLA: if no reply by 2026-09-07, send one concise follow-up; if still no reply by 2026-09-09, stop treating ITAD as an operationally available primary route and decide on the Wikidata fallback after the mandatory System Audit. A later positive ITAD reply may still supersede the fallback.
- When ITAD replies, classify it using the saved report as `permission_confirmed`, `permission_confirmed_with_conditions`, `permission_denied`, or `needs_clarification`, then create the corresponding bounded continuation.
- No ITAD implementation until permission is explicit. If permitted, use exact Epic/GOG IDs -> ITAD -> unique Steam appid -> existing canonical description/Taste path; no title/fuzzy fallback or ITAD price ingestion.

## Ожидает внешнего prerequisite, worker-слот не занимает

- ITAD integration: permission email sent; first follow-up threshold 2026-09-07; operational fallback-decision threshold 2026-09-09.
- Twitch/IGDB: waiting for Twitch Support; fallback only.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work.
- `card-explanation-production-acceptance-01`: blocked on existing Russian-description runtime.

## Выбор следующей работы

1. Get Chat 1's missing exact-runtime report saved; do not repeat the recon.
2. Start the mandatory System Auditor in a new independent chat.
3. Do not burn a worker slot waiting for ITAD. If there is no reply by 2026-09-07, send one follow-up. If there is still no reply by 2026-09-09, use the audit findings to decide whether to proceed with bounded Wikidata fallback implementation.
4. When ITAD replies, classify the reply from the saved permission-prep report and continue accordingly.