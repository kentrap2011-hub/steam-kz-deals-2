# Non-Review Dossier Defect Repair 01

- Task ID: `taste-dossier-non-review-defect-repair-01`
- Mode: `IMPLEMENT`
- Date: `2026-09-15`
- Final status: `complete_ready_for_director_acceptance`
- Repository: `kentrap2011-hub/steam-kz-deals-2`

## 1. Scope and result

Implemented the source-independent Steam review dossier pipeline repairs proven by `taste-dossier-full-defect-sweep-01`.

Completed:

- one exact machine-readable worker-facing dossier schema;
- worker/validator synchronization for source-independent required fields, JSON types, enums and structural invariants;
- rejection of invalid `category="content"`;
- strict validator coverage for bool-as-int, title binding, duplicate lanes, review-count consistency, duplicate observations, timestamp/TTL/future checks, appid type/binding and provenance structure/appid URL binding;
- GitHub-owned recovery for an invalid deterministic create-only expected artifact;
- GitHub-owned stale old-snapshot inbox quarantine on daily rollover;
- state-based lost-wakeup reconciliation inside the existing serialized pre-AI writer;
- PR/CI regressions for these boundaries;
- merge to `main`, main readback and automatic post-merge workflow verification.

Intentionally not implemented here:

- review-source selection or transport;
- new evidence semantics;
- source-access-unavailable semantics;
- a new minimum usable review-body threshold;
- a new source-specific stop-reason enum;
- source-specific review provenance IDs;
- store-only zero-review semantic completeness;
- recovery/mutation of the current production g1/g2;
- any Scheduled Task UI change, `Run now`, manual workflow dispatch, or Taste Semantic Producer change.

The parallel report `reviews/worker_reports/taste-dossier-review-source-recon-01.md` landed on `main` first in commit `33b46298426f3718168ef1f91a7bd63a2d9dbc69` and was preserved. This task did not overwrite or reinterpret that report.

## 2. Architecture preflight

Preflight sources included:

- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `CURRENT_TASK.md`
- `PROJECT_DECISIONS.md` (`TASTE-004`, `TASTE-005`, `TASTE-006`)
- `config/execution_ownership_contract.json`
- current dossier contract/persistence bridge/worker prompt/runtime/buffer/inbox/daily/projection/workflows/tests
- `taste-dossier-full-defect-sweep-01.md`
- `taste-dossier-live-compact-acceptance-01.md`
- `taste-dossier-worker-view-implement-01.md`

Result:

1. Canonical scope, retry, validation, persistence, checkpoint/progress, cleanup and completeness remain GitHub/GitHub Actions responsibilities.
2. Scheduled ChatGPT remains a constrained semantic/evidence data-plane worker.
3. The repair does not create a new recurring scheduler, independent queue, retry authority or completeness authority.
4. Recovery, stale cleanup and lost-wakeup reconciliation fit the already-authorized GitHub control plane and the existing serialized writer boundary `taste-steam-review-dossier-canonical-writer`.
5. `config/execution_ownership_contract.json` required no ownership change and was left unchanged.

## 3. Branch / PR / merge

Implementation branch:

`worker/taste-dossier-non-review-defect-repair-01`

Baseline at branch creation:

`f14f28069da3a298b013ca7e3080ab8bb41d7f7f`

Parallel source-recon report advanced `main` while this branch was in progress:

`33b46298426f3718168ef1f91a7bd63a2d9dbc69`

Implementation PR:

`#28` — `Repair non-review Steam dossier defects`

PR CI head:

`aadc3cfe8e370993f0ffd340e6a4d066329d9b5c`

Implementation merge commit:

`ca5c49b6290690918a9e9aa9fe53596d35c5d6a9`

The merge was performed normally on top of current `main`; the parallel source-recon report remained in ancestry and was not overwritten.

## 4. Files implemented

Added:

- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_recovery_contract.json`
- `scripts/taste_steam_review_dossier_strict.py`
- `scripts/taste_steam_review_dossier_recovery.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`

Modified:

- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier_buffered.py`
- `scripts/ingest_taste_steam_review_dossiers.py`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/build_taste_steam_review_dossier_work.py`
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/validate-taste-dossier-buffered.yml`

Not modified:

- `config/execution_ownership_contract.json`
- Taste Semantic Producer
- current production dossier g1/g2 artifacts
- Scheduled Task configuration/UI

## 5. Exact dossier schema and worker/validator synchronization

New authoritative source-independent worker schema:

`config/taste_steam_review_dossier_schema.json`

Schema identity:

`TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V1`

It explicitly publishes:

