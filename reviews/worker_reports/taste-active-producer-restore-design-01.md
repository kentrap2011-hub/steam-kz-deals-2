# Worker Report — Taste Active Producer Restore Design 01

## Task
Design only: determine the narrowest safe restoration path for exactly one ACTIVE recurring ChatGPT Scheduled Taste producer, without creating or mutating any Scheduled Task or processing any game.

## Verified facts
- Required task/protocol/context set has been read.
- Old completed Scheduled Task: jawbone id `6a9d6fdddc00819193ed670d782045c4`, canonical producer id `chatgpt_scheduled_task:6a9d6fdddc00819193ed670d782045c4`, producer generation `1`.
- User UI evidence in the task establishes: old task is `Completed`, Date/Time is non-editable, and Scheduled `Active` filter is empty.
- Current `config/taste_result_contract.json` is the concrete repository identity fence and pins that old canonical producer id plus generation `1` with mismatch policy `reject_before_ingest`.
- `scripts/taste_producer_fence.py` reads the active identity dynamically from that contract; it does not hard-code the old id/generation.
- `scripts/validate_taste_producer_fence.py` tests current acceptance plus wrong/missing id/generation rejection; it also does not hard-code generation `1` as the canonical current value.
- `.github/workflows/ingest-taste-batch.yml` runs the producer fence before semantic validation and persistence.
- `config/execution_ownership_contract.json` fixes the architecture boundary: GitHub is control plane; scheduled ChatGPT is a constrained semantic data plane.
- `config/daily_execution_contract.json` fixes the daily production cycle at `01:00` in timezone `Europe/Samara`; GitHub prepares exact work, Scheduled ChatGPT consumes only completed prepared input.
- Current official OpenAI Scheduled Tasks documentation supports recurring tasks and management of active/paused tasks. It does not provide sufficient evidence that this exact user-observed Completed/non-editable old task can be safely recovered in place.

## Current design direction
The narrowest viable restoration is one NEW recurring Scheduled Task with a new immutable jawbone id, producer generation advanced monotonically from `1` to `2`, while preserving the old completed task for provenance. The new task should be the same persistent task used for the one-game canary and later normal daily production; no disposable one-time canary task is required.

The repository identity cutover must remain fail-closed: replace only the concrete active producer id/generation in `config/taste_result_contract.json`; retain the existing dynamic fence validator, regression, ingest ordering, semantic contract `TASTE-SEMANTIC-RESULT-V5`, queue ownership, run/binding checks, and persistence path. Historical reports/old task records must not be rewritten to pretend the old producer had generation `2`.

## Changes
- This report file only.

## Validation still to close
- Confirm remaining required historical state report(s).
- Finalize exact first-run timing, no-overlap proof, containment/rollback, audit gate, and proposed next IMPLEMENT task filename/report path.
- Re-read final report from `main`.

## Status
`in_progress`

## Exact refs
- Task: `WORKER_TASK_TASTE_ACTIVE_PRODUCER_RESTORE_DESIGN_01.md`
- Report: `reviews/worker_reports/taste-active-producer-restore-design-01.md`
- Current identity contract: `config/taste_result_contract.json`
- Fence: `scripts/taste_producer_fence.py`
- Fence regression: `scripts/validate_taste_producer_fence.py`
- Ingest: `.github/workflows/ingest-taste-batch.yml`
- Daily cadence contract: `config/daily_execution_contract.json`
- Ownership contract: `config/execution_ownership_contract.json`
- OpenAI Help: https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt

## Efficiency / reusable lesson
Keep mutable producer identity in one canonical repository fence and make validators read it dynamically; replacing an external immutable task then requires a narrow contract cutover instead of weakening validation code.
