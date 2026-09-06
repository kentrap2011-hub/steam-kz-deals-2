# Taste Canary Atomic Ingest Failure Recon 01

## Task

READ-ONLY / RECON for the failed singleton Taste canary ingest of `Prototype™` (`App_10150`) produced by existing Scheduled Task instance `6a9d6fdddc00819193ed670d782045c4`, producer `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`, generation `1`.

Target failure:
- workflow: `Ingest context-bound taste batch`
- run: `34047485340`
- job: `101525034300`
- step: `Validate, ingest and rebuild taste consumers atomically`

No producer/task/generation/inbox/queue/receipt/cache/check mutation was performed in this recon. The only repository change is this report.

## Verified facts

### 1. Exact immediate failure in canary ingest

Run `34047485340` did **not** fail on the Prototype semantic row itself.

`python scripts/process_taste_inbox.py` entered its initial baseline consumer rebuild and called `scripts/build_pre_ai_taste_projection.py`. That builder exited with:

`Content metadata stale versus current mailing feed`

The exception propagated through `rebuild_taste_consumers()` as a `CalledProcessError`; the workflow therefore skipped `Commit accepted taste batch`.

Important ordering detail: `process_taste_inbox.py` rebuilds baseline Taste consumers **before** it starts per-inbox-file `ingest_taste_results.py`. Therefore the failing run never reached the inner result binding / fingerprint / candidate-context validation for `Prototype`.

No receipt was created, no accepted cache row was committed, and the inbox result was not transactionally consumed.

### 2. Why the baseline was stale

At canary commit `392903cf720dde1de4936436f235e9489d659ddd`:

- `data/production/pre_ai/content_metadata.json`
  - `source_updated_at_utc = 2026-09-03T18:53:27.390807+00:00`
  - `source_item_count = 831`
- `data/production/mailing/index.json`
  - `source_updated_at_utc = 2026-09-05T20:45:34.327772+00:00`
  - `item_count = 778`

`build_pre_ai_taste_projection.py` intentionally requires those source timestamps to match exactly and fails closed when they do not.

The stale pre-AI state was created by an earlier upstream atomic-refresh failure, not by the canary result.

### 3. Exact upstream root cause that left the stale snapshot in `main`

Mailing rebuild commit:

- `353df2ceaa7e060fd9e61af0eabde6dcdb9bafe0`
- message: `Rebuild mailing feed and Store state cache`
- timestamp: `2026-09-05T20:45:47Z`

It correctly triggered `Build pre-AI deterministic payload`:

- run `33991072184`
- job `101373289101`
- conclusion: `failure`

That run successfully rebuilt in its working checkout:

- current Store snapshot + content metadata (`778` rows),
- fixed-package data,
- FX snapshot,
- content rules,
- family graph,
- Taste projection (`750` subjects),
- history snapshot.

It then failed at step `Build strong and moderate deal scenarios`:

`Unexpected deal quality contract`

The exact code defect is in `scripts/build_pre_ai_deal_scenarios.py`: it hard-codes acceptance of only:

- contract id `DEAL-QUALITY-AND-SORT-V1`
- version **`1.3`**

But `config/deal_quality_contract.json` had already been advanced to version **`1.5`** by Taste step-3 work (`69baa039c30c7cbc1f266f2a4395656a2b71fad8`, `Close Taste step 3 final refinement gap`).

The v1.5 change did not replace the threshold/purchase-decision sections consumed by `build_pre_ai_deal_scenarios.py`; the builder simply retained an obsolete exact-version guard.

Because the pre-AI workflow is atomic, its later `Commit atomic pre-AI payload` step was skipped. Thus the newly generated Sep-5 content metadata / Taste projection never reached `main`, leaving the last committed pre-AI payload from Sep 3. This stale committed payload is what the Sep-6 canary ingest encountered.

**Root-cause chain:** stale hard-coded deal-quality contract version (`1.3` vs current `1.5`) -> Sep-5 pre-AI atomic workflow aborts before commit -> `main` keeps Sep-3 pre-AI metadata/queue while mailing is Sep-5 -> Sep-6 Taste ingest baseline rebuild detects source mismatch and aborts before reading the Prototype result.

### 4. Was `Prototype` an actual queue row?

Yes, with an important qualification.

