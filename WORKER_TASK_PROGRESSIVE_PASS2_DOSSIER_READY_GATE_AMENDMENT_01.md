# WORKER TASK — Progressive PASS 2 Dossier-Ready Gate Amendment 01

## Identity
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Mode: `CANONICAL RULE AMENDMENT / NO PASS2 IMPLEMENTATION`
- Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

## User-authoritative correction
PASS 2 must not evaluate an `analysis_incomplete` item before Taste Steam Review Dossier has produced current, exact-compatible accepted dossier evidence for that same game/work identity.

The intended pipeline is:
`PASS 1 incomplete -> wait for accepted compatible Dossier -> PASS 2 becomes eligible -> one bounded recovery attempt`.

No accepted compatible Dossier means:
- the item is NOT eligible for PASS 2;
- no PASS 2 attempt is consumed;
- the item remains visible as `analysis_incomplete` / PASS2-pending;
- GitHub waits for Dossier acceptance rather than letting PASS 2 improvise a deep evaluation from unrelated/light evidence.

When a current exact-compatible Dossier becomes accepted, GitHub may add that incomplete item to the PASS 2 recovery queue.

A stale, mismatched, wrong-app, wrong-work, or incompatible dossier must not unlock PASS 2.

## Goal
Amend the canonical Progressive Personalized Deals architecture/rules so the Dossier-ready prerequisite above is explicit and machine-designable before PASS 2 implementation.

Also reconcile the prior rule that PASS 2 starts only after full PASS 1 coverage with the newer Director/user direction that PASS 1 and PASS 2 operate independently in parallel:
- PASS 1 continues processing not-yet-attempted items;
- PASS 2 considers only already-incomplete items;
- the Dossier-ready gate must be satisfied before a specific item becomes PASS 2 eligible;
- neither pass waits for or blocks the other;
- one automatic PASS 2 recovery attempt per eligible semantic generation/work identity remains bounded;
- no infinite retry loop exists.

## Required work
1. Perform START gate from `CHAT_PROTOCOL.md`.
2. Read the current progressive architecture/report/contracts and current Dossier ownership/persistence contracts.
3. Identify the smallest canonical rule surfaces that must change.
4. Persist the user-authoritative rule in the appropriate canonical contract/rules/decision documentation.
5. Define exact PASS 2 eligibility in GitHub-owned terms, including exact-compatible accepted Dossier binding and attempt-budget behavior.
6. Define how Dossier acceptance makes a pending incomplete item eligible without requiring interactive intervention.
7. Define independent parallel ownership so PASS 1 and PASS 2 do not wait for or block each other.
8. Do NOT implement or activate PASS 2 runtime, scheduler, worker, queue processor, or production execution in this task.
9. Do NOT change PASS 1 worker behavior or Dossier evidence semantics except where documentation references need reconciliation.
10. Do NOT run Scheduled Tasks.

## Acceptance
- PASS2-GATE-01: no accepted compatible Dossier => no PASS 2 eligibility.
- PASS2-GATE-02: waiting for Dossier consumes zero PASS 2 attempts.
- PASS2-GATE-03: accepted exact-compatible Dossier unlocks only the matching incomplete item/work identity.
- PASS2-GATE-04: stale/mismatched Dossier cannot unlock recovery.
- PASS2-GATE-05: PASS 1 and PASS 2 may operate independently in parallel; neither waits for or blocks the other.
- PASS2-GATE-06: no PASS 2 infinite retry; bounded automatic attempt budget remains explicit.
- PASS2-GATE-07: GitHub owns eligibility/order/state/attempt accounting.
- PASS2-GATE-08: no runtime implementation or production execution occurred.
- PASS2-GATE-09: prior canonical statements saying PASS 2 only starts after full PASS 1 coverage are reconciled/superseded cleanly, not left contradictory.

## Durable report
Create and commit:
`reviews/worker_reports/progressive-pass2-dossier-ready-gate-amendment-01.md`

Report must include:
- exact canonical files changed;
- old vs new rule;
- exact eligibility predicate;
- PASS2-GATE-01..09;
- unresolved implementation details, if any;
- final status;
- exactly one recommended next step.

Allowed statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `needs_user_decision`

Before final response, reread the exact durable report from `main`.
