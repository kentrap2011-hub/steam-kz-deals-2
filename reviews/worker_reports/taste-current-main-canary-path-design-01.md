# Taste current-main canary path design 01

## Task
Design the smallest safe path to prepare and verify exactly one Taste subject from the current `main` (target for a later execution task: Chernobylite, AppID `1016800`) without rerunning a historical workflow, without rebuilding the whole production pipeline, and without executing semantic Taste work in this task.

## Lifecycle
- Last checkpoint UTC: 2026-09-09T14:08:56Z
- State: `done`
- Next concrete action: a separate implementation worker should add the bounded read-only current-main canary path described below; a separate explicitly authorized execution task would be required before running Chernobylite.

## Executive decision
There is **no existing safe bounded one-AppID current-main preparation path** that satisfies this task as-is.

The current full pre-AI workflow is capable of using current `main`, but it is too broad for the canary: it rebuilds canonical pre-AI artifacts, can perform whole-shortlist StoreBrowse work, writes canonical paths, and commits/pushes them. The existing one-AppID workflow is not a preparation canary at all; it is a real persistence/ingest test and intentionally writes canonical Taste state.

The smallest safe design is therefore:

1. a **new `workflow_dispatch`-only read-only canary workflow**;
2. explicit checkout of **`refs/heads/main`**;
3. one required `appid` input;
4. a bounded harness that imports/reuses the current-main Taste/pre-AI logic but restricts the subject to that one AppID **before** projection/payload/queue expansion;
5. all outputs written under `$RUNNER_TEMP` (or another non-repository temporary directory) and uploaded only as a workflow artifact;
6. no semantic ChatGPT execution, no inbox/ingest, no cache/overlay write, no commit/push.

This gives a fresh-current-main code-path proof without creating another production writer.

## 1. Why the historical rerun did not prove current `main`
A GitHub Actions **rerun** is tied to the original run context. In particular, it retains the original event/ref/SHA context and executes the workflow definition associated with that historical run. A default `actions/checkout` in that historical definition therefore checks out the historical `GITHUB_SHA`, not whatever happens to be at `main` when the rerun button is pressed.

Consequences:

- changing the workflow later does not retrofit the old run;
- rerunning an old run after a code fix is not proof that the fixed current `main` was exercised;
- the correct current-main proof is a **new dispatch**, with an explicit checkout ref.

The current `Build pre-AI deterministic payload` definition now explicitly checks out `ref: main`, so a fresh dispatch of the current definition is current-main-capable. That still does **not** make the full workflow suitable for this canary because its remaining behavior is broad and write-producing.

Observed `main` head during this recon was `7d935b04644cfee84b652b7a4c938d8960b913cd`; that SHA is the report checkpoint commit. A future canary must record its own checkout SHA and prove that its `HEAD` equals the resolved `origin/main` head used for that run rather than relying on this observation.

## 2. Current Taste/pre-AI producer path
The current deterministic producer is:

`.github/workflows/build-pre-ai-store-snapshot.yml` (`Build pre-AI deterministic payload`)

Relevant order of work:

1. checkout `main`;
2. validate Taste producer fence;
3. `scripts/build_pre_ai_store_snapshot.py`;
4. `scripts/build_pre_ai_taste_projection.py`;
5. `scripts/build_pre_ai_history_snapshot.py`;
6. `scripts/build_pre_ai_content_rules.py`;
7. `scripts/build_pre_ai_family_graph.py`;
8. `scripts/build_pre_ai_chatgpt_payload.py`;
9. compile/resolve existing Taste inbox/cache material and build `taste_cache_index.json`;
10. validate payload/freshness;
11. add/commit/push canonical generated artifacts, with retry/rebase handling for push contention.

Canonical Taste/pre-AI outputs include:

- `data/production/pre_ai/taste_projection.json`
- `data/production/pre_ai/chatgpt_payload.json`
- `data/production/pre_ai/chatgpt_taste_queue.jsonl`

### Bounded-key finding
Neither `scripts/build_pre_ai_taste_projection.py` nor `scripts/build_pre_ai_chatgpt_payload.py` currently exposes a safe CLI such as `--appid`, `--output-dir`, or `--dry-run`.

Both use canonical repository paths directly. Their `main()` paths operate over the resolved source set and write canonical `data/production/pre_ai/*` outputs. Therefore calling those scripts as-is for AppID `1016800` would **not** be a safe one-game artifact-only canary.

