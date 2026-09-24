# Progressive Async Traversal + Deep Invalid Transport Fix 01 — durable worker report

Task: `progressive-async-traversal-and-deep-invalid-transport-fix-01`  
Mode: IMPLEMENT / VALIDATE  
Date: 2026-09-24  
Final status: `complete_ready_for_director_acceptance`

## 1. Director-review correction DRG-01

The first implementation correctly removed Fast/Deep sibling-ingest waits and per-item mutable Deep rereads, but its Deep run-start proof still depended on `run_started_at_utc` written by the semantic worker. Director review correctly rejected that proof: an older prepared authority A plus a forged earlier worker time could falsely look current even if `main` had already advanced to B before the real invocation began.

DRG-01 is now fixed without restoring checks between games.

Deep now establishes exactly one GitHub-confirmed invocation boundary before semantic execution:

1. worker reads one proposed current `main` commit;
2. worker creates one exact create-only `PROGRESSIVE-PASS2-RUN-START-MARKER-V1`;
3. the existing GitHub PASS 2 ingest workflow confirms that marker;
4. the marker commit's **actual Git first parent** becomes `run_start_authority_commit`;
5. the marker commit's **Git committer time** becomes the trusted `run_started_at_utc`;
6. GitHub writes a durable `PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1`;
7. semantic execution may start only after that confirmed receipt exists;
8. every result/terminal receipt binds to `run_start_anchor_commit + run_start_authority_commit + run_started_at_utc`;
9. GitHub ingest requires the confirmation receipt to have existed before result transport and independently re-proves the marker/parent/time relation.

The worker's own timestamp is no longer authority. It can only echo the GitHub-confirmed time.

## 2. Architecture / ownership

Preserved invariants:

- GitHub remains sole owner of scope, order, canonical acceptance, attempts, recovery authorization, completeness and persistence.
- Scheduled ChatGPT remains bounded semantic execution plus repository-defined create-only transport.
- No new scheduler, queue, retry daemon, polling loop or canonical state owner was introduced.
- The new start marker is a one-time invocation-boundary handshake through the existing PASS 2 ingest workflow.
- There is no per-item mutable-main, Dossier, profile, recovery-authorization or progress reread after the start receipt is confirmed.
- Later GitHub/profile/Dossier/recovery/work changes belong to the next invocation and do not retroactively invalidate the frozen run.
- Exact transport existence still means only “already submitted / do not recreate”, never canonical acceptance.
- Fast and Deep remain independent; Deep has no Fast-attempt/global-Fast-completion prerequisite.
- Dossier runtime/progression/evidence behavior is unchanged.
- No Scheduled Task create/edit/enable/disable/pause/reschedule/run action was performed.

Canonical ownership/rationale surfaces updated:
- `config/progressive_pass2_contract.json` v7;
- `config/progressive_pass2_worker_prompt.md`;
- `config/execution_ownership_contract.json`;
- `PROJECT_DECISIONS.md#PPD-006`.

## 3. Exact DRG-01 start proof

### Marker

Before semantic execution the worker creates exactly:

`data/ai_inbox/progressive_pass2/run_starts/{observed_main_commit}--{run_start_nonce}.json`

with only:
- `schema_version: 1`;
- `contract: "PROGRESSIVE-PASS2-RUN-START-MARKER-V1"`;
- `observed_main_commit`;
- fresh lowercase 32-hex `run_start_nonce`.

No worker timestamp is stored in the marker.

### GitHub confirmation

`scripts/ingest_progressive_pass2.py::process_run_start_markers` and `scripts/progressive_work_authority.py::validate_run_start_marker_commit` require:

- marker has an immutable Git introduction commit;
- marker commit has exactly one parent;
- that real parent exactly equals `observed_main_commit`;
- marker commit adds only that exact marker path;
- durable marker bytes at that commit exactly match the marker JSON;
- PASS 2 contract/work were active at the real parent;
- prepared top-level profile pin is valid.

GitHub then writes:

`data/cache/progressive_pass2_run_start_receipts/{run_start_anchor_commit}.json`

with `status: confirmed`, actual parent authority, Git-derived start time, nonce, marker path, generation and profile pin. The active marker is removed by the same canonical writer.

### Result acceptance

For each Deep result/terminal artifact, GitHub:

- reads `run_start_anchor_commit` from transport;
- finds the exact confirmed receipt **in the Git parent that existed before result transport**;
- revalidates the marker commit and its actual parent;
- requires receipt introduction to be on the result lineage and persisted by canonical `steam-kz-bot`;
- requires transport authority/time to exactly equal the confirmed receipt;
- resolves work from that confirmed authority commit;
- verifies exact profile pin/generation;
- validates exact historical Dossier bytes/expiry at the GitHub-confirmed start time.

