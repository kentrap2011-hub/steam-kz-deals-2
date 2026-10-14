# ЧАТ 2 — Dossier Research→Assembly: первый реальный пилот 18 игр, gate ручного запуска

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: dossier-shadow-18-first-real-launch-gate-01
Worker slot: НОВЫЙ физический ЧАТ 2
Mode: READ-ONLY / ACCEPTANCE; допускается только отдельный report-only PR
Report: reviews/worker_reports/dossier-shadow-18-first-real-launch-gate-01.md

## START
Полностью прочитай актуальный main/CHAT_PROTOCOL.md и выполни START gate. Далее CHAT_CONTEXT.md, релевантный Dossier-маршрут PROJECT_ROUTES.md, CURRENT_TASK.md (только relevant section), config/execution_ownership_contract.json, config/dossier_shadow_research_trial_contract_v1.json, принятый отчёт reviews/worker_reports/dossier-shadow-first-18-publish-github-frozen-research-authority-01.md, исходный WORKER_TASK_DOSSIER_SHADOW_FIRST_18_PUBLISH_GITHUB_FROZEN_RESEARCH_AUTHORITY_01.md, текущий .github/workflows/publish-dossier-shadow-research-freeze.yml и только нужные строгие sandbox helpers/negative regressions. Работай только в указанном репозитории; если инструмент открыл другой — переключись до чтения/работы.

## Конкретная цель
Продвинуть новый двухэтапный Dossier к первым реальным Research→Assembly на уже согласованных **6 исторических группах [3,8,13,15,18,20], всего 18 точных игр**, без пересечения с ЧАТ 1, который реализует Deep history cards/statistics. Принятая ранее GitHub-only manual-once publication implementation (PR #218) находится в main. Установи, что **точно требуется для первого безопасного одноразового GitHub Actions dispatch** текущего publisher и дальнейшего отдельного семантического запуска. Не делай новый общий аудит Dossier, не пересматривай выбранные игры/старые источники/релизные годы и не повторяй уже доказанные offline QA.

## Acceptance checklist (bounded, факты / no guess)
1. Подтверди актуальное существование либо отсутствие *настоящей* sandbox branch `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`; отличай настоящий GitHub marker+buffer от disposable test fixtures, stdout proposal и reports. Если ветка уже появилась, проверь её исходный immutable buffer/marker lineage без повторного publish.
2. Сверь на текущем main разрешённость строго `workflow_dispatch` для `Publish frozen Dossier 18 Research trial (manual, once)`, точные required input names/confirmation/expected-main-SHA, неизменную группу 6×3 и allowlisted sandbox-only paths. Учитывай, что main может меняться независимо из-за ЧАТ 1; ожидаемый SHA нужно вычислять **непосредственно перед** реальным ручным запуском, не фиксировать текущий как обещанный будущий.
3. Проверь только *ещё не доказанные* существенные технические преграды к успешной publication, используя уже имеющиеся PR-only tests/CI/proven receipts; не проверяй вновь исторические Dossier даты, 114 источников и старые release-year claims. Если обнаружится конкретная новая проблема — точная причина и минимальный future fix; не расширяй read-only задание в изменение runtime.
4. Создай краткую практическую директорскую **GO/NO-GO карточку**: (a) один конкретный шаг вручную опубликовать GitHub buffer/marker без semantics, (b) проверяемые output SHA/marker-parent/18 frozen bindings, (c) что после publication остаётся заблокировано до независимых назначений/правил A/B рецензентов + C adjudicator и отдельного согласования sandbox-only семантики, (d) следующий owner/step. Не путай GitHub publisher с автоматическим включением Research или двухэтапного Dossier.
5. На текущем main/ЧАТ 1 исключи write collisions: никаких `web/**`, `scripts/progressive_personalization.py`, `config/progressive_pass2_contract.json`, `data/production/**`, `data/cache/**`, `data/ai_inbox/**`, `data/control/**` и общего `CURRENT_TASK.md`; никаких изменений ranking, Fast, Deep, visual feed или site statuses.
6. **Не выполняй** manual publisher, не нажимай GitHub Actions dispatch, не создавай реальный marker/branch, не вызывай Research/Assembly semantic workers, не создавай/меняй Scheduled Tasks, не включай inactive production contracts, не делай recovery/retries и не меняй очереди. Существующая пользовательская просьба о параллельном продвижении Dossier не является полномочием на этот отдельный одноразовый live control-plane dispatch.

## Done / deliverable
Сохрани компактный report reviews/worker_reports/dossier-shadow-18-first-real-launch-gate-01.md в **изолированном report-only PR**, без самослияния. Укажи проверенные GitHub refs, readiness и точный единственный следующий директорский шаг. Если настоящий frozen marker уже существует, отрази именно актуальную реальность, не запускай повторную публикацию. Stop after report; no further user prompt required until Director review.
