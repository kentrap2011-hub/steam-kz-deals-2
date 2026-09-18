# WORKER TASK — TASTE DOSSIER RUSSIAN DISCOVERY AUDIT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-russian-discovery-audit-01`
Mode: `READ / VALIDATE / BOUNDED WEB EVIDENCE AUDIT`

## START gate

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate.
Затем открой этот task-файл из `main` и зафиксируй checklist.

## Why this audit exists

Первый post-SCG live Scheduled Task run остановился до publication `g000001` и сообщил, что в пределах invocation не удалось получить достаточно надёжных attributable item-level русскоязычных feedback records для полного трёхигрового V2-кандидата.

Отдельный acceptance report уже установил:
- partial 3-game group публиковать нельзя;
- отсутствие Russian feedback само по себе не является canonical blocker;
- active contract допускает `searched_not_found_or_insufficient` и `source_access_unavailable`.

Но **ещё не проверено**, действительно ли подходящий Russian-language player feedback отсутствовал/был слишком слабым, либо live worker плохо выполнил discovery.

До исправления worker behavior нужно сначала установить качество самой методики Russian discovery.

## Authoritative live UI result

Используй дословный manual UI-result как authoritative confirmed observed behavior:

> Текущая canonical-проекция обновилась на snapshot `00072072…bd34c` от 18 сентября: ожидается `g000001`, 564 элемента остаются, backlog не завершён.
>
> Для `g000001` выполнена обязательная проверка контрактов и начато evidence-исследование трёх точных элементов: `Baldur's Gate 3 - Digital Deluxe Edition DLC`, `Hellish Quart`, `Tetris® Effect: Connected`. Группа не опубликована: в пределах этой инвокации не удалось получить достаточно надёжных attributable item-level русскоязычных feedback records для полного трёхигрового V2-кандидата. По контракту неполную группу публиковать нельзя, поэтому create-only write не выполнялся.

Не пытайся получать Scheduled Task UI самостоятельно.
Scheduled Task повторно не запускай.

## Exact audit scope

Проверить Russian-language player-feedback discoverability **только** для exact current `g000001`:

1. `Baldur's Gate 3 - Digital Deluxe Edition DLC`
2. `Hellish Quart`
3. `Tetris® Effect: Connected`

Сначала прочитай exact current descriptor `g000001` и active worker evidence contracts/prompt/schema, чтобы сохранить exact appid/title identity и binding.

Не исследуй другие игры и не расширяй backlog scope.

## Core question

Для каждой из трёх игр установить:

**Существовал ли в обычном публичном web в пределах canonical bounded research такой русскоязычный attributable item-level player feedback, который Scheduled worker мог законно использовать как `russian` или `mixed` feedback record и при необходимости bind к observation/conflict?**

Нужно проверять реальную discoverability, а не наличие русской страницы магазина или русскоязычного профессионального обзора.

## Independent bounded search method

Выполни независимый bounded web evidence audit по правилам active contract.

Для каждой игры:
- разреши release year / exact product identity;
- используй exact title + year;
- попробуй разумные русскоязычные варианты названия/транслитерации, если это помогает discovery;
- проверь обычный web search и релевантные public player-feedback surfaces;
- Steam reviews/community/discussions, русскоязычные форумы/сообщества и другие публичные player-feedback surfaces допустимы;
- профессиональные обзоры, store metadata, search/list/index pages сами по себе не являются player-feedback records;
- не сохраняй raw review/post bodies, quotes, usernames, display names или profile URLs.

Используй не больше active hard bounds:
- максимум 8 web-search queries на игру;
- максимум 16 opened/read source pages на игру.

Это audit ceilings, не targets.

## Exact product identity rule

Не смешивай base game, DLC, edition, sequel, remaster или другой appid.

### Special care: Baldur's Gate 3 - Digital Deluxe Edition DLC

Для BG3 DLC не считать общие отзывы/обсуждения базовой Baldur's Gate 3 доказательством по DLC только потому, что они русскоязычные.

Можно использовать item только если:
- physical feedback item законно относится к exact DLC/product surface **или**
- active canonical contract явно разрешает такой exact cross-surface relation (если нет — не разрешать его самостоятельно).

Если русскоязычные игроки обсуждают Deluxe Edition внутри base-game thread/review, это можно записать как **discovery observation for methodology**, но не объявлять usable dossier feedback для DLC, если current contract запрещает такое product mixing.

В report отдельно раздели:
- `discoverable_but_not_contract_usable`;
- `contract_usable_russian_feedback`.

## What counts as a usable Russian feedback record

Usable item должен удовлетворять active V2 rules, включая:
- attributable individual player review/post/comment/discussion contribution;
- stable item-level non-profile URL or neutral public_ref;
- exact parent-source relationship;
- Russian or genuinely mixed language;
- no author identity/raw text persistence;
- product identity sufficiently resolved;
- может реально поддержать хотя бы один neutral observation/conflict, а не быть пустым упоминанием названия.

