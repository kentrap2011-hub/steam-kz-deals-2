# НОВЫЙ ЧАТ 2 — независимая финальная L3 delta QA ручного Dossier V1

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v1-manual-postgroup-stop-final-l3-delta-qa-01
Worker: НОВЫЙ физический ЧАТ 2, не разработчик исходного PR #358. One report-only DRAFT PR.
Report path: reviews/worker_reports/dossier-v1-manual-postgroup-stop-final-l3-delta-qa-01.md

Сначала полностью прочитай CHAT_PROTOCOL.md, выполни START gate, затем этот task, исходный PR #358, reviews/worker_reports/dossier-v1-manual-postgroup-stop-gate-01.md и необходимые manual launcher, shared runtime, worker, evidence, terminal receipt, frozen marker/descriptor и execution ownership contracts. Работай только в указанном репозитории.

Исходный draft PR #358, branch fix/dossier-v1-manual-postgroup-stop-gate-01; последний проверенный HEAD bff8278c74d971238a9f792a2bfb155b93c66656. Проверить live HEAD/mergeability/diff/CI самостоятельно. Проверяется только новая manual one-shot launcher delta из config/taste_steam_review_dossier_manual_one_shot_prompt.md; source PR должен менять лишь launcher и исходный worker report. НЕТ повторного общего аудита.

Проверки:
1. После successful create-only publication frozen group, в том числе №1, следующую группу выбирать из неизменного marker-parent pending list, а не из mutable main; при безопасной возможности до финального ответа попытаться connected GitHub read точного следующего frozen group descriptor на фактическом immutable Git parent. Ни второй marker, ни sibling ingest ожидание, ни новая семантическая квота.
2. Корректные fail-closed stops: no next pending; marker invalid; descriptor/binding mismatch; exact create-only collision; confirmed tool error; реально подтверждённая runtime budget stop. Без доказанной причины и без попытки next descriptor окончание должно обозначать violation/not_established, НЕ successful completion. Нельзя выдумывать timeout, контекстный лимит и acceptance.
3. Изменение не должно принуждать к unsafe continuation при реальной ошибке, создавать retry, recovery, альтернативный буфер/путь, schedule или новые permission. GitHub остаётся владельцем frozen list, canonical cache, validation, accepted results, retry/completeness. Candidate published = buffered/submitted, НЕ canonically accepted.
4. Независимо пройти R1–R9 и безопасные статические structural checks source report; документировать только реально сделанное, не имитировать semantic run. Указать, что prompt-gate процедурный, не machine guarantee.
5. Проверить exact-final-source-HEAD CI по Validate execution ownership, Validate site task registry and page, Validate backlog dispositions. Любой mandatory failed/pending/skipped блокирует PASS. Проверить, что shared scheduled runtime, semantic worker, contracts, schemas, GitHub Actions, production state не менялись.

Сдать ОДИН report-only DRAFT PR, только reviews/worker_reports/dossier-v1-manual-postgroup-stop-final-l3-delta-qa-01.md, verdict PASS_FOR_DIRECTOR_MERGE либо CHANGES_REQUIRED/BLOCKED_EVIDENCE с точным source HEAD и фактами. Никаких source PR правок, merge, GitHub production, реального ручного/планового Dossier запуска, markers, retries, очередей, Scheduled Tasks. Директор лично после PASS и точного HEAD/CI проверит и примет source PR #358. Реальный новый ручной запуск Dossier потребует отдельного прямого разрешения пользователя.
