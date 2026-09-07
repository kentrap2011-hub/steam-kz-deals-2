# Worker Report — Publication Freshness Pre-Fix Forensic Recon 01

## Task
`publication-freshness-pre-fix-forensic-recon-01`

Mode: `READ-ONLY / RECON / FORENSIC`

Goal: freeze and explain the current paid-list publication freshness failure before any repair, and assess the prepared repair task without mutating production state.

## Verified facts
- Investigation started from current `main`.
- Required forensic report was created before expensive investigation, per `WORKER_REPORT_DURABILITY_PROTOCOL.md`.
- No repair, manual refresh, scheduler, writer, workflow, contract, Taste, or production-state mutation has been performed.
- The only repository mutation made by this recon is this report.
- Fresh Steam-derived deterministic state is reaching the canonical commercial pipeline above visual publication:
  - `data/production/shortlist/index.json`: `updated_at_utc=2026-09-06 21:00:38 UTC`, `app_count=4671`, `source_snapshot_id=steam_kz_daily::2026-09-06T21:00:38Z::raw`, integrity SHA-256 `5b9789ec59aecfd14376b35272196435d2f94f202d62dc35ef758421741652e1`.
  - `data/production/mailing/index.json`: same source timestamp/snapshot/integrity identity, `app_count=4671`, content digest `7fcf0973d116dab3c88bc3311dcff798c402052cdc59359757c30402da527df0`.
  - `data/production/pre_ai/store_snapshot.json`: generated `2026-09-07 03:20:25 UTC`, bound to mailing source `2026-09-06 21:00:38 UTC`, source item count `4671`, selected entry count `45`, selected-appids SHA-256 `cb119223166edf2355004ea664feb93839939c3f8fdd2572b5d027229e502483`.
  - `data/production/pre_ai/family_graph.json`: same current mailing source binding, generated `2026-09-07 03:20:25 UTC`, entry count `45`.
  - `data/production/pre_ai/chatgpt_payload.json`: generated `2026-09-07 03:20:41 UTC`, same current mailing source binding, but `status=DEGRADED`, `failure_reason=chatgpt_completion_missing`, `semantic_status.complete=false`, `semantic_status.awaiting_chatgpt_completion=true`, `provenance_only=true`.
- Therefore the active break is not Steam ingest, shortlist publication, shortlist→mailing, or deterministic pre-AI source construction.
- `scripts/build_daily_visual_payload.py` deliberately fails closed unless ChatGPT payload status is `COMPLETE`; current `DEGRADED/chatgpt_completion_missing` therefore blocks the full visual rebuild path by design.
- A deterministic scoped helper already exists: `scripts/refresh_visual_commercial_fields.py`. It refreshes commercial/worthiness fields from current deterministic pre-AI truth while preserving already-published semantic labels and enforcing strict provenance/coverage checks. The helper itself is not the missing implementation.
- `.github/workflows/build-daily-visual-payload.yml` currently has a production `giveaway_only` branch but no analogous `commercial_only` classifier/job/receipt branch. `refresh_visual_commercial_fields.py` is covered by workflow change/test logic but is not production-invoked by the workflow.
- Thus the current inactive edge is the deterministic commercial handoff into canonical visual paid publication: the full route is stopped by the intended semantic fail-closed guard, while the already-existing scoped commercial refresh route is not wired into production orchestration.

## Current canonical chain
The current intended data/publication topology is:

`Steam ingest → data/production/shortlist → data/production/mailing → data/production/pre_ai/{store_snapshot,family_graph,chatgpt_payload} → visual publication orchestration → canonical visual writer/publication helper → data/production/visual/current.json + snapshot/latest aliases + data/published/visual_current.json + visual_current.js → frontend/site`.

There are two conceptually valid visual refresh modes:
1. full semantic visual rebuild, which correctly requires a semantically complete ChatGPT production payload;
2. scoped deterministic subdomain refresh, which may update independently refreshable deterministic fields while preserving unrelated/semantic state and proving preservation by receipt.

The giveaway incident already established mode (2) for giveaway data. The paid/commercial helper for mode (2) exists, but production orchestration does not expose a `commercial_only` route.

## Exact cause classification
### Primary cause
`missing / inactive production-orchestration handoff` at deterministic commercial state → canonical visual paid publication.

Specifically, the existing visual workflow has no `commercial_only` classification/job/receipt path that invokes `scripts.refresh_visual_commercial_fields` when commercial provenance becomes newer than the paid lineage in the current visual artifact.

