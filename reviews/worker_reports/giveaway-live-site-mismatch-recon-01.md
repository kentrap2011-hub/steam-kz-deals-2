# GIVEAWAY LIVE SITE MISMATCH RECON 01

STATUS: needs_followup_fix

## TASK

- Task ID: `giveaway-live-site-mismatch-recon-01`
- Mode: `READ-ONLY / RECON`
- User evidence: after the successful Pages deploy, the giveaway was still not visible on the real site on a mobile device.
- Scope: locate the first downstream divergence in `deployed Pages artifact -> live HTTP -> browser-loaded data -> render` without reopening Epic/canonical investigation absent new evidence.

## EXACT PUBLIC ROUTES

- Live site: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`
- Frontend data path in `web/app.js`: `data/current.json`
- Therefore the exact public data URL loaded by the frontend is:
  `https://kentrap2011-hub.github.io/steam-kz-deals-2/data/current.json`

`web/feed-bootstrap.js` intercepts requests whose pathname ends in `/data/current.json`, so this is also the exact URL governed by the browser-side resilience/cache layer.

## 1. DEPLOYED PAGES ARTIFACT

Previously proven successful deploy:
- deploy run: `33832350887`
- Pages artifact ID: `9922110216`
- artifact digest: `sha256:c76443526a53e8e50f625d7a19f1dc1ed87875fd3ca3acc83441598824ac581e`
- Pages build version: `ee0a609cfa15612e19249089206fefa9d6dda714`

The exact deployed artifact was re-inspected during this recon. Its `data/current.json` contains:

```text
giveaways.state = active
giveaways.accepted_offer_count_at_build = 1
giveaways.games[0].title = Alone With You
production_contract.source_giveaway_snapshot_blob_sha = 33c1318a4950450aadb41b98a9552223b5cf43b8
```

Therefore the deployed artifact itself is not the missing-giveaway boundary.

## 2. LIVE HTTP

Direct observation of the public HTTP response body/headers from this worker environment was attempted for both:

```text
https://kentrap2011-hub.github.io/steam-kz-deals-2/
https://kentrap2011-hub.github.io/steam-kz-deals-2/data/current.json
```

The available public-web path did not return an inspectable Pages body, and the worker container cannot resolve/reach the Pages host directly. GitHub repository/Actions APIs can prove the deployed artifact but do not expose the public GitHub Pages HTTP body.

Result:
- live HTTP body equals deployed artifact: **not directly verifiable from this worker environment**;
- an earlier `deployed artifact -> live HTTP` mismatch therefore cannot be formally excluded;
- no evidence was found that would justify claiming such an HTTP mismatch actually exists.

This limitation is kept explicit rather than substituting artifact content for a live HTTP observation.

## 3. BROWSER-LOADED DATA / CACHE RECONCILIATION

A concrete downstream defect is proven in the current browser bootstrap code and is sufficient to reproduce the user's symptom even when live HTTP serves the new payload correctly.

### Persistent last-known-good cache

`web/feed-bootstrap.js` uses Cache Storage under:

```text
steam-deals-feed-lkg-v1
```

On startup it calls `readLastGood(url)`. If a cached payload exists, that cached response is returned immediately to the application and the network fetch runs only as a background refresh.

Therefore a mobile browser that previously opened the site can legitimately begin from an old visual payload that predates `Alone With You`.

### Payload identity collision

Current identity logic is:

```js
function payloadIdentity(payload){
  if(typeof payload?.generated_at_utc==='string'&&payload.generated_at_utc)return `generated:${payload.generated_at_utc}`;
  try{return `json:${JSON.stringify(payload)}`}catch{return null}
}
```

So any payload that has `generated_at_utc` is identified **only** by that top-level timestamp.

The bounded giveaway-only publication path deliberately changes only the giveaway sibling and its provenance while leaving the accepted paid visual state intact. It does not require a new top-level `generated_at_utc` merely because the giveaway sibling changed.

This creates the exact collision relevant here:

```text
old cached payload without current giveaway
  generated_at_utc = X

fresh network payload with Alone With You
  generated_at_utc = X
  source_giveaway_snapshot_blob_sha = new canonical giveaway blob
```

