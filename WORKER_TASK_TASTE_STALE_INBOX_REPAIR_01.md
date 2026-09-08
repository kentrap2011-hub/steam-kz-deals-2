# WORKER TASK — TASTE STALE INBOX REPAIR 01

## Task ID
`taste-stale-inbox-repair-01`

## Mode
`DIAGNOSE + MINIMAL IMPLEMENT + RE-INGEST EXISTING CANARY`

## Priority
`URGENT_BEFORE_01_00_PRODUCTION`

## Expected report
`reviews/worker_reports/taste-stale-inbox-repair-01.md`

## Goal
Remove the concrete blocker that prevented the already-produced generation-2 Chernobylite canary from being canonically ingested, without rerunning semantic analysis, creating another Scheduled Task, weakening producer validation, or widening to backlog processing.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `WORKER_TASK_TASTE_CANARY_EXECUTE_NOW_01.md`
- `reviews/worker_reports/taste-canary-execute-now-01.md`
- current Taste inbox/fence/ingest workflow/scripts and lifecycle contracts directly relevant to the blocker.

## Known blocker
The generation-2 canary result already exists:
`data/ai_inbox/taste/canary-app-1016800-gen2.json`

It was not ingested because the whole-inbox producer-fence scan encountered the historical generation-1 file:
`data/ai_inbox/taste/canary-App_10150-producer-g1.json`

The old file belongs to the completed generation-1 producer and must not be accepted under generation 2. The problem is that its continued presence in the active inbox blocks unrelated current generation-2 submissions.

## Hard constraints
- Do NOT delete historical evidence unless an existing canonical lifecycle explicitly requires deletion and preserves equivalent provenance elsewhere. Prefer archive/quarantine/move outside the active inbox when safe.
- Do NOT weaken producer-fence validation.
- Do NOT make generation-1 files acceptable under generation 2.
- Do NOT create a second Scheduled Task.
- Do NOT rerun ChatGPT semantic analysis for Chernobylite if the existing generation-2 result is still current and valid.
- Do NOT process another game.
- Do NOT widen the Scheduled Task to backlog/full production.
- Do NOT use paid OpenAI API, Copilot, or an external scheduler.

## Required sequence

### 0. Durable report first
Create the exact report with status `in_progress`, persist to `main`, and re-read before implementation.

### 1. Confirm the failure mechanism
Confirm from current code/contracts that the active inbox is scanned as a whole and that the stale generation-1 file is the exact deterministic blocker for the current generation-2 canary.

### 2. Determine the correct historical-file lifecycle
Identify the narrowest existing or compatible lifecycle for processed/obsolete/historical inbox artifacts.

Preferred outcome:
- historical generation-1 artifact remains preserved for provenance;
- it is no longer treated as an active candidate in the current inbox;
- active inbox validation remains strict for every file that is actually active.

If the architecture already has an archive/quarantine/processed location, use it. If not, introduce only the smallest clear archive location/behavior required, with regression coverage so stale historical producer generations cannot block all future valid inbox work.

### 3. Implement minimal repair
Repair only the stale-inbox lifecycle / active-scan interaction.

Required properties:
- current active generation-2 envelope still must pass exact producer-id/generation fence;
- old generation-1 envelope must still be rejected if placed in the active inbox;
- historical old artifact is preserved outside the active inbox or otherwise excluded only by an explicit safe lifecycle rule;
- no global ignore of producer mismatches;
- malformed/current mismatched active files remain fail-closed.

### 4. Re-ingest the EXISTING generation-2 canary
If `data/ai_inbox/taste/canary-app-1016800-gen2.json` is still current against the canonical queue/bindings and has not already been accepted:
- use the canonical existing ingest path to process that SAME result;
- do not regenerate semantic content;
- do not produce a second result file;
- verify AppID `1016800` is canonically accepted and receipt/cache/queue state advances appropriately.

If the result is stale or invalid for a reason unrelated to the historical inbox blocker, STOP and report `needs_followup`; do not select a replacement game.

### 5. Verify containment
Prove:
- historical gen1 artifact no longer blocks current inbox processing;
- active gen1/wrong producer artifacts still fail closed;
- existing gen2 Chernobylite result is accepted exactly once;
- no second game was processed;
- Scheduled Task remains the same active task and remains canary-bound;
- permanent schedule remains DAILY 01:00 Europe/Samara;
- no backlog widening occurred.

## Required report
Persist:
`reviews/worker_reports/taste-stale-inbox-repair-01.md`

Include:
- exact root cause confirmed;
- exact historical-artifact lifecycle chosen;
- exact changed paths;
- whether old file was archived/moved and where;
- regression proof that active old-generation files still reject;
- exact Chernobylite re-ingest outcome;
- exact receipt/queue acceptance evidence;
- proof no semantic rerun / no second game;
- whether independent System Audit is now ready.

## Final status — exactly one
- `complete_canary_accepted_ready_for_system_audit`
- `needs_followup`
- `blocked`

Do not start System Audit yourself.
Do not widen production.
Do not start another task.
