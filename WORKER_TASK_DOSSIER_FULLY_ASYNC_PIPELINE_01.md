# WORKER TASK — Dossier fully asynchronous Research → Assembly pipeline 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `ARCHITECTURE AMEND / IMPLEMENT INACTIVE / VALIDATE`

## User decision

Neither semantic stage may wait for GitHub.

This supersedes the remaining backpressure / accepted-Research handoff semantics from PR #177.

Research must not wait for GitHub after each item.
Assembly must not wait for GitHub acceptance of Research before it can work on the same pre-authorized item.
A fixed unresolved-slot cap such as 8 must not stop either semantic worker because GitHub ingest is behind.

GitHub remains final authority for bindings, validation, canonical acceptance, retry/recovery and publication, but it is not in the semantic workers' liveness path.

## Target model

GitHub pre-authorizes the exact item scope/bindings for the pipeline.

For each item:
1. Research consumes the pre-authorized binding and emits a create-only immutable Research package.
2. Assembly may consume that exact submitted Research package directly under the same frozen item binding, without waiting for a GitHub acceptance receipt.
3. Assembly emits a create-only Dossier candidate.
4. GitHub asynchronously validates the full chain:
   - authorization/binding;
   - Research package;
   - Assembly use of the exact Research package;
   - final strict Dossier candidate.
5. Only after GitHub validation may anything become canonical Dossier truth or Deep-ready.

If Research A is invalid, Research B/C and Assembly B/C keep running.
If Assembly A is invalid, unrelated items keep running.
A invalidates/quarantines only A's chain.

## Required changes

Amend inactive contracts/helpers from PRs #171/#173/#175/#177 so that:

- remove fixed `max_open_slots_per_phase=8` as a semantic-worker liveness gate;
- no unresolved-slot count may force an already-running Research or Assembly semantic worker to wait for GitHub;
- remove `Research GitHub accepted` as a prerequisite for Assembly semantic execution;
- replace it with exact preauthorization + immutable Research transport provenance;
- Assembly must bind to the exact Research package bytes/blob/hash/transport identity it consumed;
- final GitHub validation must reject the entire item chain if upstream Research later fails;
- no invalid Research/Assembly chain may become canonical Dossier or Deep-ready;
- retries/recovery remain GitHub-only explicit new authorizations;
- workers cannot invent/reorder/expand scope.

Design safe bounded resource behavior without semantic blocking:
- limits may control how much NEW work GitHub preauthorizes in a future invocation;
- limits may not pause a worker in the middle of already-preauthorized work waiting for GitHub acknowledgement;
- do not introduce unbounded canonical writes or a second queue owner.

## Required tests

Prove at minimum:
- Research A submitted/unaccepted does not block Research B/C.
- Assembly A can consume exact submitted Research A without GitHub acceptance receipt.
- Assembly B/C can continue while GitHub has not validated A.
- Research A later rejected => Assembly A chain cannot become canonical, but B/C remain valid/processable.
- Assembly A rejected => B/C unaffected.
- no fixed open-slot cap stops traversal of already-preauthorized work.
- exact Research bytes/hash consumed by Assembly are immutable and verified later by GitHub.
- stale/mismatched/replayed/tampered chain fails closed for that item only.
- retry/recovery cannot be worker-invented.
- current one-stage production Dossier remains unchanged.
- all new two-stage contracts remain inactive/non-authoritative.

## Boundaries

- No semantic Research worker implementation.
- No semantic Assembly worker implementation.
- No production activation/cutover.
- No changes to current one-stage Dossier authority.
- No weakening of final strict Dossier validator.
- No Deep/ranking/Steam/translation/UI/commercial refresh changes.
- No Scheduled Tasks or automations.

## Deliverable

Report:
`reviews/worker_reports/dossier-fully-async-pipeline-01.md`

Create PR and stop.
