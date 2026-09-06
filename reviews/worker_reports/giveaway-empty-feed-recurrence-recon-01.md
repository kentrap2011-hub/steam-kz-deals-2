# Worker Report — Giveaway Empty Feed Recurrence Recon 01

status: `recon_complete_recovery_required`
mode: `READ-ONLY / RECON`
task: `WORKER_TASK_GIVEAWAY_EMPTY_FEED_RECURRENCE_RECON_01.md`
repository: `kentrap2011-hub/steam-kz-deals-2`
recon_baseline_main_head: `fbe99c508e23fa6f3f4e7ab2a1ffe0a11947d67c`

## Executive result

The recurring empty/fail-closed giveaway presentation is **not** caused by an empty upstream giveaway set and is **not** a recurrence of the previous browser cache/identity incident.

The current canonical giveaway snapshot is healthy, complete, fresh, and contains one valid active Epic giveaway. The stale state exists downstream: the canonical daily visual artifact has not advanced to that refreshed giveaway snapshot. The latest inspected `Build daily visual payload` run failed in the existing `Build and refresh canonical visual payload once` step and produced a degraded freshness receipt rather than a fresh visual. Consequently `data/production/visual/current.json` remains bound to an older giveaway snapshot whose embedded freshness window has expired. The fail-closed behavior is therefore suppressing stale giveaway evidence instead of presenting it as fresh.

No production repair was performed in this recon.

## Exact current cause

The exact proven failure boundary is:

`fresh canonical giveaway snapshot -> existing giveaway visual handoff -> existing daily visual build/publication -> data/production/visual/current.json`

The canonical source advanced, but the downstream visual publication did not.

Current canonical giveaway snapshot:

- path: `data/production/giveaways/v1/current.json`
- Git blob SHA: `04a94e2fe64b6503738138900598282464e65fd3`
- `generated_at_utc`: `2026-09-05T20:45:50.245306Z`
- `fresh_until_utc`: `2026-09-07T02:45:50.245306Z`
- completeness/snapshot status: complete
- accepted offer count: `1`

Current canonical visual artifact:

- path: `data/production/visual/current.json`
- Git blob SHA: `45636d95a97d4e763115d076fea8c451ccb74231`
- `production_contract.source_giveaway_snapshot_blob_sha`: `33c1318a4950450aadb41b98a9552223b5cf43b8`
- embedded giveaway `generated_at_utc`: `2026-09-03T18:53:28.148553Z`
- embedded giveaway `fresh_until_utc`: `2026-09-05T00:53:28.148553Z`
- embedded giveaway handoff blob: `ec49195af509934f058a1b3de880ae9152ee0f64`

Therefore the current visual artifact is demonstrably not derived from the current canonical giveaway blob `04a94e...`; it is still coupled to older blob `33c131...`.

This mismatch exists durably in repository artifacts before any browser cache is involved.

## Why the site shows old / fail-closed giveaway data

The UI is intentionally fed by the precomputed visual artifact and does not perform independent external giveaway lookup. The currently published visual artifact still contains the older giveaway handoff. That handoff's freshness expired on `2026-09-05T00:53:28.148553Z`.

The current canonical giveaway snapshot was refreshed later, but no fresh visual publication consumed it. As a result, the site can only see the old visual-side giveaway evidence. Because the giveaway handoff is fail-closed, expired/untrusted giveaway evidence must not be represented as fresh; the correct presentation is unavailable/empty rather than pretending that the old snapshot is current.

## Valid upstream / canonical giveaway rows exist

Yes.

The current canonical snapshot contains one accepted active giveaway:

- title: `Alone With You`
- storefront: `epic`
- claim URL: `https://store.epicgames.com/en-US/p/alone-with-you-028a15`
- promotion start: `2026-09-03T15:00:00Z`
- promotion end: `2026-09-10T15:00:00Z`

Source evidence in the canonical snapshot shows a normal successful Epic response and a complete canonical snapshot. GamerPower also returned normally but contributed no qualifying row under policy; that is not an outage and is not the reason the feed is empty/fail-closed.

Thus `no giveaway exists upstream` is false for the current incident.

## Actions evidence

The existing workflow is `.github/workflows/build-daily-visual-payload.yml` (`Build daily visual payload`). It already reads the canonical giveaway snapshot, validates/derives the giveaway visual handoff, and builds the one canonical visual payload. No second giveaway visual writer is required.

Inspected run:

- workflow: `Build daily visual payload`
- run id: `34037436064`
- run number: `197`
- head SHA: `c007f7561954a53ef9c5000b794d216c4fc8790e`
- event: `push`
- started: `2026-09-06T13:52:53Z`
- conclusion: `failure`

