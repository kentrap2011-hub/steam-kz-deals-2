# Taste Post-Canary State Audit — Stage 2

- task_id: `taste-post-canary-state-audit-stage2-01`
- lifecycle: `in_progress`
- started_utc: `2026-09-10T06:48:32Z`
- completed_checks: `1/5`
- next_action: `check 2`
- decision: `pending`

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
- Current canonical ingest receipt `data/cache/taste_ingest_receipts/065e182a9147bfe3a7a6.json` names `TasteFitGen2_1016800_20260217.json`, confirming the persisted real AppID and producer generation `2` for the accepted ingest.
- The exact frozen source repo/path/branch/commit/content-hash tuple above comes from the accepted canary report; the current canonical record retains its exact accepted profile blob identity.
- No repair action or runtime execution was performed.