The bootstrap considers both identities equal because giveaway provenance is not part of the identity.

### Fresh network payload is then discarded as "identical"

`startBackgroundRefresh()` does:

```js
if(fresh.identity&&cached.identity&&fresh.identity===cached.identity){
  state.refreshOutcome='identical';
  log('refresh-identical',{identity:fresh.identity});
  return;
}
```

The return occurs before `applyBackgroundPayload(fresh)`.

Therefore, after the cached old payload has already been delivered to the app, a successful fresh network response containing `Alone With You` can be received, parsed, and still **never be passed into the application/render path**.

This is not ordinary HTTP browser caching: the resilience layer itself owns the Cache Storage LKG and the stale/fresh reconciliation decision.

## 4. RENDER

The fresh deployed payload itself is compatible with the current render path.

The current frontend:
- loads `data/current.json`;
- hands the selected payload to the application;
- the giveaway UI consumes the `giveaways` sibling;
- the deployed payload has `state=active`, one accepted offer, and `Alone With You`.

The exact fresh artifact was exercised through the current giveaway view-model/render logic during this recon and produced an active giveaway view with count `1` and markup containing `Alone With You`.

Therefore no new evidence points to a giveaway UI filtering/rendering defect once the fresh payload actually reaches render.

## FIRST PROVEN MISMATCH BOUNDARY

**First proven downstream defect boundary:**

```text
browser cached LKG -> background network refresh reconciliation
```

More precisely:

```text
web/feed-bootstrap.js::payloadIdentity()
    +
web/feed-bootstrap.js::startBackgroundRefresh()
```

The browser can start with a stale cached visual payload, then fetch a fresh payload containing `Alone With You`, but classify it as `refresh-identical` solely because both payloads have the same `generated_at_utc`. The fresh payload is then not applied to the app.

This directly explains the reported mobile symptom without requiring any failure in Epic parsing, canonical giveaway generation, the deployed Pages artifact, or giveaway rendering.

Because the worker cannot directly inspect the public Pages HTTP body, an even earlier artifact-to-live-HTTP mismatch remains technically unexcluded. The cache reconciliation defect above is nevertheless independently proven and actionable.

## HARD REFRESH DIAGNOSTIC

A hard refresh / clearing site data could remove or bypass the stale LKG and would be useful only as a diagnostic discriminator:
- if the giveaway appears after removing the browser's stored LKG, that strongly confirms this boundary in the user's browser;
- this is **not** an acceptable product fix, because normal users must receive giveaway-only updates without manually clearing cache.

## ONE MINIMAL NEXT FIX

Change only the browser payload identity in `web/feed-bootstrap.js` so a giveaway-only publication cannot collide with an older cached visual payload.

Minimal identity:

```text
generated_at_utc + ":" + production_contract.source_giveaway_snapshot_blob_sha
```

Equivalent implementation intent:
- preserve the existing `generated_at_utc` identity;
- append the canonical giveaway snapshot provenance when present;
- do not alter cache ownership, fetch routing, freshness/completeness semantics, giveaway rules, or render behavior.

Required focused regression for that fix:
1. cached payload and fresh network payload have the same `generated_at_utc`;
2. cached payload has old giveaway provenance / no `Alone With You`;
3. fresh payload has a new `source_giveaway_snapshot_blob_sha` and `Alone With You`;
4. refresh must **not** become `refresh-identical`;
5. fresh payload must reach `applyBackgroundPayload` / application render.

## OUT OF SCOPE / UNCHANGED

No implementation was made in this recon.

Not changed or re-investigated:
- Epic parser;
- canonical giveaway rules/source logic;
- ITAD / IGDB;
- Taste / ranking;
- giveaway UI design;
- workflow/publication architecture;
- freshness/completeness checks.

No broad Git/Actions-history search was performed.

## STATUS DECISION

`needs_followup_fix`

Reason:
- the exact deployed Pages artifact is known to contain `Alone With You`;
- fresh giveaway data is renderable once supplied to the UI;
- a precise browser-side stale-LKG reconciliation defect is proven and can prevent that fresh payload from ever reaching render;
- the recon therefore has one bounded actionable next fix;
- live public HTTP body remains unobservable from the worker environment, so the report does not overclaim that hop as verified.
