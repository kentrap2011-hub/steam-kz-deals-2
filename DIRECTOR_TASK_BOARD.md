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
17. User decision 2026-09-01: when translation is required after ready-Russian sources are exhausted, prefer ChatGPT semantic translation over generic machine-translation APIs because description quality is more important than replacing ChatGPT with a lower-quality translator. Do not pursue DeepL/Google/Yandex/Azure unless this decision is later changed.

## Активно / подготовлено сейчас

| Чат | Короткое имя | Задача | Task file | Report | Статус |
|---|---|---|---|---|---|
| `ЧАТ 1` | Русские описания | Canonical GitHub-owned translation contract with constrained scheduled ChatGPT fallback | `WORKER_TASK_RU_TRANSLATION_CONTRACT_01.md` | `reviews/worker_reports/ru-translation-contract-01.md` | `prepared_for_new_chat` |
| `ЧАТ 2` | Длительность | IGDB duration contract complete; implementation waits on credentials/licensing/attribution provisioning | `WORKER_TASK_DURATION_CONTRACT_01.md` | `reviews/worker_reports/duration-contract-01.md` | `awaiting_user_provisioning` |

## Worker chat lifecycle

- Old `ЧАТ 1 — Русские описания` reached maximum context after completing `ru-description-source-recon-01`. Report is saved and director decision made. **Old chat may be deleted.** Slot `ЧАТ 1` is reused by a fresh translation-contract chat.
- Existing `ЧАТ 2 — Длительность` completed the contract task. No further worker action should be assigned until IGDB provisioning prerequisites are clarified. Its report is durable, so the chat may be deleted; later implementation can start in a fresh `ЧАТ 2`.

## Отложено / superseded

- `WORKER_TASK_RU_TRANSLATION_PROVIDER_RECON_01.md` — **cancelled/superseded by user decision**. Do not compare generic translation APIs unless user explicitly reopens that option.
- Wikimedia ready-Russian secondary source — technically feasible but not approved as a production dependency because coverage is incomplete and reused Wikipedia text requires CC BY-SA attribution/share-alike handling. It may be reconsidered separately, but translation architecture does not depend on it.

## Последние завершённые worker-этапы

- `ru-description-source-recon-01` — `complete`; Steam RU remains primary. No broad second ready-Russian source was found. Wikimedia is a conditional subset only; translation remains necessary for some unresolved descriptions.
- `duration-contract-01` — `complete`; canonical `DURATION-ENRICHMENT-V1` chooses IGDB `game_time_to_beats`, GitHub-direct executor, structured cache/freshness/error semantics, unchanged `unknown = 2/3`. Production remains `provisioning_required` until credentials/licensing/connectivity gates are satisfied.
- `ru-description-implement-01` — deterministic producer/source-quality gate implemented. Legacy full payload has 132/442 invalid descriptions; manual translation was not performed.
- `duration-provider-recon-01` — `complete`; IGDB primary recommendation.
- `duration-source-recon-01` — `complete`; no previous structured duration source/cache/runtime path.
- `duration-data-diagnosis-01` — root cause proven: duration previously depended on text extraction.
- `ru-description-audit-01` — `complete`; 15/30 sample needed real fix.
- `detailed-score-user-fixes-01` — `complete`; phone check passed.
- `compact-purchase-options-01` — `complete`; phone check passed.
- `taste-ingest-blocker-fix-01` — `complete`.

## Ближайшие задачи

1. `ЧАТ 1`: canonical translation contract: GitHub prepares exact unresolved source-text work; scheduled ChatGPT translates only those immutable records; GitHub validates, persists and rebuilds. No manual catalog translation.
2. `ЧАТ 2`: after user clarifies project commercial status and IGDB credentials can be provisioned, bounded IMPLEMENT for GitHub-direct IGDB collection/cache/final-builder integration.
3. After both data-quality paths are implemented and rebuilt — user spot-check of visible cards.
4. Ranking/card explanation quality audit — bounded recon top-30.
5. Russian language availability as ranking factor — recon before implementation.
6. YouTube reviews — later.

## Предпочтительный продуктовый порядок

1. Способ покупки — завершено.
2. Детальная оценка — завершено.
3. Русские описания — Steam RU primary; ChatGPT translation fallback chosen for unresolved descriptions; canonical contract next.
4. Duration coverage — contract done; awaiting IGDB provisioning then implementation.
5. Качество причин `почему подходит / почему может не подойти`.
6. Информация о русском языке и её влияние на ranking.
7. Вторичные функции вроде YouTube — позже.