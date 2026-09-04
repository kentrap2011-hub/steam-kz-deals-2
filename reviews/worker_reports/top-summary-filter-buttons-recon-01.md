# TOP SUMMARY FILTER BUTTONS RECON 01

## Status

`complete`

READ-ONLY / RECON выполнен. Runtime frontend, tests, giveaway cache/fallback, deployment workflow и service-worker не изменялись. Единственная запись по задаче — этот report.

Ключевой вывод: верхние `Новые / Не смотрел / Интересно / Видел` сейчас не являются controls. Их DOM создаётся заново `renderStats()` внутри `web/app.js`. Текущие данные для всех четырёх состояний уже существуют в одном local UI state, но готовый view/action на `main` существует только для `Интересно`. Для `Новые`, `Не смотрел`, `Видел` есть готовые canonical predicates/count semantics, но нет готовых filter views/actions. Поэтому безопасный IMPLEMENT должен расширить существующий `currentTab`/feed-view transition, а не создавать второй `filterState`.

## Files inspected

Required / task context:
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_RECON_01.md`
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `CURRENT_TASK.md`

Current frontend / navigation:
- `web/index.html` — current sha `56e92cd99c9a63eaa4f5cd470464652a4751ac8f`
- `web/app.js` — current sha `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5`
- `web/styles.css` — current sha `83c76da6a48589adeca51be0a63ef43e270a7df9`
- `web/giveaway-ui.js` — current sha `dd3cf650d94d996d12cca466620a0c5109ab3ecf`

Relevant regression / deploy boundary:
- `tests/feed-bootstrap.test.js` — current sha `f4ec8a8d4165cbacdef67a27587494e07972c307`
- `scripts/test_feed_bootstrap_cache_identity.js` — current sha `91b3701ac5b974e0337a756c7d4f350d05e9eb7f`
- `.github/workflows/deploy-visual.yml` — current sha `8f4a82148b6c3607cc77b008eaa0d1cb93c89514`
- current `web/` test inventory (including `web/giveaway-ui.test.js`, `web/image-swipe-sync.test.js`, `web/package-deal-ui.test.js`, `web/score-details-ui.test.js`).

No Git history / Actions sweep was performed.

## Current implementation map

### Top summary DOM

`web/index.html` contains only the empty mount point:

- `#stats.stats`

The four cards do **not** live as static nodes in `index.html`. `web/app.js::renderStats()` replaces `#stats.innerHTML` on every render with four non-interactive `<div class="stat">` elements.

Current render order and exact semantics come from `counts()`:

1. `Новые` -> `c.newCount`
2. `Не смотрел` -> `c.unseen`
3. `Интересно` -> `c.liked`
4. `Видел` -> `c.repeat`

Current predicates/data:

- `isNew(id)` -> `rec(id).first_source === data.source_mailing_updated_at_utc && rec(id).seen === 0`
- unseen -> `(rec(id).seen || 0) === 0`
- liked -> `rec(id).status === 'liked'`
- seen/repeat -> `(rec(id).seen || 0) > 0`

These categories are not necessarily mutually exclusive. In particular `Новые` is a subset of unseen for the current source snapshot, and `liked` status is independent of `seen`.

### Existing navigation below summary

`web/index.html` currently has `.tabs` with:

- `data-tab="feed"`
- `data-tab="giveaway"`
- `data-tab="wishlist"`
- `data-tab="liked"` -> visible lower `♡ Интересно` duplicate intended for removal
- `data-tab="final"`

The separate card action `#likeBtn` is **not** the duplicate to remove. It calls `markCurrent('liked')` and changes the current game's status. It must remain because it is the write/action that lets the user mark a game as interesting.

The removable duplicate is `button.tab[data-tab="liked"]` in the upper navigation area. Its current function is only to open the liked list.

### Existing view state

`web/app.js` has one existing view selector:

- `let currentTab = 'feed'`

Existing `.tab` click wiring is:

- `currentTab = b.dataset.tab`
- `render()`

`renderTabs()` currently switches these app-owned views:

- `feedView`
- `wishlistView`
- `likedView`
- `finalView`

`giveawayView` is managed separately by `web/giveaway-ui.js`.

Persistent local state remains in the existing `state` object loaded from localStorage:

- `state.games[id].status`
- `state.games[id].seen`
- `state.games[id].first_source`
- `state.queue.ids/cursor`
- `state.settings.urgency_first`

