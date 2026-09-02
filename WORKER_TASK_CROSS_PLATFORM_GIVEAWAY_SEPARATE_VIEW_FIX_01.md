# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-separate-view-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/cross-platform-giveaway-separate-view-fix-01.md`

## Context

This supersedes the not-yet-accepted giveaway UX direction based on the user's latest real-device preference.

Do NOT implement the previously proposed nested expandable-list UX as the final design.

User preference:
- the main feed should NOT contain a permanently visible giveaway block or an expandable giveaway list;
- the desired interaction should follow the existing **Wishlist** pattern already present in the product: a compact dedicated button/tab on the main navigation surface opens a separate view/page-mode containing the giveaway list;
- description / pros / cons belong in a separate game detail card, not inline in the giveaway list.

This is a direct UI continuation. Do not repeat giveaway source recon or cross-store identity recon.

## Goal

Make giveaways a separate first-class read-only view, visually and behaviorally analogous to the existing Wishlist view.

## Required behavior

### A. Main screen

Remove the large/expandable giveaway content from the main feed surface.

Add or reuse a compact navigation control in the same interaction family as the existing Wishlist control, e.g. `🎁 Раздачи (2)` / `Бесплатно (2)` according to existing naming/style constraints.

Requirements:
- compact, always discoverable;
- shows current active count when trustworthy;
- does not consume feed viewport height beyond the navigation control itself;
- no inline giveaway rows under the main navigation;
- paid feed starts immediately below its normal controls, as before.

### B. Separate giveaway view

Tapping the giveaway control opens a dedicated giveaway view/mode using the **same existing view-switch/navigation pattern as Wishlist** where practical.

Inspect the current Wishlist implementation only as needed and reuse its established UI state/navigation conventions rather than inventing a parallel router.

The giveaway view should contain:
- page/view heading;
- compact list of active giveaways;
- one compact row/card per game with title, storefront, deadline/time remaining;
- compact `Забрать` CTA;
- compact `Подробнее` / row-selection affordance;
- truthful `empty` / `unavailable` states.

Do not render long analysis bodies inline in the list.

### C. Per-game detail card

Selecting a giveaway game from the dedicated list opens a separate detail surface/card for that game only.

Detail contains:
- title;
- storefront / deadline;
- claim CTA;
- `Описание`;
- `Плюсы`;
- `Минусы`;
- back/close control returning to the giveaway list.

Only one giveaway detail is visible at a time.

### D. Current analysis limitation

The previous worker already proved that no safe canonical Epic/GOG -> Steam analysis identity binding currently exists.

Do not repeat that recon.
Do not bind by title/fuzzy match.
Do not fabricate analysis.

Until a safe cross-store analysis identity exists, the detail card should contain one concise honest incomplete-analysis state. Keep this text contained in the detail view, not repeated in the list.

The richer real description/pros/cons requirement remains a separate identity/analysis continuation; this task is primarily the correct navigation/layout implementation.

### E. Navigation/state behavior

Match existing Wishlist-style behavior where possible:
- entering giveaway view hides the normal paid feed view rather than pushing it downward;
- back/navigation returns to the previous/main feed state;
- giveaway navigation must not mutate paid swipe position, ranking, Wishlist, Interested, Final, or card state;
- switching between Wishlist / Giveaway / normal feed must preserve each existing state according to current app conventions.

### F. Data ownership

Keep the existing single payload route:

`data/production/giveaways/v1/current.json`
→ canonical giveaway visual handoff
→ `data/production/visual/current.json`
→ Pages deploy
→ `web/data/current.json`
→ existing web app.

No second browser fetch, writer, scheduler, or hand-curated store mapping.

## Validation

Add deterministic regressions for at least:
- main feed has no expanded/inline giveaway list;
- giveaway nav control is compact and displays trusted count/state;
- tapping control enters separate giveaway view;
- dedicated view lists all current active offers compactly;
- back returns to the prior feed state;
- selecting a row opens only that game's detail card;
- detail close/back returns to giveaway list;
- incomplete analysis appears only in detail, not list;
- CTA/deadline remain correct;
- stale/expired/unavailable fail closed;
- no title/fuzzy Steam analysis binding;
- paid/Wishlist/Interested/Final state is not mutated;
- existing Wishlist navigation still works unchanged.

Then run the smallest canonical production visual/UI validation and Pages deploy needed for the change.

## Real-device acceptance — mandatory

After deploy, status must be `needs_user_verification`.

User verifies on phone:
1. main feed no longer contains giveaway content block;
2. there is a compact giveaway button/tab analogous to Wishlist;
3. tapping it opens a separate giveaway screen/view with a compact list;
4. tapping a game opens its separate detail card;
5. back navigation works naturally;
6. Wishlist and normal paid feed still behave as before.

Do not call complete before this check.

## Hard boundaries

Do NOT:
- keep the nested expandable giveaway list as the final UX;
- repeat source or cross-store identity recon;
- title/fuzzy-match Steam analysis;
- fabricate description/pros/cons;
- add a second browser data route;
- change paid ranking/Taste logic;
- weaken freshness/expiry rules.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-separate-view-fix-01.md`

### User preference implemented
How the Wishlist-style separate-view behavior is matched.

### Main navigation
Exact control/state behavior.

### Giveaway view
Exact compact list behavior.

### Detail card
Exact per-game behavior/content.

### Validation
Tests/build/deploy refs.

### User verification
Exact phone checks.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_verification`

### Recommended next step
One bounded next step only.