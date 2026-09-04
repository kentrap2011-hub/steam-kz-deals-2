# WORKER TASK — GIVEAWAY LIVE SITE MISMATCH RECON 01

Task ID: `giveaway-live-site-mismatch-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`

## New user evidence

After `giveaway-publication-gap-fix-01` reported a successful Pages deploy whose exact artifact contained active giveaway `Alone With You`, the user checked the real site on mobile and **the giveaways still did not appear**.

Therefore the user-visible incident is NOT closed.

Do not reopen the Epic parser or the already-proven canonical -> visual routing fix by default. Treat this as a new downstream mismatch between the technically deployed artifact and what the real site/browser serves or renders.

## Goal

Find the exact first boundary where the live user-facing site diverges from the successfully deployed Pages artifact that contains `Alone With You`.

Trace only:

`deployed Pages artifact -> live HTTP-served files -> browser-loaded data -> giveaway render/view`

## Read first

1. Current `main`.
2. `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`.
3. `reviews/worker_reports/giveaway-publication-gap-fix-01.md`.
4. Only the exact current deploy/frontend/cache/service-worker files needed to trace live delivery and giveaway rendering.

No broad Git/Actions archaeology.

## Minimum checks

1. Fetch/inspect the actual public Pages site and the exact live data URL the frontend uses.
2. Determine whether the live HTTP-served payload currently contains `Alone With You`.
3. Compare the live-served payload/build version with successful deploy run `33832350887` / Pages build version `ee0a609cfa15612e19249089206fefa9d6dda714`.
4. If live payload is stale, classify why: Pages/CDN delay, wrong path, old deploy still served, cache headers/service worker/app cache, or another exact delivery boundary.
5. If live payload contains the giveaway, trace whether browser/frontend state/filter/render suppresses it.
6. Inspect service-worker/cache behavior only if it is actually present in the current frontend path.
7. Do not treat a hard refresh as the permanent fix. It may be used only as a diagnostic comparison.
8. Identify exactly one smallest safe next fix if the defect is proven.

## Boundaries

Do NOT:
- change code in this task;
- change `scripts/giveaway_epic.py`;
- change giveaway eligibility/region/price semantics;
- change canonical giveaway data;
- change ITAD/IGDB;
- change Taste/ranking/paid deals;
- redesign the giveaway UI;
- weaken freshness/completeness contracts;
- perform broad Actions/history investigation.

## Done when

Save:
`reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`

Include:
1. Task
2. New user evidence
3. Live delivery evidence
4. Exact first divergence boundary
5. Root-cause classification
6. Smallest safe fix
7. User verification needed
8. Unresolved
9. Status
10. Exact refs / URLs / headers / build versions

Status exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

If a concrete defect is proven, recommend one bounded IMPLEMENT task but do not implement it in this recon.
