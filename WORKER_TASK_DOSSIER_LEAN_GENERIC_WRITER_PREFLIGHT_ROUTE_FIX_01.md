# НОВЫЙ ЧАТ 2 — адресное исправление preflight для generic Lean writer

Task ID: dossier-lean-generic-writer-preflight-route-fix-01
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Registration main SHA (historical, re-fetch live main): 147be762d217dc1e7dc53a6fbd896f323f6af08c
Executor: NEW physical ЧАТ 2
Mode: bounded IMPLEMENT + regression; no live writer or semantic execution.

## Mandatory START
Work only in kentrap2011-hub/steam-kz-deals-2; use main as the sole source of truth. First FULLY read CHAT_PROTOCOL.md in live main, follow START gate, then read CHAT_CONTEXT.md and this complete WORKER_TASK file. Review relevant PROJECT_ROUTES.md, PROJECT_DECISIONS.md, config/execution_ownership_contract.json and frozen V2/generic replay/isolated Lean writer contracts before source edits. Use current main HEAD, not this registration's historical SHA. Do not touch any other repository.

## Confirmed real incident
User launched existing GitHub Actions workflow .github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml via manual workflow_dispatch for exactly six already-frozen Lean Dossiers. Verified failed live run:
- GitHub run: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45540222575
- Job ingest: 138956661141, ended failure before persistence at 2026-11-25T03:29Z.
- Owner/actor, main ref, three checkbox selection and Python setup steps all passed. Failure at step "Persist strictly checked reusable V2 batch in isolated sandbox only" BEFORE writer main code:
  DOSSIER_V2_BATCH_BLOCKED: [Errno 2] No such file or directory: config/dossier_notes_v2_batches/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4.json
- Triggering line currently `python scripts/dossier_notes_v2_batch_preflight.py --trial-id "${NOTES_V2_TRIAL_ID}"` in that workflow. This strict *old batch-cohort* preflight calls inspect() and demands `config/dossier_notes_v2_batches/{trial_id}.json`, which the *new generic request/issuer* legitimately does not generate.
- This is a demonstrated integration/routing defect, not grounds for repeating Research/Assembly or fabricating a legacy cohort contract.
- Source PR #478 already MERGED into main at 147be762d217dc1e7dc53a6fbd896f323f6af08c after writer-code L3. This real workflow was NOT covered by its fully green offline tests.

Exact frozen target:
- trial_id dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4
- sandbox branch sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4
- observed sandbox HEAD d1b9a9e78dcde879a03370682ade4969763fd9d1
- marker b267882dd3d056a1fc18d6a3fb75380ac38bd9cd
- original generic owner request 8adeee166cbc9d78107b76e28f253e4f547dfedc; authenticated issuer GitHub Actions run 45243093290, request nonce cdcdb4951e2fc98336729af75b954da4
- six AppIDs in manifest order: 1000010, 102600, 1029690, 49520, 499180, 501590.
- 6 ready Lean Assembly candidate blobs + 6 typed transport receipts exist. Persisted isolated accepted records remain 0/6. All main/Deep/production Lean switches FALSE.

## User-approved narrow objective
Fix ONLY the demonstrated old-batch-vs-generic trial preflight integration incompatibility **along the actual full GitHub writer route**, preserving secure fail-closed authorization for both legacy strict batch and generic owner-issued Lean modes. Achieve source-ready guarded writer entry, not live acceptance. This task is not permission to rerun failed GitHub Actions, create a new authorization/request/nonce, schedule or run semantic Research/Assembly, or turn on Deep/production.

## Implementation and security requirements
1. Trace both workflow shell preflight and ALL downstream writer entrypoints; do not assume the one failing shell line is the only blocker. Inspect `scripts/dossier_notes_v2_batch_preflight.py`, `scripts/dossier_notes_v2_batch_route.py::scope`, `scripts/dossier_notes_v2_generic_replay.py`, `scripts/taste_steam_review_dossier_buffered.py::_drain_notes_v2_individual`, `scripts/dossier_lean_canonical_dual.py`, `scripts/dossier_notes_v2_isolated_lean_readback.py`, existing frozen policy and exact owner Actions route. Identify any other source-cohort-only lookup reachable by the generic writer. Keep source import from pinned main as designed.
2. Route explicitly recognized generic trial IDs to their OWN existing immutable request/grant/manifest/authorization + authenticated owner issuer preflight, never old cohort contract. Route all genuine legacy reusable batch IDs through their old unchanged cohort preflight. Unknown/malformed/unissued trial IDs must fail closed; never skip preflight solely because file missing, never add dummy old contract, never broaden generic trial acceptance.
3. Preserve owner actor/repository/ref/attempt gate, exact frozen six, marker and assignment binding, typed Research + Assembly receipts, source Git SHA/provenance, original 0/6 and atomic twelve-file acceptance protocol, duplicate/collision protections, no early positive acceptance without genuine Git push/readback. Do not touch or loosen owner-credential or security checks unless required by the precise route defect and backed by negatives.
4. Exercise offline and CI regression against the **actual GitHub writer command path**: valid frozen generic trial must pass READ-ONLY preflight and reach existing per-item writer verification; missing/malformed generic request/grant/manifest, wrong owner/ref/attempt, wrong marker or immutable receipt, stale sandbox, wrong versioned format, invalid group count, old strict reusable cohort PASS and malformed strict cohort FAIL. Negative tests must prove no stage/save action when authorization fails. Keep prior Notes V1/V2 and strict group functionality unchanged. Any mocks are labeled, not represented as real GitHub approval.
5. Target code changes to narrow specific files and tests/workflow. Maintain all global flags OFF and avoid unrelated new architecture, duplicate writer, producer change or permanent activation. If a higher-level authorization redesign becomes necessary, STOP and report proof; do not silently expand permissions.
6. Produce one source PR based on live main plus complete worker report `reviews/worker_reports/dossier-lean-generic-writer-preflight-route-fix-01.md`: incident evidence, exact cause and changed lines, tests (including regression that would have caught run #45540222575), exact HEAD/CI, residual risk. Do not self-merge. Because a real writer authorization boundary is affected, flag independent security L3 QA on material delta for Director before merge. Do not assert source CI = real acceptance.

## HARD STOP
NO workflow_dispatch or rerun of run 45540222575; do NOT use GitHub "Re-run jobs" or "Run workflow". NO writer persistence, new owner grants, new request/nonce, new Research, Assembly, Deep, production, scheduler, retry/recovery, live canonical main store edits or modifying existing sandbox records. This approval is FIX ONLY. After source QA and Director merge, determine safe next owner-run authorization separately; the owner must approve it. If old single-use policy blocks a new first-attempt run for this same trial, report that explicitly rather than bypassing the policy.
