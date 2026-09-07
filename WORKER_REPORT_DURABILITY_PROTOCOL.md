# WORKER REPORT DURABILITY PROTOCOL

This protocol exists because workers have repeatedly completed substantial work but failed to persist the required durable report before the response cycle ended.

This is a process failure, not an acceptable normal closeout state.

## Mandatory report-first lifecycle

For every non-trivial worker task with an expected report path:

1. After reading the task and before expensive investigation/implementation, create the exact required report file in `main` with status `in_progress` and a short scope/task identity section.
2. Update the same report after each major durable milestone (root cause proven, implementation committed, production run started/completed, acceptance result known).
3. Before starting a potentially long/expensive final verification sequence, persist a checkpoint into the report first.
4. If execution may end before full acceptance, stop additional exploration and persist the current truthful state (`blocked`, `needs_followup_fix`, or task-specific equivalent) rather than risking a missing report.
5. The final user-facing worker response must be sent only after the exact report path has been written to `main` and re-read/confirmed.
6. A worker must never say `finished`, `done`, `complete`, or equivalent when the required report is still only local/in-memory/uncommitted.

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
