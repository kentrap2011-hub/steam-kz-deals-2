# WORKER TASK — Taste Dossier Non-Review Defect Repair 01

Task ID: `taste-dossier-non-review-defect-repair-01`
Mode: `IMPLEMENT`

## Goal
In parallel with the separate Steam review-source RECON, fix every currently proven Steam dossier defect that does **not** depend on choosing how actual Steam review bodies will be retrieved.

This task exists so the review-source investigation does not block independent correctness/recovery work.

Do not solve, redesign, or guess the review-body acquisition mechanism here. Leave source-specific evidence semantics for the dedicated review-source task and its later follow-up.

## Parallel-work boundary
Another independent worker is currently investigating:
`taste-dossier-review-source-recon-01`

That worker owns only the question: **where/how production obtains actual Steam review bodies**.

This task owns independent defects from `taste-dossier-full-defect-sweep-01`, especially schema exactness, validator strictness, buffer recovery/lifecycle, and CI coverage that do not require the review-source decision.

Do not edit or replace the other worker's report/task.

## START gate
Read fully before writes:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`
- `reviews/worker_reports/taste-dossier-live-compact-acceptance-01.md`
- `reviews/worker_reports/taste-dossier-worker-view-implement-01.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current dossier validator/runtime, buffered transport/drain, inbox adapter, daily builder, compact projection, relevant workflows/tests.

Read `PROJECT_ROUTES.md` before broad search if required by protocol.
Perform architecture preflight before runtime/workflow/recovery changes.

## What MUST be fixed in this task

### 1. Exact worker-facing dossier schema and enum closure — source-independent part
Create one compact machine-readable canonical dossier schema/contract surface that can be read by the Scheduled Task and regression-tested against the canonical validator.

It must eliminate hidden worker-facing rules for all fields whose meaning does not depend on the review-source decision, including at minimum:
- schema id/version;
- exact required top-level fields;
- exact JSON types and nullability;
- observation category enum;
- sentiment enum;
- recurrence enum;
- evidence_languages enum as it exists under the current contract;
- mention_count type/rules that are already canonically decided;
- timestamp/TTL serialization rules;
- appid/title requirements;
- provenance structural fields already required independently of which review source is eventually selected;
- unknown/additional-field policy where the existing canonical contract already determines it.

The repository worker prompt must point to/read the exact compact schema rather than rely on prose to invent enum values.

At minimum the live `category:"content"` failure must become impossible under an exact worker-facing enum and must be covered by CI.

Do **not** finalize new semantics for source-access-unavailable, minimum review counts, review-body provenance fields, or new evidence states in this task; those depend on the review-source RECON.

If any schema choice cannot be made without that review-source decision, leave that specific part unchanged and document it as intentionally deferred. Do not guess.

### 2. Canonical validator strictness — source-independent proven gaps
Fix all proven validator defects from FDS-04 that do not require review-source policy, including where technically applicable:
- reject JSON bool where integer is intended (`schema_version`, counts, mention_count, etc.);
- bind dossier title to the exact descriptor item title during buffered validation;
- require exact lane cardinality/identity rather than allowing duplicate lane objects through set-only checks;
- reconcile lane-level sampled counts with top-level Russian/non-Russian/total counts where the existing fields already define that invariant;
- reject duplicate observations when exact duplicates add no valid semantic value;
- enforce generated/expires/TTL consistency using strict types;
- reject future-generated dossier at canonical ingest/persistence using the existing freshness model;
- strengthen appid/type identity checks;
- bind Steam/store provenance URLs to the dossier appid where this can be done independently of the future review-source mechanism;
- require structural provenance fields already mandated by the current contract.

Do not invent a new review evidence policy. Structural consistency can be fixed now; source sufficiency is deferred.

For additional/unknown fields: enforce a strict policy only if the existing contract already authorizes one. If not, preserve behavior and record the unresolved policy rather than making a new architecture/product decision.

### 3. GitHub-owned invalid deterministic artifact recovery mechanism
Implement a safe GitHub-control-plane recovery path for a validator-proven invalid deterministic expected inbox artifact.

Required properties:
- GitHub remains sole recovery owner;
- Scheduled ChatGPT never gains overwrite/delete/rename/retry authority;
- no alternate retry filenames;
- recovery may quarantine/remove only an artifact that GitHub has proven invalid under canonical validation;
- after recovery, the same deterministic path may be created again by a future corrected worker publication;
- later pending groups remain intact and blocked until canonical contiguous order permits them;
- recovery cannot itself advance canonical progress;
- recovery actions are serialized under the existing canonical writer boundary;
- auditability/durable evidence must exist for what was recovered and why.

IMPORTANT CURRENT-PRODUCTION BOUNDARY:
Implement and test the mechanism, but **do not use it yet to delete/quarantine/replace the current production g1/g2 artifacts**. Their replacement payload requirements may change after the review-source RECON. Current g1/g2 stay untouched until a later coordinated recovery task.

