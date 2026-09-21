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

## Active audit

Prepared task:
`WORKER_TASK_PROGRESSIVE_PERSONALIZED_DEALS_PASS1_SCHEDULED_WORKER_ENTRYPOINT_AUDIT_01.md`

Mode:
`READ-ONLY / ENTRYPOINT + OWNERSHIP AUDIT`

Assigned slot:
`НОВЫЙ ЧАТ — ЧАТ 2`

The previous physical ЧАТ 2 is retired/overloaded and must not be reused.

The audit must distinguish:
1. repository PASS 1 worker contract/prompt;
2. actual Scheduled Task/runtime entrypoint;
3. actual callable execution surface.

It must compare Progressive PASS 1 with:
- `Taste Semantic Producer`;
- `Taste Steam Review Dossier`.

No Scheduled Task run, reconfiguration, PASS 1 attempt, Tower Dominion analysis, backlog drain or PASS 2 is allowed in the audit.

Expected report:
`reviews/worker_reports/progressive-personalized-deals-pass1-scheduled-worker-entrypoint-audit-01.md`

As of this bootstrap refresh, creation of the audit task is confirmed; execution of that new ЧАТ 2 audit has not been confirmed by the user yet.

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

1. In the new Director conversation, read latest `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, this file and `DIRECTOR_TASK_BOARD.md`.
2. Reconcile the active audit assignment.
3. If the audit has not been launched, provide its launch only to `НОВЫЙ ЧАТ — ЧАТ 2`, using a copyable block.
4. When the user says the audit is complete / asks to check it, read its exact durable report first.
5. Classify the blocker from evidence:
   - existing compatible worker;
   - missing runtime task/setup;
   - wrong runtime binding;
   - insufficient observability.
6. Only then choose the next bounded step.
7. Do not start PASS 2.

## Director reliability rule

Do not continue from conversational momentum. Before every decision or handoff:
- separate confirmed facts from assumptions/unknowns;
- reconcile Board -> exact task -> exact durable report;
- scan for contradiction with protocol, ownership and user authorization;
- verify the proposed actor actually exists and owns the action;
- only then compose the user-facing instruction.

If repeated corrections indicate this Director conversation is accumulating conflicting operational state, rotate again to a new physical Director conversation and refresh this bootstrap rather than adding more conversational memory.
