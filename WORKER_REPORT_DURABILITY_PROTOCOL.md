# WORKER REPORT DURABILITY PROTOCOL

This protocol exists because workers have repeatedly completed substantial work but failed to persist the required durable report before the response cycle ended.

This is a process failure, not an acceptable normal closeout state.

Every worker governed by this protocol must also obey `WORKER_ANTI_STALL_PROTOCOL.md`.

## Mandatory report-first lifecycle

For every non-trivial worker task with an expected report path:

1. After reading the task and before expensive investigation/implementation, create the exact required report file in `main` with status `in_progress` and a short scope/task identity section.
2. Update the same report after each major durable milestone (root cause proven, implementation committed, production run started/completed, acceptance result known).
3. Every checkpoint must include `Last checkpoint UTC`, the current lifecycle state, and the next concrete action.
4. Before starting a potentially long/expensive final verification sequence or any asynchronous external process, persist a checkpoint into the report first.
5. Immediately after launching an asynchronous process, persist its exact run/job/task id before waiting or doing further work.
6. Never wait silently on an asynchronous process. Follow `WORKER_ANTI_STALL_PROTOCOL.md`: bounded polling only, then persist `waiting_external` and return control if it is still running.
7. If execution may end before full acceptance, stop additional exploration and persist the current truthful state (`blocked`, `needs_followup_fix`, task-specific equivalent, or non-final `waiting_external`) rather than risking a missing/stale report.
8. The final user-facing worker response must be sent only after the exact report path has been written to `main` and re-read/confirmed.
9. A worker must never say `finished`, `done`, `complete`, or equivalent when the required report is still only local/in-memory/uncommitted or has lifecycle state `in_progress`/`waiting_external`.

## Mandatory self-diagnosis on unsuccessful outcome

If a worker cannot complete its assigned task and is about to finish with any failure/follow-up state such as `failed`, `failed_closed`, `blocked`, `needs_followup`, or a task-specific equivalent, the worker must perform a bounded self-diagnosis **before returning control** whenever the evidence needed for that diagnosis is already available within the authorized scope.

The same durable report must record:
- the exact step/action that failed or blocked progress;
- the first real error or failed invariant, not only downstream symptoms;
- the most specific root cause that can be proven from available evidence;
- whether the failure is semantic/business-data related, code/config related, runtime/tooling related, external-process related, permissions/auth related, or still unknown;
- what state was already changed before the failure and what state definitely was not changed;
- whether already-produced artifacts/results remain valid and reusable;
- whether retrying unchanged would be safe, pointless, or dangerous;
- the smallest recommended next action;
- what the worker deliberately did **not** attempt because it was outside authorization.

The worker must distinguish clearly between:
- `root_cause_proven` — direct evidence identifies the cause;
- `likely_root_cause` — evidence strongly points to a cause but does not prove it;
- `root_cause_unknown` — available evidence is insufficient.

A worker must never invent a confident root cause merely to satisfy this rule.

### Self-diagnosis boundaries

Self-diagnosis does **not** expand implementation authority.

Unless the task explicitly authorizes it, the worker must not during self-diagnosis:
- repair code/configuration/state;
- rerun a failed production action;
- regenerate semantic/AI results;
- mutate queues, caches, canonical data, Scheduled Tasks, secrets, or external systems;
- widen the task into a general architecture audit;
- bypass a fail-closed guardrail.

Read-only inspection of the exact failed run/job/log/step, already-produced artifact, directly involved code path, or exact invariant is allowed when necessary to identify the failure and when that inspection is available within the task's existing permissions/scope.

If meaningful diagnosis itself would require a new consequential action, broad investigation, unavailable permissions/tooling, or work explicitly forbidden by the task, record that limitation and stop. Director can then create a separate diagnosis/repair task if needed.

### Why this rule exists

A failed worker should normally hand Director a usable explanation, not merely `something failed`. This avoids unnecessary follow-up diagnosis chats when the worker already has the evidence in front of it, while preserving the rule that fixes and retries require their own authorization when not already granted.

## Heartbeat requirement

Do not allow more than roughly 15 minutes of unresolved active worker effort without a durable report checkpoint.

If no concrete progress is possible for roughly 10 minutes and there is no identified external process legitimately still running, persist a truthful stop/follow-up state and return control instead of remaining silent.

## Missing-report recovery gate

If a previous response cycle ended and the exact required report still does not exist in `main`, the next worker turn is a persistence-recovery turn.

The **first repository mutation/tool action in that turn must create the exact report path** with status `in_progress` (or the most truthful already-known non-final status) and summarize the already-completed work from the worker's current context.

Before that first report write, do NOT:
- rerun tests;
- inspect Actions/logs;
- do more code/history research;
- start a new implementation step;
- perform another acceptance check.

If the first report write fails, stop immediately and report the exact persistence/tool error. Do not spend the turn on other work.

After the report exists in `main`, the worker may continue only the bounded closeout needed to finalize that same report.

## Stale-worker recovery gate

If a worker chat is being replaced after a stale checkpoint, the replacement must first determine whether the old worker launched any asynchronous action after its last saved checkpoint.

Do not blindly repeat a supposedly `not launched yet` action solely from an old report. Search current repository/Actions/task truth for a matching later run first. If one exists, consume that exact attempt. Launch a new attempt only if current truth proves no prior attempt exists and the task still authorizes it.

## Priority rule

When forced to choose between one more diagnostic/verification action and preserving the durable report, preserve the report first. Additional work can continue in the next turn; an unsaved result cannot be consumed reliably by Director.

## No false completion

If report persistence fails for any reason:
- say explicitly that the task is **not durably closed**;
- do not claim completion;
- remain in the same worker chat;
- retry only the report persistence/closeout path unless the task itself was also incomplete.

## Director handling

Director treats a missing exact report as incomplete regardless of worker prose. Director does not reconstruct the worker's result from Actions/logs/commits unless the task contract explicitly allows that.

A report with no checkpoint for more than ~20 minutes and no recorded external run explaining the wait is presumptively stalled and the worker may be replaced from durable state.
