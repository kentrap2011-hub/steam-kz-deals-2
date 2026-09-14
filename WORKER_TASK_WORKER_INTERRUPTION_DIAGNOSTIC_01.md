# WORKER TASK — Worker Interruption Diagnostic 01

## Task ID
`worker-interruption-diagnostic-01`

## Mode
`READ-ONLY / RECON`

## Goal
Determine, as far as observable evidence permits, what class of failure is causing repeated worker-session interruptions before task completion. Do not resume the interrupted dossier persistence implementation until this diagnostic is complete.

This is not permission to guess a hidden platform limit. The purpose is to collect evidence, compare repeated incidents, narrow the failure class, and define a bounded recovery rule.

## Required background
Read first:
- `CHAT_PROTOCOL.md` and perform START gate;
- `CHAT_CONTEXT.md`;
- `KNOWN_WORKER_PITFALLS.md -> PITFALL-004`;
- this task file completely.

Relevant observed incidents:
1. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` — worker previously described interruption as context exhaustion, later admitted no system signal/error supported that claim.
2. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md` — implementation existed only in worker branch when execution stopped before validation/merge; worker reported `причина неизвестна`.

## Scope
Use only observable evidence from the worker chat/session plus compact GitHub task/report/state needed to identify the last durable progress. Do not investigate application source code or production behavior unrelated to the interruption itself.

For each incident, record:
- last completed mandatory task-checklist item;
- last actual action before interruption;
- last tool/action invoked;
- whether that tool/action returned a response;
- exact visible system/tool error, if any;
- otherwise exact statement `system/tool error before interruption: none exposed`;
- last durable GitHub write/commit/branch state;
- whether the same chat accepted a subsequent user message;
- whether interruption occurred while reading, writing, waiting for a tool, validating, merging, or composing a response;
- any observable network/API/tool failure immediately before the stop;
- approximate count of major task stages completed since the prior durable checkpoint, if reconstructable without broad history search.

Then compare the incidents and classify the evidence into the narrowest defensible category, for example:
- `confirmed tool/network error`;
- `confirmed GitHub/action failure`;
- `repeatable stage-specific interruption`;
- `platform-level interruption with no exposed telemetry`;
- another specifically evidenced category.

Do not use plain `причина неизвестна` as the final diagnostic conclusion unless accompanied by a more useful observable classification and an explanation of exactly what telemetry is unavailable.

## Required diagnostic questions
1. Is there any actual system/platform error code or visible platform message in either incident?
2. Did the last invoked tool fail, return successfully, or have no visible response?
3. Is there a repeated stage pattern between incidents?
4. Is there a repeated tool or operation immediately before interruption?
5. Is there evidence of GitHub/network failure near the interruption?
6. Can the same chat continue after a new user message?
7. Which platform telemetry needed for root-cause determination is not exposed to the worker?
8. What additional evidence should be captured automatically on any future interruption so the next incident is more diagnosable?

## Boundaries
- READ-ONLY only except for writing this diagnostic report and required `CURRENT_TASK.md` handoff bookkeeping.
- Do not modify the interrupted implementation branch.
- Do not run validation, merge, production `Run now`, or the 591-item backlog.
- Do not create a new worker chat solely to bypass the interruption.
- Do not infer `context limit`, `timeout`, `runtime budget`, or similar without explicit evidence.

## Durable report
Write and merge to `main`:
`reviews/worker_reports/worker-interruption-diagnostic-01.md`

Report must include:
- incidents compared;
- evidence table/compact comparison;
- exact visible errors or `none exposed`;
- narrowest defensible failure classification;
- missing telemetry preventing stronger attribution;
- future interruption evidence-capture checklist;
- whether it is safe to resume the persistence-bridge task and under what checkpointing/mitigation conditions;
- exact refs;
- Status.

## Allowed final statuses
- `diagnosed_actionable`
- `classified_platform_unobservable`
- `needs_user_decision`
- `blocked`

## Expected next step
Director reads the report from `main` and decides whether to resume `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md` or adjust the worker execution procedure first.
