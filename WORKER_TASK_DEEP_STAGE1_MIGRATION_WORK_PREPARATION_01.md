# WORKER TASK — Deep Stage 1 migration work preparation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `PREPARE / VALIDATE / NO SEMANTIC EXECUTION`

## Context

PR #176 established the bounded Deep cutover preflight and correctly stopped before semantic execution.

Current new Stage 1/Stage 2 semantic state is not sufficient for production cutover.
Do not redo the integration preflight from scratch.

## Goal

Prepare the exact GitHub-owned Stage 1 migration work needed to move current eligible products onto the new two-stage Deep model.

The output must be a real canonical migration work manifest/control-plane path, not merely a diagnostic audit list.

## Required

- use only current canonical one-stage Dossier evidence;
- compute the exact current eligible Deep scope from current production truth;
- classify current products into:
  - already valid under new Stage 1, if any;
  - requires new Stage 1 semantic analysis;
  - currently blocked/waiting because canonical Dossier evidence is unavailable/incompatible;
- legacy Deep numeric scores must never be copied or reinterpreted as new Stage 1 scores;
- preserve old results as history/audit only;
- prepare exact immutable Stage 1 work IDs, bindings, result paths and order for every currently authorized Stage 1 semantic item;
- make queue generation/reconciliation deterministic and GitHub-owned;
- dedupe against any accepted new Stage 1 results that may appear;
- local stale/bad item must not corrupt unrelated migration scope;
- do not create Stage 2 scores or bootstrap anchors in this task.

## Semantic boundary

Do NOT execute the Stage 1 semantic worker.

At completion, produce the exact short manual invocation instructions that a separate semantic worker will use against the generated canonical Stage 1 work manifest.

If current contracts require an explicit Director authorization flag before materializing executable Stage 1 migration work, implement the deterministic preparation/gate and stop at that exact boundary rather than bypassing it.

## Tests

Prove:
- exact current scope and Dossier binding;
- legacy scores never become Stage 1 results;
- deterministic/stable work IDs and ordering;
- accepted current Stage 1 state is not duplicated;
- stale/incompatible Dossier items are excluded/blocked honestly;
- no Stage 2 or ranking authority changes;
- current production Deep remains unchanged until later cutover;
- no dependency on the inactive Research/Assembly Dossier project.

## Boundaries

- Current canonical one-stage Dossier only.
- No semantic result invention.
- No Stage 1 semantic execution.
- No Stage 2 semantic execution or bootstrap.
- No production cutover.
- No Scheduled Task changes.
- No new dependency on the inactive two-stage Dossier.
- Do not modify Steam discovery, translations or unrelated site behavior.

## Deliverable

Report:
`reviews/worker_reports/deep-stage1-migration-work-preparation-01.md`

Create PR and stop.
