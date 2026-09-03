# System Audit — 02

Date: 2026-09-03
Role: `SYSTEM AUDITOR`
Mode: `READ-ONLY / AUDIT`
Status: `complete`

## Scope and boundary

This audit reviewed the current production system end to end using the compact accepted control/report set required by `WORKER_TASK_SYSTEM_AUDIT_02.md`, followed by only bounded current evidence needed to verify specific system-level findings.

No production code, configuration, data, queue, ranking/Taste policy, provider implementation, release, or mobile implementation was changed. The only repository write performed by this audit is this report, as required by the task output contract.

The active mobile-feed continuation in Chat 1 was not inspected or judged as accepted implementation. The mobile incident is treated only as an active production incident and as evidence of a system-level failure class.

## Executive conclusion

The post-baseline semantic-runtime work materially improved the system and closes the original queue-as-heartbeat defect: the repository now has a durable accepted-runtime receipt, correlates accepted progress to the exact current source scope, and explicitly reports when current-scope progress has not been observed.

The semantic incompleteness fix is only partially closed end to end. Canonical pre-AI/publication state now truthfully distinguishes partition completion from unresolved semantic work and marks materially incomplete state as `degraded`; however, the current production UI does not consume or visibly present `status`, `semantic_completeness`, or `semantic_runtime_observability`. A user can therefore still see an apparently ordinary recommendation feed while hundreds of semantic rows are unresolved.

The visual-freshness failure mode is fixed and accepted on its implementation branch, but it is not closed in production. Current `main` still runs the pre-fix build/deploy workflow blobs and does not have the accepted exact build-receipt/deploy-binding mechanism active.

The accepted semantic and visual fixes did not introduce a duplicate scheduler, queue, semantic runtime, build workflow, deploy workflow, or canonical ownership boundary. The main remaining ownership ambiguity is pre-existing: two legacy one-shot Taste workflows remain dispatchable `contents: write` paths that can directly mutate the canonical Taste overlay outside the current transactional inbox path.

The current mobile incident reveals a separate user-result acceptance blind spot: a green Pages deploy and existing UI regressions do not prove prompt usable feed availability on the affected real device. The first resilience fix removed the silent blank state but only partially satisfied the real-device result; the direct continuation remains active in Chat 1 and is outside this audit's implementation scope.

## Required audit questions

### 1. Baseline Finding 1 — semantic execution observability

**Classification: `closed`**

The accepted semantic-runtime work now provides a truthful durable operational signal independent of queue presence.

Current durable evidence at `data/cache/taste_ingest_receipts/latest_runtime_status.json` records:

- runtime owner: `scheduled ChatGPT production task`;
- last successful and accepted semantic execution: `2026-09-01T21:03:08+00:00`;
- accepted batch: `4f99eff1753a8ac9480e`;
- accepted result count: `11`;
- queue progress: `37 -> 26`, delta `11`;
- `queue_presence_is_not_heartbeat=true`.

The current prepared semantic scope is newer (`2026-09-02T20:36:22.419743+00:00`) than the last accepted progress scope (`2026-09-01T20:47:04.563817+00:00`), and the current canonical pre-AI manifest truthfully reports:

- `semantic_runtime_observability.status=no_current_scope_progress_observed`;
- `current_scope_progress_observed=false`.

The scheduler platform enabled-state and exact cadence/next-run remain `not_exposed_to_repository`, but that limitation is explicit rather than fabricated. Queue existence or old accepted work therefore cannot masquerade as a current execution heartbeat.

Exact evidence:

- `reviews/worker_reports/semantic-runtime-completion-fix-01.md` blob `b414aa0d41929a8e125833b79caee74a9f022049`
- `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md` blob `5b4a25c89845ab258651a30608658e90d7d1840d`
- `data/cache/taste_ingest_receipts/latest_runtime_status.json` blob `cfeb41a044e90551ee35118f28636425a510fa26`
- `data/production/pre_ai/chatgpt_payload.json` blob `b350b1d5b679ce995988107a1d5e716cf447acd3`

