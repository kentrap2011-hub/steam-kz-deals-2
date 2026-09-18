# WORKER TASK — TASTE DOSSIER G000001 OPEN RUSSIAN DISCOVERY CONTROL 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на kentrap2011-hub/steam-kz-deals-2 до любых действий.

Task ID: taste-dossier-g000001-open-russian-discovery-control-01
Mode: READ-ONLY / RECON

## START
Сначала открой актуальный CHAT_PROTOCOL.md из main и выполни START gate.
Затем открой этот task-файл.

## Exact targets
Ищи русскоязычный PLAYER-GENERATED feedback только по этим трем целям:
1. appid 2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC
2. appid 1000010 — Crown Trick
3. appid 1000360 — Hellish Quart

Цель этого чата — CONTROL: выяснить, что вообще реально можно найти в открытом интернете, НЕ применяя production usability filters во время поиска.

## Critical instruction: ignore production acceptance rules during discovery
Не используй действующие production-правила как причину отбрасывать найденное.

В частности, во время collection НЕ отбрасывай lead только потому что:
- это list/search/index page;
- нет stable item-level locator;
- URL profile-scoped;
- нет даты;
- locator неудобный/нестабильный;
- source type не разрешён текущим contract;
- exact appid не виден в URL;
- обсуждение находится на surface базовой игры, но текст/контекст явно касается нужного DLC/edition;
- это snippet/search result, который указывает на существующее player-generated сообщение;
- provenance нельзя сегодня сериализовать в V2;
- текущий compact privacy/provenance contract это не принимает.

Твоя задача — сначала НАЙТИ русскоязычную пользовательскую обратную связь, а не доказать её production-usability.

Но:
- не подменяй player feedback журналистскими/редакционными статьями;
- не считай перевод интерфейса доказательством player feedback;
- не выдумывай контент;
- помечай relation как exact / likely exact / adjacent / ambiguous вместо преждевременного rejection.

## Web research
Ищи максимально широко по публичному интернету и разным surface classes:
- Steam / Steam Community;
- Reddit;
- русскоязычные форумы;
- Pikabu / аналогичные UGC;
- публичные store/user-review platforms;
- публичные community discussions/comments;
- другие индексируемые player-generated surfaces.

Не зацикливайся на одном домене.

Diagnostic ceiling per game:
- до 15 search queries;
- до 40 opened/read pages.

Это control-research budget, не production policy.

## What to collect
Для каждого реально найденного lead достаточно:
- game;
- domain/surface;
- URL/locator или search-result URL;
- relation to target: exact / likely exact / adjacent / ambiguous;
- Russian/mixed;
- явно player-generated yes/no;
- кратко, о чем feedback на уровне темы (без длинных цитат и без usernames);
- есть ли конкретный item/post/review или только aggregate/list/snippet.

НЕ оценивай его по текущему V2 contract.
НЕ ставь production usable/rejected.
НЕ читай strict validator ради того, чтобы фильтровать результаты.

Можно прочитать CURRENT_TASK/PROJECT_ROUTES только для подтверждения exact target identity, но не использовать production evidence filters при collection.

## Key questions
Для каждой игры:
1. Удалось ли вообще найти русскоязычный player-generated feedback?
2. Сколько различных surface classes дали leads?
3. Есть ли concrete posts/reviews/comments, даже если они не соответствуют нашим текущим serialization rules?
4. Для BG3 DLC отдельно:
   - есть ли player feedback, который содержательно явно обсуждает Deluxe DLC, даже если находится на surface базовой BG3?
   - насколько естественно реальный интернет организует такие обсуждения: отдельный DLC appid или base-game communities?
5. Что находилось легко, но production contract мог бы потерять из-за формы URL/locator/identity/provenance?

## No production changes
Не менять:
- schema/contract/prompt/validator;
- PROJECT_DECISIONS;
- production state;
- dossier artifacts;
- Scheduled Task;
- Run now/settings.

Разрешено создать только durable report.

## Durable report
Путь:
reviews/worker_reports/taste-dossier-g000001-open-russian-discovery-control-01.md

Report:
1. Task / targets.
2. Search budget actually used.
3. Compact raw lead inventory grouped by game.
4. Surface diversity per game.
5. Exact vs likely/adjacent identity observations.
6. What Russian player feedback clearly exists in the wild regardless of current production contract.
7. Patterns that current production representation may have difficulty capturing — describe factually, do not recommend a fix yet.
8. Unresolved.
9. Status: complete / blocked.
10. Exactly one recommended next step: Director compares with strict diagnostic report.
11. Efficiency / reusable lesson.

Commit report to main before declaring complete.

CURRENT_TASK.md не менять.
