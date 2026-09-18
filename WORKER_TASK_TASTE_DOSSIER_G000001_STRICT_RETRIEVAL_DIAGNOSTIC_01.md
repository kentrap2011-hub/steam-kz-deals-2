# WORKER TASK — TASTE DOSSIER G000001 STRICT RETRIEVAL DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на kentrap2011-hub/steam-kz-deals-2 до любых действий.

Task ID: taste-dossier-g000001-strict-retrieval-diagnostic-01
Mode: READ-ONLY / RECON

## START
Сначала открой актуальный CHAT_PROTOCOL.md из main и выполни START gate.
Затем открой этот task-файл и работай только в его scope.

Прочитай минимально необходимое:
- CHAT_CONTEXT.md
- CURRENT_TASK.md
- PROJECT_ROUTES.md — только Taste dossier route
- config/execution_ownership_contract.json
- config/taste_steam_review_dossier_schema.json
- config/taste_steam_review_dossier_web_evidence_contract.json
- config/taste_steam_review_dossier_worker_prompt.md
- reviews/worker_reports/taste-dossier-russian-multi-source-retrieval-implement-01.md

## Exact live scope
Исследовать только текущую canonical g000001:
1. appid 2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC
2. appid 1000010 — Crown Trick
3. appid 1000360 — Hellish Quart

Актуальный live result пользователя:
- snapshot cc99c7e3…ecc86
- expected g000001
- progress 0/732
- multi-source retrieval был выполнен
- usable Russian item-level records для всей группы получить не удалось
- candidate не опубликован

Перед web-аудитом сверить, что canonical g000001 всё ещё соответствует этим трем item. Если snapshot/group изменился — зафиксировать это и остановиться без реконструкции старого scope.

## Goal
Найти русскоязычный player feedback по каждой из трех игр, применяя ВСЕ действующие production-правила, и для каждого реально найденного кандидата показать:
- usable или rejected;
- если rejected — первое конкретное production-ограничение, которое делает его unusable;
- какой exact canonical rule/contract field вызывает rejection;
- можно ли устранить проблему только лучшим retrieval или требуется изменить contract.

Это диагностический trace действующих ограничений, а не implementation.

## Web research
Проведи thorough but bounded public-web audit.

Максимум на игру:
- 12 web-search queries;
- 30 opened/read pages.

Это diagnostic budget, не изменение production limits.

Разрешены разные public player-feedback surfaces: Steam, Steam Community, Reddit, форумы, публичные user-review площадки, community discussions, Pikabu/аналогичные UGC surfaces и другие доступные публичные источники.

Не ограничивайся Steam.

## Candidate ledger
Для каждого найденного потенциального Russian/mixed player-feedback lead зафиксируй компактно:
- game/appid;
- source/domain/surface class;
- direct URL или locator, если найден;
- exact-product relation;
- player-generated yes/no;
- Russian/mixed yes/no;
- item-level attributable locator yes/no;
- production verdict: usable / rejected;
- FIRST rejection reason;
- canonical rule/field responsible;
- whether rejection appears:
  - retrieval limitation,
  - evidence-contract limitation,
  - identity limitation,
  - privacy/provenance limitation,
  - temporal/language limitation,
  - other.

Не сохраняй usernames, display names, raw review/post bodies или длинные цитаты. Нужен provenance/diagnostic trace, а не архив контента.

## Important comparison questions
Для каждой игры ответь:
1. Русскоязычный player feedback вообще найден?
2. Найдены ли конкретные item-level сообщения/отзывы?
3. Какое правило чаще всего превращает найденное в unusable?
4. Есть ли хотя бы один случай, когда материал выглядит фактически достаточным для нашей цели, но contract его запрещает?
5. Если бы изменить ровно ОДНО правило, какое изменение разблокировало бы больше всего реально найденных leads?
Не предлагай менять правило, если проблема решается нормальным retrieval.

## No implementation
Запрещено:
- менять schema/contract/prompt/validator;
- менять PROJECT_DECISIONS;
- менять production state;
- публиковать dossier candidate;
- запускать Scheduled Task Run now;
- менять settings Scheduled Task;
- создавать retry/healing logic.

Разрешено изменить только durable report.

## Durable report
Путь:
reviews/worker_reports/taste-dossier-g000001-strict-retrieval-diagnostic-01.md

Report должен содержать:
1. Task / exact scope / snapshot.
2. Search budget actually used per game.
3. Compact candidate ledger.
4. Per-game classification.
5. Top blocking production constraints ranked by number of rejected real leads.
6. Which blockers are retrieval-only vs contract-caused.
7. One minimal contract-change candidate ONLY if evidence proves a contract rule is the blocker; otherwise say none.
8. Unresolved.
9. Status: complete / blocked / needs_user_decision.
10. Exactly one recommended next step: compare with the open-discovery control report; no implementation yet.
11. Efficiency / reusable lesson.

Commit report to main before declaring complete.

CURRENT_TASK.md не менять.
