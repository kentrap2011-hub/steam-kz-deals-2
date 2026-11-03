# НОВЫЙ ЧАТ 3 — независимая L3 QA исправления Steam DLC

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: steam-targeted-dlc-pr388-independent-l3-qa-01
Physical worker: НОВЫЙ ЧАТ 3
Mode: independent scoped L3 source QA; report-only DRAFT PR
Report: reviews/worker_reports/steam-targeted-dlc-pr388-independent-l3-qa-01.md

## START
Полностью прочитай CHAT_PROTOCOL.md из main и выполни START gate. Затем полностью прочитай этот task, адресные CHAT_CONTEXT.md, PROJECT_ROUTES.md, ownership/paid-discovery/freshness contracts и source PR #388. Работай только в указанном репозитории. В начале сверяй LIVE HEAD исходного PR #388 (последний известный `b03ea8197ca106829cb0d58b1caf05a9bf5b0c6d`), точный diff и историю GitHub Actions; не используй старые HEAD как доказательство.

## Задача
ЧАТ 2 уже разработал и протестировал исправление DLC в source PR #388. Не повторяй разработку или широкий RECON, а проведи содержательную независимую проверку рискованной кодовой дельты. Production incident: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41362591621 — parent AppID 239140 останавливал сборщик ошибкой `DLC relationship contains duplicates/invalid identities`. Нельзя заявлять, что ошибка была именно в дубликатах: лог не сохранял сырой DLC-массив. Следом https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41498105517 pre-AI fail на устаревших discovery и не дошёл до автоматической очереди Dossier.

## Независимая проверка
1. Прочитай ровно source PR #388 diff, worker report `reviews/worker_reports/steam-targeted-dlc-identity-blocker-restore-auto-dossier-01.md`, source `scripts/steam_targeted_paid_lanes.py`, tests `scripts/test_steam_targeted_paid_lanes.py` и адресный entrypoint collector; проверь архитектурное соответствие existing GitHub-owned pipeline и отсутствие изменения scope/retry/ownership.
2. Проверить на реальных code paths: только canonical positive integer / ASCII decimal AppID; bool, float, zero, negatives, leading zeros, Unicode, malformed list, absent/bad parent; проверка `steam_appid` и `fullgame`; duplicate exact membership vs malformed identity; cross-parent shared DLC; dedup price lookup; fetch/429 failures; non-DLC filtering; KZT price, percent gates; deterministic sorted ordering; bounded workers. Искать неохваченные позитивные/негативные случаи и accidental fail-open/fail-closed, привести конкретные source-grounded контрпримеры при дефектах.
3. Точно проверить обязательный GitHub CI на live source HEAD: `regression`, `validate`, `backlog-disposition`. `collect: skipped` в PR pipeline намеренный; это не настоящая production QA. Не объявлять успешным восстановление Dossier от одного source CI.
4. Проверить, что изменения не редактируют generated worker index, freshness cutoff, schedule, semantic/recovery/production, не вводят новый queue/runner; не предпринимать никакого реального запуска GitHub Actions или Dossier. Свежая автоматически подготовленная очередь после будущего штатного production цикла — отдельная пост-merge проверка.
5. Verdict `PASS_FOR_DIRECTOR_MERGE_REVIEW`, `CHANGES_REQUIRED` либо `BLOCKED_EVIDENCE`. При PASS предоставить exact HEAD, проверенный scope/CI и узкие оставшиеся ограничения. При CHANGES_REQUIRED — конкретные правки уже существующего source PR #388 для того же разработчика, НЕ новый source PR. Один следующий actor: Директор после PASS применяет exact-head CI/QA/mergeability/permission и принимает уже согласованный IMPLEMENT без второго вопроса. После source-merge проверить штатный GitHub production→pre-AI, а не вручную готовить Dossier.

## Write-set и запреты
Разрешён только `reviews/worker_reports/steam-targeted-dlc-pr388-independent-l3-qa-01.md` в одном НОВОМ report-only DRAFT PR. Никаких изменений исходного source PR, кода, CURRENT_TASK, Board, registry, рабочих процессов, Scheduled Tasks, production, semantic Dossier/Deep, retry, никаких self-merges. Не требовать новый QA-чат для отчёта этой QA. Заверши задачу в этой беседе итоговым отчётом, подтверждённым URL и verdict.
