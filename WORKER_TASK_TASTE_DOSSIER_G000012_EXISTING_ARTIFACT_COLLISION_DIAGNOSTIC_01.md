# WORKER TASK — Taste Dossier g000012 Existing-Artifact Collision Diagnostic 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repo by default or the repo target is ambiguous, stop and switch to kentrap2011-hub/steam-kz-deals-2 before doing any work.

Task ID: taste-dossier-g000012-existing-artifact-collision-diagnostic-01
Mode: READ-ONLY / RECON
Worker slot: НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1

## START

First open the current `CHAT_PROTOCOL.md` from main and complete its START gate.

Then read the current canonical Dossier/control-plane contracts needed to classify the failure, including at minimum:
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current Dossier work/index/state artifacts on `main`
- accepted Dossier nonblocking / exact-items worker reports relevant to current persistence/recovery behavior
- `DIRECTOR_TASK_BOARD.md`

## Observed production incident

The Scheduled Dossier worker reported:

- publication of `g000012` stopped fail-closed;
- GitHub create-only returned HTTP 422 because the deterministic path already existed and updating it would require the existing blob SHA;
- overwrite, alternate filename and skipping to g000013 were correctly refused;
- no new files were created in that invocation;
- the worker stated that g000012 now requires GitHub-owned validation/drain/recovery;
- the worker also stated that the recurring task was stopped/disabled to avoid retrying the blocked write.

The create-only refusal is expected fail-closed behavior. The cause of the pre-existing deterministic artifact is NOT yet established.

Important ownership note: a Scheduled semantic worker may stop its current invocation, but it does not own Scheduled Task enable/disable/reschedule settings. Determine whether the reported wording reflects an actual scheduler mutation or merely invocation stop if repository/platform evidence permits; do not speculate if not observable.

## Goal

Prove the exact root cause of the g000012 deterministic-path collision and identify the smallest owning recovery/fix without mutating production state.

Do not repair the artifact in this task.

## Required investigation

Prove, with exact refs where observable:

1. The exact failing invocation's Dossier snapshot/source binding and exact work/index identity.
2. The exact immutable `g000012` descriptor from that invocation:
   - sequence/group id;
   - appids/items;
   - item/group hashes;
   - snapshot/binding fields.
3. The exact deterministic repository submission path the worker attempted to create.
4. The exact existing artifact already present at that path:
   - blob/commit identity;
   - when/how it first appeared if history exposes it;
   - its embedded snapshot/group/item identity.
5. Whether the existing artifact belongs to:
   - the same current snapshot and exact same immutable group;
   - an older snapshot/rebuild;
   - another incompatible descriptor;
   - or cannot be established.
6. Whether canonical GitHub ingest/validation ever observed that existing artifact. If yes, state its exact classification/receipt/quarantine/persistence outcome. If no, establish the narrowest observable boundary explaining why it remained at the create-only path.
7. Historical canonical state for that g000012 identity under the snapshot that created the existing artifact.
8. Why the current worker was still authorized/projected to create that deterministic path even though it already existed.
9. Specifically test whether the deterministic submission pathname/identity is insufficiently snapshot/group-content scoped and can therefore collide across legitimate snapshot changes or regeneration.
10. Test whether the GitHub-owned normal ingest/drain/quarantine/recovery path should have removed or rendered the existing artifact inert before a later normal worker invocation.
11. Determine whether the current/fresh snapshot's future g000012 will deterministically hit the same collision if no recovery/fix occurs.
12. Record current fresh Dossier state at report time:
    - snapshot/binding;
    - accepted/failed/pending group and dossier counts;
    - current next pending sequence;
    - current g000012 status.
13. Classify the defect into one or more owning layers:
    - deterministic candidate-path identity;
    - stale-work/liveness;
    - GitHub ingest/drain;
    - failed-group recovery;
    - snapshot regeneration/rebinding;
    - worker behavior;
    - other proven layer.
14. Confirm whether the worker's create-only refusal itself was correct.
15. Confirm scheduler ownership: worker self-disable/reschedule is forbidden; if an actual scheduler mutation cannot be proven from repository evidence, state that explicitly rather than assuming it occurred.
16. Identify the smallest safe recovery for the already-existing g000012 artifact and the smallest durable fix that prevents recurrence. Do not execute either.
17. State whether Dossier normal traversal may safely continue before reaching g000012, and what exact condition must be satisfied before another attempt on g000012.
18. Confirm whether this incident affects already-canonically-accepted Dossiers used by Deep, or only forward Dossier progress.
19. Commit and reread the durable report from `main` before completion.

## Hard guards

READ-ONLY diagnosis only.

Do NOT:
- delete, overwrite, rename, move or recreate the existing g000012 artifact;
- create an alternate candidate filename;
- skip/rebind g000012 manually;
- mutate Dossier group/progress/recovery state;
- run or dispatch Dossier ingest/recovery;
- press or cause `Run now`;
- enable/disable/edit/create any Scheduled Task;
- alter Fast/PASS 1 or Deep/PASS 2 state;
- modify the active Deep activation task/PR;
- change contracts/runtime/code in this diagnostic;
- infer a root cause from HTTP 422 alone.

## Durable report

Create and commit:

`reviews/worker_reports/taste-dossier-g000012-existing-artifact-collision-diagnostic-01.md`

Keep it compact and include:
- exact incident identity;
- exact existing-path/artifact evidence;
- same-snapshot vs cross-snapshot determination;
- ingest/drain/recovery history;
- exact root cause and owning layer;
- scheduler-ownership finding;
- current canonical Dossier state;
- impact on Deep / accepted Dossiers;
- smallest safe one-off recovery;
- smallest durable recurrence fix;
- exact refs;
- final status;
- exactly one recommended next step.

Allowed statuses:
- complete_root_cause_proven
- blocked_insufficient_evidence
- needs_fix
- needs_user_decision

Before final response, commit the report and reread the exact report from main.
