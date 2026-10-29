# НОВЫЙ ЧАТ 1 — root cause: 9 rejected Dossier V1 group submissions

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v1-rejected-buffers-exact-product-binding-root-cause-01
Owner: новый физический ЧАТ 1, не прежний исполнитель PR №363.
Role: independent targeted read-only RECON. Single report-only DRAFT PR.
Report: reviews/worker_reports/dossier-v1-rejected-buffers-exact-product-binding-root-cause-01.md

## START
Полностью прочитай CHAT_PROTOCOL.md и выполни START gate, затем этот task, CHAT_CONTEXT.md и нужные sections PROJECT_ROUTES.md, PROJECT_DECISIONS.md, KNOWN_WORKER_PITFALLS.md, execution ownership. Адресно исследуй V1 canonical runtime/worker/identity, strict GitHub writer/validator, schema и web evidence contracts; не пересоздавай semantic работу и не делай широкий аудит.

## Подтверждённый сбой (2026-10-29)
Второй вручную авторизованный Dossier V1 one-shot сделал marker commit `ee3c65b81687c49df00df838dec317e9b395efc7` (11:56:56 UTC) и последовательно опубликовал 9 frozen групп (по 3 игры), snapshot `d20d3109fc28b00f0658697a77abecf717678fd614cdbc9b13afc961554c8e69`. GitHub канонически отклонил ВСЕ 9 (12:06–12:36 UTC), 0 accepted. Журнал `data/audit/taste_steam_review_dossier_transport_rejections.jsonl` подтверждает ошибки `provenance.sources[N].exact_product_binding`: группы 1–5,7–8 source_appid mismatch; 6,9 title/release mismatch. Предыдущее отклонение group 1 по `evidence_languages` случилось в более раннем запуске: не смешивать с новым. Все исходные candidate JSON теперь в `data/quarantine/taste_steam_review_dossier_inbox/retryable_transport/...`. GitHub Dossier worker index показывает `accepted_group_count=0`, `pending_group_count=200`, `accepted_dossier_count=0`; Deep подготовил 0 items. Отсутствие коммитов после group 9 не доказывает UI зависание.

## Узкие задачи
1. Независимо проверь реальную точную последовательность 9 candidate commits → автоматический GitHub drain → rejection entries → quarantined immutable artifacts → отсутствие canonical acceptance и Deep work. Укажи timestamps, marker parent, immutable snapshot и exact source file URLs. Отдели подготовленную semantic работу (27 досье) от результата, принятого GitHub (0). Проверь, есть ли доказательство о причине остановки после group 9; не выдумывай timeout.
2. Разбери на фактах 2–3 representative artifacts: group 1/2/7 для source_appid и group 6/9 для title/release. В каждом соотнеси exact `provenance.sources[index].exact_product_binding`, истинный источник и URL, canonical game identity/title/year/appid и fail-closed validator rule. Не делай вывод по одному корректному source, если другой source в том же candidate нарушает identity.
3. Найди конкретную причинную границу: где worker prompt требует / вырабатывает binding, кто serializes candidate, как GitHub validator сравнивает его с реально замороженным source identity. Различи подтверждённый malformed generated data, возможный validator mismatch и недоказанные причины. Если нельзя доказать из GitHub статически, `BLOCKED_EVIDENCE` с одной точной проверкой, не ослабляй защиту.
4. Определи, как GitHub-owned канонический recovery может или не может законно обработать отклонённые группы: нужен ли свежий user launch, marker или authorization. Только анализ, **НИКАКИХ** retry, replay, recovery, overwrite, rename, alternate path, повторной публикации или реального semantic run. Почему Deep не видит игры: Dossier buffered/submitted != GitHub accepted.
5. Рекомендуй ОДНО bounded исправление только при доказанной причине: точный владелец, files, минимальное semantic/serializer/validator изменение без weakened strict checks, позитивные/отрицательные offline fixture regression, L2/L3 risk and independent QA, rollback и безопасный отдельно разрешаемый next-run. Не плодить общие аудиты, схемы авторизации и новые очереди. Dossier V2 original18 — отдельная inactive sandbox линия с NO_GO audit #324 и targeted audit #331; не переводить V1 в V2 автоматически.

## Report and prohibitions
Единственный разрешённый write: новый `reviews/worker_reports/dossier-v1-rejected-buffers-exact-product-binding-root-cause-01.md` в отдельном DRAFT report-only PR. Никаких source/workflow/schema/contract/Board/registry/CI, production, Scheduled Tasks, manual Dossier or Deep workers, marker, no source PR merge. Итог: 9-group rejection matrix + sample exact mismatch, доказанная/ограниченная root cause, временные метки, boundary submitted-vs-accepted, ОДИН implementation plan, verdict `DIAGNOSIS_COMPLETE` / `BLOCKED_EVIDENCE`. Директор принимает решение сам.
