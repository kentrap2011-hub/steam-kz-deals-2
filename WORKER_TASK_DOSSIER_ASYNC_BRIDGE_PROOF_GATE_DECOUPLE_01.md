# WORKER TASK — decouple inactive Dossier bridge proof flag from offline execution gate 01

Repository: `kentrap2011-hub/steam-kz-deals-2`; base/source of truth: `main`.
Physical developer: **НОВЫЙ ЧАТ — ЧАТ 1**.
Task ID: `dossier-async-bridge-proof-flag-fix-01`.
Authorization: **inactive offline-only implementation + isolated CI + worker PR; NO production or real semantics.**

## Problem / accepted evidence

PR #190 (merged into `main`) verified the full Research→Assembly→GitHub strict original three-game pipeline with the corrected original-year check from PR #187 and the inactive bridge from PR #188. Its report `reviews/worker_reports/dossier-async-postmerge-joint-integration-qa-01.md` found one guard coupling: `scripts/dossier_two_stage_final_acceptance.py::offline_gate` demands `cross_pr_research_original_year_fix_verified is False` even when all true activation gates are false. Thus setting the *proof metadata* to `true` disables the safe disposable-fixture offline test path. Proof metadata must never be an activation switch.

## START
Read current `CHAT_PROTOCOL.md` fully from `main` and execute START gate, then `CHAT_CONTEXT.md`, this task, reports of PR #187, #188 and #190 and targeted `PROJECT_ROUTES.md` Dossier route. Inspect only actual `config/dossier_two_stage_final_acceptance_bridge_contract.json`, relevant interface/staging/async buffer and ownership contracts, offline bridge gate and exact PR #190 test file. Stay only in `kentrap2011-hub/steam-kz-deals-2`; correct any wrong tool-selected repo before writes.

## Required change
- Narrowly separate **cross-PR year-fix proof metadata** from **all live execution/authority flags**. Offline fixture must accept `cross_pr_research_original_year_fix_verified` as a truthful `true` or `false` boolean, while still requiring the actual `active=false`, `authorized_for_canonical_ingest=false`, `executable_in_production=false` and other existing inactive/fixture-only guards. Any malformed metadata, missing fixture marker or attempted real repo execution must remain fail-closed.
- Verify corrected Research identity/source original-work-year mismatch is a normal **passing rejection** through P1/P2/eventual bridge/strict group; legitimate later Steam storefront/port dates remain accepted. **Only after** direct joint tests pass, change the proof flag to `true` if the canonical bridge contract defines this as supported evidence; the flag itself must not allow live execution or canonical writing.
- Prove in offline tests that true/false proof values cannot activate anything; a live/unsafe gate or authorizing boolean is always rejected by the offline entry point. Test code must not create or accept a new production consumer, scheduled workflow, retry/receipt or writer.
- Rerun actual PR #190 joint regressions, P1/P2, PR #188 final bridge, Research/year, async and one-stage / ownership guards. Use disposable isolated Git. No test writes to actual `data/` or real Dossier.
- If a narrowly safe decoupling is not possible, leave proof flag false and report precise blocker. Do not soften validation to make tests pass.

## Parallel boundaries
ЧАТ 2 separately owns shadow trial **planning** and site Deep count discrepancy **diagnostics** in `WORKER_TASK_DOSSIER_SHADOW_TRIAL_PLAN_AND_SITE_DEEP_COUNT_QA_01.md`. Do not edit Chat 2 task, report, planning, quality harness, site UI/metric files or Director plan. Prefer smallest bridge gate/contract/test changes; if shared writer/live workflow needed, stop and report.

## Deliverables / safeguards
Dedicated branch and PR against current `main` (**do not merge own PR**), PR-only CI, worker report `reviews/worker_reports/dossier-async-bridge-proof-gate-decouple-01.md` with exact verified contract states and tests. No real semantic analysis, production activation, production data, Scheduled Tasks/automations, Deep/Fast/translation/UI/Steam changes, other repo, secrets, `manual-shell-write.yml`.
