# ЧАТ 1 — следующий безопасный компонент Dossier V2

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v2-next-safe-component-01
Worker slot: НОВЫЙ ЧАТ 1
Report: reviews/worker_reports/dossier-v2-next-safe-component-01.md
Mode: evidence-bounded implementation (inactive only) or report-only if a blocker prevents safe implementation

## START

Прочитай актуальный CHAT_PROTOCOL.md и исполни START gate. Проверь этот named task, точную запись registry и верх текущей Board. Выполни bounded architecture preflight: GitHub — единственный control-plane / writer / authority владелец, worker не создаёт новый способ обхода acceptance. Не восстанавливай всю историю и не просматривай огромные старые Board/registry.

## Откуда продолжать

Уже приняты inactive V2 PR #239 и #243. Ветвь V1 / historical PR #232 остаётся CHANGES_REQUIRED и не является текущим рабочим путём. Используй только точный отчёт ЧАТА 1 в PR #243 и independent QA PR #249 плюс необходимые V2 контракты. У них подтверждены оставшиеся отдельные блокеры: trusted prospective run issuer, реальные per-item receipt persistence, независимая authenticated reviewer appointment/lookup, trusted control-plane transport/atomic group writer, source-quality QA. Не рассматривай offline helper как уже работающий runtime.

## Задание

1. Определи **строго один** ближайший технический компонент в текущем GitHub-owned V2, который можно безопасно реализовать отдельно от остальных, не расширяя authority и без изменения схемы исходной 18-игровой очереди. Отчётно привяжи выбор к явному blocker и существующему контракту; не делай новый общий аудит.
2. Если выбранный компонент можно действительно реализовать в *неактивном* пути в пределах existing contracts и тестов — реализуй минимальный bounded change и существующие соответствующие регрессионные тесты. Сдай один draft PR + свой краткий report. Это НЕ активация и НЕ runtime launch. Любой code PR требует отдельного exact-HEAD independent QA перед Director merge.
3. Если не существует безопасной границы для локального изменения без нового решения об issuer/writer authority, выбери статус `CONTRACT_BLOCKED`, подготовь только report-only draft PR с одним конкретным предложением к разрешению; не создавай fake implementation и не проводи полный новый аудит.
4. Для сохранности Evidence: frozen original 18, строгие схемы, provenance, phase boundary, reviewer independence и fail-closed semantics сохраняются. Не объявляй R→A готовым к реальному trial, пока все обязательные блокеры не устранены и пользователь отдельно не разрешил конкретный однократный запуск.

## Запрещено

Любые реальный Research/Assembly, marker/issuer issuance, user approval impersonation, GitHub write в production/canonical, Deploy, scheduler, автоматические retry, новые GitHub Actions/CI/валидаторы или модификации существующих проверок. Не менять Deep, Fast, Steam Reviews, сайт/валюту, DIRECTOR_PROTOCOL, Board/registry, исторический PR #232. Работай только внутри выбранного inactive V2-компонента, своих тестов и отчёта. Если неясен владелец writer, остановись.

## Выход

Точный выбранный blocker, что доказано, что исправлено или CONTRACT_BLOCKED, changed paths, draft PR/HEAD, результаты **существующих** checks, пределы и запрос к отдельному QA.
