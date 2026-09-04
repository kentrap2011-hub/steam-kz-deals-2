# WORKER TASK — GIVEAWAY CACHE IDENTITY RECOVERY ACCEPTANCE 01

Task ID: `giveaway-cache-identity-recovery-acceptance-01`
Mode: `ACCEPTANCE / RECOVERY`
Report: `reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`

## Context

Previous Chat 2 reached its chat limit before saving the required durable report for `giveaway-cache-identity-fix-01`.

However, current `main` already contains commit:
`6282619c65c134459a4e85c80b9355fe3174e8ae` — `Fix giveaway cache payload identity`.

Do NOT redo the implementation from scratch.

Prior proven cause:
`reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`

## Goal

Recover and accept/reject the already-landed cache-identity fix using current GitHub truth.

Determine whether commit `6282619c65c134459a4e85c80b9355fe3174e8ae` correctly fixes the stale-LKG collision for giveaway-only refreshes, has focused regression coverage, and has reached the canonical production deploy path.

## Read first

1. Current `main`.
2. `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`.
3. `reviews/worker_reports/giveaway-live-site-mismatch-recon-01.md`.
4. `WORKER_TASK_GIVEAWAY_CACHE_IDENTITY_FIX_01.md`.
5. Exact commit `6282619c65c134459a4e85c80b9355fe3174e8ae` and its changed files.
6. Only the focused feed-bootstrap regression tests and exact deploy workflow/run evidence needed for acceptance.

No broad history archaeology.

## Required checks

1. What exactly changed in `payloadIdentity()`?
2. Does the new identity distinguish the proven case: same paid/top-level visual generation state but changed giveaway publication state/provenance?
3. Does it preserve true `refresh-identical` behavior when the relevant published payload identity is actually unchanged?
4. Is there focused regression coverage for stale cached giveaway payload -> fresh giveaway-only payload -> `applyBackgroundPayload()`?
5. Did those focused tests pass on the landed code?
6. Did the canonical Pages deploy path run for the landed change, and did it complete successfully?
7. Is current deployed frontend expected to contain the fix?
8. Is there any concrete defect in the landed implementation that requires a follow-up IMPLEMENT before asking the user to retest?

## Critical boundaries

READ/ACCEPT only. Do NOT change code in this task.

Do NOT:
- reopen Epic parser/canonical giveaway work;
- redesign cache ownership;
- change UI/filter/navigation;
- touch ITAD/IGDB, Taste/ranking, semantic runtime;
- broaden to unrelated deploy failures.

If the landed implementation is incomplete or incorrect, report one exact bounded follow-up fix; do not implement it.

## User-visible acceptance

Even if technical acceptance is successful, the giveaway incident is not finally closed until the user verifies the real mobile site again.

## Done when

Save:
`reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`

Include:
1. Task
2. Landed commit recovery
3. Implementation assessment
4. Regression evidence
5. Deploy evidence
6. Technical acceptance decision
7. User verification required
8. Unresolved
9. Status
10. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`

`complete` means the landed fix is technically accepted and deployed enough to request a new real-site mobile check from the user.
