# Progressive pinned live-profile handoff fix 01 — durable report

Final status: `complete_ready_for_director_acceptance`

## 1. Task and architecture preflight

Task: `WORKER_TASK_PROGRESSIVE_PINNED_LIVE_PROFILE_HANDOFF_FIX_01.md`.

Preflight outcome before implementation:

1. GitHub remains the control-plane owner for Progressive scope, ordering, pin creation, work identity, validation, attempt/recovery accounting, persistence and completeness.
2. Scheduled ChatGPT remains semantic data-plane only.
3. Canonical profile authority remains `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json`.
4. Workers are forbidden to choose mutable/latest profile state.
5. GitHub freezes an exact immutable profile object before semantics and exposes an auditable exact reference.
6. A later live-profile update does not invalidate already-started exact work.
7. A newly frozen semantic generation uses the then-current live profile.
8. Arbitrary historical/unpinned results remain unauthorized.
9. GitHub performs only deterministic fetch/freeze/hash/binding work; it does not interpret or summarize taste semantics.
10. No new scheduler, recurring stage, retry daemon, semantic producer or cache authority was added.

## 2. Reused prior canonical decision and mechanism

The implementation reused the accepted live-profile freeze/pin design instead of creating a second profile lifecycle:

- `scripts/taste_pinned_work_unit.py`
- `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
- `config/execution_ownership_contract.json`

The shared freeze now exposes `freeze_current_live_profile(...)`: resolve external `main`, fetch the file at that exact commit, reread `main`, retry only while the head moved, and stop after the existing bounded attempt count. Once frozen, downstream validation rereads the exact immutable commit rather than requiring mutable `main` to remain unchanged.

## 3. Root defect

Fast and Deep work previously carried profile-related hashes in generation binding, but the semantic worker had no canonical personalized profile content/reference to read. In addition, Deep ingest rebuilt current work immediately before accepting a result, so a newer semantic/profile generation could make already-started Deep work appear stale.

That combination made personalized semantic completion structurally unreliable even when public game evidence existed.

## 4. Exact profile pin representation

Progressive now uses `PROGRESSIVE-PROFILE-PIN-V1`:

- `authority = github_pre_semantic_immutable_live_profile`
- canonical repository and path
- `resolved_commit_sha`
- Git `blob_sha`
- `content_sha256`
- exact byte count
- immutable raw URL using the exact commit
- `pin_sha256` over the canonical pin material

The pin is exposed in each Fast/Deep work manifest at top level and each item carries `profile_pin_sha256`. The pin SHA is part of the semantic generation/item identity and therefore of result validation.

Current validated production pin after deterministic rebuild:

- profile commit: `5e06acad2a3dc410d4d74177efc69752ade45865`
- profile blob: `9b9926031889dbd98ba6585c57836d52c739a0bb`
- profile content SHA256: `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`
- profile bytes: `269906`
- Progressive pin SHA256: `cf4a4ecf03e72d0d77c85c5e101ce4e37ab36b8547d1bcc1deada780a8df2a6c`
- semantic generation: `b33cc4416860bd15a37f530c9daef8fb7755ae440929f93aa915d5363e31c490`

A read-only validation fetched `gaming_taste_live.json` at that exact immutable commit, returned the expected Git blob SHA, and parsed it as a JSON object. No production semantic worker was invoked for this proof.

## 5. Fast handoff

`progressive_pass1_work.json` now exposes the exact `profile_pin`, and every Fast item includes `profile_pin_sha256`.

The Fast worker contract now requires, before semantic evaluation:

1. item pin SHA must match the manifest pin;
2. fetch only the canonical profile repository/path at `resolved_commit_sha`;
3. never read profile `main` or use chat memory as production taste evidence;
4. verify blob SHA, byte count and content SHA256;
5. parse and use those exact pinned bytes as the sole personalized profile.

If exact profile verification fails, the worker fails closed without substituting another profile or consuming the item.

Current deterministic manifest observation after rebuild: 531 Fast items, all under the pin-aware generation above.

## 6. Deep handoff

`progressive_pass2_work.json` exposes the same pin class and each Deep item binds `profile_pin_sha256` plus the pre-existing exact Dossier path/SHA/compatibility/expiry/authorization identity.

The Deep worker contract now requires the same exact pinned-profile fetch and verification as Fast. Dossier evidence remains a separate liveness gate.

Current deterministic manifest observation after rebuild: 27 Deep items under the same profile pin/generation; each retains exact Dossier binding.

## 7. Profile concurrency behavior before and after pin

Before/during freeze:

- if external `main` moves between the first and confirming head read, preparation retries toward the newer exact commit;
- retries are bounded by the existing freeze attempt count;
- repeated churn exhausts the bounded attempts and fails closed;
- no quiet window or user pause is required.

After freeze/start:

- exact work keeps its original immutable pin;
- mutable live-profile advancement does not alter that item;
- the worker never switches profile versions mid-item;
- a later work manifest may use a newer pin/generation.

The focused regression commits work A, advances current work to B, then commits result A. Git-history resolution still finds the exact A manifest that existed before the A result. An arbitrary C result with no prior prepared manifest is rejected.

## 8. Work identity and validation behavior

Changes:

- `profile_pin_sha256` is now in PASS 1 identity fields and therefore inherited by Deep identity.
- Deep result and terminal-receipt schemas require `profile_pin_sha256`.
- `scripts/progressive_work_authority.py` proves pre-semantic authority from Git history:
  - the artifact must have a durable introduction commit;
  - an earlier manifest in that artifact's ancestry must contain its exact deterministic submission path;
  - the item pin SHA must match that manifest's top-level pin;
  - already-consumed work IDs are not reopened;
  - an older historical item cannot overwrite a newer accepted authority.
- PASS 1 ingest accepts exact previously prepared in-flight work even if the current manifest advanced.
- PASS 2 ingest does the same, but independently revalidates current canonical Dossier path/SHA/binding/expiry before persistence.

The PASS 2 workflow no longer rebuilds semantic/profile work immediately before ingest. New work is still recomputed after the accepted-state transition through the existing GitHub-owned path.

## 9. Existing attempt-state transition

No Fast or Deep state file was manually reset or rewritten.

From task-start ref `1e4e2d9611850283dfc780e08d03145703ffbc38` through final validation:

- `data/cache/progressive_pass1_state.json` blob remained `dd7a00e5a3375a2a72035cacee24f3267f738256`;
- `data/cache/progressive_pass2_state.json` blob remained `eceac72a7c9f32fd29d97ca51d27dd59d0b74d9f`.

Those stores currently contain 190 historical Fast entries and 3 historical Deep entries. Because the corrected pin is part of semantic identity, the current generation legitimately projects those old entries as non-current and creates new exact work IDs under normal generation logic. This is an identity transition, not a manual attempt reset or retry authorization.

Current generated scope observation:

- Fast current scope 531; current-generation attempted 0; remaining 531.
- Deep current coverage target 531; current-generation attempted 0; 27 currently eligible/pending and 504 waiting for Dossier.

No historical state was deleted to obtain these counts.

## 10. Exact files changed

Implementation/control-plane files:

- `.github/workflows/ingest-progressive-pass2.yml`
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `config/execution_ownership_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/progressive_pass2_result_schema.json`
- `config/progressive_pass2_execution_receipt_schema.json`
- `scripts/taste_pinned_work_unit.py`
- `scripts/build_pre_ai_taste_projection.py`
- `scripts/progressive_pass1.py`
- `scripts/build_progressive_pass1_work.py`
- `scripts/ingest_progressive_pass1.py`
- `scripts/progressive_pass2.py`
- `scripts/build_progressive_pass2_work.py`
- `scripts/ingest_progressive_pass2.py`
- `scripts/progressive_work_authority.py`

Validation/regression files:

- `scripts/test_progressive_profile_pin.py`
- `scripts/test_progressive_pass1.py`
- `scripts/test_progressive_pass2.py`
- `scripts/test_progressive_pass2_integration.py`
- `scripts/test_progressive_pass2_workflow_staging.py`
- `scripts/test_progressive_personalization.py`

The final PASS 2 test-only adjustment updates a stale pre-stage-indicator assertion to coexist with the separately accepted UI stage indicator; no site behavior was changed by this task.

Task bookkeeping:

- `CURRENT_TASK.md`
- this durable report.

No Taste Dossier contract/schema/worker semantics file was changed.

## 11. PIN-01..20

- **PIN-01 PASS** — canonical authority remains `stopgame-ratings-data/gaming_taste_live.json`.
- **PIN-02 PASS** — bounded GitHub freeze records immutable commit/blob/content SHA/bytes before Progressive semantics.
- **PIN-03 PASS** — Fast work exposes a concrete immutable profile URL/reference and verifiable identity, not hashes alone.
- **PIN-04 PASS** — Deep exposes the same profile-pin class plus unchanged exact Dossier binding.
- **PIN-05 PASS** — Fast worker prompt requires exact pinned-profile read/verification and forbids mutable latest.
- **PIN-06 PASS** — Deep worker prompt requires the same exact pinned-profile read/verification.
- **PIN-07 PASS** — deterministic A→B fixture proves a head move during freeze retries to B.
- **PIN-08 PASS** — committed A-work remains resolvable after manifest/profile advances to B.
- **PIN-09 PASS** — profile pin SHA is immutable result identity; wrong pin/bytes fail validation.
- **PIN-10 PASS** — B produces a distinct new pin and semantic generation; production rebuild used the then-current immutable profile.
- **PIN-11 PASS** — unprepared C result has no prior Git manifest authority and is rejected.
- **PIN-12 PASS** — freeze retry is bounded; continuous churn fails closed with no quiet-window requirement.
- **PIN-13 PASS** — GitHub only freezes/fetches/hashes/binds bytes; no profile-summary AI or semantic GitHub stage was added.
- **PIN-14 PASS** — PASS 1/2 contract diff changes only version/pin/authority identity fields; fit/not-fit/business thresholds were not changed.
- **PIN-15 PASS** — Dossier contracts/evidence semantics were not changed; Deep still revalidates Dossier liveness independently.
- **PIN-16 PASS** — state blobs were not reset; normal/recovery ownership remains intact and no manual recovery/retry was authorized.
- **PIN-17 PASS** — focused/canonical workflow suites below are green.
- **PIN-18 PASS** — deterministic pre-AI rebuild produced coherent Fast and Deep manifests sharing the exact pin-aware semantic generation.
- **PIN-19 PASS** — no Scheduled Task action was performed and no Fast/Dossier/Deep production worker was manually triggered.
- **PIN-20 pending only until this report commit/reread** — completed by the closeout sequence for this report.

## 12. Exact validation / workflow / commit refs

Implementation commits:

- `4e9b2f84c77a59df89afdef5d126362ce5f16c4e` — core pinned-profile handoff and historical pre-semantic authority.
- `4a4a1261e6c682343d97a7b6fc5e3d7f2c2c2cd2` — focused regressions, ownership declaration, exact fixture updates.
- `7e7ef7b7e87fbc3f7f5e14883bfa838289015bae` — stale DEEP-22 test assertion aligned with the already accepted stage-indicator UI.

Automatic deterministic control-plane commits observed:

- `7e10b54ad418aaeb4881714a0c830a1a3293372f` — pin-aware atomic pre-AI refresh after the main implementation.
- `74bfe90793bc9e8ec2efa778d0a2e471c9139495` — subsequent successful atomic pre-AI refresh after the final test adjustment.

Successful workflows:

- Build pre-AI deterministic payload run **35951498530** / run number **189** — success; includes `test_progressive_profile_pin.py`, Progressive personalization and PASS 1 regression, work generation and canonical deterministic rebuild.
- Validate execution ownership run **35951498384** / run number **202** — success.
- Validate Progressive PASS 2 core run **35951599096** / run number **132** — success after stale DEEP-22 correction; covers PASS 2 core, integration, staging, PASS 1 and Progressive projection suites.
- Build pre-AI deterministic payload run **35951599021** / run number **191** — success after final test adjustment.

The first PASS 2 validation run on commit `4a4a126...` failed only on the obsolete DEEP-22 assertion that `deep_stage_state` must be absent from UI; the separately completed stage-indicator task had intentionally made that assertion false. The assertion was corrected without changing UI/runtime semantics, and run 132 then passed.

## 13. Natural concurrent production observations

Existing GitHub automation continued normally while this task was implemented. Source pushes automatically caused deterministic pre-AI and visual rebuild workflows; these were not manual Fast/Dossier/Deep semantic worker runs.

Accepted Fast/Deep state blob SHAs remained unchanged between the task-start ref and final validation, so no accepted Fast/Deep semantic state transition was observed in those stores during this task. This report does not assume that no external Scheduled Task invocation occurred; it only records that this chat did not modify or manually trigger those tasks and that acceptance does not depend on any natural semantic result.

## 14. Unresolved items

No blocker remains for the handoff fix itself.

Actual personalized fit/not-fit quality is intentionally **not** claimed by this task. The bounded readiness proof establishes that workers now receive and can verify the exact canonical personalized profile content. Real semantic quality can only be judged from later naturally scheduled results.

## 15. Final status

`complete_ready_for_director_acceptance`

## 16. Recommended next Director step

Accept this handoff fix, then observe the next naturally scheduled Fast/Deep results for the new pin-aware generation and verify that completed fit/not-fit outcomes begin appearing without changing the contract or manually retrying production work.
