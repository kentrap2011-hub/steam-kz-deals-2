# WORKER TASK — Progressive PASS 2 Dossier Integration + Activation Prep 01

Status: PAUSED_SUPERSEDED_PENDING_ARCHITECTURE
Director note: user changed the target product semantics on 2026-09-22. PASS 2 is no longer merely recovery for PASS 1 incomplete items; deep analysis is intended to eventually cover every current eligible game. Do not continue implementation/activation under the old eligibility model. Preserve any already-landed safe integration work, but stop before further writes and report current landed state if asked.

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: progressive-pass2-dossier-integration-activation-prep-01
Mode: IMPLEMENT / VALIDATE
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.
Then open this task from main and use the current canonical contracts/routes/reports as source of truth.

Required canonical inputs:
- `config/progressive_pass2_contract.json`
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- `reviews/worker_reports/progressive-pass2-phase-c-core-implement-01.md`
- `reviews/worker_reports/taste-dossier-nonblocking-group-progress-implement-01.md`
- `reviews/worker_reports/taste-dossier-group-identity-items-mismatch-fix-01.md`

## Confirmed starting state

- PASS 2 core is implemented but inactive.
- PASS 2 eligibility requires current exact PASS 1 `analysis_incomplete` plus a current exact-compatible canonically accepted Dossier.
- Dossier non-blocking per-group progress is live-proven.
- Current Dossier candidate serialization fix is live-proven.
- Current snapshot has at least two canonically accepted groups (g000003 and g000004), six accepted dossiers, and forward progress continues.
- g000001/g000002 remain failed/recovery-owned and are not accepted evidence.
- PASS 1 continues independently in production.
- No production PASS 2 Scheduled Task/run has been accepted yet.

## Goal

Complete the missing GitHub-owned integration so PASS 2 eligibility is recomputed automatically whenever canonical inputs that can change current eligibility change, while preserving all existing ownership, one-attempt, exact-binding, and non-blocking semantics.

Prepare the repository and an exact operator activation plan for production PASS 2, but DO NOT activate semantic execution or run PASS 2 in this task.

## Architecture requirement

Do not implement a narrow one-sided hook if it would leave automatic eligibility stale.

First prove the full set of GitHub-owned input-change events that can make an item newly eligible or no longer eligible. At minimum evaluate:

1. canonical Dossier acceptance/persistence;
2. PASS 1 canonical state transition to/from current `analysis_incomplete`;
3. daily/current-input changes that can alter Dossier freshness/compatibility or current Progressive semantic generation/work identity.

Wire the existing Progressive-owned recomputation entrypoint at the smallest canonical GitHub control-plane boundaries needed so eligibility cannot depend on a later unrelated event.

Do not create a new queue owner, daemon, scheduler, retry loop, or second state authority.

## Required implementation

- Reuse `scripts/progressive_pass2.py::recompute_eligibility` / `scripts/build_progressive_pass2_work.py`; do not duplicate PASS 2 eligibility logic.
- After canonical Dossier persistence, GitHub must recompute PASS 2 work from current canonical truth.
- If PASS 1 state can change eligibility without a Dossier write, wire the current PASS 1 GitHub-owned persistence path to recompute as well.
- If daily/binding/freshness/current-generation changes can invalidate or create eligibility, wire the existing canonical preparation/rebuild path as needed.
- Recompute must be idempotent and must consume zero PASS 2 attempts.
- Recompute must never treat buffered/unaccepted Dossier candidates as accepted truth.
- Failed/recovery-owned Dossier groups remain non-authoritative for PASS 2.
- Work must remain exact-bound to current semantic generation, work_id, appid, dossier content SHA, compatibility binding, and authorization_id.
- One invalid/stale PASS 2 item must not block siblings.
- PASS 1 must remain independent and unchanged semantically.
- Dossier evidence/identity/freshness/validation semantics must remain unchanged.
- Preserve current site provenance behavior from the PASS 2 core.

## Activation preparation

Prepare, but do not execute, the exact production activation interface.

The durable report must state the exact operator configuration needed for one future Scheduled Task, including:
- exact task title;
- schedule/cadence and timezone rule;
- exact compact loader/prompt text the user should install;
- whether the task should initially be enabled or disabled;
- the exact order of repository activation vs Scheduled Task enablement vs first `Run now`;
- duplicate-task guard;
- what GitHub state must be checked after the first run.

Do not create/edit/enable/disable/run any Scheduled Task from this worker.

## Activation guard for this task

Keep:
- `config/progressive_pass2_contract.json#active = false`;
- `progressive_personalization_contract.phase_b_execution.pass2_active = false`;
- execution ownership PASS 2 active flag false;
- production PASS 2 semantic execution unauthorized.

No real PASS 2 result artifact, terminal execution receipt, or attempt consumption is allowed.

A current work manifest may be recomputed from real canonical state only as a GitHub-owned projection. This consumes zero attempts and is allowed.

## Validation

Prove at minimum:

- P2INT-01: a canonically accepted exact-compatible Dossier can make a matching current PASS 1 incomplete item eligible without manual queue construction.
- P2INT-02: buffered/unaccepted/failed Dossier artifacts cannot unlock PASS 2.
- P2INT-03: PASS 1 becoming current `analysis_incomplete` with an already accepted compatible Dossier triggers/reaches recomputation without waiting for a later unrelated Dossier event.
- P2INT-04: leaving current incomplete state or changing current generation/work identity removes/rebinds stale eligibility.
- P2INT-05: expiry/compatibility change cannot leave stale authorized PASS 2 work treated as current.
- P2INT-06: recomputation consumes zero attempts and is idempotent.
- P2INT-07: one invalid/stale item does not block valid siblings.
- P2INT-08: PASS 1 and Dossier semantics/attempt histories are unchanged.
- P2INT-09: g000001/g000002 remain failed/recovery-owned; g000003/g000004 accepted truth remains intact.
- P2INT-10: PASS 2 remains inactive and no production PASS 2 execution occurs.
- P2INT-11: activation plan is exact enough for the user to configure one Scheduled Task without inventing runtime details.
- P2INT-12: relevant focused and canonical regressions pass.
- P2INT-13: durable report committed and reread from main before completion.

## Scope exclusions

Do not:
- process the PASS 2 backlog;
- create or run the PASS 2 Scheduled Task;
- flip PASS 2 active to true;
- weaken exact Dossier or PASS 2 validation;
- alter Dossier recovery semantics;
- reopen failed Dossier groups;
- change PASS 1 semantic policy;
- change site ranking rules;
- create another recurring producer.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-pass2-dossier-integration-activation-prep-01.md`

Keep it compact and include:
- architecture preflight;
- exact recomputation trigger graph;
- exact files changed;
- validation P2INT-01..13;
- current projected PASS 2 eligible count after recomputation (projection only, zero attempts);
- proof PASS 2 is still inactive;
- exact future Scheduled Task operator configuration and activation order;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_ready_for_activation
- complete_ready_for_director_acceptance
- needs_fix
- blocked_external_operator_action
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
