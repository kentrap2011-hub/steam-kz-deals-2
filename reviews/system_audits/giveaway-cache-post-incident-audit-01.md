# Giveaway cache post-incident audit 01

Status: `complete`

Task: `giveaway-cache-post-incident-audit-01`
Mode: `READ-ONLY / AUDIT`

## Scope and exact refs

This audit follows `SYSTEM_AUDITOR_ROLE.md` and is intentionally pinned to the stabilized incident refs from `WORKER_TASK_GIVEAWAY_CACHE_POST_INCIDENT_AUDIT_01.md`. It does not reopen Epic parsing, giveaway canonical source logic, broad history, or unrelated later deploy-gate-only work.

Exact evidence reviewed:
- `reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`;
- `reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`;
- `reviews/worker_reports/giveaway-cache-identity-production-shape-fix-01.md`;
- final implementation commit `024f81937942987c96bb5db1b0e1d7b66dd67587`;
- deploy run `33841356092` and deploy job `100924142727`;
- Pages artifact `9925017623`;
- user acceptance recorded for 2026-09-04: the real existing mobile session showed giveaways correctly without clearing site data;
- `config/execution_ownership_contract.json`;
- `DIRECTOR_REVIEW_CHECKPOINTS.md`;
- `DIRECTOR_TASK_BOARD.md`.

## Finding 1 — production giveaway publication identity is now authoritative and production-shaped

**User impact:** resolved. A giveaway-only publication can no longer be discarded as `refresh-identical` merely because the ordinary paid-feed `generated_at_utc` did not change. This closes the user-visible stale-giveaway failure mechanism proven by the recon.

**Evidence:** the final commit changes `payloadIdentity()` to combine the existing `generated_at_utc` with `payload.production_contract.source_giveaway_snapshot_blob_sha`. The prior failed acceptance established that this provenance field exists in the actual deployed production schema while the rejected flat giveaway fields did not. The production-shape fix report then inspected exact Pages artifact `9925017623` and found both the shipped bootstrap code reading this provenance field and the shipped production payload containing it. The exact commit diff is limited to replacing the synthetic giveaway identity inputs in `web/feed-bootstrap.js`.

**Severity:** original incident severity was high because fresh user-visible giveaway data could be fetched and silently not applied; residual severity after the final fix is `none found` within this bounded failure class.

**Assessment:** **proven resolved**, not a risk hypothesis.

**Bounded verification/fix candidate:** no further incident fix is required. Preserve the production-shaped identity regression as the guard for this publication identity contract.

## Finding 2 — true-identical behavior, LKG fallback, and single cache/bootstrap ownership are preserved

**User impact:** positive. Truly identical payloads still avoid an unnecessary application refresh, while a changed giveaway publication reaches the existing application/render path. Offline/cache-first usability remains intact.

**Evidence:** the production-shaped regression at the exact deployed commit proves three relevant branches: (1) identical production-shaped payloads produce `refreshOutcome === 'identical'` and do not re-run `init()`; (2) stale-vs-fresh giveaway provenance with unchanged ordinary feed fields produces `refreshOutcome === 'updated'`, exactly one `init()` call, and delivery of the fresh payload; (3) when network refresh fails, the cached LKG remains the ready source and no application re-init occurs. The exact bootstrap still has one cache name (`steam-deals-feed-lkg-v1`), one `readLastGood`/`writeLastGood` cache path, and one existing `startBackgroundRefresh()` reconciliation path that calls the existing `applyBackgroundPayload()`/`win.init()` mechanism. The final implementation commit introduces no second cache, scheduler, queue, publication store, or identity owner.

This is consistent with `config/execution_ownership_contract.json`: canonical publication/data authority remains in the repository/GitHub control plane; the browser bootstrap only performs its existing bounded LKG resilience/reconciliation role. No control-plane responsibility was moved into an interactive or parallel authority.

**Severity:** `none found` for new cache ownership, hidden dual-state authority, or new fail-open weakness.

**Assessment:** **proven** for the changed path and focused regression coverage.

**Bounded verification/fix candidate:** none required for incident closure; keep future cache identity changes inside the same single bootstrap/cache ownership boundary.

## Finding 3 — the evidence chain is sufficient to close this failure class

**User impact:** the production outcome, not only local code behavior, is verified. The exact fix passed the canonical Pages deployment path, reached the exact Pages artifact, and then succeeded in the user's pre-existing mobile browser state without requiring cache/site-data clearing.

**Evidence:** run `33841356092` is `completed/success` at head SHA `024f81937942987c96bb5db1b0e1d7b66dd67587`; its only deploy job `100924142727` is successful, including `Validate giveaway visual payload`, `Run UI regressions`, `Upload Pages artifact`, and `Deploy to GitHub Pages`. The run exposes exactly one Pages artifact, `9925017623`, tied to the same head SHA. The production-shape fix report records exact artifact inspection and a passing focused regression. `DIRECTOR_REVIEW_CHECKPOINTS.md` and `DIRECTOR_TASK_BOARD.md` record the final real-device acceptance on 2026-09-04 without clearing site data.

Together these cover the failure chain that mattered here: production-shaped identity semantics -> focused behavior -> canonical deploy gate -> exact deployed artifact -> real existing-browser acceptance. No exact incident evidence points to a remaining cache ownership, publication identity, fail-open, or hidden dual-state defect requiring another incident-specific change before normal backlog continues.

**Severity:** `none found` after acceptance.

**Assessment:** **proven sufficient for systemic closure of this incident class**. This does not claim immunity from unrelated future cache/publication defects outside the bounded evidence.

**Bounded verification/fix candidate:** no incident-specific follow-up implementation is required.

## Required questions

1. **Does `payloadIdentity()` now use an authoritative field that actually exists in the production payload for giveaway-only publication identity?** Yes — `production_contract.source_giveaway_snapshot_blob_sha`, verified against the production-shaped contract and exact deployed artifact evidence.
2. **Does the fix preserve true-identical behavior and avoid unnecessary refresh application when payload identity is genuinely unchanged?** Yes — the exact production-shaped regression proves `identical` with zero `init()` calls for truly identical payloads.
3. **Does the fix preserve existing single cache/bootstrap ownership rather than creating a second cache or publication authority?** Yes — the change is confined to identity derivation inside the existing bootstrap and retains the single LKG cache/reconciliation path.
4. **Did focused production-shaped regression + exact deployed artifact + user mobile acceptance provide sufficient evidence to close this failure class?** Yes.
5. **Is any immediate follow-up required before ordinary backlog continues?** No incident-specific implementation follow-up is required.

Giveaway cache incident systemic closure: accepted
Recommended next task: Director checkpoint reconciliation — record this completed audit as the current System Audit and clear/reset the due checkpoint state when reconciling the parallel deploy-gate report.