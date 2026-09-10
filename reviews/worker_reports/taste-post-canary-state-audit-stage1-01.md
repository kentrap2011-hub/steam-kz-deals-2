# TASTE POST-CANARY STATE AUDIT — STAGE 1

- task_id: `taste-post-canary-state-audit-stage1-01`
- lifecycle: `complete_stage1_state_pass`
- started_utc: `2026-09-10T05:54:32Z`
- completed_checks: `4/4`
- decision: `PASS_STAGE1_STATE`

## Checks

### Check 1 — accepted canonical Taste state
**PASS.** `data/cache/taste_fit.entry_overlay.json` currently has `entry_count: 807` and contains exactly one match for `App_1016800`. That entry is keyed as `App_1016800` and has `appid: 1016800`, consistent with the accepted Chernobylite canary baseline.

Evidence source: `data/cache/taste_fit.entry_overlay.json`.

### Check 2 — pending Taste queue
**PASS.** The canonical pending queue is `data/production/pre_ai/chatgpt_taste_queue.jsonl`; a fresh exact search of its current contents finds no occurrence of `App_1016800`. The accepted Chernobylite canary is therefore no longer pending in the Taste queue.

Evidence source: `data/production/pre_ai/chatgpt_taste_queue.jsonl`.

### Check 3 — consumed active inbox submission
**PASS.** A fresh recursive `main` tree search finds no path containing package id `20260909T061807Z__1908946`. It also finds no active `data/ai_inbox` path. The accepted Chernobylite inbox submission is therefore absent because it was consumed.

Evidence source: current recursive `main` tree.

### Check 4 — ingest receipt
**PASS.** `data/cache/taste_ingest_receipts/065e182a9147bfe3a7a6.json` exists with `status: complete`, exact `batch_id: 065e182a9147bfe3a7a6`, exactly one input file `canary-app-1016800-gen2.json`, `result_count: 1`, `full_evaluation_result_count: 1`, and the sole ingested key `App_1016800`. Its queue transition is `567 -> 566`, and all recorded transactional checks are true. This records exactly one accepted Chernobylite result, matching `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`.

Evidence source: `data/cache/taste_ingest_receipts/065e182a9147bfe3a7a6.json`; accepted baseline: `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`.

## Decision

`PASS_STAGE1_STATE`

No TASTE state, Scheduled Task, code, production/config/data state, semantic generation, ingest, or second game was modified by this audit. Only this audit report was created and incrementally updated as required.
