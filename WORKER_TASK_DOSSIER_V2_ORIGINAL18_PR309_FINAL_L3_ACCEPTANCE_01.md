# ЧАТ 4 — независимая финальная приёмка PR №309 (Dossier V2 original18)

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`
Task ID: `dossier-v2-original18-pr309-final-l3-acceptance-01`
Worker slot: **НОВЫЙ физический ЧАТ 4**
Mode: ONE_SHOT_INDEPENDENT_L3_REVIEW; NO_IMPLEMENTATION; NO_SEMANTIC_EXECUTION

## Зачем
Пользователь 27 октября прямо поручил директору **принять ЧАТ 3 / PR №309**. Разработчик ЧАТ 3 закончил код и отчёт. В силу production-adjacent scoped owner authorization, GitHub Actions и immutable Research/Assembly receipts директорскому merge gate требуется **одна содержательная независимая проверка**. Никакой новый RECON, общая QA цепочка, вторая подготовка, повтор успешных тестов или новая реализация не разрешены.

## Проверяемый результат
PR [№309](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/309), на регистрации HEAD `849cc0353271e5ed0a1e45da91767c482f1f833a`, статус draft, unmerged. ЧАТ 3 worker-report:
`reviews/worker_reports/dossier-v2-original18-real-pilot-end-to-end-route-implement-01.md`.
Код последнего существенного изменения HEAD `46a0ffbe041f9a64f99b7a520067a8866232b0f8`, после него только report/handoff.
Existing GitHub CI run `40462620881`: **68 успешно выполненных целевых тестов** scoped issuer/original18, Research/Assembly Git receipts, existing isolated writer; все обязательные CI на финальном PR HEAD также success. Это *не* реальный Research. Настоящий статус: 0/18, нет sandbox ref и ручного owner GitHub Actions freeze/authorization.

## Единственная узкая проверка
1. Читать `CHAT_PROTOCOL.md`, выполнить START и адресный preflight. Сверить точный PR #309 HEAD, diff, report и уже зелёные CI. **Не перезапускать 68 тестов**, если не найден новый материальный код после проверенного HEAD; report-only SHA не обнуляет кодовую приёмку.
2. Проверить **только** рискованные пути: однократный frozen original18 manifest, owner-authenticated manual freeze/authorization и actor/run proof, отказ при чужом grant/неверном marker/replay, GitHub-scoped create-only Research и отдельные typed Assembly receipts с exact source lineage и non-force push, разделение двух семантических работников, изолированный writer и флаги default false, полный запрет V1/Deep/production activation и публикации за пределы sandbox.
3. Точно проверить, что workflow_dispatch/авторизация требуется **после merge** от аккаунта владельца и worker не заявляет 18/18; никаких фиктивных run receipts. Сравнить exact текущий main и changed workflows/contract с записанным freeze/grant, без новых общих аудитов.
4. Вернуть один чёткий вердикт **PASS_FOR_DIRECTOR_MERGE** либо **CHANGES_REQUIRED** с одним точным основанием и минимальным исправлением в существующем PR №309 (если есть дефект). Разделить: «код безопасен для main в dormant режиме» и «0/18, настоящий запуск не выполнен». PASS означает право директора рассмотреть merge по действующему CI/user grant, а не autorun.
5. Сохранить один `reviews/worker_reports/dossier-v2-original18-pr309-final-l3-acceptance-01.md` в один **report-only PR** или review-comment к №309 с точным HEAD, фактами и вердиктом. Нет права редактировать №309, `main`, shared director files, schedules/workflows, production, sandbox; не создавать CI или дополнительную цепочку QA.

## Completion
В отчёте: `verified_head`, `existing_checks`, конкретные L3 safeguards, `PASS_FOR_DIRECTOR_MERGE | CHANGES_REQUIRED`, genuine-run status `0/18` unless actual authenticated evidence disproves, exact remaining owner GitHub Actions manual UI steps after merge. Директор затем принимает решение, а не создаёт следующий общий аудит.
