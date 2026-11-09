# НОВЫЙ ЧАТ 2 — аудит ускорения поиска Steam KZ: лишние проверки, сетевые запросы, инкрементальные скидки

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: steam-kz-discovery-incremental-filter-speed-recon-01
Assigned worker: **НОВЫЙ физический ЧАТ 2**
Mode: **READ-ONLY RECON + измерения существующего исполнения / offline microbenchmarks + план безопасного эксперимента**
Required report: `reviews/worker_reports/steam-kz-discovery-incremental-filter-speed-recon-01.md`

## Обязательный START и scope guard
Сначала **полностью** прочитай актуальный `CHAT_PROTOCOL.md` из `main`, выполни START gate; затем полностью прочитай этот task, `CHAT_CONTEXT.md`, архитектурный preflight по `config/execution_ownership_contract.json` и `config/daily_execution_contract.json`. Найди только релевантный Steam KZ search/review/DLC маршрут через `PROJECT_ROUTES.md`, проверяй неочевидные существующие решения в `PROJECT_DECISIONS.md`, и прочитай конкретный раздел `config/mailing_policy.json#paid_discovery` и его условия полноты.
**Работай только в указанном репозитории. Не открывай, не используй и не изменяй другие репозитории даже для источников вкуса/сайта.** Документацию Steam можно исследовать в открытом Интернете как внешний справочный источник, но код и данные проекта — только этот repo. Если tool выбрал другой GitHub repository, остановись и исправь target.

## Пользовательская цель и границы разрешения
Пользователь хочет проверить эффективность текущего ежедневного получения игр со скидками, получить **реальные измерения выигрыша**, найти способы уменьшить объём первоначальной выдачи и лишние проверки, сравнить альтернативы Steam API, а **после отдельного явного согласования** испытать предложенные новые правила и доказать, что предложения не потеряны, а обновление быстрее.

**СЕЙЧАС разрешён только RECON** (чтение GitHub/документации, анализ готовых логов/артефактов, безопасные offline эксперименты на доступных фиксированных данных без GitHub production). Никакого IMPLEMENT, переключения endpoint в рабочих сценариях, создания source/workflow изменений, дополнительного запуска collector/dispatch, network replay, live side-by-side, нового расписания или публикации. **Не трогай текущий ручной штатный Steam KZ workflow, который пользователь уже запустил на main; при необходимости изучай его логи только после завершения.** Утверждённая пользователем проба новых правил — отдельный future gate; разрешение на исследование не есть разрешение на такую пробу.

## A. Фактическая карта работы и базовая скорость
1. Адресно проследи фактический путь `.github/workflows/steam-test.yml` → `scripts/steam_partial_publish_runner.py` → `scripts/steam_production.py` → `scripts/steam_targeted_paid_lanes.py` и relevant caching/review/fallback/manifest; порядок source-validation, Steam Search KZ page traversal, local gates, review enrichment, eligible roots, appdetails DLC, final selection, mailing/pre-AI. Не исследуй unrelated semantic workers.
2. Для последних **2–3 уже завершённых реальных GitHub runs** (при наличии) извлеки из явных progress/timing/diagnostic логов количественные stage seconds, wall seconds, request count по Steam Search / AppReviews / StoreBrowse / appdetails, total_count, pages, parsed/eligible/selected, retry/HTTP 429/502, failure stage. Отметь source SHA, дату, incomplete/failed. Если какого-то измерения нет — `NOT_MEASURED`, не выдавай предположение за секундомер. Не считай nightly downstream временем одного Steam collector; не выдумывай производительность нового метода.
3. Отдельно выясни, сколько фактически занимают `paid_source_rejection_reason`, повторная проверка цены, скидки и типового контента на N=1000/5000/10000 уже загруженных объектов. **Если локальная среда доступна**, проведи воспроизводимые offline microbenchmarks (например, perf_counter, несколько повторов, реальные или честно synthetic fixtures, отдельно parse/CPU/network) и зафиксируй точные команды, N, количество прогонов, median/range и окружение. Если среда недоступна — `NOT_MEASURED`, предложи узкий instrument-only метод; **не утверждай заранее, что выигрыш ничтожен**. Никакой новой Steam сети для CPU-замеров.
4. Ищи доказанно повторяющиеся/ненужные сетевые fetch, expensive validation, Steam Search source_price_bound initial 3+ GET, сортировочную/страничную сверку, дубли enrichment, бесполезную пересортировку/парсинг, всё с доказательством почему безопасно убрать. Не путай cheap local O(N) и дополнительный HTTP; не рекомендуй убрать цену/тип/KZT/integrity лишь потому, что реальный leak ещё не наблюдался. Сравни экономию против рисков.

