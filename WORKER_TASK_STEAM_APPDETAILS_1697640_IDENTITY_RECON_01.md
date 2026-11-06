# НОВЫЙ ЧАТ 1 — RECON ONLY: несоответствие AppID 1697640 в Steam KZ appdetails

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: steam-appdetails-1697640-identity-recon-01
Worker: **НОВЫЙ физический ЧАТ 1**
Mode: **READ-ONLY DIAGNOSIS / RECON, NO IMPLEMENT, NO FIX**
Output report: `reviews/worker_reports/steam-appdetails-1697640-identity-recon-01.md` in at most ONE report-only PR, plus concise factual explanation to user.

## User authorization boundary — critical
Пользователь явно разрешил **только установление причины** ошибки и показ доказательств. **Любое исправление кода, алгоритма, policy, tests, CI/workflow, runtime, price scope, identity checks или отключение fail-closed запрещено до НОВОГО явного одобрения пользователя после отчёта.** Даже если причина кажется очевидной или решение простое, не создавать source PR, не выполнять IMPLEMENT, не корректировать production. Единственные разрешённые GitHub writes — *один* report-only PR, содержащий один отчёт по указанному пути; он не является исправлением и не должен сам объединяться. Не запускать GitHub Actions production, workflow dispatch, replay, retry, semantic Dossier/Deep, scheduled tasks, mass requests или backfill.

## START и scoped route
Сначала полностью прочитать `CHAT_PROTOCOL.md`, выполнить START gate и полностью прочесть этот task. Адресно читать `CHAT_CONTEXT.md`, `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, только необходимый участок `scripts/steam_targeted_paid_lanes.py` (`get_appdetails`, `_canonical_appid`, `_check_fetched_identity`, `discover_dlc_for_bases`), минимальный вызывающий путь `scripts/steam_partial_publish_runner.py` и релевантные части исходного GitHub Actions run. Не делать широкий аудит репозитория. Если потребуется предложить любое изменение runtime/ownership, предварительно провести architecture preflight и оставаться строго в RECON.

## Доказанный исходный инцидент
Реальный ручной main run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42033530995 (main `61d29f95582d74f83cf897c3fbe67c3d0d31139d`) остановился в `targeted_dlc_relations_failed` с текстом:
`KZ appdetails App_1697640 contradicts requested AppID 1697640`.
`dlc_price`, appdetails №1223; HTTP 200 на всех 1223, appdetails first_429=false. Предыдущий каталог сохранён, последующие mailing/pre-AI пропущены. В логе есть **только запрошенный AppID 1697640**, фактическое значение `data.steam_appid` в неудачном ответе не записано. Важно: фраза ошибки НЕ раскрывает, какое значение вернул Steam. Не утверждать конкретное второе число, наличие redirects или неверные данные Steam без доказательства.

После этого был штатный scheduled run https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42140416634; его итог и связь с AppID 1697640 проверять **только при необходимости**, не считать тем же инцидентом по умолчанию.

## Вопросы, на которые нужно ответить
1. **Почему** система вообще запрашивала AppID `1697640`? Показать, из какого exact parent/DLC listing пришла идентичность в данном run, если это доказуемо по сохранённым артефактам/логам; если нет — UNKNOWN, не выдумывать игру-родителя.
2. Точно объяснить кодовый механизм: `appids=1697640&cc=kz`, ответ-key `1697640`, `success`, `data.steam_appid`; какая проверка была пройдена, и на какой проверке возникло несовпадение. Различать **key ответа** от **внутреннего steam_appid**, отсутствие поля и тип поля. Показать реальное значение несовпадающего ID только после документированного доказательства.
3. Пытаться восстановить источник расхождения безопасно и **точечно**: сначала существующие минимальные run artifacts, GitHub logs, доступные доказательства Steam/SteamDB/official docs. Если разрешён прямой публичный точечный Steam `appdetails` с `cc=kz` — не более одного bounded запроса на проблемный ID, без автоматических повторов, fan-out и сохранения токенов; обязательно записать дату, URL/параметры, факт HTTP+success, raw entry-key, внутренний `steam_appid` или его отсутствие и тип значения. Один текущий ответ не доказывает исторический JSON, если ответ изменился.
4. Сопоставить возможные классы причин (например, реальные metadata mismatch, перепривязка Steam AppID, особенность API, ложноположительная проверка приложения) **только с наблюдаемыми доказательствами**. Не заменять UNKNOWN вероятной версией. Вывести варианты безопасного решения **как предложения**, включая сохранение fail-closed и ограничения; не рекомендовать безусловный skip неправильной identity, расширение поиска или подмену цены/связей другой игрой.
5. Итог **сначала показать пользователю**: коротко (а) запрошенный ID, (б) фактический ID/UNKNOWN, (в) первопричина CONFIRMED/LIKELY/UNKNOWN, (г) доказательства и ограничения, (д) один рекомендуемый способ исправления и риски. Прямо спросить о разрешении на **отдельную будущую IMPLEMENT-задачу**. **До ответа пользователя никаких действий по исправлению.**

## Deliverable / STOP
Один краткий report-only PR (только `reviews/worker_reports/steam-appdetails-1697640-identity-recon-01.md`, без изменений программ/тестов/workflows/registry/Board) со ссылками на доказательства, точными типами и фактическими полями или с явным `UNKNOWN`, root-cause versus hypotheses, вариантами действий, риском и статусом `RECON_COMPLETE_AWAITING_USER_DECISION` либо `RECON_BLOCKED_UNVERIFIED`. Рабочий чат не объединяет PR и не назначает разработчика. Директор после отчёта покажет результат пользователю; только после явного согласия на bounded IMPLEMENT регистрируется отдельная задача. Если доступ к Steam API не получен — остановиться честно без фиктивной причины, указать точно необходимое наблюдение.
