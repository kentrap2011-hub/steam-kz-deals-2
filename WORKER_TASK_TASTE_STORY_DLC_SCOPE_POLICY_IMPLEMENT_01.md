# WORKER TASK — TASTE STORY DLC SCOPE POLICY IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-story-dlc-scope-policy-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантные Taste/dossier/package routes в `PROJECT_ROUTES.md`;
- `DIRECTOR_PROTOCOL.md` только если нужен closeout format;
- `config/execution_ownership_contract.json`;
- текущие canonical Taste/dossier scope contracts/policies;
- `PROJECT_RULES.md` — только релевантный DLC/Taste участок;
- `PROJECT_DECISIONS.md` — связанные DLC/package/Taste решения;
- scripts/workflows, которые фактически формируют Taste dossier eligible scope, только после определения canonical owner.

Перед первой write обязательно выполни architecture preflight из `CHAT_CONTEXT.md`.

## User-approved product rule

Пользователь уточнил исходный смысл DLC:

> В Taste/recommendation logic нужно учитывать только сюжетные DLC. Deluxe Edition upgrade, песни, артбуки, косметика, предметные наборы и подобный бонусный контент вообще не воспринимаем как отдельный meaningful game/Taste объект.

Это не эвристика для одной Baldur's Gate 3. Это canonical product rule для DLC scope.

## Core eligibility rule

DLC может попадать в Taste/dossier semantic scope **только при положительном подтверждении**, что оно добавляет самостоятельный сюжетный игровой контент.

### Include

Включать DLC, если authoritative/reliable product metadata подтверждает хотя бы один существенный narrative-content признак, например:
- новая сюжетная кампания;
- самостоятельная story chapter / episode;
- новая сюжетная линия;
- новые story quests / questline;
- narrative expansion / story expansion;
- отдельное приключение/история с игровым прохождением;
- другой эквивалентный substantial playable narrative content.

Наличие только новой карты/персонажа/оружия/режима без сюжетного содержания само по себе недостаточно.

### Exclude

Не считать самостоятельным Taste/dossier объектом:
- Digital Deluxe / Deluxe Upgrade;
- soundtrack / OST;
- digital artbook;
- cosmetic packs / skins;
- weapon/item/equipment packs;
- currency/resource packs;
- bonus songs;
- wallpapers/avatars/digital extras;
- supporter/founder packs, если они не содержат отдельного сюжетного контента;
- season pass / bundle entitlement сам по себе, если это только контейнер доступа к другим DLC;
- upgrade packs / bonus-content packs;
- прочие non-story add-ons.

Если DLC смешанный и содержит story content плюс косметику/бонусы, inclusion разрешено только если сюжетный playable content сам по себе существенный и положительно подтверждён.

## Fail-closed ambiguity rule

Не использовать простое правило `type=DLC => include`.

Если по доступной canonical metadata нельзя положительно доказать story-content eligibility:
- DLC не включается в Taste/dossier semantic scope;
- причина должна быть machine-readable;
- не делать broad manual web research по всему backlog из interactive/worker чата;
- если existing GitHub-accessible metadata недостаточно системно, зафиксировать минимальный bounded classification architecture, которая остаётся GitHub-owned и deterministic.

Предпочтение: false negative по сомнительному DLC лучше, чем включение косметики/Deluxe/OST как отдельной игры.

## Explicit regression case

`appid 2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC`

Должен стать **ineligible for Taste/dossier semantic scope**.

Причина: это bonus/digital-deluxe content pack, а не сюжетное DLC с самостоятельной story campaign/questline.

После активации он не должен находиться в canonical required dossier group plan.

## Scope of change

Исправь canonical scope formation, а не evidence retrieval.

Нужно найти реальную точку, где формируется eligible Taste/dossier scope, и внедрить правило там так, чтобы downstream worker уже не получал non-story DLC.

Не исправлять вручную текущую g000001.
Не удалять/редактировать immutable candidate artifacts вручную.
Не перепривязывать старый snapshot.
Normal GitHub-owned rebuild/recovery должен сам создать fresh compatible projection при необходимости.

## Backlog-wide effect

После реализации проверь весь текущий prepared/eligible DLC scope машинно, а не вручную по одному BG3 DLC.

Нужно получить компактную classification summary:
- сколько DLC-like items было рассмотрено;
- сколько story-eligible;
- сколько non-story excluded;
- сколько ambiguous excluded fail-closed;
- несколько representative examples каждой категории.

Не делай ручной web audit сотен DLC. Используй существующие GitHub-accessible product metadata/normalization paths; если их недостаточно для reliable positive classification, это должно быть явно отражено и решено минимально в canonical producer, а не интерактивным перебором.

## Do not overfit titles

Название может быть strong hint, но не единственная truth source.

Нельзя строить основной production classifier только на:
- словах `Deluxe`, `Soundtrack`, `Pack`;
- regexp по title без metadata corroboration.

Title heuristics могут быть fast negative hints для очевидных случаев, но positive `story_eligible` требует содержательного подтверждения из reliable product metadata.

## Machine-readable semantics

