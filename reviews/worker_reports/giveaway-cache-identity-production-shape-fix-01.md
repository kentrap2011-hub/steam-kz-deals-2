# Giveaway cache identity production-shape fix 01

## 1. Task

Task: `WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_PRODUCTION_SHAPE_FIX_01.md`

Mode: bounded IMPLEMENT.

Goal: correct only the stale-LKG cache identity giveaway component so it uses the real production publication provenance and no longer collides when only giveaway publication changes.

Required report path: `reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`.

## 2. Proven defect

The prior acceptance report `reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md` proved that commit `6282619c65c134459a4e85c80b9355fe3174e8ae` was deployed but insufficient.

That implementation read a synthetic schema:

- flat `giveaway_generated_at_utc`;
- flat `giveaway_status`;
- array-shaped `giveaways`.

The deployed production payload instead uses:

- `payload.production_contract.source_giveaway_snapshot_blob_sha` for giveaway publication provenance;
- object-shaped `payload.giveaways`;
- no flat `giveaway_generated_at_utc`;
- no flat `giveaway_status`.

Therefore the previous identity could still collapse stale cached giveaway state and a fresh giveaway-only publication to the same value.

## 3. Changes

### `web/feed-bootstrap.js`

`payloadIdentity()` now keeps the existing ordinary feed generation key and JSON fallback, but replaces the incorrect synthetic giveaway inputs with the actual production provenance:

```js
const generatedAt=typeof payload?.generated_at_utc==='string'?payload.generated_at_utc.trim():'';
const giveawaySnapshotBlobSha=typeof payload?.production_contract?.source_giveaway_snapshot_blob_sha==='string'
  ?payload.production_contract.source_giveaway_snapshot_blob_sha.trim()
  :'';
if(generatedAt||giveawaySnapshotBlobSha){
  return `published:${JSON.stringify([generatedAt,giveawaySnapshotBlobSha])}`;
}
try{return `json:${JSON.stringify(payload)}`}catch{return null}
```

Removed from identity logic:

- `payload.giveaway_generated_at_utc`;
- `payload.giveaway_status`;
- `Array.isArray(payload.giveaways)` / giveaway array count.

No cache architecture, fetch ownership, giveaway rules, parser, ranking, ITAD/IGDB, Taste, summary buttons, or other frontend behavior was changed.

### `scripts/test_feed_bootstrap_cache_identity.js`

The focused regression now uses production-shaped fixtures:

- `giveaways` is an object;
- giveaway provenance lives at `production_contract.source_giveaway_snapshot_blob_sha`;
- no invented flat giveaway timestamp/status fields exist;
- stale and fresh payloads keep identical `generated_at_utc` and identical `items`;
- stale payload uses old giveaway provenance, `state: absent`, zero accepted offers and empty games;
- fresh payload uses new provenance, `state: active`, one accepted offer and active giveaway data.

The regression also counts app init calls and captures the payload delivered through the refresh application path.

### Deploy gate

No workflow edit was needed. Current `.github/workflows/deploy-visual.yml` already runs:

```text
node scripts/test_feed_bootstrap_cache_identity.js
```

inside the canonical `Run UI regressions` Pages deployment gate.

## 4. Production-shaped regression evidence

Focused regression result from the canonical deployment job:

```text
giveaway cache identity production-shape regression: PASS
```

The regression proves both required branches:

1. stale cached production-shaped payload -> fresh giveaway-only payload
   - ordinary feed `generated_at_utc` unchanged;
   - ordinary `items` unchanged;
   - giveaway snapshot provenance changes;
   - `refreshOutcome === 'updated'`;
   - app `init()` is called exactly once;
   - the fresh production-shaped payload is delivered to the refresh application path.

2. truly identical production-shaped payload
   - identity remains equal;
   - `refreshOutcome === 'identical'`;
   - app `init()` is not re-run.

The offline/cache-first fallback assertion also remains green.

