# ЧАТ 1 — Независимая L3-проверка нового исправления Dossier V1

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v1-pr322-sequential-frozen-outcome-final-l3-delta-qa-01
Worker: НОВЫЙ физический ЧАТ 1; independent report-only L3 QA.

Сначала полностью прочитай CHAT_PROTOCOL.md из main, выполни START gate, затем данное задание и только релевантные Dossier V1 frozen/ownership contracts. Только указанный репозиторий.

Проверить источник — существующий draft PR №322, branch implement/dossier-v1-manual-one-shot-authorization-01, известный HEAD af4d4b79472c1317f526ae4c4cc269845a294905 (перепроверить live HEAD). Отчёт независимой проверки №339 зафиксировал дефект последовательных opposite frozen old-group outcomes, после чего ЧАТ 4 исправил его внутри PR №322 и сообщил в reviews/worker_reports/dossier-v1-explicit-manual-one-shot-authorization-01.md.

Только независимая проверка материальной L3-02 поправки; использовать принятые результаты L3-01, не повторять полный аудит. Проверить candidate→drain→terminal→drain и terminal→drain→candidate→drain через различные marker parents одной immutable group, consumption audit по exact group, отсутствие потери уже успешно разобранного обзора, отсутствие ошибочного начисления попыток, sibling progression, повторные прочтения и законные более новые успешные разборы. Проверь регрессии, точный HEAD, реальные CI; не объявлять успех только из-за зелёной проверки. Не менять source PR, contracts, schedules, production/семантику. Один report-only DRAFT PR, путь reviews/worker_reports/dossier-v1-pr322-sequential-frozen-outcome-final-l3-delta-qa-01.md, verdict PASS_FOR_DIRECTOR_MERGE или CHANGES_REQUIRED.
