# WORKER TASK — Taste Dossier Snapshot Count Reconciliation 01

## Task ID
`taste-dossier-snapshot-count-recon-01`

## Mode
`READ-ONLY / RECON`

## Goal
Reconcile the count invariant reported by the latest successful production `Taste Steam Review Dossier` run before the Director declares the dossier pipeline fully production-validated.

Observed user/runtime report:
- same daily snapshot;
- three accepted checkpoints in this run = 30 dossiers;
- `completed_required_count: 30`;
- `remaining_required_count: 554`;
- `full_backlog_complete: false`;
- next checkpoint size: 10;
- previous production validation had reported the current fixed daily snapshot as 591 required items.

If this is truly the same immutable prepared snapshot and `completed_required_count` is the snapshot total completed count, then `30 + 554 = 584`, not 591. Determine exactly why these numbers differ.

## Required background
Read first:
- `CHAT_PROTOCOL.md` and perform START gate;
- `CHAT_CONTEXT.md`;
- this task file completely;
- `reviews/worker_reports/taste-steam-review-dossier-persistence-bridge-01.md`;
- `PROJECT_DECISIONS.md -> TASTE-005` if needed to interpret the snapshot invariant.

## Questions to answer
1. Was the successful 30-dossier production run operating on the exact same `snapshot_id` as the earlier 591-required report?
2. What is the immutable prepared-required total for that snapshot?
3. What exactly does `completed_required_count` count: total completed within the snapshot, completed in the current invocation, or something else?
4. What exactly does `remaining_required_count` count?
5. Can any already-fresh/reused dossiers reduce the immutable prepared-required total after snapshot preparation? Under TASTE-005 this should not happen; verify the actual contract meaning rather than assume.
6. Was the earlier `591 required items` figure stale, derived from a different snapshot, or semantically different from prepared-required count?
7. Is there any production-state inconsistency, silent item loss, or incorrect reporting?

## Scope / boundaries
- READ-ONLY only.
- Do not modify production code, contracts, workflow, snapshot, queue, dossier store, or Scheduled Tasks.
- Do not press production `Run now`.
- Do not process additional dossier checkpoints.
- Do not inspect unrelated project areas.
- If a defect is found, report it precisely and recommend a separate bounded IMPLEMENT task; do not repair it in this RECON.

## Durable report
Write and merge to `main`:
`reviews/worker_reports/taste-dossier-snapshot-count-recon-01.md`

Report must include:
- exact snapshot identity/identities involved;
- exact count definitions;
- arithmetic reconciliation;
- whether the immutable snapshot invariant holds;
- whether any items were lost/skipped;
- whether the earlier 591 figure was wrong/stale/different-scope;
- exact refs supporting the conclusion;
- Status;
- Recommended next step.

## Allowed final statuses
- `reconciled_no_defect`
- `defect_found_needs_implement`
- `blocked`

## Expected next step
Director reads the durable report from `main`. If `reconciled_no_defect`, production validation may proceed from the same snapshot. If a defect is found, Director requests separate user authorization before any IMPLEMENT fix.