### 4. Stale inbox cleanup on snapshot rollover
Implement bounded GitHub-owned cleanup/quarantine of old-snapshot dossier inbox artifacts when a new canonical daily snapshot becomes active.

Requirements:
- old snapshot artifacts must not accumulate indefinitely in the current tree;
- current-snapshot pending artifacts must not be deleted accidentally;
- cleanup must not advance progress;
- same-day preservation must not treat current-snapshot artifacts as stale;
- cleanup belongs to GitHub, not ChatGPT.

### 5. Lost-wakeup reconciliation
Implement a GitHub-owned way to re-evaluate an already-present valid current-snapshot pending artifact if its original inbox push failed to produce a successful ingest wake.

Prefer integration with existing GitHub-owned preparation/writer flows rather than a new scheduler or ChatGPT retry loop.

Required semantics:
- state-based, idempotent;
- validates current main state;
- still obeys maximal valid contiguous prefix;
- no duplicate canonical progress;
- no worker-created retry artifact required;
- existing serialization/concurrency remains authoritative.

Do not create a new ChatGPT-owned queue, retry manager, or backlog manager.

### 6. CI / contract-conformance coverage
Add deterministic tests that would have caught all source-independent defects above before live acceptance.

At minimum include:
- exact worker-facing schema ↔ validator enum parity;
- negative `category:"content"` case;
- invalid enum matrix for source-independent enums;
- missing required field/type/nullability matrix;
- bool-as-int rejection;
- wrong descriptor title;
- duplicate lane objects;
- lane/top-level count mismatch;
- duplicate exact observations;
- wrong appid binding in provenance URL where applicable;
- future-generated dossier rejection before persistence;
- invalid expected artifact -> authorized GitHub recovery -> same deterministic path eligible again;
- no alternate retry filename;
- recovery does not advance progress;
- stale old-snapshot inbox cleanup;
- current-snapshot inbox preservation;
- lost-wakeup reconciliation is idempotent and drains only valid contiguous prefix.

Keep existing transport/compact projection regression coverage green.

## Explicitly DEFERRED to review-source follow-up
Do not decide or implement these here:
- which endpoint/tool/source obtains actual Steam review bodies;
- direct Scheduled Task retrieval vs GitHub-prepared review evidence;
- new source-access-unavailable evidence state;
- minimum usable review-body count policy;
- how Russian/non-Russian review bodies are fetched or paginated;
- source-specific review provenance identifiers/fields not already fixed by current contract;
- whether store-only zero-review dossier can ever be considered semantically complete.

The separate source RECON will answer these.

## Production safety / parallel merge safety
Use a worker branch + PR.

Before writes, inspect relevant push/workflow triggers.

Because another READ-ONLY worker may write only its durable report to `main` while this task is active:
- rebase/update branch before merge as necessary;
- do not overwrite/revert unrelated newer `main` commits;
- if the source-RECON report lands while this PR is open, preserve it untouched.

No manual GitHub workflow dispatch.
No Scheduled Task `Run now`.
No Scheduled Task UI changes.
No Taste Semantic Producer changes.
No current production g1/g2 deletion/quarantine/replacement in this task.

Automatic workflows triggered by merge are allowed; observe them read-only and report exact effects.

## Expected surfaces
Verify rather than blindly assume, but likely changes may include:
- a new compact canonical worker-readable dossier schema file under `config/`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical dossier validator/runtime;
- buffered validation/ingest adapter;
- daily builder/cleanup path;
- relevant GitHub workflows for recovery/reconciliation;
- dossier validation/recovery regression tests;
- validation workflow wiring.

`config/execution_ownership_contract.json` should remain unchanged unless a contradiction is discovered. If implementation would require moving ownership away from GitHub, stop and report `blocked`.

## Definition of done
This task is complete only when:
- worker-facing source-independent schema/enums are exact and machine-readable;
- `content` mismatch is covered and rejected deterministically before live use;
- source-independent validator gaps above are fixed/tested;
- GitHub-owned invalid-artifact recovery mechanism exists and is tested but current g1/g2 are untouched;
- stale old-snapshot inbox lifecycle is implemented/tested;
- lost-wakeup reconciliation is implemented/tested;
- existing compact traversal/buffer drain tests remain green;
- no review-source choice was guessed;
- no Taste Semantic Producer change occurred;
- merged `main` readback and automatic workflow effects are verified.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-non-review-defect-repair-01.md`

Report must include:
- architecture preflight;
- exact scope implemented vs intentionally deferred;
- branch/PR/merge refs;
- exact files changed;
- schema surface introduced;
- validator fixes;
- recovery mechanism semantics;
- stale cleanup semantics;
- lost-wakeup reconciliation semantics;
- tests/run IDs/results;
- automatic post-merge workflow effects;
- confirmation current production g1/g2 were not mutated;
- confirmation no review-source decision was made;
- remaining work after this task, which should be limited to review-source/evidence closure plus coordinated current g1/g2 recovery/live acceptance;
- one next step only.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `implementation_incomplete`

Stop after durable report. Do not run live acceptance.