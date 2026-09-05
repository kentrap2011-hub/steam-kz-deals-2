# WORKER TASK — DIRECTOR ORCHESTRATION SHADOW OBSERVER IMPLEMENT 01

Task ID: `director-orchestration-shadow-observer-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/director-orchestration-shadow-observer-implement-01.md`
Priority: `VERY_HIGH_INFRASTRUCTURE_PRIORITY`

## Context

Direct continuation of:
`reviews/worker_reports/autonomous-director-orchestration-recon-01.md`

The recon concluded that cloud-first automation without a permanently running home PC is feasible, but ordinary ChatGPT worker chats are not a reliable automation substrate. The recommended Phase 1 is a deterministic **shadow observer** that computes what the future orchestrator *would* assign while making no product-task dispatches and no automatic repository/product changes.

The current manual Taste IMPLEMENT in Chat 1 remains active and must be represented as an occupied external/manual slot so the shadow planner cannot pretend both slots are free.

## Goal

Implement only Phase 1 shadow orchestration safety primitives.

The system must be able to:
- represent orchestration state in machine-readable form;
- represent the current manual slot occupancy;
- evaluate priority, dependencies and semantic conflict keys;
- compute at most two `would_assign` candidates deterministically;
- reject conflicting/stale/cancelled/dependency-blocked tasks;
- run safely in GitHub Actions;
- publish only a shadow plan/artifact/report;
- never dispatch a worker, invoke OpenAI/Codex, mutate product state, merge code, or alter current worker assignments.

## Required implementation

### 1. Contract

Create:
`config/director_orchestration_contract.json`

It must define at minimum:
- Phase 1 shadow-only mode;
- max logical slots = 2;
- allowed task status enum;
- priority semantics;
- dependency semantics;
- explicit semantic conflict keys;
- single-state-writer invariant for future phases;
- external/manual slot occupancy support;
- stale/cancelled/deferred tasks are not eligible;
- current contract does NOT replace `DIRECTOR_PROTOCOL.md`, `DIRECTOR_TASK_BOARD.md` or `DIRECTOR_REVIEW_CHECKPOINTS.md` yet;
- no secrets in orchestration state.

### 2. Initial shadow state

Create:
`orchestration/state.json`

It must:
- have explicit schema/state revision;
- contain two logical slots;
- record current Chat 1 Taste task as external/manual occupancy;
- contain a small representative queued task set sufficient to prove ordering/conflicts, derived from current Director board/task files rather than invented fake product policy;
- include task_id, revision, mode, priority, conflict keys, status, task_file, expected_report, dependencies, assigned_slot, user/review gate summaries as needed for Phase 1;
- contain no secret values.

Do not migrate the whole backlog in this task. Only enough state to prove the shadow planner safely.

### 3. Deterministic shadow planner

Create:
`scripts/director_orchestration_shadow.py`

It must:
- validate the contract/state shape;
- detect current occupied slots;
- compute which queued tasks would be eligible;
- enforce dependencies and conflict keys;
- enforce max 2 total occupied/would-assigned slots;
- keep manual/external occupancy reserved;
- sort deterministically using explicit user priority, then dependency-unblocking value/age/FIFO only as defined by the contract;
- ignore stale/cancelled/deferred/blocked tasks;
- emit deterministic JSON plan to stdout/file;
- make no repository writes and no dispatches;
- fail closed on malformed/ambiguous state.

Recommended output fields:
- `observed_state_revision`;
- `occupied_slots`;
- `would_assign`;
- `blocked_by_conflict`;
- `blocked_by_dependency`;
- `ineligible`;
- `warnings`.

### 4. GitHub Actions shadow workflow

Create:
`.github/workflows/director-orchestration-shadow.yml`

Requirements:
- `workflow_dispatch`;
- safe low-frequency reconciliation trigger is allowed;
- one serialized concurrency group, e.g. `director-orchestrator-shadow`;
- minimal read permissions;
- checkout current repo;
- run deterministic tests and planner;
- upload `shadow-plan.json` as artifact;
- no OpenAI/Codex call;
- no repository_dispatch/workflow dispatch of workers;
- no commit/push/PR/merge;
- no product pipeline trigger.

### 5. Focused deterministic tests

Add a bounded test file, e.g.:
`scripts/test_director_orchestration_shadow.py`

At minimum prove:
1. max two slots total;
2. current manual Taste task occupies one slot;
3. a conflicting Taste/ranking task is not selected in the other slot;
4. an unrelated safe task can be selected for the free slot;
5. unmet dependency blocks assignment;
6. higher explicit user priority wins among equally safe eligible tasks;
7. stale/cancelled/deferred task is not selected;
8. malformed/ambiguous state fails closed;
9. no more than one free slot is filled while Chat 1 remains manually occupied.

## Current active/manual occupancy

Bind the initial manual occupied slot to the current active task:
`WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`

Do not modify or interrupt that task.

## Boundaries

Do NOT:
- invoke OpenAI/Codex;
- add `OPENAI_API_KEY` or any secret;
- dispatch workers;
- auto-assign/modify actual product tasks;
- edit product pipeline behavior;
- change Taste/ranking implementation;
- modify review checkpoint semantics;
- merge/deploy product changes automatically;
- migrate the entire backlog;
- create GitHub Issues/Projects as a second canonical task database;
- add a third worker slot.

## Validation

Required:
- local deterministic test(s) pass;
- workflow syntax is valid;
- one normal `workflow_dispatch` run of `director-orchestration-shadow.yml` succeeds;
- artifact `shadow-plan.json` exists;
- artifact proves Chat 1 manual occupancy is respected and at most one `would_assign` task is chosen for the free slot;
- no worker/product workflow was dispatched as a side effect.

## Done when

Save:
`reviews/worker_reports/director-orchestration-shadow-observer-implement-01.md`

Include:
1. Status
2. Files changed
3. Contract/state semantics
4. Exact current manual slot binding
5. Test results
6. Shadow workflow run ID/job ID
7. Shadow artifact ID/name
8. Exact `would_assign` result
9. Proof no real worker/product dispatch occurred
10. Any blocker before Phase 2
11. One bounded next step only
12. Exact commits/refs

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