No additional filter state is needed or recommended.

## Existing filter/action map

| Summary item | Existing data/predicate | Existing control/action today | Can reuse directly? |
|---|---|---|---|
| `Новые` | `isNew(id)` | none; count/badge only | **No direct action.** Reuse predicate + existing `currentTab`/feed transition. |
| `Не смотрел` | `(rec(id).seen || 0) === 0` | none; count only | **No direct action.** Reuse predicate + existing `currentTab`/feed transition. |
| `Интересно` | `rec(id).status === 'liked'` | `.tab[data-tab="liked"]` -> `currentTab='liked'` -> `render()` -> `likedView` | **Yes.** This is the exact lower navigation action to move to the top summary control. |
| `Видел` | `(rec(id).seen || 0) > 0` | none; count/repeat badge only | **No direct action.** Reuse predicate + existing `currentTab`/feed transition. |

Important discrepancy found by RECON: `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md` describes existing representations for all four categories, but current `main` only has an actual `liked` view/action. The other three meanings already exist in the single source-of-truth state, but their filter transitions do not. IMPLEMENT must not pretend those actions already exist and must not introduce a parallel filter model.

## Recommended DOM event wiring

### 1. Render real controls from `renderStats()`

Because `renderStats()` replaces `#stats.innerHTML` every render, the four generated nodes should become semantic buttons, for example using one shared attribute namespace such as:

- `data-summary-filter="new"`
- `data-summary-filter="unseen"`
- `data-summary-filter="liked"`
- `data-summary-filter="seen"`

Keep the existing `.stat` class so the current visual layout remains intact. Add active/pressed semantics from the same `currentTab` state (`active` class and/or `aria-pressed`). Do not store active summary state separately.

### 2. Bind once on `#stats` via event delegation

Do **not** attach four listeners inside every `renderStats()` call, because those nodes are destroyed/recreated on each render.

Recommended bounded wiring:

- one permanent click listener on `#stats`;
- resolve `event.target.closest('[data-summary-filter]')`;
- pass the declared target to one existing-view activation helper.

### 3. Centralize the current tab transition

The existing `.tab` listener and the new summary listener should use one small transition helper rather than duplicating `currentTab=...; render()` branches.

Safe mapping:

- `liked` -> existing `currentTab='liked'` and existing `likedView`;
- `new` -> feed mode derived from `isNew(id)`;
- `unseen` -> feed mode derived from `seen===0`;
- `seen` -> feed mode derived from `seen>0`.

The helper may extend the existing `currentTab` enum with `new`, `unseen`, `seen`. This is still the same existing view state variable and does **not** require a new localStorage field, schema version, `filterState`, or second source of truth.

### 4. Derive filtered feed IDs; never rewrite canonical queue ownership

For `new/unseen/seen`, derive the active IDs from the already ordered `state.queue.ids` and existing record predicates. Do not mutate/rebuild `state.queue.ids` merely to apply a UI filter.

Recommended invariant:

- canonical local ordering stays in `state.queue.ids`;
- summary filter only derives an in-memory subset in that same order;
- `state.queue.cursor` remains the only stored cursor and points to the corresponding full-queue ID;
- no filter key is persisted to localStorage.

Navigation helpers that currently assume every `state.queue.ids` entry is visible will need bounded adaptation for filtered feed modes: current item alignment, next/previous, start, visible position/count, and empty-filter case. `feedCount` should continue to represent the full feed; the four summary counters already represent the filtered subset counts.

### 5. Preserve card status action

`#likeBtn` / `markCurrent('liked')` must remain untouched semantically. It is the action that creates liked state; the top `Интересно` summary button only opens the existing liked view.

## Lower duplicate removal plan

Remove only this visible navigation element from `web/index.html` after top `Интересно` works:

- `button.tab[data-tab="liked"]` containing `♡ Интересно <span id="likedCount">...`

Keep:

- `#likedView`
- `#likedList`
- `#likeBtn`
- liked status handling in `markCurrent('liked')`
- liked count in the top summary card.

Necessary follow-up inside `web/app.js` at the same time:

- `renderStats()` currently writes to `$('likedCount').textContent` unconditionally. Once the lower nav button is removed, that element no longer exists. Remove that redundant assignment or null-guard it; otherwise render will throw.

Do not remove the liked view itself. The upper `Интересно` summary card should become its sole visible entry point in the top navigation area.

