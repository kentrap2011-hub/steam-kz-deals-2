# GIVEAWAY PUBLICATION GAP RECON 01

STATUS: needs_fix

## TASK

- Task ID: `giveaway-publication-gap-recon-01`
- Mode: `READ-ONLY / RECON`
- Goal: locate the first exact boundary where the healthy canonical giveaway `Alone With You` stops propagating to the published site.
- Scope discipline: no parser, workflow, frontend, writer, ITAD/IGDB, Taste, ranking, or production-data implementation changes were made. The prior Epic parser incident was not reopened because no new parser-failure evidence was found.

## VERIFIED FACTS

### 1. Canonical giveaway is healthy on current `main`

Current canonical source:
- path: `data/production/giveaways/v1/current.json`
- blob: `33c1318a4950450aadb41b98a9552223b5cf43b8`
- latest bounded canonical update commit: `cffe98c7d3bc93396e52d2738825c612fdf9bc57` — `Update Steam KZ production and giveaways`

The snapshot is complete and contains exactly one accepted giveaway:
- title: `Alone With You`
- source: Epic Games Store
- country/region: KZ
- active current promotion: `2026-09-03T15:00:00Z` through `2026-09-10T15:00:00Z`
- discount: `100%`
- Epic source health: `status=ok`, `complete=true`, `accepted_count=1`, `unverified_count=0`, `error_code=null`
- overall `accepted_offer_count=1`, `game_group_count=1`

There is therefore no current evidence that the Epic parser is the publication defect. The completed `epic-giveaway-schema-fix-01` remains closed.

### 2. Actual publication chain

The repository-owned path from giveaway source to the browser is:

```text
data/production/giveaways/v1/current.json
  -> scripts/giveaway_visual_handoff.py
  -> data/production/visual/current.json
  -> .github/workflows/deploy-visual.yml
       cp data/production/visual/current.json web/data/current.json
       upload Pages artifact from web/
  -> browser web/app.js DATA_URL = data/current.json
  -> giveaway view/filter/render
```

Relevant exact refs:
- giveaway handoff: `scripts/giveaway_visual_handoff.py` @ `ec49195af509934f058a1b3de880ae9152ee0f64`
- deploy workflow: `.github/workflows/deploy-visual.yml` @ `7479a56ac7ee363e6a212952e58f36558b371877`
- browser loader: `web/app.js` @ `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5`

Pages does **not** publish `data/production/giveaways/v1/current.json` directly. It publishes `web/data/current.json`, which the deploy workflow stages as a direct copy of `data/production/visual/current.json`.

### 3. First exact loss boundary

The first proven loss is:

```text
healthy canonical giveaway snapshot
    -> stale giveaway sibling in data/production/visual/current.json
```

Current visual payload:
- path: `data/production/visual/current.json`
- blob: `a2af7944c808877eaee7c18cad72fb2a069e85ec`
- latest bounded commit touching this file: `fbc82821db0bc43029765629a0d3047219c7a0fb` — `Refresh giveaway visual payload`
- commit time: `2026-09-03T16:30:49Z`

Its giveaway sibling currently says:

```text
giveaways.state = unavailable
giveaways.generated_at_utc = 2026-09-02T20:36:23.116897Z
giveaways.derived_at_utc = 2026-09-03T16:30:48.215658Z
giveaways.accepted_offer_count_at_build = 0
giveaways.games = []
```

Its production provenance records:

```text
production_contract.source_giveaway_snapshot_blob_sha = 7354f8769b21bb9dda53910871374a5011af5586
```

That provenance SHA is the old canonical giveaway snapshot used at visual-build time. At commit `fbc82821db0bc43029765629a0d3047219c7a0fb`, canonical blob `7354f8769b21bb9dda53910871374a5011af5586` was still the pre-fix incomplete state:
- `snapshot_status=incomplete`
- Epic `status=error`
- Epic `complete=false`
- Epic `accepted_count=0`
- `error_code=SOURCE_SCHEMA_FAILURE`
- `error_message=Epic schema changed: element.price.totalPrice must be object`
- no accepted giveaway games.

The repaired canonical snapshot arrived later, in commit `cffe98c7d3bc93396e52d2738825c612fdf9bc57` at `2026-09-03T18:53:30Z`, with current blob `33c1318a4950450aadb41b98a9552223b5cf43b8` and `Alone With You` accepted.

Current `data/production/visual/current.json` still points to the old blob `7354f876...` and still contains no `Alone With You`.

Therefore the exact first publication gap is **between canonical giveaway current and the derived visual payload**. The canonical repair succeeded, but the published visual derivative was not regenerated against that repaired canonical blob.

### 4. Classification

Primary classification: **stale derived publication payload / post-canonical visual-refresh gap**.

This evidence does **not** support these as the first defect:
- Epic parser — current canonical source is healthy and complete;
- wrong browser data path — `web/app.js` deliberately loads `data/current.json`, exactly the file staged by deploy;
- giveaway view/filter/render — the record is already absent before the browser receives the payload;
- browser cache — a hard refresh can only reload the same staged payload if that payload still has `games=[]`.

