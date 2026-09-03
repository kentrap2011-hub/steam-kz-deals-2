# Worker Report — Mobile Feed Instant Cache Fix 01

Task ID: `mobile-feed-instant-cache-fix-01`

Status: `needs_user_action`

## Exact storage mechanism and why

Implemented one browser-local last-known-good entry using the **Cache Storage API**:

- cache name: `steam-deals-feed-lkg-v1`;
- key: resolved absolute URL for the existing canonical `data/current.json` request;
- stored value: one successful cloneable `Response` only;
- no historical payload list, polling queue, IndexedDB, service worker, second data source, or server-side cache.

Reason for choosing Cache Storage instead of `localStorage`:

- current canonical `data/production/visual/current.json` size at implementation time: **4,123,452 bytes** (~3.93 MiB);
- serializing that full payload into `localStorage` would be too close to common practical per-origin/mobile limits and would also incur string-storage overhead;
- Cache Storage is designed to store full response bodies and is the smallest appropriate browser-local mechanism for this payload size.

The canonical source of truth remains `data/current.json`. Cache Storage is presentation-only last-known-good fallback.

## Last-known-good validation / read / write contract

A payload is considered usable by the cache layer only when:

1. network response is HTTP-successful;
2. JSON parsing succeeds;
3. parsed value is an object;
4. `payload.items` is an array, matching the shape required by existing `web/app.js`;
5. the payload is handed through the existing app bootstrap/render path;
6. the final UI state is renderable as existing `card` or existing `empty` state.

Only after step 6 is the network `Response` clone written as the new last-known-good entry.

The cache never persists:

- HTTP error responses;
- malformed JSON;
- invalid-shape payloads;
- aborted/timeout requests;
- a payload whose app/render path ends in an error/non-renderable state.

Cache reads are also parsed and shape-validated before being supplied to the app. A corrupt/invalid cached entry is deleted and ignored; bootstrap then falls open to the existing bounded network path.

Cache open/read/write failures are non-fatal and also fail open to normal network loading.

## Instant-render and background-refresh flow

### True cold start / no valid local entry

Behavior remains the resilient path from the previous incident fix:

1. cache lookup is attempted;
2. if absent/unavailable/invalid, existing feed area shows `Загружаю игры…`;
3. canonical `data/current.json` is fetched with `cache: 'no-store'` semantics inherited from existing `app.js`;
4. each network attempt is bounded by `AbortController` with a `9000 ms` timeout;
5. maximum two attempts total: initial attempt + one retry;
6. success goes through existing `app.js` queue/filter/render behavior;
7. terminal failure produces the existing explicit error behavior rather than a silent blank state.

### Repeat visit / valid local entry

Behavior is now stale-while-revalidate style:

1. read and validate the single last-known-good cached response;
2. return that payload immediately to the same existing `app.js` fetch/init path;
3. render normal cards/empty semantics without waiting for canonical network latency;
4. do **not** show blocking `Загружаю игры…` when a valid local response was found;
5. start exactly one bounded background refresh against canonical `data/current.json`;
6. compare the refreshed valid payload with the currently displayed cached payload;
7. use `generated_at_utc` as the stable identity when present; serialized equality is only a fallback when that timestamp is unavailable;
8. if identical, do nothing visible and do not re-run the app renderer;
9. if different, feed the fresh response back through the existing global `init()` / existing app processing path using one injected response, so `web/app.js` remains the single authoritative renderer/queue builder;
10. only if that fresh payload renders successfully is it committed as the new last-known-good cache entry.

No second renderer or duplicated filtering/ranking logic was added.

The existing `web/app.js` file itself was not changed.

## State/navigation preservation

The background replacement uses the existing `init()` function rather than a duplicate renderer.

That means current app globals/state remain authoritative. In particular:

- no page reload is performed;
- no new tab/filter model exists in the cache layer;
- existing queue rebuilding keeps using existing state preservation rules;
- lifecycle/cache code does not reset the visible cached feed while refresh is pending.

## Failure and stale behavior

When a valid cached feed is already visible and background refresh fails, times out, returns HTTP failure, malformed JSON, or invalid shape:

- cached cards remain visible;
- no terminal blocking error replaces the visible feed;
- the previous last-known-good cache entry remains unchanged;
- console diagnostics record the refresh failure and classification;
- there is still only one bounded retry, not a polling/retry loop.

No new arbitrary "materially old" threshold was invented. Existing payload timestamps/status remain authoritative; the task explicitly prohibited inventing a new freshness policy. Existing `app.js` freshness text therefore remains unchanged rather than adding an intrusive warning based on a new age rule.