Therefore choosing an earlier `run_started_at_utc` cannot change which Git state was actually current at start.

## 4. Mandatory forged-time regression

`scripts/test_progressive_async_traversal.py` now contains the required Director scenario:

1. exact Deep state A is prepared;
2. `main` advances to replacement state B before the invocation;
3. a real run-start marker is created after B and GitHub confirms B as the actual marker parent;
4. result transport references old A and forges `run_started_at_utc` to a time before B;
5. GitHub confirmation still says B;
6. the A result is rejected as `rejected_invalid_result_no_attempt`;
7. Deep semantic state remains unchanged.

The same regression then proves:

- a result bound to the real confirmed B authority succeeds;
- a later Dossier change C made after start confirmation does **not** invalidate the already-confirmed B run;
- the next invocation anchors the newer state and sees the changed Dossier;
- no per-game mutable-current check is used.

The focused step `Progressive async traversal + invalid transport regression` passed in PR run `35981637513` and again in main PASS 2 run `35981732708`.

## 5. Asynchronous Fast/Deep traversal remains intact

### Fast

The previously accepted Fast fix remains unchanged:

- one exact PASS 1 manifest/profile pin is frozen once per invocation;
- ordered predeclared siblings may run without waiting for prior sibling ingest/manifest advancement;
- exact current transport is a do-not-recreate marker only;
- stale/wrong-generation/wrong-path artifacts do not count as submitted;
- Fast malformed exact-current payload keeps the existing one-shot terminal-incomplete behavior.

### Deep

After the single GitHub run-start confirmation:

- work manifest/order/work mode/profile pin/Dossier SHA+binding+expiry/recovery authorization are frozen once;
- exact pinned profile bytes are verified once;
- no mutable manifest/Dossier/profile/recovery/progress checks occur between items;
- A submission does not have to be ingested before B executes;
- exact existing result/terminal transport means do-not-rerun, not acceptance;
- same-invocation retry after invalid-transport cleanup remains forbidden.

Current contract explicitly has:
- `per_item_mutable_manifest_dossier_or_authorization_reread=false`;
- `prior_sibling_ingest_required=false`;
- `prior_sibling_attempt_advancement_required=false`;
- `github_run_start_confirmation_required=true`;
- `worker_supplied_run_started_at_is_authority=false`.

## 6. Deep invalid transport policy remains unchanged

The accepted DR-01 policy from the original implementation is preserved:

- malformed/invalid exact authorized Deep result or execution receipt consumes zero semantic attempts;
- GitHub persists the existing rejection receipt first;
- GitHub removes the bad active deterministic inbox candidate in the same canonical-writer transaction;
- no raw rejected-payload archive exists;
- no rejected-payload fingerprint field exists;
- the semantic worker never retries the freed path in the same invocation;
- only a later invocation with a new then-current GitHub-confirmed start view can submit again.

Same-path delete/re-add authority resolution remains regression-covered.

## 7. Files changed for DRG-01

Runtime / contracts:
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/progressive_pass2_result_schema.json`
- `config/progressive_pass2_execution_receipt_schema.json`
- `config/execution_ownership_contract.json`
- `PROJECT_DECISIONS.md`

Git/GitHub authority and ingest:
- `scripts/progressive_work_authority.py`
- `scripts/progressive_pass2.py`
- `scripts/ingest_progressive_pass2.py`
- `.github/workflows/ingest-progressive-pass2.yml`
- `scripts/stage_progressive_pass2_canonical_writer.sh`

Validation:
- `scripts/test_progressive_async_traversal.py`
- `scripts/test_progressive_pass2_integration.py`
- `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py`

The Dossier test file change is validation-harness-only: it now follows already-existing PASS 1/PASS 2 staging helper scripts and PASS 2 ingest-owned recomputation instead of requiring those paths/command strings literally inside workflow YAML. No Dossier runtime, contract, prompt, progress, evidence or recovery behavior was changed.

## 8. Exact implementation refs

Original async/invalid-transport implementation:
- `69508034743e9d2ef4f96c2083eff089b0bb8bd3`
- `a470fe109825f8a7194b54ea63906a79d9bec366`

Director correction:
- PR `#95`
- validated PR head: `f8bae5c6f0f7f9d65428ae29336464955b1a51d3`
- squash merge to `main`: `1fe2fa668320626fb1f471b08f465d87512792dc`

