# Worker Report — Taste Current-Live Profile Binding Fix 01

## 1. Task
- Task ID: `taste-current-live-profile-binding-fix-01`
- Source task: `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`
- Mode: `IMPLEMENT`
- Scope completed: smallest safe change to the existing lightweight current-main one-AppID Taste preparation path.
- No real semantic canary was executed by this task.

## 2. Verified predecessor/blocker
- The predecessor one-AppID harness deliberately disabled canonical profile refetch and reused the profile recorded in committed `data/production/pre_ai/taste_projection.json`.
- The first real acceptance attempt therefore prepared profile blob `191b6d6c5dec2f9ef2976517f301528740f9bec2` while the canonical live profile had already advanced to `9c9ef7cdf2d705b8dd10196cec654f16e04341e4`.
- That acceptance attempt correctly stopped before semantic execution: Scheduled Task mutation/trigger `0`, semantic results `0`, canonical ingest attempts `0`.
- This was a preparation-time binding defect, not a reason to require a user-controlled quiet window.

## 3. Architecture preflight
- `config/mailing_policy.json` remains authoritative for Taste profile loading. It keeps `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json` canonical, requires `load_once_per_run`, requires recording the Git blob SHA, forbids historical profile fallback, and fails closed when the canonical profile is unavailable.
- `config/execution_ownership_contract.json` keeps deterministic scope selection, queue construction, binding validation and persistence authority in GitHub. The existing scheduled ChatGPT runtime remains the semantic worker; this change does not transfer production control-plane ownership to the interactive chat.
- `config/taste_result_contract.json` still fences semantic production to `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`; no producer-fence rule was weakened.
- `scripts/ingest_taste_results.py` compares result bindings to the current projection before persistence. Therefore if the canonical profile later advances and the current projection is rebuilt for that newer profile, an older semantic result is rejected cleanly before ingest. The next bounded preparation attempt independently resolves and freezes the newer live profile.
- No second queue, scheduler, writer, retry daemon, cache authority, semantic runtime, or recurring workflow was introduced.
- Files named by older generic preflight instructions (`RUNTIME_EXPOSED_SURFACES.md`, `CANONICAL_DATA_CONTRACT.md`, `PROJECT_ARCHITECTURE.md`, `CONTENT_PIPELINE.md`) are not present in current `main`; no missing contract content was invented. The active canonical Taste policy/ownership/result/ingest contracts were sufficient to authorize this bounded fix.

## 4. Changes
### `scripts/build_taste_current_main_canary.py`
- Removed committed `taste_projection.json` as the profile authority for this canary path.
- Added a deterministic live-profile freeze against the canonical GitHub repository:
  1. resolve canonical repository `main` commit;
  2. fetch `gaming_taste_live.json` by that exact immutable commit through GitHub Contents API;
  3. verify returned bytes against the advertised Git blob SHA;
  4. parse the exact bytes as a JSON object;
  5. re-resolve `main` to detect a profile update that happened during the freeze boundary;
  6. if the head moved, retry from the newer head, with an absolute maximum of `3` attempts;
  7. once head confirmation is stable, freeze exact commit SHA + blob SHA + content SHA256 + byte count + immutable commit-pinned raw URL.
- Continuous churn for all three bounded attempts fails closed with a retry-later error; there is no unbounded profile chase.
- Writes the exact frozen bytes only to the external temporary artifact workspace as `frozen_profile/gaming_taste_live.json` plus `frozen_profile/profile_binding.json`.
- Existing production Taste projection/payload builders receive that frozen profile once for the bounded tuple. They do not refetch a later version mid-tuple.
- Added exact prepared-vs-frozen validation for canonical repository, path and blob SHA.
- Added `prepared_semantic_tuple.json` carrying the frozen profile binding plus model, semantics, fingerprint, candidate-context digest and the bounded queue row.
- Existing one-AppID, candidate-context, cache/model/semantics/fingerprint, repository-clean, no-AppDetails-fallback and queue-cardinality checks remain in force.

### `tests/test_taste_current_main_canary.py`
- Expanded focused suite from `7` to `13` tests.
- Added deterministic fake-GitHub concurrency simulations and exact snapshot/binding tests.

### `.github/workflows/taste-current-main-canary.yml`
- Kept the permanent route manual `workflow_dispatch` only and `contents: read`.
- Passes only the workflow-scoped read token to the harness for canonical GitHub reads.
- Uploads the exact frozen profile, immutable binding and prepared semantic tuple alongside the existing read-only proof files.
- No schedule, semantic execution, ingest, push, canonical write or Scheduled Task operation was added.