### Contributing blocking condition
The full visual route is intentionally fail-closed on semantic incompleteness. Current `chatgpt_payload` is `DEGRADED` with `chatgpt_completion_missing`, so a full rebuild cannot legally absorb the fresh commercial state.

### Causes not supported by current evidence
- source scheduler gap: disproven by fresh shortlist/mailing/pre-AI artifacts;
- shortlist→mailing trigger failure: disproven by identical current source identity in shortlist and mailing;
- contract/version incompatibility as the active root cause: not observed;
- provenance/freshness guard incorrectly rejecting otherwise legal commercial-only refresh: not the root, because no production commercial-only invocation exists to reach that guard;
- missing commercial refresh implementation: disproven by existing `scripts/refresh_visual_commercial_fields.py`;
- need for a new scheduler or writer: contradicted by existing ownership/routing architecture.

## Why the system looked partially healthy
- Steam/source collection continued normally.
- Shortlist and mailing continued updating with a fresh shared source identity.
- Deterministic pre-AI store/family state continued updating from fresh mailing.
- Giveaway scoped publication was separately repaired and continued to mutate the visual artifact without changing paid rows.
- Therefore repository/workflow activity, fresh upstream timestamps, and even successful visual commits could coexist with a paid section whose commercial lineage remained stale.
- The frontend is correctly rendering the stale canonical paid facts it receives; entries whose retained sale window ended are therefore shown as `скидка закончилась` rather than being silently hidden or fabricated.

## Why freshness / receipt / fail-closed checks did not raise a clear stale-paid alarm
- Existing fail-closed checks are primarily integrity/safety gates: they prevent invalid full publication when semantic completion/provenance is missing.
- `scripts/visual_freshness_receipt.py` currently supports `full` and `giveaway_only`, not `commercial_only`.
- A successful `giveaway_only` receipt proves paid hash/order preservation and giveaway freshness, and explicitly has `full_visual_freshness=false`; it does not assert that paid commercial lineage matches the newest deterministic commercial source.
- A failed full refresh proves that full semantic publication is unsafe; it does not by itself enforce a paid-list liveness SLA or compare paid source timestamp/hash to newest mailing/store provenance and escalate prolonged lag.
- Net result: safety/fail-closed behavior worked, but no scoped paid-commercial freshness receipt/invariant converted the growing upstream→paid lineage lag into a dedicated alert/failure state.

## Comparison with previous giveaway incident
### Different
- Giveaway now has an explicit wired `giveaway_only` production path, classifier, preservation checks, and scoped receipt.
- Paid commercial refresh already has a strict helper but no corresponding production orchestration branch or receipt scope.
- Giveaway source is a separately refreshable subdomain; commercial refresh derives from current deterministic mailing/pre-AI truth and must preserve semantic labels/coverage while updating prices/discount windows/ranking-related deterministic commerce.

### Common systemic problem
Both incidents expose the same architectural coupling: multiple independently refreshable deterministic subdomains ultimately feed one canonical visual artifact, while the full visual path is coupled to a semantic-completion gate. If a deterministic subdomain has no independently wired scoped handoff, correct fail-closed behavior preserves old visual state indefinitely. Integrity protection therefore needs a paired liveness/freshness invariant for each independently refreshable publication subdomain.

## Frozen pre-fix evidence
### Current upstream/commercial identities
- shortlist blob SHA: `724d4914167e58615bc1b89193cebfdd8dcc5639`
- shortlist source timestamp: `2026-09-06 21:00:38 UTC`
- shortlist source integrity SHA-256: `5b9789ec59aecfd14376b35272196435d2f94f202d62dc35ef758421741652e1`
- mailing blob SHA: `029413ab406371948235f58f652f754dd9720fc2`
- mailing content digest: `7fcf0973d116dab3c88bc3311dcff798c402052cdc59359757c30402da527df0`
- store snapshot blob SHA: `1da3bf26fbb0a08a103698e23656141e85bc5426`
- family graph blob SHA: `6b1692bea0e33380b50016a1597654678212f28e`
- ChatGPT payload blob SHA: `db17224af3793744149e8e58ac10ef29e7177b46`
- ChatGPT payload state: `DEGRADED / chatgpt_completion_missing`
- current visual blob SHA before repair: `242275cf24368062f0c76535f305ba4688784ac0`