A publication race is relevant historical context, but the durable current fact is simpler and stronger: the committed publication source itself is stale relative to the canonical giveaway provenance.

### 5. Refresh-routing evidence

Current workflow:
- path: `.github/workflows/build-daily-visual-payload.yml`
- blob: `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`

Its `push.paths` explicitly includes:
- `data/production/giveaways/v1/current.json`

So a canonical giveaway update can trigger the visual workflow.

However, the existing bounded `giveaway_refresh` route depends on `scope.outputs.giveaway_only == 'true'`. The `giveaway_only` classifier allow-list contains giveaway handoff/frontend/workflow files, but **does not contain** `data/production/giveaways/v1/current.json`.

Consequently, a commit whose relevant change is the canonical giveaway snapshot does not qualify for the existing bounded giveaway-only refresh path. This routing asymmetry is a concrete likely mechanism for how a healthy canonical update can remain absent from the visual derivative. This recon does not claim a specific historical full-build run failure beyond the evidence needed to locate the first boundary.

### 6. Published/site payload implication

The deploy workflow stages:

```text
cp data/production/visual/current.json web/data/current.json
```

and uploads `web/` as the Pages artifact. The browser then loads `data/current.json`.

Because the repository artifact used for staging already has `giveaways.games=[]`, `Alone With You` is absent before frontend filtering/rendering can act on it. The task's verified observation that the real site currently shows no giveaway is consistent with this upstream omission.

A hard refresh is therefore only diagnostic. It cannot permanently fix a giveaway that is absent from the deployed source payload.

## CHANGES

- Production code: none.
- Workflows: none.
- Frontend: none.
- Epic parser: none.
- ITAD/IGDB/Taste/ranking/writers: none.
- Production snapshots/payloads: none.
- Added only this recon report: `reviews/worker_reports/giveaway-publication-gap-recon-01.md`.

## VALIDATION

Exact evidence refs used for the boundary:

- task: `WORKER_TASK.md` on current `main`
- canonical current path: `data/production/giveaways/v1/current.json`
- healthy canonical blob: `33c1318a4950450aadb41b98a9552223b5cf43b8`
- healthy canonical update commit: `cffe98c7d3bc93396e52d2738825c612fdf9bc57`
- stale/pre-fix canonical blob used by visual: `7354f8769b21bb9dda53910871374a5011af5586`
- visual current path: `data/production/visual/current.json`
- visual current blob: `a2af7944c808877eaee7c18cad72fb2a069e85ec`
- latest bounded visual refresh commit: `fbc82821db0bc43029765629a0d3047219c7a0fb`
- giveaway visual handoff blob: `ec49195af509934f058a1b3de880ae9152ee0f64`
- deploy workflow blob: `7479a56ac7ee363e6a212952e58f36558b371877`
- browser loader blob: `web/app.js` @ `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5`
- visual-build workflow blob: `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`

Temporal/provenance proof:

```text
2026-09-03T16:30:48Z visual giveaway derivative built
source giveaway blob = 7354f876... (incomplete / Epic SOURCE_SCHEMA_FAILURE / 0 accepted)

2026-09-03T18:53:30Z canonical giveaway updated
current giveaway blob = 33c1318a... (complete / Epic ok / Alone With You accepted)

current visual still references 7354f876... and games=[]
```

This is sufficient to locate the first deterministic loss boundary without reopening source parsing or speculating about UI behavior.

## UNRESOLVED

- A direct byte-for-byte download of the currently served GitHub Pages `data/current.json` was not available through the worker's accessible endpoint set. This does not block the boundary finding because the repository file that the deploy workflow stages is already missing `Alone With You`, and the task provides the live-site observation that no giveaway is shown.
- The exact historical reason no later full visual publication replaced the stale derivative after commit `cffe98c7...` was not proven and is not required to identify the first loss boundary. The bounded workflow classifier mismatch above is concrete routing evidence and the appropriate target for the follow-up implementation review.

No unresolved Epic parser question remains from this recon.

## STATUS DECISION

`needs_fix`

The recon completed successfully and found a precise defect boundary. `Alone With You` exists in the healthy canonical source but is lost at the canonical-to-visual publication handoff because the current visual payload is still derived from the older incomplete canonical blob. Closing the gap requires a bounded publication-refresh implementation; no user decision is required.

## RECOMMENDED NEXT STEP

One bounded IMPLEMENT task: **make a committed change to `data/production/giveaways/v1/current.json` reliably drive the existing giveaway-only visual handoff so `data/production/visual/current.json` is regenerated from that exact canonical blob, and verify before publication that `production_contract.source_giveaway_snapshot_blob_sha` equals the current canonical giveaway blob and staged `web/data/current.json` contains `Alone With You`.**

Do not change the Epic parser or redesign the giveaway UI as part of that implementation unless new independent evidence requires it.

## EFFICIENCY / REUSABLE LESSON

For publication gaps, compare provenance blob SHAs across `canonical -> derived -> deployed` artifacts before debugging frontend filtering; it can identify the first stale boundary without broad workflow-history investigation.