## Lifecycle safety

The previous mobile resilience rules remain intact:

- no parallel duplicate feed bootstrap loops;
- bounded network timeout;
- one retry maximum per network bootstrap/refresh operation;
- hidden -> visible and BFCache lifecycle handling never blank a visible cached/ready feed;
- lifecycle events do not start additional background refresh loops once the cache-first refresh already exists;
- a valid cache-delivered feed is treated as the visible ready source while refresh occurs independently.

## Diagnostics

Existing `[feed-bootstrap]` diagnostics were extended with cache/background-refresh events, including:

- cache availability/open failure;
- cache hit/miss;
- corrupt cache parse/shape failure;
- cache read/write success/failure;
- bootstrap/network phase (`bootstrap` vs `refresh`);
- attempt number;
- resolved canonical URL;
- timeout/network/HTTP/parse/shape outcome;
- parsed item count;
- payload identity;
- final render state;
- background refresh `identical`, `updated`, or `failed` outcome;
- lifecycle recovery skips while a cached/ready feed is already visible.

No analytics or external telemetry service was added.

## Focused regression results

Focused Node regression for the updated cache/bootstrap controller was executed successfully:

```text
feed instant cache regression: PASS
```

Covered paths include:

1. first visit / no cache + fast network -> normal render + LKG cache write;
2. repeat visit + valid cache + slow/pending network -> cached card renders before network settles;
3. valid cache + identical canonical payload -> no disruptive re-render/reset;
4. valid cache + different newer payload -> fresh payload re-enters existing app path, renders in place, and updates LKG cache;
5. valid cache + network failure -> cached feed remains visible and refresh is bounded to two attempts;
6. invalid/corrupt cache -> deleted/ignored -> normal bounded network bootstrap;
7. malformed/invalid network response -> never replaces existing valid cache;
8. cache open/write failure -> normal network path remains functional;
9. lifecycle events during background refresh -> no duplicate refresh loop;
10. cached visible feed remains visible across hidden -> visible / BFCache lifecycle events;
11. cold-start timeout still terminates explicitly after bounded attempts;
12. cache write is refused unless the payload reaches a renderable app state;
13. non-feed fetches and canonical payload pass-through remain unchanged.

Normal Pages workflow UI regressions also passed on the production release commit.

## Exact implementation / release refs

Canonical branch: `main`

Implementation commits:

- `d61f276e17395c0cc91a57d72388738934b75ed3` — add Cache Storage last-known-good + cache-first/background-refresh behavior to `web/feed-bootstrap.js`.
- `c1b13f28d9878bbb0d0b48726003c390139f5f07` — update focused regression coverage in `tests/feed-bootstrap.test.js`.
- `f745dac844213880cd7eb984573877f58803a3f0` — production release ref; bump `feed-bootstrap.js` asset version in `web/index.html` so clients load the new cache-first implementation.

Final relevant blobs at release ref:

- `web/feed-bootstrap.js`: `67fbc7866ac5a7244f0fd8a467e2e0a3925235c7`
- `tests/feed-bootstrap.test.js`: `f4ec8a8d4165cbacdef67a27587494e07972c307`
- `web/index.html`: `56e92cd99c9a63eaa4f5cd470464652a4751ac8f`

Canonical payload size evidence used for the storage decision:

- `data/production/visual/current.json`: `4,123,452 bytes` at implementation-time inspection.

## Production deploy

Production deployment was performed through the canonical Pages workflow:

- workflow: `Deploy visual mailing`
- workflow run: `33779042331`
- run number: `256`
- head SHA: `f745dac844213880cd7eb984573877f58803a3f0`
- conclusion: `success`

The workflow completed its existing UI regressions, staging, Pages artifact upload, and GitHub Pages deployment successfully.

No separate visual-freshness branch was merged as part of this task.

## Real-device verification still required

Per task requirement, do not declare the incident complete until the affected phone verifies the deployed behavior.

Required user acceptance:

1. open the page once and allow one successful full load so a last-known-good response is stored;
2. reload at least 5 times, including several rapid reloads;
3. after the first successful cached visit, cards should normally appear essentially immediately instead of waiting several seconds on `Загружаю игры…`;
4. if the network is slow, already visible cached cards must remain visible while background refresh runs;
5. switch to another app and return; the feed must remain visible with no reset/blanking;
6. when canonical `generated_at_utc` changes, verify the refreshed payload eventually replaces the cached payload in place.

Until this real-device acceptance is completed, status remains `needs_user_action`.