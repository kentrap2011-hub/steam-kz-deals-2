# НОВЫЙ ЧАТ 1 — независимая L3 QA изменённых правил директора

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: director-pr372-consent-gate-independent-l3-qa-01
Worker: НОВЫЙ физический ЧАТ 1, не прежний завершивший Chat 1
Mode: INDEPENDENT, READ-ONLY L3 governance/authorization QA
Report: reviews/worker_reports/director-pr372-consent-gate-independent-l3-qa-01.md

## START
Полностью прочитай CHAT_PROTOCOL.md, выполни START gate, затем этот task, адресно необходимые разделы CHAT_CONTEXT.md, DIRECTOR_PROTOCOL.md, PROJECT_ROUTES.md, actor/ownership contracts и source PR #372 (https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/372). Работай только в указанном репозитории, не читай и не меняй другие репозитории.

## Центральная задача
Source PR #372 объединяет две уже согласованные пользователем функции: (1) результат worker → один новый обоснованный шаг → одно согласие до новой работы → REGISTER без пересогласования; (2) уже согласованная конкретная bounded implementation задача после точных обязательных CI, risk-specific независимой QA и проверки HEAD/scope/mergeability/rights принимается директором без второго разрешения "принимаем ли?". ЧАТ 3 внёс эту поправку внутри существующего source PR #372, но честно классифицировал её L3 из-за границ user consent. Предварительный source HEAD `5d1126192f5a61f1a5143849a63330570d3359f3`; обязательно прочитай live HEAD и CI, не доверяй старому.

## Независимая QA
1. Проверить точный source diff PR #372, обе серии report и последнее выданное пользователем согласие; не выводить grants из одного worker report, Board или CI. Сверить все активные STATUS/DECIDE/REGISTER/MERGE/post-QA closeout и CHAT_PROTOCOL PRE-SEND на непротиворечивость; старые определения не должны незаметно восстанавливать второй вопрос.
2. Проверить положительный scoped authorization: только user-approved concrete IMPLEMENT→source MERGE при неизменном scope, успешных required CI, достаточной L3 QA, правомерности actor, текущем HEAD, mergeability и без конфликтов.
3. Проверить отрицательные кейсы: нет либо отозвано initial grant; ambiguity "да"; только RECON/QA grant; scope drift, new owner/permissions; production/deploy, semantic one-shot, scheduled, recovery/retry; material new HEAD after QA; red/pending/skipped required CI; недоступность GitHub; target PR уже merged; source vs QA report PR. Все должны fail-closed либо не повторять действие.
4. Убедиться, что не расширяются права до автономного запуска production/semantic/новых Scheduled Tasks и что первоначальная функция result→consent→new task сохранилась.
5. Отдельно проверить замечание завершённого Chat 1 PR #380: после QA/merge PR #372 должен быть отдельно внедрён durable closeout/recovery, пока он НЕ реализован. Вердикт по PR #372 нельзя трактовать как завершение восстановления. Используй факты независимой fallback QA PR #382, но не повторяй её широкий аудит.
6. Привести фактическую точную CI/HEAD evidence и 12+ содержательных static/regression scenarios, разграничить GitHub-run tests и статические рассуждения. Одна критическая ошибка → CHANGES_REQUIRED, не рекомендовать source merge.

## Write-set and outcome
Читать source PR #372, не менять его. Единственный разрешённый файл: reviews/worker_reports/director-pr372-consent-gate-independent-l3-qa-01.md в одном новом report-only DRAFT PR. Нельзя изменять Board, registry, source, scripts, workflows, исходный report, реальные semantic/production/recovery operations, либо принимать PR самому.

Итог: PASS_FOR_DIRECTOR_MERGE_REVIEW / CHANGES_REQUIRED / BLOCKED_EVIDENCE, live source HEAD, risk QA findings, required exact-HEAD CI, one next actor. При PASS директор сразу выполняет допустимый user-approved HEAD-bound source merge, без второго вопроса. После принятия source PR передаёт отдельную bounded реализацию долговечного closeout/recovery по PR #380 и QA #382, не считает её готовой.