## 5. Focused tests
GitHub validation job `102600034706` ran:

`python -m unittest tests.test_taste_current_main_canary -v`

Result: **13/13 passed**.

Coverage includes:
- exact current-live profile content/blob/commit freeze;
- profile change before freeze selects the newer proven version;
- continuous profile churn is bounded and fails closed after at most three attempts;
- unavailable or malformed live profile fails closed;
- stale committed profile cannot silently override frozen live binding;
- profile change after freeze cannot create a mixed-version tuple;
- exactly one positive numeric AppID;
- exactly one Taste family;
- queue cardinality `0..1`;
- no other-AppID leakage;
- candidate context must be committed StoreBrowse basic info and non-empty;
- queue fingerprint/context binding consistency;
- valid zero-queue one-family partition behavior.

All focused test steps concluded `success`.

## 6. Concurrency/profile-update behavior proof
The concurrency rule is now explicit and bounded:

### Update before freeze
- Preparation resolves `main`, fetches the file by immutable commit, then resolves `main` again.
- If `main` moved during that boundary, the candidate snapshot is not accepted as frozen; the bounded attempt restarts from the newer commit.
- Focused test `test_profile_change_before_freeze_selects_newer_proven_version` passed.

### Update after freeze
- Freeze is complete only after one exact commit/file pair passes content/blob verification and the branch-head confirmation.
- The tuple then uses that immutable snapshot for all later preparation steps; no later `main` read can silently rewrite the tuple.
- `validate_prepared_outputs` rejects any projection whose repository/path/blob differs from the frozen binding.
- Focused test `test_profile_change_after_freeze_cannot_create_mixed_tuple` passed.

### Continuous updates at the boundary
- Maximum freeze attempts: `3`.
- If `main` changes across every attempt, preparation fails closed. No unbounded retry loop and no requirement for the user to stop editing tastes.
- A later normal bounded run starts from the then-current `main`, so Taste cannot remain permanently pinned to an old profile.
- Focused test `test_continuous_profile_churn_is_bounded_and_fails_closed` passed.

### Later update before ingest
- The current canonical ingest contract still requires result `profile_blob_sha`, model, semantics and source timestamp to equal the current projection.
- If production has advanced to a newer profile before ingest, an old semantic result fails closed before persistence; the next bounded preparation uses the newer profile. No manual cache/queue repair is required by this path.

## 7. Non-semantic Chernobylite preparation validation
A one-shot branch-only validation wrapper was used solely because the connected GitHub tooling cannot dispatch the permanent `workflow_dispatch` route directly.

Validation:
- AppID: `1016800`.
- Taste key: `App_1016800`.
- Title: `Chernobylite Complete Edition`.
- GitHub Actions run: `34391317370`.
- Job: `102600034706` (`validate-one`).
- Run/job conclusion: `success`.
- Checked out actual current `refs/heads/main`, commit `6f000db6fb6caa979fd0489a881bd7bb7521e5d1`.
- Current-main/clean-tree preflight: success.
- Focused tests: success.
- Preparation: success.
- Repository-untouched proof: success.
- Artifact upload: success.
- Harness elapsed: `1.66s`.
- Exactly one subject: yes.
- Queue cardinality: `1`.
- Queue decision: `semantic_queue_row`.
- Only queued subject: `App_1016800` / AppID `1016800`.
- Direct committed candidate description count: `1`.
- AppDetails fallback requested: `0`.

## 8. Exact profile proof and prepared binding proof
Exact canonical live profile frozen for the validation:
- identity: `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json`;
- resolved immutable profile commit: `c8a915d1ecad2bfd4f22d83182542925f73b1e54`;
- exact Git blob SHA: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`;
- exact content SHA256: `6ed2adb975860783abf402ed74446eb257b1e78af69c332590dc27718a663cc4`.

Prepared tuple binding:
- profile blob SHA: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`;
- frozen profile blob == projection profile blob == payload profile blob == prepared tuple profile blob: **true**;
- Taste model: `taste-v3`;
- Taste semantics SHA256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`;
- Taste fingerprint: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`;
- candidate-context SHA256: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`.

The former stale committed profile SHA cannot win this path: the validation used the then-current canonical live commit/blob directly and the tuple equality assertions passed.

## 9. Safety/containment proof
Validation assertions and workflow boundaries prove:
- semantic execution attempted: `false`;
- canonical Taste ingest attempted: `false`;
- production write attempted: `false`;
- Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` mutated: `false`;
- Scheduled Task triggered: `false`;
- second game/result: `0`;
- canonical queue/cache/receipt/inbox hand-edit: `false`;
- StoreBrowse refresh: `false`;
- Steam AppDetails fallback: `0`;
- full production rebuild: `false`;
- historical rerun: `false`;
- paid OpenAI API/Copilot/external scheduler: `false`;
- output paths: temporary/artifact-only, outside repository;
- repository clean before/after: `true`;
- validation workflow permissions: `contents: read`.

