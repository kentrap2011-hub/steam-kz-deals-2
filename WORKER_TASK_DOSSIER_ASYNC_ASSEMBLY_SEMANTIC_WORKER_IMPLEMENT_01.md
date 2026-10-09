# WORKER TASK — Inactive fully-async Dossier Assembly semantic worker 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Task ID: `dossier-async-assembly-semantic-worker-implement-01`
Physical developer slot: **ЧАТ 2 — NEW conversation**
Mode: **IMPLEMENT INACTIVE / OFFLINE VALIDATE**

## Goal

Implement the **inactive** Assembly semantic-worker entry prompt and the minimal bounded implementation/validation for a fully asynchronous Research → Assembly handoff. Assembly must consume **exact submitted immutable Research bytes** without waiting for a GitHub Research-accepted receipt, produce a create-only candidate and move on. This is implementation, **not** permission to run actual games or activate production.

Source decision: PR #179, `reviews/worker_reports/dossier-fully-async-pipeline-01.md`; current fully-async V2 Research/Assembly contracts.

## START / ownership / interfaces

1. Read current `CHAT_PROTOCOL.md` and execute START gate, then current `CHAT_CONTEXT.md` and this task **fully** from `main`.
2. Operate **only** in `kentrap2011-hub/steam-kz-deals-2`; if a tool defaults to another repo, stop and correct it.
3. Run architecture preflight. GitHub owns frozen Assembly preauthorization and scope/order, final whole-chain validation, retries/recovery, current one-stage canonical Dossier and Deep readiness.
4. Read targeted sections of `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, `config/dossier_two_stage_interfaces_contract.json`, `config/dossier_two_stage_staging_contract.json`, `config/dossier_two_stage_async_buffer_contract.json`, `config/dossier_async_assembly_result_v1.schema.json`, relevant Research package schema and existing offline P2/async helpers. Avoid broad repo search.

## Required implementation

- Deliver a versioned **inactive Assembly semantic-worker prompt** (suggested `config/dossier_two_stage_assembly_semantic_worker_prompt.md`) and only required Assembly-specific helper/contract/offline tests. Follow the actual fully-async V2 handoff, **not** legacy accepted-only P2.
- Traverse the **exact frozen GitHub-preauthorized Assembly plans** in original order, bound to the actual single-parent Assembly marker and the originally prepared Research assignment/plan/blob. No self-selected games, scopes, retry/recovery, lease or unbounded dynamic discovery.
- For each ready item, consume only the **exact already-submitted create-only Research Git transport**: original commit + path + Git blob SHA + raw-byte SHA-256 + canonical Research JSON SHA-256 + original Research marker/parent + prepared work blob + Assembly plan blob. Verify binding without inventing acceptance. **No Research GitHub acceptance receipt is required**.
- No dependency on a previous Assembly acceptance or fixed unresolved-slot/backpressure. If an item's Research package is not yet submitted or is mismatched, fail/skip **only that item** as appropriate under the frozen contract without falsely consuming a semantic attempt, and continue with other ready siblings. Do not poll/wait for GitHub ingestion and do not invent a retry schedule.
- Use exact Research source evidence first; revisit the **exact original source** for each named gap before any narrow, single-gap lookup. Follow bounded gap/identity/privacy rules: no broad re-research, speculative facts, fake dates, author identifiers, quotes, duplicate-source independence or fabricated evidence. Material unresolved contradictions return typed diagnosis to GitHub.
- Emit a schema-valid `DOSSIER-ASYNC-ASSEMBLY-RESULT-V1` create-only candidate only at the frozen `data/ai_inbox/dossier_assembly/{snapshot_id}/g{sequence:06d}/{appid}--{assembly_assignment_id}.json` path. Preserve all frozen original bindings and consumed Research transport provenance; never overwrite, rename, rebind or directly publish canonical Dossier.
- Invalid Research A or Assembly A must not block independently valid B/C. Eventual GitHub validation may later reject the A chain; **only existing strict V2 GitHub three-game atomic acceptance** may publish canonical Dossier or unlock Deep.
- Remain `active=false`, `authorized_for_semantic_execution=false` and `executable_in_production=false`. Do not claim both semantic stages production-ready or turn on global worker flags.

## Concurrent work boundary

ЧАТ 1 independently implements inactive Research worker. Do not edit Research-owned worker prompt/package schema/helpers or its task/report. Avoid rewriting shared interfaces. If a shared change is unavoidable, document the exact blocker for Director rather than create conflicting parallel edits. A submitted test Research package may be supplied by existing P2 offline fixture helpers; do **not** run the new real Research worker.

## Verification / deliverables

- Isolated disposable-Git offline tests: submitted yet GitHub-unaccepted Research A can be consumed; exact byte/blob/hash/marker checks; Assembly A candidate before acceptance; continue B/C; late Research A rejection quarantines only A; invalid/missing/stale Research and duplicate candidate fail closed; exact-source-first named-gap behavior; no worker-chosen retry/lease/order; inactive guards and existing one-stage parity.
- Run appropriate P1/P2/async, execution-ownership and Assembly schema validation; CI must be offline/PR-only, with no production writes or actual semantic work.
- Report: `reviews/worker_reports/dossier-async-assembly-semantic-worker-implement-01.md` with test evidence, exact file ownership, blockers, PR and explicit non-activation.
- Open one focused PR against latest `main` in a new implementation branch; **do not merge it**. Update `CURRENT_TASK.md` safely without deleting unrelated work.

## Hard prohibitions

No live Research or Assembly execution; no fake production results, no one-stage Dossier mutation, no Deep/Fast/ranking/site/Steam/translation changes, no production scheduler, no secrets, no other repository, no `manual-shell-write.yml`. Do **not** create/change/run/delete any Scheduled Tasks or automations.

## Finish

Stop after inactive implementation and PR-only verification. Next step is Director acceptance and a separately authorized integration/quality and activation sequence; do not execute canonical cutover.