### Existing one-AppID workflow is not reusable for preparation
`.github/workflows/test-one-real-taste-persistence.yml` accepts an AppID, but it:

- requires a semantic result already present in inbox/cache;
- calls `scripts/ingest_taste_results.py`;
- writes an ingest receipt;
- writes producer-owned cache/overlay targets;
- commits/pushes those changes.

It is a persistence test, not a deterministic preparation canary, and must not be used here.

## 3. Can current `main` regenerate only Taste/pre-AI without rebuilding production?
**Yes, conceptually and safely, if the canary reuses the committed current-main input snapshots and is bounded before output generation.** There is no need to run the heavy `steam-test.yml` production rebuild merely to exercise current Taste code for one already represented subject.

Relevant current inputs/dependencies are:

| Input / dependency | Current source | Role in Taste preparation | Canary treatment |
| --- | --- | --- | --- |
| shortlist / family subject universe | committed production/pre-AI source material, including `store_snapshot.json` | determines candidate subjects | select only requested AppID |
| store context | `data/production/pre_ai/store_snapshot.json` | name/store URL/description and candidate context | reuse committed row; do not whole-shortlist refetch |
| history | `data/production/pre_ai/history_snapshot.json` | historical/profile context | read-only |
| content rules | `data/production/pre_ai/content_rules.json` | deterministic content filtering | read-only |
| family graph | `data/production/pre_ai/family_graph.json` | family eligibility/context | read-only |
| canonical Taste profile | `config/taste_reference_profile.json` | profile binding/corpus source | read-only |
| Taste semantics | `config/taste_semantics.json` | semantics version and decision/scoring rules | read-only |
| Taste models | `config/taste_models.json` | model binding/version | read-only |
| cache + overlay resolution | `data/production/taste_cache_index.json`, produced using producer-fence ownership rules | existing semantic/cache state and fingerprint freshness | read-only; preserve resolved winner |
| prior semantic payload where applicable | `data/production/pre_ai/chatgpt_payload.json` | prior semantic precheck/binding material | read-only |
| contracts/rules | `config/taste_result_contract.json` and current rule/config files | exact validation/bindings | read-only |

`scripts/build_pre_ai_store_snapshot.py` performs Steam StoreBrowse work for the resolved production candidate set, with fallback requests. That network step should **not** be rerun across the entire shortlist just to prove one Taste subject.

For the canary, if AppID `1016800` does not have adequate committed current-main store/candidate context, the correct bounded behavior is to fail closed with an explicit `upstream_snapshot_missing_or_insufficient` result. Refreshing the production/store snapshot is a separate upstream-data task, not something the canary should silently expand into.

## 4. Smallest safe current-main canary design
### 4.1 Trigger and checkout
Future implementation should add a new workflow, for example:

`.github/workflows/taste-current-main-canary.yml`

Required properties:

- trigger: `workflow_dispatch` only;
- input: one required numeric `appid`;
- permission: `contents: read`;
- checkout: `actions/checkout@v4` with `ref: refs/heads/main`, `fetch-depth: 0`;
- no production workflow chaining;
- no schedule;
- no write token requirement.

At startup, record:

- requested AppID;
- run ID/run URL;
- `git rev-parse HEAD`;
- resolved `origin/main` SHA;
- repository working-tree status before preparation.

Require checked-out `HEAD` to equal the main SHA resolved for the run. This is the direct proof missing from a historical rerun.

### 4.2 Bounded harness
Preferred implementation is a small dedicated read-only harness, for example:

`scripts/build_taste_current_main_canary.py`

It should **reuse/import current production helper logic** rather than fork Taste semantics, but provide a safe boundary that the current builders do not have:

- `--appid <one value>`;
- `--output-dir <temporary directory>`;
- no canonical writes;
- no commit/push;
- no inbox/ingest;
- no cache/overlay writes;
- no semantic ChatGPT call;
- no broad StoreBrowse refresh.

The AppID filter must be applied before the projection/payload/queue expansion, not by generating a full canonical queue and deleting other rows afterward.

If importing the existing helpers requires path adaptation, the adapter should construct the one-subject in-memory/temp input and call current-main functions. It must not alter production behavior merely to make the canary convenient.

### 4.3 Artifact-only outputs
Suggested artifact contents:

- `main_provenance.json`
- `taste_projection.one.json`
- `chatgpt_payload.one.json`
- `chatgpt_taste_queue.one.jsonl`
- `canary_proof.json`

No file under `data/production/**` or `reviews/chatgpt_taste_inbox/**` is an allowed canary output.

