# WORKER TASK — TASTE CURRENT-MAIN CANARY PATH IMPLEMENT 01

## Task ID
`taste-current-main-canary-path-implement-01`

## Mode
`IMPLEMENT`

## Expected report
`reviews/worker_reports/taste-current-main-canary-path-implement-01.md`

## Goal
Implement the approved lightweight read-only current-main canary preparation path for exactly one Taste AppID, based on the completed design in:

`reviews/worker_reports/taste-current-main-canary-path-design-01.md`

This task must make it possible to prove deterministic one-game Taste preparation from current `main` without rerunning a historical workflow, without rebuilding the full production pipeline, and without writing canonical production state.

Do NOT run Chernobylite semantic analysis in this task.
Do NOT modify the existing Scheduled Task.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `WORKER_ANTI_STALL_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_DESIGN_01.md`
- `reviews/worker_reports/taste-current-main-canary-path-design-01.md`
- current Taste/pre-AI producer and validation code directly needed for implementation.

## Required implementation

### 1. Add one new read-only manual workflow
Add:

`.github/workflows/taste-current-main-canary.yml`

Required properties:
- `workflow_dispatch` only;
- one required numeric `appid` input;
- no schedule;
- `permissions: contents: read` only;
- explicit checkout of `refs/heads/main`;
- record checked-out `HEAD` and resolved `origin/main` SHA;
- fail if provenance cannot be established;
- no production workflow chaining;
- no GitHub write permission;
- no `git add`, commit, push, or repository mutation;
- upload proof/result only as workflow artifact.

### 2. Add one bounded one-AppID harness
Preferred path from design:

`scripts/build_taste_current_main_canary.py`

The harness must:
- require exactly one AppID;
- support temp/output-dir supplied by workflow;
- reuse/import current Taste/pre-AI logic rather than fork/reimplement Taste semantics;
- bound the subject BEFORE projection/payload/queue expansion;
- read current committed snapshots/config/cache state only;
- not perform broad StoreBrowse/full-shortlist refresh;
- not write to canonical `data/production/**`;
- not write to inbox/ingest/cache/overlay canonical paths;
- not call semantic ChatGPT;
- not call canonical ingest;
- fail closed if required AppID context is absent/insufficient or provenance cannot be established unambiguously.

### 3. Artifact-only proof
Emit under runner temp/output directory only, using the design as contract. At minimum provide an auditable proof artifact containing:
- requested AppID;
- checked-out current-main SHA;
- source snapshot/config provenance;
- target subject count;
- current Taste fingerprint/profile/model/semantics bindings;
- current candidate context and source/provenance;
- raw decision/gate evidence used by current Taste v3 path;
- deterministic queue decision;
- queue cardinality `0..1`;
- if one queue row exists, prove it belongs only to the requested AppID and matches bindings/context;
- clean repository-tree proof before/after.

Suggested files may follow the approved design:
- `main_provenance.json`
- `taste_projection.one.json`
- `chatgpt_payload.one.json`
- `chatgpt_taste_queue.one.jsonl`
- `canary_proof.json`

Exact filenames may differ only if there is a strong implementation reason; document any deviation in report.

### 4. Safety assertions
The implementation/workflow must fail if:
- any AppID other than requested reaches bounded Taste preparation;
- more than one semantic queue row is emitted;
- required profile/model/semantics binding is missing or inconsistent;
- candidate context provenance is ambiguous;
- repository working tree changes;
- canonical production/inbox/cache/overlay path is touched;
- any semantic execution or ingest is attempted.

### 5. Tests
Add focused tests sufficient to prove at least:
- one-AppID bounding;
- output isolation to temp dir;
- queue cardinality `0..1`;
- exact binding consistency;
- fail-closed missing/insufficient context;
- no canonical repository mutation;
- no other AppID leakage.

Use the smallest test surface that actually proves these properties. Do not broaden into unrelated regression work.

### 6. Validation run — NON-SEMANTIC ONLY
A non-semantic validation of the new path is allowed and expected after implementation.

You MAY dispatch the new read-only workflow against a harmless test AppID / fixture or AppID `1016800` **only to prepare/read-only proof artifacts** if no semantic ChatGPT execution, inbox/ingest, production write, or Scheduled Task mutation can occur.

If using AppID `1016800` for this preparation-only validation:
- this is NOT the Chernobylite semantic canary;
- do not trigger the Scheduled Task;
- do not produce/submit a semantic result;
- do not ingest anything.

Measure and record actual workflow/harness runtime.

If any external GitHub run exceeds the anti-stall bounded waiting window, save exact run/job id with lifecycle `waiting_external` and return control rather than waiting silently.

## Hard boundaries
- no paid OpenAI API;
- no Copilot;
- no external scheduler/service;
- no new Scheduled Task;
- do not modify Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`;
- no semantic Chernobylite execution;
- no semantic execution for any other game;
- no canonical Taste ingest;
- no production/pre-AI canonical writes from the canary workflow;
- no manual hash substitution;
- no weakening producer fence, binding, V5/evidence/price-blind semantics;
- no full `steam-test.yml` production rebuild for this implementation validation;
- no historical workflow rerun;
- no unrelated backlog work.

## Required report
`reviews/worker_reports/taste-current-main-canary-path-implement-01.md`

Include:
- files changed;
- exact implementation architecture;
- how current production Taste logic is reused;
- tests and results;
- any non-semantic workflow run id/job/artifact;
- measured runtime;
- proof repository remained untouched by canary execution;
- proof no semantic/Scheduled Task/ingest activity occurred;
- unresolved risks;
- readiness for a separate Chernobylite execution task.

## Final status — exactly one
- `complete_implementation_ready_for_canary_execution`
- `needs_followup`
- `blocked`

Do not run the real Chernobylite semantic canary.
Do not start System Audit.
Do not widen production.
Do not start another task.
