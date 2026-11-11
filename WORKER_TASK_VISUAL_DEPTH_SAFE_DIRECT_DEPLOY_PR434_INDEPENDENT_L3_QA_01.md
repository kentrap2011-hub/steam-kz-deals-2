# НОВЫЙ ЧАТ 3 — независимая L3 проверка исправления ночной публикации сайта PR №434

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: visual-depth-safe-direct-deploy-pr434-independent-l3-qa-01
Assigned worker: НОВЫЙ физический ЧАТ 3
Mode: independent READ-ONLY L3 QA, one REPORT-ONLY draft PR
Required report: reviews/worker_reports/visual-depth-safe-direct-deploy-pr434-independent-l3-qa-01.md

## START и границы
Сначала полностью прочитай актуальный CHAT_PROTOCOL.md из main, выполни START gate. Затем полностью прочитай этот task, релевантные CHAT_CONTEXT.md, PROJECT_ROUTES.md, PROJECT_DECISIONS.md и архитектурный preflight для GitHub Pages (config/execution_ownership_contract.json, config/daily_execution_contract.json, config/site_publication_resilience_contract.json). Не просматривай unrelated Dossier V1/V2, каталог, исторические Steam процессы.

Только repository kentrap2011-hub/steam-kz-deals-2; другой repo не искать, не читать, не использовать, не менять. Если GitHub tool выбрал другой repo, прекрати и исправь target.

Пользователь разрешил независимую ПРОВЕРКУ, не source IMPLEMENT/merge/deploy. Допустимы чтение PR/GitHub workflows/logs, GitHub Actions уже завершённых запусков и безопасные disposable offline тесты. Единственная запись — новый файл данного отчёта в одном REPORT-ONLY draft PR. Нельзя изменять исходный PR, ни один код/workflow/тесты/config/cache/prod/registry/Board/CURRENT_TASK, запускать GitHub Actions dispatch/rerun, Steam collector, Pages deploy, Scheduled Tasks, semantic worker, открывать новый implementation PR или сливать PR.

## Проверяемая база
- Source PR №434: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/434; первоначально проверенный HEAD `25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43`. Перед каждым вердиктом возьми свежий HEAD и exact current changed-files; при drift сравни delta, не объявляй прежние checks достаточными.
- Исходный RECON PR №433: отчёт reviews/worker_reports/site-nov11-83-vs-100-pages-deploy-recon-01.md, открыт, report-only. Вывод: 4-й workflow_run не создаётся в ночной цепочке; старый JSON 100 минус 17 завершённых скидок = 83; позднее успешно загруженная новая сотня не доказывает автоматический nightly path. Это не permission для нового source fix.
- Source implementation report в PR №434: reviews/worker_reports/visual-depth-safe-direct-pages-dispatch-implement-01.md. Source write-set на момент назначения: .github/workflows/build-daily-visual-payload.yml, .github/workflows/deploy-visual.yml, .github/workflows/validate-execution-ownership.yml, scripts/visual_deploy_dispatch.py, scripts/test_visual_deploy_dispatch.py, scripts/test_site_publication_resilience.py, PROJECT_DECISIONS.md, PROJECT_ROUTES.md, worker report. Любое дополнительное непонятное изменение выяснить, не замалчивать.
- Source PR exact known HEAD уже имеет SUCCESS: Validate site publication resilience, Validate site deploy isolation (PR only), Validate execution ownership, Validate backlog dispositions, Validate site task registry and page, Validate Progressive PASS 2 core, Validate package purchase value. Всё равно требуется независимый QA и post-merge real run.

## Обязательная независимая проверка
1. Установи точный diff/HEAD, GitHub Actions triggers, job dependency, permissions и chain-depth rationale. Новая прямая visual→Pages workflow_dispatch должна создаваться только после успешного producer job (build или строго разрешённый persisted refresh), из допустимого main/repository; запрещены неверное событие, другой run/attempt, непрошедший job, branch/ref drift и duplicate workflows. Приоритет — доказанная система полномочий, а не удобный обход четвёртого workflow_run.
2. Проверяй изолированный job-local `actions:write` и deploy-side verified original run ID/attempt, GitHub actor/event/repo/main, job success, matching typed immutable freshness receipt, staged bytes vs canonical visual, no-build/degraded distinction. Неподтверждённое происхождение или устаревшие/отсутствующие данные должны fail closed. Не считать сам input dispatch разрешением.
3. Адресные негативные и позитивные варианты: success, producer failed/skipped, missing/altered receipt, wrong repo/branch/main/attempt/event/run, wrong SHA, stale/current drift, allowed persisted deterministic degraded material и forbidden no-build, unexpected concurrency, duplicate entrypoints, status-only trigger, manual/push compatibility и гонка между другим push deploy и normal night. Не объявляй concurrency полностью проверенным без evidence.
4. Проверить, что `workflow_run` visual удалён из подписок deploy, но другое допустимое `workflow_run` для status-only сохранено; `push` и legacy manual не сломаны; .github/workflows/validate-execution-ownership.yml действительно тестирует новый helper и relevant CI, не пустой тест. Риски вокруг GITHUB_TOKEN recursion и 3-hop limitation сохранены в explanation.
5. Сверь exact source HEAD все required CI, test names, содержимое локальных fixtures/positive+negative assertions, partial/degraded paths, реальный отчёт автора. По возможности выполнить offline тесты на точной ревизии без запуска production; если невозможно — NOT_EXECUTED и GitHub CI evidence. Никаких новых реальных публикаций даже для проверки.
6. Решение: PASS_FOR_DIRECTOR_MERGE_REVIEW либо CHANGES_REQUIRED либо BLOCKED, с точными минимальными замечаниями. Даже PASS не равно live production acceptance: нужен merge после директорского gate, а затем нормальный unattended nightly run -> Pages deploy -> live URL readback current 100. Если исправление небезопасно, укажи конкретный test/code path и ожидаемый fix без его реализации.

## STOP / Deliverable
Сохрани ровно один REPORT-ONLY DRAFT PR, содержащий только новый reviews/worker_reports/visual-depth-safe-direct-deploy-pr434-independent-l3-qa-01.md, и выдай точную ссылку и summary директору. Отдельные разделы: exact source HEAD / diff; architectural authority; verified positives/negatives, measured vs static; mandatory exact CI; regression/race risks; verdict + one minimal next step. NO source PR edits, no independent QA auto-merge, no production dispatch or semantic V2 launch.