## B. Как сократить первоначальную выдачу и число последующих запросов
1. Зафиксируй **реальные параметры** текущего Steam Search: `specials=1`, `category1=998`, `maxprice=4500`, `hidef2p=1`, `cc=kz`, 100/page, `sort_by`; порог скидки >=50% сейчас client-side. Сошлись на файлы/строки. Различи Steam category (включая Sub packages) и app.type. Не заявляй, что поиск нарушает price/type или что фильтр скидки недоступен вообще, без конкретных доказательств.
2. Проверь **официальные первоисточники** и реальные схемы доступных Steam API: `IStoreQueryService/Query` (`min_discount_percent`, `discounted_dates_filter` — существуют ли, применимы ли, semantics и права), `IStoreService/GetAppList` (`if_modified_since`, `price_change_number` — есть ли и что именно меняют), Steam Search другие параметры. Исправь возможные ошибки прежнего обсуждения: auth/API key, endpoint/версия, доступность из GitHub Actions, лимиты, цена именно KZT, корректная App/Sub идентичность, DLC и root, пагинация, стабильный cursor/sort/total, precision/correctness, квалификация бесплатного/внешнего контента. Если открытые документы не доказывают подходящее поле — `UNVERIFIED`. Внешние ссылки только в report с названиями точных методов. Не выполнять live probe новых API до отдельного approval.
3. Изучить вариант `only new/changed since last run` vs `full snapshot`: скидка началась раньше, но актуальна; скидка закончилась; скидка изменена; цена/доступность изменилась для KZ; игра стала подходящей после улучшения рейтинга/профиля; новое DLC/parent и пакет; пропущенный запуск, сбой, out-of-order события, удаления, непрерывность cursor, часовой пояс. Докажи, есть ли API, позволяющий **событие начала скидки**, или только факт изменения metadata, либо период действующей скидки; нельзя путать эти вещи.
4. Рассмотри hybrid: хранить last-known offers и цены, delta/cursor updates + обновление действующих offers + expiration/reconciliation, периодическая полная сверка. Укажи новые ownership/checkpoint/contract/failure риски и стоимость поддержки; прежде чем рекомендовать архитектуру, проведи preflight.
5. Ищи другие рациональные оптимизации по измеренному приоритету: снижение количества Search pages, повторных AppReviews, StoreBrowse, appdetails/parent lookups, cache TTL/invalidation, ограничение scope без потери, пересечения/дедуп, потенциально safe batch/concurrency без 429, более дешёвые сортировки. Не менять действующие лимиты 180 appdetails starts/300s, retry, paid 50%/4500 KZT, parent fail-closed или daily completeness по умолчанию.

## C. Матрица решений и ТОЛЬКО план следующего пробного запуска
Подготовь сравнение `CURRENT` vs 2–4 конкретных вариантов. Для каждого: требования API, что устраняет, **измеренный** baseline cost, реалистичный математический upper-bound/estimate экономии с явным обозначением допущений (никаких придуманных процентов ускорения), request & wall-time delta, risk of missed App/Sub/DLC, speed of implementation, verified/unknown evidence, fallback. Отметь также оптимизации, которые заведомо не окупятся.

План будущего **предварительно согласуемого** теста:
- отдельный изолированный PR/Actions or offline instrumented compare старой и новой стратегии; один конкретный proposed scope + ожидаемые calls/timeout, без изменений main/production outputs, без рассылки, без semantic workers;
- сравнение на **одном одинаковом зафиксированном source snapshot / контрольном промежутке времени**, контроль изменения предложения между A и B; ID-множество `App_` и `Sub_`, активные предложения, цену KZT, discount, истечение, root/DLC/parent chains, complete/unresolved, ошибок/пропусков; не только top-100;
- критерии PASS: ни одной необъяснённой пропущенной ранее допустимой игры, комплекта и DLC; отсутствие ложных скидок и неверного KZT; проверяемые source coverage/fail-closed; реальные сетевые request count и wall time с одинаковым scope; честный diff+расследование любых расхождений;
- если новая стратегия не может гарантировать текущую полноту/правило ежедневного полного снимка — не менять main, зафиксировать BLOCKED и предложить согласование contract + fallback periodic full reconciliation;
- отдельное согласие пользователя прежде чем создавать/запускать trial или внедрять изменения; после RECON сообщить один наиболее выгодный и безопасный эксперимент.

## Deliverable
**Один report-only draft PR**, добавляющий *только* `reviews/worker_reports/steam-kz-discovery-incremental-filter-speed-recon-01.md`. Не правь `CURRENT_TASK.md`, source, unit tests, workflow, manifest, policy, Board, registry, configs, saved production data. В отчёте:
1. Confirmed facts / unverified hypotheses / impossible to measure.
2. Baseline table по 2–3 completed runs (ссылки на GitHub runs и exact source), CPU benchmark methodology/results или `NOT_MEASURED`.
3. Чёткий разбор официальной доступности/date/discount Steam API и связанных рисков.
4. Поиск дублей/лишних проверок с временем, стоимостью и защитной ролью.
5. Ранжированные 2–4 варианта со savings evidence, risk и планом честного A/B без потери игр.
6. **Вердикт RECON_COMPLETE или RECON_BLOCKED**; одно предложение на согласование пользователя, **не запрашивай согласие в GitHub Actions** и не выполняй IMPLEMENT.

После PR коротко сообщи пользователю номер и ссылку, основные измеренные факты, неизвестные данные и какую отдельную пробу предлагаешь. Далее остановись: Директор проверит и запросит у пользователя отдельное согласие на trial.
