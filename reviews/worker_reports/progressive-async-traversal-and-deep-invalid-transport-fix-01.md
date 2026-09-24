# Progressive Async Traversal + Deep Invalid Transport Fix 01 — durable worker report

Task: `progressive-async-traversal-and-deep-invalid-transport-fix-01`  
Mode: IMPLEMENT / VALIDATE  
Date: 2026-09-24

## 1. Final status

`complete_ready_for_director_acceptance`

The approved Fast asynchronous traversal, Deep invocation-start authority snapshot, and Deep invalid-transport cleanup policy are implemented and validated. No production semantic worker was manually run for acceptance.

Primary implementation commits:
- `69508034743e9d2ef4f96c2083eff089b0bb8bd3` — main implementation.
- `a470fe109825f8a7194b54ea63906a79d9bec366` — hardening that proves the claimed Deep run-start commit was still the latest first-parent main authority at the claimed run-start time.

## 2. Architecture preflight

All fixed architecture decisions remained true:

1. GitHub remains the sole owner of scope, order, canonical acceptance, attempt state, retry/recovery authorization, completeness and persistence.
2. Scheduled ChatGPT remains bounded semantic execution plus create-only candidate transport.
3. No new scheduler, queue owner, retry daemon, polling loop or canonical state owner was added.
4. Fast and Deep traverse only GitHub-prepared work.
5. Exact transport existence means only “already submitted / do not recreate”, never “accepted”.
6. Exact immutable profile pins and Git-history pre-semantic work authority remain mandatory.
7. Deep freshness moved from per-item mutable-current checks to one invocation-start boundary.
8. Later profile/Dossier/recovery/work changes are deferred to the next invocation and do not retroactively invalidate the current frozen run.
9. GitHub can prove the exact run-start authority from immutable Git history plus explicit run-start transport binding.
10. No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action was performed.

No Dossier progression/evidence contract or stage-independence architecture was changed.

## 3. Exact root causes repaired

### Fast

The worker prompt reloaded current GitHub work before each new item. That made semantic traversal effectively wait for GitHub ingest/manifest advancement even though sibling work had already been independently prepared.

### Deep

Two old freshness gates conflicted with the approved invocation snapshot model:
- the worker prompt reread/revalidated mutable Deep/Dossier state before later items;
- `ingest_progressive_pass2.py` called `prepared_work_item_dossier_is_live()` against mutable-latest Dossier state before persistence.

That allowed a legitimate run-start-authorized result to be invalidated by changes that happened after the invocation began.

### Invalid Deep transport

`rejected_invalid_result_no_attempt` and `rejected_invalid_execution_receipt_no_attempt` were not included in the active-inbox removal statuses. The attempt remained unconsumed, but the deterministic create-only path stayed occupied, producing a transport deadlock.

A further closeout review found that “historical commit containing prepared work” alone was not strong enough to prove that the commit was actually the current run-start authority. The hardening commit adds a first-parent Git-time boundary proof.

## 4. Fast traversal behavior before / after

Before:
- current manifest was reread before each next item;
- result A could indirectly serialize B on GitHub ingest/manifest advancement.

After:
- one exact PASS 1 manifest and exact profile pin are frozen at invocation start;
- only its ordered predeclared items may be traversed;
- after A is created, B may execute immediately without waiting for A ingest/removal/count advancement/manifest rebuild;
- an exact existing `submission_path` is only a do-not-recreate marker and traversal continues;
- stale/similarly named/wrong-generation/wrong-path artifacts are not markers;
- each frozen item is visited at most once per invocation;
- Fast malformed exact-current one-shot terminal-incomplete behavior is unchanged.

Canonical surfaces: `config/progressive_pass1_contract.json` v3 and `config/progressive_pass1_worker_prompt.md`.

## 5. Deep traversal behavior before / after

Before:
- worker semantics reread mutable Deep/Dossier state between games;
- ingest revalidated each candidate against mutable-current Dossier binding/expiry.

After:
- each invocation records one exact `run_start_authority_commit` and one `run_started_at_utc`;
- work manifest, ordered items, work mode, profile pin, Dossier path/SHA/compatibility/expiry state, and recovery authorization identity/reason/binding are frozen once from that exact Git revision;
- exact pinned profile bytes are verified once for the invocation;
- Dossier liveness is established at the invocation boundary;
- later mutable profile/Dossier/recovery/manifest/progress changes are not reread between games;
- sibling ingest/attempt advancement is not required before the next run-start item;
- exact existing result/terminal transport means do-not-rerun only, not acceptance;
- GitHub ingest validates the returned artifact against the exact run-start authority, not mutable-latest Dossier state.

The Deep result and execution-receipt schemas now require `run_start_authority_commit` and `run_started_at_utc`.

## 6. Deep invalid transport behavior before / after

Before:
- invalid exact-current result/terminal receipt could be classified as zero-attempt but remain at the active deterministic inbox path.