- required top-level fields including `schema` and `schema_version`;
- exact canonical category enum;
- exact sentiment enum;
- exact recurrence enum;
- exact evidence-language enum;
- exact review-lane identities;
- sampling strategy enum;
- JSON integer rules with `bool` explicitly excluded;
- TTL limits;
- timezone-aware timestamp/expiry rules;
- appid type/pattern;
- exact descriptor-title binding requirement;
- lane cardinality/count invariants;
- duplicate-observation rule;
- source-independent provenance structure;
- current additional-fields policy;
- an explicit list of source-dependent fields deliberately deferred to the separate source/evidence work.

The active worker prompt now requires this schema to be read before evidence work and forbids inventing enum synonyms. It specifically calls out that `category:"content"` is invalid because it is absent from the canonical enum.

The active canonical ingress paths now call `scripts/taste_steam_review_dossier_strict.py`, which loads the same schema. Buffered and retained legacy ingress therefore share the same source-independent worker/validator shape rather than relying on duplicated prose.

The existing V2 dossier contract remains the broader pipeline/control-plane contract. CI asserts that the new schema category/sentiment/recurrence enums match its existing neutrality enums, and that the exact required top-level set is the existing dossier required-field set plus the already-required dossier schema metadata (`schema`, `schema_version`).

Unknown/additional fields were **not** globally forbidden because the current contract does not authorize such a breaking tightening. Existing raw-review and personal/commercial forbidden-key guards remain active.

## 6. Validator repairs

`validate_dossier_strict(...)` now rejects the previously proven source-independent defects:

### JSON type strictness

The following must be actual JSON integers, not Python booleans or coercible strings:

- `schema_version`
- `ttl_days`
- observation `mention_count`
- review top-level counts
- lane `sampled`
- lane `batches`

`appid` must be a numeric **string**, not an integer coerced to string.

### Descriptor identity

For canonical ingress:

- dossier `appid` must equal the exact prepared item appid;
- dossier `title` must equal the exact prepared descriptor title;
- dossier count/order must equal exact prepared items.

### Observation consistency

- category/sentiment/recurrence/evidence-language values come from the exact schema;
- `category="content"` is rejected;
- recurrence minimum mention rules remain enforced;
- an exact duplicate observation object is rejected.

### Review-lane consistency

- exactly two lanes are required;
- identities must be exactly one `russian` and one `non_russian`;
- duplicate lane identities are rejected;
- lane sampled counts must equal the matching top-level language counts;
- Russian + non-Russian counts must equal `sampled_total`.

### Time/TTL checks

- generated/expiry timestamps must parse as timezone-aware ISO-8601;
- `expires_at_utc == generated_at_utc + ttl_days`;
- prepared TTL must match;
- a dossier more than five minutes future-generated is rejected **before persistence**;
- present provenance capture timestamps are also structurally parsed.

### Provenance/appid binding

Existing required source-independent provenance structure is enforced:

- `store_description.url`
- `store_description.content_sha256`
- `steam_reviews.url`

Steam store/review provenance URLs must bind to the dossier appid through the Steam `/app/{appid}` or `/appreviews/{appid}` path.

No new review-source-specific fields were made mandatory in this repair.

## 7. GitHub-owned invalid deterministic artifact recovery

New contract:

`config/taste_steam_review_dossier_recovery_contract.json`

New runtime:

`scripts/taste_steam_review_dossier_recovery.py`

Recovery is deliberately not a worker retry mechanism. It requires an explicit GitHub-side recovery request and proves all of the following before moving anything:

- request schema/action is authorized;
- request snapshot is the current canonical snapshot;
- request sequence is the current canonical expected sequence;
- request group hash binds the current immutable group descriptor;
- request artifact path is the one exact deterministic expected inbox path;
- exactly one artifact claims that current expected position;
- the artifact exists;
- canonical validation of that exact artifact actually fails.

A canonically valid expected artifact cannot be recovered/quarantined by this path.

On authorized recovery:

- only the invalid current expected artifact is moved out of active inbox into GitHub-owned quarantine;
- later pending groups remain untouched;
- the deterministic inbox path becomes free for a corrected future create-only publication;
- no alternate retry filename is created in active inbox;
- canonical manifest progress is re-read and proven unchanged;
- an audit record contains artifact hash, bindings, validator error, operator reason and `canonical_progress_advanced=false`;
- the recovery request itself is archived under GitHub-owned quarantine rather than left active.

The recovery workflow remains inside the existing canonical writer concurrency group.

**This recovery was not applied to current production g1/g2 in this task.**

## 8. Stale inbox cleanup

Old-snapshot inbox cleanup is implemented as bounded GitHub-owned quarantine during an actual new daily snapshot build.

Properties:

- runs only when `build_taste_steam_review_dossier_work.py` reports `built_new_daily_snapshot`;
- same-day snapshot preservation performs no stale cleanup;
- only recognizable inbox artifacts whose filename binds a different 64-hex snapshot are moved;
- current-snapshot artifacts are preserved;
- unrecognized files are preserved fail-closed;
- no canonical progress is advanced;
- moved files go to the GitHub-owned dossier inbox quarantine tree.

