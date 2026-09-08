# taste-refreshed-canary-rerun-01

## Status
`in_progress`

## Task
Refresh the exact Chernobylite Complete Edition (`App_1016800`) canary binding against the current canonical Taste profile, use the same existing generation-2 `Taste Semantic Producer` Scheduled Task, run only that one canary, restore its permanent DAILY 01:00 Europe/Samara schedule, and verify canonical acceptance without weakening safety or widening production.

## Durable checkpoint
Report created in `main` before any Scheduled Task mutation or active Taste inbox mutation.

## Known starting state
- Target is only `Chernobylite Complete Edition`, AppID `1016800`.
- Existing active Scheduled Task required by contract: `Taste Semantic Producer`, task id `6aa032f37e688191a5c9a1a83f91c5d9`, producer generation `2`.
- Existing Chernobylite generation-2 inbox result is known stale from the prior task because its profile binding no longer matched the then-current canonical profile.
- Historical generation-1 blocker was already preserved outside the active inbox in the preceding repair.

## Current tuple
Pending exact current canonical re-read/freeze.

## Archive
Pending preservation of the stale prior generation-2 Chernobylite result under `data/ai_archive/taste/` before active removal.

## Scheduled Task
Pending verification of the existing task state, canary-only prompt refresh, safe same-task trigger, and restoration to DAILY 01:00 Europe/Samara.

## Canonical acceptance
Pending canonical ingest workflow, receipt/cache, active-inbox consumption, and queue-state proof.

## Containment
- No new Scheduled Task created.
- No other game selected.
- No mass/backlog semantic analysis started.
- No paid OpenAI API, Copilot, or external paid service used.
- No safety/binding/semantic guard weakened.

## System Audit readiness
Pending successful canary acceptance. System Audit will not be started by this task.
