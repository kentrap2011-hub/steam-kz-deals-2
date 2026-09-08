# taste-stale-inbox-repair-01

## Task
Confirm and minimally repair the stale Taste inbox blocker, preserve the historical generation-1 artifact, and re-ingest the already-produced Chernobylite generation-2 result through the canonical ingest path without semantic rerun, another game, another Scheduled Task, or weakened producer validation.

## Status
`in_progress`

## Verified facts
- The active Taste producer fence is canonical `TASTE-SEMANTIC-RESULT-V5`, active producer `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, generation `2`, with mismatch policy `reject_before_ingest`.
- `.github/workflows/ingest-taste-batch.yml` runs `scripts/taste_producer_fence.py data/ai_inbox/taste` before `process_taste_inbox.py`.
- `taste_producer_fence.py::validate_taste_inbox()` scans every top-level `data/ai_inbox/taste/*.json` and rejects the whole run on the first producer mismatch.
- Before repair, the active inbox contained exactly historical gen1 `canary-App_10150-producer-g1.json` and current gen2 `canary-app-1016800-gen2.json`.
- Prior workflow run `34260132159` failed exactly on the historical gen1 file before the Chernobylite ingest transaction.
- Current Chernobylite queue/bindings matched the already-produced gen2 result before re-ingest.

## Root cause confirmed
The original blocker was deterministic whole-active-inbox fencing: a historical generation-1 submission remained in the active top-level Taste inbox, so the strict generation-2 fence rejected that old file and aborted before the valid-current-generation Chernobylite submission could reach semantic ingest validation.

## Architecture preflight
- Owner of queue scope, validation, persistence and inbox ingest: GitHub/GitHub Actions under `config/execution_ownership_contract.json`.
- Canonical authorization: `config/taste_result_contract.json` producer fence plus the existing GitHub-owned ingest workflow.
- Repair stays inside GitHub-owned artifact lifecycle; it does not transfer control-plane work to ChatGPT or this interactive chat.
- No new recurring stage, queue, retry loop, quota, scheduler, producer identity or backlog manager is introduced.

## Historical-artifact lifecycle chosen
No pre-existing Taste archive/quarantine location existed in the current `data/ai_inbox` layout. A dedicated historical archive outside the active inbox is now defined at `data/ai_archive/taste/**`.

Rules persisted in `data/ai_archive/taste/README.md`:
- only `data/ai_inbox/taste/*.json` is active;
- archived artifacts are provenance only and are not ingest candidates;
- archiving never makes an old producer valid;
- if the same old/wrong producer artifact is put back into the active inbox, normal strict producer fencing still rejects it;
- malformed active files remain fail-closed.

The exact historical gen1 Prototype artifact is preserved at:
`data/ai_archive/taste/generation-1/canary-App_10150-producer-g1.json`

The active copy was then removed by commit:
`440efa3f0bc61d8b70cbda011d99dd5d16d67965`

## Regression / safety proof
Focused regression in `scripts/validate_taste_producer_fence.py` proves:
- archived historical content does not enter the active inbox scan;
- an old-generation producer placed in the active inbox is still rejected;
- malformed active JSON is still rejected.

Canonical re-ingest workflow run `34267795151`, job `102201457478`, independently executed that regression and the unchanged active producer gate:
- `Validate singleton Taste producer fence regression`: PASS;
- `Enforce active producer on canonical Taste inbox`: PASS;
- `Validate normalized taste factor contract`: PASS;
- `Validate taste inbox transactional proof regression`: PASS.

This proves the historical gen1 file no longer blocks the active inbox and producer safety was not weakened.

## Chernobylite re-ingest outcome so far
Removing only the archived gen1 active copy triggered the existing canonical workflow automatically against the already-present `canary-app-1016800-gen2.json`.

Workflow:
- run: `34267795151`;
- head SHA: `440efa3f0bc61d8b70cbda011d99dd5d16d67965`;
- job: `102201457478`;
- no new semantic submission was produced by this worker.

The former stale-file gate is cleared, but the workflow then failed at the later existing step:
`Validate, ingest and rebuild taste consumers atomically` (`scripts/process_taste_inbox.py`).

Therefore Chernobylite is not yet proven canonically accepted. A bounded diagnosis of this later failure is in progress solely to determine whether the existing result is invalid/stale for an unrelated reason, in which case the task contract requires STOP with `needs_followup` rather than semantic rerun or replacement-game selection.

## Changed paths
- `reviews/worker_reports/taste-stale-inbox-repair-01.md`
- `data/ai_archive/taste/README.md`
- `data/ai_archive/taste/generation-1/canary-App_10150-producer-g1.json`
- `scripts/validate_taste_producer_fence.py`
- removed active copy: `data/ai_inbox/taste/canary-App_10150-producer-g1.json`

Implementation refs:
- report start: `6c65eedfb39ad3668b2153aae5e75a04498940fe`
- root-cause checkpoint: `cf25ea2bc2ffdad852e0fa7fbf36e1b6c91e2aa8`
- archive lifecycle README: `4de393be585f2e73cf0f89ec45c0f43a770d84b3`
- preserved historical file: `37b7fecb7de41b7be4e2432c0feb1744438db391`
- focused producer/archive regression: `ff3b80831459045eb9c403a5c85bc5904225abc7`
- active stale-file removal / canonical re-ingest trigger: `440efa3f0bc61d8b70cbda011d99dd5d16d67965`

## Validation
- Original root-cause confirmation: PASS.
- Historical evidence preserved before active removal: PASS.
- Active old-generation/malformed submissions still reject: PASS via canonical run regression.
- Existing current-generation producer fence: PASS via canonical run.
- Historical gen1 no longer blocks current active inbox: PASS via canonical run.
- Chernobylite canonical acceptance: NOT YET — later process step failed.

## Unresolved
- Exact later `process_taste_inbox.py` rejection reason still needs bounded localization.
- Receipt/queue exact acceptance evidence is not present yet and must not be claimed.

## Recommended next step
Localize only the later canonical validation failure for the SAME existing Chernobylite result. If it is unrelated to the stale historical file, stop with `needs_followup` as required; do not rerun ChatGPT, pick another game, create a task, or widen production.

## Efficiency / reusable lesson
`none`
