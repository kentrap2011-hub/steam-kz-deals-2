# taste-refreshed-canary-rerun-01

## Status
`in_progress`

## Task
Refresh the exact Chernobylite Complete Edition (`App_1016800`) canary binding against the current canonical Taste profile, use the same existing generation-2 `Taste Semantic Producer` Scheduled Task, run only that one canary, restore its permanent DAILY 01:00 Europe/Samara schedule, and verify canonical acceptance without weakening safety or widening production.

## Durable checkpoint
Report was created in `main` before any Scheduled Task mutation or active Taste inbox mutation and was re-read successfully.

## Architecture preflight
- GitHub/GitHub Actions remains owner of queue scope, current-input construction, producer fencing, validation, persistence, receipt state and completeness under `config/execution_ownership_contract.json`.
- The existing scheduled ChatGPT task remains only the constrained semantic producer authorized by `config/taste_result_contract.json`.
- This task is explicitly authorized to refresh and execute only the same existing Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9`; no new recurring stage/task is permitted.
- The proposed mutation does not transfer GitHub control-plane responsibilities to ChatGPT or this interactive worker: the scheduled task receives exactly one GitHub-selected canary tuple and must no-op on any mismatch.
- No new queue, quota, retry loop, scheduler, backlog manager or producer generation is introduced.

## Verified starting state
- Target remains exactly `Chernobylite Complete Edition`, `taste_subject_key=App_1016800`, AppID `1016800`.
- Current queue row still requires full Taste work: `evaluate_taste_fit`, `evaluate_normalized_taste_factors`, `resolve_grounded_negative_analysis`; `ai_required_reason=taste_cache_key_missing`.
- Current queue identity still has `taste_fingerprint=b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129` and `candidate_context_sha256=2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`.
- Active producer fence remains exactly `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`, contract `TASTE-SEMANTIC-RESULT-V5`, mismatch policy `reject_before_ingest`.
- Existing active stale Chernobylite file is still present with old profile binding `c42a6a5dcf608e04bf86d24be9e1542f1b934456`.
- The live canonical profile has changed again: current `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json` blob SHA observed during this task is `4df6b1aee00af0457740f50d0a8f2fc85e375b42`, so the old result is unquestionably stale and cannot be reused.

## Current-data freshness gate
At the beginning of this task the committed pre-AI snapshot still referenced the older source timestamp `2026-09-07T20:45:43.377890+00:00` and older profile blob `c42a6a5dcf608e04bf86d24be9e1542f1b934456`.

A normal scheduled GitHub run `34274404165` (`Steam KZ production shortlist`) then started at `2026-09-08T20:22:19Z` and is currently collecting the new nightly source. Because the task explicitly requires *current* Chernobylite data and current profile, the exact canary tuple will be frozen only after this owning GitHub refresh completes. The worker will not bind the Scheduled Task to the already-aging committed source while its canonical refresh is actively running.

## Candidate tuple — stable fields already confirmed
- `taste_subject_key`: `App_1016800`
- `appid`: `1016800`
- `taste_fingerprint`: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- `candidate_context_sha256`: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`
- `taste_model_version`: `taste-v3`
- `taste_semantics_sha256`: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- final current `profile_blob_sha` and `source_mailing_updated_at_utc`: pending post-refresh freeze.

## Archive
Archive lifecycle is canonical at `data/ai_archive/taste/**`; only `data/ai_inbox/taste/*.json` is active. The stale gen2 file will be copied to the archive first, clearly marked by path as stale-profile history, and only then removed from the active inbox.

No archive or inbox mutation has occurred yet in this task.

## Scheduled Task
Same required task identity:
- title: `Taste Semantic Producer`
- task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- generation: `2`
- permanent schedule required after dispatch: DAILY 01:00 Europe/Samara.

No Scheduled Task mutation has occurred yet in this task. No new task has been created.

## Canonical acceptance
Pending refreshed source freeze, archive/removal of old gen2 result, same-task prompt refresh/execution, canonical ingest, receipt/cache advancement, active-inbox consumption and queue-removal proof.

## Containment
- New Scheduled Task created: **NO**.
- Other game selected: **NO**.
- Mass/backlog semantic analysis started: **NO**.
- Paid OpenAI API/Copilot/external paid service used: **NO**.
- Producer fence/binding/V5 safety weakened: **NO**.
- System Audit started: **NO**.

## System Audit readiness
Pending successful canary acceptance. System Audit will not be started by this task.
