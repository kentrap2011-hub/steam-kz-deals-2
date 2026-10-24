# ЧАТ 1 — Dossier V2: существующий механизм запуска vs новый issuer

Repository: kentrap2011-hub/steam-kz-deals-2
Canonical source: main
Task ID: dossier-v2-original-run-issuer-reuse-01
Worker slot: НОВЫЙ ЧАТ 1
Deliverable: один bounded report + опциональный маленький inactive code draft PR (если действительно безопасно)

## Вопрос пользователя — главный принцип задачи

«Мы уже запускали новый Dossier: почему опять надо придумывать механизм?»
**Не проектировать новый issuer с нуля**, прежде чем не проверено, что действующий в оригинальном эксперименте GitHub Research launch/marker/authorization механизм можно переиспользовать с V2.

## START и входы

Полностью прочитай актуальный CHAT_PROTOCOL.md, исполни START gate и ограниченный architecture preflight. Проверь этот named task, конкретный registry item и только текущий top Board. Роль: worker, не директор.

Используй как доказательную базу ТОЛЬКО:
- доказательства реально использованного запуска Research original 18: sandbox `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`, Research marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, Research feasibility authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`, подтверждаемый Git ancestry и канонические тогдашние source contracts; не полагайся на одни рассказы о запуске.
- ограниченный исторический Research report PR #233, исходные Research scripts/protocol только в части marker/authorization/verified transport;
- новые, уже MERGED inactive V2 PR #239 и #243, V2 контракт и точный блокирующий отчёт PR #261;
- существующий GitHub control-plane owner contract и необходимые V2 tests.
Не повторяй общий Dossier audit, полный read всех старых source files или разбор качества всех 18 пакетов.

## Задача — доказать reuse прежде нового проекта

1. Восстанови **точную цепочку** прошлого настоящего Research запуска: кто/какое событие дал разрешение, какой GitHub объект / branch / marker заморозил 18 игр, какой nonce/parent и подтверждение GitHub до semantic execution, какой actor/transport сохранял результаты. Раздели подтверждённые Git факты и внешнее человеческое разрешение, которое не воспроизводится только из Git. Не притворяйся, что прежний worker имел право выдавать новое V2 разрешение.
2. Сопоставь требования V2 из PR #261 с этой реально работающей цепочкой, по каждому механизму ответь: `REUSE_AS_IS`, `ADAPT_OFFLINE`, `MISSING` или `UNVERIFIED`. Конкретно: immutable 18/six triples, authorization provenance and one-use grant, creator identity/authority, manifest/marker parent/nonce/freeze, confirmation/receipt, replay/duplicate/race protection, create-only, bounded writer. Покажи, что исторические sha/разрешения не служат повторным разрешением.
3. Найди **один** наименьший технический путь reuse без ослабления V2 fail-closed gates и без новой системы/нового CI. При доказанной совместимости и уже существующем праве на изменение inactive offline V2, можно адаптировать одну чистую deterministic функцию либо fixture/test около существующего V2-кода, используя уже принятые тесты. НЕЛЬЗЯ реализовывать реальный runtime issuer, writer, credential validator или approval token без отдельного scope/user authorization. Если любое работающее изменение создаёт новую authority — НЕ кодируй, закончи отчётом `CONTRACT_BLOCKED_REUSE_DECISION`.
4. Дай конкретный вывод: (A) exact reusable mechanism + минимальная offline адаптация; или (B) 1-2 точные неустранимые несовместимости/недостающая внешняя grant authority с наиболее узким следующим контрактным решением. В любом случае не уходи в архитектуру «на будущее» или новый issuer blueprint вместо ответа о reuse.

## Жёсткие запреты

Не запускать semantic Research, Assembly, Deep, Fast, migration, recovery, ingest или production; не создавать новый manifest/marker/nonce, не повторять original 18; не изменять GitHub workflows, settings, new CI/Actions/validators/automation/scheduler/queues/retries. Не отключать существующие проверки. Не менять production, страницы, валюту, Deep/Fast, исходные immutable исторические commit/Research. Не менять Director protocol/registry/Board, PR #232 или чужой draft PR. Никакой самовольной публикации или merge. Любая code правка требует отдельный exact-HEAD independent QA перед приёмкой.

## Результат

Один report в `reviews/worker_reports/dossier-v2-original-run-issuer-reuse-01.md`, один draft PR (report-only либо код + report); точный final HEAD, existing CI, доказательные ссылки на реальные source commits, компактная таблица reuse и **одно** рекомендуемое действие. Не называй simulated/synthetic tests доказательством реальной выдачи V2 полномочий.
