# НОВЫЙ ЧАТ 2 — довести автоматический Lean writer до настоящей активации

Task ID: dossier-lean-writer-auto-activation-01
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Worker: NEW PHYSICAL ЧАТ 2
Mode: bounded ACTIVATION / FIX / runtime acceptance; one source PR only if a fix is necessary.

## START и источник истины
1. Только репозиторий `kentrap2011-hub/steam-kz-deals-2`. Нельзя искать, читать, менять или использовать другой репозиторий. Если GitHub/tool выбрал другой target — STOP и исправь scope.
2. Сначала полностью прочитай `CHAT_PROTOCOL.md` в live `main`, выполни START gate, затем `CHAT_CONTEXT.md`, эту задачу, релевантные `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md`, `config/execution_ownership_contract.json` и `config/dossier_lean_writer_auto_ready_v1.json`. Пройди architecture preflight до runtime/workflow изменений. Не подменяй live `main` историческим SHA.
3. Источник автоматизации — уже объединённый source PR #484, merge commit `5ec1fd0f0ffbf72948e09366b43b155d361f1950` (сверь актуальный `main`). На финальном source HEAD #484 6/6 GitHub Actions checks прошли. По явной воле владельца source PR был принят без независимой L3 QA; этот факт НЕ является доказательством безопасности реального запуска и не разрешает произвольные будущие восстановления.
4. Рабочая реализация по умолчанию выключена: `config/dossier_lean_writer_auto_ready_v1.json#activation_enabled=false`, `source_merge_is_not_activation=true`. Предыдущий ручной owner run #45540222575 завершился ошибкой до записи и израсходовал первую ручную попытку. Строго НЕ перезапускай #45540222575 и НЕ выдавай старую authorisation за новую.
5. Пользователь явно распорядился поручить тебе **включить** подготовленную событийную автоматизацию. Не требуй от пользователя заходить в GitHub, вводить JSON/маркеры или нажимать `Run workflow`. Это разрешение относится только к узкому **изолированному sandbox auto-writer** для шести прежних готовых досье и будущих отдельно owner-authorized `lean_auto_writer` партий, НЕ к semantic Research/Assembly, Deep, canonical main, production, global Lean flags или unlimited retries.

## Что выполнить
A. Адресно проверь именно путь активации из #484: реальный GitHub Actions trigger, `workflow_run`/owner activation-file, проверку актёра/ветки/commit/immutable grants, состояние отдельной одноразовой recovery authority, политику, sandbox HEAD, validity 14-day evidence и idempotent claim. Не начинай новую общую архитектуру и не запускай semantic работу.
B. Подготовь **минимальное** versioned включение механизма для пользователя с уже выраженной авторизацией: GitHub сам обнаруживает READY и использует существующий writer без ручных workflow_dispatch параметров; для старых шести ровно один отдельный согласованный recovery attempt; для новых партий только отдельный иммутабельный owner opt-in. Нельзя изменять `allow_automatic_semantic_retry`, включать канонический Lean writer/reader/Deep и делать общий запуск всей очереди.
C. Если для корректной активации нужен новый source PR, внеси только узкую поправку с подходящими негативными/позитивными тестами, точным финальным HEAD CI, и предоставь директору source PR для приёмки. Не делай self-merge. Если безопасный путь уже существует без правок source, применяй только подтверждённый GitHub-owned one-use activation path после проверки действующих разрешений — без неавторизованных обходов.
D. После реального события докажи по GitHub Actions run ID и неизменяемому sandbox readback, что ровно 6 документов + 6 accepted receipts действительно записаны (либо назови точную причину, если fail-closed). Для будущих партий отдельно подтверди default-off без owner opt-in, а auto-ready механизм остаётся запущенным для отдельно разрешённых партий. Зелёный PR CI сам по себе не равен live success.
E. Поскольку прежнее L3 waiver явно касалось только merge #484, **не считай его автоматическим отказом от обязательных safety gates для реальной активации**. Если текущий contract требует отдельной independent security QA/owner action или нельзя выполнить живой GitHub owner event доступными connector tools, честно STOP с точным единственным blocker и минимальным действием директора; не проси пользователя выполнить длинные ручные GitHub операции. Не имитируй согласие и не запускай опасный shortcut.

## Acceptance, scope и отчёт
- Без дублирования Research/Assembly, без второго scheduler, polling/retry loop, new secrets, credential-in-chat, rerun старой failed Action, переписывания immutable данных, без production/Deep.
- Сохрани все strict V1/V2 и manual writer пути, shared single-writer concurrency, fail-closed typed receipt, SHA, edition/year/TTL, exact transaction и postpush readback.
- Только локально необходимая QA и existing GitHub CI; не назначай дополнительные QA-чаты сам. Риск новой authority/activation фиксируй прозрачно и передай директору.
- Один итоговый worker-report: `reviews/worker_reports/dossier-lean-writer-auto-activation-01.md` в GitHub; статусы `ACTIVATED_AND_VERIFIED`, `SOURCE_READY_AWAITING_DIRECTOR_MERGE` либо точный `BLOCKED_...`. Укажи реальный Actions ID, sandbox SHA/readback, source PR/HEAD, переключатели и что реально работает.
- Не объявляй «готово» без доказательства включённого и выполненного реального GitHub события; не останавливайся на source merge в качестве завершённой активации.
