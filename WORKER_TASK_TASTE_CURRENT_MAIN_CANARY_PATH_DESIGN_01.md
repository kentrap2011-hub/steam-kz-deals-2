# WORKER TASK — TASTE CURRENT-MAIN CANARY PATH DESIGN 01

## Mode
READ-ONLY / RECON + DESIGN

## Expected report
`reviews/worker_reports/taste-current-main-canary-path-design-01.md`

## Goal
Design the smallest safe way to prepare and test exactly one Taste game, Chernobylite AppID 1016800, starting from current `main` instead of rerunning an old historical workflow attempt.

Do not implement or run the canary in this task.

## Read first
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `WORKER_ANTI_STALL_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `reviews/worker_reports/taste-preai-sync-retry-after-contention-01.md`

## Required answer
Establish from current repository truth:
1. why the historical rerun path failed;
2. whether an existing fresh-current-main path can regenerate only the Taste/pre-AI state needed for AppID 1016800;
3. if not, the smallest safe change needed to create such a path;
4. exact scripts/workflows/files involved;
5. how to avoid touching unrelated production outputs;
6. how to avoid write conflicts;
7. how all existing profile-binding, producer-fence, semantic validation, ingest, receipt/cache and queue guarantees remain unchanged;
8. implementation plan for a later task;
9. acceptance plan;
10. expected runtime improvement compared with rerunning the full production workflow.

## Boundaries
- current `main` only;
- no historical workflow rerun as the proposed normal canary path;
- no manual generated-file or hash edits;
- no new semantic producer or Scheduled Task;
- no semantic execution;
- no unrelated backlog work.

## Final status
Exactly one:
- `complete_design_ready_for_implementation`
- `needs_followup`
- `blocked`
