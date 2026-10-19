# WORKER TASK — DOSSIER SHADOW ASSEMBLY: GITHUB PYTHON VALIDATION AND SEMANTIC TRANSPORT FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Task ID: `dossier-shadow-assembly-github-python-handoff-fix-01`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`
Mode: `RECON / CONTRACT GATE → IMPLEMENT / VALIDATE only if architecture preflight passes`
Scope: nonproduction isolated 18-game Research→Assembly trial only.
Report: `reviews/worker_reports/dossier-shadow-assembly-github-python-handoff-fix-01.md`

## Scope and START gate

Use **only** `kentrap2011-hub/steam-kz-deals-2`. Never silently work in any other repository. Start by fully reading current `CHAT_PROTOCOL.md`, completing START gate, then read this file completely, relevant routes, `config/execution_ownership_contract.json`, `CHAT_CONTEXT.md` architecture preflight and exact Dossier sandbox contracts. This is a **developer task**, not a Research/Assembly semantic run, not authorization for any Scheduled Task, and not authority to change production.

## Verified frozen evidence

- Original isolated branch: `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`.
- Research marker: `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`.
- Direct-child Research feasibility authorization: `2a726cf6731c0fc1e7bc809474627383c107ef9b`.
- Research: exactly 14 create-only submitted JSON files from frozen original 18. Four AppIDs missing: `1508750`, `1607130`, `1849000`, `1857090`. Independent QA observed Research defects in SULFUR (2124120) and Sifu (2138710), but original Python inspect was not executed. All submitted Research reports `research_incomplete`; this does NOT by itself block the isolated Stage B inspect.
- Assembly issuer GitHub Action: `39054131983`, `workflow_dispatch`, first attempt SUCCESS on original sandbox.
- Assembly buffer commit: `9782ab8492aadc744c23ec0425abf8d2d877590e`.
- Assembly marker commit / pinned sandbox HEAD: `2c2649fb98322507cd3758ff0ff7992128f94de0`.
- Fixed 6 groups `3,8,13,15,18,20`, 18 games; no real Assembly candidate published.
- Prior manually invoked Assembly chat stopped `BLOCKED` **before semantic work**: its environment had Python and jsonschema but could not obtain a real Git checkout because GitHub DNS for git/curl failed. The chat was correctly forbidden from fabricating Python inspect by porting validators to JS.
- Working GitHub Actions issuer was able to checkout and run Python. Do not repeat this one-shot issuer.

## Task: repair the COMPLETE technical handoff, not just one read-only check

1. Independently verify actual current GitHub state and original frozen contracts. Read: `config/dossier_shadow_18_assembly_semantic_prompt.md`, `config/dossier_two_stage_assembly_semantic_worker_prompt.md`, `scripts/dossier_shadow_18_assembly_stage_b.py`, the Research strict schema/transport validators and Assembly candidate schema/verification.
2. Perform mandatory architecture preflight BEFORE implementation. Explicitly prove GitHub still owns immutable queue, git provenance, deterministic validation, publication/receipts and retry/completeness; ChatGPT owns only explicitly authorized narrow semantic work. Do not add a scheduler, new queue, bypass, accept-anything fallback, or a parallel validator.
3. Find the **minimal safe GitHub-native** mechanism to execute **actual canonical Python** `inspect` against the exact sandbox Git history and original 14 introducing commits. The resulting per-AppID `ready`, `research_transport_invalid`, `research_not_submitted` diagnostics must be reproducible and provably tied to frozen marker and immutable inputs; do not declare `ready` based solely on 12 manual QA passes.
4. Continue beyond inspect: work out how separately authorized ChatGPT semantics can submit the exact typed `semantic={outcome,payload,supplemental_operations}` for each `ready` game, while GitHub executes the ORIGINAL `build_candidate` and `verify_candidate` Python against genuine repository history and enforces original create-only sandbox path, one-parent Git lineage, privacy, exact-source revisits and strict V2 Dossier validation. Submission interface must be demonstrably viable with the actual available connector capabilities, not merely described theoretically.
5. Address the original sandbox's immutable source: it was forked **before** any future implementation PR. A new workflow in `main` is not automatically executable in historical sandbox code. Propose and demonstrate an authorization-safe execution/installation route using authentic GitHub Actions checkout(s) and pinned scripts without rewriting frozen Research, Assembly buffer, marker, issuer proof or arbitrary branch history. If original authority cannot support it, STOP at CONTRACT/RECON rather than inventing a replacement marker.
6. Preserve original errors: two invalid packages must fail validation; four missing packages must stay missing; no Research rewrite/retry. Never use a semantic workaround to bypass canonical validation.
7. Test end-to-end using **only fixtures/mock semantics** in temporary or PR-only environments. Tests must cover deterministic readiness for 18 frozen rows, invalid/missing nonblocking behavior, immutable original provenance, allowed/forbidden typed candidate transport, reproducible Python checks and race/create-only rejection. Do not generate real game dossiers as part of implementation.
8. Only if all preceding authority/contract gates pass: create a narrow implementation branch and PR for director review (do not self-merge), with tested workflows/scripts/fixtures and a durable worker report. If a safe full solution cannot be demonstrated, report `BLOCKED_CONTRACT` or `BLOCKED_RUNTIME` precisely and do not present a partial workflow as unblocking the pilot.

## Nonnegotiable prohibitions

Do not run Research, semantic Assembly, or the one-shot Assembly issuer again. Do not create alternate markers/authorizations, retries or recovery. No production/canonical one-stage Dossier, Deep, Fast, ranking, profile or website writes. No Scheduled Task creation/change. Do not overwrite original 14 Research artifacts, assembly buffer or marker. Do not relax validators or treat sandbox submissions as accepted Dossiers.

## Required conclusion

Report actual confirmed root cause, exact GitHub actor/permissions, canonical code path for inspect → typed semantic handoff → build_candidate → GitHub verify, tests/CI with IDs, compatibility with frozen 18-game authority, PR URL/commit if created, blocking unknowns, and a **short** instruction to Director for next step. Do not autonomously restart the one-shot semantic pilot.
