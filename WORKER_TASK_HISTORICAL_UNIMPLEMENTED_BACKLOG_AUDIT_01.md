# WORKER TASK — Historical unimplemented backlog audit 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `DIAGNOSTIC / HISTORY AUDIT / NO IMPLEMENTATION`

## User goal

Recover the project's older **planned but still unimplemented tasks** that may have disappeared from the current forward task registry/page.

A known example is an old plan to add **YouTube reviews/videos to the game page**, but this is only an example. Do not stop after finding that one item.

## Required audit

Search the repository history deeply enough to reconstruct earlier plans, including as needed:
- historical versions of `DIRECTOR_TASK_BOARD.md`;
- historical `CURRENT_TASK.md`;
- old worker-task files and task filenames;
- project decisions / route / planning documents;
- worker reports where a follow-up was explicitly deferred;
- relevant merged/closed PR history and commit messages when needed to determine whether a planned task was later implemented, superseded, rejected or forgotten.

Do not assume every old mention is still valid.

For every plausible old task, classify it as one of:
1. **still unimplemented and should return to forward backlog**;
2. **already implemented / completed**;
3. **superseded / rejected by a later product decision**;
4. **duplicate of a current task**;
5. **unclear — needs Director/user decision**.

## Evidence requirement

For every task recommended for restoration, provide:
- original task/idea name or concise reconstructed name;
- what was supposed to be done;
- earliest/strongest durable evidence you found;
- evidence that it was **not subsequently implemented**;
- whether exact historical requirements are recoverable or need clarification;
- recommended effort / urgency;
- recommended dependency/order if known.

Specifically investigate the remembered YouTube-review task and recover its old intended scope if durable evidence exists. Do not invent channel/source/selection rules if they cannot be recovered.

## Boundaries

- Diagnostic only: **do not implement any recovered product task**.
- Do **not** modify `config/director_task_plan.json` or `DIRECTOR_TASK_BOARD.md` with recovered tasks.
- Do **not** create or modify Scheduled Tasks / automations.
- Do not change Steam, Dossier, Deep, ranking, site behavior or production data.
- Do not treat historical completed archive entries as live work merely because they are old.
- Prefer evidence over speculation.

## Deliverable

Create:
`reviews/worker_reports/historical-unimplemented-backlog-audit-01.md`

The report must end with a compact proposed restoration list for Director review.

Create a PR containing only the diagnostic report and minimal worker closeout metadata needed by protocol.

Stop after the report/PR. Do not start implementing any recovered task.
