# WORKER TASK — Taste Dossier Live Buffered Prompt Prep 01

Task ID: `taste-dossier-live-buffered-prompt-prep-01`
Mode: `READ-ONLY / PREP`

## Goal
Prepare the exact replacement prompt text for the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` after buffered-submission IMPLEMENT has landed and been accepted by Director.

The user will manually edit the Scheduled Task UI. Worker chats must NOT attempt to read, edit, or verify Scheduled Task UI state because that surface is unreliable for them.

## START gate
Read fully:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-buffered-contract-01.md`
- `reviews/worker_reports/taste-dossier-buffered-submission-implement-01.md`
- `reviews/worker_reports/taste-dossier-live-prompt-acceptance-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`

Perform architecture preflight before drafting.

## Required output
Prepare ONE complete replacement prompt for the existing live Scheduled Task.

The prompt must:
- instruct the Scheduled Task to read the current canonical repository worker prompt from `main` first and treat it as authoritative;
- preserve the ownership boundaries in the dossier contract, persistence bridge, and execution ownership contract;
- use the latest GitHub-prepared work manifest and exact immutable group plan/order only;
- make checkpoint/group size 10 explicit as durability boundary only, never a quota;
- authorize group N -> successful create-only buffered publish -> immediately group N+1 in the same invocation without waiting for canonical ingest N;
- make clear local create-only publication is not canonical acceptance;
- forbid worker-chosen scope/order, overwrite/update, alternate retry filename, direct canonical state writes, independent queue/retry/backlog management;
- require stop on create/write failure;
- require a new invocation to reload canonical GitHub state rather than infer resume from buffer contents;
- if current expected deterministic artifact already exists while canonical progress has not advanced, require stop and leave resolution to GitHub drain;
- stop publishing an older snapshot if a newer canonical snapshot becomes current;
- define normal completion only by GitHub canonical completeness;
- preserve current Scheduled Task title, schedule/cadence and production limits;
- explicitly say not to modify Taste Semantic Producer.

Do not invent any new runtime rules beyond the landed contract/prompt.

## Manual-UI boundary
Do NOT attempt to inspect the current Scheduled Task prompt or state.
The user will paste the prepared replacement manually.

Therefore the report must provide:
1. exact copy-paste replacement prompt in one fenced text block;
2. concise manual instruction: edit only the prompt/instructions field of the existing `Taste Steam Review Dossier` task and leave title/schedule/cadence/limits unchanged;
3. what the user should report back after saving: simply that the prompt was replaced, or paste the live text if verification is desired.

## Prohibitions
- No repository runtime/config/code changes.
- No live Scheduled Task mutation.
- No production run.
- No `Run now`.
- No Taste Semantic Producer changes.
- No schedule/limit changes.

## Durable report
Write to main:
`reviews/worker_reports/taste-dossier-live-buffered-prompt-prep-01.md`

Report must include architecture preflight, exact replacement prompt, manual UI instruction, and explicit confirmation that nothing was changed/run.

Allowed final status:
- `complete_ready_for_manual_prompt_update`
- `blocked`

Stop after durable report.