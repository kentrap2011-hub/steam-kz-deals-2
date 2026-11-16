# НОВЫЙ ЧАТ 2 — повторный независимый аудит качества Research V2 на шести играх

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: dossier-v2-fresh6-rerun1-research-reaudit-evidence-01
Assigned: ОТЛОЖЕНО пользователем 2026-11-16; прежняя резервация ЧАТА 2 снята; worker_slot=null.
Mode: READ-ONLY / RECON — независимое содержательное QA, один report-only DRAFT PR.

## START и обязательный evidence gate
Сначала прочитай CHAT_PROTOCOL.md из main и полностью выполни START gate. Затем прочитай этот task, CHAT_CONTEXT.md и обязательно config/dossier_research_independent_quality_audit_protocol.md, внедрённый PR #458; адресно проверь PROJECT_ROUTES.md, релевантный PITFALL-009 в KNOWN_WORKER_PITFALLS.md и действующий Research V2 contract/schema.
Работай ТОЛЬКО в kentrap2011-hub/steam-kz-deals-2; другие GitHub репозитории не читать, не искать и не использовать. Если GitHub connector указывает другой repo — STOP.

Разрешение пользователя на повторный аудит уже дано; это не новое разрешение на семантическое исполнение/публикацию или Assembly. ЧАТ 2 разработчика протокола свою задачу завершил. Выполни независимую переоценку Research без полагания на прежние 4 QUALITY_GOOD / 2 QUALITY_WEAK в #456: этот старый вывод дезавуирован, потому что независимого посещения страниц не было.

## Frozen scope
Единственная партия: dossier-notes-v2-fresh6-20261114-rerun1
Ветка: sandbox/dossier-notes-v2-fresh6-20261114-rerun1
Manifest: data/control/dossier_notes_v2/manifests/dossier-notes-v2-fresh6-20261114-rerun1.json
Source candidate JSON: data/ai_inbox/dossier_notes_v2/dossier-notes-v2-fresh6-20261114-rerun1/
Typed Research receipts: data/control/dossier_notes_v2/receipts/dossier-notes-v2-fresh6-20261114-rerun1/
Строго в порядке манифеста: 1000010 Crown Trick; 102600 Orcs Must Die!; 1029690 Sniper Elite 5; 49520 Borderlands 2; 499180 Braid, Anniversary Edition; 501590 Bulletstorm: Full Clip Edition.
Фиксируй source sandbox HEAD и blob привязки в начале. Никаких самостоятельно выбранных/заменённых игр или иных изданий.

## Реальная независимая проверка всех шести
1. Из frozen manifest установи точные AppID и edition. СНАЧАЛА используй настоящие веб-инструменты для независимого поиска, ОТКРЫТИЯ и чтения соответствующих внешних материалов по каждой игре/изданию. Не ограничивайся одной поисковой выдачей или чужими ссылками. Зафиксируй подтверждаемые факты/сомнения до прочтения Research notes и старого QA #456. Не выдумывай вызов инструмента, полученный контент или его дату.
2. Затем считай каждый оригинальный candidate JSON (notes_text, unknowns_text, conflicts_text, source_log, research_status) и technical receipt через GitHub. Сопоставь с самостоятельно полученными веб-данными. URL в Research source_log не является свидетельством аудиторского открытия страницы.
3. Для существенных Research claims явно покажи evidence chain: claim → доступный точный URL → класс источника + реально прочитанный фрагмент и контекст → CONFIRMED/UNCERTAIN/UNKNOWN → влияние на оценку. Search snippet/search_result_only/blocked/unavailable никогда не свидетельствуют о чтении страницы и не позволяют писать CONFIRMED. Для каждого CONFIRMED должно быть фактическое открытие и релевантное чтение в ТЕКУЩЕЙ сессии.
4. Полнота для каждой игры: основные механики; solo/co-op и другие режимы; оригинал vs edition/remaster/DLC; опыт игроков (не только маркетинговые описания); плюсы, минусы, проблемы и важные пропуски; жалобы привязывать к дате, платформе и версии. Не выдавать одиночные отзывы за массовую частоту, не смешивать игру с продолжением. Исторические PC/console баги не обобщать без достаточной базы.
5. Применить обязательный per-game Evidence Gate ДО финального суждения: QUALITY_GOOD (подтверждено ключевое и нет существенного пробела), QUALITY_WEAK (фактически выявлены существенные пробелы/неточности), BLOCKED_EVIDENCE (нет настоящих подтверждений для независимого суждения). Не использовать предыдущий рейтинг 4/2 в качестве исходного вывода. При недоступности внешнего веб-доступа остановиться честно, не публикуя фиктивные подтверждения. Без искусственных численных квот по URL/отзывам.
6. Дать один обоснованный общий вердикт и указать, какие конкретные игры нуждаются в исправлении содержания до Assembly, а какие годятся как непроверенные leads для отдельно разрешённого Assembly. Указывать неопределённости и неточности, не подменять аудит повторным Research.

## Write-set / запреты / результат
Единственная разрешённая запись — отчёт:
reviews/worker_reports/dossier-v2-fresh6-rerun1-research-reaudit-evidence-01.md
в отдельном одном report-only DRAFT PR к main. В нём — точные manifest/sandbox reference, 6 per-game outcomes, таблица/связки проверяемых открытых внешних источников и утверждений, подтверждение фактических веб-действий с честным access status, существенные пропуски и опасения, итоговый вердикт, блокеры и один bounded next step. Зафиксировать ссылку на report-only PR и exact HEAD; зелёный GitHub CI доказывает техническую публикацию, НЕ независимое чтение внешнего сайта.

Запрещены: правки research candidate/receipt/sandbox, старого PR #456, протокола, source/runtime/contract/schema/workflows, Board/registry, production, canonical ingest, V1/Deep, scheduled tasks, выдача новых grants, Research rerun, Assembly, искусственный retry, запуск Actions, source merge. Не считать эту проверку разрешением на Assembly и не запускать ничего после публикации.

Definition of Done: все шесть независимо проверены по новому каноническому Evidence Gate и опубликован ровно один содержательный отчёт в report-only DRAFT PR; если веб-доступ фактически отсутствует — честный BLOCKED_EVIDENCE. После этого директор принимает решение по конкретным находкам, не разрешая новой semantic стадии автоматически.
## Управленческая остановка (2026-11-16)

Пользователь решил пропустить отдельный аудит и перейти к Assembly. Это задание оставлено для истории, но не авторизовано к запуску при нынешнем решении; прежняя незапущенная резервация физического ЧАТА 2 снята. Не считай этот статус завершённым аудитом или оценкой Research. Новое назначение потребует отдельного указания пользователя.
