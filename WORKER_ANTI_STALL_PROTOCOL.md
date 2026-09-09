# WORKER ANTI-STALL PROTOCOL

Purpose: prevent worker chats from silently consuming long response cycles while waiting on GitHub Actions or other asynchronous work.

This protocol applies to every non-trivial worker task in this repository.

## 1. Never wait silently on an external process

A worker must not keep a ChatGPT response open simply waiting for GitHub Actions, deployment, scheduled-task execution, remote indexing, or another asynchronous process to finish.

Immediately after starting an external process, the worker must persist a checkpoint in the exact task report containing:
- UTC timestamp;
- exact run/job/task id;
- what was launched;
- what must be checked next;
- confirmation that no duplicate retry may be launched blindly.

## 2. External-wait timebox

After launching an asynchronous process, the worker may perform only a short bounded verification window:
- at most 3 status checks;
- no more than roughly 10 minutes of waiting/polling in the same response cycle.

If the process is still running after that bounded window:
1. update the same durable report;
2. set non-final lifecycle state `waiting_external`;
3. record the exact run/job id and current remote status;
4. re-read the report from `main`;
5. return control to the user/Director immediately.

The next worker turn must resume from that exact run/job id. It must not launch a replacement unless the task explicitly authorizes one and repository truth proves the prior attempt did not start.

`waiting_external` is not task completion. Final status must still use the final statuses defined by the task.

## 3. Heartbeat checkpoint

While actively doing non-trivial work, update the durable report after every major milestone and before any potentially long step.

A report checkpoint must include:
- `Last checkpoint UTC`;
- current lifecycle state (`in_progress`, `waiting_external`, or a task-final state);
- the next concrete action.

Do not allow more than roughly 15 minutes of active worker effort without a durable checkpoint when the task is still unresolved.

## 4. No-progress rule

If the worker cannot make a concrete next step for roughly 10 minutes and there is no identified external run that is legitimately still executing, it must not remain silent.

It must persist the most truthful state and return control:
- task-defined `needs_followup` when another bounded step is required;
- task-defined `blocked` when progress cannot continue safely;
- `waiting_external` only when an identified asynchronous run is actually outstanding.

## 5. One long asynchronous action per response cycle

A worker should not chain multiple long remote operations inside one response cycle.

Preferred pattern:
1. prepare/checkpoint;
2. launch one long remote operation;
3. record exact identity;
4. bounded status check;
5. either consume the result if already complete or return `waiting_external`.

This makes worker replacement safe and keeps Director/user visibility high.

## 6. Recovery from a stale worker chat

When replacing a worker whose report has not changed for a long time:
- new worker starts from repository truth and the exact existing report;
- first determine whether the old worker actually launched any remote action after its last checkpoint;
- never infer from an old `not launched yet` checkpoint that nothing happened later;
- consume any discovered already-running/already-completed action rather than duplicating it;
- only launch a new attempt if the task permits it and current truth proves no prior attempt exists.

## 7. Director stall interpretation

A worker chat should be treated as probably stalled when:
- its durable report has had no checkpoint for more than ~20 minutes;
- and there is no explicitly recorded external run still in progress that explains the wait.

If an external run is recorded, Director may check only that run/report status. Director should not redo the worker's technical investigation.

## 8. Final response gate

Before any worker says the task is finished:
- exact report is updated in `main`;
- report is re-read;
- lifecycle state is not `in_progress` or `waiting_external`;
- final status is one of the exact final statuses defined by the task.