Добавь минимальный canonical machine-readable classification, достаточный для audit/debug, например эквивалент:
- `story_dlc_eligible`;
- `non_story_dlc_excluded`;
- `story_content_unproven_excluded`;

с compact reason/evidence source.

Не обязан использовать именно эти имена, если существующая модель уже имеет подходящее поле. Не плодить второй parallel source of truth.

## Relationship to packages/base games

Сохрани действующую архитектуру package/member aggregation и exact appid identity.

- Base games остаются без изменения.
- Story DLC может оставаться самостоятельным dossier/Taste объектом согласно этому правилу.
- Non-story DLC не должно создавать самостоятельную Taste semantic obligation.
- Package/season-pass/container не должен становиться story DLC только потому, что внутри него есть story DLC members; использовать существующую member/package architecture, не смешивать identity.
- Не менять pricing/package economics в этой задаче.

## Required regressions

Минимум:

### STORY-DLC-01 — BG3 Digital Deluxe excluded
appid `2378500` excluded from Taste/dossier scope as non-story digital-deluxe content.

### STORY-DLC-02 — obvious soundtrack/artbook/cosmetic excluded
Deterministic fixtures for OST/artbook/cosmetic/item pack must not enter semantic dossier scope.

### STORY-DLC-03 — real story expansion included
Fixture with positive reliable metadata for new story campaign/questline remains eligible.

### STORY-DLC-04 — ambiguous DLC fail-closed
DLC with no positive story-content evidence is excluded as `story content unproven`, not silently included.

### STORY-DLC-05 — mixed story + cosmetics
DLC containing substantial confirmed playable story content plus bonus cosmetics remains eligible because story component is independently confirmed.

### STORY-DLC-06 — season pass/container
Season pass/container is not itself a story DLC semantic object solely because it grants story DLC children.

### STORY-DLC-07 — base game unaffected
Normal base-game Taste/dossier eligibility remains unchanged.

### STORY-DLC-08 — current group-plan regeneration
After canonical activation, current required group plan must not contain appid `2378500`.

## Canonical policy / decisions

Это user-approved non-obvious product rule.

Обнови:
- canonical policy/rule file that actually owns Taste/DLC eligibility;
- `PROJECT_DECISIONS.md` с коротким rationale;
- `PROJECT_ROUTES.md`, если найден/изменён существенный route.

Rationale:
- Taste model evaluates meaningful playable narrative products, not merchandising/digital bonus packs;
- only story DLC is independently meaningful for this user's recommendation/taste workflow;
- positive story evidence is required;
- ambiguous/non-story DLC is excluded fail-closed;
- do not waste dossier research budget on Deluxe/OST/cosmetic add-ons.

## Architecture constraints

Не менять:
- GitHub control-plane ownership;
- Scheduled ChatGPT role;
- dossier group size = 3;
- parallel buffer/maximal contiguous prefix architecture;
- Russian retrieval/evidence contract except references needed to consume changed scope;
- item-level locator/provenance rules;
- Crown Trick/Hellish Quart evidence issue;
- Taste Semantic Producer;
- ranking weights;
- pricing/deal scoring;
- package economics;
- giveaway;
- UI;
- retry/healing architecture.

Не создавать новый recurring worker/queue/classification service unless canonical preflight proves absolutely required. Prefer existing GitHub preparation path.

## Compatibility / activation

После implementation:
- bounded branch/PR;
- focused CI/regressions + ownership checks;
- merge only green;
- normal GitHub-owned activation/rebuild;
- fresh snapshot/group plan if scope/binding changes require it;
- old projection/artifacts stale/inert only through existing canonical recovery path;
- никакого manual rebind/progress repair.

## Scheduled Task

**Scheduled Task Run now не запускать.**
Scheduled Task settings не менять.

## Durable report

Required path:
`reviews/worker_reports/taste-story-dlc-scope-policy-implement-01.md`

Report должен содержать:
1. Task / repo / mode.
2. Architecture preflight.
3. Exact canonical rule implemented.
4. Actual owning scope path/files.
5. Positive story eligibility evidence model.
6. Fail-closed ambiguity semantics.
7. Machine-readable classification model.
8. Backlog-wide compact classification summary.
9. STORY-DLC-01..08 results.
10. Explicit BG3 Digital Deluxe result.
11. Confirmation package/base-game semantics preserved.
12. PR / CI / merge refs.
13. Activation result.
14. New snapshot/group-plan state:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size;
   - exact new g000001 if changed.
15. PROJECT_DECISIONS ref.
16. Confirmation Russian retrieval/provenance rules unchanged.
17. Confirmation Scheduled Task Run now/settings unchanged.
18. Unresolved.
19. Status.
20. Exactly one recommended next step.
21. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

## CURRENT_TASK.md

Можно обновлять только по правилам `CHAT_PROTOCOL.md`. Не затирать unrelated work.

## Exactly one next step after success

Do not immediately run Scheduled Task.

Return to Director first. Director will decide whether the new g000001 should be live-tested or whether the Crown Trick/Hellish Quart locator-contract issue should be resolved before another Run now.
