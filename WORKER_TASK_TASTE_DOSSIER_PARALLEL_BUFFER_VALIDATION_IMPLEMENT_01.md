# WORKER TASK — Taste Dossier Parallel Buffer Validation Implement 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-parallel-buffer-validation-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## Product decision / target behavior

The pre-publication Python requirement introduced in PR #36 is not compatible with the real Scheduled ChatGPT runtime and must not remain the worker gate.

The desired architecture is instead:

1. Scheduled ChatGPT researches canonical groups of **3 games** and publishes immutable create-only **candidate buffer artifacts** without waiting for GitHub validation.
2. GitHub validates those candidate artifacts asynchronously with the canonical strict validator.
3. GitHub accepts/persists only the **maximal contiguous prefix** of valid groups beginning at the canonical expected sequence.
4. If group `N` is invalid, canonical progress stops at `N`.
5. Valid groups after `N` may already exist in the buffer, but remain buffered and are not promoted across the gap.
6. Scheduled ChatGPT may continue researching/publishing later predeclared groups while GitHub validation lags or while canonical expected sequence has not yet advanced, as long as snapshot/plan/binding liveness remains unchanged.
7. Do **not** split groups into per-game acceptance or per-game retry state. Group size remains `3` and a group is the acceptance unit.
8. Do **not** design automated self-healing/retry logic for invalid semantic groups. An invalid group means the system is not yet production-ready; the contract/prompt/validator should be fixed, a new compatible snapshot created, and old buffered artifacts made stale/quarantined through the normal binding mechanism.

This is intentionally a simple producer-buffer-validator pipeline, not a synchronous request/response protocol.

## Why this task exists

The latest live run against snapshot `057b53265eb1238ec4543a355ba22ef769b5ea2638e9e1c5276a9c01d972605f` stopped fail-closed before research because the worker prompt required executing:

`python scripts/taste_steam_review_dossier_prepublication.py --artifact ...`

The Scheduled ChatGPT runtime has GitHub access but no permitted mechanism to execute repository Python. It correctly returned:

- `prepublication_validator_unavailable`
- artifacts published: `0`
- canonical progress claimed: `0`

This was safe, but it makes the current production path unusable. The Python validator itself is fine; it belongs on the GitHub side, where it can execute.

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully, then read at minimum:

- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- relevant `CURRENT_TASK.md` state;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md` for active Taste dossier ownership/buffering/validation decisions;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-dossier-prepublication-recovery-implement-01.md`;
- `reviews/worker_reports/taste-dossier-contract-gaps-implement-01.md`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-03.md`;
- active worker prompt, schema, web-evidence contract and parent dossier contract;
- buffered submission/ingestion/drain implementation;
- GitHub workflows that react to create-only candidate artifacts;
- current worker index/group descriptor liveness rules.

Run architecture preflight before implementation.

## Architecture invariants

Must remain true:

1. GitHub owns canonical scope, order, snapshot identity, group plan, validation, canonical persistence, progress, recovery and completeness.
2. Scheduled ChatGPT owns only bounded research/synthesis and create-only publication of candidate buffer artifacts.
3. No second scheduler, queue, retry manager, backlog manager or external service is introduced.
4. Candidate transport artifacts remain immutable/create-only.
5. Canonical progress remains fail-closed and contiguous.
6. Group size remains exactly `3` except the natural final tail group.
7. Existing strict evidence, privacy/content, temporal, item-identity, Russian-evidence, conflict and compatibility guards remain active.
8. Package-member/DLC identity behavior remains unchanged.
9. Downstream Taste-fit/ranking/pricing/commercial logic remains unchanged.

If the requested behavior cannot be implemented inside these boundaries, STOP and report `blocked` rather than inventing another control plane.

## Required change A — remove synchronous pre-publication execution from Scheduled ChatGPT

Remove the requirement that Scheduled ChatGPT execute repository Python or any repository-local validator before create-only publication.

Required worker behavior:

- research/synthesize a complete canonical group according to the active contract;
- publish the candidate group to the deterministic create-only buffer/inbox path;
- do **not** require `python scripts/taste_steam_review_dossier_prepublication.py` or any equivalent local execution;
- do **not** substitute a handwritten/manual validator inside the prompt;
- do not claim canonical acceptance after publication;
- publication means only `candidate buffered`, never `accepted`;
- if the GitHub create-only write itself fails, stop on transport failure as before.

The existing repository pre-publication script may remain as a CI/developer/testing utility if useful, but it must no longer be a runtime prerequisite for Scheduled ChatGPT.

## Required change B — worker must not wait for canonical validation between groups

The Scheduled worker should be allowed to continue to later **already-declared canonical group descriptors** within the same invocation while GitHub validation/ingestion is still pending.

Required liveness semantics:

- after publishing group `N`, re-check only the bindings needed to prove the same snapshot/group plan/compatibility contract is still active;
- canonical `expected_sequence` is allowed to lag behind the worker's most recently buffered sequence because validation is asynchronous;
- do not require `expected_sequence == N+1` before researching/publishing group `N+1`;
- do not stop merely because group `N` has not yet been canonically accepted;
- do not skip descriptor order;
- do not invent groups outside the immutable plan;
- stop if snapshot id, group-plan hash, compatibility binding or other true liveness binding changes;
- stop on transport failure or ordinary invocation/time limit.

This is parallel buffering, not speculative reordering.

## Required change C — GitHub remains the only acceptance gate

Candidate artifacts must be validated asynchronously by GitHub using the active canonical strict/buffered validation path.

Required behavior:

- strict validation happens before canonical persistence/progress advancement;
- GitHub drains only the maximal contiguous prefix starting at canonical expected sequence;
- if group `N` is invalid, canonical progress does not cross `N`;
- later valid groups remain in the buffer/inbox and are not promoted across `N`;
- no partial acceptance inside a 3-item group;
- no automatic semantic repair or retry is introduced;
- no alternate corrected filename is created automatically for the same group/snapshot;
- a future contract/prompt fix should create a new compatibility binding/snapshot, after which old buffered artifacts become stale/inert/quarantined via the existing normal mechanism.

Do not weaken strict validation to improve throughput.

## Required change D — minimal durable validation status, only if not already available

The user wants GitHub to be able to indicate that a buffered group is wrong while leaving later buffered work untouched.

First inspect the current GitHub-owned ingestion/drain outputs.

- If the repository already has a durable, machine-readable way to distinguish `pending`, `accepted`, and `invalid expected group` (for example via an existing receipt/state/quarantine record), reuse it and do not add another status layer.
- If no durable machine-readable invalid marker exists, add the **smallest GitHub-owned validation receipt/status** needed to record that a specific candidate group failed strict validation and why.

Constraints for any added marker:

- it is observational state, not a retry queue;
- it does not let later groups advance across the invalid group;
- it does not mutate the candidate artifact;
- it does not trigger automated semantic repair;
- it is bound to snapshot id + group sequence + group hash + compatibility binding;
- a new snapshot naturally supersedes it.

Do not add per-game error state.

## Required change E — preserve the existing error philosophy

Do not design around the assumption that semantic errors are expected forever.

The intended production philosophy is:

- buffer/validation runs fast and independently;
- any invalid group discovered during acceptance means the system still needs improvement;
- canonical data remains protected;
- buffered later work may exist, but production readiness is not declared until a live run validates cleanly;
- fixes are made at the system contract/prompt/validator level, not through an automated retry/healing subsystem.

This philosophy should be reflected in comments/docs/report, but do not add runtime complexity merely to encode it.

## Deterministic regressions required

Add/adjust focused regressions proving at least:

1. Scheduled-worker contract no longer requires repository Python/pre-publication execution before candidate publication.
2. A worker can publish group 1, then group 2 and group 3 while canonical expected sequence still remains 1, provided snapshot/plan/binding liveness is unchanged.
3. Groups must still be published in descriptor order; no skipping/reordering.
4. GitHub validates candidate group 1 and advances only if valid.
5. If group 2 is invalid while groups 3 and 4 are already buffered, canonical state accepts group 1 only, stops at group 2, and leaves groups 3/4 buffered/unpromoted.
6. A valid later group cannot cross an invalid earlier group.
7. No partial per-game acceptance occurs inside an invalid group of 3.
8. Candidate artifacts remain create-only/immutable.
9. On compatibility/snapshot change, old buffered artifacts cannot satisfy the new plan and follow existing stale/quarantine behavior.
10. Existing evidence-guard, privacy/content, recency, alias/item-identity, Russian, conflict, compatibility-binding, package-member and recovery regressions remain green.
11. Group size remains 3.

If a durable invalid receipt/status already exists, add a regression showing it records the invalid group without changing canonical progress. If a new minimal receipt is added, regression-test that exact behavior.

## Migration / activation

This task changes worker runtime semantics and likely worker prompt content/binding, so use the existing content-complete compatibility mechanism from PR #38.

Requirements:

- let the normal GitHub-owned rebuild create a fresh snapshot/binding if prompt/contract content changes;
- no manual queue/cache/progress/receipt edits;
- no manual dossier artifact creation;
- no Scheduled Task `Run now` during implementation;
- old incompatible candidate artifacts must be stale/inert under the new binding;
- fresh canonical state should have truthful progress and group size 3.

## PR / CI / activation

Use normal worker branch -> PR -> canonical CI -> merge path.

After merge:

- observe the automatic GitHub-owned pre-AI activation;
- confirm the fresh snapshot/index/group descriptors carry the new binding;
- confirm group size 3;
- confirm canonical expected sequence/progress are truthful;
- confirm the Scheduled worker prompt no longer contains the blocking Python requirement;
- do not run the Scheduled Task.

## Prohibitions

Do not:

- split 3-item groups into per-game acceptance;
- add per-game retry/status logic;
- add automated semantic retry/healing;
- run Scheduled Task `Run now`;
- require Scheduled ChatGPT to execute Python/shell/CI;
- weaken canonical strict validation;
- change group size away from 3;
- store raw review bodies/usernames/profiles/excerpts;
- change downstream Taste/ranking/pricing/commercial behavior;
- create another queue/control plane/external service;
- use any other repository.

## Definition of Done

Complete only when:

- Scheduled ChatGPT can publish candidate groups without local repository execution;
- worker can continue buffering later planned groups while GitHub validation lags;
- GitHub alone decides canonical acceptance;
- maximal contiguous-prefix behavior is proven with a middle invalid group and later buffered valid groups;
- no per-game split/retry architecture is introduced;
- existing strict evidence protections remain green;
- compatibility migration/fresh snapshot is activated normally;
- group size remains 3;
- no Scheduled Task live run occurred;
- durable report is in `main`.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `blocked`

## Durable report

Publish to `main`:

`reviews/worker_reports/taste-dossier-parallel-buffer-validation-implement-01.md`

Report must include:

- architecture preflight;
- exact old synchronous behavior removed;
- exact new worker buffering/liveness semantics;
- exact GitHub validation/drain semantics;
- whether existing validation status was reused or a minimal receipt was added;
- proof invalid group blocks canonical progress while later groups stay buffered;
- proof no per-game split/retry was introduced;
- PR/merge/CI refs;
- fresh snapshot id, counts, expected sequence and first group descriptor after activation;
- proof group size remains 3;
- confirmation no Scheduled Task `Run now` occurred;
- remaining risks;
- exactly one next step.

On success, the one next step should be: run the existing Scheduled Task exactly once and perform a separate READ/VALIDATE live acceptance of parallel buffering plus GitHub contiguous-prefix validation.

Ensure the durable report is in `main` before completion. Stop after report publication.