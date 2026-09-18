# WORKER TASK — TASTE DOSSIER STEAM STORE REVIEW CARD PARENT FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-steam-store-review-card-parent-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical strict validator / compact provenance paths;
- `PROJECT_DECISIONS.md`, особенно TASTE-010;
- `reviews/worker_reports/taste-dossier-transient-author-dedupe-fallback-implement-01.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Live acceptance finding

Authoritative user-provided Scheduled Task result for current canonical state:

- snapshot: `99c3601f…ba8b8`;
- expected group: `g000001`;
- scope: `730`;
- binding: `transient-author-dedupe-fallback-2026-09-18`;
- g000001:
  1. Crown Trick — appid 1000010
  2. Hellish Quart — appid 1000360
  3. Tetris® Effect: Connected — appid 1003590
- Hellish Quart and Tetris Effect had usable Russian concrete player-review cards.
- Crown Trick had 120 Russian-language reviews and concrete Russian review cards visibly exposed on the exact-product Steam Store app page.
- Those cards could not be serialized because active V2 rules prohibit Steam Store app page as `player_feedback` source.
- Result: Crown Trick remained `existence_established_retrieval_unresolved`; atomic g000001 was not published; canonical progress remained 0/730.

Treat that live result as authoritative confirmation of the production blocker.

## Problem

The new `transient_author_deduped` fallback is internally inconsistent with the old broad prohibition on Steam Store app pages.

The old rule correctly prevents:
- Steam Store app page itself from becoming a player-feedback record;
- aggregate rating/review counts from becoming mentions;
- language review totals from becoming feedback items;
- storefront metadata from being treated as individual player feedback.

But it now also blocks **concrete individual review cards visibly rendered on the exact-product Steam Store page**, even when:
- the concrete review body is actually inspected;
- the author is transiently distinguishable for dedupe;
- no author identity is persisted;
- exact appid identity is known;
- the card otherwise satisfies the transient-author fallback.

That is the defect to fix.

## Exact required rule

Keep this invariant:

> A Steam Store app page is NOT itself a player-feedback record, mention, review item, or sufficient evidence source.

Add this narrow exception:

> A Steam Store exact-app page MAY act as the **parent collection/source surface** for `transient_author_deduped` fallback records when concrete individual review cards/items are actually visible and inspected on that page.

This exception applies only to the parent surface role.

### Still forbidden

Do NOT allow any of the following to become feedback records or mentions:
- Steam Store app page itself;
- review count, e.g. `120 Russian reviews`;
- percent positive;
- aggregate rating;
- language count;
- review-summary block;
- generic storefront text;
- search/index snippets with no concrete inspected review card;
- collection/list surface where no individual item content was actually inspected.

### Allowed

A concrete review card may become fallback evidence when all normal transient-author fallback conditions hold:
- exact appid/product identity;
- concrete individual player-generated review item visibly inspected;
- language known from the concrete item;
- transient author/account identity available strongly enough for dedupe;
- no neutral stable review locator available/usable;
- author identity discarded before serialization;
- persisted item uses local opaque fallback id only;
- parent exact-product Steam Store app page is stored as safe collection provenance;
- recurrence strength remains subject to existing fallback caps.

## Do not broaden normal stable-locator rules

A Steam Store app page must NOT become a valid stable item locator.

If a neutral `recommendationid` / direct stable item URL is available, continue to use the normal `stable_locator` path.

Do not reinterpret the whole Steam page as one review.

Do not synthesize review-level `public_ref` from card position, date, author name or DOM order.

## Source classification

Implement the smallest schema/contract representation needed.

Preferred outcome:
- retain `source_kind` / source semantics that distinguish Steam Store page from item record;
- allow a narrow parent mode such as existing `feedback_surface_mode = concrete_item_collection` on exact-app Steam Store surfaces;
- the child fallback record remains the actual player-feedback record;
- parent aggregate metadata remains non-mention provenance only.

Do not introduce a second duplicate source model if current transient-author schema already has the needed field.

## Russian gate interaction

A valid Russian/mixed concrete review card on exact-product Steam Store, serialized through the transient-author fallback, MAY satisfy `russian_attempt = found_and_used`.

The aggregate fact that Russian reviews exist still cannot satisfy `found_and_used` by itself.

## Exact product identity

Steam appid exposed by the Store page must equal the exact dossier appid.

No base-game/DLC cross-satisfaction.
No title-only loose matching.
Story-DLC policy remains unchanged.

## Required regressions

### STORE-CARD-01 — Steam Store page itself remains invalid feedback
Exact app page with counts/ratings only cannot create a player-feedback record or mention.

### STORE-CARD-02 — aggregate Russian count remains existence signal only
`120 Russian reviews` does not satisfy `found_and_used`.

### STORE-CARD-03 — concrete Crown Trick review card fallback accepted
Exact appid 1000010 Steam Store page with an actually inspected Russian concrete review card + transient distinct author + no neutral locator can serialize a valid fallback record.

### STORE-CARD-04 — no author persistence
Crown Trick fallback serialization contains no username/SteamID/profile URL/direct hash.

### STORE-CARD-05 — parent-only semantics
The Steam Store app page is accepted only as parent collection provenance; it is not itself a feedback item.

### STORE-CARD-06 — stable locator remains preferred
If a neutral recommendationid exists, normal stable path is used instead of fallback.

### STORE-CARD-07 — exact appid mismatch rejected
A concrete review card surfaced under a different Steam appid cannot satisfy the dossier item.

### STORE-CARD-08 — fallback recurrence caps unchanged
Store-page fallback cards remain capped by TASTE-010 recurrence rules and cannot alone produce moderate/strong.

### STORE-CARD-09 — Russian gate
Valid Russian Crown Trick fallback record can satisfy `found_and_used`.

### STORE-CARD-10 — no concrete card, no fallback
Steam Store page with only aggregate/review-summary metadata is rejected as concrete feedback.

### STORE-CARD-11 — current g000001 fixture
Deterministic fixture for:
- Crown Trick Store concrete-card fallback;
- Hellish Quart existing fallback/stable behavior;
- Tetris Effect existing fallback/stable behavior;
must validate as a complete three-game candidate shape without weakening unrelated evidence rules.

## Architecture constraints

Do not change:
- GitHub control-plane ownership;
- Scheduled ChatGPT role;
- group size = 3;
- atomic group semantics;
- maximal contiguous prefix;
- transient-author privacy model;
- direct-hash ban;
- stable-locator requirement for normal records;
- source-agnostic Russian discovery;
- story-DLC scope policy;
- package/pricing/ranking/giveaway/UI;
- retry/healing architecture.

Do not create:
- new recurring task;
- reviewer identity database;
- cross-run author mapping;
- new queue;
- Steam-specific retry loop.

## Canonical policy / decisions

Update only the owning evidence/source contract and prompt/schema/validator pieces actually required.

Add or amend a compact decision entry in `PROJECT_DECISIONS.md` explaining:
- Steam Store app page remains aggregate/storefront provenance, not feedback;
- concrete review cards rendered inside it can parent transient-author fallback records;
- this is necessary because the worker can inspect the review card even when no neutral item locator is exposed;
- aggregate counts remain non-evidence;
- privacy and recurrence restrictions from TASTE-010 remain unchanged.

Do not rewrite unrelated decisions.

## Compatibility / activation

Because evidence contract/schema/prompt/validator behavior changes:
- bounded branch/PR;
- focused regressions + existing dossier regression suite + ownership validation;
- merge only green;
- normal GitHub-owned activation/rebuild;
- fresh compatible binding/snapshot if required by canonical compatibility rules;
- no manual rebind/progress repair.

## Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not change Scheduled Task settings.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-steam-store-review-card-parent-fix-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight.
3. Exact defect proven by live acceptance.
4. Exact narrow source-rule change.
5. What remains forbidden.
6. Persisted parent/child schema semantics.
7. Russian gate interaction.
8. Exact-product identity preservation.
9. Confirmation transient-author privacy/recurrence rules unchanged.
10. STORE-CARD-01..11 results.
11. Crown Trick fixture result.
12. Confirmation Hellish Quart/Tetris behavior not regressed.
13. PR / CI / merge refs.
14. Activation/binding/snapshot state:
    - snapshot id;
    - prepared/completed/remaining;
    - expected sequence;
    - group count;
    - group size;
    - exact g000001.
15. PROJECT_DECISIONS ref.
16. Confirmation Run now/settings unchanged.
17. Unresolved.
18. Status.
19. Exactly one recommended next step.
20. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

## CURRENT_TASK.md

Update only according to `CHAT_PROTOCOL.md`; preserve unrelated concurrent work.

## Exactly one next step after success

Return to Director. Do not run Scheduled Task inside this task. Director decides whether to perform one live acceptance against the resulting compatible g000001.
