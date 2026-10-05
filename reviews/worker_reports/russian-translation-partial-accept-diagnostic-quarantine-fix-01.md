# Worker report — Russian translation partial acceptance and diagnostic quarantine fix 01

Task: `RUSSIAN_TRANSLATION_PARTIAL_ACCEPT_DIAGNOSTIC_QUARANTINE_FIX_01`  
Worker slot: ЧАТ 2  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Base/source of truth: `main`  
Implementation branch: `fix/russian-translation-partial-accept-diagnostic-quarantine-01`  
PR: #145 — `Isolate Russian translation quality failures into diagnostics`  
Validated implementation head before report/closeout-only commits: `88add831215992387b9353666bf5014b75978d9a`

## START / architecture preflight

The START gate was performed from current `main` before task-specific implementation. The current Russian-description route and canonical ownership/request/result/cache/manual-worker contracts were read first.

The resulting architecture remains:
- GitHub owns scope, queue construction, exact identity validation, diagnostic classification, persistence, completeness, timestamps and downstream rebuild.
- Translation semantic workers only process the exact normal GitHub-prepared queue.
- The browser only renders producer-owned observability.
- No new Scheduled Task, recurring diagnostic worker, retry loop, Fast/Dossier/Deep/ranking/expiry behavior or second backlog subsystem was introduced.

## Contract changes

Updated:
- `config/russian_description_translation_contract.json`;
- `config/russian_description_translation_result_contract.json`;
- `config/russian_description_manual_semantic_worker_prompt.md`;
- `PROJECT_ROUTES.md`.

The contracts now distinguish two failure classes:

1. **Submission/container or exact-binding corruption** remains fail-closed for the submission before persistence. This includes malformed shape, duplicate identity, unknown/stale request identity, AppID/hash/source-version mismatch, invalid status and unsafe cross-field combinations.
2. **Exact-current per-item translated-text quality failure** is isolatable after exact identity safety has passed. The item is not cached and enters translation diagnostics; safe valid siblings remain acceptable.

Both the existing scheduled translation worker and the explicit manual one-shot worker are forbidden to reconstruct, retry or resolve items removed from the normal queue into diagnostics.

## Diagnostic-state semantics

New canonical state:
`data/cache/russian_description_translation_diagnostics.json`

Contract:
`RUSSIAN-DESCRIPTION-TRANSLATION-DIAGNOSTICS-V1`

An active entry is keyed by exact `request_id` and retains:
- request/source/AppID/title/work type;
- exact `source_text_sha256` and `source_version`;
- source locale/quality/path and target locale;
- diagnostic reason and observed quality;
- submitted failing translated text / worker quality note when present;
- source submission path;
- first quarantine timestamp;
- explicit resolution fields.

Currentness rules:
- only an active entry matching the current exact request identity suppresses normal translation work;
- a source/binding change creates a new request identity and the stale diagnostic cannot suppress it;
- if deterministic current resolution becomes direct `ready_ru`, the historical diagnostic is no longer current/countable;
- explicit GitHub-owned resolution marks the exact entry resolved and allows the unchanged request to become normal queue work again if it is still unresolved;
- dictionary keying by exact request ID makes repeated ingest idempotent rather than duplicating diagnostic entries;
- there is no automatic diagnostic semantic worker or retry.

## Partial-accept implementation

`scripts/ingest_russian_description_translations.py` now performs all submission/result shape and exact-binding checks before persistence. Exact-bound translated results are then partitioned by the existing canonical `classify_description` quality gate:
- `good_ru` -> canonical translation cache;
- exact-bound non-`good_ru` -> translation diagnostics;
- explicit worker `status=error` -> existing error handling.

No canonical writes occur if later validation discovers submission-level unsafe corruption, so partial acceptance does not weaken AppID/request/hash/source-version safety.

`scripts/build_russian_description_translation_queue.py` loads diagnostic state and excludes only exact-current active diagnostic requests from the normal semantic queue while keeping them unresolved in producer accounting.

## Pinned checkpoint 1 regression

Pinned incident:
- submission commit: `32caa3b35fb750cd31da7198f28e34855928edd6`;
- file: `data/ai_inbox/russian_descriptions/manual-one-shot-9b3f6d2c7a41.json`;
- failed workflow run/job: `37138503097 / 111247856419`;
- pinned failed request: `2aeac6b30b8bea9fcecd9be3269154b2bb4b84fefc3345986929ee9f4e23b76e`;
- AppID: `1237980`.

