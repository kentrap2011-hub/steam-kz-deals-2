# НОВЫЙ ЧАТ 1 — DLC без цены: пропуск только достоверного no-price, KZT защита обязательна

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: steam-targeted-dlc-missing-price-guard-01
Worker: **НОВЫЙ физический ЧАТ 1**
Mode: bounded IMPLEMENT + developer self-review + existing tests/CI; **ONE source PR, NO separate QA worker**
Final report: `reviews/worker_reports/steam-targeted-dlc-missing-price-guard-01.md`

## START и рамки
Сначала полностью прочитай текущий `CHAT_PROTOCOL.md`, выполни START gate, затем полностью этот task. Читай адресно `CHAT_CONTEXT.md`, `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, `config/mailing_policy.json` и релевантные границы DLC. Выполни architecture preflight до правки. GitHub по-прежнему владеет production/control plane: никакого нового workflow, планировщика, очереди, semantic Dossier/Deep, ручного production/replay или переноса ответственности в чат.

## Подтверждено и что ещё нужно доказать
На live main SHA `798566d5d6bc5c1ae1956b230b2844c751f35950` GitHub Actions run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41944401178 (collect job `126972891588`) завершился `DLC App_201877 has non-KZT price` после HTTP 200 на DLC AppID 201877. Все 432 appdetails имели HTTP 200, first_429=false; live source-validation прошёл. Полный сбор не завершился, старое платное содержимое сохранено, downstream mailing/pre-AI skipped. Пользователь проверил страницу Steam DLC и сообщает, что цены нет. **Это сильная гипотеза no-price, но фактический appdetails `price_overview` в этом run не был сохранён** — не приписывай Steam недоказанные точные поля.

Текущий код: `scripts/steam_targeted_paid_lanes.py::discover_dlc_for_bases` после строгой identity/type проверки делает `price = data.get('price_overview') or {}`; затем `price.get('currency') != 'KZT'` вызывает отказ ДО проверки `final`/`discount_percent`. Поэтому отсутствующая цена маскируется под неверную валюту.

## ОДНО ограниченное исправление
1. Подтверди точную ветку условий из кода и, если доступно без широкого/массового запроса, реальный ответ для `AppID 201877`, обязательно для `cc=kz`. Не выводи «Steam вернул None» без прямого доказательства; если запрос небезопасен/недоступен, используй воспроизводимый искусственный тест и явно отметь границу доказательств.
2. Локально различи: (а) **достоверное отсутствие ценовых данных** (`price_overview` отсутствует/null/документированно пуст) → DLC не является проверенным платным предложением, **не создавать карточку, продолжить другие DLC**; (б) присутствующие корректные полные данные `currency=KZT` → прежние price/discount gates; (в) **присутствующая цена/валютный маркер не KZT, противоречивая/частичная или malformed структура** → не трактовать как no-price и **не обходить строгую проверку**, для важных integrity failures сохранить fail-closed. Если точные требования для null/empty/partial не очевидны, проверь контракт и не расширяй no-price исключение по умолчанию.
3. Сохрани точную `KZ` привязку, identity, parent/fullgame relation, ordered dedupe, no-global-DLC traversal, полный paid source scope, `PAID_MAX_PRICE_KZT`, `PAID_MIN_DISCOUNT_PERCENT`, прежнюю публикацию на ошибке, строгую обработку настоящей foreign currency. Не меняй appdetails 180/300 limiter, Steam Search cap/sort #399, не создавай retry ради отсутствующей цены.
4. Добавь deterministic regressions в `scripts/test_steam_targeted_paid_lanes.py`: exact App_201877 no-price fixture и следующие валидные DLC продолжают обрабатываться; KZT платный скидочный DLC проходит; присутствующий RUB/USD/другая валюта fail-closed; malformed `price_overview` и опасная partial `currency` fail-closed; wrong identity/type/parent всё ещё fail-closed; подсчёт eligible DLC/источника честный. Не делать реальных Steam запросов в unit tests.
5. **Самостоятельно** проведи developer self-review и существующие адресные тесты плюс PR GitHub `steam-test.yml` `regression`/`validate`/`backlog-disposition` (все реально обязательные на финальном HEAD). Проверь примеры, исправь все обнаруженные ошибки **в этом же единственном source PR**. Не инициируй и не требуй второй worker/QA чат; это локальная правка небольшой ветки, отдельная L3 QA не запрошена. Если обнаружится material scope/risk, не маскируй его — STOP и сообщи директору.
6. Worker-report должен содержать source PR URL, HEAD SHA, changed files, фактические тесты/CI с результатами, до/после для no-price и foreign-currency, судьбу App_201877 (confirmed/assumed/unknown), остаточные риски. PR не принимать самостоятельно. Изменения в статус/Board/plan — только через Director.
7. Директор применит acceptance gates и после merge оценит **один** настоящий main production run `Steam KZ production shortlist`; успехом считается не локальный unit test, а полный Steam→mailing→pre-AI и свежая подходящая Dossier binding. Для нового live запуска отдельное разрешение, если штатный auto trigger не случится.

## STOP
Если на `AppID 201877` фактически есть валидная KZT цена, выясни причину несовпадения и не внедряй выдуманный no-price fix. Если валюта реально иностранная, не заменяй fail-closed на «пропустить всё»; верни конкретное доказательство и один следующий безопасный шаг.