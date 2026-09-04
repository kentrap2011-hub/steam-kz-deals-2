# WORKER TASK — GIVEAWAY CACHE IDENTITY PRODUCTION SHAPE FIX 01

Task ID: `giveaway-cache-identity-production-shape-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`

## Proven defect

Acceptance report:
`reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`

Status there: `needs_followup_fix` / `deployed_but_fix_insufficient`.

The landed commit `6282619c65c134459a4e85c80b9355fe3174e8ae` is conceptually aimed at the correct stale-LKG identity collision but reads the wrong production fields:
- flat `giveaway_generated_at_utc` — absent in production;
- flat `giveaway_status` — absent in production;
- array-shaped `giveaways` — production uses an object.

Actual production giveaway publication provenance is under:
`payload.production_contract.source_giveaway_snapshot_blob_sha`.

Therefore stale cached payload and fresh giveaway-only payload can still collide as identical when ordinary feed generation state is unchanged.

## Goal

Make the smallest safe correction so the existing cache identity uses the **actual production payload shape** and distinguishes giveaway-only publication changes.

## Required implementation

1. Update only the giveaway identity component in `web/feed-bootstrap.js::payloadIdentity()` to use actual production provenance, at minimum:
   `payload.production_contract.source_giveaway_snapshot_blob_sha`.
2. Preserve existing ordinary-feed identity behavior and fallback behavior.
3. Do not depend on invented flat giveaway fields or array-shaped `giveaways`.
4. Update the focused regression `scripts/test_feed_bootstrap_cache_identity.js` to use production-shaped fixtures:
   - `giveaways` is an object;
   - provenance lives in `production_contract.source_giveaway_snapshot_blob_sha`;
   - cached stale variant has old/no giveaway state;
   - fresh variant has new provenance and active giveaway data;
   - ordinary feed generation fields remain unchanged.
5. Regression must prove:
   - stale cache -> fresh giveaway-only payload => `updated` and `applyBackgroundPayload()` / app init occurs;
   - truly identical production-shaped payload => `identical`.
6. Keep/add the focused regression in the canonical deploy UI gate if current `main` does not already run it.

## Critical boundaries

Do NOT:
- reopen Epic parser/canonical giveaway work;
- change giveaway eligibility/price/region rules;
- redesign cache ownership/fetch flow;
- change top-summary navigation/filter work;
- touch ITAD/IGDB, Taste/ranking, semantic runtime;
- weaken freshness/completeness.

Keep scope to the real-schema identity correction + focused regression + necessary deploy gate wiring only.

## Validation

Before status `complete`:
1. run the focused production-shaped regression;
2. run existing relevant UI regressions;
3. verify the exact landed production payload shape is exercised, not a synthetic schema;
4. run/observe the canonical Pages deploy for the final fix commit;
5. record exact commit SHA, workflow run ID, job ID and Pages artifact/deploy evidence;
6. verify the deployed artifact contains the corrected `feed-bootstrap.js` and active giveaway payload.

The worker owns any CI/deploy wait in the same chat.

## User verification

This is user-visible. Even after technical `complete`, the incident remains open until the user checks the real mobile site again.

Do not ask the user to clear cache/site data as the product fix. A normal existing browser session must self-refresh correctly.

## Done when

Save:
`reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`

Include:
1. Task
2. Proven defect
3. Changes
4. Production-shaped regression evidence
5. Existing regression evidence
6. Deploy evidence
7. User verification required
8. Unresolved
9. Status
10. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
