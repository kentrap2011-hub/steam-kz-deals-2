# cross-platform-giveaway-ui-ux-fix-01

## User acceptance defect

Phone acceptance of `cross-platform-giveaway-ui-01` found two concrete UX problems:

1. The giveaway block was permanently expanded and consumed too much of the first mobile viewport, pushing the paid feed down.
2. Expanded giveaway rows only exposed title/store/deadline/CTA, without enough game context.

This task fixes the first defect fully and handles the second without inventing unsafe Epic/GOG -> Steam identity.

## Compact UI change

Implemented on `main` in squash commit:

- `5c47e0fe0b6eab0e24399891983f4667c36e1faf` — `giveaways: compact mobile block and honest analysis state`

Files changed by the product implementation are limited to:

- `web/giveaway-ui.js`
- `web/giveaway-ui.css`
- `web/giveaway-ui.test.js`
- `web/index.html`

Behavior now:

- giveaway surface is collapsed by default;
- active compact header renders as `🎁 Бесплатные раздачи (N)`;
- empty/updating/unavailable states remain truthful in the compact header;
- the same button expands and collapses repeatedly using `aria-expanded` + `hidden`;
- mobile collapsed height is approximately one compact control instead of a stack of giveaway cards;
- giveaway block remains before the paid queue, but the paid queue is immediately reachable below the compact control;
- exact store/deadline/claim CTA behavior remains inside the expanded content;
- no giveaway interaction mutates paid swipe/ranking/final/wishlist state;
- browser data route remains the existing single `data/current.json` fetch.

A bounded follow-up commit was used only to retrigger the existing giveaway-only validation route after the first multi-file push was misclassified by the workflow scope probe:

- `9ff985daf3fb3f4421f89ab1d8b1a4558aaf7123` — `giveaways: trigger bounded UX validation`

It adds only a CSS comment and does not alter product behavior.

## Analysis enrichment route

A narrow identity preflight was performed against the current canonical route only. No safe existing Epic/GOG -> Steam analysis binding was found.

Important distinction:

- giveaway `canonical_game_key` / `identity_confidence` is sufficient for grouping giveaway offers;
- it is not an explicit binding to the Steam/Taste game identity used by the paid analysis surface.

Therefore this task deliberately does **not**:

- map by normalized title only;
- fuzzy-match title/publisher;
- copy Steam `summary`, `why_fit`, or `risks` because names look similar;
- fabricate description/pros/cons.

Expanded giveaway cards now expose an explicit honest incomplete-analysis state with the visible sections:

- `Описание`
- `Плюсы`
- `Минусы`

Each section explains that confirmed analysis is unavailable until a safe cross-store identity exists. The card also states that Steam analysis is not transferred by title.

The UI regression suite includes an adversarial row containing fake `steam_analysis` fields (`UNSAFE_TITLE_ONLY_ANALYSIS`, `UNSAFE_PLUS`, `UNSAFE_MINUS`) and proves none of them are rendered.

Minimal remaining producer/identity gap: an explicit, provenance-bearing cross-store identity from the giveaway canonical game identity to a storefront-neutral analysis identity. A future bounded task can recon/define that contract, e.g. `cross-platform-giveaway-analysis-identity-recon-01`; it is intentionally not invented here.

Canonical data route remains unchanged:

`data/production/giveaways/v1/current.json`
-> existing giveaway visual handoff / final visual producer
-> `data/production/visual/current.json`
-> existing Pages deploy copy
-> `web/data/current.json`
-> existing browser payload renderer.

No second browser fetch, writer, scheduler, or manually curated mapping was added.

## Current giveaway sample

Current canonical giveaway source on `main`:

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
- total accepted offers: `2`

Current cards:

1. `Breathedge`
   - Epic Games
   - KZT `0`, `100%` discount
   - deadline `2026-09-03T15:00:00Z`
   - CTA `https://store.epicgames.com/en-US/p/breathedge`
   - expanded analysis state: explicitly incomplete; no title-only Steam analysis
2. `Rival Stars Horse Racing : Desktop Edition`
   - Epic Games
   - KZT `0`, `100%` discount
   - deadline `2026-09-03T15:00:00Z`
   - CTA `https://store.epicgames.com/en-US/p/rival-stars-horse-racing-dd09de`
   - expanded analysis state: explicitly incomplete; no title-only Steam analysis

So the deployed compact active header is expected to show `🎁 Бесплатные раздачи (2)` while the snapshot remains valid/fresh.

## Production validation

### Behavioral regressions

`web/giveaway-ui.test.js` now verifies:

- collapsed default state;
- compact active count;
- expand -> collapse -> expand repeatability;
- exact CTA/deadline rendering remains available after expansion;
- truthful empty/unavailable/updating states;
- stale payload suppresses CTA fail-closed;
- client-expired offers suppress CTA and use updating state rather than false trusted empty;
- multiple storefront offers remain preserved;
- similar titles with different canonical keys remain separate;
- explicit `Описание` / `Плюсы` / `Минусы` incomplete-analysis presentation;
- injected title-only Steam analysis is ignored;
- browser still uses only `data/current.json`;
- giveaway view/toggle does not mutate paid state.

