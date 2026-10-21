# Site publication failure isolation — READ-ONLY architecture investigation (2026-10-21)

Status: REPORT ONLY; no production remediation or runtime deploy authorized.

## Verified runtime evidence
- [Deploy run 39479228940](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39479228940), job 118823116489: `Run UI regressions` fails; `scripts/test_site_tasks.py` reports four FAIL and five ERROR, including `Unexpected/omitted task registry fields` and `KeyError: 'recent_completion'`. This is the Director tasks test path, not a proven paid-game corruption.
- [Deploy run 39456363674](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39456363674), job 118744176966: `Validate visual freshness receipt contract` exits with `OSError [Errno 39] Directory not empty: 'objects'` while executing `test_giveaway_source_mismatch_fails_closed`. This is a temporary Git fixture cleanup failure, not a proven actual receipt mismatch.
- Both jobs terminate before Pages deployment. This establishes blocked deployments for these two runs, NOT the last successful publish timestamp or the freshness of each individual data domain.

## Current main inspection
- `web/app.js::sourceLabel` displays `data.source_mailing_updated_at_utc` from `data/current.json`; this is a source timestamp, not a Pages deployment timestamp.
- `.github/workflows/deploy-visual.yml` runs two synthetic receipt/material tests before classification; runs nine UI commands serially including `python scripts/test_site_tasks.py` and `node web/tasks.test.js`; later `Generate static Director task page data` is mandatory before Pages upload. Thus unrelated tasks tests and task-data generation are both blockers.
- `Validate independent current site status` is also currently a blocking step when present, and `Validate giveaway visual payload` can block paid publication. `Record Russian description diagnostic` is a blocking command despite its diagnostic label. Classification and source-binding checks remain critical.
- `config/site_publication_resilience_contract.json` already authorizes local identifiable defect quarantine, compatible last-good fragments or omission, independent status publication, but requires global identity/material/source integrity fail closed.
- `config/execution_ownership_contract.json`: GitHub owns classification, publication, canonical integrity and persistence; browser remains read-only. No new scheduler/ChatGPT ownership.

## Actual freshness: evidence limit
- The repository file API returns an empty content body for large `data/production/visual/current.json`; `web/data/current.json` is generated only in Pages staging and absent from main. No verified deployed JSON bytes, GitHub Pages deployment manifest, or successful build/deploy chronology was available in this inspection.
- Therefore paid games, discounts, analytics freshness and precise date of last successful publication are **UNVERIFIED**; do not infer they are stale solely from displayed 16 October source timestamp or the two failed runs.
- Required read-only proof: retrieve current canonical visual JSON from pinned Git commit or build artifact; retrieve live Pages `data/current.json` and `data/status.json`; compare hashes, source timestamps, item count/IDs, prices, discount/offer expirations, ranking/Deep/Fast statistics, receipt source bindings, and latest successful build/deploy run IDs. Keep commercial source freshness, visual build freshness and Pages deployment freshness distinct.

## Developer assignment — minimum safe changes
1. Keep core paid publication fail-closed on missing/contradictory source identity, prices/offers, canonical scope, material SHA, schema, safety and exact build receipt. Never make critical checks `continue-on-error`.
2. Split required **production acceptance** from unrelated **regression CI**. Move synthetic `test_visual_freshness_receipt.py` and `test_visual_material_freshness_guard.py` into dedicated PR/CI; Deploy must still execute the actual receipt verifier against the exact staged bytes and upstream run. Fix temp-Git cleanup race separately without weakening mismatch tests.
3. Move `scripts/test_site_tasks.py` and `web/tasks.test.js` to task-page PR/CI. During Deploy, validate/generate task section in an isolated step; if it fails, use a previously published task artifact only with integrity and compatibility proof, otherwise omit tasks link/data and report degraded section. Never publish invalid newly generated tasks.
4. Treat independent status and giveaways as independently versioned optional publication sections ONLY where their contracts explicitly permit fallback. Keep source binding verification per section; if status-only event, require exact status validity. For a full paid deploy, a status failure must not suppress validated paid bytes. Giveaway isolation needs contract-specific proof and safe omission; no unconditional bypass of a globally coupled source contract.
5. Examine Russian description diagnostic and each UI test for whether it is a core data/safety validator or an optional presentation regression; preserve true core gates and move independent regressions to CI. No blind disabling of tests.
6. Preserve Pages artifact atomicity: stage a complete internally consistent snapshot and publish once. Record source, staged and published hashes, section dispositions (fresh/reused/omitted), last-success timestamps and quarantined reasons. Never mix incompatible versions of ranking/analytics/prices.
7. No new queue, recurring task, retry daemon, production worker, or change to GitHub ownership.

## Required QA acceptance
- Fault injection: broken tasks registry, tasks tests, tasks generator, optional status, giveaway and diagnostic do not block independently validated paid publish; tasks fallback is integrity checked or omitted.
- Negative: altered paid prices, invalid discount scope, missing canonical input, stale/mismatched receipt, material SHA drift, corrupted core payload and wrong run ID **block** paid publication.
- Test synthetic Git cleanup race is fixed deterministically; mismatch tests continue failing closed on genuine mismatches.
- Check paid/giveaway/status-only triggers independently, source-to-stage-to-deploy exact hashes, no unexpected files or changes, last-good compatibility and no broken navigation to omitted tasks.
- Independent QA verifies workflow diff, matrix, security, source binding, real GitHub Actions dry run / PR-only checks and separately authorized post-merge deploy. Do not claim end-to-end success without runtime verification.

## Decision / gate
RECON COMPLETE FOR THE TWO SPECIFIED FAILURES; ACTUAL SITE FRESHNESS UNVERIFIED. Proposed isolation fits SITE-PUBLICATION-RESILIENCE-V1 in principle; any new section fallback identity or missing contract authority must be specified/approved before implementation. This PR contains report only and does not authorize code changes or deployment.
