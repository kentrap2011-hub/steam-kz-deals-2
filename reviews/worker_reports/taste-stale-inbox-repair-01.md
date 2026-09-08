# taste-stale-inbox-repair-01

## Task
Confirm and minimally repair the stale Taste inbox blocker, preserve the historical generation-1 artifact, and re-ingest the already-produced Chernobylite generation-2 result through the canonical ingest path without semantic rerun, another game, another Scheduled Task, or weakened producer validation.

## Status
`in_progress`

## Verified facts
- The active Taste producer fence is canonical `TASTE-SEMANTIC-RESULT-V5`, active producer `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`, with mismatch policy `reject_before_ingest`.
- `.github/workflows/ingest-taste-batch.yml` runs `scripts/taste_producer_fence.py data/ai_inbox/taste` before `process_taste_inbox.py`.
- `taste_producer_fence.py::validate_taste_inbox()` scans every top-level `data/ai_inbox/taste/*.json` and rejects the whole run on the first producer mismatch.
- Current active inbox contains exactly the historical gen1 `canary-App_10150-producer-g1.json` and the current gen2 `canary-app-1016800-gen2.json`.
- The prior canonical workflow run `34260132159` failed exactly on the historical gen1 file before the Chernobylite ingest transaction.
- Current Chernobylite queue row still exists and its appid, taste fingerprint, candidate-context digest and required Taste work match the existing gen2 result.
- Current global profile/model/semantic/source bindings also still match the existing gen2 result: profile `c42a6a5dcf608e04bf86d24be9e1542f1b934456`, model `taste-v3`, semantics `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`, source `2026-09-07T20:45:43.377890+00:00`.

## Root cause
The blocker is deterministic whole-active-inbox fencing: a historical generation-1 submission remained in the active top-level Taste inbox, so the strict generation-2 fence rejects that old file and aborts before the valid current Chernobylite submission can be ingested. The new gen2 envelope itself is still current and has not been shown invalid.

## Architecture preflight
- Owner of queue scope, validation, persistence and inbox ingest: GitHub/GitHub Actions under `config/execution_ownership_contract.json`.
- Canonical authorization: `config/taste_result_contract.json` producer fence plus the existing GitHub-owned ingest workflow.
- Planned repair stays inside GitHub-owned artifact lifecycle; it does not transfer control-plane work to ChatGPT or this interactive chat.
- No new recurring stage, queue, retry loop, quota, scheduler, producer identity or backlog manager is introduced.

## Planned minimal lifecycle repair
No pre-existing Taste archive/quarantine location was found in the current `data/ai_inbox` layout. Introduce a dedicated historical Taste archive outside the active inbox, preserve the old gen1 file there, and add focused regression proving archived stale producer evidence is not scanned while the same stale producer remains rejected if placed back in the active inbox.

## Changes
- Durable report created before implementation changes.

## Validation
- Root-cause confirmation: PASS by current workflow/script inspection plus prior failed run evidence.
- Existing Chernobylite result freshness/current-binding check: PASS.
- Implementation and canonical re-ingest: pending.

## Unresolved
- Historical gen1 artifact has not yet been moved out of the active inbox.
- Chernobylite has not yet been canonically re-ingested/receipted.
- Final queue advancement and exact-once acceptance proof pending.

## Recommended next step
Implement only the archive lifecycle/regression, then remove the preserved gen1 copy from the active inbox so the canonical existing workflow processes the already-present Chernobylite result.

## Efficiency / reusable lesson
`none`
