# Worker Report — Taste Pinned Profile Batch Lifecycle Fix 01

- task_id: `taste-pinned-profile-batch-lifecycle-fix-01`
- lifecycle: `needs_followup`
- current_utc: `2026-09-10T12:33:00Z`
- implementation_status: `pinned_validation_model_and_regressions_pass_but_production_lifecycle_not_fully_wired`
- final_status: `needs_followup`
- next_action: `wire the existing GitHub pre-semantic producer/checkpoint path to create and durably commit the already-implemented active pin before semantic execution, then make process_taste_inbox post-ingest proof distinguish accepted pinned A from current live B without weakening any binding guard`

## Scope guardrails observed

No semantic Taste run was executed. The existing 10-result package was not ingested, edited, or regenerated. No next 10 games were analyzed. No queue/cache/production data was manually mutated. Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` and its cadence were not modified or triggered by this task.

A branch-only validation workflow used `contents: read` and ran tests only. It did not run `scripts/process_taste_inbox.py`, `scripts/ingest_taste_results.py --input ...`, any semantic worker, or any production write command. The validation checkout proved tracked repository state remained unchanged. The temporary validation branch was force-reset to the tested `main` commit after the run, so the one-shot workflow is no longer present at the branch tip.

## Durable checkpoint and implementation history

The required report checkpoint was saved before further testing/change in commit:

- `1ca3a2f0e2056e7a789b436586b73a9cc9087a19` — report checkpoint recording already completed implementation.

Original implementation commits already present when this continuation began:

- `887505e28caf8dd89d3b6ad490980063be437bb5` — initial `scripts/taste_pinned_work_unit.py` helper.
- `55b91fb098df983fb0e3cf95c17ebb1d5858560a` — `scripts/ingest_taste_results.py` switched from current-live validation to pinned-work-unit validation.
- `b3c8813649ad2238304ce7fc57e39af6cbcaf09f` — first focused lifecycle regression tests.

The authority was subsequently strengthened, without reverting to historical-profile fallback:

- `8f9961f9f63efe91058d6092e273d8b88d885aaf` — introduced explicit durable pre-semantic work-unit pin state.
- `26bc8579a83b062242f976fd020cece9174a53bb` — made pin validation resolver-aware and restricted legacy grandfathering to the exact proven package.
- `5431266c72c017bce5d74ef49631ec081b76bba3` — focused tests for A→B, next B pin, arbitrary stale rejection, strict binding guards, and the existing package.

Contract/test synchronization in this continuation:

- `b27befae0cc23198af45fa2f6cf5001ef2af6ba7` — `config/taste_result_contract.json` v1.1 explicitly defines `TASTE-PINNED-WORK-UNIT-V1`, required immutable profile identity, exact ordered row identity, `pinned_work_unit_sha256`, `pin_authority_commit`, fail-closed binding rules, and the exact legacy package exception while preserving `TASTE-SEMANTIC-RESULT-V5` and producer generation 2.
- `5bc24ccba943b6f202dabd1914b455457b12e727` — `config/execution_ownership_contract.json` explicitly assigns Taste work-unit pin creation/retirement and result validation authority to GitHub control plane; Scheduled ChatGPT remains only the constrained semantic data plane.
- `523f417bff92753597c06706e7f99df020f5e69b` — `scripts/validate_taste_v3_contract.py` regression fixture updated to supply the required pinned authority to the already-changed `validate_input` signature; no semantic rule was changed.

`config/taste_checkpoint_contract.json` was reviewed but deliberately left unchanged. It is the separate `MANDATORY-TASTE-CHECKPOINT-V1` proof for final cache completeness before downstream stages; it is not the pre-semantic work-unit/profile authority. Changing it would conflate two distinct checkpoint meanings and is not necessary for the pinned-work-unit contract.

`config/taste_validation_contract.json` was also left unchanged because it governs the separate full mechanical fingerprint-validation artifact rather than semantic work-unit pin lifecycle.

## Implemented pinned authority model

The implemented helper defines canonical active authority at:

`data/production/pre_ai/taste_active_work_unit.json`

New work-unit authority requires:

- schema `TASTE-PINNED-WORK-UNIT-V1`;
- canonical producer id `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`;
- producer generation `2`;
- immutable profile identity: repository, path, resolved commit SHA, Git blob SHA, content SHA256, byte count;
- exact semantic bindings: profile blob, Taste model, Taste semantics SHA256, source mailing timestamp;
- exact ordered work rows: key, appid, Taste fingerprint, candidate-context SHA256, `work_required`;
- canonical ordered work-unit SHA256.

For a normal new result, validation additionally requires exact result bindings:

- `pinned_work_unit_sha256`;
- `pin_authority_commit`.

The result introduction commit must descend from the exact durable pin commit. Active pin bytes must equal their Git authority snapshot. Any profile/model/semantics/source/order/appid/fingerprint/context/count/duplicate mismatch fails closed.

There is no generic lookup of an arbitrary old profile revision.

## Test execution — actual GitHub Actions run

A branch-only read-only validation workflow was created solely to execute tests because the worker environment cannot clone GitHub directly.

- temporary branch: `taste-pinned-lifecycle-validation-once`
- validation-only workflow commit: `623ce1458ed3868fdfe0b07da1b0fe6aca23d819`
- workflow run: `34477068093`
- job: `102870321162`
- tested main base: `523f417bff92753597c06706e7f99df020f5e69b`
- token permissions: `Contents: read`, `Metadata: read`
- job conclusion: `success`
- repository tracked state after tests: unchanged (`TASTE_PINNED_VALIDATION_REPOSITORY_UNTOUCHED=PASS`)

### Focused pinned lifecycle suite

Command:

`python -m unittest tests.test_taste_pinned_work_unit -v`

Result: **4/4 passed**.

Passed cases:

1. `test_a_pin_survives_live_b_and_new_work_after_retirement_uses_b`
   - A is durably pinned before result creation;
   - live projection advances to B before the A result is resolved;
   - exact A-bound result still resolves against durable A pin;
   - after A pin retirement, a new pin is created with B;
   - copied arbitrary stale A result after B is rejected;
   - fresh B-bound result resolves against B.
2. `test_active_pin_requires_full_immutable_profile_identity`
   - incomplete profile identity fails closed.
3. `test_existing_10_package_is_exactly_grandfatherable_and_v5_stays_strict`
   - the real existing package resolves only through the exact legacy proof;
   - exact authority/result commits and A profile are verified;
   - full `ingest.validate_input` V5 validation succeeds;
   - missing V5 evidence field and duplicate result are rejected.
4. `test_pin_hash_commit_order_fingerprint_context_model_semantics_and_count_fail_closed`
   - wrong pin hash rejected;
   - wrong authority commit rejected;
   - order mismatch rejected;
   - Taste fingerprint mismatch rejected;
   - candidate-context mismatch rejected;
   - model mismatch rejected;
   - semantics mismatch rejected;
   - result-count mismatch rejected;
   - duplicate key rejected.

### Current-live freeze regressions

Command:

`python -m unittest tests.test_taste_current_main_canary -v`

Result: **13/13 passed**.

This reconfirms the existing immutable live-profile freeze rules: exact commit/blob/content snapshot, profile update before freeze selects the newer version, profile update after freeze cannot mix tuple versions, continuous boundary churn fails closed, stale committed profile cannot override the frozen live binding, and candidate context/queue cardinality checks remain strict.

### Directly affected V5 / producer / transactional / ownership regressions

Commands and results:

- `python scripts/validate_taste_v3_contract.py` → `TASTE_V5_CONTRACT_VALIDATION=PASS`; pinned binding exercised; normalized factor vector persisted; negative evidence rules and negative-only semantic immutability preserved.
- `python scripts/validate_taste_producer_fence.py` → `TASTE_PRODUCER_FENCE_REGRESSION=PASS`; correct active producer accepted; wrong/missing producer id and generation rejected; historical archive excluded from active scan.
- `python scripts/validate_taste_inbox_transactional_proof.py` → `TASTE_INBOX_TRANSACTIONAL_PROOF_VALIDATION=PASS`; legal retained base-support, final Taste exclusion, deal exclusion, and illegal retained Taste work fail-closed cases all behaved as expected.
- `python scripts/validate_execution_ownership.py` → `ARCHITECTURE_OWNERSHIP_VALID`.

## A → B result

The pin/resolver/ingest-validation layer behaves correctly under A→B:

- a durable A pin remains A after live advances to B;
- a matching A result is accepted by pinned authority rather than compared to live B;
- after retirement, the next work-unit pin uses B;
- arbitrary old A cannot reach backward to history and is rejected;
- strict row/model/semantics/context/fingerprint/order/V5 protections remain active.

However, this does **not** yet establish the full original end-to-end lifecycle through the existing production pre-semantic creation and post-ingest transactional verification paths. See root cause below.

## Existing 10-result package — final disposition

`existing_batch_provably_grandfatherable_under_pinned_work_unit_rule`

This conclusion is now verified by executable regression, not only by inspection.

Exact proof:

- package path: `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`;
- pre-semantic durable checkpoint commit: `0ec1ed0ec10e8950f86e6f600bc360325481ae9b`;
- result introduction commit: `f138d5216248c999fde588c47ca5088ff9c076ee`;
- result commit direct parent: the exact pre-semantic checkpoint;
- profile blob: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`;
- immutable profile commit: `c8a915d1ecad2bfd4f22d83182542925f73b1e54`;
- profile content SHA256: `6ed2adb975860783abf402ed74446eb257b1e78af69c332590dc27718a663cc4`;
- pre-semantic checkpoint explicitly records canonical queue lines `1..10`, exact keys/appids/fingerprints/context hashes, model, semantics and source binding before semantic execution;
- current package bytes still match the exact result-introduction commit, as exercised by `resolve_pinned_work_unit` during the passing test;
- the package passes full V5 `ingest.validate_input` against this grandfathered exact pin authority.

