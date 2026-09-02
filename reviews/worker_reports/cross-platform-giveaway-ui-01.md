# cross-platform-giveaway-ui-01

## Task

Implement the user-facing cross-platform giveaway block through the existing canonical visual payload and Pages route, without a second browser fetch or participation in paid-game ranking/swipe/final/wishlist state.

## Canonical handoff

Implemented route:

`data/production/giveaways/v1/current.json`
→ `scripts/giveaway_visual_handoff.py`
→ `scripts/build_final_visual_payload.py`
→ `data/production/visual/current.json`
→ existing Pages deploy copy to `web/data/current.json`
→ existing `web/app.js` fetch
→ `window.GiveawayUI.render(...)`.

The browser continues to read only `data/current.json`; it does not fetch `data/production/giveaways/**` directly.

## Changes

Implemented in `main`:

- fail-closed giveaway-to-visual handoff with derived `active`, `empty`, and `unavailable` states;
- strict source contract/schema/KZ/completeness/freshness checks before exposing offers;
- build-time removal of expired offers and validation of first-party HTTPS claim URLs;
- deterministic ordering by promotion deadline, title, then offer identity;
- preservation of multiple verified storefront offers and no fuzzy title merge;
- separate always-visible `Бесплатные раздачи` block at the top of `#feedView`, before the paid queue;
- standalone giveaway renderer and styles in `web/giveaway-ui.js` / `web/giveaway-ui.css`;
- client-time suppression of expired offers; if an `active` payload ages out or all offers expire in-browser, the UI fails closed to unavailable/updating copy rather than claiming a trusted empty result;
- giveaway cards do not participate in paid ranking, swipe, final, or wishlist state;
- canonical visual build and Pages deploy validation wired without creating a second scheduler/writer.

Key implementation commits:

- `b8972893d04d314bf22b04019d5c210262cd0b22` — fail-closed visual handoff
- `fd761b24c3ae161b0a3f77a73ddda1b0a053fcbc` — handoff regressions
- `c62b0fc6ec6c5805e293f089733c641373a4159b` — read-only UI renderer
- `f8fc56665332f2d783b79c8a6633a22fe5268f1e` — giveaway UI styles
- `961fd11b7c82dbd115fa9227a1cdb67f10b7d9d0` — UI regressions
- `ae2239f10adba88991ab8c1a638ae30070ab6b45` — derived giveaway field in final visual payload
- `3f43f85b27b5f197a13bcfb8243c8611ba995798` — separate feed block
- `fee5d4a6d5a029c2f665798a723aa7b24ddff31e` — render from canonical payload
- `b8e37b32a6df8a344dc06e53a23e51a3f45537c7` — generated payload validator
- `faac997f654fc1f63fcd5550e7b7b0b7b78d765c` — canonical build validation wiring
- `3810e931f7451c24f3282f89a35dcf8552613a41` — Pages UI validation wiring
- `6ee9f7385bd74c857ad020d63b1e9cd064762f94` / `77db00d707549b544b68514601d6929a717557d5` / `4169f633aed69d910ed37b4826cffde80ae58ef2` — bounded canonical giveaway-only visual refresh path and auxiliary-only proof
- `7b9c6aec46e36474b7ccf924ca1cd9d7d5c314c4` — scope Pages acceptance to the verified auxiliary visual diff

## Validation

### Behavioral tests

Canonical visual refresh job ran:

`python scripts/test_giveaway_visual_handoff.py`

Result: `Ran 11 tests ... OK`.

Covered behavior includes:

- fresh + complete + active → `active` with visible offer data;
- fresh + complete + zero accepted → trusted `empty`;
- incomplete → `unavailable`;
- stale → `unavailable`;
- wrong contract/country → `unavailable`;
- expired offer removed at build time;
- multiple storefront offers preserved;
- similar titles with distinct canonical keys are not merged;
- deterministic deadline/title/identity ordering;
- malformed accepted surface fails closed;
- source snapshot is not mutated.

Pages deploy validation ran `node web/giveaway-ui.test.js` and returned `GIVEAWAY_UI_TESTS=PASS`. Its scenarios verify:

- active cards and storefront CTA rendering;
- trusted empty copy with no CTA;
- unavailable copy with no CTA;
- all offers expiring client-side → updating/unavailable state, not trusted empty;
- stale visual payload → unavailable with no CTA;
- multiple storefront CTAs are preserved;
- similar titles remain separate cards;
- `web/app.js` keeps the single `const DATA_URL='data/current.json'` route and contains no direct giveaway-production fetch;
- giveaway view-model evaluation does not mutate paid items/queue/final state.

The same deploy job also passed existing `image swipe`, compact purchase-options, and detailed-score mobile regressions.

### Canonical visual build

Workflow: `Build daily visual payload`

- run: `33554699101`
- run number: `166`
- head: `4169f633aed69d910ed37b4826cffde80ae58ef2`
- conclusion: `success`
- canonical bounded refresh job: `giveaway_refresh`
- job ID: `100012600882`
- result: `VISUAL_GIVEAWAY_REFRESH=BUILT changed=true state=active offers=2`
- generated visual validation: `GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=2 fresh_until=2026-09-03T01:30:40.405647Z`
- paid items hash before/after: identical (`d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`)
- auxiliary diff proof: `GIVEAWAY_AUXILIARY_DIFF=PASS non_giveaway_state_unchanged=true`
- generated commit: `43b7d8f47bfda036741e3d6e03fd276f9c4bf5b4` (`Refresh giveaway visual payload`)