## 5. Existing regression evidence

Canonical Pages job `Run UI regressions` completed successfully with:

```text
image swipe regression: PASS
compact purchase options mobile regression: PASS
detailed score mobile regression: PASS
GIVEAWAY_UI_TESTS=PASS
giveaway cache identity production-shape regression: PASS
```

Giveaway payload validation in the same job also passed:

```text
GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=1 fresh_until=2026-09-05T00:53:28.148553Z
```

## 6. Deploy evidence

Final implementation commit:

- `024f81937942987c96bb5db1b0e1d7b66dd67587`
- message: `Use production giveaway provenance in cache identity`
- parent test commit: `1388e26311717bac23e1bce45793504b2826f560`

Scope comparison from pre-task main `f6aa2f2270afd72e3ce1a299ddf4263b4498ab0d` to final implementation commit shows exactly two changed files:

- `scripts/test_feed_bootstrap_cache_identity.js`
- `web/feed-bootstrap.js`

Canonical Pages deployment:

- workflow: `Deploy visual mailing`
- workflow run ID: **`33841356092`**
- run number: `264`
- event: `push`
- head SHA: `024f81937942987c96bb5db1b0e1d7b66dd67587`
- run conclusion: **success**
- deploy job ID: **`100924142727`**
- deploy job conclusion: **success**
- Pages artifact ID: **`9925017623`**
- Pages build version / deployment ID reported by `actions/deploy-pages`: **`024f81937942987c96bb5db1b0e1d7b66dd67587`**
- deployed URL: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`

The Pages deployment step reported success at `2026-09-04T05:40:46Z`.

### Exact production artifact inspection

The exact uploaded Pages artifact `9925017623` was downloaded and inspected after deployment.

Its shipped `feed-bootstrap.js` contains:

```text
const giveawaySnapshotBlobSha=typeof payload?.production_contract?.source_giveaway_snapshot_blob_sha==='string'
  ?payload.production_contract.source_giveaway_snapshot_blob_sha.trim()
  :'';
...
return `published:${JSON.stringify([generatedAt,giveawaySnapshotBlobSha])}`;
```

The artifact contains none of the rejected synthetic identity inputs:

- no `giveaway_generated_at_utc` in `feed-bootstrap.js` identity logic;
- no `giveaway_status` in identity logic;
- no `Array.isArray(payload?.giveaways)` giveaway identity check.

The same exact deployed artifact contains production-shaped active giveaway data:

```text
generated_at_utc=2026-08-31T18:09:11.137550+00:00
giveaways_type=dict
giveaway_state=active
giveaway_games=1
source_giveaway_snapshot_blob_sha=33c1318a4950450aadb41b98a9552223b5cf43b8
flat giveaway_generated_at_utc present=false
flat giveaway_status present=false
```

This directly proves that the deployed runtime code reads the provenance field that actually exists in the deployed production payload.

## 7. User verification required

Technical implementation and deployment are complete.

The user-visible incident remains open until the user checks the normal existing mobile browser session again. No cache/site-data clearing should be required or requested as the product fix.

**It is now appropriate to ask the user to re-check giveaways on the phone.**

## 8. Unresolved

No bounded implementation defect remains from this task based on regression, CI, deploy and exact artifact inspection.

Only user acceptance on the real mobile session remains.

## 9. Status

**complete**

## 10. Exact refs

- task: `WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_PRODUCTION_SHAPE_FIX_01.md`
- prior acceptance: `reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`
- production-shaped regression commit: `1388e26311717bac23e1bce45793504b2826f560`
- final implementation commit: `024f81937942987c96bb5db1b0e1d7b66dd67587`
- workflow: `.github/workflows/deploy-visual.yml`
- workflow run: `33841356092`
- deploy job: `100924142727`
- Pages artifact: `9925017623`
- Pages deployment/build version: `024f81937942987c96bb5db1b0e1d7b66dd67587`
- report: `reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`
