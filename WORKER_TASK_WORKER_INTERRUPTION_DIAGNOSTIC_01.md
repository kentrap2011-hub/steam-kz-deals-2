# WORKER TASK — Worker Interruption Diagnostic 01

## Task ID
`worker-interruption-diagnostic-01`

## Mode
`READ-ONLY / RECON`

## Goal
Determine, as far as observable evidence permits, what class of failure is causing repeated worker-session interruptions before task completion, using an exact reproducibility trace and controlled replay rather than blind retries.

Important current-state rule: if `ЧАТ 2` is already actively executing the previously issued continuation of `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md`, do **not** interrupt that in-flight work merely to start this diagnostic. Let the current execution reach its next safe boundary: either successful task completion/report, or another interruption. Run this diagnostic immediately after that boundary and before any further blind retry if another unknown interruption occurs.

## Required background
Read first:
- `CHAT_PROTOCOL.md` and perform START gate;
- `CHAT_CONTEXT.md`;
- `KNOWN_WORKER_PITFALLS.md -> PITFALL-004`;
- this task file completely.

Relevant observed incidents:
1. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` — worker previously described interruption as context exhaustion, later admitted no system signal/error supported that claim.
2. `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PERSISTENCE_BRIDGE_01.md` — implementation existed only in worker branch when execution stopped before validation/merge; worker reported `причина неизвестна`.

If the currently in-flight continuation produces another interruption before this diagnostic starts, include that occurrence as an additional incident and capture its exact reproduction recipe before any further retry.

## Primary diagnostic method — reproduce, then minimize
For every unknown interruption, reconstruct the exact observable action sequence from the last durable checkpoint to the stop. The reproduction recipe must include, in order:
- checklist stage;
- concrete action;
- tool/action/command used;
- relevant non-secret arguments and refs;
- batch/range/payload size or other load-shaping parameters;
- whether each action received a response;
- brief observable result and refs/commit/run/job where applicable;
- exact final action before the interruption.

Then perform a controlled replay in maximally equivalent conditions.

If the original sequence contains unsafe or irreversible production writes, replay it on a disposable branch, synthetic fixture or otherwise safe equivalent while preserving operation type, ordering, argument shape and comparable load. Do not damage production merely to reproduce a platform interruption.

If the interruption reproduces, minimize it: split the sequence into smaller parts and rerun progressively smaller subsets until the smallest reproducible action sequence is identified. Test observable variables one at a time where feasible, such as:
- specific tool/action;
- read vs write vs validation vs merge stage;
- payload/result size;
- number of sequential tool calls;
- specific operation type;
- network/API behavior;
- waiting on a tool response vs response composition.

If it does not reproduce, record `not reproduced`, all replay conditions, and every known difference from the original incident. Do not declare the issue solved merely because one replay succeeded.

## Required incident record
For each incident record:
- last completed mandatory task-checklist item;
- last durable checkpoint;
- exact ordered reproduction recipe after that checkpoint;
- last actual action before interruption;
- last tool/action invoked;
- whether that tool/action returned a response;
- exact visible system/tool error, if any;
- otherwise exact statement `system/tool error before interruption: none exposed`;
- branch/commit/write state;
- whether the same chat accepted a subsequent user message;
- whether interruption occurred during read/write/validation/merge/tool wait/response composition;
- any observable network/API/tool failure immediately before the stop.

## Required diagnostic questions
1. Is there any actual system/platform error code or visible platform message in any incident?
2. Can the action sequence be reproduced in the same chat/session class?
3. If reproduced, what is the smallest reproducible sequence?
4. Which exact tool/action or stage is common to reproductions?
5. Does changing payload/range/batch size change reproducibility?
6. Did the last invoked tool fail, return successfully, or have no visible response?
7. Is there evidence of GitHub/network failure near the interruption?
8. Can the same chat continue after a new user message?
9. Which platform telemetry needed for root-cause determination is not exposed to the worker?
10. What trace must future workers persist proactively so another incident can be replayed exactly?

## Classification
Return the narrowest defensible class, such as:
- `confirmed tool/network error`;
- `confirmed GitHub/action failure`;
- `repeatable tool-specific interruption`;
- `repeatable payload/size-sensitive interruption`;
- `repeatable stage-specific interruption`;
- `platform-level interruption with no exposed telemetry`;
- another specifically evidenced category.

Plain `причина неизвестна` is not a sufficient diagnostic conclusion after controlled reproduction has been attempted.

## Boundaries
- READ-ONLY only except for writing this diagnostic report and required `CURRENT_TASK.md` handoff bookkeeping.
- Do not interrupt already in-flight persistence-bridge execution solely to start this task.
- Once this diagnostic begins, do not modify the interrupted implementation branch.
- Safe disposable/synthetic reproduction is allowed only as needed to reproduce tool/action behavior; do not alter production state.
- Do not run production `Run now` or the real 591-item backlog as part of this diagnostic.
- Do not create a new worker chat solely to bypass the interruption.
- Do not infer `context limit`, `timeout`, `runtime budget`, or similar without explicit evidence.

## Durable report
Write and merge to `main`:
`reviews/worker_reports/worker-interruption-diagnostic-01.md`

Report must include:
- incidents compared;
- exact reproduction recipe(s);
- replay result(s);
- smallest reproducible sequence if found;
- variables tested during minimization;
- exact visible errors or `none exposed`;
- narrowest defensible failure classification;
- missing telemetry preventing stronger attribution;
- future proactive trace/checkpoint rule;
- whether it is safe to continue/resume the persistence-bridge task and under what mitigation conditions;
- exact refs;
- Status.

## Allowed final statuses
- `diagnosed_actionable`
- `classified_platform_unobservable`
- `needs_user_decision`
- `blocked`

## Expected next step
Director reads the report from `main` and decides whether any worker execution procedure must change before the next persistence-bridge continuation or production validation.
