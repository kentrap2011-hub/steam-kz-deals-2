# Taste Dossier MO:Astray Non-Steam Russian Source Diagnostic 01

## 1. Task / repo / mode

- Task: `TASTE DOSSIER MO:ASTRAY NON-STEAM RUSSIAN SOURCE DIAGNOSTIC 01`.
- Task ID: `taste-dossier-mo-astray-non-steam-russian-source-diagnostic-01`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `READ-ONLY DIAGNOSTIC`.
- Scope: only `MO:Astray`.
- Steam was used only as the already-established exact-product identity/existence context. No Steam child-retrieval effort was repeated.
- No implementation, prompt/schema/contract/validator/test change, PR, candidate publication, progress mutation, Scheduled Task run, or settings change was performed.
- The only repository write is this durable report.

## 2. Current snapshot / g000011 / exact target

Canonical worker index at diagnostic start:

- snapshot: `ec6ff4015ad01a9dcaaa2be845230cf04790c1444b99d5a1c31dad39047de872`
- prepared / completed / remaining: `702 / 18 / 684`
- canonical expected sequence: `7`
- group count: `234`
- full backlog complete: `false`
- active evidence revision: `contract-contradictions-fix-2026-09-18`
- active worker prompt revision: `web-evidence-v2-steam-russian-review-retrieval-improvement-v1`

Exact immutable `g000011` descriptor:

1. `1102190` — Monster Train
2. `1104380` — The Room VR: A Dark Matter
3. `1104660` — MO:Astray

Exact diagnostic target:

- title: `MO:Astray`
- canonical Steam appid: `1104660`
- release year used for research identity: `2019`
- developer: Archpray / Archpray Inc.
- publisher: Rayark / Rayark International Limited
- already-established Russian existence signal: `144` Russian-language Steam reviews
- prior Steam item-level state: usable Russian/mixed concrete item not obtained; Steam Community child implementation ended `blocked_external_transport`

The create-only publications previously reported for `g000001`–`g000010` remain buffered transport progress, not automatic canonical acceptance.

## 3. Diagnostic budget used

Task ceiling:

- web/search queries: maximum `20`
- opened/read source representations: maximum `40`

Actually used:

- **12 / 20 search queries**
- **9 / 40 opened/read source representations**, conservatively counting find/click representations and one failed Reddit child-click attempt

No production ceilings were changed.

The search budget was deliberately diversified rather than spent on one site.

## 4. Source-diversification plan actually executed

The executed non-Steam plan covered materially different source classes:

1. broad exact-title Russian player-review/discussion discovery;
2. StopGame user reviews / game-community content;
3. DTF user/community discovery;
4. iXBT forum discovery;
5. 4PDA forum discovery;
6. Reddit Russian-language community comments;
7. Pikabu user-generated discussion discovery;
8. VK public-web community discovery;
9. public storefront user reviews via Google Play;
10. public game-database / review surfaces surfaced by broad search, including GameFAQs/MobyGames;
11. exact title + release year + Russian `отзывы игроков` reachability control;
12. exact title + release year + StopGame site-specific reachability control.

The search engine also surfaced Steam pages incidentally. Those results were ignored for retrieval and used only consistently with the task's permitted identity/existence context.

## 5. Source-class results

### StopGame user reviews — usable

The exact StopGame game entity for `MO:Astray` exposes:

- title `MO:Astray`;
- release date `25 October 2019`;
- developer `Archpray`;
- publisher `Rayark`;
- PC among listed platforms;
- a dedicated user-review area.

A concrete Russian-language user review is directly reachable at the stable non-profile item URL:

`https://stopgame.ru/game/mo_astray/review/10186`

The item is dated `2023-12-26`. It contains concrete player feedback about durable game traits including story presentation, pixel-art presentation and side-scrolling gameplay. It also mentions Russian translation/localization, but because the item is older than 365 days that old localization statement must not be used as current-state evidence without a separate recent check.

This is the cleanest contract-usable non-Steam item found.

### StopGame user/community blog — usable secondary lead for durable traits

A public user/community blog post dated `2025-08-01` contains a concrete Russian MO:Astray mini-review within a multi-game roundup:

`https://stopgame.ru/blogs/topic/118581/moyigroiyul2025`

The same representation includes an embedded exact `MO:Astray` game card with the 2019 release identity and PC among platforms. The post gives concrete player feedback about gameplay interest, story, visual presentation and reading-heavy mechanics.

The post is older than 365 days at the diagnostic date, so it is suitable only for durable traits, not current technical/localization state.

### Reddit Russian community — concrete lead, locator unresolved