### 4.4 One-subject assertions
The harness/workflow must fail if:

- any prepared subject has an AppID other than the requested one;
- more than one Taste queue row is emitted;
- the result cannot be traced to the checked-out current-main inputs;
- a required profile/model/semantics binding is absent;
- the working tree changes;
- a canonical output path is touched.

A zero-row semantic queue is valid when current deterministic Taste logic concludes that no semantic evaluation is needed (for example, an applicable fresh cache decision). In that case the proof artifact must carry the deterministic reason instead of forcing a semantic request.

## 5. Required Chernobylite proof contract (design only; not executed)
For a later authorized run with AppID `1016800`, `canary_proof.json` must make the following directly auditable.

### Provenance
- requested AppID is exactly `1016800`;
- checked-out current-main SHA;
- source snapshot/config paths and, where practical, their hashes;
- target occurs once in the bounded subject set;
- no other AppID reaches Taste preparation.

### Candidate context
- `candidate_context_source`;
- raw bounded `candidate_context` used by the payload/queue path;
- store/description provenance such as current `description_source` where emitted;
- enough raw provenance to explain exactly why that candidate context was selected.

The inspected generic builders do **not** expose a standalone bounded canary proof artifact and no repository code search located a dedicated safe `candidate_context_source` canary surface. The future adapter must therefore surface the current-main context provenance in `canary_proof.json` without inventing evidence. If the production path exposes only lower-level provenance fields for the selected context, the adapter may normalize those into the proof field while preserving the raw fields alongside it; if it cannot establish the source unambiguously, it must fail closed.

### Taste identity/bindings
- `taste_fingerprint`;
- `taste_profile_id`;
- `taste_model_id`;
- `taste_model_version`;
- `taste_semantics_version`.

These values must be copied from the actual bounded current-main projection/payload/queue objects and checked for internal equality. They must not be hard-coded into the canary proof.

### Taste v3 gates / decision trace
The proof must preserve **all raw gate/decision fields emitted by the current Taste v3 path for the subject**, plus a compact normalized gate matrix for review. At minimum the reviewer must be able to establish from raw current-main data:

- profile/model/semantics binding validity;
- candidate-context availability/sufficiency and its provenance;
- resolved cache/overlay state selected by the existing ownership/fence rules;
- whether cached semantic material matches the current Taste fingerprint/bindings or is stale/inapplicable;
- applicable historical/negative/tried-warning evidence carried into the current decision path;
- the final deterministic Taste decision;
- whether that final decision does or does not require a semantic queue item.

The normalized matrix is only a view. Raw projection/payload/queue fields remain authoritative so the canary does not create a second Taste decision contract.

### Queue proof
If a semantic row is produced:

- queue size must be exactly `1`;
- its AppID/subject AppID must be `1016800`;
- its fingerprint/profile/model/semantics bindings must equal the projection/payload bindings;
- its candidate context must be the bounded current-main subject context.

If no row is produced, the proof must identify the deterministic no-queue decision and the matching cache/binding evidence.

### Canonical repository untouched
Before and after preparation:

- capture `git status --porcelain`;
- require `git diff --exit-code`;
- require no changed path under `data/production/**`;
- require no changed path under `reviews/chatgpt_taste_inbox/**`;
- require no workflow/config/source modification by the run itself.

The workflow then uploads the temp artifact and exits. There is no `git add`, commit, push, or repository write step.

## 6. Why this avoids production write conflicts
The full pre-AI workflow is a canonical writer and already contains commit/push/rebase contention handling. The proposed canary is not another writer:

- checkout is pinned to one current-main commit for the duration of the run;
- repository permission is `contents: read`;
- every generated file is outside the checkout/canonical tree;
- no Git persistence step exists.

Therefore a scheduled or manually running production/pre-AI workflow may advance `main` while the canary is running without creating a push race. The canary remains a reproducible proof of the exact SHA recorded at startup. If newer upstream production data is desired, launch another fresh canary after that data lands rather than mixing live state into the existing run.

## 7. Producer-fence, queue-binding, receipt/cache guarantees remain unchanged
The canary must stop **before semantic execution and before ingest/persistence**.

That means:

- `taste_producer_fence.py` ownership/precedence rules are not bypassed or rewritten;
- existing resolved cache/overlay state is consumed read-only;
- no new canonical queue is published;
- no semantic result is placed in the inbox;
- `scripts/ingest_taste_results.py` is not invoked;
- no ingest receipt or canonical cache/overlay entry is created.

