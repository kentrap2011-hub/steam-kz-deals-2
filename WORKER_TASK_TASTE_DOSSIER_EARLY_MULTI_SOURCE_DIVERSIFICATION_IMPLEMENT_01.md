# WORKER TASK — TASTE DOSSIER EARLY MULTI-SOURCE DIVERSIFICATION IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-early-multi-source-diversification-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- current canonical dossier worker index/work manifest sufficient to resolve snapshot/binding;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- relevant strict/prepublication/buffered/compatibility paths only as needed;
- `reviews/worker_reports/taste-dossier-mo-astray-non-steam-russian-source-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`;
- `reviews/worker_reports/taste-dossier-steam-community-child-retrieval-implement-01.md`;
- `reviews/worker_reports/taste-dossier-russian-multi-source-retrieval-implement-01.md` if present;
- recent relevant TASTE decisions in `PROJECT_DECISIONS.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted diagnosis

Treat these findings as accepted:

1. The active evidence model is source-agnostic and already allows ordinary public non-Steam player-feedback sources.
2. For MO:Astray, exact appid `1104660`, Steam proves 144 Russian-language reviews exist.
3. The previous production invocation stopped with `existence_established_retrieval_unresolved` because it failed to obtain a contract-usable Russian/mixed concrete Steam item.
4. A later read-only diagnostic found an exact-product Russian user review on StopGame with a stable non-profile item locator:
   `https://stopgame.ru/game/mo_astray/review/10186`
5. That item is contract-usable for durable traits under the current contract.
6. The diagnostic found it cheaply after diversification: approximately one search query plus page/item opens.
7. No contract change and no new external retrieval provider is needed for MO:Astray.
8. No canonical prompt/contract change has occurred since the failed production invocation that would make the worker behave differently by itself.
9. Therefore the actionable gap is retrieval strategy/order: after Russian existence is proven, the worker can spend too much bounded effort on Steam before pivoting to materially different public player-feedback sources.

## Goal

Improve the generic Scheduled-worker retrieval strategy so that it **diversifies earlier** after Steam proves Russian review existence but fails to yield a contract-usable concrete item.

The worker must not treat Steam as the required retrieval source.

The desired behavior is:

`Russian existence proven -> bounded preferred Steam item attempt -> if no usable item, early generic non-Steam diversification -> stable concrete player-feedback item if available`

Do not special-case MO:Astray or StopGame in production logic.

## Core design requirement

The fix must change **ordering/prioritization**, not evidence semantics.

After an exact-product Russian existence signal is established:

1. Prefer a cheap/strong Steam item-level path first because exact product binding is often easy there.
2. But if the initial Steam item attempts yield only:
   - aggregate counts;
   - inaccessible language-filter representation;
   - profile-scoped item only;
   - non-Russian cards;
   - collection/index row without child item;
   then pivot early to materially different public player-feedback sources.
3. Do NOT spend most/all of the 8-query budget retrying equivalent Steam route families before diversification.
4. A generic early diversification query should use exact product identity signals such as:
   - exact title;
   - release year when helpful;
   - Russian player-review/discussion wording;
   - exact appid/developer/publisher only when useful for disambiguation.
5. Search across source classes, not a hardcoded named-site list.
6. Site-specific follow-up is allowed only after a promising result/source class is discovered.
7. If a stable concrete non-Steam player-feedback item is found, use the existing source/provenance/language/recency rules unchanged.
8. Continue source-agnostic diversification only as needed within the existing budget.

## No fixed Steam quota unless justified

Do not introduce a brittle rule such as "exactly N Steam queries" unless the current prompt structure requires a deterministic bound and the implementation can justify it.

Prefer a semantic stop condition:
- once materially equivalent Steam routes have failed to expose an accepted item shape, diversify.

If an explicit small route count is necessary for deterministic worker behavior, document why and keep it generic/minimal.

## Production budget

Do NOT increase:
- max 8 web/search queries per game;
- max 16 opened/read pages per game.

The task should make the existing budget more efficient.

No website quotas.
No unlimited retries.
No new recurring stage/service.

## Repo-owned lever / architecture

Expected primary lever:
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical prompt revision/content-complete binding metadata.

Do not add local shell/Python/browser automation dependencies.

GitHub remains control plane.
Scheduled ChatGPT remains semantic/public-web retrieval worker.

If architecture preflight shows another current canonical repo-owned artifact actually controls source ordering, use the smallest correct owner instead of duplicating rules.

## Required live proof — MO:Astray

A prompt edit alone is not sufficient.

Using the improved strategy in the current ordinary web environment, perform a bounded proof on MO:Astray appid `1104660` showing that the worker:

1. recognizes the established Russian existence signal;
2. does not burn the diagnostic path on repeated Steam attempts;
3. pivots to a materially different public player-feedback source;
4. reaches at least one contract-usable Russian/mixed concrete non-Steam item;
5. verifies exact product identity;
6. derives language from the concrete item;
7. uses a safe stable locator or other already-legal identity shape;
8. applies recency correctly.

The known StopGame item may serve as the acceptance proof if rediscovered by the generic strategy, but production prompt logic must NOT hardcode StopGame or its URL.

Do NOT publish a production candidate during proof.