Post-merge canonical derived commits:
- visual: `8c515b1ff0f026ad1bcbca79a7c3e8b7dbd479b4`
- pre-AI: `aaa10533313fbacdb0a78eb406708c576f8dd27b`

## 9. Validation

### PR #95 final head

- `35981637513` — **Validate Progressive PASS 2 core: success**
  - Compile PASS 2 Python — success
  - Progressive async traversal + invalid transport regression — success
  - PASS 2 core regression — success
  - PASS 2 Dossier integration regression — success
  - PASS 2 canonical-writer staging regression — success
  - PASS 1 regression — success
  - PASS 1 ingest activation regression — success
  - PASS 1 canonical-writer staging regression — success
  - Progressive personalization regression — success
  - current projection accounting — success
  - unresolved-row, visual routing and UI provenance — success
  - active production eligibility recompute without attempt consumption — success
- `35981637494` — **Validate buffered Steam review dossier runtime: success**
- `35981637894` — **Validate backlog dispositions: success**

The Dossier gate initially exposed two stale test assumptions about staging helpers/recompute placement that already differed on pre-task main. Only the regression harness was updated; no Dossier behavior was altered. The final Dossier run above is green.

### Fresh main after merge

- `35981732708` — **Validate Progressive PASS 2 core: success**
- `35981732888` — **Validate execution ownership: success**
- `35981732886` — **Validate backlog dispositions: success**
- `35981732695` (#195) — **Build pre-AI deterministic payload: success**
- `35981732905` (#575) — **Build daily visual payload: success**

An unrelated `Validate SteamDB true-miss runtime resolutions` push run `35981732674` failed outside the Progressive/Deep surfaces. This task changed no SteamDB runtime/validation behavior and did not attempt SteamDB remediation.

## 10. Acceptance matrix

- **F-01..F-06 PASS** — accepted Fast async traversal/profile-pin semantics remain intact.
- **D-01 PASS** — one frozen Deep invocation view, now GitHub-confirmed.
- **D-02 PASS** — work/profile/Dossier/recovery identity frozen from confirmed authority.
- **D-03 PASS** — later Dossier change does not invalidate the current confirmed run.
- **D-04 PASS** — next invocation sees newer state.
- **D-05 PASS** — expired-at-start Dossier remains fail-closed.
- **D-06 PASS** — exact historical Dossier bytes at confirmed authority are used; mutable-latest ingest liveness is not reapplied.
- **D-07 PASS** — stale/unprepared authority is fail-closed.
- **D-08 PASS** — Deep still has no Fast prerequisite/global Fast barrier.
- **D-09..D-17 PASS** — zero-attempt invalid transport cleanup, no raw archive/fingerprint, path reuse, sibling independence and stale/mismatched fail-closed semantics remain intact.
- **O-01 PASS** — GitHub remains canonical control plane.
- **O-02 PASS** — no new scheduler/queue/retry daemon/polling owner.
- **O-03 PASS** — Dossier behavior unchanged.
- **O-04 PASS** — no Scheduled Task settings/action invoked.
- **O-05 PASS** — this worker did not manually execute Fast/Dossier/Deep production backlog.
- **DRG-01 PASS** — old replaced authority A + forged earlier worker time cannot be accepted as current; actual run-start state is anchored by one GitHub-confirmed marker/receipt before semantics, and no per-item mutable checks were restored.

## 11. Fresh-main state observation

After normal external production and post-merge deterministic rebuilds, fresh `main` showed:

- PASS 2 contract version: `7`, active;
- `github_run_start_confirmation_required=true`;
- `worker_supplied_run_started_at_is_authority=false`;
- `per_item_mutable_manifest_dossier_or_authorization_reread=false`;
- current Deep work: 30 prepared items;
- current Deep durable state: 4 physical entries.

No active `data/ai_inbox/progressive_pass2/run_starts` directory and no production `data/cache/progressive_pass2_run_start_receipts` directory existed at the final observation, so this implementation task itself did not manufacture a production run-start marker/receipt. Normal external production may advance independently after this report.

## 12. Unresolved items

None in DRG-01/task scope.

The unrelated SteamDB true-miss validation failure remains outside this task.

## 13. Final Director recommendation

**Ready for repeat Director review / acceptance.**

DRG-01 is closed by a GitHub-owned, one-time invocation-start confirmation. Worker-controlled time can no longer select an older authority, the required A→B forged-time regression is green, and the accepted no-checks-between-games asynchronous traversal remains unchanged.
