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
- No GitHub control-plane responsibility is moved to ChatGPT or this worker. The task remains one exact GitHub-selected canary and must no-op on any mismatch.
- No new queue, quota, retry loop, scheduler, backlog manager or producer generation is introduced.

## Exact frozen canary tuple
At the mutation gate, the exact current canonical/committed canary state is:
- title: `Chernobylite Complete Edition`
- `taste_subject_key`: `App_1016800`
- `appid`: `1016800`
- `taste_fingerprint`: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- `candidate_context_sha256`: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`
- `profile_blob_sha`: `167b4e66a1a799fa023a397a896600554cbaf902`
- `taste_model_version`: `taste-v3`
- `taste_semantics_sha256`: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- `source_mailing_updated_at_utc`: `2026-09-07T20:45:43.377890+00:00`

Eligibility remains full fresh Taste:
- `ai_required_reason=taste_cache_key_missing`;
- `work_required=evaluate_taste_fit`;
- `work_required=evaluate_normalized_taste_factors`;
- `work_required=resolve_grounded_negative_analysis`.

The live profile was re-read immediately before this freeze and its blob SHA is now `167b4e66a1a799fa023a397a896600554cbaf902`; this supersedes both the old canary binding `c42a6a5d...` and the earlier observation `4df6b1ae...` made while the profile repository was still changing.

## Concurrent nightly source refresh
GitHub run `34274404165` (`Steam KZ production shortlist`) is still collecting the next nightly commercial snapshot and has not committed it yet. Therefore the source timestamp above is the latest completed canonical source at the freeze point. The scheduled canary prompt will be fail-closed: it must re-read the exact tuple immediately before semantic work and no-op if the source, profile, fingerprint, context, eligibility or producer fence changes. No fallback/successor game is allowed.

## Existing stale generation-2 result
Active stale file:
`data/ai_inbox/taste/canary-app-1016800-gen2.json`

It is bound to old profile SHA:
`c42a6a5dcf608e04bf86d24be9e1542f1b934456`

This file is invalid for the frozen tuple and will now be preserved under the existing `data/ai_archive/taste/**` lifecycle before its active copy is removed.

## Scheduled Task identity
- title: `Taste Semantic Producer`
- task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- generation: `2`
- permanent schedule required after dispatch: DAILY 01:00 Europe/Samara.

No Scheduled Task mutation has occurred yet in this task. No new task has been created.

## Canonical acceptance
Pending archive/removal of the old gen2 result, same-task canary prompt refresh/execution, canonical ingest, receipt/cache advancement, active-inbox consumption and queue-removal proof.

## Containment
- New Scheduled Task created: **NO**.
- Other game selected: **NO**.
- Mass/backlog semantic analysis started: **NO**.
- Paid OpenAI API/Copilot/external paid service used: **NO**.
- Producer fence/binding/V5 safety weakened: **NO**.
- System Audit started: **NO**.

## System Audit readiness
Pending successful canary acceptance. System Audit will not be started by this task.
