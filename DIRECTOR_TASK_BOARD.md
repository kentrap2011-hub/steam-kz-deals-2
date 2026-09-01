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
8. UI-задачи с реальным-device judgment закрывать только после пользовательской проверки.
9. Worker-чат удалять только после сохранённого report, решения директора и всех ближайших проверок.
10. Для активных задач хранить ожидаемый report path. При фразе `один чат закончил` директор сам проверяет reports и свежие commits.
11. Если expected report не найден, но worker сообщил о завершении, дополнительно проверить свежие commits; если report всё равно отсутствует, считать результат не сохранённым.
12. Task-file не считается запущенной, пока пользователь реально не отправил команду worker-чату.
13. Живые worker-чаты имеют пользовательские слоты `ЧАТ 1`, `ЧАТ 2`.
14. Первая строка каждого копируемого сообщения worker-у содержит его метку, например `=== ЧАТ 2 — ДЛИТЕЛЬНОСТЬ ===`.
15. Та же метка повторяется во всех follow-up сообщениях этому чату.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Русские описания | Systemic producer/pipeline fix after 30-card audit | `WORKER_TASK_RU_DESCRIPTION_IMPLEMENT_01.md` | `reviews/worker_reports/ru-description-implement-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Длительность | Find canonical structured duration source/path and owner; no per-game lookup | `WORKER_TASK_DURATION_SOURCE_RECON_01.md` | `reviews/worker_reports/duration-source-recon-01.md` | `ready_to_continue_in_existing_chat` |

## Последние завершённые worker-этапы

- `duration-data-diagnosis-01` — `blocked` only because canonical structured source/path was not yet established. Root cause proven: final visual duration currently depends on text extraction from descriptions/summaries; manual per-game recount was stopped after user correction. Report `reviews/worker_reports/duration-data-diagnosis-01.md`.
- `ru-description-audit-01` — `complete`; bounded sample 30 cards: 15/30 need a real description fix; root cause systemic producer/source handling, not UI. Report commit `99785d4860ce6cce3bf90f437419553cb6fed6d5`.
- `detailed-score-user-fixes-01` — `complete`; пользовательская phone-проверка пройдена.
- `compact-purchase-options-01` — `complete`; phone-проверка пройдена.
- `taste-ingest-blocker-fix-01` — `complete`; canonical ingestion recovery closed.

## Ближайшие задачи после текущей пары

1. После `duration-source-recon-01`: если canonical source/path уже есть — bounded IMPLEMENT в GitHub-owned pipeline; если нет — сначала точный contract/user decision gap, без самодельной очереди.
2. После `ru-description-implement-01` проверить, что full-catalog processing принадлежит GitHub pipeline; если нужен semantic translation runtime, GitHub готовит точный scope для canonical scheduled ChatGPT path.
3. Ranking and card explanation quality audit — bounded recon top-30.
4. Russian language availability as ranking factor — recon before implementation.
5. YouTube reviews — позже, после стабилизации основной карточки.

## Предпочтительный продуктовый порядок

1. Способ покупки — завершено.
2. Детальная оценка — завершено.
3. Русские описания — systemic fix следующий.
4. Duration coverage — source/ownership recon, затем systemic fix.
5. Качество причин `почему подходит / почему может не подойти`.
6. Информация о русском языке и её влияние на ranking.
7. Вторичные функции вроде YouTube — позже.