# WORKER TASK — Taste Canary Atomic Ingest Failure Recon 01

## Task ID
`taste-canary-atomic-ingest-failure-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`VERY_HIGH_USER_PRIORITY`

## Expected report
`reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`

## Direct predecessor
Read first:
`reviews/worker_reports/taste-existing-singleton-canary-execute-01.md`

Accepted predecessor outcome:
- exact existing producer `6a9d6fdddc00819193ed670d782045c4` was reused;
- exactly one durable semantic submission exists: `App_10150` / `Prototype`;
- producer fence and validation gates passed;
- canonical ingest workflow run `34047485340` failed at `Validate, ingest and rebuild taste consumers atomically`;
- no fresh receipt or accepted queue delta exists;
- no second row was accepted;
- exact Scheduled Task is disabled/fail-closed;
- do NOT create another task/producer/generation.

## Goal
Determine the exact root cause of the failed atomic canonical Taste ingest for the one existing canary submission, and define one minimal bounded IMPLEMENT recovery action.

Do not run another semantic game in this recon.

## Required investigation
1. Read current `main`.
2. Read:
   - `CHAT_PROTOCOL.md`
   - `CHAT_CONTEXT.md`
   - `DIRECTOR_PROTOCOL.md`
   - predecessor report above;
   - current canonical Taste inbox/ingest scripts/contracts.
3. Inspect GitHub Actions run `34047485340` and its failing job/step deeply enough to establish the exact non-secret failure reason inside `Validate, ingest and rebuild taste consumers atomically`.
4. Determine whether the failure is caused by:
   - the canary row no longer belonging to the current canonical queue/scope;
   - stale binding/fingerprint/context;
   - invalid semantic payload fields;
   - transactional consumer rebuild issue;
   - unrelated current repository drift;
   - another exact cause.
5. Determine whether the existing `Prototype` inbox submission can safely be retried/accepted after a minimal code/data-path fix, or whether it must remain rejected and a future new canary row would be required after Director approval.
6. Verify that no second semantic row was accepted and that the existing Scheduled Task remains fail-closed/disabled. Do not mutate scheduler state unless needed only to force-disable the same existing task for safety.
7. Define exactly one bounded next IMPLEMENT action. Do not implement it here.

## Hard invariants
- READ-ONLY / RECON only.
- Do not create/clone a Scheduled Task.
- Do not create producer generation 2.
- Do not run another semantic inference.
- Do not manually edit/delete/fabricate the existing inbox submission.
- Do not manually patch receipts, queue, caches or consumer outputs.
- Do not weaken V5, producer fence, current-scope/binding validation, transactional semantics, or fail-closed behavior.
- No paid OpenAI API.
- No Copilot fallback.
- No throughput widening.
- No unrelated Taste/ranking/UI/giveaway work.

## Required report
Save exactly:
`reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`

Report must contain:
- final status exactly one of:
  - `complete`
  - `blocked`
- exact failing run/job/step;
- exact root cause or narrowest proven boundary if some evidence is unavailable;
- whether `App_10150 / Prototype` was current/eligible at submission and at ingest time;
- whether the existing inbox submission itself is semantically valid/current or must remain rejected;
- whether any repository drift contributed;
- confirmation no second row was accepted;
- confirmation exact task `6a9d6fdddc00819193ed670d782045c4` remains fail-closed/disabled;
- exactly one minimal bounded next IMPLEMENT action;
- whether a future new semantic canary would be necessary after that fix, or the existing submission can be safely reprocessed.

Do not implement the fix and do not start another task.
