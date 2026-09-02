# cross-platform-giveaway-separate-view-fix-01

## User preference implemented

Real-device feedback superseded the previous inline/accordion direction. The giveaway surface is no longer embedded or expandable inside the paid feed.

Implemented release commit:
- `b5a72815abae47cb1570b4704e43f9aef09c5cb6` — `giveaways: move to separate Wishlist-style view`
- PR: `#12`

The net implementation diff is limited to:
- `web/index.html`
- `web/giveaway-ui.js`
- `web/giveaway-ui.css`
- `web/giveaway-ui.test.js`

No giveaway source/classification code, paid ranking/Taste code, scheduler, writer, or browser data route was changed.

## Main navigation

The main page now exposes one compact navigation control in the same existing tab family as Wishlist:

`🎁 Раздачи (N)`

Behavior:
- there is no giveaway list, detail content, or accordion inside `#feedView`;
- the existing paid card/position/swipe surface remains the first content of `#feedView`;
- the giveaway control uses the existing `.tab` / `data-tab` interaction family;
- active snapshot shows the current active game count;
- complete empty snapshot shows `(0)`;
- unavailable/updating state shows `(!)` rather than inventing a successful empty state;
- selecting another normal tab closes the giveaway view;
- the explicit `← Назад` control returns through an existing tab, with feed as the safe fallback.

The single browser data dependency is preserved: `web/app.js` still loads only `data/current.json`. No direct `data/production/giveaways/**` fetch was added.

## Giveaway view

A dedicated `#giveawayView` now owns the giveaway list, parallel in page structure to the existing Wishlist/Interested/Final list views.

Each active game is intentionally compact and contains only:
- title;
- storefront;
- absolute deadline;
- live time-remaining text;
- compact exact `Забрать` CTA;
- `Подробнее`.

The list does **not** show description/pros/cons or the analysis-gap explanation. Multi-store offers remain grouped under the canonical giveaway game row and all exact claim CTAs are retained.

Freshness and expiry remain fail-closed at render time:
- stale/malformed/unavailable payload => unavailable state and no CTA;
- complete empty => truthful empty state;
- offers whose `promotion_end_utc` has passed are removed;
- if all formerly active offers expire before the next repository refresh, the view becomes `updating`, not false empty;
- the renderer schedules an in-page refresh at the next known offer/freshness boundary without another network fetch or scheduler.

## Detail card

`Подробнее` opens a separate one-game detail surface; the compact giveaway list is hidden until `← К раздачам` is used.

The detail contains only the selected game plus its exact active storefront/deadline/claim CTA rows.

The already-proven identity limitation from the preceding task was **not** re-researched. No Epic/GOG -> Steam title/fuzzy binding was added and raw Steam analysis is not consumed merely because a name looks the same.

Because there is still no proven canonical analysis binding for the current Epic giveaway games, the detail shows one concise honest incomplete-analysis state covering the requested fields:

`Описание, плюсы и минусы пока недоступны: нет подтверждённой связи этой версии игры с каноническим анализом. По одному совпадению названия данные не подставляем.`

Tests inject fake unsafe `steam_analysis` text and assert that none of it appears in either list or detail.

## Validation

Deterministic/UI coverage in `web/giveaway-ui.test.js` now verifies:
- compact active navigation count;
- giveaway content absent from `#feedView`;
- dedicated giveaway view exists alongside existing Wishlist view;
- compact list rows have title/store/deadline/time remaining/claim CTA/`Подробнее`;
- description/pros/cons are absent from list;
- one selected detail excludes other games;
- back-to-list route exists;
- exact claim URL/deadline is retained in detail;
- honest incomplete-analysis state appears only in detail;
- injected title-only Steam analysis cannot leak into UI;
- empty/unavailable/stale/expired behavior stays fail-closed;
- multi-store offers remain under one game;
- pure giveaway rendering does not mutate a paid queue/Wishlist state fixture;
- `app.js` keeps its sole `data/current.json` production fetch and existing Wishlist tab behavior.

### Current production sample

Canonical current snapshot at validation time:
- contract: `CROSS-PLATFORM-GIVEAWAY-V1`;
- snapshot: `complete`;
- fresh until: `2026-09-03T02:47:04.954912Z`;
- Steam: complete, 0 accepted;
- Epic: complete, 2 accepted;
- GOG: complete, 0 accepted;
- unverified: 0.

Current giveaway view therefore renders two compact rows:
1. `Breathedge` — Epic Games — exact Epic claim URL — promotion end `2026-09-03T15:00:00Z` — `Подробнее` opens only its detail with the honest incomplete-analysis state.
2. `Rival Stars Horse Racing : Desktop Edition` — Epic Games — exact Epic claim URL — promotion end `2026-09-03T15:00:00Z` — `Подробнее` opens only its detail with the same honest incomplete-analysis state.

No Steam analysis is copied into either game on title equality.

### Production deploy

Release commit:
- `b5a72815abae47cb1570b4704e43f9aef09c5cb6`

Canonical Pages deploy:
- workflow: `Deploy visual mailing`
- run: `33593558792`
- job: `100132318846`
- conclusion: `success`
- giveaway payload validation: `PASS`, `state=active`, `offers=2`, `fresh_until=2026-09-03T02:47:04.954912Z`
- paid visual acceptance: reused existing canonical payload with structural giveaway-only proof;
- UI regressions: `image swipe regression: PASS`, `compact purchase options mobile regression: PASS`, `detailed score mobile regression: PASS`, `GIVEAWAY_UI_TESTS=PASS`;
- `web/data/current.json` was staged from the canonical precomputed visual payload;
- GitHub Pages deployment reported `success` for `b5a72815abae47cb1570b4704e43f9aef09c5cb6`.

An automatic `Build daily visual payload` push run also started:
- run: `33593558890`
- giveaway handoff test: `PASS`;
- generated giveaway visual payload validation: `PASS`;
- it then failed in the unrelated general paid-card gate `Require meaningful Russian descriptions before canonical commit` because `129/433` paid visible cards were reported missing a meaningful Russian description.

That general-build failure did not change or invalidate this web-only release: the dedicated Pages workflow separately validated the already-canonical giveaway payload, proved the paid visual state unchanged, ran all UI regressions, staged the payload, and deployed successfully. No new visual payload mutation was required for the separate-view UX change.

## User verification

Real-device acceptance is still mandatory. On phone verify:
1. the normal feed has no giveaway panel/list consuming vertical space;
2. `🎁 Раздачи (2)` is visible as a compact navigation control comparable to Wishlist;
3. one tap opens a separate compact giveaway list rather than expanding content in the feed;
4. each row stays compact and `Подробнее` opens only that game's detail;
5. the detail shows store/deadline/claim CTA plus the honest incomplete-analysis state, and `← К раздачам` returns to the list;
6. `← Назад` / normal tabs return cleanly and paid swipe state, Wishlist, Interested and Final remain visually and behaviorally intact.

Efficiency / reusable lesson: for auxiliary mobile surfaces with list -> detail interaction, reuse the existing top-level tab/list-view navigation family and keep heavy explanatory content out of both the paid feed and compact list.

## Status

`needs_user_verification`

## Recommended next step

Perform the six phone checks above on the deployed Pages build; only after that acceptance should this UX fix be marked complete.