At canary commit `392903cf720dde1de4936436f235e9489d659ddd`, the persisted `data/production/pre_ai/chatgpt_taste_queue.jsonl` really contained:

- `family_id = game:10150`
- `taste_subject_key = App_10150`
- `appid = 10150`
- title `Prototype™`
- `taste_fingerprint = ed46bdeca520dcc7dd002fb462eef58689fb423a6ef8be1acd896109622f8a4e`
- `candidate_context_sha256 = b43f8e93ab6bc1aa8d4e213c3a4aa6978e09b434e266e2a3c2669b745e87a3e5`

The inbox result used those same per-row identifiers.

However, that queue was **not globally current**: it belonged to the stale Sep-3 pre-AI snapshot that remained committed only because run `33991072184` failed atomically. So `Prototype` was a legitimate row of the queue actually supplied to the producer, but that queue itself was stale relative to the Sep-5 mailing/current profile inputs.

`Prototype` also remains present in the Sep-5 mailing source. Its row-level deterministic Taste identity inputs inspected here are materially unchanged: appid/title/core-fit/release-date/description remain the same; the visible fit-tag change is ordering only, and the fingerprint builder sorts tags. No Prototype-specific source mutation explains the failure.

### 5. Binding / fingerprint / context freshness

The submitted result is internally consistent with the **old bound queue row**:

- task instance / producer / generation are the requested singleton values,
- row key/appid match,
- `taste_fingerprint` matches the persisted queue row,
- `candidate_context_sha256` matches the persisted queue row,
- producer-fence, format, and normalized-result workflow checks passed.

But the result is no longer reusable as a current result after the pre-AI pipeline is repaired.

The result is bound to the old whole-document snapshot, including:

- `source_mailing_updated_at_utc = 2026-09-03T18:53:27.390807+00:00`
- profile blob SHA `c478cda9bb7a9b024a30ca188dce4b98a2de24ea`

The failed Sep-5 pre-AI refresh already showed the would-be fresh projection using:

- mailing source timestamp `2026-09-05T20:45:34.327772+00:00`
- `current_profile_blob_sha = c42a6a5dcf608e04bf86d24be9e1542f1b934456`

So a repaired atomic refresh changes the result binding in at least **two** exact-contract dimensions: source mailing timestamp and profile blob SHA.

`config/taste_result_contract.json` and `scripts/ingest_taste_results.py` intentionally require exact whole-document binding equality and do not permit relabeling an old result onto a new snapshot. Per-row fingerprint/context stability cannot override a stale whole-document binding.

### 6. Is the semantic result itself bad?

No semantic defect was found in this recon.

For the queue/context it was actually given, the result is coherent and structurally valid:

- verdict `INCLUDE`, fit `strong`, reason code `include_strong`,
- normalized Taste factors are present,
- evidence/reasons are tied to the supplied user Taste context and the Prototype candidate,
- outer producer-fence / result-format / normalized-result checks passed.

However, it would be incorrect to call the old result **current-ingest-valid**, because `process_taste_inbox.py` failed before `ingest_taste_results.py` could run its exact binding checks, and the authoritative profile/source binding has since moved.

Therefore the correct conclusion is: **semantic content appears valid for its Sep-3-bound candidate context; it is not a valid reusable result for the refreshed current binding.**

### 7. Game-specific data problem or general processing problem?

General processing/orchestration problem.

Any Taste inbox item processed while committed `content_metadata.source_updated_at_utc` differs from the current mailing source timestamp will fail in the same initial baseline rebuild before its own row is ingested.

The original upstream defect is likewise generic: `build_pre_ai_deal_scenarios.py` rejects the repository's current deal-quality contract v1.5, causing the entire atomic pre-AI snapshot commit to be skipped.

Nothing in the observed stack identifies `Prototype` data as the cause.

## Exact root cause

**Primary root cause:** `scripts/build_pre_ai_deal_scenarios.py` still hard-codes `DEAL-QUALITY-AND-SORT-V1` version `1.3`, while the canonical `config/deal_quality_contract.json` is version `1.5`. This caused pre-AI run `33991072184` to fail with `Unexpected deal quality contract` and skip its atomic commit.

