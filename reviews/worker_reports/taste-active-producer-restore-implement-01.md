# Worker Report — Taste Active Producer Restore Implement 01

## Task
`taste-active-producer-restore-implement-01`

Restore exactly one active recurring ChatGPT Scheduled `Taste Semantic Producer`, migrate canonical producer identity to generation 2, and arm exactly one fresh current-game canary without widening to backlog processing.

## Status
`in_progress`

## Control-plane preflight
- User directly verified immediately before continuation: `ChatGPT → Scheduled → Active` is empty.
- This is accepted as positive proof that active ChatGPT Scheduled Task count is `0` before creation.
- Known old task remains historical provenance and must not be modified:
  - title: `Taste Semantic Producer`
  - task id: `6a9d6fdddc00819193ed670d782045c4`
  - producer id: `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
  - producer generation: `1`
  - known UI state: `Completed`
- Scheduled Task create attempt count remains `0` at this checkpoint.

## Canary binding fixed before task creation
Selected exactly one current full-evaluation game row from the canonical current queue/projection:

- title: `Chernobylite Complete Edition`
- `taste_subject_key`: `App_1016800`
- `appid`: `1016800`
- `taste_fingerprint`: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- `candidate_context_sha256`: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`
- `profile_blob_sha`: `c42a6a5dcf608e04bf86d24be9e1542f1b934456`
- `taste_model_version`: `taste-v3`
- `taste_semantics_sha256`: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- `source_mailing_updated_at_utc`: `2026-09-07T20:45:43.377890+00:00`

Current queue state for this exact row at selection:
- `ai_required_reason = taste_cache_key_missing`
- `work_required` includes `evaluate_taste_fit`, `evaluate_normalized_taste_factors`, and `resolve_grounded_negative_analysis`.
- The row is therefore a fresh full Taste evaluation candidate under the current projection.
- This task authorizes no other key/appid/fingerprint/context and no refreshed successor if any binding changes.

## Schedule staging decision
- Permanent recurrence must remain DAILY at `01:00 Europe/Samara`.
- Planned first occurrence: `2026-09-09 01:00 Europe/Samara`.
- This leaves a multi-hour staging window for immutable task-id capture, same-task prompt finalization, generation-2 GitHub producer-fence migration, and validation before execution.

## Required singleton behavior to install
- Exactly one recurring Scheduled Task named `Taste Semantic Producer`.
- Maximum one semantic result total for the fixed canary tuple above.
- No fallback candidate and no next-row selection.
- If any exact binding is stale/currently absent/already accepted, no-op.
- After successful canonical canary ingest, later scheduled invocations remain no-op under the unchanged canary prompt.
- No automatic backlog widening.
- Submission only through the existing canonical GitHub Taste inbox/ingest route.
- After immutable task id capture, producer identity must be `chatgpt_scheduled_task:<NEW_TASK_ID>` with generation `2`.

## GitHub producer fence before migration
Current canonical fence remains unchanged at this checkpoint:
- `producer_fence.active_producer_id = chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`
- `producer_fence.active_producer_generation = 1`
- `producer_fence.missing_legacy_or_mismatch_policy = reject_before_ingest`
- semantic contract remains `TASTE-SEMANTIC-RESULT-V5`.

## Changes so far
- Updated only this same durable report in `main` to resume from the prior blocked state and freeze the exact canary tuple before task creation.
- No Scheduled Task has yet been created or changed in this continuation at this checkpoint.
- No producer fence has yet been migrated.
- No canary semantic analysis has run.

## Validation pending
- Create exactly one new recurring task and capture immutable id.
- Update only that same task if its returned id must be inserted into its prompt.
- Migrate only producer identity fields in `config/taste_result_contract.json` to generation 2.
- Prove new id/gen2 accepted; old id/gen1 and wrong/missing identity rejected.
- Reconfirm singleton/canary containment and recurring schedule.

## Cost / containment
- No paid OpenAI API.
- No Copilot.
- No external scheduler.
- No backlog or mass analysis.

## Recommended next step
Create exactly one recurring `Taste Semantic Producer` for the fixed canary and safe first `01:00 Europe/Samara` occurrence. If creation outcome is ambiguous, do not retry; stop fail-closed and record the exact state here.

## Refs
- Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_IMPLEMENT_01.md`
- Design: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
- Canonical queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- Current projection: `data/production/pre_ai/taste_projection.json`
- Producer fence: `config/taste_result_contract.json`

## Efficiency / reusable lesson
For immutable scheduler replacements, freeze the exact data-plane tuple in durable state before the single create attempt so task-id capture and producer-fence migration cannot accidentally widen scope.
