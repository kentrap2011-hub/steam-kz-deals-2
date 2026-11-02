# НОВЫЙ ЧАТ 2 — независимая проверка PR #368, Dossier V2

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: dossier-v2-pr368-evidence-guard-l3-qa-01
Worker slot: НОВЫЙ физический ЧАТ 2 (не продолжать прежний завершённый ЧАТ 2).
Mode: independent READ-ONLY focused L3 QA, one DRAFT report-only PR
Report: reviews/worker_reports/dossier-v2-pr368-evidence-guard-l3-qa-01.md

## START
Прочитай CHAT_PROTOCOL.md полностью и выполни START gate, затем этот task, адресные CHAT_CONTEXT.md и PROJECT_ROUTES.md. Работай ТОЛЬКО в указанном репозитории. Не искать, читать, менять или использовать другой репозиторий. При неоднозначном GitHub target сначала переключиться на kentrap2011-hub/steam-kz-deals-2, иначе STOP.

## Доказанная база
Source PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/368
Исходный известный source HEAD: 090ac91386422149264454fff8d3807a83856bfb, перед выводом перечитать точный фактический HEAD и required CI. Исходная branch fix/dossier-v2-assembly-presubmit-evidence-guard-01. Финальный implementation report: reviews/worker_reports/dossier-v2-assembly-presubmit-evidence-quality-guard-01.md. Существующие QA original18: reviews/worker_reports/dossier-v2-real-original18-quality-audit-01.md и dossier-v2-original18-strict-mismatch-targeted-fix-01.md. Уже известно: 14/18 stored isolated sandbox, 4 rejected, production disabled. Не повторять pilot.

## Независимая адресная проверка
1. Зафиксировать точный diff и write-set source PR: ТОЛЬКО config/dossier_two_stage_autonomous_assembly_v2_worker_prompt.md, scripts/test_dossier_research_notes_v2.py и worker-report. Сравнить с действующими V2 Assembly schema, strict validator, prepare_assembly_transport, разрешёнными operation.access enum и prepublication repair contracts. Проверить отсутствие обходов strict, отключённых флагов, runtime/schedule/worker/canonical изменений.
2. Проверить одну обязательную pre-submit проверку worker-а: pinned exact AppID/title/edition/original year, допустимый enum и unknown при реально недоступных review bodies, независимые source player evidence, evidence_role=historical и датированное недавнее current_state для чувствительных к обновлениям утверждений; Research Notes — лишь leads, не verified final; при нехватке поддержки честные assembly_missing_evidence / assembly_semantic_conflict. Никаких вымышленных отзывов/консенсуса/SULFUR 1.0. Сохранить две механические prepublication правки и immutable final submission.
3. Адресные positive/negative cases: AppID 206420-style historical + durable-only FAIL; historical без dated current_state FAIL; historical + current-state valid PASS precheck; 1607130-style access_blocked FAIL; truthful unknown typed incomplete PASS precheck, но не canonical accepted; неверные pinned AppID/title/edition FAIL. Убедиться, что regression fixtures вызывают нужные checks, а не пустой тест. По возможности выполнить только безопасные offline disposable tests, отчётливо отделить actual от static.
4. Exact current source HEAD CI: проверить все required GitHub status checks, не полагаться только на прежние 71/71 offline и 4 успешных checks для первоначального HEAD; если HEAD изменился, рассмотреть конкретную материальную дельту.
5. Не выдавать pre-submit prompt/test за проверку истины внешних источников. Девять независимо непроверенных quality grades из 18, SULFUR pre-1.0 freshness, закрытые review bodies и отсутствие реального semantic validation остаются ограничениями. NO_GO для production, пилотного перепрохождения и Deep.

## Strict security/write-set
Не менять source PR, ни один code/prompt/test, V2 strict schema/validator, frozen original18 submissions, receipts, runtime/ownership/contracts, registry, Board, CURRENT_TASK.md, Actions или Scheduled Tasks. НЕ запускать реальный semantic Research/Assembly, retries/ingest/publish и не выполнять merge source PR. Допустим только один новый report-only draft PR с файлом reviews/worker_reports/dossier-v2-pr368-evidence-guard-l3-qa-01.md. При дефекте указать точное место и нужную локальную правку; не исправлять самому.

## Готовность
Один отчёт: source HEAD, checked files, exact-head CI, протестированные позитивные/негативные случаи (actual/static), scope, остаточный риск, рекомендации, точные ссылки на report-only PR/source PR и один финальный verdict PASS_FOR_DIRECTOR_MERGE_REVIEW / CHANGES_REQUIRED / BLOCKED_EVIDENCE. Без незаслуженного PASS. Если нужен repair, директор получает адресный следующий шаг, но работник не создаёт новую задачу. После сдачи слот ЧАТ 2 свободен; только директор может отдельно принять исходный PR по действительному пользовательскому разрешению и safety gates.