This design prevents old transport artifacts from accumulating in the active inbox while avoiding unsafe blanket deletion.

## 9. Lost-wakeup reconciliation

`ingest_taste_steam_review_dossier_inbox.py` now exposes a state-based nonfatal reconciliation mode.

It is called by the **existing** serialized `Build pre-AI deterministic payload` workflow after the daily dossier manifest is prepared/preserved.

Properties:

- current GitHub repository state is authoritative; no prior push event is trusted as queue state;
- uses the same maximal valid contiguous buffered drain;
- can accept already-present valid contiguous pending groups even when their original wake-up was lost;
- idempotent replay cannot advance the same canonical prefix twice;
- no worker retry artifact is needed;
- no new scheduler/recurring workflow was created;
- invalid expected artifact, gap or legacy/buffer conflict is nonfatal in the unrelated pre-AI build and produces no progress mutation.

The normal dedicated inbox-ingest workflow remains fail-closed on an invalid current expected group.

## 10. CI / regression coverage

PR workflow:

`Validate buffered Steam review dossier runtime`

PR run:

- run ID: `34971732975`
- run number: `14`
- conclusion: `success`

The regression suite now covers:

- exact schema/prompt/contract enum alignment;
- required-field relationship;
- current allowed extra-field behavior;
- `category="content"` rejection;
- wrong descriptor title rejection;
- appid/provenance URL mismatch rejection;
- bool-as-int rejection across schema/TTL/mentions/counts/batches;
- numeric appid rejection;
- duplicate lanes;
- lane/top-level count mismatch;
- duplicate observations;
- non-integer TTL;
- expiry mismatch;
- future-generated dossier rejection;
- missing required provenance structure;
- malformed capture timestamp;
- buffered title binding;
- recovery of an invalid current expected deterministic artifact;
- refusal to recover a valid expected artifact;
- later pending-group preservation during recovery;
- corrected re-publication at the same deterministic path followed by contiguous drain;
- stale old-snapshot quarantine with current/unrecognized preservation;
- lost-wakeup reconciliation of already-present valid pending work;
- nonfatal no-progress behavior for an invalid expected group.

Existing fixed-daily, buffered and same-day preservation regressions also remain in the PR workflow.

## 11. Post-merge verification

Implementation merge:

`ca5c49b6290690918a9e9aa9fe53596d35c5d6a9`

Automatic post-merge workflows:

### Build pre-AI deterministic payload

- run ID: `34971807206`
- job ID: `104389634867`
- conclusion: `success`
- `Prepare fixed daily full Steam review dossier backlog`: success
- `Reconcile already-present dossier inbox state`: success
- `Regression test fixed daily dossier snapshot control plane`: success
- atomic pre-AI commit step: success

The resulting automatic pre-AI commit was:

`f0aa026d7c80b9f5a6e5539761dea342d6f7c09e`

Its changed-file set contains ordinary pre-AI payload/translation refreshes and no dossier manifest/index/inbox/cache mutation. This is the expected behavior because current g1 remains invalid and nonfatal reconciliation must not advance through it.

### Validate execution ownership

- run ID: `34971807052`
- conclusion: `success`

Execution ownership therefore remained consistent after the merge.

## 12. Production g1/g2 preservation and current state

Post-merge/current readback shows the canonical worker index still at:

- snapshot: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`
- `canonical_expected_sequence = 1`
- `prepared_required_count = 594`
- `completed_required_count = 0`
- `remaining_required_count = 594`
- `full_backlog_complete = false`

Current production g1 remains present at its original deterministic path with blob SHA:

`50464e84c167a09fb47402567a19bf8282905410`

Current production g2 remains present at its original deterministic path with blob SHA:

`48f53d5595721e2bc5b864f3486f003618c583d5`

Neither was deleted, quarantined, replaced, overwritten or canonically accepted by this task.

## 13. Explicit non-actions

This task did **not**:

- choose or implement the production Steam review-body source;
- redefine evidence semantics from the parallel recon;
- create new source-dependent evidence states;
- press Scheduled Task `Run now`;
- open/change Scheduled Task UI;
- manually dispatch any GitHub workflow;
- mutate Taste Semantic Producer;
- mutate `config/execution_ownership_contract.json`;
- recover current production g1/g2;
- run live acceptance.

## 14. Remaining work / one next step

Remaining work is intentionally limited to the review-source/evidence closure handled by the parallel source work, followed by coordinated use of the now-implemented GitHub recovery path for the already-invalid production deterministic artifact(s) and a separate live acceptance after the source/evidence implementation is landed.

**Next step:** Director should combine `taste-dossier-review-source-recon-01` with this repair report into the source/evidence IMPLEMENT follow-up; only after that implementation is merged should the current g1/g2 recovery and live Scheduled Task acceptance be authorized.
