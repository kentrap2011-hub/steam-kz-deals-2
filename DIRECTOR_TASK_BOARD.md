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
| `ЧАТ 1` | Компактные раздачи | User re-verifies the newly deployed collapsed giveaway UI on phone; richer real description/pros/cons still needs a safe cross-store analysis-identity continuation | `WORKER_TASK_CROSS_PLATFORM_GIVEAWAY_UI_UX_FIX_01.md` | `reviews/worker_reports/cross-platform-giveaway-ui-ux-fix-01.md` | `needs_user_verification` |
| `НОВЫЙ ЧАТ 2` | Контракт подтверждённых минусов | Continue from completed negative-gap diagnosis; define canonical completeness/unresolved/typed-evidence contract for grounded negatives | `WORKER_TASK_GROUNDED_NEGATIVE_CONTRACT_RECON_01.md` | `reviews/worker_reports/grounded-negative-contract-recon-01.md` | `ready_for_new_chat` |

## Заменённый worker-чат

- Старый `ЧАТ 2` (`card-negative-analysis-gap-01`) можно больше не открывать: report сохранён и статус `complete`. Пользователь сообщает, что открытие этого чата зависает в клиенте. Все нужные факты перенесены в GitHub task/report; новая работа должна идти в НОВОМ ЧАТЕ 2.

## Ожидает внешнего prerequisite, worker-слот не занимает

- `card-explanation-production-acceptance-01` остаётся `blocked` на существующем Russian-description runtime. После появления prerequisite: visual build -> gates -> payload commit -> Pages deploy -> user verification.

## Подготовлено, но НЕ назначено следующим

- `WORKER_TASK_TRINE4_MISSING_DIAGNOSIS_01.md` остаётся подготовленным.
- Duration connectivity остаётся blocked на user-provisioned IGDB secrets.

## Последние решения

- `cross-platform-giveaway-ui-ux-fix-01` — implementation/deploy завершены, статус `needs_user_verification`. Giveaway block теперь collapsed-by-default и компактный. Safe Epic/GOG -> Steam analysis binding не найден, поэтому worker правильно не копировал analysis по названию; expanded cards показывают честный incomplete-analysis state. Реальные description/pros/cons всё ещё остаются незакрытым пользовательским требованием и потребуют отдельного identity/analysis continuation после UI recheck.
- `card-negative-analysis-gap-01` — `complete`. Системный дефект подтверждён: в real generated top-30 28/30 карточек не имели visible grounded negative; причины включают permissive `INCLUDE + negative_evidence=[]`, misrouted negative concerns и потерю валидного free-text evidence узким lexical mapper. Final fail-closed suppression heuristics исправен и не должен ослабляться.
- Старый Chat 2 заменяется новым из-за клиентского зависания; повторная диагностика запрещена.
- Real-device acceptance остаётся обязательным для Chat 1.

## Выбор следующей работы

После report нового Chat 2 выбрать прямой IMPLEMENT/следующий контрактный шаг по его фактам. Trine 4 не продвигать перед прямым continuation, если grounded-negative contract recon потребует bounded implement.