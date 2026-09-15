# WORKER TASK — Taste Dossier Full Defect Sweep 01

Task ID: `taste-dossier-full-defect-sweep-01`
Mode: `READ-ONLY / RECON`

## Goal
Perform a broad, end-to-end, read-only defect sweep of the Steam review dossier production path so we stop discovering predictable contract/runtime defects one live run at a time.

Do **not** stop after the first defect. Continue through every accessible layer and return one consolidated defect inventory, with severity, proof, affected surface, and recommended fix grouping.

This task is intentionally wider than the previous one-defect investigations, but it is still bounded to the Steam review dossier pipeline. Do not modify Taste Semantic Producer.

## Why this task exists
The latest live compact acceptance proved:
- compact index/descriptor reading works;
- one invocation can publish group N and N+1 without waiting for canonical acceptance N;
- GitHub correctly failed closed because a generated dossier used unsupported observation category `content`.

The immediate concern is that `content` may be only the first of several predictable incompatibilities between what the Scheduled Task can generate and what the canonical validator accepts. We want to surface those now, before another live `Run now`.

## START gate
Read fully before analysis:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-worker-view-recon-01.md`
- `reviews/worker_reports/taste-dossier-worker-view-implement-01.md`
- `reviews/worker_reports/taste-dossier-live-compact-acceptance-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-acceptance-02.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current canonical work manifest
- current compact worker index
- current group descriptors
- current dossier inbox artifacts, especially published groups 1 and 2
- canonical dossier validator/runtime code
- buffered submission/drain code
- relevant build/ingest workflows
- relevant existing dossier tests.

Read `PROJECT_ROUTES.md` before broad search where protocol requires it.
Run architecture preflight before making any recommendation that would alter ownership/control-plane behavior.

## Core instruction: full sweep, not first-error debugging
Do not stop when one invalid field is found.

For every existing published dossier artifact that can be inspected, validate the **entire payload** and enumerate **all detectable violations**, including violations after the first one the production validator currently reports.

Then continue to static contract/prompt/runtime analysis to identify additional defects that have not yet appeared in production but are reasonably predictable from mismatched schemas, enums, requirements, assumptions, or workflow state transitions.

The purpose is to produce a repair batch, not another single-defect diagnosis.

## Sweep areas

### A. Generated dossier payload vs canonical validator
Build a field-by-field compatibility matrix between what the repository worker prompt instructs/allows the Scheduled Task to generate and what the canonical validator actually accepts.

Check at minimum:
- every required top-level field;
- types;
- nullability;
- min/max counts;
- enum values;
- observation categories;
- strength/confidence/recurrence fields;
- localization fields;
- review-count/source/provenance fields;
- timestamps/date/TTL formatting;
- appid/title identity;
- strings vs arrays vs objects;
- duplicate/empty observations;
- any normalization/casing requirements;
- unknown/additional-field behavior if relevant;
- hash/serialization assumptions where payload content participates.

Explicitly search for every validator enum/allowed-value set and compare it with wording/examples in the worker prompt. `content` is one known mismatch; look for all others.

### B. Exhaustive validation of current groups 1 and 2
The latest live run published deterministic buffered artifacts for groups 1 and 2 and GitHub stopped at group 1.

Independently inspect/validate **every dossier in both group artifacts** and produce a complete per-dossier violation inventory. Do not infer that group 2 is valid merely because canonical drain never reached it.

If existing production validator stops at the first failure, use bounded read-only/local analysis to continue validation against the same canonical rules. Do not change production code to do this.

Classify findings as:
- definitely invalid under current canonical contract;
- suspicious/underspecified but not proven invalid;
- valid.

### C. Prompt underspecification / hallucination risk
Audit whether the worker prompt gives the model enough exact instructions to stay inside canonical schema without improvising.

Look for:
- free-form category naming where an enum is required;
- ambiguous field meanings;
- missing allowed-value lists;
- examples that contradict validator rules;
- fields the model is told to produce but not enough source evidence exists to support;
- fields validator requires but prompt does not clearly require;
- terminology mismatches between contract, bridge, prompt and validator.

Recommend deterministic prompt/schema guards where appropriate, but do not implement.

### D. Evidence-availability / source-surface failures
The live worker began group 3 but stopped because available Steam/web evidence was insufficient for all planned items.

Determine whether this is:
- expected fail-closed behavior for rare games;
- a predictable systematic blocker for part of the backlog;
- caused by overly strict dossier requirements;
- caused by prompt/source strategy gaps;
- likely to strand canonical expected groups permanently.

