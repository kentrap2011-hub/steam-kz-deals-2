# Worker Report — Mobile Page Blank Feed Fix 01

Task ID: `mobile-page-blank-feed-fix-01`

Status: `needs_user_action`

## Exact implementation

Implemented a minimal bootstrap-resilience layer without changing Taste/ranking/filtering/card semantics and without redesigning the interface.

Changed production files:

- `web/feed-bootstrap.js` — new focused bootstrap controller that wraps only the main `data/current.json` request.
- `web/index.html` — loads `feed-bootstrap.js?v=mobile-page-blank-feed-fix-01` immediately before the existing `app.js` bootstrap.

Unchanged production behavior surface:

- `web/app.js` filtering, queue building, navigation, card rendering and ranking logic were not modified.
- No payload format changes.
- No service worker, cache layer, polling loop, background queue or external telemetry was added.

Focused regression test added:

- `tests/feed-bootstrap.test.js`

## Bootstrap state / timeout / retry / lifecycle behavior

The bootstrap controller exposes one bounded state model equivalent to:

- `idle`
- `loading`
- `ready`
- `failed`

Exact request behavior:

- target request: only URLs resolving to `/data/current.json`;
- timeout per attempt: `9000 ms`;
- cancellation: `AbortController`;
- maximum attempts: `2` total (`1` initial + `1` retry);
- automatic retry delay: `200 ms`;
- only one bootstrap promise is created for the feed request, so duplicate concurrent bootstrap loops are prevented;
- once payload/render reaches `ready`, lifecycle events do not refetch or reset the feed.

Foreground recovery:

- `visibilitychange` is used only after an actual `hidden -> visible` transition;
- `pageshow` recovery is used only for `event.persisted === true` (BFCache restore), avoiding a redundant retry on normal initial `pageshow`;
- if attempt 1 is still active after a real background/foreground transition, it is aborted and the single allowed retry is used; the requests do not overlap;
- if attempt 1 has already failed and is in the bounded retryable wait, foreground recovery triggers the same one remaining retry immediately;
- during attempt 2, or after `ready`, lifecycle events cannot create additional attempts.

## User-visible states

The existing feed area is reused; there is no layout/card redesign.

Immediately when the bootstrap layer installs:

- `#gameCard` remains hidden;
- `#emptyFeed` is made visible with `Загружаю игры…`.

During the single retry window:

- `#emptyFeed` shows `Повторяю загрузку игр…`.

Successful payload:

- existing `app.js` renders the normal card/feed;
- controller records final render state `card` and state becomes `ready`.

Legitimate zero-result queue:

- existing empty surface remains visible;
- bootstrap loading text is restored to `Активных игр в этой очереди сейчас нет.`;
- controller records final render state `empty` and state becomes `ready`.

Terminal failure after both bounded attempts:

- card remains hidden;
- `#emptyFeed` is visible with `Не удалось загрузить игры. Обновите страницу.`;
- state becomes terminal `failed` / non-retryable;
- the feed cannot remain silently blank after bootstrap starts.

## Diagnostics added

Concise console diagnostics use prefix:

`[feed-bootstrap]`

Recorded events/details include:

- installation with timeout/retry delay;
- bootstrap start;
- attempt number;
- resolved absolute data URL;
- fetch resolved with HTTP status and `ok`;
- fetch rejected;
- explicit timeout classification;
- HTTP failure classification;
- JSON parse failure classification;
- lifecycle abort/recovery;
- retry source (`automatic`, `visibilitychange`, or `pageshow`);
- parsed `itemsLength`;
- final render state: `card | empty | error`;
- queue length read from rendered feed count when available.

No analytics service or external logging dependency was added.

## Focused regression results

Command-equivalent focused regression run:

```text
node tests/feed-bootstrap.test.js
```

Result:

```text
feed bootstrap regression: PASS
```

The focused test covers:

1. successful fetch -> `ready` -> card render;
2. valid zero-result payload -> explicit empty state;
3. network failure -> two bounded attempts -> explicit error;
4. HTTP failure -> two bounded attempts -> explicit error;
5. JSON parse failure -> two bounded attempts -> explicit error;
6. pending request timeout -> no indefinite blank state;
7. ordinary lifecycle signal during an active request does not create a duplicate fetch;
8. retryable failed state can use foreground as the one guarded recovery;
9. real hidden -> visible during unresolved attempt 1 aborts then retries without parallel requests;
10. once `ready`, visibility/BFCache `pageshow` does not reload/reset the feed;
11. non-feed fetches and payload pass-through remain unchanged.

The normal Pages workflow also reached its `Run UI regressions` step successfully on the release commit.

## Release refs

Canonical branch: `main`

Implementation commits, in order:

- `6490d27a3a546197aa68decae12a89091244d6b3` — add resilient feed bootstrap layer.
- `e7a2da7f50d0f4b6ea8b8e82ecd0898172dce6fb` — load bootstrap layer before `app.js`.
- `b27a17bdeae38c5f59bdca3f607f68008af7a971` — add focused regression test.
- `af2c7362743b4fe3d80ea10caee7cb606acab3e5` — final implementation ref; explicit timeout diagnostic classification.

Final production blobs at release ref:

- `web/feed-bootstrap.js`: `85fe0ab0ea9b98b79662f3290f1b9eb6e47b03b5`
- `web/index.html`: `25249a6a25cc15cf81fcf6fd710d4f2b0219facd`
- `tests/feed-bootstrap.test.js`: `a9b2a33face751879a500218b3955771a05b5409`

## Production deploy

A normal Pages deploy was required because `web/**` changed.

Production deploy was performed automatically from `main` and completed successfully:

- workflow: `Deploy visual mailing`
- workflow run: `33766838776`
- run number: `254`
- head SHA: `af2c7362743b4fe3d80ea10caee7cb606acab3e5`
- conclusion: `success`

The successful run passed the repository UI regression step, staged the existing precomputed payload, uploaded the Pages artifact and completed the Pages deployment.

An earlier deploy attempt for `e7a2da7f50d0f4b6ea8b8e82ecd0898172dce6fb` failed before deployment on an existing payload-description gate. The final release run above succeeded; no workflow or payload semantics were changed to bypass that gate.

## Real-device verification still required

Per task boundary, the incident must not be declared fixed until the user verifies the deployed page on the affected phone.

Required acceptance on the actual device:

1. open the page fresh;
2. confirm `Загружаю игры…` appears briefly instead of a blank feed hole if data is not instant;
3. confirm game cards appear;
4. refresh/reload several times;
5. confirm the feed never remains blank;
6. switch to another app and return;
7. confirm an already healthy feed remains healthy with no duplicate/restart glitch.

Until that real-device acceptance is completed, task status is `needs_user_action`.