**Immediate canary failure:** because that atomic pre-AI commit never happened, Sep-3 `content_metadata`/Taste consumers remained in `main` beside a Sep-5 mailing feed. Run `34047485340` then failed closed during its initial `build_pre_ai_taste_projection.py` baseline rebuild with `Content metadata stale versus current mailing feed`, before per-result ingestion.

## Can the existing Prototype result be reused?

**No.**

It must not be manually patched, relabeled, or forced through.

After the minimal upstream fix, the pre-AI snapshot must be rebuilt against current sources. The refreshed binding will differ from the existing result at least by mailing timestamp and profile blob SHA. The exact binding contract therefore correctly makes the existing Sep-3-bound result stale.

A **new singleton canary semantic result will be required after the fix**, using the refreshed current queue/binding. That new canary is a later EXECUTE task and was not started here.

## One minimal next IMPLEMENT

Update `scripts/build_pre_ai_deal_scenarios.py` so its fail-closed contract guard is aligned to the repository's current `DEAL-QUALITY-AND-SORT-V1` **version `1.5`**, with a focused regression that proves the current v1.5 contract is accepted while a genuinely incompatible contract still fails closed.

Do **not** weaken the guard to accept arbitrary future versions, do not edit generated pre-AI artifacts manually, and do not change Taste ingest binding checks.

Acceptance for that IMPLEMENT should include a successful existing `Build pre-AI deterministic payload` run that reaches `Commit atomic pre-AI payload` and leaves `content_metadata.source_updated_at_utc` aligned with the current mailing source. Only after that should a separate EXECUTE generate one fresh Prototype/current-row canary.

## Changes

- Added only `reviews/worker_reports/taste-canary-atomic-ingest-failure-recon-01.md`.
- No production code/config/workflow/data/cache/inbox/queue/receipt/task/generation changes.

## Validation

Read-only verification included:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_TASK_TASTE_CANARY_ATOMIC_INGEST_FAILURE_RECON_01.md`
- predecessor canary worker report
- canary inbox and persisted Taste queue
- `scripts/process_taste_inbox.py`
- `scripts/ingest_taste_results.py`
- `scripts/build_pre_ai_taste_projection.py`
- `scripts/build_pre_ai_deal_scenarios.py`
- `config/taste_result_contract.json`
- `config/deal_quality_contract.json`
- production mailing/pre-AI metadata
- pre-AI workflow definition and artifact history
- GitHub Actions run `34047485340`, job `101525034300`
- upstream GitHub Actions run `33991072184`, job `101373289101`
- Sep-5 mailing commit `353df2ceaa7e060fd9e61af0eabde6dcdb9bafe0`
- deal-quality v1.5 commit `69baa039c30c7cbc1f266f2a4395656a2b71fad8`

## Unresolved

The failed Sep-5 pre-AI run never committed its freshly generated queue artifacts, so there is no persisted authoritative fresh `App_10150` queue row to quote byte-for-byte from that run. This does not affect the reuse decision: the fresh run itself proves that whole-document binding changes (mailing timestamp and profile SHA), which is sufficient to invalidate the existing result under the exact result contract.

## Status

complete

## Recommended next step

Perform only the minimal IMPLEMENT above: align the deal-scenario builder's exact contract guard with canonical v1.5 and validate that the normal atomic pre-AI refresh completes. Do not run a new Taste canary as part of that IMPLEMENT unless separately directed after the refreshed queue is committed.

## Compact refs

- canary ingest run: `34047485340`
- canary ingest job: `101525034300`
- canary submission commit: `392903cf720dde1de4936436f235e9489d659ddd`
- stale-source-producing upstream run: `33991072184`
- upstream job: `101373289101`
- Sep-5 mailing commit: `353df2ceaa7e060fd9e61af0eabde6dcdb9bafe0`
- deal contract v1.5 commit: `69baa039c30c7cbc1f266f2a4395656a2b71fad8`
- last successful pre-AI payload commit before the break: `264a8898635f43d757941c929adf5419ef1a8cac`
- result subject: `App_10150` / `Prototype™`

## Efficiency lesson

When an atomic inbox processor rebuilds shared consumers before row ingestion, diagnose the earliest baseline rebuild first. Here that immediately separated a global stale-snapshot failure from a semantic-row failure; tracing the stale snapshot one workflow upstream then exposed the obsolete contract-version guard without touching the canary data.
