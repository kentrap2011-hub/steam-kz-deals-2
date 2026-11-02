# НОВЫЙ ЧАТ 3 — поправить повторное разрешение на принятие в исходном PR #372
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: director-pr372-no-repeat-approval-implement-01
Slot: НОВЫЙ физический ЧАТ 3 (не старый завершённый исполнитель).
Mode: bounded implement and regression review, update SAME source PR #372.
Report: reviews/worker_reports/director-pr372-no-repeat-approval-implement-01.md

Сначала полностью прочитай CHAT_PROTOCOL.md, выполни START gate; затем этот task, адресные CHAT_CONTEXT.md, PROJECT_ROUTES.md, DIRECTOR_PROTOCOL.md, исходный PR #372 и его report. Работай только в repo kentrap2011-hub/steam-kz-deals-2: другой репозиторий запрещён; при неверном target STOP.

Source PR #372 https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/372 contains report→consent→REGISTER fix. Сохрани его. Пользователь уточнил: уже одобренная bounded IMPLEMENT/QA задача после успешных точных mandatory CI и risk-appropriate независимой QA должна быть принята директором без нового вопроса «принимаем?». Исправь ВНУТРЕННИЕ противоречия active STATUS/DECIDE/REGISTER/MERGE, post-QA closeout и CHAT_PROTOCOL PRE-SEND; не добавляй вторую ledger/approval-модель. Отдельного user approval требуют новая цель или изменённый scope, реальные semantic/retry, production/deploy, Scheduled Tasks, расширение полномочий и high-risk action. Сохрани STOP при красных/pending checks, неподтверждённом HEAD/mergeability, отсутствующей L3 QA, конфликте и отсутствии actor permission.

Проверить минимум 12 сценариев: user одобрил scoped implementation + all gates pass => директор выполняет MERGE без второго запроса; новый diagnosis => спрашивает до REGISTER; отказ => no write; drift/unsafe production => отдельное согласие; QA fail, CI red, stale-head, forbidden scope => fail closed; already-registered => no duplicate. Никаких реальных production/semantic запусков или пробных merge.

Меняй только существующую branch PR #372: DIRECTOR_PROTOCOL.md, CHAT_PROTOCOL.md, reviews/worker_reports/director-pr372-no-repeat-approval-implement-01.md и, если требуется по смыслу, прежний report той же задачи. Не создавай другой source PR, не меняй registry/Board/ownership/source #371/#368, не self-merge. Укажи risk-level изменения consent-logic (не маскируй L3 под L1), необходимость независимой узкой QA, точный final source HEAD и CI, окончательный verdict READY_FOR_NARROW_INDEPENDENT_QA / READY_FOR_DIRECTOR_MERGE_REVIEW / CHANGES_REQUIRED, следующий actor.
