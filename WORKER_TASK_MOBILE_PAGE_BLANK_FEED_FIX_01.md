# WORKER TASK — MOBILE PAGE BLANK FEED FIX 01

Task ID: `mobile-page-blank-feed-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/mobile-page-blank-feed-fix-01.md`

## Source decision

Direct continuation of:
- `WORKER_TASK_MOBILE_PAGE_INTERACTION_FREEZE_RECON_01.md`
- `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md`

The corrected incident is:
- page shell and controls are interactive;
- after fresh load/reload, the game feed region is blank;
- switching away and returning can make the feed appear;
- canonical payload is non-empty;
- current bootstrap performs one unbounded `fetch('data/current.json', { cache: 'no-store' })` before first feed render;
- both content and empty/error result surfaces begin hidden;
- there is no bounded timeout/retry or lifecycle-aware recovery for the main feed.

The recon did **not** prove the exact Android/WebView transport-level reason, but it identified a concrete unsafe application state that permits the observed blank feed indefinitely. Implement the resilience fix and diagnostics; do not broaden into unrelated frontend redesign.

## Goal

Make it impossible for the main feed to remain silently blank indefinitely after a normal load/reload, while preserving current filtering/card behavior.

The fix must:
1. expose an immediate visible loading state;
2. bound the initial data request with timeout/cancellation;
3. allow one bounded retry/recovery path;
4. recover safely when the page returns to foreground if bootstrap is unresolved/retryable;
5. prevent duplicate concurrent bootstrap loops;
6. surface explicit empty/error states instead of silent blankness;
7. add enough diagnostics to distinguish timeout/network/HTTP/parse/render outcomes during acceptance.

## Primary implementation surface

Keep the change minimal. Expected primary surface:
- `web/app.js`
- `web/index.html` only if a loading-state element/text is needed
- one focused test/helper file if required

Do not touch more than 3 production files unless the report proves it is strictly necessary.

## Required implementation behavior

### A. Explicit bootstrap state

Introduce one small state model equivalent to:
- `idle`
- `loading`
- `ready`
- `failed`

Requirements:
- bootstrap must be idempotent;
- while one fetch is active, lifecycle events must not start parallel duplicate requests;
- once `ready`, routine focus/visibility changes must not reset or refetch unnecessarily;
- failed/timeout/unresolved states may trigger at most the bounded recovery defined below.

### B. Visible loading state

On fresh load/reload, the feed region must not start as an unexplained empty hole.

Before the data request starts, show a clear lightweight loading state in the existing feed area, for example `Загружаю игры…`.

Do not redesign the page.

### C. Bounded request

Wrap the primary `data/current.json` request with `AbortController` or an equivalent supported mechanism.

Use a short mobile-appropriate timeout, approximately 8–10 seconds unless current code/tests justify a nearby value.

A request that times out must settle into a known retryable/error state; it must not leave the feed blank.

### D. One bounded retry

Allow at most one automatic retry for the bootstrap attempt.

No unbounded timer loop, polling loop or background retry queue.

The retry must respect the same timeout and idempotency guard.

### E. Foreground/lifecycle recovery

Add guarded recovery for the main feed on the smallest relevant lifecycle hooks, preferably:
- `pageshow`
- `visibilitychange` when document becomes visible

`online` may be included if it materially helps and remains bounded.

Lifecycle recovery must:
- do nothing when state is already `ready`;
- never create parallel fetches;
- retry only when bootstrap has not succeeded and remains retryable;
- not cause repeated re-render/reload on every normal app switch once feed is healthy.

### F. Explicit terminal UI states

Preserve current semantics:
- valid payload + visible items -> render card/feed normally;
- valid payload + legitimate zero-result queue -> show existing empty state;
- HTTP/network/timeout/parse failure after bounded retry -> show explicit error state;
- never leave both the main feed/card and empty/loading/error surfaces hidden after bootstrap starts.

### G. Diagnostics

Add bounded diagnostics sufficient for acceptance to distinguish:
- bootstrap start and attempt number;
- resolved data URL;
- fetch resolved / rejected / timed out;
- HTTP status;
- JSON parsed;
- `items.length`;
- built `queue.length`;
- final render state: `card | empty | error`;
- lifecycle-triggered recovery.

Use concise `console` diagnostics or the smallest existing diagnostic mechanism. Do not add analytics/telemetry service or external logging dependency.

## Required focused tests

Add/extend focused regression tests that prove at minimum:
1. successful fetch -> `ready` -> card/feed render;
2. valid zero-result payload -> explicit empty state;
3. network/parse/HTTP failure -> explicit error after bounded attempts;
4. pending request timeout -> no indefinite blank state;
5. lifecycle foreground event during active request does not create duplicate parallel bootstrap;
6. lifecycle foreground event after retryable failed/unresolved state can trigger the one guarded recovery;
7. once `ready`, visibility/pageshow does not unnecessarily reload/reset the feed;
8. existing filtering/navigation/card behavior remains unchanged in the tested path.

Do not require a real network call in unit/focused tests if a mocked fetch is sufficient.

## Production / release

This is a current user-visible production incident. If implementation and focused tests pass:
- prepare the change for the canonical production path;
- do not mix in the separate accepted `worker/visual-freshness-chain-fix-01` branch unless Director explicitly authorizes that after this incident is stabilized;
- report exactly what branch/commit is ready and whether a normal Pages deploy is required.

Do not claim the incident fixed until the user verifies the deployed page on the affected phone.

## Required real-device acceptance after deployment

User must verify on the actual affected device:
1. open page fresh;
2. confirm loading state appears briefly instead of blank hole if data is not ready instantly;
3. confirm game cards appear;
4. refresh/reload page several times;
5. confirm feed does not remain blank;
6. switch to another app and return;
7. confirm healthy feed remains healthy and no duplicate/restart glitch appears.

## Boundaries

Do NOT:
- change Taste/ranking/data-selection semantics;
- change current canonical payload format merely for this fix;
- redesign cards/navigation;
- add service worker or new cache layer;
- create polling/background queues;
- merge the separate visual-freshness branch as part of this implementation;
- add external telemetry services;
- broaden into stale/degraded production-data freshness investigation.

## Required result

Report:
1. exact implementation;
2. exact bootstrap state/timeout/retry/lifecycle behavior;
3. exact user-visible loading/error behavior;
4. diagnostics added;
5. focused regression results;
6. branch/commit/ref ready for release;
7. whether production deploy was performed;
8. exact real-device verification still required.

Status exactly one:
- `complete`
- `needs_followup_fix`
- `blocked`
- `needs_user_action`

## Completion

Save:
`reviews/worker_reports/mobile-page-blank-feed-fix-01.md`

Final answer must state exact report path, status and exact refs.