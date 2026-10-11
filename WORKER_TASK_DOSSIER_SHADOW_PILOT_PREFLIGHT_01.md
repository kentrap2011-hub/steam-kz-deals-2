# WORKER TASK — Dossier real-evidence shadow pilot preflight, inactive

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`
Physical worker: **НОВЫЙ ЧАТ — ЧАТ 1**
Task ID: `dossier-shadow-pilot-preflight-01`
**MODE: OFFLINE / READ-ONLY REAL BASELINE CHECKS / NO SEMANTIC EXECUTION / PR ONLY**

## Goal
After merged PRs #193 (year-fix proof metadata decoupled) and #194 (prospective shadow trial proposal), remove the **next concrete technical readiness blocker** for a small, separately approved Research→Assembly vs accepted one-stage Dossier real-evidence shadow comparison. Prepare a safe, reproducible **trial preflight and immutable input/legacy writer-receipt verification** that lets Director decide whether even a proposed 6 original-group/18-game calibration pilot is eligible. **Do not initiate, authorize, freeze or select a real pilot.** Do not mistake the proposed 30 groups/90 games or 6 groups/18-game pilot for user-approved quotas. This is a technical preflight, not another conceptual re-plan.

## START and precise sources
Fully read current `CHAT_PROTOCOL.md` in `main` and perform START gate, then `CHAT_CONTEXT.md`, this task, targeted `PROJECT_ROUTES.md` Dossier section, PR #194 prospective report `reviews/worker_reports/dossier-shadow-trial-prospective-plan-01.md`, PR #191 accepted protocol `reviews/dossier_two_stage_shadow_trial_protocol.md`, actual `config/dossier_two_stage_final_acceptance_bridge_contract.json` (`cross_pr_research_original_year_fix_verified=true`, all live gates false), existing accepted one-stage Dossier writer/manifest/group receipt contracts and shadow comparison harness. Only `kentrap2011-hub/steam-kz-deals-2` and current `main` are authoritative.

## Required implementation/evidence
- Add a deterministic **fail-closed, offline preflight** consuming only caller-supplied explicit frozen Git refs/bindings: original exact 3-game group identity and membership; original game/year/appid; accepted **one-stage historical canonical writer transaction/receipt + unchanged exact cache file/blob SHA**; current Research/Assembly proposal identity; safe provenance and privacy constraints. A schema-valid legacy JSON or bare on-disk cache file is **not** historical writer acceptance. Reject absent/mismatched receipt, wrong group/appid/work/year, tampered blob, wrong Git parent, unsupported marker and changed target Git snapshot. No accepted baseline => not eligible, no bypass.
- Exercise authoritative **existing** writer/receipt/strict V2 and shadow harness APIs if usable; do not create a second canonical truth/selector, validator, cache, retry or receipt. If existing receipts cannot prove historical acceptance for candidate group, report exact evidence gap with the smallest future fix, never claim eligible.
- Add disposable-Git synthetic fixture regressions for genuine positive and adversarial cases, no public source fetching; a read-only **diagnostic** of current repository artifact shapes is permitted but must not materialize or publish real Research/Assembly semantic results or assign real games. Avoid copying user/profile or review content into reports.
- Produce a **pilot launch gate checklist** with exact inputs, sample/reviewer/threshold approvals still needed, independent human verification and no semantic execution until user separately authorizes frozen scope. Preserve fully async independent semantic worker behavior; no per-item GitHub accepted-receipt waiting, no new fixed quota or scheduled action.
- Separate distinction between `preflight_ready` (technical proofs) and `quality_verified` (impossible here). No real result or stage may be marked Dossier/Deep ready. Do not set any `active`/`authorized_*` flags.
- Keep changes additive and isolated from Chat 2's site files. CI PR-only and nonmutating. If this turns out to require a production writer or shared contract rewrite, report the blocker and do not implement unapproved scope.

## Deliverables
Focused PR, synthetic tests + PR-only workflow if needed, worker report `reviews/worker_reports/dossier-shadow-pilot-preflight-01.md` and exact evidence checklist. Prefer new `scripts/dossier_shadow_pilot_preflight.py`, `scripts/test_dossier_shadow_pilot_preflight.py`, `.github/workflows/validate-dossier-shadow-pilot-preflight.yml`. Do **not** merge own PR.

**Forbidden:** actual semantic Research/Assembly, real trial selection/freezing or running, production/cache/Deep changes, Scheduled Tasks or automation changes, GitHub canonical writes, new control plane or scheduler, Fast removal, site fixes, other repo, secrets, `manual-shell-write.yml`.
