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
16. Before introducing semantic translation, first check whether approved structured sources already provide ready Russian text. Translation is fallback, not assumed default.

## Активно сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Русские описания | Recon ready-Russian structured sources before any translation architecture | `WORKER_TASK_RU_DESCRIPTION_SOURCE_RECON_01.md` | `reviews/worker_reports/ru-description-source-recon-01.md` | `ready_to_continue_in_existing_chat` |
| `ЧАТ 2` | Длительность | Canonical IGDB duration-source/enrichment contract; GitHub-direct executor | `WORKER_TASK_DURATION_CONTRACT_01.md` | `reviews/worker_reports/duration-contract-01.md` | `ready_to_continue_in_existing_chat` |

## Отложено / superseded for now

- `WORKER_TASK_RU_TRANSLATION_CONTRACT_01.md` — **deferred**, not current. User correctly challenged the assumption that translation is needed before checking other ready-Russian sources. Revisit only if source recon proves a translation fallback is still necessary.

## Последние завершённые worker-этапы

- `ru-description-implement-01` — deterministic producer/source-quality gate implemented. Legacy full payload has 132/442 invalid descriptions; manual translation was not performed.
- `duration-provider-recon-01` — `complete`; primary recommendation IGDB `game_time_to_beats`, executor `GitHub-direct`; RAWG rejected as semantic mismatch and HLTB scraping rejected without official permission/API.
- `duration-source-recon-01` — `complete`; no existing structured duration source/cache/runtime path.
- `duration-data-diagnosis-01` — root cause proven: final visual duration currently depends on text extraction from descriptions/summaries; no manual per-game processing allowed.
- `ru-description-audit-01` — `complete`; 15/30 sample needed real fix; root cause systemic producer/source handling.
- `detailed-score-user-fixes-01` — `complete`; phone check passed.
- `compact-purchase-options-01` — `complete`; phone check passed.
- `taste-ingest-blocker-fix-01` — `complete`.

## Ближайшие задачи после текущей пары

1. После `ru-description-source-recon-01`: choose source precedence. If ready-Russian sources cover the gap adequately, implement GitHub-direct source enrichment. Only if gaps remain should a bounded translation contract be reconsidered.
2. После `duration-contract-01`: bounded IMPLEMENT for GitHub-direct IGDB collection/cache/final-builder integration, gated on credentials/licensing/attribution/connectivity provisioning.
3. После реализации и production rebuild двух data-quality paths — пользовательская выборочная проверка карточек.
4. Ranking/card explanation quality audit — bounded recon top-30.
5. Russian language availability as ranking factor — recon before implementation.
6. YouTube reviews — later.

## Предпочтительный продуктовый порядок

1. Способ покупки — завершено.
2. Детальная оценка — завершено.
3. Русские описания — deterministic gate готов; source recon before translation.
4. Duration coverage — IGDB выбран; canonical contract следующий.
5. Качество причин `почему подходит / почему может не подойти`.
6. Информация о русском языке и её влияние на ranking.
7. Вторичные функции вроде YouTube — позже.