Job evidence:

- `scope`: success
- `build`: failure
- giveaway handoff validation step: success
- history readiness gate: success
- failing step: `Build and refresh canonical visual payload once`
- later generated-payload validation and canonical commit steps: skipped

The run still uploaded its durable visual freshness receipt. That receipt records:

- `fresh_build`: `false`
- `outcome`: `degraded/no_fresh_build`
- `produced_visual`: `null`
- `reason`: `build_reported_no_fresh_change`
- workflow run id: `34037436064`

This is sufficient to prove why the newer canonical giveaway snapshot did not become the current visual artifact: the existing visual build failed/degraded and did not publish a replacement.

The connector does not expose the failing step's raw stderr/log payload, so this recon does **not** invent a deeper exception string. The exact proven root-cause boundary is the failed existing visual build/publication step, not the giveaway source or canonical giveaway writer.

## Fail-closed verification

Fail-closed remains intact.

`scripts/giveaway_visual_handoff.py` requires a trusted snapshot contract/schema/country, complete required source health, and a non-expired `fresh_until_utc`. If those checks fail, it returns state `unavailable` with zero accepted offers rather than treating stale evidence as current.

The failed visual run also did not overwrite the canonical visual artifact with an unproven fresh result; its receipt is explicitly degraded with `fresh_build=false` and `produced_visual=null`.

Therefore fail-closed is behaving as intended. It is not the defect to remove or weaken.

## What is broken

Broken:

- the existing downstream daily visual build/publication did not successfully advance `data/production/visual/current.json` to the refreshed canonical giveaway snapshot;
- the current visual artifact therefore carries an expired giveaway handoff and an old source giveaway blob SHA.

The broken boundary is downstream of the canonical giveaway source/writer and upstream of the UI.

## What is NOT the cause

The current incident is **not** caused by:

- absence of valid giveaways upstream;
- an empty canonical giveaway snapshot;
- Epic source failure;
- GamerPower transport failure;
- canonical giveaway writer failing to refresh `data/production/giveaways/v1/current.json`;
- the previous cache/identity/production-shape incident;
- fail-closed policy itself;
- a second giveaway scheduler/writer created by this recon.

The old cache/identity incident is a different failure domain. In this incident the stale identity is already durable inside `data/production/visual/current.json`: it references old giveaway source blob `33c131...` while current canonical source is `04a94e...`. Browser cache behavior is not needed to explain that repository-level mismatch.

## Recon non-implementation / ownership invariants

This task remained recon-only.

- production was not repaired;
- `data/production/giveaways/v1/current.json` was not manually changed;
- `data/production/visual/current.json` was not manually changed;
- cache was not patched manually;
- fail-closed was not weakened;
- no workflow was edited;
- no scheduler was created;
- no second giveaway writer was created;
- no production Actions run was triggered or rerun by this recon;
- the only repository mutation made by this task is this durable report.

Workflow inventory/current ownership continues to use the existing canonical visual pipeline; no separate giveaway scheduler/writer was introduced in this recon.

## One exact next bounded action

Open **one separate bounded recovery/IMPLEMENT task** scoped only to the existing `Build daily visual payload` failure at run `34037436064`, starting with the failed `Build and refresh canonical visual payload once` step and making only the minimum repair/recovery needed for that existing path to complete.

Acceptance criterion for that single bounded action:

1. the existing visual workflow completes successfully without a second scheduler/writer or manual cache patch;
2. newly published `data/production/visual/current.json.production_contract.source_giveaway_snapshot_blob_sha` exactly equals the then-current Git blob SHA of `data/production/giveaways/v1/current.json`;
3. the giveaway handoff is freshly derived under the existing fail-closed contract;
4. a fresh visual freshness receipt reports a produced/persisted fresh visual.

Do not solve this by creating another giveaway scheduler/writer, manually editing cache/visual data, or weakening freshness checks.

## Should the user recheck the site now?

**No.**

This recon deliberately changed no production state. At recon close, `data/production/visual/current.json` is still bound to the old giveaway source SHA, so a user recheck would only test the already-known unresolved stale/fail-closed publication state.

The user should recheck only after the bounded recovery action has successfully published a visual artifact whose `source_giveaway_snapshot_blob_sha` matches the current canonical giveaway blob and whose giveaway handoff is fresh.

## Final status

`RECON COMPLETE — ROOT CAUSE BOUNDARY IDENTIFIED — RECOVERY REQUIRED`

Current incident: fresh valid canonical giveaway data exists, but the existing downstream visual build/publication failed and left the site-facing visual artifact on an older expired giveaway snapshot.

No production fix was applied in this recon.