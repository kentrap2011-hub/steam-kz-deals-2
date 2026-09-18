# WORKER TASK — TASTE DOSSIER RUSSIAN MULTI-SOURCE RETRIEVAL IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-russian-multi-source-retrieval-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START gate

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main` и зафиксируй checklist.

После START прочитай только минимально необходимые актуальные canonical files:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical strict/buffered validation paths только в объёме этой задачи;
- `PROJECT_DECISIONS.md` для существующего TASTE-008 и нового retrieval rationale.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Required prior evidence

Прочитай полностью:
1. `reviews/worker_reports/taste-dossier-russian-discovery-audit-01.md`
2. `reviews/worker_reports/taste-dossier-russian-existence-retrieval-gate-implement-01.md`

Используй также следующий authoritative manual live result пользователя как observed behavior:

> Canonical snapshot и binding не изменились: ожидается g000001 snapshot 093952f4…58296.
>
> В этой инвокации выполнен новый bounded evidence-поиск по точной группе. Для Baldur's Gate 3 - Digital Deluxe Edition DLC Steam подтверждает существование более 500 русскоязычных пользовательских обзоров точного appid 2378500; для Hellish Quart — около 560 русскоязычных обзоров appid 1000360. При этом получить из доступных поверхностей contract-usable attributable item-level русскоязычные записи не удалось.
>
> По действующему russian-existence-retrieval-gate-2026-09-18 это состояние existence_established_retrieval_unresolved, которое запрещает считать dossier полным. Поэтому g000001 не сериализована и create-only candidate не опубликован. Canonical progress остаётся 0/732; к g000002 переходить нельзя.

Не пытайся получать Scheduled Task UI самостоятельно.

## Proven problem

Текущий existence/retrieval gate работает правильно: proven existence + no usable item => fail closed.

Но live behavior показывает, что Scheduled worker недостаточно диверсифицирует retrieval после existence signal. Он фактически застревает на Steam/Steam-like surfaces, хотя active contract уже разрешает ordinary multi-source player-feedback research.

Новый fix должен улучшить **retrieval strategy**, не ослабляя gate.

## Goal

Когда exact-product Russian player-feedback existence уже доказано, worker должен выполнить **bounded adaptive multi-source retrieval**, а не продолжать крутиться вокруг одного источника/домена.

Steam может быть existence signal или одним из retrieval surfaces, но не является обязательным источником usable Russian record.

## Canonical retrieval behavior

После `existence_established` и пока usable Russian/mixed item-level record не найден:

1. Worker должен перейти в explicit **retrieval diversification phase**.
2. Он обязан использовать оставшийся bounded search budget для разных разумных public player-feedback surface classes, а не повторять вариации одного и того же Steam aggregate/list/index пути.
3. Допустимые surface classes включают, когда реально доступны и релевантны exact product:
   - Steam Community / discussions / user review item surfaces;
   - Reddit exact-product threads/comments;
   - публичные русскоязычные игровые форумы;
   - публичные community discussions / comment threads;
   - публичные store/user-review surfaces;
   - Pikabu/аналогичные публичные user-generated discussion surfaces;
   - другие credible public player-feedback surfaces.
4. VK/другие social/community surfaces допустимы только когда публичный конкретный post/comment доступен без профильно-идентифицирующего persistence и соответствует compact provenance rules.
5. Professional/editorial/journalistic Russian content остаётся context only и не заменяет player feedback.
6. Нельзя объявлять fixed website quota или обязательный список сайтов.
7. Нельзя требовать посещения всех перечисленных классов.
8. Но если existence proven и первый retrieval surface не дал usable item, worker не может завершить bounded search, не попробовав **хотя бы один materially different player-feedback surface class**, если такой surface reasonably discoverable и search/page budget ещё доступен.
9. Если после первого диверсифицированного шага evidence всё ещё unresolved и budget остаётся, worker должен продолжать adaptive diversification по наиболее перспективным доступным surface classes, пока:
   - usable Russian/mixed item найден;
   - hard bound исчерпан;
   - либо больше нет reasonably discoverable distinct surface classes.

## Search-budget semantics

Сохрани текущие hard ceilings:
- <=8 web-search queries per game;
- <=16 opened/read source pages per game.

Не увеличивать ceilings в этой задаче без доказанной необходимости.

Но внутри этих ceilings исправь распределение бюджета:
- repeated aggregate/list lookups одного источника после existence signal не должны поглощать весь budget;
- после existence signal query planning должно приоритизировать item-level discovery;
- repeated same-domain/same-surface query variants должны считаться diminishing-return и уступать distinct surface search.

Не создавать persistent retry state или новый scheduler.

## Exact identity

Exact-product identity остаётся строгой.

Особенно для `Baldur's Gate 3 - Digital Deluxe Edition DLC`:
- base-game feedback не становится DLC feedback автоматически;
- multi-source diversification не даёт права смешивать appid/product identity;
- если сторонняя discussion surface явно обсуждает exact DLC/Deluxe content, worker должен доказать exact-product relevance согласно active contract;
- если relevance недостаточна — item не usable.

Для Hellish Quart и Crown Trick действуют те же exact title/appid/year safeguards.

## Machine-contract requirement

Текущий failure state `existence_established_retrieval_unresolved` сохраняется.

Не вводить новый state только ради diversification, если можно детерминированно выразить behavior через active evidence contract/prompt + validator invariants.

Но новое правило должно быть machine-testable настолько, чтобы deterministic regression мог доказать минимум:
- existence proven;
- first surface yields no usable item;
- second materially different public player-feedback surface contains a usable item;
- worker contract требует продолжить retrieval до второго surface при наличии budget, а не преждевременно завершить unresolved.