The corrected validator was run against the already-submitted 20-result checkpoint without regenerating or editing its translations.

Validated result on PR CI:
- result records: **20**;
- cache-acceptable exact-bound translations: **19**;
- translation diagnostics: **1**;
- explicit worker error results: **0**;
- pinned failed request is the diagnostic item: **yes**.

CI emitted:
`{"pinned_checkpoint_accepted_count": 19, "pinned_checkpoint_diagnostic_count": 1, "pinned_checkpoint_error_count": 0, "pinned_checkpoint_result_count": 20, "pinned_failed_request_in_diagnostics": true}`.

This proves the required A-valid / B-bad-quality / C-valid behavior on the real failed checkpoint: B no longer discards valid siblings.

## Live checkpoint recovery status

Live canonical acceptance was **not** performed because the project protocol does not authorize this worker to merge PR #145 into `main`.

Fresh `main` at closeout still reports:
- normal translation queue: **82**;
- `untranslated_game_count`: **82**;
- `translation_diagnostic_count`: not present yet because the new contract/runtime is not merged;
- last attempt/success timestamps remain `2026-10-01T03:02:12.440625+00:00`.

A concurrent transport conflict also appeared while this task was running: `main` now contains a second 20-result submission
`data/ai_inbox/russian_descriptions/manual-one-shot-a41c7e5d920b.json`
(commit `c836a70a311f909ed5b8239b5e3b7c3f701ddced`) with the same 20 request IDs as pinned checkpoint 1, including the pinned request. The existing ingest intentionally treats duplicate request identity across submissions as submission-level unsafe ambiguity.

This worker did **not** delete, rewrite, rebind, or choose between that concurrent submission and the pinned checkpoint. Therefore post-merge recovery must first make an explicit Director-owned transport choice for these overlapping inbox submissions, then run the corrected canonical ingest. The pinned checkpoint itself is proven exact-current and deterministically classifies as 19 accepted + 1 diagnostic on the PR validation path.

## Statistics / site observability

Producer status now includes:
`translation_diagnostic_count`

Projection:
`chatgpt_ru_description_status.json`
-> `scripts/progressive_personalization.py::_translation_processing_metrics`
-> `processing_status.translation_diagnostic_count`
-> `web/progressive-personalization-ui.js::statisticsSections`.

The Statistics translation block renders:
`На диагностике перевода`

The browser does not infer the count from cards/client state.

Existing nonblocking Russian publication behavior remains unchanged: unresolved descriptions may remain visible without becoming fake `ready_ru`, while a card claiming `ready_ru` with bad text still fails the strict quality gate.

## Required regression coverage

Covered deterministically:
1. three-result mixed checkpoint with bad quality in the middle; valid siblings persist;
2. exact bad item enters diagnostics and leaves normal queue;
3. diagnostic item is not re-emitted by normal queue generation;
4. source/binding change does not inherit stale diagnostic state;
5. explicit canonical resolution safely clears the exact diagnostic;
6. re-ingest is idempotent for cache and diagnostic identity;
7. Statistics receives and renders the diagnostic count;
8. nonblocking Russian-publication behavior remains intact;
9. identity/AppID/hash mismatch remains submission-level fail-closed.

The focused regression also dry-runs the real pinned 20-result checkpoint.

## Validation

Latest validated implementation head: `88add831215992387b9353666bf5014b75978d9a`.

GitHub checks on that head:
- Validate execution ownership — run `37194537301` — **success**;
- Validate Progressive PASS 2 core — run `37194537366` — **success**;
- Validate backlog dispositions — run `37194537674` — **success**.

The execution-ownership job explicitly passed:
- `RUSSIAN_DESCRIPTION_TRANSLATION_CONTRACT_VALID`;
- existing translation runtime/manual worker/publication regressions;
- new partial-accept/diagnostic regressions;
- pinned checkpoint count proof above.

A prior UI expectation failed after the new Statistics row was introduced; the test was updated to assert the new producer-owned diagnostic row, after which Progressive PASS 2 core passed.

## PR / acceptance state

PR #145 is open and mergeable. It is intentionally not merged by this worker.

Remaining Director acceptance steps:
1. review and merge PR #145;
2. explicitly reconcile the two overlapping 20-result inbox submissions; do not regenerate translations or manually rebind request identities;
3. run the corrected canonical ingest for the intended checkpoint transport;
4. verify fresh `main` cache/diagnostics/status:
   - pinned checkpoint should produce 19 accepted and 1 diagnostic if bindings remain unchanged;
   - normal queue/status must be rebuilt from current sources;
