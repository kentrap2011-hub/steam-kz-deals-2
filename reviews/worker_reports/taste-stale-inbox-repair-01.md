# taste-stale-inbox-repair-01

## Task
Confirm and minimally repair the stale Taste inbox blocker, preserve the historical generation-1 artifact, and re-ingest the already-produced Chernobylite generation-2 result through the canonical ingest path without semantic rerun, another game, another Scheduled Task, or weakened producer validation.

## Status
`in_progress`

## Verified facts
- Task contract identifies `data/ai_inbox/taste/canary-app-1016800-gen2.json` as the existing generation-2 Chernobylite result.
- Task contract identifies `data/ai_inbox/taste/canary-App_10150-producer-g1.json` as the suspected historical generation-1 blocker.

## Changes
- Durable report created before implementation changes.

## Validation
- Pending required reading, root-cause confirmation, lifecycle repair, and canonical re-ingest verification.

## Unresolved
- Exact failure mechanism not yet independently confirmed from current code/contracts.
- Historical artifact lifecycle and exact archive destination not yet confirmed.
- Chernobylite acceptance/receipt/queue advancement not yet verified.

## Recommended next step
Complete the bounded required reading and architecture preflight, then prove the blocker before any implementation mutation.

## Efficiency / reusable lesson
`none`
