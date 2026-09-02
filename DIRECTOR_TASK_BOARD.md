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
| `ЧАТ 1` | Запуск проверки Trine 4 | Determine whether the existing automatic Taste processing is currently running, whether it can be safely started now, and how completion for `App_690640` is detected | `WORKER_TASK_TASTE_RUNTIME_TRIGGER_STATUS_01.md` | `reviews/worker_reports/taste-runtime-trigger-status-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Альтернатива Twitch/IGDB | Find the safest non-Twitch primary exact identity route Epic/GOG -> authoritative game identity -> exact Steam appid, keeping IGDB only as fallback | `WORKER_TASK_GIVEAWAY_IDENTITY_PROVIDER_ALTERNATIVES_01.md` | `reviews/worker_reports/giveaway-identity-provider-alternatives-01.md` | `ready_to_continue_in_existing_chat` |

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
- First audit becomes due as soon as BOTH current tracks reach stable boundaries:
  1. `taste-runtime-trigger-status-01` has a saved report + Director decision;
  2. giveaway identity continuation reaches a durable implementation/blocker decision.
- Before the next ordinary backlog implementation after that point, run the first System Audit unless the user explicitly prioritizes a more urgent time-sensitive incident.

## Trine 4 diagnosis result

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Trine 4 is present through store snapshot, shortlist, purchase/deal context and Taste queue.
- First disappearance is missing completed Taste analysis before visual preparation; price/ranking/region are not the cause.
- Next bounded step is to establish whether normal processing is running, manually startable, and how its completion is observed.

## Giveaway identity state

- Accepted giveaway UI remains unchanged.
- Exact identity recon found no safe current Epic/GOG -> Steam semantic binding.
- IGDB was prepared as the clean exact bridge, but Twitch developer application creation is blocked before credentials because Twitch requires 2FA and initial 2FA phone registration fails for the user's Russian +7 number.
- Twitch Support request has been submitted.
- Report: `reviews/worker_reports/chat2-twitch-blocker-status-01.md`, blob `3aa927ad15917c9a2e2b1568e9b25261a16c5355`.
- Director decision: do not wait on Twitch as the primary plan. Keep Twitch/IGDB as fallback while support is pending and recon a non-Twitch exact identity provider/route.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Twitch/IGDB credentials path: blocked on Twitch account 2FA activation/support; fallback only for now.
- `grounded-negative-implement-01`: existing GitHub-owned Taste data-plane has unresolved work; no worker-owned manual processing.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime.

## Принятый UI раздач

- Giveaway navigation UX accepted by user on real device. Only analysis content/identity remains open.

## Выбор следующей работы

Continue in existing Chat 2 with `WORKER_TASK_GIVEAWAY_IDENTITY_PROVIDER_ALTERNATIVES_01.md`. Do not repeat Twitch troubleshooting. Read whichever active report arrives first; when an implementation slot becomes free for ordinary backlog work, check `DIRECTOR_REVIEW_CHECKPOINTS.md` first.