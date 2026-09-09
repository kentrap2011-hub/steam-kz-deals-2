# Taste current-main canary path design 01

## Task
Design the smallest safe path to prepare and test exactly one Taste game (Chernobylite, AppID 1016800) from current `main`, without rerunning a historical workflow and without implementing or executing the canary in this task.

## Lifecycle
- Last checkpoint UTC: 2026-09-09T13:52:00Z
- State: `in_progress`
- Next concrete action: read the remaining required project truth and trace the current production/pre-AI scripts/workflows that could support a single-AppID fresh-current-main preparation path.

## Verified facts
- Task mode is READ-ONLY / RECON + DESIGN.
- No Chernobylite semantic execution, no Scheduled Task changes, and no historical workflow rerun are permitted.

## Changes
- Report file only; no product/workflow/runtime implementation changes.

## Validation
- Required report path did not exist before this checkpoint and is now created in `main`.

## Unresolved
- Historical rerun failure mechanism.
- Whether a current-main single-AppID preparation path already exists.
- Smallest safe design if it does not.

## Status
`in_progress`

## Recommended next step
Trace repository truth for the Taste/pre-AI producer path and its invariants, then update this report with the design.

## Efficiency / reusable lesson
none
