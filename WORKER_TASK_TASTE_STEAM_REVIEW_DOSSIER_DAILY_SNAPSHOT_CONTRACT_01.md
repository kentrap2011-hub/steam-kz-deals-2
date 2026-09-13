# WORKER TASK — Taste Steam review dossier daily snapshot contract 01

Task ID: `taste-steam-review-dossier-daily-snapshot-contract-01`

Status: `authorized_ready_for_worker`

Mode: `IMPLEMENT`

## Goal

Complete only the canonical contract/rationale part of the user-approved daily full-backlog dossier architecture.

This is intentionally a small phase split from `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` because two worker sessions exhausted context before implementation. Do not implement runtime/workflow changes in this phase.

## User-approved target architecture

- GitHub once per day prepares one fixed full dossier backlog snapshot from the current eligible Taste queue.
- The existing `Taste Steam Review Dossier` Scheduled Task processes that prepared snapshot from start to finish.
- Checkpoint size 10 is only a persistence/runtime boundary, never a scope/quota boundary.
- GitHub does not rebuild scope merely to reveal the next 10 after each checkpoint.
- `Run now` consumes the latest already-prepared daily snapshot; it does not require on-demand GitHub scope refresh.
- New source changes after preparation may wait until the next daily preparation.
- GitHub remains scope/order/freshness/completeness owner; ChatGPT cannot add items outside the prepared snapshot.
- `Taste Semantic Producer` and its limits remain unchanged.

## Mandatory START

Follow `CHAT_PROTOCOL.md` START gate.

Read only the minimal files needed for this contract phase:
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- relevant existing Taste dossier entry in `PROJECT_DECISIONS.md`;
- relevant existing Taste dossier entry in `PROJECT_ROUTES.md` if one exists;
- parent task `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_CONTROL_PLANE_REFRESH_01.md` only as scope reference.

Do not inspect runtime scripts/workflows except one bounded lookup if needed to avoid writing a contract impossible to map to current ownership.

Do not perform broad repo search.

## Required changes

Reconcile canonical documentation/contracts so they explicitly authorize and describe the fixed daily full-backlog snapshot model.

At minimum ensure canonical state says:
1. daily preparation scope is the full eligible dossier backlog for that preparation snapshot, not only the next checkpoint;
2. snapshot identity/provenance is fixed for the prepared day/run until completion;
3. checkpoint 10 is durability only and does not mutate scope;
4. completed checkpoint progress is persisted against the same prepared snapshot;
5. completion means zero remaining items in that prepared snapshot;
6. `Run now` uses the latest prepared snapshot and does not force an immediate scope rebuild;
7. later source-queue changes are picked up by the next daily preparation, not injected into an in-flight snapshot;
8. GitHub remains control-plane owner and ChatGPT cannot independently derive/expand scope;
9. fresh dossier reuse / stale+missing inclusion / default TTL 20 days remain unchanged;
10. downstream exact Taste semantic pin remains separate and unchanged.

Update `PROJECT_DECISIONS.md` with concise durable rationale explaining why the old next-checkpoint/rebuild-after-each-checkpoint model was replaced.

Update `PROJECT_ROUTES.md` only if an existing route would otherwise direct future workers toward the superseded model.

## Prohibitions

Do not:
- change runtime scripts;
- change GitHub Actions workflows;
- change either Scheduled Task;
- run production backlog;
- run Taste throughput measurement;
- change production limits;
- perform age-priority work;
- create a new scheduler/queue/backlog manager.

## Validation

Perform only bounded contract consistency checks:
- no remaining canonical statement in the touched dossier contract/rationale contradicts the fixed daily snapshot model;
- execution ownership still assigns scope/queue/completeness to GitHub;
- downstream Taste semantic pin ownership remains unchanged.

No runtime regression matrix is required in this phase.

## CURRENT_TASK.md

Update only if required by `CHAT_PROTOCOL.md` for truthful handoff. Do not erase unrelated active work.

## Durable report

Write:
`reviews/worker_reports/taste-steam-review-dossier-daily-snapshot-contract-01.md`

Report must contain:
- exact canonical conflict found;
- files changed;
- concise final contract semantics;
- validation performed;
- unresolved items (runtime implementation is expected and should be named as the next phase, not treated as a blocker);
- exact commit refs.

## Allowed final statuses

- `complete_contract_ready_for_runtime_implementation`
- `needs_user_decision`
- `blocked`

Do not report `blocked` without a concrete verified blocker.

## Expected next step

After Director accepts this contract phase, create a separate narrow runtime/workflow implementation task that implements exactly this approved contract and its focused regressions.
