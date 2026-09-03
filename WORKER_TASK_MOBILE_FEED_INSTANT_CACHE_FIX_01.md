# WORKER TASK — MOBILE FEED INSTANT CACHE FIX 01

Task ID: `mobile-feed-instant-cache-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/mobile-feed-instant-cache-fix-01.md`

## Source decision

Direct continuation of:
- `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`
- `reviews/worker_reports/mobile-page-blank-feed-fix-01.md`

Real-device result after the deployed blank-feed fix:
- the feed no longer stays silently empty;
- the page now visibly shows `Загружаю игры…` while waiting;
- sometimes refresh is effectively instant;
- sometimes the loading state remains visible for several seconds, after which the games still appear;
- user wants this delay removed/reduced, not merely surfaced.

The first fix is therefore a partial success: resilience is improved, but normal repeat visits/reloads are still network-blocking.

## Goal

Make repeat page loads/reloads feel effectively instant by rendering the **last known good feed payload locally first**, while refreshing the current canonical payload in the background.

Target behavior after at least one successful feed load on that device:

`open/reload -> render last known good feed immediately -> background refresh current.json -> update in place only if a newer/different valid payload arrives`

Network latency must no longer block the first useful card render on repeat visits.

A true first visit with no local last-good payload may still use the existing visible loading + bounded network bootstrap path.

## Architectural rule

Implement one bounded **stale-while-revalidate style client fallback** for the existing main feed only.

Do NOT add a service worker, polling loop, second data source, background scheduler or server-side cache.

The canonical source of truth remains `data/current.json`. Local storage/cache is only a last-known-good presentation fallback and must never become a second canonical production data plane.

## Preferred storage mechanism

Choose the smallest safe browser-local mechanism after checking current payload size/support:
- prefer Cache Storage API or another browser storage mechanism suitable for the full response if localStorage size would be unsafe;
- localStorage is allowed only if the current payload size is clearly bounded and safely below practical device/browser limits;
- store only one current last-known-good feed payload plus minimal metadata;
- fail open to normal network bootstrap if local cache read/write is unavailable or throws.

Do not introduce IndexedDB unless simpler browser storage is demonstrably insufficient.

## Required behavior

### A. Cache only validated successful payloads

A payload may become last-known-good only after:
- HTTP success;
- JSON parse success;
- expected payload shape is usable by existing app code;
- feed reaches a valid renderable state.

Never persist:
- HTTP error body;
- malformed JSON;
- terminal error state;
- partial/aborted response.

### B. Instant repeat bootstrap

On page start:
1. attempt to read last-known-good payload locally;
2. if present and valid, hand it to the existing feed/app path immediately;
3. render normal cards/empty semantics without waiting for network;
4. start one background network refresh against canonical `data/current.json`;
5. existing timeout/retry/idempotency protections still apply to that refresh.

Do not show the large blocking `Загружаю игры…` state when a valid local payload is already available and renderable.

A small existing/non-blocking update indicator may be used if already available, but do not redesign the page.

### C. Background refresh

The background refresh must:
- request canonical fresh data using existing freshness-safe semantics;
- validate the response;
- compare a stable identity when available (`generated_at_utc`, payload hash/serialized equality, or another existing exact version field);
- if identical, do nothing visible;
- if newer/different and valid, update the local last-good entry and refresh the active feed in place without a page reload;
- preserve the user's current tab/filter/navigation state as much as current architecture safely allows;
- never blank the already rendered feed while refresh is pending or fails.

If background refresh fails/times out:
- keep showing the last-known-good feed;
- do not replace it with an error screen;
- diagnostics should report the refresh failure;
- if the user has no local payload (true cold start), preserve the existing explicit error behavior after bounded attempts.

### D. Freshness transparency

Do not falsely label cached data as newly fetched.

If the existing UI has a compact refresh/update indicator, it may indicate background refresh in progress/failure. Do not add intrusive warnings for a normal short-lived background refresh.

If a cached payload is materially old according to an existing trustworthy timestamp and the network refresh fails, expose the smallest clear stale/degraded hint available without redesigning the UI. Do not invent a new freshness policy; reuse existing timestamps/status when available.

### E. Interaction/lifecycle safety

Preserve the previous fix:
- no parallel duplicate feed fetches;
- bounded timeout;
- maximum bounded retry behavior;
- hidden -> visible / BFCache recovery only when appropriate;
- once a valid feed is on screen, lifecycle events must not blank/reset it.

Background/foreground should never turn a visible cached/ready feed back into blocking loading state.

## Important compatibility requirement

The existing `web/app.js` filtering, ranking, card semantics and navigation remain authoritative.

Do not fork or duplicate queue-building/rendering logic in the cache layer.

The cache/bootstrap layer should supply a valid payload through the existing app path or the smallest shared interface, not implement a second renderer.

## Focused tests

Prove at minimum:
1. first visit/no cache + fast network -> normal load and cache write;
2. repeat visit + valid cache + slow/pending network -> cached feed renders before network settles;
3. repeat visit + cache + identical network payload -> no disruptive rerender/reset;
4. repeat visit + cache + newer/different valid network payload -> local cache updates and visible feed refreshes safely;
5. repeat visit + cache + network timeout/failure -> cached feed remains visible, no terminal blocking error;
6. invalid/corrupt local cache -> ignored, normal bounded network bootstrap used;
7. failed/malformed network response never replaces valid cache;
8. cache read/write failure does not break normal network loading;
9. lifecycle events do not create duplicate background refresh loops;
10. once visible feed is ready from cache, app switch/return does not blank it;
11. existing feed filtering/navigation/card behavior remains unchanged.

## Production and user acceptance

If implementation/tests pass, deploy through the canonical Pages path.

Do not mix in the separate accepted visual-freshness branch as part of this task.

Do not declare complete until real-device verification.

Required user verification after deploy:
1. open page once and let it fully load;
2. reload 5+ times, including several rapid reloads;
3. after the first successful cached visit, cards should normally appear essentially immediately rather than waiting on `Загружаю игры…`;
4. if network is slow, already visible cards must stay visible while refresh happens in background;
5. switch to another app and return; feed must remain visible;
6. verify fresh data still eventually replaces old data when a new payload is available.

## Boundaries

Do NOT:
- change Taste/ranking/filtering semantics;
- change canonical payload ownership;
- add service worker;
- add polling/background scheduler;
- add a second renderer or second production data source;
- store unbounded historical payloads;
- make cache permanent authority;
- merge `worker/visual-freshness-chain-fix-01` as part of this task;
- broaden into server/build freshness investigation.

## Required result

Report:
1. exact storage mechanism and why chosen;
2. exact last-known-good validation/write/read contract;
3. exact instant-render + background-refresh flow;
4. how stale/failure behavior works;
5. focused regression results;
6. production release/deploy refs if performed;
7. exact real-device verification still required.

Status exactly one:
- `complete`
- `needs_user_action`
- `needs_followup_fix`
- `blocked`

## Completion

Save:
`reviews/worker_reports/mobile-feed-instant-cache-fix-01.md`

Final answer must state exact report path, status and exact refs.