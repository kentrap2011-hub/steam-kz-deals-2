# WORKER TASK — INGEST EXISTING 10-RESULT TASTE BATCH THROUGH PINNED LIFECYCLE

## Task ID
`taste-existing-batch-pinned-ingest-01`

## Mode
`AUTHORIZED PRODUCTION INGEST / EXISTING RESULTS ONLY`

## Expected report
`reviews/worker_reports/taste-existing-batch-pinned-ingest-01.md`

## User authorization
The user explicitly approved proceeding with production ingest of the already-produced 10-result Taste package after acceptance of the pinned-profile lifecycle fix.

## Goal
Canonically ingest the existing untouched package:
`data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`

Use the completed pinned-profile lifecycle architecture. Do not regenerate or edit the semantic results.

## Preconditions
Read once:
- `reviews/worker_reports/taste-pinned-profile-batch-lifecycle-fix-01.md`
- `reviews/worker_reports/taste-existing-batch-retry-01.md`

Verify before launch:
- pinned lifecycle fix final status is `complete_pinned_profile_lifecycle_fix_ready_for_acceptance`;
- existing package still exists unchanged;
- its durable grandfather proof still matches exact path/bytes/result-introduction commit/pre-semantic parent described in the accepted lifecycle report;
- no later successful ingest has already consumed this exact package;
- there is no conflicting active ingest/lock that makes launch unsafe.

If any precondition fails, stop fail-closed and self-diagnose in the same report.

## Mandatory report-first rule
The FIRST repository mutation after reading this task must be creation of the expected report with lifecycle `in_progress`, current UTC, target package, queue count before ingest, and next action. Commit immediately.

## Execution
Launch exactly one canonical production ingest attempt for this existing package through the normal repository ingest workflow/path.

Immediately persist the exact workflow run/job id before polling.

Follow `WORKER_ANTI_STALL_PROTOCOL.md` for bounded polling.

Do NOT:
- regenerate semantic results;
- edit/rewrite/reintroduce the package;
- create a replacement package;
- start semantic analysis for any new game;
- start the next 10-game batch;
- manually edit queue/cache/overlay/production state;
- modify Scheduled Task or cadence;
- change code/contracts/config in this task.

## Acceptance
PASS only if all are proven:
- canonical ingest succeeds;
- exactly the intended 10 existing results are accepted without semantic regeneration;
- grandfathered pinned authority is the exact authority used;
- inbox package is consumed according to canonical workflow;
- receipt/batch identity exists and is verified;
- canonical cache/overlay/index and rebuilt consumer state are committed atomically;
- queue count before and after is recorded and actual delta explained;
- current live-profile work remains pending where required by A→B rules and is not falsely treated as covered by old A results;
- any active work-unit transition after ingest is correct and points only to current remaining work;
- no unrelated semantic results are consumed;
- Scheduled Task remains untouched;
- no next 10 games are started.

Do not assume queue delta is exactly 10. Report exact verified counts and why.

## Failure behavior
If the single ingest attempt fails:
- do not launch another attempt;
- do not regenerate/edit results;
- do not start next games;
- perform bounded self-diagnosis in the SAME report under `WORKER_REPORT_DURABILITY_PROTOCOL.md`;
- identify the first real error/root cause as far as evidence permits;
- state exactly what changed and what did not;
- state whether the existing 10 results remain reusable;
- recommend the smallest next action.

## Finish
Final status must be one of:
- `complete_existing_10_pinned_ingest_accepted`
- `failed_closed_root_cause_proven`
- `failed_closed_root_cause_unknown`
- `waiting_external`
- `blocked`

If successful, explicitly report:
- exact workflow run/job id;
- exact ingest/acceptance commit;
- receipt/batch id;
- exact accepted result count = 10;
- queue count before/after and delta;
- whether all 10 original results are canonically durable;
- confirmation no semantic regeneration occurred;
- confirmation no next batch was started;
- whether throughput-drain experiment may now resume from the next canonical work-unit.

Then STOP and return control to Director.
