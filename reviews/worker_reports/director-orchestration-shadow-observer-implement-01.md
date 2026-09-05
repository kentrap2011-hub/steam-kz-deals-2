# Director Orchestration Shadow Observer Implement 01

Task: `director-orchestration-shadow-observer-implement-01`
Mode: `IMPLEMENT` — Phase 1 shadow observer only
Status: `complete`

## 1. Task

Implement the smallest safe Phase 1 simulation of the future autonomous Director without OpenAI/Codex, API credentials, real worker dispatch, product-task mutation, product merge/deploy, or interference with the active Chat 1 Taste IMPLEMENT.

Required proof was a real `workflow_dispatch` run of `.github/workflows/director-orchestration-shadow.yml` producing `shadow-plan.json` and demonstrating:

- Chat 1 is already occupying one logical slot;
- at most one second slot is free;
- conflicting Taste/ranking work is not selected;
- an independent safe task can be selected;
- no real worker/product workflow is dispatched.

## 2. Changes

Permanent Phase 1 files added:

1. `config/director_orchestration_contract.json`
   - Phase 1 explicitly `shadow_observer` / read-only planning;
   - exactly two logical slots;
   - deterministic priority ordering;
   - fail-closed dependency semantics;
   - shared semantic conflict keys;
   - external/manual occupancy is reserved;
   - only `queued` tasks are eligible;
   - stale/cancelled/deferred/blocked/accepted states are not eligible;
   - future single state writer is one serialized GitHub dispatcher/controller;
   - current Director protocol/board/review checkpoints remain canonical and are not replaced;
   - OpenAI/Codex, worker dispatch, product mutation and secrets in state are forbidden in Phase 1.

2. `orchestration/state.json`
   - machine-readable `schema_version=1`, `state_revision=1`;
   - exactly `slot_1` and `slot_2`;
   - `slot_1` bound to the current manual Chat 1 Taste task;
   - `slot_2` free;
   - small representative queue from existing Director/task files only.

3. `scripts/director_orchestration_shadow.py`
   - validates contract/state and fails closed on ambiguity;
   - validates exact occupied-slot/task binding;
   - validates dependency references;
   - respects gates/status/priority/dependencies/conflicts;
   - computes dependency-unblocking tie-break value;
   - caps total occupied + `would_assign` at two;
   - produces deterministic JSON only;
   - performs no dispatch or repository/product mutation.

4. `scripts/test_director_orchestration_shadow.py`
   - 10 focused deterministic tests.

5. `.github/workflows/director-orchestration-shadow.yml`
   - trigger: `workflow_dispatch` only;
   - `permissions: contents: read`;
   - `persist-credentials: false` checkout;
   - serialized concurrency group `director-orchestrator-shadow`;
   - runs tests + planner;
   - uploads artifact `shadow-plan` containing `shadow-plan.json`;
   - contains no OpenAI/Codex step, API key, repository dispatch, worker workflow dispatch, commit, push, PR, merge or deploy step.

No product source, product task, Taste implementation, Director checkpoint, deploy pipeline or runtime contract was changed.

## 3. Exact manual slot binding

`orchestration/state.json` records:

- `slot_1.status = occupied`;
- `slot_1.occupancy_type = external_manual`;
- `slot_1.task_id = taste-evidence-state-and-confidence-implement-01`;
- `slot_1.task_file = WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`;
- active conflict keys: `taste-write`, `ranking-write`, `taste-ranking-policy`;
- `slot_2.status = free`.

The active Chat 1 task itself remains untouched.

## 4. Planner semantics

Eligibility is deterministic and fail-closed:

1. task must be `queued`;
2. user/review gates must be clear;
3. every dependency must exist in state and have a satisfied terminal status;
4. no semantic conflict key may overlap an occupied slot;
5. no semantic conflict key may overlap another task already selected in the same plan;
6. candidates sort by:
   - explicit priority class descending;
   - dependency-unblocking value descending;
   - queue sequence ascending;
   - task ID ascending;
7. selected tasks fill only currently free logical slots;
8. occupied + `would_assign` may never exceed 2.

Malformed/ambiguous state raises `ShadowPlanError`; no guessed assignment is emitted.

## 5. Local validation