The temporary validation workflow was never added to `main`. After the run, branch `taste-live-binding-validation-once` was force-reset back to main commit `6f000db6fb6caa979fd0489a881bd7bb7521e5d1`, removing the one-shot workflow commit from the branch tip. No recurring validator was left behind.

## 10. Unresolved
- The real semantic Chernobylite canary remains intentionally unexecuted; this task was not authorized to run it.
- The live profile may continue changing normally after this validation. That is expected and no longer corrupts a frozen tuple. The later acceptance task must use the tuple's immutable profile snapshot/binding, and canonical ingest must continue to reject it if production has since advanced in a way the current contracts make stale.
- The older generic architecture filenames noted in preflight are absent from current `main`; this did not block the fix because active canonical Taste contracts unambiguously assign ownership and binding behavior.

## 11. Status
`complete_ready_for_real_canary_acceptance`

## 12. Recommended next step
Director should issue the separate one-game **ACCEPTANCE** task for Chernobylite/AppID `1016800`, using the existing authorized Scheduled Task producer and the frozen immutable tuple/profile-binding rules proven here. Do not reuse the old `191b6d...` tuple and do not reintroduce a requirement that the user pause profile updates.

This worker stops here and does not execute the semantic canary.

## 13. Exact commit/run/job/artifact/file refs
Main implementation commits:
- `bf74649f5a4ce0ad55d5f2e59f7044bcfec7b3d8` — durable architecture/preflight checkpoint report.
- `a53db6e02fe10141bc3bacb3768f3f283a8bc8f1` — `scripts/build_taste_current_main_canary.py`, live-profile freeze/binding implementation.
- `5b935951e986cdfed7f568251a467b59d9ffabdb` — `tests/test_taste_current_main_canary.py`, concurrency/binding regression tests.
- `6f000db6fb6caa979fd0489a881bd7bb7521e5d1` — `.github/workflows/taste-current-main-canary.yml`, permanent artifact/binding integration.

Validation-only refs:
- branch-only one-shot workflow commit: `59b92ef72088a7678ade5bb35db9d0b1b4ee3350` (later removed from branch tip by reset; never merged to `main`).
- run: `34391317370`.
- job: `102600034706`.
- artifact ID: `10119736896`.
- artifact name: `taste-current-live-binding-validation-1016800-34391317370`.
- artifact size: `64928` bytes.
- artifact ZIP digest: `sha256:847fe85482b1b32f122bdbf4f4b0d23aeecb637c2a6037b628bc8e34135272cb`.
- artifact expiry reported by GitHub: `2026-09-16T18:49:09Z`.

Permanent files changed:
- `scripts/build_taste_current_main_canary.py`
- `tests/test_taste_current_main_canary.py`
- `.github/workflows/taste-current-main-canary.yml`
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`

Read-only validation artifact files:
- `main_provenance.json`
- `frozen_profile/profile_binding.json`
- `frozen_profile/gaming_taste_live.json`
- `prepared_semantic_tuple.json`
- `taste_projection.one.json`
- `chatgpt_payload.one.json`
- `chatgpt_taste_queue.one.jsonl`
- `canary_proof.json`

## 14. Efficiency / reusable lesson
The safe concurrency boundary is not "profile must stay quiet while Taste runs". It is "freeze one canonical Git object once, prove exact bytes/blob/commit, then bind every field of one semantic tuple to that immutable object". A short bounded head-confirmation loop handles updates that race the freeze itself; updates after freeze are handled by immutable tuple provenance and the existing fail-closed ingest binding gate. This pattern avoids a second architecture, avoids unbounded retries, and permits normal parallel taste-profile updates.
