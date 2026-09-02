# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины. Эта board хранит только директорские метаданные: worker-slot, задача, report path, статус, приоритет и пользовательские проверки.

## Правила работы

1. Одновременно по умолчанию работают не больше двух worker-чатов.
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
12. Живые worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
13. Before semantic translation, first check approved ready-Russian sources. Translation is fallback, not default.
14. Current project commercial status: personal/non-commercial; commercial use requires `COMMERCIALIZATION_GUARD.md` review.
15. Task-memory invariant: future user work must have a durable destination; backlog removal requires destination/completion/cancellation evidence.
16. Worker efficiency is important, but prepared work is not automatically next.
17. **Priority discipline:** `prepared` does not mean `next`. When a worker finishes, first read its report, then choose direct continuation vs explicit user priority vs dependencies vs backlog.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Запуск проверки Trine 4 | Determine whether the existing automatic Taste processing is currently running, whether it can be safely started now, and how completion for `App_690640` is detected | `WORKER_TASK_TASTE_RUNTIME_TRIGGER_STATUS_01.md` | `reviews/worker_reports/taste-runtime-trigger-status-01.md` | `ready_to_continue_in_existing_chat` |

## Trine 4 diagnosis result

- Canonical identity: `App_690640`, family `game:690640`.
- Live sale captured: KZ available, `1,520 KZT` from `7,600 KZT`, `-80%`, observed `2026-09-02T06:42:05.485251Z`, sale end `2026-09-15T17:00:00Z`.
- Trine 4 is present through store snapshot, shortlist, purchase/deal context and Taste queue.
- First disappearance is missing completed Taste analysis before visual preparation; price/ranking/region are not the cause.
- User correctly asked not to wait blindly. Next bounded step is to establish whether normal processing is running, manually startable, and how its completion is observed.

## Giveaway analysis identity recon — complete, blocked on prerequisite

- Report saved: `reviews/worker_reports/giveaway-analysis-identity-recon-01.md`, blob `faa254b9abd2bdd18e615f4f7ad5d0f0d6d6165d`.
- UI/navigation is already accepted; no further UI redesign is needed.
- Current giveaway data has exact Epic provider product/offer IDs but no authoritative cross-store semantic-analysis identity.
- Existing `canonical_game_key` is title/publisher-derived and must NOT authorize Steam/Taste reuse.
- Smallest safe route is exact provider identity -> IGDB External Game -> IGDB game id -> exact Steam appid -> existing canonical description/Taste path.
- Current bounded sample: 0/2 active Epic giveaways have a safe existing binding; both remain fail-closed.
- Blocker is the already-known IGDB provisioning prerequisite, not a new architecture gap.

## Ожидает внешнего prerequisite, worker-слот не занимает

- Giveaway analysis identity: requires GitHub Actions secrets `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`. After provisioning, bounded IMPLEMENT should reuse the existing IGDB provider route; no title/fuzzy fallback, manual mapping, new queue, second semantic runtime, or browser fetch.
- `duration-igdb-implement-01` is blocked on the same two IGDB secrets.
- `grounded-negative-implement-01`: same existing GitHub-owned Taste data-plane has unresolved work; no worker-owned manual processing.
- `card-explanation-production-acceptance-01` remains blocked on the existing Russian-description runtime.

## Принятый UI раздач

- Giveaway navigation UX accepted by user on real device. Only analysis content/identity remains open.

## Выбор следующей работы

Read `taste-runtime-trigger-status-01` before deciding whether to trigger existing processing now or wait. Giveaway analysis implementation should start only after the two existing IGDB GitHub Actions secrets are provisioned.