Не считать usable:
- Russian-rendered Steam Store page;
- review/search/list/index page without attributable item;
- professional/editorial article;
- forum category root without individual player item;
- vague search snippet;
- aggregate Steam review counts;
- base-game feedback for DLC when contract identity does not permit it.

## Per-game required result

Для каждой из трёх игр дай ровно одну основную classification:

- `usable_russian_feedback_found`
- `russian_feedback_found_but_not_contract_usable`
- `no_usable_russian_feedback_found_within_bounds`
- `identity_or_access_blocked`

Если `usable_russian_feedback_found`:
- укажи только compact neutral provenance sufficient to prove discoverability (source type/domain, non-profile item URL or neutral public_ref, approximate date/language where available);
- не цитируй и не пересказывай raw user content;
- укажи, какой тип neutral observation/conflict такой item мог бы законно поддерживать, не создавая dossier.

Если usable items несколько, не надо собирать production dossier; достаточно минимального proof set, обычно 1–3 items на игру.

## Overall audit classification

После трёх per-game результатов выбери ровно одну:

1. `confirmed_russian_discovery_failure`
   - usable Russian feedback оказался reasonably discoverable хотя бы для существенной части exact group, и live claim о невозможности получить usable Russian records указывает на реальный discovery weakness;

2. `confirmed_russian_evidence_scarcity`
   - bounded independent audit также не нашёл usable Russian feedback для всех трёх exact products, при этом методически поиск был полноценным;

3. `mixed_discovery_failure_and_scarcity`
   - для части exact products usable Russian feedback найден, для части — действительно не найден/не usable;

4. `blocked_cannot_determine_discovery_quality`
   - доступ/identity/evidence не позволяют честно классифицировать.

Не утверждай точную внутреннюю причину, почему Scheduled worker что-то не нашёл, если runtime search trace отсутствует. В таком случае формулируй только наблюдаемый факт: evidence был discoverable / не был discoverable в независимом bounded audit.

## Compare discovery methodology, not just outcome

Если usable Russian feedback найден, зафиксируй **какой минимальный search pattern/surface его обнаружил**, например:
- exact title + year + Russian-language query;
- site-specific search;
- Steam community/discussion surface;
- Russian product-name variant.

Не превращай это в новый production search engine или fixed website quota.
Цель — понять, отсутствует ли в worker prompt очевидная discovery instruction.

## Required decision at end

Report должен ответить:

1. Были ли реально доступные contract-usable Russian feedback items для каждой из трёх игр?
2. Если были — насколько обычным/разумным поиском они находились?
3. Если не были — были ли хотя бы Russian pages/items, которые выглядели как evidence, но contract правильно запрещает их использовать?
4. Есть ли доказанный methodology/discovery gap?
5. Следует ли сначала исправлять Russian discovery method, либо только уже доказанный worker contract misread, либо нужны оба fix-а?
6. Какой **один следующий bounded IMPLEMENT task** должен создать Director?

## Architecture / safety constraints

- Это READ / VALIDATE audit, не IMPLEMENT.
- Не меняй prompt/schema/contract/validator/runtime.
- Не создавай production candidate.
- Не запускай Scheduled Task `Run now`.
- Не меняй group size=3.
- Не split-ить groups.
- Не добавлять retry/healing.
- Не менять parallel buffer/maximal contiguous prefix.
- Не менять canonical progress/cache/receipts/quarantine.
- Не запускать Proactive Project Auditor.
- Не публиковать raw player text/user identity.

## Durable report

Required path:

`reviews/worker_reports/taste-dossier-russian-discovery-audit-01.md`

Report должен попасть в `main` до завершения task.

Обязательные разделы:
- Task / repository / mode.
- Exact snapshot/group identity audited.
- Search methodology and bounded query/page counts per game.
- Per-game classification table.
- Minimal compact provenance for any usable proof items.
- Distinction between discoverable and contract-usable.
- Overall classification.
- Human-readable conclusion.
- Whether Russian discovery method has a proven gap.
- Whether previous contract-misread fix is still needed.
- Unresolved.
- Status.
- Exactly one recommended next bounded IMPLEMENT task.
- Efficiency / reusable lesson per `DIRECTOR_PROTOCOL.md`.

Allowed final statuses:
- `confirmed_russian_discovery_failure`
- `confirmed_russian_evidence_scarcity`
- `mixed_discovery_failure_and_scarcity`
- `blocked_cannot_determine_discovery_quality`

## CURRENT_TASK.md

Можно обновить только в рамках требований `CHAT_PROTOCOL.md` для реально выполняемой audit-задачи; unrelated concurrent work не удалять и не переписывать.

## Next-step boundary

После durable report остановись.
Не начинай fix автоматически.