## Generalization proof

Also demonstrate from prompt/tests that the strategy applies generically to future games where:
- Russian Steam existence is proven;
- Steam item retrieval remains aggregate/profile/index-only;
- another public player-feedback source may exist.

The strategy must not become:
- "try StopGame";
- "try Russian sites in this fixed order";
- "always leave Steam after one failure" regardless of a cheap usable Steam card already present.

## Required regressions

### DIVERSIFY-EARLY-01 — Steam remains preferred cheap exact-product path
A readily available safe concrete Steam item can still be used without unnecessary detour.

### DIVERSIFY-EARLY-02 — aggregate-only triggers diversification
Russian existence/count without concrete item does not consume repeated equivalent Steam retries.

### DIVERSIFY-EARLY-03 — profile-only triggers diversification
A profile-scoped concrete Russian hit remains discovery-only and causes safe diversification rather than persistence/re-parenting.

### DIVERSIFY-EARLY-04 — non-Russian Steam cards do not block diversification
Concrete non-Russian cards cannot satisfy the Russian gate and should not cause repeated same-family attempts after the Steam route is exhausted.

### DIVERSIFY-EARLY-05 — index-row-only triggers diversification
A safe collection/index row without concrete child is not evidence and should not monopolize remaining budget.

### DIVERSIFY-EARLY-06 — generic source diversification
Prompt uses materially different public player-feedback source classes and does not hardcode MO:Astray/StopGame.

### DIVERSIFY-EARLY-07 — stable non-Steam item accepted
A stable exact-product non-Steam player-feedback item uses existing evidence/provenance path.

### DIVERSIFY-EARLY-08 — language/recency unchanged
Language derives from bound concrete item; old items support durable traits only.

### DIVERSIFY-EARLY-09 — production ceilings unchanged
8/16 remain hard ceilings; no new per-site quota or retry loop.

### DIVERSIFY-EARLY-10 — privacy/provenance guards unchanged
No profile identity persistence, no author hashes, no aggregate mentions, no re-parenting.

### DIVERSIFY-EARLY-11 — prior suites remain green
Russian gate, multi-source, Store-card, transient-author, contradiction, language, semantic consistency, package/story-DLC, buffering/compatibility/ownership suites remain green.

### DIVERSIFY-EARLY-12 — MO:Astray live proof
Generic improved strategy reaches a contract-usable Russian/mixed non-Steam item for appid 1104660 within the existing 8/16 production budget.

If DIVERSIFY-EARLY-12 fails, status cannot be `complete_ready_for_live_acceptance`.

## Contract/schema boundaries

Do NOT weaken or expand evidence semantics merely to pass the proof.

Do not change:
- profile privacy;
- source_id/feedback_id privacy;
- exact appid/product binding;
- physical parent/container binding;
- language projection;
- Russian existence states;
- aggregate count semantics;
- recurrence caps;
- recency rules;
- cross-release identity rules.

If a real contract contradiction is discovered, stop scope expansion and report `needs_user_decision` with the exact contradiction.

## Activation

If implementation succeeds:

- bounded branch/PR;
- focused regressions + existing relevant dossier suites + ownership validation;
- merge only green;
- normal GitHub-owned activation;
- fresh prompt binding/snapshot if required;
- no manual progress rebind/repair.

IMPORTANT:
A content-complete prompt revision may create a fresh compatible snapshot and reset completion for the new binding. Report this clearly and do not attempt to preserve incompatible old canonical/buffered progress manually.

Do not treat earlier create-only candidate publications as compatible automatically after a prompt-binding change.

## Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not change Scheduled Task settings.

The MO:Astray proof is validation only and must not publish production state.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-early-multi-source-diversification-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight / actual retrieval owner.
3. Accepted diagnosis.
4. Exact ordering problem found in current prompt.
5. Repo-owned implementation.
6. Before/after retrieval flow in plain language.
7. Generic diversification behavior.
8. MO:Astray live proof ledger.
9. Exact usable non-Steam item proof.
10. Budget used in proof.
11. Confirmation no named-site/product hardcoding.
12. Confirmation contract/schema/strict semantics unchanged.
13. DIVERSIFY-EARLY-01..12.
14. Existing guard suites.
15. PR / CI / merge refs.
16. Activation/binding/snapshot state:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size;
   - exact expected group;
   - scope delta and reason;
   - compatibility effect on prior buffered/canonical progress.
17. Scheduled Task confirmation.
18. Unresolved.
19. Status.
20. Exactly one recommended next step.
21. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked_external_transport`

## Status rule

`complete_ready_for_live_acceptance` is allowed ONLY if:
- real canonical repo-owned strategy change is implemented and activated;
- DIVERSIFY-EARLY-01..11 pass;
- DIVERSIFY-EARLY-12 succeeds on MO:Astray within the current 8/16 production budget;
- no evidence/privacy/provenance/recency rule is weakened.

## Exactly one next step

If complete:
- return to Director for one clean production live acceptance on the newly activated compatible snapshot.

If needs_fix:
- identify one exact implementation defect.

If needs_user_decision:
- identify one bounded architectural/contract choice only.

If blocked_external_transport:
- identify the exact missing capability.

Do not run production inside this task.