Если для этого нужен минимальный machine-readable retrieval-policy invariant/revision — добавь его в existing evidence contract. Не создавать второй validator truth source.

## Strict validator

Не превращай strict validator в web-search trace validator: GitHub не должен пытаться доказать, какие сайты worker реально посетил, если таких данных нет в candidate.

Canonical strict validator должен:
- сохранить existing Russian existence/retrieval state coherence;
- сохранить fail-closed для `existence_established_retrieval_unresolved` и access unresolved;
- не ослаблять exact identity;
- не ослаблять source-item provenance/language/temporal/summary/conflict guards;
- не требовать Steam source;
- принимать valid dossier с Russian record из non-Steam public player-feedback source, если все ordinary provenance/identity rules выполнены.

Worker-facing contract/prompt должен владеть adaptive retrieval strategy; strict validator — итоговой структурной/evidence consistency.

## Required regressions

Добавь focused deterministic regressions минимум для:

### RUS-MS-01 — Steam existence -> non-Steam usable Russian item
- exact-product Steam aggregate proves Russian feedback existence;
- Steam item retrieval fails;
- a different public player-feedback surface contains contract-usable exact-product Russian item;
- worker generation contract requires continuing to that distinct surface while budget remains;
- final `found_and_used` shape is valid.

### RUS-MS-02 — do not stop after one failed surface
- existence proven;
- first reasonable surface returns only aggregate/list/non-item evidence;
- second materially different surface is discoverable;
- prompt/contract must not permit immediate `existence_established_retrieval_unresolved` before diversification.

### RUS-MS-03 — diversified search still unresolved
- existence proven;
- at least two materially distinct reasonable player-feedback surface classes attempted in fixture logic;
- none yields usable item;
- unresolved remains correct and fail-closed.

### RUS-MS-04 — non-Steam provenance accepted
- valid exact-product Russian item from forum/Reddit/community-style source;
- satisfies ordinary compact provenance;
- accepted without any Steam item-level record.

### RUS-MS-05 — journalism does not satisfy gate
- Russian professional/editorial article found during diversification;
- cannot become player feedback or satisfy `found_and_used`.

### RUS-MS-06 — identity remains strict
- a Russian post about base BG3 cannot satisfy BG3 Digital Deluxe DLC solely because it is Russian and mentions Baldur's Gate 3;
- exact DLC relevance/binding still required.

### RUS-MS-07 — no fixed website quota
- machine contract/prompt must encode adaptive diversification, not “visit N named sites”;
- Steam must remain optional as retrieval source.

## Architecture constraints — MUST NOT CHANGE

- GitHub remains control plane.
- Scheduled ChatGPT remains bounded semantic/data worker + immutable create-only publisher.
- Group size remains 3.
- No per-game group split.
- No automatic retry/healing manager.
- No new queue, recurring stage, crawler service or backlog manager.
- No fixed website quota.
- No Steam-only requirement.
- Do not increase search/page hard bounds unless deterministic proof makes current bounds impossible; default is keep them unchanged.
- Do not weaken strict validator.
- One canonical strict validator truth source.
- Parallel buffer / maximal contiguous prefix unchanged.
- Scope/order/progress/completeness ownership unchanged.
- No manual repair of queue/cache/progress/receipts/candidates.
- No Taste Semantic Producer/ranking/pricing/package/giveaway/UI changes.

## PROJECT_DECISIONS

Добавь компактное rationale update/new decision adjacent to TASTE-008:

- existence proof creates retrieval obligation;
- retrieval obligation is **source-agnostic**;
- Steam aggregate can prove existence without becoming required retrieval source;
- after one surface fails, bounded adaptive diversification across materially different player-feedback surface classes is required while budget remains;
- no fixed website quota;
- exact product identity remains strict;
- professional content remains context-only.

Не переписывай unrelated decisions.

## Compatibility / activation

Prompt/evidence-contract changes входят в content-complete binding.

После implementation:
- bounded branch/PR;
- focused dossier CI + regressions + ownership check;
- merge only green;
- normal GitHub-owned activation;
- fresh snapshot if binding incompatible;
- old snapshot/candidates stale/inert only through canonical behavior;
- no manual rebind/progress repair.

## Scheduled Task

**Do NOT run Scheduled Task `Run now` in this implementation task.**
Scheduled Task settings не менять.

## Durable report

Required path:

`reviews/worker_reports/taste-dossier-russian-multi-source-retrieval-implement-01.md`

Report committed to `main` before complete.

Обязательные разделы:
1. Task / repo / mode.
2. Architecture preflight.
3. Reconciled prior live evidence.
4. Exact multi-source retrieval rule.
5. Why Steam is existence/source option, not required retrieval source.
6. How search budget diversification works.
7. Machine contract/prompt changes.
8. Strict validator impact and confirmation it was not weakened.
9. RUS-MS-01..07 regressions.
10. Exact identity preservation.
11. Confirmation journalism/context still does not satisfy player-feedback gate.
12. PR / CI / merge refs.
13. Activation/binding/snapshot state:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size=3;
   - old snapshot handling.
14. PROJECT_DECISIONS ref.
15. Confirmation Run now/settings unchanged.
16. Unresolved.
17. Status.
18. Exactly one recommended next step.
19. Efficiency / reusable lesson per DIRECTOR_PROTOCOL.md.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

## CURRENT_TASK.md

Обновлять только по правилам `CHAT_PROTOCOL.md`, не затирать unrelated concurrent work.

## Exactly one next step after success

One separate live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the resulting current compatible snapshot, with manual UI result supplied by the user. Do not run Proactive Auditor before clean live acceptance.