Grandfathering is intentionally exact-path/exact-commit/exact-parent/exact-bytes/exact-binding only. Copying or reintroducing the file later is not grandfathered and no arbitrary historical profile fallback is authorized.

The package was **not ingested** in this task.

## Self-diagnosis — first real completion blocker

Despite all focused tests passing, the original task cannot truthfully receive `complete_pinned_profile_lifecycle_fix_ready_for_acceptance` yet because the production lifecycle does not actually create/use/retire the new active pin end to end.

### Root cause 1 — pre-semantic production pin is not wired

The implemented canonical path is `data/production/pre_ai/taste_active_work_unit.json`, but that file is absent from current `main`.

`.github/workflows/build-pre-ai-store-snapshot.yml` currently builds the Taste projection and ChatGPT payload and atomically commits those artifacts, but it does **not** invoke `scripts/taste_pinned_work_unit.py prepare`, does not create `taste_active_work_unit.json`, and does not stage such a pin in its atomic pre-AI commit.

Therefore the invariant "GitHub durably records exact authorized work-unit/profile before semantic execution" is implemented as a helper/contract but not yet connected to the normal production preparation path.

The helper's `prepare` command also requires an immutable `profile_binding` containing resolved profile commit/content SHA256, while the ordinary production Taste projection currently records only repository/path/raw URL/blob SHA/bytes. The existing one-AppID canary has the required immutable freeze implementation, but ordinary pre-AI production has not yet been wired to reuse it for the active pin.