### Historical visual evidence
- Commit `d3d268a57b49b89f58867f88cfd1800f2398c06b` refreshed daily visual at `2026-08-31T20:37:59Z`.
- Subsequent visual commits on `2026-09-01` include `19472a7f...`, `f928af44...`, `0c6db0ea...`, `15db361d...`, `8a778db3...`, `9aa0aef0...`.
- Later visual mutations include giveaway-only refresh commits, including `a05aec8d...` on `2026-09-04`, `1d7fb4d1...` on `2026-09-06T17:14:23Z`, and `df4a96ac...` on `2026-09-06T21:01:43Z`.
- Prior freshness recon proved the paid section retained the `31 Aug 2026 00:37` commercial snapshot semantics/lineage while later visual activity preserved/reused those paid rows.
- Current retained evidence proves at minimum that fresh deterministic source cycles after that paid snapshot (including the `2026-09-06T21:00:38Z` source) did not reach canonical paid commercial publication.

## Historical break boundary
Exact first missed legal commercial-refresh invocation is still being bounded from retained history and must not be guessed.

What is already proven:
- paid visual commercial state is tied to the August 31 snapshot according to the prior freshness recon;
- September 1 full visual refresh activity existed but reused/preserved old commercial state rather than establishing a fresh deterministic paid lineage;
- upstream deterministic cycles subsequently advanced through September 2/3/5/6 while paid visual commercial state did not catch up;
- later giveaway-only visual commits are not evidence of paid freshness because they intentionally preserve paid rows.

If no retained run/receipt can prove the exact first missed handoff, final report will state the narrowest proven stale boundary rather than infer an exact failure timestamp.

## Architecture / reliability invariants
- GitHub Actions owns deterministic transforms, orchestration, canonical persistence, and fail-closed behavior per `config/execution_ownership_contract.json`.
- ChatGPT semantic incompleteness must continue to block full semantic publication.
- A scoped commercial refresh must never invent semantic truth; it may only preserve previously canonical semantic labels when coverage/provenance checks prove that preservation safe.
- Scoped commercial refresh must preserve giveaway state exactly.
- No second canonical writer, scheduler, or parallel publication chain is warranted.

## Repair task assessment — provisional
`WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md` is directionally correct but should receive a minimal pre-execution correction/clarification, not a redesign:
- explicitly reuse `scripts.refresh_visual_commercial_fields` rather than implement a second refresh mechanism;
- wire a `commercial_only` branch into the existing `build-daily-visual-payload.yml` orchestration;
- add scoped commercial receipt/freshness proof analogous in spirit to `giveaway_only`;
- keep the global `ChatGPT production payload is not complete` full-build guard unchanged;
- require current deterministic source binding plus complete prior semantic-row coverage; fail closed otherwise;
- prove giveaway preservation during commercial-only refresh;
- use existing orchestration/scheduling ownership; do not add a new scheduler or writer;
- acceptance must prove paid source timestamp/hash has caught up to the current deterministic commercial source and that the scoped receipt records the exact lineage.

## Validation
- Initial durability checkpoint persisted before investigation.
- Mid-investigation checkpoint records the reconstructed path, current source identities, primary break classification, guard blind spot, giveaway comparison, and repair-task direction.
- No repair action has been invoked.

## Unresolved
- Tighten the historical stale boundary from retained Git/workflow evidence if possible.
- Freeze current receipt/run identity if retained/accessible.
- Finalize repair-task safety verdict and report status.

## Status
`in_progress`

## Recommended next step
Complete bounded read-only evidence capture for visual/run/receipt history, then finalize this recon only. Do not execute repair.

## Exact refs
- Task: `WORKER_TASK_PUBLICATION_FRESHNESS_PRE_FIX_FORENSIC_RECON_01.md`
- Prepared repair task under assessment: `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01.md`
- Report: `reviews/worker_reports/publication-freshness-pre-fix-forensic-recon-01.md`
- Current visual: `data/production/visual/current.json`
- Commercial scoped helper: `scripts/refresh_visual_commercial_fields.py`
- Visual workflow: `.github/workflows/build-daily-visual-payload.yml`
- Freshness receipt implementation: `scripts/visual_freshness_receipt.py`

## Efficiency / reusable lesson
When a canonical aggregate artifact contains independently refreshable subdomains, fail-closed correctness and freshness liveness must be modeled separately. A healthy upstream plus a successful scoped refresh for one subdomain is not evidence that another preserved subdomain is fresh.
