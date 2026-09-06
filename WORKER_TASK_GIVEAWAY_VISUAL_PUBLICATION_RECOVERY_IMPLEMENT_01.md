# WORKER TASK — Giveaway Visual Publication Recovery Implement 01

## Task ID
`giveaway-visual-publication-recovery-implement-01`

## Mode
`IMPLEMENT / ACCEPTANCE`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`

## Direct predecessor
Read first:
`reviews/worker_reports/giveaway-empty-feed-recurrence-recon-01.md`

The predecessor proved:
- current canonical giveaway snapshot is healthy, complete, fresh and contains a valid active Epic giveaway;
- site-facing `data/production/visual/current.json` is still bound to an older expired giveaway snapshot;
- latest inspected canonical `Build daily visual payload` run `34037436064` failed/degraded at `Build and refresh canonical visual payload once`;
- no fresh visual was persisted;
- this is NOT the old browser cache/identity incident and NOT an upstream giveaway-source outage;
- fail-closed behavior is correct and must remain.

## Goal
Repair/recover only the existing canonical daily visual build/publication path so the fresh canonical giveaway snapshot is incorporated into the site-facing visual artifact and can be published through the normal production route.

Do not create a separate giveaway-only writer/scheduler as a workaround.

## Required investigation + implementation
1. Start from current `main` and the exact predecessor report.
2. Inspect the failed existing workflow/run boundary only as deeply as needed to determine why `Build and refresh canonical visual payload once` produced no fresh visual.
3. Identify the smallest real defect or blocking interaction in the existing canonical visual pipeline.
4. Implement the minimum correction/recovery needed for the **existing** visual build/publication path to advance.

### Important interaction rule
If the existing daily visual build is being prevented from publishing a fresh giveaway handoff because some unrelated subsystem (for example unresolved Taste semantics or another independent section) is fail-closed, do NOT simply disable that subsystem's safety gate.

Instead determine whether the canonical visual architecture already supports, or can safely support with a minimal change, refreshing the giveaway handoff while preserving the unrelated subsystem's own fail-closed/degraded state.

Any such change must:
- keep a single canonical `data/production/visual/current.json` writer;
- preserve explicit degraded/unavailable state for unrelated incomplete sections;
- never fabricate Taste/commercial/other freshness;
- never promote stale unrelated data to fresh merely to publish giveaways.

If safe section-level refresh is impossible without a broader architecture change, stop `blocked` and report the exact architectural gate rather than weakening safety.

## Hard invariants
- Existing canonical giveaway snapshot remains `data/production/giveaways/v1/current.json`.
- Existing canonical site-facing visual remains `data/production/visual/current.json`.
- Existing `Build daily visual payload` path remains the canonical visual writer/publication route.
- No second scheduler.
- No second giveaway writer.
- No manual patch of giveaway cache, handoff or `visual/current.json`.
- No weakening of freshness or completeness checks.
- No fake success receipt.
- No UI-only workaround.
- Do not change giveaway eligibility/business rules unless the proven failure directly requires a narrowly scoped bug fix; current canonical giveaway snapshot is already healthy.
- Do not touch Taste recommendation semantics/ranking logic.

## Validation / live acceptance
After the fix/recovery, use the normal production route and prove all of the following:

1. Existing canonical visual workflow completes the relevant build/publication path successfully.
2. `data/production/giveaways/v1/current.json` is still complete/trusted at publication time.
3. Newly published `data/production/visual/current.json.production_contract.source_giveaway_snapshot_blob_sha` exactly matches the then-current Git blob SHA of `data/production/giveaways/v1/current.json`.
4. Embedded giveaway handoff is freshly derived and non-expired under the existing fail-closed contract.
5. A fresh visual freshness receipt reports an actually produced/persisted visual, not `degraded/no_fresh_build` with `produced_visual = null`.
6. The valid active giveaway(s) from the canonical snapshot are represented in the site-facing visual artifact according to existing policy.
7. No second visual writer/scheduler was introduced.
8. No manual production artifact editing was used.

If the normal site deployment is a distinct canonical workflow after the visual artifact update, run/observe that existing route as needed and include exact deploy evidence. Do not invent a new deploy mechanism.

## User verification gate
Status `complete_ready_for_user_verification` only if the production artifact/deploy is genuinely updated and the user can meaningfully re-check the real mobile site.

Do NOT claim final user-visible closure yourself. Director will ask the user for Android verification after consuming the report.

## Allowed final status — exactly one
- `complete_ready_for_user_verification`
- `blocked`
- `needs_followup_fix`

## Required report
Save exactly:
`reviews/worker_reports/giveaway-visual-publication-recovery-implement-01.md`

Report must contain:
- final status;
- exact proven failure inside the previous visual build boundary;
- exact implementation/recovery made;
- commits;
- focused regression/validation results;
- exact canonical workflow run(s);
- current canonical giveaway blob SHA at acceptance time;
- resulting `visual/current.json` source giveaway blob SHA;
- fresh handoff timestamps/state;
- freshness receipt result;
- deploy evidence if distinct;
- proof no second writer/scheduler/manual patch/fail-open change;
- explicit `ready_for_user_mobile_verification: true|false`;
- any remaining blocker.

Do not start another major task.