A Russian-language `r/ru_gamer` thread contains a concrete player comment naming `Mo astray`, describing it as a 2D pixel puzzle game with a story and saying the player liked it.

The comment body was visibly inspectable, but the current transport did not expose a safely resolvable stable child permalink from that representation. The thread itself is a broad multi-game discussion, not an exact-product collection parent suitable for transient-author fallback. Therefore this lead was not needed and is not counted as contract-usable here.

### Google Play store user reviews — concrete Russian reviews, rejected for this PC/Steam dossier identity

The public Google Play page for `MO: Astray` by Rayark exposes multiple concrete Russian-language user reviews.

However, that surface is explicitly the later mobile version/port, while the dossier target is the 2019 Steam work identity bound to appid `1104660`. Because the active evidence contract forbids cross-release combination and requires exact work identity, these mobile-port reviews were conservatively rejected for this dossier rather than used to bridge platform/version differences.

### DTF / iXBT / 4PDA / Pikabu / VK

Site-specific discovery queries were executed. No stronger contract-usable exact-product Russian/mixed concrete player-feedback item was surfaced within the diagnostic budget.

### GameFAQs / MobyGames and similar database surfaces

Broad discovery surfaced exact-product database/review pages, but the returned representations did not expose a Russian concrete player review usable for the Russian gate. Aggregate/player-score or critic-only material was not treated as player-feedback evidence.

## 6. Candidate ledger

No username, display name, account ID, profile URL, author hash, or raw long review body is persisted below.

| ID | Source/platform | Exact product identity | Actual player feedback | Concrete content visible | Language | Stable safe locator | Safe parent/container | Date | Current contract usability | FIRST rejection reason if unusable | Classification |
|---|---|---:|---:|---:|---|---:|---:|---|---|---|---|
| NS-RU-01 | StopGame dedicated user review | yes | yes | yes | Russian | yes — dedicated `/game/mo_astray/review/10186` item URL | yes — exact MO:Astray game/review surface | 2023-12-26 / old | **yes**, for durable traits | n/a | `contract_usable_stable_locator` |
| NS-RU-02 | StopGame user/community blog post | yes | yes | yes | Russian | yes — stable topic URL | yes — concrete post itself; exact MO:Astray card/segment visible | 2025-08-01 / old | **yes**, for durable traits | n/a | `contract_usable_stable_locator_secondary` |
| NS-RU-03 | Reddit Russian community comment | yes by explicit title/context | yes | yes | Russian | no safely resolved child permalink in current representation | no exact-product fallback parent; broad multi-game thread only | ~2025 / old | no | stable child locator not resolved and broad thread is not an exact-product fallback parent | `locator_unresolved_nonblocking` |
| NS-RU-04 | Google Play store user reviews | same game lineage but later mobile port | yes | yes | Russian | collection surface; no per-review stable item used | store page is safe | 2021–2022 / old | no for this dossier | cross-release/platform-version identity is not proven equivalent to the exact Steam appid-bound target | `cross_release_identity_rejected` |

## 7. Concrete usable non-Steam item(s)

### Primary usable item

`NS-RU-01` is contract-usable as-is:

- exact MO:Astray game entity;
- exact release identity corroborators on the same site: 2019, Archpray, Rayark, PC;
- actual player-authored review rather than editorial/professional content;
- Russian language is established from the concrete feedback item itself;
- dedicated stable non-profile item URL;
- no author/profile identity is needed or persisted;
- raw review body does not need to be persisted;
- old date is compatible with durable gameplay/story/art findings.

It can satisfy the Russian gate by binding at least one durable observation to the Russian feedback record and setting `evidence.russian_attempt=found_and_used`.

The old localization statement on that item must not be serialized as a current localization fact without separate recent support.

### Secondary usable item

`NS-RU-02` provides an additional stable public Russian player/community item for durable traits. It is not required to establish the primary result because `NS-RU-01` already closes the Russian retrieval gate.

## 8. Production-strategy reachability assessment under current 8/16 budget

**The current production worker should already be able to find the primary StopGame item within the existing 8-search / 16-page per-game ceiling.**

Evidence:

1. The active prompt already requires source-agnostic diversification after exact-product Russian existence proof.
2. It explicitly prioritizes materially different public player-feedback surface classes over repeated same-surface aggregate/list attempts.
3. It explicitly permits relevant site-specific player-feedback/community searches when ordinary search does not resolve the Russian attempt.
4. The diagnostic control query using the current identity pattern — exact `MO:Astray` + `2019` + Russian `отзывы игроков` wording — surfaced the StopGame game page directly.
5. From that result, one page open exposes the review list and one child click opens the stable dedicated review item.

Thus the usable route is reachable with approximately:

- 1 search query;
- 2 opened/read pages;

