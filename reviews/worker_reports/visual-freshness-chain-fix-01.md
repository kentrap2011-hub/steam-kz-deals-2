# Visual Freshness Chain Fix 01

Task ID: `visual-freshness-chain-fix-01`  
Mode: `IMPLEMENT`  
Status: `complete`

## 1. Exact implementation performed

Implemented exactly the two missing mechanisms from the preceding acceptance, without changing ranking/Taste semantics, history readiness policy, canonical visual ownership, or Pages ownership.

### Build-side durable freshness receipt

Updated `.github/workflows/build-daily-visual-payload.yml` to:

- capture the intended source/pre-AI cycle before the ordinary build attempt;
- run the focused freshness contract test;
- track whether the canonical visual persistence step completed;
- create `/tmp/visual-freshness-receipt.json` with `if: always()` for the ordinary build job;
- upload that receipt as the durable Actions artifact `visual-freshness-receipt` with 30-day retention;
- emit an explicit degraded receipt for the existing giveaway-only branch of the same workflow, because that invocation intentionally does not constitute a fresh paid-list build;
- add the bounded `no_build_receipt` job for the existing case where an upstream `workflow_run` is not eligible for the build job, so the overall invocation cannot succeed without a freshness outcome.

No second production workflow or production data plane was introduced.

### Freshness receipt helper and focused test

Added:

- `scripts/visual_freshness_receipt.py`
- `scripts/test_visual_freshness_receipt.py`

The helper owns capture, receipt creation, and deploy verification. The test owns the three required bounded cases.

### Deploy-side exact triggering-run binding

Updated `.github/workflows/deploy-visual.yml` to:

- grant only `actions: read` in addition to its existing permissions;
- for `workflow_run`, download `visual-freshness-receipt` from exactly `${{ github.event.workflow_run.id }}` using `actions/download-artifact@v4`;
- stage the existing canonical `data/production/visual/current.json` as before;
- verify the staged payload against the exact triggering build receipt before Pages configuration/upload/deploy;
- expose `VISUAL_PUBLICATION_OUTCOME` and a GitHub Step Summary classification;
- classify non-`workflow_run` publications as `unbound/non_workflow_run`, never as a fresh-cycle success.

The existing general/giveaway visual validation and UI regression steps remain in place.

## 2. Exact receipt schema, fields, and ownership

Contract owner: `scripts/visual_freshness_receipt.py`  
Contract: `visual-freshness-receipt-v1`  
`schema_version`: `1`

Receipt fields:

```text
schema_version
contract
fresh_build
outcome
reason
intended_source_cycle
  captured_checkout_commit_sha
  history_snapshot_blob_sha
  history_snapshot_present
  history_snapshot_parse_error
  history_status
  history_complete_coverage
  source_cycle
    source_mailing_updated_at_utc          # when available
    source_mailing_generated_at_utc        # when available
    generated_at_utc                       # when available
    persistent_cache_updated_at_utc        # when available
produced_visual                            # populated only for fresh_build=true
  blob_sha
  commit_sha
  source_history_snapshot_blob_sha
workflow_run
  id
  attempt
  event
  head_sha
  upstream_workflow_run_id
  upstream_head_sha
observed_visual                            # optional diagnostic when a proposed fresh receipt is downgraded
```

For `fresh_build=false`:

- `outcome` is exactly `degraded/no_fresh_build`;
- `produced_visual` is `null`;
- `reason` is explicit, including bounded reasons such as `prerequisite_not_ready`, `build_reported_no_fresh_change`, `canonical_persistence_failed`, `visual_source_history_mismatch`, `upstream_prerequisite_not_ready`, or `giveaway_only_refresh`.

For `fresh_build=true`, the helper requires all of the following before issuing the fresh receipt:

- the build reported a fresh visual change;
- canonical persistence completed;
- an exact intended `history_snapshot.json` blob SHA was captured;
- the persisted canonical visual declares that same history blob in `production_contract.source_history_snapshot_blob_sha`;
- the receipt records the exact canonical visual blob SHA and the exact commit SHA that owns that visual file.

## 3. Exact deploy binding behavior

For a `workflow_run` deployment:

1. The deploy downloads the receipt from the exact triggering Build daily visual payload run ID.
2. The receipt's `workflow_run.id` must equal that triggering run ID.
3. If `fresh_build=true`, verification fails closed unless all identities still match:
   - current canonical `history_snapshot.json` blob SHA == receipt intended history blob SHA;
   - current canonical `visual/current.json` blob SHA == receipt produced visual blob SHA;
   - latest canonical commit touching `visual/current.json` == receipt produced visual commit SHA;
   - that commit contains the same visual blob SHA;
   - canonical visual `production_contract.source_history_snapshot_blob_sha` == intended history blob SHA;
   - staged `web/data/current.json` is byte-identical to canonical `current.json` and hashes to the receipt visual blob SHA.
