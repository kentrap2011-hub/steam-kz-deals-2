# ЧАТ 1 — причина DLC 235960 и план мгновенной живой проверки GitHub (RECON)

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: steam-nested-dlc-235960-root-cause-live-smoke-design-01
Worker: **НОВЫЙ физический ЧАТ 1**
Mode: **RECON / READ-ONLY NOW** — root-cause report + constrained live-smoke design. **НЕ IMPLEMENT**, не изменять код, workflow, policy, pricing, тесты, production до отдельного согласия пользователя после исследования.
Report: `reviews/worker_reports/steam-nested-dlc-235960-root-cause-live-smoke-design-01.md` в **одном report-only draft PR**. Не self-merge.

## START и repo guard
Первым делом полностью прочитай из актуального main `CHAT_PROTOCOL.md` и выполни START gate; затем этот task, `CHAT_CONTEXT.md`, адресный Steam KZ DLC-маршрут `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, `config/mailing_policy.json` (paid discovery), `PROJECT_DECISIONS.md` только relevant, `scripts/steam_targeted_paid_lanes.py` вокруг `discover_dlc_for_bases`, `scripts/steam_partial_publish_runner.py` и `.github/workflows/steam-test.yml`. Работай **ТОЛЬКО** в `kentrap2011-hub/steam-kz-deals-2`. Не искать, читать или менять другие repos. Если GitHub/tool переключился на другой repo, остановись. Не делать repository-wide audit.

## Доказанный инцидент
Штатный scheduled main Steam KZ run №42315924316 (2026-11-07 UTC) на `b24a34027e4c96af40efca8554a954a635d27173` завершился после 1817 appdetails HTTP 200 (без appdetails 429): `DLC App_235960 contradicts verified parent relation` в `targeted_dlc_relations_failed`. Точный run: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42315924316. Лог подтверждает запросы `2820` (parent_relations #3), `201310` (dlc_price #390), `235960` (dlc_price #404), `1697640` (dlc_price #1117); HTTP 200 на все. Raw `cc=kz` JSON `data.dlc` и `data.fullgame` не сохранён в логе — **не угадывать фактическую отрицательную связь**. Ручной run №42262206049 2026-11-06 ранее остановился на независимом Steam HTTP 502 для `874344`. PR #404 уже добавил bounded two-hop parent-chain, #408 — verified root-game alias; оба в main. Старые paid данные сохранены, mailing/pre-AI skipped. Это не 429 и не повтор ошибки идентичности 1697640.

## Сначала установить фактическую причину и показать пользователю
1. Адресно проверить ветки `direct`, `nested`, `fullgame`, `paths` при ошибке `235960`. Установить, **какой именно root и какое поле** приводят к contradiction, не принимая гипотезу `2820→201310→235960` за полный фактический набор связей. Обязательно различить:
   - `235960` listed напрямую у base, а `fullgame` ссылается на промежуточный DLC;
   - тот же `235960` listed у нескольких admitted roots, из которых часть не имеет доказанного пути;
   - `201310` отсутствует в root list или сам `fullgame` противоречит root;
   - другой подтверждённый сценарий. Не утверждать любой из них без доказательств.
2. Определить, можно ли доказать все необходимые ребра **по существующим** GitHub логам/artifacts/исходному PR; при недостатке сырого Steam JSON сделать только компактный read-only запрос точных публичных `appdetails?appids=...&cc=kz&l=english` IDs в пределах 3–6 обоснованных IDs, без fan-out/массовой очереди/автоповторов. Если доступ к Steam отсутствует, отметить UNKNOWN и какой конкретный JSON/поле пользователь может предоставить. Не создавать новый GitHub workflow для RECON и не вызывать production. Нельзя считать новые JSON идентичными историческому ответу.
3. Отчёт с доказательствами: exact requested IDs, `type`, `steam_appid`, `fullgame.appid`, релевантная принадлежность к `dlc`, подтверждённые origin root IDs, где именно алгоритм fail-closed, реальное vs предположения. При недостатке данных — `RECON_BLOCKED_UNVERIFIED`.

## Заранее спроектировать ТОЧЕЧНУЮ LIVE-проверку GitHub после будущего исправления
Пользователь одобрил идею **проверить только DLC 235960 на реальных данных Steam до мерджа будущего source PR**, чтобы не запускать каждый раз 50–60-минутный production. Это не разрешение прямо сейчас чинить алгоритм либо запускать production.

Составить проверяемый проект smoke-gate, который после отдельного согласия на IMPLEMENT:
- работает на GitHub Actions, максимально использует существующий PR-only `steam-test.yml` / existing producer, **без нового schedule**; если новая `workflow_dispatch` не может работать до появления workflow в default main, учесть это и выбрать фактически работоспособный **PR-only** запуск до merge, либо обосновать альтернативу;
- делает **только обоснованное ограниченное** число реальных `cc=kz` запросов по `2820`, `201310`, `235960` и **другим root ID, только если их необходимость доказана**; без полного каталога, без каких-либо production writes, без секретов, без бессрочного retry, без обхода общего 180/300s лимита; timeout и network-error дают `INCONCLUSIVE/FAIL`, никогда не подменяются зелёным PASS;
- использует **тот же validator и caller semantics**, что production (или отчёт явно указывает покрытый subset и почему smoke не доказывает всё); не создаёт параллельный упрощённый алгоритм, который легко пропустит исходный случай; фиксирует входной AppID, фактический `steam_appid` и тип, exact parent link(s), расхождение `fullgame`, выбранный путь, причины skip без ложного «всё ОК»;
- подтверждает, что `235960` правильно принят/отклонён **по реальным relationship evidence**, genuine unrelated DLC и ошибочные цены остаются fail-closed, KZT 4500/≥50% не ослаблены; без фиктивной скидочной карточки для бесплатного/неpriced DLC;
- сохраняет короткий bounded GitHub Actions summary/artifact (без больших raw JSON и sensitive headers), statuses `PASS` / `FAIL` / `INCONCLUSIVE`, точный source commit/PR и дату запроса;
- выполняет локальные deterministic positive/negative tests и имеющийся PR CI, отдельно обозначает, что успешный smoke **не доказывает полный scope**; один полноценный main collector→mailing→pre-AI остаётся отдельным после source acceptance и отдельного пользовательского разрешения на ручной запуск.

## User approval gate (ОБЯЗАТЕЛЕН)
**ЗАКОНЧИ RECON, покажи пользователю точную доказанную причину + предложенное исправление + форму короткого GitHub live smoke и спроси разрешение на IMPLEMENT. До его явного следующего «исправь/да» — никакого IMPLEMENT, source PR, workflow patch, dispatch, live production или code changes.** Эта задача не конвертируется автоматически в IMPLEMENT. Если пользователь одобрит, директор зарегистрирует отдельное scoped IMPLEMENT-поручение с дополнительными risk/CI gates и обязательной независимой QA для существенной workflow-дельты. Не считать уже выданное согласие на идею живой проверки разрешением на изменение parent/source/price-policy.

## Deliverable
Только `reviews/worker_reports/steam-nested-dlc-235960-root-cause-live-smoke-design-01.md` в одном report-only draft PR. Статус `RECON_COMPLETE_AWAITING_USER_DECISION` либо `RECON_BLOCKED_UNVERIFIED`. Доказанные поля, source lines, ссылки на run, конкретные риски, **один предложенный bounded fix** и точная проверка GitHub, включая возможность её запуска **до** merge. Финальный короткий вывод для пользователя; ничего больше не менять.
