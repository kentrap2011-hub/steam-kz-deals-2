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
- profile resolved commit: `c8a9151e75286dc7260c87925d4fb906da4d5faa`
- profile blob SHA: `b4871a730d96bc799970190374bc95710a3ce93f`
- profile content SHA256: `6ed2b116d9414663da0e3ffcb2d8eb68937e23975ac2aac894034121e6a20b01`
- semantics_sha256: `0dbcc4c167c672020516adc754da0050d0e5c1e2d39b9b58fc06e2d6a2a43833`
- canonical fingerprint: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- canonical input context_sha256: `2fb17c31681aec253a59d2e212a0c920fd18245fb4696983049dc056054b38dc`

## Check results

### Check 1 — Current canonical `App_1016800` binding

**Result: PASS**

- Current `data/cache/taste_fit.entry_overlay.json` contains `App_1016800` with `model_version=taste-v3`, profile blob `b4871a730d96bc799970190374bc95710a3ce93f`, semantics SHA256 `0dbcc4c167c672020516adc754da0050d0e5c1e2d39b9b58fc06e2d6a2a43833`, fingerprint `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`, and context SHA256 `2fb17c31681aec253a59d2e212a0c920fd18245fb4696983049dc056054b38dc`; these match the accepted canary values exactly.
- Current canonical ingest receipt `data/cache/taste_ingest_receipts/065e182a9147bfe3a7a6.json` names `TasteFitGen2_1016800_20260217.json`, independently confirming the persisted real AppID and producer generation `2` for the accepted ingest.
- The exact source repo/path/branch/commit/content-hash tuple above is the frozen accepted source binding from the canary acceptance report; the current canonical record retains its exact accepted profile blob identity. No contradictory current binding has been observed in this check.
- No repair action or runtime execution was performed.
