# PROACTIVE PROJECT AUDITOR PROTOCOL

## Purpose

The project must not rely on the user to notice operational, orchestration, scheduling, queue-ordering, stale-binding, or architecture gaps.

A reusable **Proactive Project Auditor** role performs bounded read-only checks and raises gaps itself.

The auditor is not a permanent third worker. It uses a free `ЧАТ 1` or `ЧАТ 2` slot when a trigger below is reached, preserving the global maximum of two worker chats.

## Core rule

The user should not have to ask questions such as:
- is the Scheduled Task still using an old canary prompt?
- is the cadence still the old cadence?
- are queue priorities actually the intended priorities?
- did a design assumption become stale after a later change?
- is a finished fix wired into the real production path?
- are we processing the right work first?
- did a worker finish only a local layer while the authorized end-to-end goal remains incomplete?

The auditor must proactively look for these classes of mismatch at the defined gates.

## Mandatory audit triggers

Run a bounded proactive audit when safe after any of these events:
1. a production failure or fail-closed stop;
2. a change to producer/scheduler/queue/cache/ingest lifecycle;
3. a change to a user operating requirement such as cadence, priority/order, or processing scope;
4. before declaring an automated production mode fully enabled;
5. after a multi-step architecture repair reaches terminal acceptance;
6. when the Director observes that the same category of issue has required repeated user discovery.

Do not interrupt an in-flight atomic production operation merely to audit it. Audit at the next safe boundary.

## Audit scope

Read-only by default. Inspect only the smallest set of live artifacts needed to compare:
- current user goal and explicit operating requirements;
- `DIRECTOR_TASK_BOARD.md`;
- the exact active task/report;
- actual Scheduled Task prompt/cadence when relevant;
- active producer/ownership contract when relevant;
- real queue construction/order when relevant;
- live workflow wiring for the affected path when relevant;
- stale canary/test-only assumptions that could still be active in production.

Do not perform a broad repository review without a named reason.

## Required questions

For every bounded audit, ask:
1. Is the live system doing what the user currently thinks it is doing?
2. Is any temporary canary/test/recovery restriction still active after its purpose ended?
3. Is the current queue/work ordering aligned with the user's priority policy?
4. Is the actual schedule aligned with the user's requested cadence?
5. Did the latest fix reach the real production path end-to-end?
6. Is any existing design/report now stale because a later requirement superseded it?
7. Is there avoidable repeated work that should be converted into a queued architecture improvement?
8. Is any unresolved blocker being mistaken for normal capacity or business behavior?

## Findings

The auditor must distinguish:
- `blocking_gap` — active processing would be incorrect/unsafe;
- `operational_gap` — system works but not according to current intended behavior;
- `optimization_gap` — safe to defer;
- `no_gap_found`.

For every gap, record:
- exact observed mismatch;
- evidence/ref;
- user-visible consequence;
- smallest next action;
- whether processing may safely continue before the fix.

## Authority

The auditor may:
- read relevant state;
- create/update its compact report;
- recommend or add a clearly labeled backlog item to `DIRECTOR_TASK_BOARD.md` through Director coordination.

The auditor may not, unless a separate task explicitly authorizes it:
- change production code/config/contracts;
- mutate queues/cache/results;
- rerun failed production work;
- change a Scheduled Task;
- broaden scope into implementation.

Finding a gap does not grant repair authority.

## Director obligation

At each mandatory trigger, the Director must decide whether the audit can run safely in a free worker slot. If yes, schedule it without requiring the user to first identify a suspected problem.

The Director should only involve the user when:
- a product/priority choice is genuinely ambiguous;
- a consequential implementation needs authorization;
- the evidence cannot resolve the required decision.

The user is not the project's monitoring layer.