## Relevant tests/scripts

There is currently **no focused regression for `web/app.js` summary/filter navigation**. Existing UI regressions in deploy are:

- `node web/image-swipe-sync.test.js`
- `node web/package-deal-ui.test.js`
- `node web/score-details-ui.test.js`
- `node web/giveaway-ui.test.js`
- `node scripts/test_feed_bootstrap_cache_identity.js`

`tests/feed-bootstrap.test.js` is an additional cache-first/bootstrap behavior suite but is not currently listed in the deploy workflow's `Run UI regressions` step.

### Minimum new regression recommended

Add one focused Node regression, preferably `web/top-summary-filter-buttons.test.js` (or an equivalently named deterministic script), covering at minimum:

1. four summary controls are rendered with `new/unseen/liked/seen` mappings and current real counts;
2. `new` uses `isNew` semantics;
3. `unseen` uses `seen===0`;
4. `liked` enters the same existing `likedView/currentTab='liked'` path previously used by the lower tab;
5. `seen` uses `seen>0`;
6. active state follows the same `currentTab`, with no independent filter state;
7. filtered feed navigation keeps `state.queue.ids` order/contents unchanged;
8. empty filtered subset shows the existing empty-feed state rather than a stale card;
9. lower `.tab[data-tab="liked"]` is absent while `#likeBtn` and `#likedView` remain;
10. repeated `renderStats()` does not duplicate handlers (delegated listener invariant).

Register this focused test in `.github/workflows/deploy-visual.yml::Run UI regressions` so it is part of the existing UI deploy gate.

Minimum IMPLEMENT verification commands:

- `node --check web/app.js`
- `node web/top-summary-filter-buttons.test.js`
- `node web/giveaway-ui.test.js`
- `node scripts/test_feed_bootstrap_cache_identity.js`
- then the existing full `Run UI regressions` deploy step.

A production mobile check remains required by the queued IMPLEMENT task before final UX acceptance.

## Giveaway fix interaction assessment

### Cache/fallback logic

No semantic conflict was found with the active giveaway/feed cache fix **if this task remains within the bounded files below**.

Current cache identity regression is isolated in:

- `web/feed-bootstrap.js` (bootstrap/cache implementation; referenced by the test)
- `scripts/test_feed_bootstrap_cache_identity.js`
- cache-first behavior is also covered by `tests/feed-bootstrap.test.js`

The giveaway cache identity test explicitly treats giveaway publication fields as part of payload identity and verifies cached feed remains usable on refresh failure. The summary-filter task does not need to change payload identity, cache storage, cache fetch interception, freshness, giveaway fields, or fallback behavior.

Do not edit:

- `web/feed-bootstrap.js`
- `scripts/test_feed_bootstrap_cache_identity.js`
- `tests/feed-bootstrap.test.js`
- giveaway producer/cache payload fields

for this task.

### Shared-file / sequencing risk

There is one **file-level sequencing overlap**, not a logic conflict: `web/index.html` currently contains the cache-busted `feed-bootstrap.js?v=mobile-feed-instant-cache-fix-01` asset wiring and giveaway asset wiring. This task also needs `web/index.html` to remove the lower liked tab and likely bump only its own app/styles asset version.

Therefore the queued instruction to implement only after the giveaway fix is accepted is correct. When IMPLEMENT starts from the accepted `main`, edit only the liked-tab markup / this task's app+style asset refs. Do not rewrite or roll back `feed-bootstrap.js` / giveaway query versions.

### Giveaway view navigation boundary

`web/giveaway-ui.js` binds capture listeners to existing `.tab` buttons and keeps its own `returnTab`. Dynamically generated summary buttons are not part of that binding. This does not require editing giveaway code, but the focused UI regression should prove that:

- summary clicks do not leave `giveawayView` visibly stacked with the selected app view;
- giveaway tab still opens/closes normally after lower liked tab removal;
- cache refresh does not reset the selected non-giveaway `currentTab`/summary mode.

If preserving exact "return to liked/filter after leaving giveaway" cannot be achieved from `web/app.js` without changing giveaway internals, treat that as a bounded navigation follow-up rather than modifying giveaway cache/fallback machinery in this task.

Assessment: **no cache/fallback conflict; minor shared `index.html` merge/asset-wiring risk, so implement after giveaway fix acceptance and keep giveaway files read-only.**

