# DIRECTOR BOOTSTRAP

Last refreshed: 2026-09-21

Purpose: compact restart context for a NEW physical Director conversation.

This file is a bootstrap snapshot, not a replacement for canonical project truth. After reading it, the Director must use the latest `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, `DIRECTOR_TASK_BOARD.md`, exact active task files and durable worker reports as authoritative. If this file conflicts with newer canonical state, newer canonical state wins.

## Repository scope

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, change or use another repository for this project unless an exact task explicitly authorizes it.

## Director role

- Director orchestrates; worker chats execute nontrivial project work.
- GitHub owns production control-plane state.
- Interactive chats must not become production backlog workers.
- No autonomous IMPLEMENT without explicit user authorization.
- PASS 2 is not authorized.
- At most two worker slots are active when safe.
- Any text the user must copy goes in a copyable writing block.
- Named slot handoffs must state NEW/EXISTING physical chat explicitly outside the block and repeat the slot as the first line inside the block.

## Current product priority

Progressive Personalized Deals.

Accepted target:
1. `analyzed_fit` — visible first.
2. `analysis_incomplete` — visible second.
3. `not_analyzed` — visible third.
4. `analyzed_not_fit` — excluded from normal list.

PASS 1 is coverage-first, at most one attempt per current semantic binding. One failed item must not block later items. PASS 2 is separate future recovery and remains off.

## Accepted production baseline

Phase A is accepted/live.

Phase B PASS 1 code/control-plane is implemented and freshness-fixed.

Current known production facts:
- GitHub-owned PASS 1 is active.
- PASS 2 is inactive.
- current visual has 720 visible unresolved Tier 3 items after one legitimate expiry;
- the PASS 1 manifest/control-plane reported 721 remaining before that visual expiry projection;
- no real PASS 1 semantic item has yet been accepted;
- no PASS 1 retry/backlog drain has been authorized.

Key report:
`reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-implement-01.md`

## Current blocker

The bounded one-item live acceptance stopped as `blocked_external`.

Task:
`WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PHASE_B_PASS1_LIVE_ACCEPTANCE_01.md`

Report:
`reviews/worker_reports/progressive-personalized-deals-phase-b-pass1-live-acceptance-01.md`

Known facts from that acceptance:
- GitHub order selected sequence 1: Tower Dominion, `App_3226530`, appid `3226530`;
- no semantic result artifact was created;
- no PASS 1 attempt was consumed;
- no retry, second item, backlog drain or PASS 2 occurred;
- the worker environment could not invoke a claimed existing Scheduled PASS 1 worker.

Important: the existence of an actual correctly-bound Scheduled PASS 1 runtime entrypoint is NOT yet accepted as fact.

## Completed PASS 1 entrypoint audit

Task:
`WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PASS1_SCHEDULED_WORKER_ENTRYPOINT_AUDIT_01.md`

Report:
`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-entrypoint-audit-01.md`

Final status:
`complete_insufficient_observability`

Accepted result:
- the repository PASS 1 contract/prompt exists;
- Phase B created no new independent scheduler;
- an actual compatible Progressive PASS 1 Scheduled Task/runtime entrypoint is not yet proven to exist or be absent;
- `existing authorized Scheduled PASS 1 worker` is an unproven runtime-existence premise;
- Taste Semantic Producer and Taste Steam Review Dossier cannot be treated as PASS 1 workers unchanged;
- current overall blocker is `insufficient_observability`;
- no production attempt/state change occurred.

Exact unresolved fact:
- owner-scope Scheduled Tasks inventory must be inspected read-only for any Progressive PASS 1 candidate task, including title, task ID, enabled state, schedule/timezone and effective prompt/loader binding.

Until that is resolved:
- do not press `Run now`;
- do not create/reconfigure a Scheduled Task;
- do not resume PASS 1 production;
- do not start PASS 2.


## Existing Scheduled workers: do not conflate

Known existing historical tasks include:
- `Taste Steam Review Dossier`;
- `Taste Semantic Producer`.

They are separate mechanisms with separate contracts. Do not call either one the Progressive PASS 1 worker without the active audit proving compatibility/binding.

## Worker conversation state

- Previous physical ЧАТ 2: retired/overloaded. Never route work there as an existing chat.
- Slot `ЧАТ 2`: reusable only through a NEW physical chat for the active entrypoint audit.
- ЧАТ 1: contains the bounded PASS 1 live-acceptance attempt that ended `blocked_external`; do not resume production execution there until the entrypoint audit is accepted by Director.

## Immediate Director sequence

1. Treat the PASS 1 entrypoint audit as completed and accepted with `complete_insufficient_observability`.
2. Obtain one read-only owner-scope Scheduled Tasks inventory observation.
3. Classify exactly one branch:
   - compatible existing Progressive PASS 1 worker;
   - wrong runtime binding;
   - missing runtime entrypoint/setup;
   - still insufficient observability.
4. Only then choose the next bounded task/action.
5. Do not start PASS 1 production or PASS 2 before this classification.


## Director reliability rule

Do not continue from conversational momentum. Before every decision or handoff:
- separate confirmed facts from assumptions/unknowns;
- reconcile Board -> exact task -> exact durable report;
- scan for contradiction with protocol, ownership and user authorization;
- verify the proposed actor actually exists and owns the action;
- only then compose the user-facing instruction.

If repeated corrections indicate this Director conversation is accumulating conflicting operational state, rotate again to a new physical Director conversation and refresh this bootstrap rather than adding more conversational memory.
