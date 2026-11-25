# ЧАТ 2 — Generic Lean writer preflight route fix 01

- Task: `WORKER_TASK_DOSSIER_LEAN_GENERIC_WRITER_PREFLIGHT_ROUTE_FIX_01.md`
- Repository: `kentrap2011-hub/steam-kz-deals-2` only
- Initial main HEAD: `a8708f68081abf4dcfdae08bae6fdca373318bdc`
- Source branch: `fix/dossier-lean-generic-writer-preflight-route-20261125`
- Status: `IMPLEMENT_IN_SOURCE_PR_PENDING_CI_INDEPENDENT_SECURITY_L3`
- Real acceptance: **0/6**. No live writer, semantic execution, rerun, Deep, production or issuer was invoked.

## Confirmed incident and root cause

GitHub Actions failed real owner writer run `45540222575` (job `138956661141`) on 2026-11-25 at the **shell preflight** of the existing shared writer. The command `python scripts/dossier_notes_v2_batch_preflight.py --trial-id "${NOTES_V2_TRIAL_ID}"` tried to open `config/dossier_notes_v2_batches/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4.json`. Its absence is legitimate: this versioned generic trial was issued from a one-add owner request, grant, manifest, nonce marker and direct-child authorization, not a per-trial source cohort config. The run exited 2 before writer verification or stage/push. The prior PR #478 offline tests did not exercise this full workflow shell route.

## Architecture preflight

1. **Owner**: GitHub Actions holds manifest/authorization, canonical writer, strict Git transport receipts, staging/push and completeness; interactive chat edits source only.
2. **Authority**: `config/execution_ownership_contract.json`, `config/dossier_notes_v2_generic_replay_policy.json`, `config/dossier_notes_v2_isolated_lean_acceptance.json`, legacy `config/dossier_notes_v2_batch_policy.json`, and inactive global V2/Lean writer contracts.
3. **Boundary**: none of these responsibilities is delegated to ChatGPT; owner Actions run must authenticate independently, not from a user-provided claim.
4. **No new** recurring worker, queue, retry, runtime, approval or semantic attempt. Both source/Deep/production flags remain OFF.

## Precise fix

1. `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`: pin reviewed main source for any generic-prefixed request; route generic prefix to a new *read-only* generic preflight, while genuinely legacy IDs still execute their original cohort preflight unchanged. Keep the main-ref owner/attempt gate, exact selected sandbox checkout, local/remote HEAD equality check, exact-six staged and committed 12-file readback, nonforce single sandbox push and post-push readback.
2. `scripts/dossier_notes_v2_writer_preflight.py` (new): require exact `dossier-notes-v2-assembly-replay-<32 lowercase hex>`, actual owner workflow/ref/actor/attempt context, nonempty bounded SHA map and exact sandbox branch. Recheck existing generic policy, unique immutable authorizer, request-bound grant/manifest/nonce/authorization structure via `batch.issuer_structure` → `generic.issuer_structure`, frozen manifest via `v2._manifest` / `generic.frozen_plan`, and completed **authenticated first-attempt owner Actions issuer** via existing `batch.authenticated_owner_run`. For the only approved exact-six Lean trial, also require its existing immutable marker, frozen sandbox HEAD, per-item pair, typed receipt blob and zero previously accepted records via `require_isolated_sandbox_writer` before writer verification. Malformed generic prefix must fail closed rather than fall through to legacy or bypass issuer.
3. `scripts/taste_steam_review_dossier_buffered.py::_drain_notes_v2_individual` and `scripts/dossier_notes_v2_batch_route.py::scope` already recognize the generic/legacy split and retain their issuer, separate typed Research/Assembly receipts, validated final format and collision guards; no change to these security-critical persistence functions.
4. `scripts/test_dossier_notes_v2_writer_preflight.py` (new) exercises generic owner preflight → actual existing writer boundary in disposable Git, negative owner/run/ref/attempt, malformed/absent/modified issuer, marker, receipt and legacy fallback. **Mocks are synthetic only and NOT actual GitHub authorization or source truth.**
5. `.github/workflows/validate-dossier-research-notes-v2.yml`: PR-only test hook and Python compile gate for the new preflight/route regression. No production workflow dispatched.

## Checks and residual risk

- Regression intended to detect run #45540222575: the actual writer workflow's generic prefix must select the authenticated generic issuer path and **never** try the nonexistent old cohort config; legacy must keep old cohort check.
- Test results: **pending PR checks at final SHA** (update this report on completion).
- Exact final HEAD: **pending last report/CI commit** (see final PR head; update on completion).
- Source CI does **not** equal real owner writer acceptance. Same trial's failed real Actions run may consume a single-use attempt policy; no recovery, new request, nonce, run retry or reissue is authorized here.
- Mandatory independent **security L3** on the material writer authorization route delta and Director approval before merge. Real owner-run readback and 6/6 persisted remain explicitly **unverified**.
- No changes to original18, Notes V1, Deep/production caches, scheduled tasks, canonical main Lean store, existing sandbox receipts or global switches.

## Runtime/latency note

The investigation involved the complete START/ownership checks, the failed job log and exact workflow/issuer/shared-writer source path. This was necessary because a fix limited to the first shell line could still have left downstream generic source-cohort lookups. The durable new command-route regression should prevent rediscovering this incident after future source changes.