The general `build` job in this run was intentionally skipped because the verified `giveaway_refresh` sibling path handled the bounded auxiliary mutation; the workflow as a whole completed successfully.

Execution ownership validation for the same change also succeeded:

- workflow run: `33554699102`
- job: `100012542701`
- result: `ARCHITECTURE_OWNERSHIP_VALID`

### Pages deploy

There was one resolved deploy failure on the generated visual commit:

- failed run: `33554755725`
- failed job: `100012722851`
- generated visual head: `43b7d8f47bfda036741e3d6e03fd276f9c4bf5b4`
- deployment ID: `6209575743`

The failure was addressed by bounded commit `7b9c6aec46e36474b7ccf924ca1cd9d7d5c314c4`, which scopes Pages acceptance to a proven giveaway-only auxiliary visual diff instead of broadening the task.

Successful production Pages deploy:

- workflow: `Deploy visual mailing`
- run: `33554881002`
- run number: `230`
- head: `7b9c6aec46e36474b7ccf924ca1cd9d7d5c314c4`
- deploy job: `100013140799`
- conclusion: `success`
- deployment ID: `6209597474`
- Pages artifact ID: `9818897267`
- deployed Pages build version: `7b9c6aec46e36474b7ccf924ca1cd9d7d5c314c4`
- detected visual payload commit: `43b7d8f47bfda036741e3d6e03fd276f9c4bf5b4`
- scope proof: `VISUAL_DEPLOY_SCOPE=giveaway_only ... non_giveaway_state_unchanged=true`
- generated payload validation: `GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=2 fresh_until=2026-09-03T01:30:40.405647Z`
- UI validation: `GIVEAWAY_UI_TESTS=PASS`
- Pages deployment result: `Reported success!`
- production URL: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`

There is no current deploy blocker.

## Current production state

Canonical giveaway source currently stored on `main`:

- file: `data/production/giveaways/v1/current.json`
- blob: `a6f45abbd40d756d0421eb3492eb3e5ef8e8f510`
- contract: `CROSS-PLATFORM-GIVEAWAY-V1`
- country: `KZ`
- snapshot: `complete`
- generated: `2026-09-01T20:47:04.954912Z`
- fresh until: `2026-09-03T02:47:04.954912Z`
- Steam: `ok`, complete, accepted `0`
- Epic: `ok`, complete, accepted `2`
- GOG: `ok`, complete, accepted `0`
- accepted total: `2`

Current accepted offers are:

1. `Breathedge` — Epic Games — 100% off / KZT 0 — ends `2026-09-03T15:00:00Z` — `https://store.epicgames.com/en-US/p/breathedge`
2. `Rival Stars Horse Racing : Desktop Edition` — Epic Games — 100% off / KZT 0 — ends `2026-09-03T15:00:00Z` — `https://store.epicgames.com/en-US/p/rival-stars-horse-racing-dd09de`

Current visual production file:

- file: `data/production/visual/current.json`
- blob: `e86805bcf45c6e9c579e108f8635dc8eb6f8c8b3`
- latest commit touching it: `43b7d8f47bfda036741e3d6e03fd276f9c4bf5b4`
- stored giveaway state: `active`
- stored offers: `2`
- visual freshness deadline: `2026-09-03T01:30:40.405647Z`

The newer source snapshot was produced after the bounded visual refresh, so the deployed visual uses the previous verified snapshot. It is still within its own declared freshness window on 2026-09-02. This is intentionally fail-closed: once that visual freshness deadline passes, the browser must stop presenting its rows as current even if the underlying source has since become newer.

## User verification

Real-device acceptance is still required. On the phone, open:

`https://kentrap2011-hub.github.io/steam-kz-deals-2/`

Please verify exactly these points:

1. A separate `Бесплатные раздачи` block is visible at the top of the feed before the paid-game queue.
2. While the deployed visual is still fresh, it shows `Breathedge` and `Rival Stars Horse Racing : Desktop Edition`; each `Забрать в Epic Games` CTA opens the corresponding Epic first-party page.
3. Giveaway cards have no paid swipe/ranking/final/wishlist behavior, and the normal paid feed below them still works as before.
4. The UI is not misleading around freshness/expiry: after `2026-09-03T01:30:40.405647Z` (03:30:40 Europe/Berlin), this deployed snapshot must no longer be shown as current; it should switch to unavailable/updating copy rather than continue to show stale giveaway CTAs. The promotions themselves are recorded to end at `2026-09-03T15:00:00Z` (17:00 Europe/Berlin).

Until this real-device check is confirmed, the task must not be called complete.

## Efficiency / reusable lesson

For an auxiliary production surface, prove that non-owned state is byte/structure-stable before allowing a bounded refresh/deploy path. This permits the smallest canonical production validation without re-running unrelated paid-feed production work or weakening fail-closed checks.

## Status

needs_user_verification

## Recommended next step

Open the deployed Pages URL on the phone, verify the four items in `User verification`, and report pass/fail; only after that confirmation should this task be closed as complete.
