# ЧАТ 3 — техническая защита регистрации задач

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: director-typed-registration-prewrite-implement-01
Worker: НОВЫЙ физический ЧАТ 3 (не продолжение ранее завершённых чатов).
Mode: ограниченная самостоятельная реализация или адресная диагностика, только в разрешённом scope.

Сначала полностью прочитай актуальный CHAT_PROTOCOL.md и выполни START gate, затем этот task, относящиеся к нему CHAT_CONTEXT.md / PROJECT_ROUTES.md и точные контракты. Работай только в данном репозитории. Другой репозиторий не открывать и не менять.

## Цель и доказательства
Директор снова допустил запрещённые поля и неправильные значения в PR #338, как ранее в PR #317. Системный отчёт ЧАТА 3 — report-only PR #342 (reviews/worker_reports/director-repeated-registration-failures-systemic-fix-01.md, branch report/director-repeated-registration-failures-systemic-fix-01). Предыдущий аудитор PR #319 предложил похожую технику, но ничего не внедрил. Не повторяй диагностику.

Реализуй один реально применимый директором REGISTER pre-write механизм: сформировать в памяти новые task-файлы + registry + текущую Board-секцию; проверить допустимые enum, все публичные поля, timestamps, зависимости, ID/file, разрешённый write-set, точный base, явные transitions старых задач; только после полного PASS писать в GitHub. Запретить незапрошенные изменения других item IDs, исторических Board-секций, чужих code/workflow файлов. Ошибки "малая" и "PR #" предъявлять одновременно в одном preflight, до branch/commit, без молчаливой автозамены. Проверка должна работать и для двух задач с двумя *явно разрешёнными* completion transitions, как в #338.

Представь реально исполнимый интерфейс для функций GitHub connector и functions.exec. Не выдавай записанный в репозитории JS за возможность импортировать его в исполняемом чате: если импорт/транзакционный Git tree невозможен, докажи рабочий вариант в имеющемся интерфейсе или честно BLOCKED_TOOLING. Сохрани GitHub как владельца контроля, единственный registration PR и нынешние CI. Не добавляй scheduled tasks, отдельный workflow, новый цикл QA и длинные правила.

Проверки: fixtures #317 и #338 с нулём write calls при неправильных значениях; валидный один/два task batch, независимость чужих записей, exact base race, неверные IDs/URLs/secrets/слоты. Один узкий implementation PR от main, только необходимые скрипты/schema/тесты/короткая замена регистрационного правила, без изменения живых задач и production. Отчёт reviews/worker_reports/director-typed-registration-prewrite-implement-01.md. Verdict READY_FOR_DIRECTOR_REVIEW или BLOCKED_TOOLING, exact HEAD CI; не объединять самостоятельно.
