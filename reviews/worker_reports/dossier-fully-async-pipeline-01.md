# Worker report — Dossier fully async Research → Assembly 01

Date: 2026-10-09  
Worker slot: **ЧАТ 1**  
Task: `WORKER_TASK_DOSSIER_FULLY_ASYNC_PIPELINE_01.md`  
Base: `main`; implementation: `implement/dossier-fully-async-pipeline-01`  
Status: **implementation verified by PR-only CI, ready for Director review; NOT active**

## Architecture preflight

1. **Current owner:** `config/execution_ownership_contract.json` assigns all scope, ordering, binding, validation, acceptance, retry, recovery and canonical Dossier to GitHub. Semantic ChatGPT is data-plane only.
2. **Authority:** this explicit user decision plus task file amends only future **inactive** `dossier_two_stage_*` contracts before any activation.
3. **No ownership transfer:** GitHub preauthorizes every finite exact manifest, workers may only traverse it and create one immutable result per game; GH validates the chain later.
4. **No new scheduler/queue/retry:** no Scheduled Tasks, recurring workflows, canonical paths or production runtime hooks altered.

## Changes

- Removed the fixed 8-open-slot/unresolved-count liveness check from the inactive async helper/contract. A `new_authorization_limit`, if chosen by GitHub, applies only at preparation of a future **new** immutable finite manifest; preauthorized traversal never asks GitHub for slot release.
- Preauthorized Assembly plan V2 references original GitHub-prepared Research work blob and exact item/target, not GitHub Research acceptance.
- Provisional Assembly obtains the **submitted** Research bytes from a create-only Git commit; proves original Research marker/assignment first-parent ancestry and retains exact original commit, path, Git blob SHA, raw-byte SHA-256, canonical JSON SHA-256, Research prepared work blob and Assembly plan blob.
- New inactive `DOSSIER-ASYNC-ASSEMBLY-RESULT-V1` candidate schema repeats that immutable Research transport provenance, without falsely claiming acceptance.
- Eventual offline GitHub chain checker first validates the original Research transport using existing strict Research P2 logic. If invalid, quarantines only that item chain. If valid, checks the Assembly candidate exact binding, then uses existing strict Assembly semantic/gap validation; ready-to-publish V2 payload also undergoes the existing strict V2 Dossier validator. It **never** writes canonical Dossier, issues Deep readiness or replaces existing atomic three-game group acceptance.
- The old inactive accepted-only P2 staging helper remains available for legacy fixture compatibility but is **not** the new async semantic execution handoff. This avoids changing live Dossier.
- Persisted architecture decision `DOSSIER-ASYNC-001`, updated short route, execution ownership and temporary handoff.

## Tests included

`scripts/test_dossier_two_stage_async_buffer.py` uses disposable Git history to verify:
1. Research A submitted/unaccepted while B/C proceed.
2. Preauthorized Assembly A directly consumes submitted Research A with no accepted receipt.
3. Assembly B/C proceed while A unvalidated.
4. Late Research A rejection invalidates A's Assembly chain, B/C survive.
5. Invalid Assembly A does not invalidate B/C.
6. No unresolved-slot or GitHub ack in existing buffer liveness; optional limit only constrains **new** issuance.
7. Exact Research transport blob, hash, marker and plan binding; stale/duplicate, wrong-work, and overwritten commit fail closed.
8. Workers cannot invent/reorder/recover items beyond GitHub-prepared scope.
9. Current one-stage and legacy P1/P2 interfaces remain untouched and disabled.
10. A real 12-item frozen Research manifest (four 3-game groups) passes despite the former 8-slot boundary.

PR-only validation workflow: `.github/workflows/validate-dossier-two-stage-contract-interfaces.yml` (P1/P2/async, one-stage factual dates, Dossier/Deep year-kind compatibility).

## GitHub CI evidence

PR: #179 (open). Implementation/test head `45ef0dfb587826444c15e5be7e525f7fe287e6a6`.

- Inactive Dossier two-stage interfaces (P1/P2/async/one-stage factual dates/year-kind): run `37933053587` — **success**.
- Validate execution ownership: `37933053650` — **success**.
- Validate backlog dispositions: `37933053596` — **success**.
- Validate Progressive PASS 2 core: `37933053638` — **success**.
- Validate site publication resilience: `37933053622` — **success**.

These are offline/PR-only regressions. They do **not** prove a live production pipeline, because activation and semantic workers remain explicitly forbidden.

## Boundaries / residual work

- **Not implemented:** Research or Assembly semantic workers, live two-stage ingest/writer integration, production activation, scheduled task changes. No worker executes from this PR.
- **Final canonical Dossier:** only existing strict V2 3-game GitHub atomic validation can accept; no per-item helper result is acceptance or Deep-ready.
- Future integration must reconcile already persisted Research receipt idempotently and bind the original submitted bytes. All resulting stage counters/observation require a separate activation review.
- **Next action:** Director reviews this PR and its CI tests; do not merge/activate as semantic pipeline without distinct integration/cutover authorization.