Inspect enough current descriptors/backlog metadata to estimate whether more groups are likely to hit the same problem. Do not browse all 594 games manually if a bounded representative method can answer the question.

Identify what production behavior should be for genuinely insufficient evidence: valid sparse dossier, explicit no-evidence state, stop, skip forbidden, etc., according to current contract. Flag any missing contract semantics.

### E. Buffered transport / retry / recovery state
Audit current state after the rejected acceptance:
- groups 1 and 2 artifacts remain in inbox;
- canonical expected sequence remains 1;
- worker must not overwrite/create alternate retry artifacts.

Determine the exact safe recovery requirement before another live run.

Check for future deadlocks around:
- invalid expected artifact already exists;
- corrected payload needing same deterministic path;
- create-only semantics;
- replay handling;
- deletion/replacement ownership;
- how a fixed worker is supposed to recover without violating transport immutability.

If current contract has no safe recovery path for an invalid already-published deterministic artifact, classify that as a separate blocker rather than hiding it under the `content` defect.

### F. Compact traversal and canonical progress interaction
Audit edge cases now that compact traversal works:
- canonical expected sequence advances while worker is locally on N+1/N+2;
- multiple GitHub drain runs wake from sequential commits;
- index rereads during fast progress;
- index reaches beyond local next sequence;
- snapshot rolls over mid-invocation;
- descriptor missing/stale;
- final partial group;
- complete snapshot;
- restarted worker with existing pending artifacts;
- group N valid, N+1 invalid, N+2 already published;
- cleanup after maximal contiguous prefix.

Use existing tests/code and current contract. Identify missing regression coverage even if no current defect is proven.

### G. Workflow / serialization / trigger audit
Check dossier-specific workflows for predictable issues:
- canonical-writer concurrency consistency;
- staging of manifest/index/descriptors/inbox/cache;
- path triggers;
- self-trigger loops;
- races between worker publication commits and ingest commits;
- automatic pre-AI refresh interaction with pending inbox artifacts;
- same-day preservation;
- daily rollover with pending old-snapshot groups;
- failure before canonical commit;
- cleanup behavior.

Do not broaden into unrelated repository workflows.

### H. Tests vs production contract coverage
Map current tests against the defects/edge cases above.

Identify which important contract properties currently lack automated regression tests, especially anything that could have caught the `content` mismatch before live acceptance.

Prefer recommendations that move foreseeable failures into deterministic CI rather than discovering them via Scheduled Task.

## Required defect inventory format
For each finding assign an ID like `DOSSIER-SWEEP-001` and include:
- severity: blocker / high / medium / low;
- status: proven current defect / latent contract mismatch / missing coverage / expected behavior;
- affected layer;
- exact evidence;
- user-visible/runtime consequence;
- whether it blocks the next live acceptance;
- recommended fix scope;
- whether it can be fixed together with other findings in one IMPLEMENT batch.

Separate **proven defects** from speculative hardening. Do not inflate the list with theoretical issues unsupported by current code/contract evidence.

## Repair-batch recommendation
At the end, group compatible proven defects into the smallest sensible number of IMPLEMENT batches.

The preferred outcome is one bounded IMPLEMENT batch that fixes all currently proven pre-live blockers plus adds regression coverage for the latent mismatches that can reasonably be tested.

Do not recommend one task per tiny enum error unless there is a real architectural reason to separate them.

If a finding requires an architecture/ownership change, separate it from ordinary validation/prompt fixes and run architecture preflight on that recommendation.

## Production/live prohibitions
- READ-ONLY / RECON only.
- No repository runtime/config/code changes.
- No Scheduled Task UI inspection or edit.
- No `Run now`.
- No manual GitHub workflow dispatch.
- No production artifact deletion/replacement.
- No synthetic production writes.
- No branch/probe/temp-file creation for tooling experiments.
- No Taste Semantic Producer changes.

Local ephemeral analysis and running existing read-only tests/validators is allowed if it does not mutate repository/production state.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`

The report must include:
- architecture preflight;
- scope/methodology;
- complete validation result for every dossier in current groups 1 and 2;
- prompt-vs-validator compatibility matrix;
- evidence-availability findings;
- current invalid-inbox recovery analysis;
- compact traversal edge-case audit;
- workflow/concurrency audit;
- automated-test coverage gaps;
- prioritized defect inventory with IDs;
- one consolidated repair-batch proposal;
- explicit list of what must be fixed before the next live `Run now`;
- explicit list of nonblocking hardening items;
- one next step only.

Allowed final statuses:
- `sweep_complete_repair_batch_ready`
- `blocked`
- `no_additional_defects_found`

Do not stop at the known `content` error. Continue the full sweep and only then write the report.