## Bounded IMPLEMENT plan

One bounded implementation, in order:

1. **Start from accepted post-giveaway-fix `main`.** Re-read `web/index.html`, `web/app.js`, `web/styles.css`, `.github/workflows/deploy-visual.yml` only to account for intervening accepted changes.
2. **`web/app.js`: centralize existing view transition** around `currentTab`; extend the same variable with `new/unseen/seen`; derive matching feed IDs from existing `state.queue.ids`, `isNew`, and `rec(id).seen`; do not add localStorage fields or mutate canonical queue order for filtering.
3. **`web/app.js`: make `renderStats()` emit four semantic buttons** and add one delegated `#stats` listener. Active state comes only from `currentTab`.
4. **`web/app.js`: adapt only the feed navigation assumptions required by filtered modes** (current item alignment, next/previous, start, visible position/count, empty subset), preserving full queue contents/order and `manual_end_at` behavior.
5. **`web/index.html`: remove only `.tab[data-tab="liked"]`** after the upper liked transition works. Keep `#likeBtn`, `#likedView`, and `#likedList`. Remove/guard the now-missing `#likedCount` write in app code. Do not alter giveaway/feed-bootstrap wiring except this task's own app/style cache-bust refs if needed.
6. **`web/styles.css`: add only button-reset/click affordance and active-state styling for `.stat`**, reusing current card colors/borders; no redesign.
7. **Add one focused regression** `web/top-summary-filter-buttons.test.js` and register it in `.github/workflows/deploy-visual.yml::Run UI regressions`; include the four mappings, queue non-mutation, lower duplicate removal, and handler-idempotence checks.
8. **Run bounded validation:** syntax check, new focused test, giveaway UI test, giveaway cache identity test, then full existing UI regression gate. Deploy only after all pass; require the queued real-mobile user check before final UX acceptance.

Expected implementation files:

- `web/app.js`
- `web/index.html`
- `web/styles.css`
- new `web/top-summary-filter-buttons.test.js`
- `.github/workflows/deploy-visual.yml` (only to register the new regression)

Expected files **not** to change:

- `web/feed-bootstrap.js`
- `web/giveaway-ui.js`
- `web/giveaway-ui.css`
- `scripts/test_feed_bootstrap_cache_identity.js`
- `tests/feed-bootstrap.test.js`
- producer/cache/backend files
- service worker / deployment machinery outside the one existing UI-test command list

## Risks / unknowns

1. **Task text vs current code:** only `liked` has a real existing filter/view action. `new/unseen/seen` have existing state semantics but no existing direct controls/views. Any IMPLEMENT claiming "direct reuse" for all four without adding bounded logic to the existing `currentTab` path would be inaccurate.
2. **Filtered feed cursor semantics:** `state.queue.cursor` is an index into the full ordered queue. A derived subset must map back to full IDs/indexes; never replace `state.queue.ids` with the filtered set.
3. **Seen mutation while filtering:** navigation calls `markSeen()`. In `new`/`unseen` modes the item can immediately stop matching the current filter, so next/previous logic must choose/re-align deterministically and avoid stale-card display.
4. **Liked duplicate identity:** remove the top-navigation `.tab[data-tab="liked"]`; do not remove `#likeBtn`, because that would remove the user's ability to mark a game interesting.
5. **Giveaway return behavior:** removal of the visible liked tab means `giveaway-ui.js::returnTab` can no longer discover liked through `.tab.active`. This is not a cache conflict, but must be covered by a navigation regression and must not be solved by modifying giveaway cache/fallback code inside this task.
6. **Asset cache-bust overlap:** `web/index.html` currently carries query versions for the accepted/active giveaway/feed bootstrap work. IMPLEMENT must preserve those exact accepted refs while changing only its own relevant assets.

## Final assessment

- Recon status: `complete`
- Directly reusable existing summary action: `Интересно -> currentTab='liked' -> likedView`
- Existing reusable state semantics for the other three: yes (`isNew`, `seen===0`, `seen>0`)
- Existing direct actions for the other three: no
- New parallel filter state required: no
- Giveaway cache/fallback conflict: no
- Shared file/merge risk with current giveaway fix: yes, limited to `web/index.html`; sequencing after giveaway acceptance is required
- Safe next step: execute the single bounded IMPLEMENT plan above after the giveaway fix is accepted on `main`.
