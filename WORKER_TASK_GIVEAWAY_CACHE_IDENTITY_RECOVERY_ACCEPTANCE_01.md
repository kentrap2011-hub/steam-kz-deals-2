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

## New user evidence

After the landed commit was visible on `main`, the user immediately checked the real mobile site again and reported:

**the free-giveaway button / giveaway view still does not work.**

Treat this as decisive evidence that the user-visible incident is still open.

This check does NOT by itself prove that commit `6282619c...` is logically wrong, because it is still necessary to determine whether the exact commit was successfully deployed to the production Pages site before the user's check.

Acceptance must therefore explicitly distinguish:
1. fix landed but had not yet reached production at user-check time;
2. fix was deployed and production still failed, meaning the landed fix is insufficient or another downstream defect remains.

Do not mark the incident accepted merely because unit tests or a repository commit are green.

## Goal

Recover and accept/reject the already-landed cache-identity fix using current GitHub truth plus the failed real-device verification above.

Determine whether commit `6282619c65c134459a4e85c80b9355fe3174e8ae` correctly fixes the stale-LKG collision for giveaway-only refreshes, has focused regression coverage, and has reached the canonical production deploy path.

If it was already deployed before the failed user check, identify whether one exact remaining defect is proven.

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
6. Did the canonical Pages deploy path run for commit `6282619c...`, and did it complete successfully?
7. Establish deploy timing relative to the user's failed real-site check as far as repository/Actions evidence permits.
8. Is current deployed frontend expected to contain the fix?
9. Given the failed user verification, is the most accurate classification:
   - `not_deployed_at_user_check`,
   - `deployed_but_fix_insufficient`,
   - `cannot_determine`?
10. Is there any concrete defect in the landed implementation that requires a follow-up IMPLEMENT before another user retest?

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

The user's latest real-device verification has already failed.

Therefore technical `complete` is allowed only if evidence proves the fix was **not yet deployed at the time of that check** and is now deployed enough to justify one new retest.

If evidence proves it was already deployed before that failed check, status must not be `complete` unless there is a separate, newer deployed correction that the user has not yet tested.

## Done when

Save:
`reviews/worker_reports/giveaway-cache-identity-recovery-acceptance-01.md`

Include:
1. Task
2. New user evidence
3. Landed commit recovery
4. Implementation assessment
5. Regression evidence
6. Deploy evidence and timing
7. Technical acceptance decision
8. User verification state
9. Unresolved
10. Status
11. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`

If `complete`, explicitly explain why the user's failed check happened before the accepted deploy and why a new retest is now meaningful.
