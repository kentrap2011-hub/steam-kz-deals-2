# WORKER TASK — Taste Dossier Live Prompt Alignment 01

Task ID: `taste-dossier-live-prompt-alignment-01`
Mode: `READ-ONLY / PREP`

## Goal
Prepare the exact replacement text for the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` so its live prompt matches the canonical repository worker contract.

## Source of truth
Read `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, `CHAT_CONTEXT.md`, `reviews/worker_reports/taste-dossier-run-stop-recon-01.md`, and `config/taste_steam_review_dossier_worker_prompt.md`.

## Important UI boundary
Do not spend time trying to read or edit the live Scheduled Task through automation/tool surfaces. Worker access to current Scheduled Task UI fields is unreliable. The user will make any needed UI change manually.

Treat the live prompt already confirmed in the recon report as the current prompt.

## Work
1. Verify the canonical repository prompt is internally consistent with the accepted dossier contract and persistence bridge.
2. Produce the exact full replacement prompt the user should paste into the existing Scheduled Task.
3. Keep the existing intent and do not change schedule, title, Taste Semantic Producer, queue/state ownership, checkpoint size, or any production limits.
4. The replacement must make explicit that checkpoint size is only a durability boundary, the same snapshot must continue checkpoint-by-checkpoint in the same invocation, normal completion is only at `full_backlog_complete=true` and `remaining_required_count=0`, and early stop requires an actual blocker/error/runtime interruption or pending ingest visibility as defined by the canonical contract.
5. Do not modify the Scheduled Task yourself.
6. Do not run production.
7. Do not modify repository runtime/config/contracts unless a real inconsistency is found; if one is found, report it and stop rather than implementing.

## Durable report
Write to main:
`reviews/worker_reports/taste-dossier-live-prompt-alignment-01.md`

Report must contain:
- canonical source refs;
- exact replacement prompt in one copy-ready block;
- a concise manual UI instruction for the user;
- confirmation that schedule/limits/other tasks must remain unchanged;
- one expected next step: user manually replaces the live prompt, then Director performs acceptance planning.

Stop after report. Do not edit the Scheduled Task.