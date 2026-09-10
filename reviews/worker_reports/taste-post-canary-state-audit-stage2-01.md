# Taste Post-Canary State Audit — Stage 2

- task_id: `taste-post-canary-state-audit-stage2-01`
- lifecycle: `done`
- started_utc: `2026-09-10T06:48:32Z`
- completed_checks: `5/5`
- next_action: `none`
- decision: `pass`

## Accepted canary binding

The two predecessor reports were read once before investigation. The accepted binding used by this audit is:

- AppID: `1016800`
- producer_generation: `2`
- model_version: `taste-v3`
- profile source repo: `kentrap2011-hub/stopgame-ratings-data`
- profile source path: `gaming_taste_live.json`
- profile source branch: `main`
- profile resolved commit: `c8a915d1ecad2bfd4f22d83182542925f73b1e54`
- profile blob SHA: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`
- profile content SHA256: `6ed2adb975860783abf402ed74446eb257b1e78af69c332590dc27718a663cc4`
- semantics_sha256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- canonical fingerprint: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- canonical input context_sha256: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`

## Check results

### Check 1 — Current canonical `App_1016800` binding

**Result: PASS**

- Current `data/cache/taste_fit.entry_overlay.json` contains `App_1016800` with profile blob `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`, `taste_model_version=taste-v3`, semantics SHA256 `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, fingerprint `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`, and candidate-context SHA256 `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`; these match the accepted canary tuple exactly.
- Current canonical ingest receipt `data/cache/taste_ingest_receipts/065e182a9147bfe3a7a6.json` is `status=complete`, batch id `065e182a9147bfe3a7a6`, has the sole input `canary-app-1016800-gen2.json`, `result_count=1`, `full_evaluation_result_count=1`, and sole key `App_1016800`; this confirms the persisted real AppID and generation-2 canary ingest.
- The exact frozen source repo/path/branch/commit/content-hash tuple above comes from the accepted canary report; the current canonical record retains its exact accepted profile blob identity.
- No repair action or runtime execution was performed.

### Check 2 — Persisted cache/index/overlay consistency

**Result: PASS**

- The accepted ingest commit `69af81919611fda00ffc507570d0788d6b9a53dc` explicitly synchronized the canary overlay/index and modified `data/cache/taste_fit.entry_index.json` as the merged per-entry index.
- Current `data/cache/taste_fit.entry_index.json` declares `source_cache.path=data/cache/taste_fit.json` with blob `069ee4e5f2e7b09a173b64b99358bb0fe3ea0d71`, size `127366`, and `150/150` entries; these match the current persisted cache surface.
- The same index declares `source_overlay.path=data/cache/taste_fit.entry_overlay.json` with blob `5ffe06db251ed79551d6758e1787e59f04edcf87`, size `1006141`, and `807/807` entries; these match the current persisted overlay surface.
- Merge policy is `overlay_exact_key_wins`. The merged index entry for `App_1016800` contains AppID `1016800`, profile blob `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`, model `taste-v3`, semantics SHA256 `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, context SHA256 `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`, fingerprint `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`, verdict `INCLUDE`, fit `moderate`, and reason `include_moderate`; this is identical to the current overlay projection.
- `App_1016800` negative-readiness projection is `complete_with_confirmed_negative`, confirmed-negative count `1`, ready `true`, consistent with the accepted canary result.
- The separate legacy `taste_fit.index.json` is not the canary-synchronized merged index; its own metadata describes only a compact projection of a historical base `taste_fit.json`. It is not used as evidence for the canonical merged surface in this check.
- No repair action or runtime execution was performed.

### Check 3 — No contradictory duplicate `App_1016800` saved state

**Result: PASS**

- Current `data/cache/taste_fit.entry_overlay.json` has exactly one keyed occurrence of `App_1016800`.
- Current `data/cache/taste_fit.entry_index.json` contains the expected merged entry plus its negative-readiness projection; both refer to the same accepted result and are not competing saved-state records.
- The accepted ingest diff increased overlay `new_key_count` from `669` to `670` while inserting `App_1016800`; the base-cache source was not mutated by that ingest. The current merged index still references the same current base-cache blob, so the canary remains an overlay-new key rather than a conflicting base-cache duplicate.
- Current `data/production/pre_ai/chatgpt_taste_queue.jsonl` contains no `App_1016800` occurrence.
- Current `data/ai_inbox/taste` is absent, so there is no active duplicate canary submission waiting beside the persisted result.
- No contradictory duplicate or stale `App_1016800` record was found in the nearby canonical persisted TASTE surfaces checked above.
- `data/cache/taste_direct_conflicts.report.json` was observed to reference an older cache blob, so it was not treated as current authoritative evidence for this check.
- No repair action or runtime execution was performed.

### Check 4 — No post-canary saved-state drift

**Result: PASS**

- Direct commit comparison from accepted canonical ingest `69af81919611fda00ffc507570d0788d6b9a53dc` to current `main` reports `47` commits ahead and `0` behind.
- Every changed path in that comparison is a director/protocol/task/report document. No canonical TASTE saved-state path under `data/cache`, `data/production/pre_ai`, or `data/ai_inbox` changed after the accepted ingest.
- Therefore the accepted persisted canary state itself has not drifted since the canonical ingest. No source-of-truth exception is needed because no saved-state mutation occurred in the comparison interval.
- The audit report commits created by this task are documentation-only and do not alter TASTE state.
- No repair action or runtime execution was performed.

### Check 5 — Final verdict

**Result: PASS**

All required saved-state conclusions are established: the current `App_1016800` record preserves the exact accepted canary binding; the canonical cache/merged-index/overlay surfaces agree; no contradictory duplicate or active stale copy was found; and the canonical TASTE saved state has not changed since accepted ingest commit `69af81919611fda00ffc507570d0788d6b9a53dc`.

## Final decision

`pass`

No repair actions were performed. No TASTE data, runtime/cache state, Scheduled Task, code, queue, inbox, or configuration was modified or executed. Only this required audit report was created and incrementally updated after each check.