### 2. Baseline Finding 2 — semantic incompleteness visibility

**Classification: `partially_closed`**

The canonical publication contract is now correct, but the user-visible surface is not yet carrying that truth.

Current canonical pre-AI state clearly distinguishes:

- `complete_family_partition=true` / `scope_partition_complete=true`;
- `unresolved_semantic_count=644`;
- `resolved_semantic_count=0`;
- `total_relevant_semantic_scope=644`;
- `sufficiently_complete_for_publication=false`;
- semantic/top-level `status=degraded`.

Current visual construction also still imports and applies the accepted semantic status helper (`apply_visual_semantic_status`). Therefore partition accounting can no longer be confused with semantic completion inside canonical artifacts.

However, current production `web/app.js` does not consume `data.status`, `semantic_completeness`, or `semantic_runtime_observability`. It loads the payload, extracts `items`, builds/renders the queue, and shows only a source timestamp via `sourceLabel()`/`#freshness`. There is no explicit degraded/incomplete user-facing state tied to unresolved semantic scope.

Therefore a materially unresolved semantic scope can still be presented to the user as an apparently ordinary complete feed, even though the repository payload truth is degraded.

Exact evidence:

- `data/production/pre_ai/chatgpt_payload.json` blob `b350b1d5b679ce995988107a1d5e716cf447acd3`
- `scripts/build_visual_feed_v2.py` blob `4b303abe6e204c1ffaa9ef6083685ee38c3382fb`
- `web/app.js` blob `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5`
- accepted semantic report blob `5b4a25c89845ab258651a30608658e90d7d1840d`

### 3. Baseline Finding 3 — visual stale-success risk

**accepted_fix_readiness: `accepted / ready_for_release`**

The accepted branch implementation correctly adds a durable build freshness receipt, explicit `degraded/no_fresh_build` classification, exact triggering-run binding, and fail-closed deploy verification. Acceptance passed fresh, no-build/degraded, stale-mismatch, and ownership/regression controls.

Accepted refs:

- implementation report blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`
- acceptance report blob `6a691fb29d88b1785accf717752149e027265a2c`
- accepted branch build workflow blob `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`
- accepted branch deploy workflow blob `7479a56ac7ee363e6a212952e58f36558b371877`

**production_closure_state: `still_open`**

Current production `main` still uses the old workflow blobs:

- `.github/workflows/build-daily-visual-payload.yml` blob `2d56b81f822412c433852d55a749a4db8ce33b78`
- `.github/workflows/deploy-visual.yml` blob `625a22da18300795974ba6e3b46c6b92db1184d4`

The current build path can still classify history readiness as false and exit that readiness step successfully without a visual build. The current deploy path still checks out current `main`, stages the existing canonical `data/production/visual/current.json`, and deploys it without the accepted exact triggering-run freshness receipt binding.

Therefore the baseline production failure mode must not be called closed until the accepted branch is actually released and exercised in production.

### 4. Ownership / duplicate mechanisms

The accepted semantic fix did **not** introduce a second scheduler, semantic runtime, queue, or manual semantic persistence path. `config/execution_ownership_contract.json` remains unchanged and still assigns production scope/queue/retry/completeness/orchestration to GitHub and only bounded external semantic work to the scheduled ChatGPT runtime.

The accepted visual fix did **not** introduce a second build workflow, deploy workflow, or production data plane; it adds a receipt contract inside the existing build/deploy chain.

The remaining ownership ambiguity is the pre-existing legacy Taste mutation surface:

- `.github/workflows/persist-ai-pilot-25.yml` still has `workflow_dispatch`, `contents: write`, invokes `scripts/ingest_taste_results.py`, and commits `data/cache/taste_fit.entry_overlay.json` directly to `main`;
- `.github/workflows/test-one-real-taste-persistence.yml` still has the same dispatch/write shape and directly commits the overlay;
- the current canonical production ingest path is `.github/workflows/ingest-taste-batch.yml`, which validates transactional proof, runs `scripts/process_taste_inbox.py`, and commits synchronized overlay/index/receipts/pre-AI consumer state.

Both one-shot workflows have narrow historical preconditions that are unlikely to match current state, so successful current mutation is not proven. The ownership risk therefore remains a bounded `risk_hypothesis`, not a proven present corruption path.

Exact evidence:

- ownership contract blob `f0b5f48756489965ec223a42f3b234f62ac4bae1`
- canonical ingest workflow blob `3242fbe96fba9ab6a2165176a852a0fedbead759`
- legacy pilot workflow blob `ccfbcd2f703d6cf40fd2277985fdc0ee6e823bbb`
- legacy one-real workflow blob `6c023ef5c7f91ef4f2ff183707cd69d595e10a50`

## Significant current findings

### Finding 1 — Canonical semantic degraded truth is not visible in the user-facing feed

**User impact**

Users can receive an apparently normal recommendation list while a materially large semantic scope is unresolved. Games blocked behind unresolved semantic work can therefore be absent without the page visibly saying that the recommendation set is incomplete/degraded.

**Exact evidence**

- Current pre-AI manifest blob `b350b1d5b679ce995988107a1d5e716cf447acd3` reports `status=degraded`, `complete_family_partition=true`, `unresolved_semantic_count=644`, `sufficiently_complete_for_publication=false`, and `current_scope_progress_observed=false`.
- Current visual builder blob `4b303abe6e204c1ffaa9ef6083685ee38c3382fb` applies `apply_visual_semantic_status(output, payload)`.
- Current `web/app.js` blob `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5` loads the payload and renders `items`/timestamp but does not consume or display `status`, `semantic_completeness`, or `semantic_runtime_observability`.

**Severity:** `high`

**Certainty:** `proven`

**Bounded verification/fix candidate**

Add one bounded publication/UI acceptance that requires an explicit visible degraded/incomplete state whenever canonical `sufficiently_complete_for_publication=false`, preserving all existing Taste/ranking semantics. Prove the visible state from a fixture with partition complete plus non-zero unresolved semantic scope.

### Finding 2 — Accepted visual freshness control is not active in production

**User impact**

Production can still report a successful visual build/deploy chain while publishing an older canonical payload after a no-build path. For a sale feed, that can silently present stale deals as if the daily publication were fresh.

**Exact evidence**

- Accepted fix/acceptance blobs: `e5226710d435cfbb1c0190e11d937b025ceb9aac`, `6a691fb29d88b1785accf717752149e027265a2c`.
- Accepted branch workflow blobs: build `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`, deploy `7479a56ac7ee363e6a212952e58f36558b371877`.
- Current production `main` still uses build blob `2d56b81f822412c433852d55a749a4db8ce33b78` and deploy blob `625a22da18300795974ba6e3b46c6b92db1184d4`, without the accepted receipt/binding mechanism.
- `DIRECTOR_TASK_BOARD.md` explicitly records the accepted branch as ready but release-deferred during the mobile incident.

**Severity:** `high`

**Certainty:** `proven`

**Bounded verification/fix candidate**

After the active mobile incident is stabilized, release the already accepted visual-freshness branch through the normal production path and capture one ordinary production build/deploy proving the receipt classification and exact triggering-run binding. Do not redesign the accepted fix.

### Finding 3 — Green Pages deployment does not prove prompt usable mobile feed availability

**User impact**

On the affected real device, repeated reloads can still spend several seconds in `Загружаю игры…` before cards appear. The first fix prevents a silent blank hole, but the user's practical result — prompt availability of the feed — is not yet stabilized.

**Exact evidence**

- Recon blob `48700dc77ac17fa031dd129996bef74075d86872` identified the original single-shot/unbounded bootstrap dependency and lack of recovery.
- First-fix report blob `61b23ffc479dff473310b1d7aed0d36d43a11c8f` records production deploy run `33766838776` as successful but leaves task status `needs_user_action` pending real-device acceptance.
- `DIRECTOR_TASK_BOARD.md` blob `7c0fe0e13704643275e7a37604e613be90939579` records the actual device result as only partial: silent blank feed is gone, but some reloads still wait several seconds before cards appear; Chat 1 is implementing the direct continuation.
- Current production deploy workflow blob `625a22da18300795974ba6e3b46c6b92db1184d4` runs image-swipe/package/score/giveaway UI regressions but does not run the focused `tests/feed-bootstrap.test.js` regression from the first fix. Even that focused test is a simulated browser regression, not a proof of real-device cold/reload network behavior.

**Severity:** `high`

**Certainty:** `proven`

**Bounded verification/fix candidate**

Do not change or compete with Chat 1's active implementation. After that continuation reaches production and real-device acceptance, run one bounded post-incident acceptance that proves repeat-open/reload/foreground behavior and verifies that the stable client behavior has a durable regression gate appropriate to the accepted implementation.

### Finding 4 — Legacy one-shot Taste workflows remain alternate dispatchable canonical writers

**User impact**

An operator can still see multiple manual workflows with `contents: write` authority over the canonical Taste overlay, making semantic persistence ownership harder to reason about and increasing the chance of an obsolete path being dispatched or later repurposed outside the transactional inbox mechanism.

**Exact evidence**

- `.github/workflows/persist-ai-pilot-25.yml` blob `ccfbcd2f703d6cf40fd2277985fdc0ee6e823bbb`: `workflow_dispatch`, `contents: write`, direct `ingest_taste_results.py`, direct overlay commit/push.
- `.github/workflows/test-one-real-taste-persistence.yml` blob `6c023ef5c7f91ef4f2ff183707cd69d595e10a50`: same alternate write shape.
- `.github/workflows/ingest-taste-batch.yml` blob `3242fbe96fba9ab6a2165176a852a0fedbead759`: current transactional production path via `process_taste_inbox.py` with synchronized overlay/index/receipts/pre-AI state.
- Both legacy workflows contain exact historical preconditions, so this audit does not prove that either can mutate current state successfully today.

**Severity:** `medium`

**Certainty:** `risk_hypothesis`

**Bounded verification/fix candidate**

Run a two-file ownership cleanup/recon limited to these legacy dispatchable workflows: prove whether either still has a legitimate operational purpose; if not, retire/disable it, or explicitly constrain it so the transactional inbox path is the only normal production Taste writer.

## Baseline disposition

| Baseline finding | Disposition | Reason |
|---|---|---|
| Finding 1 — semantic execution heartbeat | `closed` | Durable accepted execution/progress receipt and exact current-scope correlation now exist; queue presence is explicitly not heartbeat. |
| Finding 2 — semantic incompleteness visibility | `partially_closed` | Canonical artifacts now truthfully expose degraded/unresolved semantic scope, but the current production UI does not surface that degraded truth to the user. |
| Finding 3 — visual stale-success | `partially_closed` | The fix is accepted and release-ready on its branch, but production `main` still runs the old no-receipt/no-binding workflows. |
| Finding 4 — giveaway identity provider readiness | `partially_closed` | ITAD permission is now confirmed and provider-neutral implementation is prepared, but no accepted operational cross-store identity route is active yet; Twitch/IGDB remains waiting. |
| Finding 5 — legacy Taste mutation paths | `still_open` | The two one-shot dispatchable direct-overlay writers still exist; current corruption is not proven because their historical preconditions constrain them. |

## Mobile incident audit-trigger disposition

**Yes — stabilization of the current mobile incident should trigger another future System Audit.**

Reason:

- `SYSTEM_AUDITOR_ROLE.md` requires an audit after an unexpected user-visible missing/incorrect result or unobserved automatic-process incident is stabilized unless the previous audit already covered the exact stabilized failure class.
- This audit runs **before** the mobile incident reaches a stable/accepted boundary and intentionally does not inspect the active Chat 1 continuation as accepted implementation.
- The stabilized continuation may change the client presentation fallback/cache boundary, and its end-to-end production behavior is not knowable from the currently accepted evidence.

The next audit does not need broad re-investigation of semantic runtime or visual freshness. It should be narrowly triggered after mobile stabilization and should incorporate the accepted final mobile behavior plus whatever production release state exists then.

## Director recommendations — maximum 2

1. **After mobile stabilization, close production visual freshness:** release the already accepted `worker/visual-freshness-chain-fix-01` path through normal production and capture one bounded production acceptance proving exact build-receipt/deploy binding. This addresses the highest-impact known production stale-success gap without redesign.

2. **Close the semantic user-truth gap:** prepare one bounded implementation/acceptance that surfaces canonical `semantic_completeness.status=degraded` / `sufficiently_complete_for_publication=false` in the user-visible feed and proves unresolved semantic scope cannot look like a fully healthy complete recommendation set. Do not change Taste/ranking policy.

The legacy one-shot Taste writer cleanup remains a valid medium-priority ownership task, but it is below the two high-impact user-result gaps above.

## Exact refs reviewed

Required starting/control refs:

- `WORKER_TASK_SYSTEM_AUDIT_02.md` blob `c1c8ae9319040ebf4d0147f12add1b9d940c179f`
- `SYSTEM_AUDITOR_ROLE.md` blob `255694c625a680bd29fcd3aec8b434d05be14982`
- `DIRECTOR_REVIEW_CHECKPOINTS.md` blob `b1d7eb5457abb189e2566a1336f36e07504ba1d9`
- `DIRECTOR_TASK_BOARD.md` blob `7c0fe0e13704643275e7a37604e613be90939579`
- `reviews/system_audits/baseline-01.md` blob `5d3abfd95e84205b999329aa30bc806687d8b9cf`
- `reviews/worker_reports/semantic-runtime-completion-fix-01.md` blob `b414aa0d41929a8e125833b79caee74a9f022049`
- `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md` blob `5b4a25c89845ab258651a30608658e90d7d1840d`
- `reviews/worker_reports/visual-freshness-chain-fix-01.md` blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`
- `reviews/worker_reports/visual-freshness-chain-acceptance-02.md` blob `6a691fb29d88b1785accf717752149e027265a2c`
- `config/execution_ownership_contract.json` blob `f0b5f48756489965ec223a42f3b234f62ac4bae1`
- `reviews/worker_reports/mobile-page-interaction-freeze-recon-01.md` blob `48700dc77ac17fa031dd129996bef74075d86872`
- `reviews/worker_reports/mobile-page-blank-feed-fix-01.md` blob `61b23ffc479dff473310b1d7aed0d36d43a11c8f`

Bounded current evidence expansion:

- `data/cache/taste_ingest_receipts/latest_runtime_status.json` blob `cfeb41a044e90551ee35118f28636425a510fa26`
- `data/production/pre_ai/chatgpt_payload.json` blob `b350b1d5b679ce995988107a1d5e716cf447acd3`
- `scripts/build_visual_feed_v2.py` blob `4b303abe6e204c1ffaa9ef6083685ee38c3382fb`
- `web/app.js` blob `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5`
- `.github/workflows/build-daily-visual-payload.yml` blob `2d56b81f822412c433852d55a749a4db8ce33b78`
- `.github/workflows/deploy-visual.yml` blob `625a22da18300795974ba6e3b46c6b92db1184d4`
- `.github/workflows/ingest-taste-batch.yml` blob `3242fbe96fba9ab6a2165176a852a0fedbead759`
- `.github/workflows/persist-ai-pilot-25.yml` blob `ccfbcd2f703d6cf40fd2277985fdc0ee6e823bbb`
- `.github/workflows/test-one-real-taste-persistence.yml` blob `6c023ef5c7f91ef4f2ff183707cd69d595e10a50`

## Completion

Status: `complete`

Report: `reviews/system_audits/system-audit-02.md`
