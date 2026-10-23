# ЧАТ 4 — сайт: реальная публичная доставка и свежесть

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: pages-live-delivery-freshness-followup-01
Slot: НОВЫЙ ЧАТ 4
Dependency: старый Pages audit report PR #245
Own report: reviews/worker_reports/pages-live-delivery-freshness-followup-01.md
Mode: independent READ-ONLY live readback; one report-only draft PR

Ты — рабочий QA реальной публикации, не директор. Сначала прочитай CHAT_PROTOCOL.md, выполни START gate и ограниченный architecture preflight. Прочитай это зарегистрированное задание из current main, проверь addressed registry entry + top Board. Не повторяй полный аудит PR #245.

Проведи фактическую проверку:
1. Попробуй получить **действительно публичные** HTTP/browser ответы Pages по корню сайта, app.js, data/current.json, data/status.json, data/tasks.json, data/publication-disposition.json. Зафиксируй UTC, HTTP status, содержимое/sha256, размер и cache headers, только если реально наблюдаемы. GitHub-репозиторий, успешный Actions и архив Pages **не являются** публичным HTTP.
2. Найди фактически актуальный Pages artifact и delivery/freshness receipt, сравни с публичными байтами там, где они получены. Различай source Git, artifact, Pages CDN, browser cache/UI, свежесть коммерческих данных и возраст семантического анализа.
3. Проверяй, есть ли доказанный сбой именно доставки/устаревания, а не легитимное сохранение semantic history (`degraded/no_fresh_build`). Отдели факты от предположений. Если CDN недоступен в инструментах, итог LIVE_HTTP_UNVERIFIED; не называй сайт сломанным и не генерируй выдуманные метрики.
4. Подготовь **только короткий report-only draft PR** со статусом LIVE_READBACK_VERIFIED / LIVE_HTTP_UNVERIFIED / CONFIRMED_DELIVERY_PROBLEM, точными наблюдениями и одним рекомендуемым директору следующим действием. Самостоятельно ничего не исправляй.

**Запреты:** никакого Deploy или workflow_dispatch, правок production, Dossier/Deep/Fast/Reviews, новых CI/Actions/валидаторов/автоматизаций или изменений существующих проверок. Не менять отображение рублей на тенге и вообще UI/валюту. Не объединять PR. Не дублировать работу ЧАТА 3.
