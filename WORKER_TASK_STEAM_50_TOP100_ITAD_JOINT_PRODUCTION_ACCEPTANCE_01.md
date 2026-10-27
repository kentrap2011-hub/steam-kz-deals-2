# ЧАТ 4 — единая независимая приёмка PR #311 и #312

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth / base branch: `main`
Task ID: `steam-50-top100-itad-joint-production-acceptance-01`
Worker slot: НОВЫЙ физический ЧАТ 4
Mode: ONE_BOUNDED_INDEPENDENT_L3_CODE_AND_INTEGRATION_ACCEPTANCE

## Цель

Пользователь разрешил «делаем приёмка, делаем обновление или что требуется что бы завершить». Провести **одну** конечную, независимую, предметную приёмку двух готовых реализаций, чтобы директор мог последовательно принять их и осуществить **один нормальный main production update**, если QA даст PASS. Никакого нового общего аудита или дополнительных проверочных циклов.

- PR #311, начальный exact HEAD `3e9eb3a11eebbced15281ff39b61a99d7447afa4`, draft: скидки >=50%, видимые топ-100, целевые DLC, пакеты, Deep полный scope. Report `reviews/worker_reports/steam-discovery-50-percent-discount-top100-implementation-01.md`.
- PR #312, начальный exact HEAD `21f88f46c12312d054a94832ff5a443a914a9f39`, ready: ITAD Epic/GOG exact ID. Report `reviews/worker_reports/giveaway-itad-identity-implement-01.md`; реальный read-only ITAD proof GitHub Actions run `40359222508`: 2 current Epic→Steam success, GOG historical diagnostic ONLY.
- Оба PR имеют зелёные регрессионные проверки. `collect` на PR пропущен: это не доказательство настоящего normal main refresh.
- **Общий файл**: `scripts/build_final_visual_payload.py` изменён в ОБОИХ PR. #311 добавляет ограничение paid visible-100 только после полного Deep/rank и статистику; #312 прикрепляет verified giveaway identity и существующий анализ. Нельзя потерять одну из этих функций при последовательном merge.

## Точная проверка и завершение

1. Выполнить `CHAT_PROTOCOL.md` START и адресный архитектурный preflight, прочитать эти два worker-report и точные PR diffs/HEAD/CI. Не делать широкий review всего проекта. Сохранить точные новые SHA, если изменились.
2. Для #311 проверить actual code gates: KZ discount >=50%, <=4500 KZT, obscure low-signal с защитой исключительных предложений и неизвестных reviews, exact admitted-base→DLC без глобального DLC crawl, независимый Sub даже с нераспроданными членами, fail-closed и полноту collection, что Deep-очередь не срезается по top-100, видимый cap 100 только после полного анализа/ранга и корректные funnel/Statistics.
3. Для #312 проверить exact Epic offer/GOG product ID→ITAD UUID→один валидный `app/<positive>`; никакой title fallback, прозрачный fail-closed, cache/credentials/attribution, существующий один giveaway writer, только точное переиспользование canonical Steam analysis и безопасную UI-проекцию. Не выдавать 7 live API read-only запросов за завершённую production-публикацию.
4. **Объединённое поведение:** сравнить shared-file diff и возможные merge-конфликты. Проверить, что каппирование до 100 не лишает giveaway нужного уже проанализированного Steam-результата; это может быть существенным конфликтом бизнес-логики даже при бесконфликтном Git merge. При возможности проверить один disposable combined integration tree с узким тестом именно новой комбинации; не менять ни один PR, `main`, production или общие файлы. Не повторять уже успешные отдельные CI/test suites без выявленного пробела.
5. Выдать **по одному** вердикту `PASS_FOR_DIRECTOR_MERGE` / `CHANGES_REQUIRED` для каждого PR и для их совместного результата. При CHANGES_REQUIRED назвать одну конкретную минимальную исправляемую дельту и исполнителя ЧАТ 1/2, без новой цепочки аудитов. При PASS явно передать директору последовательность интеграции PR и один обычный существующий main GitHub Actions collection+site pipeline. Для финального завершения требуется доказать на реальном нормальном обновлении все нужные факты: <=100 текущих KZ скидок >=50%, source completeness, подходящие DLC, независимые пакеты, полный Deep scope, точные ITAD receipts/cache для текущих offer IDs, отсутствие регрессий сайта.
6. Сохранить один отчёт `reviews/worker_reports/steam-50-top100-itad-joint-production-acceptance-01.md` в **одном report-only PR** (или PR review comment с полным долговременным verdict, если возможно). Не создавать второй QA для проверки отчёта.

## Ограничения

Это независимая READ-ONLY приемка, не разработка. Не менять исходники PR 311/312, их branch/HEAD, `scripts/build_final_visual_payload.py`, PR #309 Dossier, production, CI/workflows, permissions, Scheduled Tasks или секреты. Не self-merge, не делать production run. Директор отвечает за объединение и выполнение настоящего normal main update после PASS; если нет GitHub Actions dispatch, указать точные действия в UI, не симулировать запуск. Existing CI green и authenticated ITAD proof переиспользовать. Никаких новых дополнительных аудитов или подготовки вместо завершения.
