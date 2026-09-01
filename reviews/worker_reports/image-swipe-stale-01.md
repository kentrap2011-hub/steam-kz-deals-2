# Image swipe stale-image regression report

## Task
Fix the stale image shown after rapid mobile card swipes while preserving the existing swipe directions, current-game navigation, package/scoring semantics, and the `CURRENT_TASK.md` task ledger.

## Verified facts
- `web/app.js` switches the current game and card text synchronously, while the original `setShot()` directly replaced the `<img>` source and gallery background. A browser can continue painting the previous decoded bitmap while the replacement image is still loading, so title/price can already belong to the new game while the old image is still visible.
- Swipe navigation is separate from image loading. The existing direction contract remains unchanged: swipe left goes to the next game and swipe right goes to the previous game.
- The package work advanced independently while this worker ran. This worker did not edit `CURRENT_TASK.md`, package/scoring code, or package semantics.
- No focused executable JavaScript UI race regression existed for this path, so a small standalone Node regression was added.

## Changes
- Added `web/image-swipe-sync.js`.
  - Clears the old foreground image and blurred gallery background immediately when a new shot is requested, so a previous game's bitmap cannot remain visible during the new load.
  - Loads the requested image offscreen.
  - Uses a monotonically increasing request generation plus current game, shot index, and URL checks before committing the loaded image.
  - A late/stale image load is ignored and cannot overwrite the current card.
  - Image load failure leaves the current visual blank rather than restoring stale content.
- Added `web/image-swipe-sync.test.js`.
  - Simulates rapid `A -> B -> C` navigation with intentionally out-of-order image completion.
  - Verifies that only `C` can commit.
  - Verifies a rapid reverse navigation path rejects the older pending image and commits only the newest game.
  - Verifies the old visible bitmap/background are cleared while the current image is loading.
- Updated `web/index.html` to load the new UI guard immediately after `app.js` with a cache-busting query token.
- Implementation commits:
  - `9a0b39097946ae166c3d7d9b687e368818e69a99` — add stale image commit guard.
  - `4a7d5b7cc7f4c0f580e0cbd706d8f0c5db779e72` — add image swipe race regression.
  - `ec15768c3ecd050084f8d5ed49e5cd1ef025b679` — load the guard with cache busting.
  - `1504ce75a247d4cd75dcdbcc314361ef7c4e5265` — initial worker report.
- PR `#9` merged to `main` as `d10cfe40aed926f488e02e93d19c6c43037d8e93`.

## Validation
- `node --check web/image-swipe-sync.js` — PASS.
- `node --check web/image-swipe-sync.test.js` — PASS.
- `node web/image-swipe-sync.test.js` — PASS (`image swipe regression: PASS`).
- Rapid `A -> B -> C`, then resolve images in `B, A, C` order — PASS: `B` and `A` are rejected; only `C` commits.
- Old visual during a card switch — PASS: old `<img src>` is removed, the image is hidden, and the blurred background is cleared until the current request commits.
- Rapid reverse path `C -> B` before `C` resolves — PASS: stale `C` completion is rejected; `B` commits.
- Existing swipe direction handlers were not changed.
- Package/scoring files and `CURRENT_TASK.md` were not changed by this worker.
- GitHub PR check `validate` completed successfully for head `1504ce75a247d4cd75dcdbcc314361ef7c4e5265`.
- GitHub Pages deploy run `33487513565` for merge commit `d10cfe40aed926f488e02e93d19c6c43037d8e93` completed successfully.

## Unresolved
- This worker environment does not provide a physical mobile browser/device run. The race behavior is covered by an executable DOM/Image simulation using the production guard code, but one real-phone stress swipe remains a useful acceptance check.

## Status
PASS — fix is merged to `main`, regression validation passed, and the Pages deployment completed successfully. The task ledger was not closed or rewritten by this worker.

## Recommended next step
Perform one real-phone stress pass with rapid left/right swipes (ideally on a slower connection) to confirm the production browser never displays a previous game's image under the current game's title/price.
