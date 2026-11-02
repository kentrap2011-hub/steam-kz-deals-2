# НОВЫЙ ЧАТ 5 — независимый аудит медленной выдачи директорских промптов

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: director-worker-prompt-latency-target-60s-audit-01
Worker slot: НОВЫЙ физический ЧАТ 5
Mode: independent READ-ONLY targeted latency RECON / process QA; ONE report-only DRAFT PR.
Report: reviews/worker_reports/director-worker-prompt-latency-target-60s-audit-01.md

## START
Прочитай CHAT_PROTOCOL.md целиком и выполни START gate. Затем прочитай этот task и только нужные фрагменты DIRECTOR_PROTOCOL.md, CHAT_CONTEXT.md, PROJECT_ROUTES.md и регистратор scripts/director_registration_prewrite.js. Работай только в kentrap2011-hub/steam-kz-deals-2; другой репозиторий не искать, не менять, не использовать. Если GitHub target неверный или неоднозначный — STOP. Никакого общего repository archaeology.

## Почему
Пользователь наблюдает примерно 3 минуты до получения короткого копируемого промпта нового worker-чата; недавно наблюдал также 4 минуты, ранее около 5 минут. Цель пользователя: **обычный короткий prompt/handoff в среднем около 60 секунд**. Не придумывать инструментальных точных wall-clock метрик чата, которых GitHub не содержит; человеческое наблюдение и GitHub timestamps разделять. Проверить, что путь не загружен лишними чтениями, повторными инструментальными вызовами, неверными полями и CI retries.

## Чёткие объекты исследования
1. Последние адресные регистрации PR #373, #376, #377, #378; также один старый подтверждённый повтор ошибок PR #338 и вектор предыдущего аудита PR #319 / #342, при необходимости отчёт PR #305 о verification overhead. Перечитывать ровно необходимые короткие записи, PR commits/CI and statuses, не полные истории. Использовать точное время создания PR, старт/окончание required CI, commit/merge, количество amend/retry, если оно видно в GitHub.
2. Разделить critical path: (a) director DECIDE/source truth/status scan, (b) подготовка task и краткого текста, (c) deterministic prewrite/strict field checks, (d) create tree/commit/branch/registration PR, (e) GitHub CI queue/runtime, (f) head-bound merge, (g) main verification, (h) response/copy UI. Для каждого: доказанное время GitHub или unknown, обязательность, повторные вызовы, возможность параллелить/устранить. Помнить, что calls in one functions.exec могут параллелиться, но publication depends on exact main and required CI.
3. Проверить, какие предыдущие рекомендации реально внедрены, в особенности scripts/director_registration_prewrite.js atomic validation; отметить повторения, которые действительно остаются, а не предлагать ещё один абстрактный аудит. Обычный короткий command после зарегистрированного task должен появляться быстро; создание нового canonical task и обязательное CI могут занимать больше минуты, это разные виды ожидания.
4. Сравнить по минимуму три работающих решения: минимальное устранение лишних адресных чтений/повторных проверок, шаблон typed one-shot registration с dryRun и независимыми parallel reads, отделение мгновенной выдачи уже зарегистрированных task от новой записи с CI. Рассмотреть asynchronous/nonblocking GitHub CI без преждевременной выдачи запуска как отдельную возможность, но не разрешать worker до main/CI. Можно дополнительно предложить надёжные time-budget и instrumentation в пределах уже существующих инструментов, не выдумывая фоновые агенты.
5. Дать конкретные критерии: сценарий уже зарегистрированной задачи — целевая выдача до 60 секунд при доступном GitHub, новый REGISTER — целевое 60 секунд при быстрых CI или честно назвать внешний предел, ноль ненужных retries, ноль незарегистрированных launcher, ноль обходов safety. Определить измеримый p50/p90 только если действительно есть достаточная выборка; иначе выписать план измерений без ложной статистики. Отдельно оценить эффект для пользователя (скорость) и риск безопасности.
6. **Следующий шаг НЕ должен теряться.** Дай один конкретный минимальный implement task c точным fileset, владельцем и проверкой эффекта, без немедленного запуска нового аудита. При наличии готовой существующей реализации предложи использовать её, а не дублировать.
7. Считать получение worker report не концом parent-task: узко определить, как директор должен довести оценку до решения и закрыть процесс, не превращая 60-секундный prompt в рискованный auto-merge/production. Не конфликтовать с параллельными работами ЧАТОВ 1 и 3 о director continuity и consent rules.

## Ограничения и приёмка
Это только read-only independent audit: не изменять source, scripts, director protocols, Board/registry, текущие worker tasks, GitHub workflows, settings, CURRENT_TASK.md, production, V1/V2/Deep, scheduler. Один новый report-only DRAFT PR с единственным файлом reviews/worker_reports/director-worker-prompt-latency-target-60s-audit-01.md. Не запускать real semantic tasks, не self-merge, не обходить mandatory checks, не требовать «среднее 60s» ценой преждевременного launcher. Отчёт должен содержать фактическую цепочку времени, гипотезы отдельно, таблицу устранимого overhead, реалистичное целевое SLO, ровно одно практическое решение/следующий ответственный, и вердикт: ACTIONABLE_LATENCY_FIX / EXTERNAL_CI_BOUND / BLOCKED_EVIDENCE.