The existing ingest path already enforces exact queue/result binding for AppID, `taste_fingerprint`, profile ID, model ID/version, and semantics version. A later real semantic result must still pass those unchanged checks. The canary only proves deterministic preparation from current `main`; it does not create an alternate persistence route.

## 8. Explicitly prohibited paths
Do **not** use any of the following for this canary:

- rerun of the historical Actions run;
- `steam-test.yml` full production rebuild;
- modification of the Scheduled ChatGPT Task;
- manual patching of canonical `chatgpt_taste_queue.jsonl`;
- direct writes to `data/production/pre_ai/**`;
- writes to `reviews/chatgpt_taste_inbox/**`;
- writes to canonical Taste cache/index/overlay;
- `test-one-real-taste-persistence.yml`;
- semantic execution of Chernobylite as part of preparation/design.

## 9. Expected runtime improvement
No canary or Chernobylite execution was performed in this task, so there is no measured runtime claim.

Structurally, the existing full pre-AI path includes whole-candidate StoreBrowse work, multiple unrelated snapshot/build stages, validation, and canonical commit/push contention handling. The bounded design removes the broad network refresh, unrelated subject expansion, and all Git write/rebase work. Its active preparation is one-subject file/config loading plus current Taste projection/payload logic.

Expected effect: after runner startup, deterministic canary preparation should be **seconds-to-tens-of-seconds class rather than a workflow-wide minutes-class path**, with runner startup potentially becoming the dominant fixed cost. This is a design expectation, not a benchmark; the implementation worker should record actual step duration on its first non-semantic test and compare it with a representative full pre-AI run.

## 10. Implementation handoff
A separate implementation task can be scoped narrowly to:

1. add `.github/workflows/taste-current-main-canary.yml` with `workflow_dispatch`, one AppID input, explicit `refs/heads/main`, and `contents: read`;
2. add a small bounded harness (preferred) rather than changing canonical producer behavior;
3. reuse current Taste helper logic and current committed inputs;
4. emit only temp/artifact proof files;
5. assert one subject, queue cardinality `0..1`, exact bindings, current-main provenance, all Taste v3 decision evidence, and a clean repository tree;
6. add focused tests for target bounding, output isolation, zero/one queue behavior, and fail-closed missing-context behavior;
7. **do not run Chernobylite** in the implementation task unless a later task explicitly grants execution permission.

The implementation should be considered complete only when an artifact-only test can prove current-main provenance and zero canonical diffs without invoking semantic ChatGPT or ingest.

## Changes
Only this report was created/updated:

- `reviews/worker_reports/taste-current-main-canary-path-design-01.md`

No workflow, script, contract, production data, `CURRENT_TASK.md`, inbox, cache, overlay, or Scheduled Task was changed.

## Validation
Recon inspected the current task/protocols and the current producer/persistence implementation, including:

- `WORKER_TASK_TASTE_CURRENT_MAIN_CANARY_PATH_DESIGN_01.md`
- `WORKER_ANTI_STALL_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `PROJECT_ROUTES.md`
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/steam-test.yml`
- `.github/workflows/test-one-real-taste-persistence.yml`
- `scripts/build_pre_ai_store_snapshot.py`
- `scripts/build_pre_ai_taste_projection.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/build_taste_cache_index.py`
- `scripts/taste_producer_fence.py`
- `scripts/ingest_taste_results.py`
- `config/execution_ownership_contract.json`
- the prior contention/historical-rerun report.

No workflow was dispatched or rerun. No Chernobylite semantic action was executed. No Scheduled Task was changed.

## Unresolved / intentionally deferred
- Actual canary runtime is not measurable until the bounded path is implemented and run.
- The proof adapter must expose an unambiguous `candidate_context_source` from the current-main context provenance; it must fail closed rather than inventing the source if current raw fields are insufficient.
- Whether the then-current committed snapshot contains sufficient AppID `1016800` context is an implementation/run preflight question and was deliberately not converted into a semantic execution here.

## Status
`complete_design_ready_for_implementation`

## Recommended next step
Create a separate implementation worker task for the read-only `workflow_dispatch` + bounded temporary-output harness. Keep Chernobylite execution as a separately authorized follow-up.

## Efficiency / reusable lesson
For current-code canaries, prefer **fresh dispatch + explicit current branch ref + read-only artifact output**. Historical reruns prove historical code, while reusing a canonical producer with hard-coded output paths turns a diagnostic into another production writer and recreates the contention being diagnosed.