# WORKER TASK

Task ID: `giveaway-publication-gap-fix-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/giveaway-publication-gap-fix-01.md`

## Goal

Исправить уже доказанный publication gap: актуальная canonical giveaway-раздача есть в `data/production/giveaways/v1/current.json`, но `data/production/visual/current.json` остаётся собран из старого giveaway snapshot и поэтому сайт не получает `Alone With You`.

Это bounded fix. Не переоткрывай Epic parser и не перерабатывай giveaway UI.

## Proven recon result

Source report:
`reviews/worker_reports/giveaway-publication-gap-recon-01.md`

Доказано:
- canonical `data/production/giveaways/v1/current.json` — complete, Epic ok/complete, `Alone With You` accepted;
- published chain uses `data/production/visual/current.json` -> `web/data/current.json`;
- current visual payload still references old giveaway source blob `7354f876...` and has `giveaways.games=[]`;
- current canonical giveaway blob is `33c1318a4950450aadb41b98a9552223b5cf43b8`;
- first loss boundary is canonical giveaway -> derived visual payload;
- existing giveaway-only refresh routing does not classify a change to `data/production/giveaways/v1/current.json` as giveaway-only, so a healthy canonical giveaway update can fail to refresh the visual derivative.

## Read first

1. Current `main`.
2. `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`.
3. `reviews/worker_reports/giveaway-publication-gap-recon-01.md`.
4. `data/production/giveaways/v1/current.json`.
5. `data/production/visual/current.json`.
6. Only the exact current workflow/helper files needed for the existing giveaway visual refresh path.

Do not perform broad Git/Actions archaeology.

## Required implementation

Make the smallest safe change so that a committed change to the canonical giveaway snapshot reliably drives the existing bounded giveaway visual refresh path.

Expected behavior after the fix:

1. A change to `data/production/giveaways/v1/current.json` can enter the existing giveaway-only refresh route without requiring unrelated full visual rebuild work.
2. The existing giveaway handoff regenerates the giveaway sibling in `data/production/visual/current.json` from the current canonical giveaway snapshot.
3. Provenance remains strict: `production_contract.source_giveaway_snapshot_blob_sha` must match the canonical giveaway blob used for that derivative.
4. The staged `web/data/current.json` must contain the same giveaway result that is present in the refreshed visual payload.
5. Do not weaken any freshness/completeness contract merely to make the workflow green.

Prefer the existing workflow/handoff architecture. Do not introduce a second publication path, scheduler, writer, cache authority or renderer.

## Critical boundaries

Do NOT:
- change `scripts/giveaway_epic.py` or reopen the Epic schema fix;
- change giveaway eligibility/region/price semantics;
- change ITAD/IGDB identity work;
- change Taste/ranking/paid-deal logic;
- redesign the giveaway frontend/view unless new independent evidence proves it necessary;
- weaken visual freshness or semantic completeness checks;
- touch mobile feed behavior;
- add another workflow or publication authority.

## Validation

Use focused tests / workflow validation appropriate to the exact change.

Then run/use the canonical bounded publication path needed to prove production recovery.

Required proof before calling the implementation complete:
- refreshed `data/production/visual/current.json` no longer uses the stale giveaway source blob;
- its `production_contract.source_giveaway_snapshot_blob_sha` equals the canonical giveaway blob used for the refresh;
- its giveaway sibling contains `Alone With You` while that canonical giveaway remains active;
- staged/published `web/data/current.json` contains `Alone With You`;
- no unrelated producer/output ownership is changed;
- exact commit refs and workflow/deploy run IDs are recorded.

If a CI/deploy run is long-running, own that wait/check inside this worker chat rather than returning it to the Director unfinished.

## User-visible acceptance

This is a user-visible incident. Even after technical production proof, do not claim final user-visible closure on behalf of the user.

Report when the deployed site should contain the giveaway and tell the Director that real-site verification by the user is still required.

## Done when

Save report:
`reviews/worker_reports/giveaway-publication-gap-fix-01.md`

Report sections:
1. Task
2. Proven cause
3. Changes
4. Validation
5. Production/deploy evidence
6. User verification required
7. Unresolved
8. Status
9. Recommended next step
10. Exact refs
11. Efficiency / reusable lesson

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`

`complete` means the bounded production publication gap is technically repaired and deployed; user real-site verification may still be pending and must be stated explicitly.
