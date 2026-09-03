# Visual Freshness Chain Acceptance 02

Task ID: `visual-freshness-chain-acceptance-02`  
Mode: `ACCEPTANCE`  
Status: `complete`

## Required result

1. `Fresh-cycle build proof`: `pass`
2. `Deploy-to-built-cycle binding`: `pass`
3. `Stale-success visibility`: `pass`
4. `Ownership/regression preserved`: `pass`

## Exact evidence

### 1. Fresh-cycle build proof — pass

Evidence:

- implementation branch head: `4080030e686d6b04fcc666069819aa46df18da7a`;
- build workflow blob: `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`;
- freshness helper blob: `81c59c5ca54192e87c984ffd8b1f7cb78815c3ae`;
- focused test blob: `7ca29c732b4b165304ff87054771e399f0c46847`.

The build workflow captures `/tmp/visual-freshness-intent.json` before the ordinary build attempt, then keeps the existing history readiness gate. A fresh candidate can only be created after `steps.build.outputs.built == 'true'` and the canonical persistence step reports `persisted=true`.

The receipt helper records:

- the captured checkout commit;
- the exact intended `history_snapshot.json` blob SHA;
- available source-cycle timestamps/status;
- the workflow run identity;
- for a fresh result, the exact canonical visual blob SHA and exact commit SHA touching `data/production/visual/current.json`;
- the visual payload's declared `production_contract.source_history_snapshot_blob_sha`.

`create_receipt()` sets `fresh_build=true` only when the build reported true, persistence completed, an intended history blob exists, and the persisted visual declares that exact intended history blob. Otherwise the receipt is downgraded to `degraded/no_fresh_build`.

The focused test's fresh case constructs an intended history cycle, persists a visual bound to that history blob, creates a fresh receipt and verifies exact run/history/visual-blob/visual-commit/staged-payload binding. The completed implementation report records the bounded result `VISUAL_FRESHNESS_RECEIPT_TESTS=PASS cases=fresh,degraded,stale_mismatch`.

Conclusion: a fresh classification cannot be produced from only a green workflow; it requires the intended source/history identity plus successful canonical persistence and exact produced visual identity.

### 2. Deploy-to-built-cycle binding — pass

Evidence:

- deploy workflow blob: `7479a56ac7ee363e6a212952e58f36558b371877`;
- freshness helper blob: `81c59c5ca54192e87c984ffd8b1f7cb78815c3ae`.

For `workflow_run`, deploy uses `actions/download-artifact@v4` with:

- artifact name `visual-freshness-receipt`;
- `run-id: ${{ github.event.workflow_run.id }}`;
- the current repository and token.

The deploy then passes that same triggering run ID as `--expected-run-id` to `verify-receipt` before Pages configure/upload/deploy.

For a fresh receipt, verification fails unless all of these are exact:

- receipt workflow run ID == triggering build run ID;
- current canonical history blob == intended history blob;
- current canonical visual blob == receipt produced visual blob;
- latest commit touching canonical visual == receipt produced visual commit;
- that commit contains the same visual blob;
- visual provenance points to the intended history blob;
- staged `web/data/current.json` is byte-identical to canonical visual and hashes to the receipt visual blob.

Pages configuration, Pages artifact upload and Pages deployment occur only after this binding step succeeds.

Conclusion: the fresh workflow-run publication is bound to the exact triggering build receipt rather than an arbitrary/latest artifact or whatever `current.json` happens to exist.

### 3. Stale-success visibility — pass

Evidence:

- freshness helper blob: `81c59c5ca54192e87c984ffd8b1f7cb78815c3ae`;
- focused test blob: `7ca29c732b4b165304ff87054771e399f0c46847`;
- deploy workflow blob: `7479a56ac7ee363e6a212952e58f36558b371877`.

The helper explicitly fails closed on:

- source/history blob mismatch;
- canonical visual blob mismatch;
- visual commit mismatch;
- receipt commit/blob mismatch;
- visual/source provenance mismatch;
- staged/canonical byte mismatch;
- staged blob mismatch;
- workflow run ID mismatch.

The focused stale case first creates a valid fresh receipt, then replaces canonical visual state and proves verification exits instead of returning `fresh`.

For no-build paths, the receipt is explicitly:

- `fresh_build=false`;
- `outcome=degraded/no_fresh_build`;
- `produced_visual=null`.

Deploy verification accepts that only as `degraded/no_fresh_build`, and `VISUAL_PUBLICATION_OUTCOME` plus the GitHub Step Summary state that it is not a fresh-cycle success.

Direct push/manual deploy is classified `unbound/non_workflow_run`, also explicitly not fresh.

Conclusion: a successful workflow cannot silently turn stale/no-build state into normal fresh success.

### 4. Ownership/regression preserved — pass

Evidence:

- branch/main compare at acceptance: branch `worker/visual-freshness-chain-fix-01` is `ahead_by=12`, `behind_by=27`, merge base `40bdbe894958ff953ee2a58bb64fd025816dc75f`, current main `ab4cc4a8771b360f2e98a4ac03560d7e2ee980f1`;
- branch diff against current main contains only:
  - `.github/workflows/build-daily-visual-payload.yml`;
  - `.github/workflows/deploy-visual.yml`;
  - `scripts/visual_freshness_receipt.py`;
  - `scripts/test_visual_freshness_receipt.py`;
  - the completed implementation report.

No second build workflow, deploy workflow or production data plane was introduced.

The build workflow's existing history/Taste/ranking validation gates remain present. The final build-workflow diff is additive (`+170/-0`), so no existing ranking/Taste gate or semantic block was deleted by this change. The deploy keeps its existing visual/giveaway validations and UI regressions.

The 27 commits added to `main` since merge base do not modify either freshness workflow or either freshness helper/test file, so the current branch divergence does not invalidate the reviewed implementation or create an implementation-file conflict with current production state.

Giveaway-only build invocations emit an explicit degraded receipt with reason `giveaway_only_refresh`. Non-workflow-run deploys are explicitly `unbound/non_workflow_run`. Neither path is silently fresh.

Receipt ownership remains a single small Actions artifact contract owned by `scripts/visual_freshness_receipt.py` and consumed by the existing deploy workflow.

## Remaining blocker/defect

None identified within the acceptance boundary.

The implementation branch is behind current `main`, but current-main changes since merge base do not touch the implementation workflow/helper/test files; this is not a freshness acceptance blocker.

## Production merge/release readiness

Yes. `worker/visual-freshness-chain-fix-01` is ready for production merge/release for the scoped freshness fix.

No manual production regeneration or Pages deployment was performed for acceptance.

## Recommended next step

Merge `worker/visual-freshness-chain-fix-01` into current `main` and let the normal build/deploy chain exercise the new receipt classification in production.

## Exact refs

- Acceptance task blob: `55d986eee9b77b2f36aea52b61b2fa390d741b81`
- Implementation branch: `worker/visual-freshness-chain-fix-01`
- Implementation branch head: `4080030e686d6b04fcc666069819aa46df18da7a`
- Current main at acceptance: `ab4cc4a8771b360f2e98a4ac03560d7e2ee980f1`
- Merge base: `40bdbe894958ff953ee2a58bb64fd025816dc75f`
- Implementation report blob: `e5226710d435cfbb1c0190e11d937b025ceb9aac`
- Build workflow blob: `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`
- Deploy workflow blob: `7479a56ac7ee363e6a212952e58f36558b371877`
- Freshness helper blob: `81c59c5ca54192e87c984ffd8b1f7cb78815c3ae`
- Focused test blob: `7ca29c732b4b165304ff87054771e399f0c46847`