Final Pages validation also re-ran the existing image-swipe, compact purchase-options, and detailed-score regressions successfully.

### First canonical build attempt: not accepted

The implementation push initially triggered `Build daily visual payload` run:

- run `33589818919`
- run number `169`
- head `5c47e0fe0b6eab0e24399891983f4667c36e1faf`

Its scope classifier incorrectly produced `giveaway_only=false`, so the unrelated general paid visual build ran and failed at its existing Russian-description gate. The giveaway-only refresh job was skipped. This run was **not** treated as production acceptance.

Root cause of the scope false negative: the scope probe uses `set -o pipefail` with a `git diff ... | grep -q giveaway` pipeline. On the larger multi-file diff, `grep -q` can terminate after the first match, causing upstream `git diff` to receive SIGPIPE; with `pipefail`, the successful semantic match can therefore evaluate as a failed pipeline.

The task was not called complete at this point.

### Successful bounded canonical visual build

A minimal giveaway-CSS-only retrigger caused the existing workflow to select the intended bounded path.

Workflow: `Build daily visual payload`

- run `33589909638`
- run number `170`
- head `9ff985daf3fb3f4421f89ab1d8b1a4558aaf7123`
- scope job `100121624865`: success, `VISUAL_SCOPE=giveaway_only`
- general paid `build` job: skipped
- giveaway refresh job `100121662458`: success
- handoff regressions: `Ran 11 tests ... OK`
- builder: `VISUAL_GIVEAWAY_REFRESH=BUILT changed=true state=active offers=2`
- generated payload: `GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=2 fresh_until=2026-09-03T02:47:04.954912Z`
- paid items SHA before: `d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`
- paid items SHA after: `d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`
- auxiliary proof: `GIVEAWAY_AUXILIARY_DIFF=PASS non_giveaway_state_unchanged=true`

Canonical generated visual commit:

- `4e79f0efe951e86be4d05f791a585bbd44c917a3` — `Refresh giveaway visual payload`
- `data/production/visual/current.json` blob: `4d71034840ca7bbf2133a0f7632b5c6180c52cf2`

### Successful Pages deploy

Final deploy from the canonical refreshed visual:

- workflow: `Deploy visual mailing`
- run `33589942712`
- run number `235`
- head `4e79f0efe951e86be4d05f791a585bbd44c917a3`
- deploy job `100121719331`: success
- GitHub Pages deployment ID: `6217639122`
- Pages artifact ID: `9830521646`
- artifact zip SHA256: `6c12714b7cc6b2042cdd737227c7e56da27fd8a803715515bb2dfe1afaa7aad0`
- deploy scope: `VISUAL_DEPLOY_SCOPE=giveaway_only ... non_giveaway_state_unchanged=true`
- paid visual acceptance: `reused_existing_canonical_payload structural_diff_proof=pass`
- giveaway payload validation: `PASS state=active offers=2 fresh_until=2026-09-03T02:47:04.954912Z`
- UI regression result: `GIVEAWAY_UI_TESTS=PASS`
- image swipe regression: `PASS`
- compact purchase options mobile regression: `PASS`
- detailed score mobile regression: `PASS`
- Pages result: `Reported success!`

Production URL:

`https://kentrap2011-hub.github.io/steam-kz-deals-2/`

There is no current deploy blocker.

## User verification

Real-phone acceptance is required again. Verify exactly:

1. On initial load the giveaway area is a compact collapsed control, expected while current state is active: `🎁 Бесплатные раздачи (2)`; the paid game card is immediately reachable below it.
2. Tap once: the giveaway cards expand. Tap the same control again: they collapse. Repeat once more to verify the toggle remains stable.
3. In each expanded game card, verify store/deadline/CTA plus the visible `Описание`, `Плюсы`, `Минусы` area. For the current two Epic games it must honestly say analysis is incomplete; it must **not** show copied Steam analysis based only on the title.
4. Verify the paid feed below is visually and behaviorally unchanged: normal swipe/navigation, `Интересно`, `Финал`, wishlist-related state and paid ranking behavior still work as before.

Do not close the task as complete until this phone check is confirmed.

## Efficiency / reusable lesson

With `set -o pipefail`, avoid `producer | grep -q` in workflow scope classifiers: an early successful `grep -q` can SIGPIPE the producer and invert a positive match on larger diffs.

## Status

needs_user_verification

## Recommended next step

Open the deployed Pages URL on the phone and confirm the four checks in `User verification`. If they pass, close this UX-fix task; only then consider a separate bounded identity/analysis recon if richer real description/pros/cons are still desired.
