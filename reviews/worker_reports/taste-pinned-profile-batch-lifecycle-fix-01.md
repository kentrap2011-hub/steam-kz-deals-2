# Worker Report — Taste Pinned Profile Batch Lifecycle Fix 01

- task_id: `taste-pinned-profile-batch-lifecycle-fix-01`
- lifecycle: `complete`
- current_utc: `2026-09-10T12:58:00Z`
- implementation_status: `production_pinned_work_unit_lifecycle_wired_and_regression_proven`
- final_status: `complete_pinned_profile_lifecycle_fix_ready_for_acceptance`
- next_action: `return_control_to_director; existing_10_result_package_remains_uningested`

## Final result

`complete_pinned_profile_lifecycle_fix_ready_for_acceptance`

The production Taste lifecycle now uses the already-established `TASTE-PINNED-WORK-UNIT-V1` authority end to end:

1. normal pre-AI production builds the exact current Taste projection and ordered ChatGPT queue;
2. before any semantic work can begin, GitHub creates or preserves `data/production/pre_ai/taste_active_work_unit.json` and includes it in the same atomic pre-AI Git commit;
3. the pin freezes the exact immutable profile repository/path/resolved commit/blob/content SHA256/byte identity plus model/semantics/source and exact ordered key/appid/fingerprint/context/work identity;
4. semantic results must bind to the exact work-unit hash and the exact Git authority commit;
5. ingest validates against that durable pin rather than the later live profile;
6. post-ingest proof distinguishes an exact accepted older A result from current B reuse eligibility, so A is persisted without being misclassified as a B cache hit and B remains exact pending work;
7. only after transactional proof passes is the completed normal active pin retired and the then-current live work frozen as the next active pin;
8. arbitrary historical results without the exact durable pre-semantic pin still fail closed.

## Exact production implementation commit

The final tested production files were atomically applied to `main` in:

- `fc355295eb0c473a9d0d73ad33e4cfa9d621cc0b` — `fix: complete pinned Taste production lifecycle [skip ci]`

The `[skip ci]` marker was intentional: installing this architecture must not itself start a new production work-unit, semantic run, or ingest while this implementation task is still active. GitHub reports zero workflow runs for this head SHA.

The commit changes exactly these six files and no production data/cache/queue/result file:

- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/ingest-taste-batch.yml`
- `scripts/process_taste_inbox.py`
- `scripts/taste_pinned_work_unit.py`
- `scripts/validate_taste_inbox_transactional_proof.py`
- `tests/test_taste_pinned_production_lifecycle.py`

Comparison `72995d07a46da80993026f7d1228e8dff5182622...fc355295eb0c473a9d0d73ad33e4cfa9d621cc0b` is one commit ahead and contains only those six paths.

## Pre-semantic durable pin creation

`.github/workflows/build-pre-ai-store-snapshot.yml` now runs:

`python scripts/taste_pinned_work_unit.py ensure`

after the exact split ChatGPT consumer bundle/queue is built and before the atomic pre-AI commit is published.

The workflow stages `data/production/pre_ai/taste_active_work_unit.json` in that same atomic commit. Therefore semantic execution can only consume an already-committed work-unit authority; the Git commit containing the pin is the durable `pin_authority_commit`.

If a valid active pin already exists, `ensure` preserves it even if current live has moved forward. This is the required in-flight behavior: a later B cannot overwrite a work-unit already pinned to A.

If there is no active pin and there is queued Taste work, `ensure` freezes the profile currently represented by the prepared projection using bounded GitHub head/contents/head confirmation. It verifies that the immutable fetched blob and byte count still match the already-prepared projection, computes content SHA256, and records:

- repository;
- path;
- resolved commit SHA;
- Git blob SHA;
- content SHA256;
- byte count.

If live changes between projection preparation and pin freeze so the tuple could become mixed, pin creation fails closed instead of silently selecting a different version.

The freeze steps use the workflow's normal `github.token`; no paid/external service or scheduler was added.

## Exact pinned authority

Canonical active authority path:

`data/production/pre_ai/taste_active_work_unit.json`

Schema:

`TASTE-PINNED-WORK-UNIT-V1`

The pin binds:

- producer id `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`;
- producer generation `2`;
- immutable profile identity;
- `profile_blob_sha`;
- `taste_model_version`;
- `taste_semantics_sha256`;
- `source_mailing_updated_at_utc`;
- exact ordered work-unit rows;
- exact `key` / `appid` / `taste_fingerprint` / `candidate_context_sha256` / `work_required` per row;
- canonical ordered work-unit SHA256.

A normal new result must also carry:

- `pinned_work_unit_sha256` equal to the active pin's exact hash;
- `pin_authority_commit` equal to the Git commit that durably contains that exact pin.

The result-introduction commit must descend from that authority commit and the active pin bytes must match their Git snapshot. There is no generic lookup of arbitrary historical profile revisions.

## Post-ingest A → B transactional proof

`scripts/process_taste_inbox.py` now resolves and proves the exact pinned authority for every inbox package before canonical ingest.

For each result it separately computes whether the accepted pinned result is reusable for the **current** projection. Reuse requires exact equality of:

- profile blob;
- model version;
- semantics SHA256;
- appid;
- Taste fingerprint;
- candidate-context SHA256;
- current `work_required` identity.

This produces the required behavior when A was pinned before semantics but live is B at ingest time:

- the A result remains valid and may be persisted because its exact A pin is proven;
- it does **not** increment B safe-cache-hit count;
- it does **not** decrement B `ai_required_count`;
- the corresponding current B queue rows must remain present with exact identity/work requirements;
- post-ingest verification fails if an older A result is accidentally promoted to a B cache hit or if B work disappears/changes;
- same-profile results retain the previous strict cache-hit/queue-decrement behavior.

The old atomic/fail-closed checks remain: complete projection, complete family partition, sale-end consistency, unique queue keys, exact queue count, legal retained negative/base-support work, V5 result shape and producer fence.

## Active pin retirement and next-profile pinning

After canonical ingest writes its candidate state and all post-ingest transactional checks pass, `process_taste_inbox.py` performs the pin transition.

For a normal active work-unit:

1. the completed pin must still exactly match the current active pin;
2. only then is that active pin retired in the working transaction;
3. if current queue still contains work, the current projection/profile is frozen again using the same immutable profile rules;
4. the next active pin is written from the current queue and current live profile;
5. `.github/workflows/ingest-taste-batch.yml` stages the active-pin deletion/replacement together with inbox removal, overlay/index/receipt changes and rebuilt pre-AI consumer state in the same ingest commit.

If creation of the next pin fails, no successful ingest commit is produced. Thus retirement cannot become a window in which the durable repository silently loses the prior pin after a failed transaction.

For the exact legacy grandfathered 10-result package, there is deliberately no claim that it is the current active pin. Processing that package in a future authorized task therefore cannot retire an unrelated newer active pin. If no active pin exists after a successful legacy transaction and current work remains, the current live work is prepared as the next pin.

## A → B production lifecycle regression

New regression:

`tests/test_taste_pinned_production_lifecycle.py`

It proves three production-level cases:

### Immutable profile freeze

- exact resolved commit/blob/content SHA256/byte identity is frozen;
- projection/live mixed tuple is rejected fail closed.

### Full A → B lifecycle

In a temporary Git repository:

1. projection/queue A is prepared;
2. A active pin is created and committed before semantic result creation;
3. projection advances to B;
4. `ensure` preserves the already-active A pin;
5. an exact A-bound result is introduced only after B is live;
6. resolver accepts it against the durable A authority;
7. transactional proof confirms it is not reusable as B;
8. B safe-hit count and `ai_required_count` remain unchanged;
9. exact B work remains in the queue;
10. only after proof succeeds is A retired;
11. the next pin is created from B;
12. a fresh B result resolves against B;
13. a later copied arbitrary A result is rejected.

### Workflow wiring

The test also asserts that normal pre-AI workflow contains pre-semantic pin creation/persistence and normal ingest workflow includes the active-pin lifecycle in its atomic commit set.

## Final tests from committed `main`

Final validation was run from a temporary read-only branch created directly from production implementation commit `fc355295eb0c473a9d0d73ad33e4cfa9d621cc0b`.

- final validation workflow commit: `01ef4fbad7d0bfa0e06e6a96fb078bf5df66a278`
- GitHub Actions run: `34479631781`
- job: `102878861799`
- permissions: `Contents: read`, `Metadata: read`
- result: `success`

The one-shot workflow was not merged to `main`; after the run the temporary validation branches were force-reset to `fc355295eb0c473a9d0d73ad33e4cfa9d621cc0b`, so the one-shot workflow is not present at their tips.

Exact final results:

- changed lifecycle scripts `py_compile`: PASS;
- `python -m unittest tests.test_taste_pinned_production_lifecycle -v`: **3/3 PASS**;
- `python -m unittest tests.test_taste_pinned_work_unit -v`: **4/4 PASS**;
- `python -m unittest tests.test_taste_current_main_canary -v`: **13/13 PASS**;
- `TASTE_V5_CONTRACT_VALIDATION=PASS`;
- `TASTE_PRODUCER_FENCE_REGRESSION=PASS`;
- `TASTE_INBOX_TRANSACTIONAL_PROOF_VALIDATION=PASS`;
- `ARCHITECTURE_OWNERSHIP_VALID`;
- `TASTE_PINNED_FINAL_MAIN_REPOSITORY_UNTOUCHED=PASS`.

The focused fail-closed suite still proves rejection for:

- wrong pin hash;
- wrong pin authority commit;
- result order mismatch;
- Taste fingerprint mismatch;
- candidate-context mismatch;
- model mismatch;
- semantics mismatch;
- result-count mismatch;
- duplicate key;
- missing V5 fields;
- stale/unproven historical result;
- incomplete immutable profile identity.

## Existing 10-result package — final disposition unchanged

`existing_batch_provably_grandfatherable_under_pinned_work_unit_rule`

The existing package remains exactly:

`data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`

Its durable proof remains:

- pre-semantic checkpoint commit: `0ec1ed0ec10e8950f86e6f600bc360325481ae9b`;
- result introduction commit: `f138d5216248c999fde588c47ca5088ff9c076ee`;
- result commit direct parent is that exact pre-semantic checkpoint;
- profile blob A: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`;
- immutable profile commit: `c8a915d1ecad2bfd4f22d83182542925f73b1e54`;
- profile content SHA256: `6ed2adb975860783abf402ed74446eb257b1e78af69c332590dc27718a663cc4`;
- exact ordered 10 keys/appids/fingerprints/context hashes and model/semantics/source binding were durably recorded before semantic execution;
- focused regression still resolves the current bytes through only this exact grandfather proof and passes full V5 `validate_input`;
- copying/reintroducing the same old result elsewhere is not grandfathered and is rejected.