Local focused validation before publication:

`python scripts/test_director_orchestration_shadow.py -v`

Result: **10/10 passed**.

Covered:

1. max two slots;
2. manual Chat 1 Taste occupancy is reserved;
3. conflicting Taste/ranking task is not selected;
4. unrelated safe task can be selected;
5. unmet dependency blocks selection;
6. higher explicit priority wins when candidates are otherwise safe;
7. dependency-unblocking value is a deterministic tie-breaker;
8. stale/cancelled/deferred tasks are not selected;
9. malformed/ambiguous slot binding fails closed;
10. missing dependency fails closed;
11. selected tasks cannot conflict with each other (included within the 10 test methods).

Local initial plan matched the later GitHub artifact.

## 6. Real GitHub Actions validation

Target workflow:

`.github/workflows/director-orchestration-shadow.yml`

Real run:

- run ID: `33955350364`;
- run number: `1`;
- event: **`workflow_dispatch`**;
- head SHA: `d07dfaa6544352cdcbb5874610c3db4dc3643e81`;
- status: `completed`;
- conclusion: **`success`**;
- job ID: `101277589011`;
- job: `shadow-plan`;
- all steps succeeded, including tests, plan build and artifact upload.

The GitHub-hosted run independently reran the same 10 tests and reported `Ran 10 tests ... OK`.

Target workflow token permissions in the run log:

- `Contents: read`;
- `Metadata: read`.

No write permission was available to the target shadow planner job.

## 7. Artifact

Artifact:

- artifact ID: `9966167937`;
- artifact name: `shadow-plan`;
- contained file: `shadow-plan.json`;
- size: `1057` bytes;
- digest: `sha256:d9a16064c14d28b7fb5e1362c797e75b1c01b8d21171cd1b9bd2c13f5886ca43`;
- source run: `33955350364`;
- source head: `d07dfaa6544352cdcbb5874610c3db4dc3643e81`.

Artifact was downloaded and inspected after the run.

## 8. Exact `would_assign`

`shadow-plan.json` contains exactly one proposed assignment:

- task: `epic-ru-availability-source-probe-01`;
- task file: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`;
- mode: `READ_ONLY_RECON`;
- domain: `epic-ru-availability`;
- conflict key: `provider-authority:epic`;
- proposed slot: `slot_2`.

This is simulation only. The task was **not dispatched**.

The artifact reports:

- `occupied_slots[0] = slot_1 / taste-evidence-state-and-confidence-implement-01 / external_manual`;
- `free_slots_before_plan = [slot_2]`;
- `total_occupied_or_would_assign = 2`;
- `max_two_slots_respected = true`;
- `manual_external_occupancy_reserved = true`.

## 9. Conflict and dependency proof

`wishlist-good-deal-override-recon-01` was not selected despite its high shadow priority.

It appears in `blocked_by_conflict` because its keys overlap the occupied Taste slot:

- `taste-write`;
- `ranking-write`;
- `taste-ranking-policy`.

It independently appears in `blocked_by_dependency` because:

- required dependency: `taste-evidence-state-and-confidence-implement-01`;
- that dependency is still represented as `running`, not accepted.

Therefore explicit priority cannot bypass dependency or conflict safety.

`top-summary-filter-buttons-01` is independent and otherwise eligible, but appears under `eligible_not_selected` with `reason = capacity`, because only `slot_2` is free and the higher-priority safe RECON was selected first.

## 10. Proof that no real worker/product dispatch occurred

There are three independent layers of proof.

### A. Target workflow definition

`.github/workflows/director-orchestration-shadow.yml` contains only:

- checkout;
- deterministic Python tests;
- deterministic planner execution;
- `cat shadow-plan.json`;
- artifact upload.

It has no `repository_dispatch`, no worker `workflow_dispatch`, no OpenAI/Codex, no commit/push, no PR/merge and no deploy step.

### B. Target run permissions and steps

Run `33955350364`, job `101277589011` had only read GitHub content permission. Its recorded successful steps were exactly:

1. checkout;
2. tests;
3. build shadow plan;
4. show shadow plan;
5. upload artifact;
6. cleanup.

The artifact itself states:

- `worker_dispatch_performed = false`;
- `product_mutation_performed = false`;
- `openai_or_codex_invoked = false`.

### C. Exact run inventory around the dispatch head

For exact head `d07dfaa6544352cdcbb5874610c3db4dc3643e81`, GitHub reported `total_count = 3` workflow runs only:

1. `33955350364` — **Director orchestration shadow observer**, event `workflow_dispatch`;
2. `33955346471` — one-time **Director orchestration shadow bootstrap**, event `push`, used only to call the target workflow's official `workflow_dispatch` endpoint because the available connected GitHub tool surface exposes Actions reads/reruns but no first-run dispatch method;
3. `33955346434` — existing infrastructure guard **Validate execution ownership**, event `push`.

There was no worker workflow, Codex/OpenAI workflow, product build workflow, product deploy workflow or product task dispatch in that exact run set.

The one-time bootstrap contained no product logic and used only the ephemeral GitHub Actions `github.token` with `actions: write` to dispatch **the shadow observer itself**. It was immediately removed after the successful target run:

- bootstrap add commit: `d07dfaa6544352cdcbb5874610c3db4dc3643e81`;
- bootstrap removal commit: `7c24c30f44977350a6f9f94cee6d32401054acf3`.

It is not part of the steady-state Phase 1 implementation.

The ordinary existing `Validate execution ownership` push workflow is an infrastructure guard, not a product worker/dispatch, and it completed successfully.

## 11. OpenAI/API/secret proof

Phase 1 used:

- no OpenAI API call;
- no Codex invocation;
- no `OPENAI_API_KEY`;
- no provider credential;
- no secret stored in contract/state/report.

The target shadow workflow runs entirely from repository state on a GitHub-hosted runner.

## 12. Commit refs

Permanent implementation commits, in order:

- `1c0eec9fb4315042bc6288c54873d7c91b8e05a3` — Phase 1 orchestration contract;
- `afcc25157c1325ea9b2df2c9d70382bcb88a9473` — initial machine-readable shadow state;
- `148dfdf28a1cc449ec329a0b913c724dc942aa0f` — deterministic planner;
- `9b8a0ddb35a80dcdb0b30e29b49a54a0fcb0f4bd` — focused tests;
- `86570fac9ca81f7d33496fa5e7d24449ed5df828` — permanent shadow workflow.

Validation-only transient bootstrap:

- add: `d07dfaa6544352cdcbb5874610c3db4dc3643e81`;
- remove: `7c24c30f44977350a6f9f94cee6d32401054acf3`.

No product commit/merge/deploy was made by the shadow observer.

## 13. Phase 2 blocker assessment

**No architectural blocker was found before Phase 2.** Phase 1 demonstrated the safety invariants required before adding a cloud worker substrate:

- durable machine-readable state exists;
- manual external occupancy is respected;
- max two logical slots is enforced;
- semantic conflicts and dependencies fail closed;
- deterministic priority/capacity planning works;
- GitHub can execute the planner and publish durable evidence without a PC;
- a real `workflow_dispatch` can complete without launching workers/product flows.

However, Phase 2 must not be activated until its separate prerequisites are explicitly satisfied:

1. provision an OpenAI API key only in an approved GitHub Actions secret store; never put it in chat/task/report/Git;
2. perform a bounded security/permissions review of the exact Codex Action worker + trusted publisher boundary;
3. preserve GitHub as the single durable queue/state owner;
4. start with automatic `READ-ONLY / RECON` and `AUDIT` only, not autonomous IMPLEMENT;
5. keep the current manual Taste task external until it actually finishes or is deliberately migrated.

Those are Phase 2 prerequisites/user credential gates, not failures of Phase 1.

## 14. Unresolved

None for the Phase 1 definition of done.

The current shadow state is intentionally a repository snapshot, not yet an automatically reconciled live queue. Automatic intake/state mutation/worker leases belong to later orchestration phases and must not be retrofitted into this Phase 1 workflow.

## 15. Recommended next step

One bounded next task only: define and implement the **Phase 2 read-only RECON/AUDIT cloud-worker security/dispatch boundary**, including the OpenAI secret prerequisite and trusted report-publisher separation, without enabling autonomous product IMPLEMENT.
