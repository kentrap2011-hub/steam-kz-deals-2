# НОВЫЙ ЧАТ 1 — независимая QA Steam alias PR #408

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: steam-listed-base-alias-pr408-independent-qa-01
Worker: **НОВЫЙ физический ЧАТ 1** (не прежний разработчик)
Mode: **INDEPENDENT SOURCE QA / READ-ONLY; NO IMPLEMENT**
Report path: reviews/worker_reports/steam-listed-base-alias-pr408-independent-qa-01.md

## START и границы
Работай **только** в репозитории `kentrap2011-hub/steam-kz-deals-2`; другие репозитории не искать, не читать и не изменять. Если система открыла другой repo, остановись. Первым делом полностью прочитай `CHAT_PROTOCOL.md` в актуальном `main`, выполни START gate; затем полностью прочитай этот task, `CHAT_CONTEXT.md`, релевантный `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json` и KZ paid-DLC раздел `config/mailing_policy.json`. Не выполняй широкий аудит backlog, не запускай production, не редактируй source или tests, workflow, Board, registry, automation, scheduler, `CURRENT_TASK.md` и не меняй политику. Только один **report-only PR** с собственным QA-отчётом. Никакого self-merge.

## Точный материал QA
- Исходный **draft source PR #408**: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/408 (`fix: exclude verified Dying Light root-game alias from targeted DLC`), начальный HEAD `d3000e5cc66e1f2d1989232e97f0f55494068e04`. На старте и перед финальной сдачей сверить **актуальный** HEAD и всю материальную дельту. Reviewer — **другой физический чат**, не автор.
- Исходный report-only RECON PR #407: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/407; он не объединён. Он содержит отчёт `reviews/worker_reports/steam-appdetails-1697640-identity-recon-01.md`.
- 05.11.2026 реальный main run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42033530995 остановился на `KZ appdetails App_1697640 contradicts requested AppID 1697640`: 1223 HTTP 200, без 429. Историческое внутреннее ID в логе отсутствует.
- 06.11.2026 пользователь получил текущий официальный Steam API JSON: outer key `1697640`, `success=true`, `data.steam_appid=239140` (целое), `type=game`, `name=Dying Light`, `data.dlc` содержит `1697640`. Текущий alias доказан; не выдавай этот JSON за записанное историческое тело ответа.
- Пользователь отдельно одобрил ограниченное IMPLEMENT после RECON, и отдельным сообщением **одобрил независимую QA**. Эта QA не является полномочием на source merge, production, sematic Dossier, retry или повторный запуск.

## Независимая проверка
1. Проверить точный PR diff #408, изменение `scripts/steam_targeted_paid_lanes.py`, unit tests, policy decisions и worker report. Граница: только `verified listed root game alias` при **единственном** доказанном root, type=game, exact root internal appid и **обратном** членстве alias в `dlc` root. Нельзя принимать алиас чужого root, тип DLC, ambiguous root, неполные связи, самоссылки. Проверить, что `get_appdetails` по умолчанию по-прежнему строго валидирует ID, что реальный production caller точно передаёт контекст только в first-hop, а mock тесты не скрывают нетипичной caller ветки.
2. Проверить, что алиас `1697640` НЕ становится paid DLC, не наследует price/discount `239140`, не запускает nested expansion, не подменяет identity или relation. Настоящие платные дочерние DLC сохраняются. Не допускаются silent truncation, неверная `related_dlc_unique_ids` или `dlc_price_lookups` статистика и декларация completeness при неполной проверке.
3. Негативные случаи: unrelated/malformed ID, foreign/missing `fullgame`, missing reverse edge, duplicate/multiple eligible roots, nested alias, poisoned `dlc` list, wrong type, wrong price currency, truncated/partial KZT `price_overview`, неправильно опубликованная цена, циклы, ошибочная обработка HTTP 429/5xx. Сохранены KZ cc, 180 physical request starts / rolling 300s, deadline/429 guards, цена ≤4500 ₸, скидка ≥50%, существующий fail-closed и last-known-good publication isolation. Отдельно оценить конкретные L2/L3 риски и не маскировать их тестами.
4. На **точном финальном HEAD** исходного PR #408 подтвердить GitHub CI `steam-test.yml/regression`, `validate`, `backlog-disposition`; исходно reported 18/18 targeted PASS at `d3000e5cc66e1f2d1989232e97f0f55494068e04`. PR-only `collect` штатно skipped — это не production proof. Самостоятельные небольшие offline тесты по необходимости допустимы, но в source PR ничего не меняй.
5. Результат — **один** report-only draft PR, в котором изменён только `reviews/worker_reports/steam-listed-base-alias-pr408-independent-qa-01.md`. Укажи `PASS` или `BLOCKED_SAFETY`, source PR URL, его точный HEAD, файлы/строки с ошибками, точные результаты CI, границы/непроверенные факты, substantive risk level, один следующий шаг. Нет source fixes, QA self-merge, production, scheduler, Dossier/Deep. Если обнаружен существенный дефект — докажи минимальным контрпримером и обозначь блокер. Пользователю покажи краткий итог и ссылку; окончательный MERGE/решение за директором.

## STOP
Если прямой caller, exact root proof или безопасный KZT/identity guard недостаточно доказаны, либо CI не green на exact source HEAD, выставь `BLOCKED_SAFETY`. Не предлагай просто игнорировать mismatch и не маркируй unit tests как live recovery.