After:
1. semantic state remains unchanged for invalid transport;
2. existing ingest rejection status/reason is persisted;
3. `write_ingest_receipts(...)` happens before active-file cleanup in the canonical writer workspace;
4. invalid-no-attempt statuses are included in `removable_names(...)`;
5. the canonical writer stages receipt creation and inbox deletion together in one Git persistence transaction;
6. no same-invocation retry is authorized;
7. a later invocation may submit again only if its then-current GitHub run-start authority still authorizes the item.

Valid semantic execution still consumes attempts exactly once.

## 7. Rejected-error persistence; no raw archive / new fingerprint

Implemented policy:
- existing ingest receipt persistence is retained;
- rejection reason is preserved, including run-start authority failure detail when applicable;
- active invalid candidate is deleted only after the receipt exists in the local canonical-writer transaction;
- no separate raw rejected-payload archive was created;
- no new rejected-payload fingerprint/hash field was added;
- existing SHA-256 use for ingest-receipt filename identity remains unchanged;
- the old rejection receipt remains available after a later valid submission because the existing content-based receipt filename differs for different transport bytes.

Focused regression asserts both schema/source absence of a new rejected-payload fingerprint and persistence of separate old-rejection and later-success receipts.

## 8. Work-authority / path-reuse design implemented

Deep transport carries the minimal new durable run-start identity:
- `run_start_authority_commit`;
- `run_started_at_utc`.

`progressive_work_authority.resolve_presemantic_work_item_at_commit(...)` resolves the exact manifest at that commit and requires the exact full prepared transport path plus exact profile pin binding.

`progressive_pass2.validate_run_start_authority(...)` reads the exact Dossier bytes from that Git commit, verifies content SHA, compatibility identity and expiry at the run-start boundary, and never consults mutable-latest Dossier state.

Hardening in `a470fe109825f8a7194b54ea63906a79d9bec366` additionally proves:
- the authority commit is on the result’s first-parent main lineage;
- the authority commit existed by `run_started_at_utc`;
- no later first-parent main commit had already superseded it by that time;
- the result transport commit does not predate the claimed invocation start.

Therefore an arbitrary older prepared commit is not sufficient.

Same deterministic path reuse remains safe after GitHub-owned invalid cleanup. `result_introduction_commit(...)` finds the durable add commit whose bytes equal the currently present artifact, so a deleted bad file followed by a later create-only valid re-add resolves to the new introduction commit. Focused regression proves reject/delete/re-add on the same exact path.

## 9. Files changed