4. Only after this verification does the workflow configure/upload/deploy Pages.
5. If `fresh_build=false`, verification accepts only the explicit `degraded/no_fresh_build` receipt and exposes that classification; it is not reported as fresh.
6. A direct push/manual deploy has classification `unbound/non_workflow_run`; it is explicitly not classified as fresh.

Therefore an older or concurrently replaced `current.json` cannot be accepted as fresh for the triggering source cycle.

## 4. Validation

### Fresh path — PASS

Focused test creates a current history cycle, persists a visual whose provenance points to that exact history blob, creates a `fresh_build=true` receipt, stages the canonical payload, and verifies the exact run/history/visual-blob/visual-commit/staged-payload binding.

Observed bounded result:

```text
VISUAL_FRESHNESS=fresh ...
```

### No-build / degraded path — PASS

Focused test creates a receipt with no fresh build and prerequisite not ready. It proves:

- `fresh_build=false`;
- `outcome=degraded/no_fresh_build`;
- `produced_visual=null`;
- deploy verification returns the explicit degraded classification rather than fresh.

Observed bounded result:

```text
VISUAL_FRESHNESS=degraded/no_fresh_build reason=prerequisite_not_ready run_id=202
```

The production workflow also covers the pre-existing upstream-ineligible and giveaway-only invocation paths with explicit degraded receipts.

### Stale mismatch — PASS, fails closed

Focused test first creates a valid fresh receipt, then replaces canonical visual state with a different/stale visual before deploy verification. Verification raises and does not return a fresh classification. In the Pages workflow this failure occurs before Pages configure/upload/deploy.

### Focused test result

```text
VISUAL_FRESHNESS_RECEIPT_TESTS=PASS cases=fresh,degraded,stale_mismatch
```

### Syntax / bounded regression evidence

- `scripts/visual_freshness_receipt.py`: Python compile PASS.
- `scripts/test_visual_freshness_receipt.py`: Python compile PASS.
- modified build workflow: YAML parse PASS; jobs resolve as `scope,giveaway_refresh,no_build_receipt,build`.
- modified deploy workflow: YAML parse PASS; job resolves as `deploy`.
- final net diff against the synchronized production base contains only the two workflow changes plus the two focused helper/test files; the build workflow net diff has no deletions, confirming the accidental intermediate ranking-export edits were removed and existing ranking/Taste behavior was restored before completion.
- existing ordinary visual/deploy validation and UI regression commands remain present and unchanged where applicable; no production workflow was executed merely to force validation.

No broad workflow-run archaeology was performed.

## 5. Production deployment performed

No.

No manual production regeneration, production build, production push, or Pages deployment was performed for this implementation task. Validation was bounded to the implementation branch and local contract/syntax checks.

## 6. Follow-up acceptance readiness

Yes.

The implementation is ready now for a bounded follow-up acceptance against `worker/visual-freshness-chain-fix-01`, covering:

1. fresh source/history -> fresh visual -> receipt -> exact deploy binding;
2. no-build -> durable `degraded/no_fresh_build` receipt -> explicitly degraded publication outcome;
3. stale/mismatched canonical visual -> verification failure before Pages publication as fresh.

## Exact refs

- Task blob: `ee2fd92c69e47f36a759f36714295780e4253997`
- Implementation branch: `worker/visual-freshness-chain-fix-01`
- Synchronized production base included before report: `40bdbe894958ff953ee2a58bb64fd025816dc75f`
- Pre-report implementation head: `57ab2741742caadd3d182c7f78d1f0fcde681003`
- Build workflow blob: `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`
- Deploy workflow blob: `7479a56ac7ee363e6a212952e58f36558b371877`
- Freshness helper blob: `81c59c5ca54192e87c984ffd8b1f7cb78815c3ae`
- Focused test blob: `7ca29c732b4b165304ff87054771e399f0c46847`
- Build workflow implementation commit: `2ee8c9ec9160dfa66b0abc5aa1cdd9a766c49068`
- Deploy binding implementation commit: `6b2fd3c6a7179b4b3f581fdd7b17f31ffb3ca70d`
- Ranking-semantics restoration commit: `3810015ff30ccc873f90b5d9ee7dc77d76c9d78f`