once the worker enters non-Steam diversification. It does not require exhausting the 8/16 ceiling.

No new provider, crawler, retry loop or named-site quota is needed for this exact game.

## 9. Primary blocker/result classification

**Primary result: `non_steam_usable_found`.**

Reason:

- at least one exact-product Russian concrete non-Steam player-feedback item is safely reachable;
- the strongest item has a stable non-profile item URL;
- the current evidence/privacy model already permits its source class and locator shape;
- current worker guidance already requires the diversification that discovers it;
- no generic strategy gap is demonstrated.

This is not `strategy_diversification_gap`: the current prompt already contains the needed generic diversification rules, and an ordinary exact-title/year Russian player-review query reaches the usable source inside budget.

This is not `external_transport_limitation`: although the prior Steam Community child path remains transport-blocked, MO:Astray's Russian gate does not depend on that Steam child once the StopGame item is used.

This is not `contract_contradiction`: the existing source policy and compact-provenance rules accept this shape without relaxation.

## 10. Whether current contract is internally consistent

**Yes.**

The relevant active rules align:

- ordinary multi-source player-feedback research is active;
- allowed player-feedback source classes include `forum`, `store_user_reviews`, `community_discussion`, `reddit` and `other_player_feedback`;
- a stable non-identifying item URL is the preferred feedback identity;
- collection/index pages alone are not feedback records;
- author/profile identity must not persist;
- Russian language must come from the concrete bound item;
- old feedback remains valid for durable gameplay/story/pacing/structure traits;
- current technical/localization state requires recent support;
- exact work identity remains fail-closed.

The StopGame dedicated review fits these rules without exception.

## 11. Whether any contract change is justified

**No.**

No evidence, privacy, exact-product, language, recurrence, provenance or recency rule needs to be weakened or extended.

In particular, no reason exists to:

- allow profile-scoped identity;
- turn aggregate counts into feedback records;
- relax stable-locator requirements;
- treat mobile-port reviews as automatically equivalent to the Steam appid-bound target;
- add a StopGame-specific contract rule.

The existing generic multi-source model is sufficient.

## 12. Whether external retrieval capability is still needed

**Not for MO:Astray's Russian gate.**

The previously proposed external Steam Community child-link capability may still be relevant to the separate general Steam transport problem, but this diagnostic does not justify requiring it for MO:Astray.

For this exact target, current public-web tooling plus the existing multi-source strategy already exposes a legal non-Steam Russian item.

Therefore no new external retrieval provider is necessary to unblock MO:Astray.

## 13. Minimal next-step direction

Use the existing production worker and current multi-source contract without modification.

A clean live acceptance should verify that, after Steam existence proof and failed Steam item retrieval, the worker actually diversifies to the reachable StopGame user-review path and completes MO:Astray with `found_and_used`.

No prompt/contract/provider implementation should precede that acceptance.

## 14. Unresolved

- This diagnostic does not prove which exact search query/order the Scheduled runtime will choose on its next live invocation; it proves the usable source is reachable under the existing strategy and comfortably inside the current budget.
- The prior Steam Community child-link transport limitation remains real as a separate general capability issue, but it is no longer a blocker for this exact MO:Astray Russian gate.
- Canonical progress currently reports expected sequence `7` while prior live transport reportedly buffered through `g000010`; the Scheduled worker must continue to respect GitHub-owned buffered validation/recovery and must not skip or overwrite earlier expected artifacts.
- Google Play mobile-port feedback was conservatively left unused because cross-release/platform identity was not required to close the gate and need not be relaxed.

## 15. Status

`complete_non_steam_usable_found`

## 16. Exactly one recommended next step

Perform **one clean live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task under the current canonical prompt/contract, after the GitHub-owned control plane has made the relevant traversal state live for `g000011`, and verify that MO:Astray resolves through the existing non-Steam multi-source path rather than changing contracts or adding a retrieval provider first.**

Do not run that Scheduled Task from this diagnostic.

## 17. Efficiency / reusable lesson

The reusable lesson is that the architecture decision should not be made from a Steam-only failure once the active contract is explicitly source-agnostic.

For a proven exact-product Russian existence signal:

1. attempt the preferred Steam item path only within the existing bounded strategy;
2. if it remains aggregate/profile/index-only, pivot early to one generic exact-title + release-year + Russian player-review query across public non-Steam surfaces;
3. inspect stable item-level results before considering new transport capability;
4. only return to external-provider architecture when materially diverse non-Steam discovery is also unavailable or transport-blocked.

For MO:Astray, that early generic diversification exposes a dedicated StopGame user-review item and avoids an unnecessary Steam-specific architecture escalation.