The production implementation diff contains no change to this package, queue or Taste cache. The package was not ingested in this task.

## Contract state

Previously synchronized canonical contracts remain in force:

- `config/taste_result_contract.json` v1.1 — exact pre-semantic pin, work-unit hash, authority commit and narrow grandfathering rule while preserving `TASTE-SEMANTIC-RESULT-V5` and generation 2;
- `config/execution_ownership_contract.json` — GitHub owns pin creation/retirement and exact validation; Scheduled ChatGPT remains the constrained semantic data plane.

`config/taste_checkpoint_contract.json` remains the separate final cache-completeness checkpoint and was correctly not repurposed as semantic pin authority.

## Scope confirmation

During this implementation/verification task:

- no semantic Taste run was executed;
- no new games were analyzed;
- the existing 10-result package was not edited, regenerated or ingested;
- no canonical Taste queue was manually changed;
- no canonical Taste cache was manually changed;
- no production data was manually rewritten as test state;
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` and its cadence were not modified;
- no production ingest workflow was dispatched;
- no production workflow ran for implementation head `fc355295eb0c473a9d0d73ad33e4cfa9d621cc0b`;
- validation workflows used read-only repository permissions and left tracked state unchanged.

## Final status

`complete_pinned_profile_lifecycle_fix_ready_for_acceptance`