Implementation-owned changes:
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/execution_ownership_contract.json`
- `config/progressive_pass2_result_schema.json`
- `config/progressive_pass2_execution_receipt_schema.json`
- `scripts/progressive_work_authority.py`
- `scripts/progressive_pass2.py`
- `scripts/ingest_progressive_pass2.py`
- `scripts/test_progressive_async_traversal.py`
- `scripts/test_progressive_pass2_integration.py`
- `.github/workflows/validate-progressive-pass2-core.yml`
- `PROJECT_DECISIONS.md` (PPD-006 durable rationale)

No Dossier worker/progression/evidence file and no Scheduled Task configuration was changed.

## 10. Tests / workflows and exact refs

Final hardening validation:
- commit `a470fe109825f8a7194b54ea63906a79d9bec366`
- GitHub Actions run `35975616173` — **Validate Progressive PASS 2 core: success**
  - Compile PASS 2 Python — success
  - Progressive async traversal + invalid transport regression — success
  - PASS 2 core regression — success
  - PASS 2 Dossier integration regression — success
  - PASS 2 canonical-writer staging regression — success
  - PASS 1 regression — success
  - PASS 1 ingest activation regression — success
  - PASS 1 canonical-writer staging regression — success
  - Progressive personalization regression — success
  - Current staged projection accounting — success
  - Unresolved-row preservation regression — success
  - Visual activation routing regression — success
  - UI provenance regression — success
  - Recompute active production eligibility without consuming attempts — success

Final deterministic production projection validation:
- run `35975616059` — **Build pre-AI deterministic payload: success**
  - Progressive PASS 1 work build — success
  - Progressive personalization/PASS 1 regression step — success; this step includes `test_progressive_profile_pin.py`
  - Dossier regression suite — success
  - Progressive PASS 2 eligibility recompute — success
- run `35975616058` — **Build daily visual payload: success**

Initial implementation validation:
- commit `69508034743e9d2ef4f96c2083eff089b0bb8bd3`
- run `35975091837` — Validate Progressive PASS 2 core: success
- run `35975091806` — Validate execution ownership: success
- run `35975091938` — Build pre-AI deterministic payload: success
- run `35975091877` — Build daily visual payload: success

Tests were strengthened; no acceptance test was weakened or skipped to obtain green status.

## 11. Acceptance matrix

### Fast

- **F-01 PASS** — contract/prompt freeze one invocation-start manifest and explicitly forbid waiting for A ingest before B; focused regression asserts `prior_sibling_ingest_required=false` and the A→B no-wait rule.
- **F-02 PASS** — exact existing current path is do-not-recreate and traversal continues; focused regression asserts this contract/prompt behavior.
- **F-03 PASS** — `existing_transport_implies_canonical_acceptance=false`; prompt explicitly forbids acceptance/attempt inference.
- **F-04 PASS** — stale/wrong-generation/wrong-path transport is explicitly not a submitted marker; focused regression asserts the contract.
- **F-05 PASS** — existing Fast invalid exact-current one-shot terminal-incomplete policy remains unchanged; PASS 1 regression passed in run `35975616173`.
- **F-06 PASS** — exact profile pin model remains; `test_progressive_profile_pin.py` passed inside run `35975616059`, and focused regression asserts later live update does not invalidate already-pinned work.

### Deep run-start snapshot / traversal

- **D-01 PASS** — one exact run-start view; sibling ingest wait disabled; focused regression + prompt.
- **D-02 PASS** — exact manifest item, work mode, profile pin, Dossier SHA/binding/expiry and recovery fields are frozen; exact-commit resolver and schemas bind returned transport to that view.
- **D-03 PASS** — temp-Git regression changes Dossier after run start and proves the frozen result remains valid.
- **D-04 PASS** — same regression proves a later invocation sees changed Dossier bytes and cannot silently reuse the old binding.
- **D-05 PASS** — expired-before-boundary Dossier is rejected by the focused boundary test.
- **D-06 PASS** — exact run-start Dossier is loaded from historical Git bytes and accepted despite later mutable change; mutable-current ingest liveness gate removed.
- **D-07 PASS** — both unprepared authority and older historically prepared-but-already-superseded authority fail closed; first-parent/time proof added in `a470fe109825f8a7194b54ea63906a79d9bec366`.
- **D-08 PASS** — `prior_fast_attempt_required=false` and `global_fast_completion_required=false`; focused regression asserts both.

### Deep invalid transport

- **D-09 PASS** — malformed exact authorized result returns `rejected_invalid_result_no_attempt`, leaves state unchanged, becomes removable; focused regression + staging regression.
- **D-10 PASS** — malformed exact authorized terminal receipt returns `rejected_invalid_execution_receipt_no_attempt`, leaves state unchanged, becomes removable; focused regression + staging regression.
- **D-11 PASS** — contract names GitHub next-invocation authority as retry owner and forbids same-invocation retry.
- **D-12 PASS** — focused regression proves later valid result is accepted once and replay is ignored.
- **D-13 PASS** — focused regression writes old rejection then later valid receipt and proves both durable receipt records coexist.
- **D-14 PASS** — contract and source assert no raw rejected-payload archive.
- **D-15 PASS** — schemas/source contain no new rejected-payload fingerprint field; focused regression asserts this.
- **D-16 PASS** — invalid/failed sibling blocking remains false; no sibling ingest wait.
- **D-17 PASS** — stale/mismatched/unprepared authority remains fail-closed; current-invalid fallback is limited to an exact current deterministic path/identity.

### Ownership / cross-stage

- **O-01 PASS** — GitHub remains sole canonical acceptance/attempt/recovery owner; ownership validation passed.
- **O-02 PASS** — no scheduler/queue/retry daemon/polling owner added.
- **O-03 PASS** — implementation diff contains no Dossier behavior file changes; Dossier regression suite passed in `35975616059`.
- **O-04 PASS** — no Scheduled Task settings/action were changed or invoked.
- **O-05 PASS** — no Fast/Dossier/Deep semantic production backlog was manually processed; only GitHub CI/deterministic builders ran.

## 12. Natural concurrent production observations

Normal GitHub production continued during validation, as permitted by the task. After implementation/hardening commits, standard pre-AI/visual/runtime workflows advanced `main` with data-only commits. Compare checks showed those follow-up commits did not overwrite the implementation source/contract files.

The initial implementation push also triggered `Validate SteamDB true-miss runtime resolutions` run `35975091881`, which failed in its stage-15 SteamDB validation step. The Progressive implementation commit did not modify SteamDB validation/runtime files, and all task-relevant Progressive/ownership/pre-AI/visual gates were green. This unrelated workflow observation was not used for acceptance and no SteamDB remediation was attempted in this task.

No natural semantic Fast/Dossier/Deep result was required or manually induced for validation.

## 13. Unresolved items

None in task scope.

The unrelated SteamDB true-miss validation failure above remains outside this task and is intentionally not diagnosed/fixed here.

## 14. Final Director recommendation

**Accept.**

The requested behavior is implemented with GitHub-owned authority preserved, Deep freshness moved to the approved invocation boundary, invalid zero-attempt transport deadlock removed, same-path reuse proven, arbitrary historical authority hardened fail-closed, and all task-specific validation gates green.