### Root cause 2 — post-ingest transactional proof still assumes accepted result equals current live profile

`scripts/process_taste_inbox.py` still computes post-ingest expectations as though every full Taste result must immediately become a cache hit in the **current rebuilt projection**:

- expected safe-cache hits increase by full-evaluation count;
- expected current `ai_required_count` decreases by full-evaluation count;
- every ingested key is required to be a current projection cache hit;
- current queue count is expected to drop accordingly.

For the required A→B lifecycle, successful persistence of an A-bound result while live is already B is intentionally **not** a B cache hit. B must remain unresolved for the next work-unit. Consequently the current transactional proof would reject the correct state after rebuilding consumers on B, preventing the A work-unit from completing through post-ingest verification/commit even though `ingest_taste_results.py` itself correctly accepts the pinned A result.

This is the exact remaining mismatch identified earlier; the green transactional regression only proves the existing same-profile cases and does not remove this A≠B assumption.

### Root cause 3 — pin retirement is not part of the canonical ingest commit

`.github/workflows/ingest-taste-batch.yml` does not currently stage/remove `data/production/pre_ai/taste_active_work_unit.json`, and `process_taste_inbox.py` does not retire that pin after a proven successful work-unit. Thus the requirement that the next work-unit after completion freezes then-current B is proven at helper/test level but is not yet implemented in the normal production completion path.

## Why status is not complete

The user explicitly required full-batch authority through semantic evaluation, validation, ingest, post-ingest verification, and durable commit. Passing isolated pin validation while the production preparation and post-ingest paths remain unwired would make a `complete...` status false.

The first real completion failure is architectural integration, not semantic correctness of the pin matcher. The smallest follow-up is therefore to connect the already-implemented authority model to the existing GitHub pre-AI/ingest lifecycle and add one focused synthetic A→B post-ingest regression. No second queue, new scheduler, historical-profile acceptance, or Scheduled Task change is needed.

## Exact files changed by this task so far

- `scripts/taste_pinned_work_unit.py`
- `scripts/ingest_taste_results.py`
- `tests/test_taste_pinned_work_unit.py`
- `config/taste_result_contract.json`
- `config/execution_ownership_contract.json`
- `scripts/validate_taste_v3_contract.py`
- `reviews/worker_reports/taste-pinned-profile-batch-lifecycle-fix-01.md`

No canonical queue/cache/production data file is intentionally part of the task changes.

## Final status

`needs_followup`