5. verify the normal visual rebuild/Pages path independently before claiming the live site is fresh.

No Scheduled Task or automation was created, edited or removed.


## Director continuation closeout — 2026-10-05

### Reconciliation with current main

PR #145 was reconciled with the then-current `main` by a merge commit preserving all completed implementation while taking fresh main as the second parent. A bounded overlap check showed that among PR implementation files, only `CURRENT_TASK.md` had moved on main; its fresh main content was preserved and only this worker's own continuation block was appended.

After reconciliation and duplicate-transport resolution:
- validated implementation/transport head: `f25cfadfcb09a56cc36a7ba6a8d393d7a0691829`;
- PR #145: `mergeable=true`;
- compare to current `main`: `behind_by=0`;
- no implementation file from another active worker was overwritten.

### Exact duplicate-transport resolution

The two inbox files were inspected directly:
- canonical pinned failed checkpoint: `data/ai_inbox/russian_descriptions/manual-one-shot-9b3f6d2c7a41.json`;
- later overlapping submission: `data/ai_inbox/russian_descriptions/manual-one-shot-a41c7e5d920b.json`.

Confirmed:
- both contain exactly 20 result records;
- both contain the same 20 `request_id` values in the same order;
- all exact binding fields match for corresponding identities;
- 17 of the 20 translated texts differ between the two submissions.

The task itself identifies the first file as the checkpoint to recover. Therefore the resolution is intentionally transport-level, not semantic:
- keep `manual-one-shot-9b3f6d2c7a41.json`;
- remove the later overlapping `manual-one-shot-a41c7e5d920b.json` in PR #145;
- do not weaken duplicate-request safety in ingest;
- do not combine, choose per-item translations, regenerate translations, or change any request/AppID/hash/source binding.

This prevents double acceptance and removes the prior submission-level duplicate ambiguity. When PR #145 is merged, the inbox-path deletion is itself part of the merge diff, so the existing canonical ingest workflow can process the remaining pinned checkpoint through the corrected implementation.

### Fresh binding proof

Immediately after reconciliation:
- pinned checkpoint result count: **20**;
- exact-current bindings still present in the current canonical queue: **20/20**;
- stale/missing/mismatched pinned bindings: **0**;
- normal queue before live acceptance: **82**;
- `untranslated_game_count` before live acceptance: **82**;
- later duplicate present on PR branch: **no**.

No translation text was regenerated or modified.

### Mixed-success proof remains valid

The reconciled CI executed the focused pinned regression against the already-submitted checkpoint and emitted:

`{"pinned_checkpoint_accepted_count": 19, "pinned_checkpoint_diagnostic_count": 1, "pinned_checkpoint_error_count": 0, "pinned_checkpoint_result_count": 20, "pinned_failed_request_in_diagnostics": true}`

Therefore the intended result remains proven:
- **19 accepted**;
- **1 translation diagnostic**;
- **0 worker error results**;
- request `2aeac6b30b8bea9fcecd9be3269154b2bb4b84fefc3345986929ee9f4e23b76e` / AppID `1237980` is the diagnostic item.

Live canonical cache/status are intentionally not pre-written by this worker. They will change only after Director acceptance/merge causes the canonical ingest path to run.

### Reconciled check results

On head `f25cfadfcb09a56cc36a7ba6a8d393d7a0691829`:
- Validate execution ownership — run `37295407305` — **success**;
- Validate Progressive PASS 2 core — run `37295407282` — **success**;
- Validate backlog dispositions — run `37295407272` — **success**.

Execution-ownership CI also reconfirmed:
- `RUSSIAN_DESCRIPTION_TRANSLATION_CONTRACT_VALID`;
- Russian nonblocking publication/statistics regression: **ok**;
- Russian partial-accept/diagnostic regression: **ok**;
- real pinned checkpoint classification: **19 accepted + 1 diagnostic**.

### Remaining Director action

PR #145 is ready for Director acceptance and is not merged by this worker.

After merge, verify from fresh `main` that the existing canonical ingest workflow:
1. consumes the remaining pinned checkpoint only once;
2. persists 19 exact-bound `good_ru` translations;
3. creates one current translation diagnostic for AppID `1237980`;
4. rebuilds normal translation queue/status honestly;
5. triggers the normal downstream visual rebuild path.

No Scheduled Task was created or modified. No Dossier, Deep, Fast, ranking, expiry, or unrelated project logic was changed in this continuation.
