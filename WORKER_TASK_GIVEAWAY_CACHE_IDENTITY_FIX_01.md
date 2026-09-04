# WORKER TASK — GIVEAWAY CACHE IDENTITY FIX 01

Task ID: `giveaway-cache-identity-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/giveaway-cache-identity-fix-01.md`

## Proven cause

Source recon:
`reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`

The exact deployed Pages artifact contains `Alone With You`, and the fresh payload renders correctly once it reaches the application.

The proven browser-side defect is in `web/feed-bootstrap.js`:
- stale last-known-good payload can be returned immediately from Cache Storage;
- `payloadIdentity()` currently identifies payloads only by top-level `generated_at_utc` when present;
- giveaway-only refresh can change giveaway provenance/data while preserving the same top-level `generated_at_utc`;
- stale cached payload and fresh network payload then collide as `refresh-identical`;
- the fresh payload is discarded before `applyBackgroundPayload()`.

## Goal

Make the smallest safe change so giveaway-only payload updates cannot collide with an older cached LKG payload.

## Required implementation

Update the existing payload identity in `web/feed-bootstrap.js` so identity includes giveaway provenance when present.

Minimum intended identity semantics:

`generated_at_utc + production_contract.source_giveaway_snapshot_blob_sha`

Preserve existing fallback behavior for payloads that lack those fields.

Do not redesign cache ownership, fetch flow, retry behavior, freshness semantics, or rendering.

## Required regression

Add focused regression coverage proving:
1. cached and fresh payloads have the same `generated_at_utc`;
2. cached payload has old giveaway provenance and no `Alone With You`;
3. fresh payload has new `source_giveaway_snapshot_blob_sha` and contains `Alone With You`;
4. refresh is not classified as `refresh-identical`;
5. fresh payload reaches `applyBackgroundPayload()` / app update path.

Also preserve existing identical-payload behavior when both relevant identity components are actually equal.

## Boundaries

Do NOT:
- change Epic parser;
- change canonical giveaway rules/data;
- change ITAD/IGDB;
- change Taste/ranking;
- redesign giveaway UI;
- change cache storage ownership or create a second cache path;
- weaken freshness/completeness checks;
- change unrelated frontend navigation/filter state.

## Validation and deploy

Run focused frontend tests first, then the canonical deploy path needed for the production site.

Record exact commit and deploy/run refs.

This is user-visible. Technical completion is not final UX acceptance: after deploy, Director must request a real-site mobile verification from the user.

## Done when

Save:
`reviews/worker_reports/giveaway-cache-identity-fix-01.md`

Include:
1. Task
2. Proven cause
3. Changes
4. Regression validation
5. Deploy evidence
6. User verification required
7. Unresolved
8. Status
9. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
