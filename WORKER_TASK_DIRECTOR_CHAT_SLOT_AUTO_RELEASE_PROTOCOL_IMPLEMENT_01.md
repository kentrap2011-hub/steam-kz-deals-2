# ЧАТ 1 — техническое устранение повторной ошибки учёта свободных чатов

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: director-chat-slot-auto-release-protocol-implement-01
Worker slot: НОВЫЙ физический ЧАТ 1. Предыдущий ЧАТ 1 сдал независимую проверку №348 и освобождён.
Mode: L1 bounded governance implementation; ONE implementation PR.
Canonical accepted audit: reviews/worker_reports/director-chat-completion-slot-release-recurrence-audit-01.md (merged audit PR №351).
Owner of rule: DIRECTOR_PROTOCOL.md.

## Начало
Сначала полностью прочитай актуальный CHAT_PROTOCOL.md, выполни START gate, затем этот task, DIRECTOR_PROTOCOL.md и указанный принятый audit report. Работай только в указанном репозитории, main как source of truth. Предыдущие аудиты №325, правки №333/334/337 и технический REGISTER №345 рассматривать только по нужным audit ссылкам; не выполнять новый аудит.

## Единственное разрешённое изменение
В одном source PR исправить только DIRECTOR_PROTOCOL.md по точному bounded плану принятого аудита:
1. STATUS/CHAT_AVAILABILITY: разделить рабочую доступность НОМЕРА и технически неизвестное состояние UI. По итоговому сдаваемому worker-report номер автоматически СВОБОДЕН, даже если код/QA не приняты. После зарегистрированного и выданного, но не запущенного нового задания номер ЗАРЕЗЕРВИРОВАН (ожидает запуска). После подтверждённого user запуска номер ЗАНЯТ до финальной сдачи. Статусы реестра active/complete и наличие открытого окна ChatGPT сами по себе не доказывают занятости/освобождения. Сохранять STOP/read-only для простого запроса о статусе.
2. Обязательная сводка в конце каждого директорского ответа: только операционные `свободен/зарезервирован/занят/неизвестно при действительном конфликте`; без бессрочного UNKNOWN после финального report и без дополнительных вопросов «закрыли окно?». Нерассмотренный source PR/QA не занимает прежний слот.
3. §2 выбор номера/передача: убрать скрытое условие «явно закрыта физическая беседа»; минимальный реально свободный номер для НОВОГО чата; новая текущая, но не запущенная регистрация сохраняет резервацию; уточнения допустимы лишь при настоящем доказательственном конфликте.
4. §3: «после завершения/принятия» заменить на «после финальной сдачи результата независимо от приёмки»; §10 убрать неверный `complete != UI close => UNKNOWN slot`; §11 чётко отделить рекомендацию удалить окно в UI от автоматического освобождения номера. Не удалять безопасность при удалении UI.
5. Security: release номера не является разрешением на semantic запуск, retries, recovery, production, scheduler, merge или изменение immutable bindings. Существующие mandatory CI и L3 gate остаются. Не добавлять новый gate, workflow, UI-детектор, очередь, registry schema, новое планирование или автоматизацию.

Разрешённый write set source PR: ТОЛЬКО DIRECTOR_PROTOCOL.md и один короткий implementation worker-report в reviews/worker_reports/director-chat-slot-auto-release-protocol-implement-01.md; не переписывать Board/registry, старые отчёты, scripts/director_registration_prewrite.js и действующие WORKER_TASK. Сохранять малую дифф-дельту и оригинальный контекст правил, заменять, а не наслаивать ещё одно противоречащее правило.

## Acceptance и завершение
В отчёте кратко зафиксировать walkthrough статуса/назначения: (а) старые ЧАТЫ 1/2 завершили QA №339/340 и свободны при unmerged source; (б) ЧАТЫ 3/4/6 сдали source и свободны вне зависимости от приёмки; (в) новые QA 1/2 назначены, но не запущены => резерв, а не «занят»; (г) подтверждённый запуск занимает до final report; (д) исторический `active/complete` не захватывает слот; (е) вопрос о UI отдельно может быть UNKNOWN; (ж) STATUS не создаёт REGISTER; (з) MERGE без L3/CI продолжает BLOCKED. Привести negative examples и rollback по аудиту.
Дождаться GREEN существующих exact-final-HEAD site task + backlog CI. Один implementation PR, можно готовый к review, не self-merge, не создавать независимый QA без конкретного L3 риска. Verdict READY_FOR_DIRECTOR_MERGE или BLOCKED_CONCRETE. Директор самостоятельно проверит и примет минимальный L1 governance PR.
