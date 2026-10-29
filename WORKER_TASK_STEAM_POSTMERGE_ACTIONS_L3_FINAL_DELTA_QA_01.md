# ЧАТ 1 — независимая финальная проверка трёх исправлений Steam

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: steam-postmerge-actions-l3-final-delta-qa-01
Physical worker: НОВЫЙ ЧАТ 1 (отдельный диалог от завершённого ЧАТА 1 — governance implementation).
Role: independent narrow L3 delta QA; ONE report-only draft PR.
Report path: reviews/worker_reports/steam-postmerge-actions-l3-final-delta-qa-01.md

Сначала полностью прочитай актуальный CHAT_PROTOCOL.md, выполни START gate, затем данный task и необходимые актуальные Steam mailing/metadata/eligibility/offer-family/ownership contracts и exact reference reports. Работай только в указанном репозитории.

## Исходные доказательства / scope
- Исходный implementation PR #346: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/346 , branch fix/steam-postmerge-actions-failures-01 ; последний известный HEAD 8619ad1dfcd88ea203f6d7e732f335e3597767db. Независимо пересчитать АКТУАЛЬНЫЙ HEAD, mergeability и обязательные GitHub CI. Не считать результат CI автоматическим security verdict.
- Независимый предыдущий L3 QA: PR #349, reviews/worker_reports/steam-postmerge-actions-failures-final-l3-qa-01.md. Его CHANGES_REQUIRED относится к прошлому source HEAD 8df383752da1b119742702767d780a00580a18a5. Не повторять его уже пройденные проверки вне новой дельты.
- Целевой repair отчёт ЧАТА 4 в ТОМ ЖЕ source PR #346: reviews/worker_reports/steam-postmerge-actions-l3-targeted-repair-01.md. Изменения только CR-1 / CR-2 / CR-3.

## Обязательная независимая L3 дельта
1. CR-1: проверки реальной идентичности метаданных до cache reuse, eligibility classification и family/price consumption. Доказать fail-closed для App_2 со steam_id=999, wrong key/type; корректно различать Sub_456 steam_id=456 и representative mailing appid=2. Проверить точные producer/consumer вызовы, отсутствие обхода валидатора в альтернативных ветках.
2. CR-2: при чтении family ОБА метаданные и eligibility обязаны соответствовать живому HEAD blob SHA data/cache/taste_fit.index.json, помимо взаимного равенства. Негативный кейс: оба frozen/index A, а текущий HEAD index B. Проверить корректную Git provenance и точку read boundary; отсутствие беззвучного fallback.
3. CR-3: диагностический stage 12 требует eligible + excluded == число current-feed INCLUDE, НЕ исторические 101. Проверить нулевые unresolved, полное покрытие, исторические-only записи и динамические данные (ранее observed: 703 current offers, 101 historical INCLUDE, 34 current INCLUDE, 67 historical-only).
4. Подтвердить сохранность уже принятой части прошлого QA: текущая mailing scope, корректность AppID, никакого синтетического price, fail-closed policy/profile SHA, отсутствие удаления устаревших исторических решений. Не расширять аудит на collector / сайт / новые функции.
5. Инспектировать существующие изменения и негативные тесты в исходном PR, exact final source HEAD и все применимые существующие PR CI. GREEN PR tests не доказывают end-to-end production live collection, publish/deploy; это отдельный postmerge gate.

## Выход / запреты
Создай только ОДИН report-only draft PR с файлом reviews/worker_reports/steam-postmerge-actions-l3-final-delta-qa-01.md, конкретным verdict PASS_FOR_DIRECTOR_MERGE либо CHANGES_REQUIRED/BLOCKED_EVIDENCE. Директор сам принимает source PR #346 при PASS и green exact-HEAD CI; если обнаружен реально новый дефект, дать минимальную правку В ТОМ ЖЕ source PR #346 без другого implementation PR. Никаких правок исходного PR самим QA, никаких ручных production Actions/semantics, scheduler, queue, retries, recovery, новых workflow или merge. Другой полный аудит и повторная QA неизменённой части запрещены.
