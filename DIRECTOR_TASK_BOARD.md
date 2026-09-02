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
| `ЧАТ 1` | Точный запуск проверки Trine 4 | Find the exact existing scheduled Taste runtime, its enabled state, exact cadence, supported manual trigger if any, and completion observation for `App_690640` | `WORKER_TASK_TASTE_RUNTIME_EXACT_TRIGGER_RECON_01.md` | `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Разрешение ITAD API | Prepare the exact IsThereAnyDeal permission request and classify the provider reply before any implementation | `WORKER_TASK_ITAD_TERMS_PERMISSION_PREP_01.md` | `reviews/worker_reports/itad-terms-permission-prep-01.md` | `ready_to_continue_in_existing_chat` |

## Отдельный advisory chat — Taste Reviewer

- Role: `TASTE_REVIEWER_ROLE.md`.
- Durable profile: `USER_TASTE_PROFILE.md`.
- Baseline task: `TASTE_REVIEW_BASELINE_01.md`.
- First report: `reviews/taste_reviews/baseline-01.md`.
- Status: `ready_for_new_advisory_chat`.
- Purpose: understand Dmitry's game taste deeply and independently challenge whether current filtering/ranking is too restrictive or mis-prioritized.
- This reviewer must not modify production code/weights. It may maintain only its profile/review artifacts and advise the Director.

## Mandatory System Auditor checkpoint

- Role: `SYSTEM_AUDITOR_ROLE.md`.
- Durable trigger state: `DIRECTOR_REVIEW_CHECKPOINTS.md`.
- First audit is now marked due. Existing direct continuations in Chat 1 / Chat 2 may finish first, but before assigning the next ordinary backlog implementation the audit must run unless the user explicitly prioritizes a more urgent time-sensitive task.

## Trine 4 state

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Trine 4 reaches the existing Taste queue and is blocked only because its Taste result is unresolved.
- `taste-runtime-trigger-status-01` confirmed queue presence but did NOT verify that processing is currently active, exact cadence, or a supported manual trigger.
- Director decision: continue only with exact-runtime/control recon in Chat 1.

## Giveaway identity state

- Accepted giveaway UI remains unchanged.
- Twitch/IGDB remains fallback because Twitch 2FA activation is blocked for the user's account and Support is pending.
- `giveaway-identity-provider-alternatives-01` completed and selected IsThereAnyDeal (ITAD) as the strongest non-Twitch technical route.
- Bounded current Epic proof: 2/2 active offers map from the exact Epic offer ID -> ITAD game UUID -> one exact Steam appid without title matching.
- Wikidata is the non-Twitch fallback but covered only 1/2 current sample games.
- ITAD implementation is blocked only on Terms clarification: their docs state private API use should contact them, and the project must not assume permission.
- Director decision: prepare one concise permission request to `api@isthereanydeal.com`; do not implement before affirmative/conditional permission.
- If ITAD permits use, next bounded IMPLEMENT reuses exact Epic/GOG IDs -> ITAD -> unique Steam appid -> existing canonical description/Taste path. No title/fuzzy fallback, no price ingestion, no new scheduler/runtime/browser fetch.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB credentials path: blocked on Twitch account 2FA activation/support; fallback only.
- ITAD production integration: blocked until Terms/API-use permission is confirmed.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work; no worker-owned manual processing.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime.

## Принятый UI раздач

- Giveaway navigation UX accepted by user on real device. Only analysis content/identity remains open.

## Выбор следующей работы

Continue current direct continuations in both existing chats. Do not assign ordinary backlog implementation until the mandatory System Auditor checkpoint is handled.