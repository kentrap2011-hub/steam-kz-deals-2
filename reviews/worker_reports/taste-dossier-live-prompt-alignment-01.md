# Taste Dossier Live Prompt Alignment 01

## Task
Prepare the exact replacement text for the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` so its live prompt is explicitly bound to the canonical repository worker contract. Do not edit the Scheduled Task, run production, change scheduling/limits, or modify Taste Semantic Producer.

## Verified facts
- The live prompt confirmed in `reviews/worker_reports/taste-dossier-run-stop-recon-01.md` is materially weaker than the canonical worker contract because it does not explicitly require same-snapshot checkpoint continuation through canonical completion.
- `config/taste_steam_review_dossier_worker_prompt.md` is internally consistent with the active dossier contract, persistence bridge, and execution-ownership contract.
- Checkpoint size `10` is an internal durability boundary only, never a run quota, daily quota, production limit, or overall scope limit.
- After every successfully ingested checkpoint, the worker must reload the advanced manifest for the same `snapshot_id` and continue the next checkpoint in the same Scheduled Task invocation when the advanced manifest is visible.
- Normal completion is only `full_backlog_complete=true` and `remaining_required_count=0` for the same snapshot.
- Early stop is permitted only for pending ingest visibility / unchanged create-only submission state as defined by the canonical worker contract, or an actual platform/tool/runtime blocker, error, or interruption.
- GitHub remains control-plane owner for scope, ordering, checkpoint advancement, retry/completeness, validation, and canonical persistence. The Scheduled Task remains the constrained external/semantic data-plane worker.
- No repository inconsistency requiring runtime/config/contract changes was found.

## Exact replacement prompt
Paste this as the complete prompt/instructions field of the existing Scheduled Task:

```text
Run the production Steam review dossier collector for Taste using the existing implemented production path. Before processing anything, read the current `config/taste_steam_review_dossier_worker_prompt.md` from `main` in `kentrap2011-hub/steam-kz-deals-2` and follow it as the authoritative worker contract. Also preserve the active ownership and persistence boundaries defined by `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_persistence_bridge.json`, and `config/execution_ownership_contract.json`.

Use only the latest GitHub-prepared `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2` manifest and only its exact `current_checkpoint_items[]`, in order. Checkpoint size (normally 10) is only an internal durability boundary; never treat it as a run quota, daily quota, production limit, or overall scope limit. After every successfully submitted checkpoint is canonically ingested, reload the advanced work manifest for the SAME `snapshot_id`. If the advanced manifest is visible, continue its next `current_checkpoint_items[]` in the same Scheduled Task invocation. Repeat checkpoint-by-checkpoint for that same snapshot.

Normal completion is allowed only when that same snapshot has `full_backlog_complete=true` and `remaining_required_count=0`. Do not stop merely because one or several checkpoints completed. Stop earlier only when canonical ingest has not yet become visible after submission, the canonical create-only/pending-ingest condition in the worker contract requires stopping, or a real platform/tool/runtime blocker, error, or interruption actually prevents continuation. Never invent completion. Already accepted checkpoints remain durable; a later invocation must reload the latest manifest and resume only the remaining work from the latest prepared snapshot.

Do not refresh or rebuild dossier scope on `Run now` or after checkpoint persistence. Do not invent or reorder scope, create an independent queue/retry loop, reinterpret checkpoint size as a quota, or take over GitHub-owned checkpoint/completeness logic. Persist produced dossier artifacts/state only through the existing canonical repository persistence bridge described by the authoritative worker contract.

Do not modify Taste Semantic Producer, its scheduling or limits. Do not change this Scheduled Task's title, schedule, cadence, checkpoint size, or any production limits. Report the run result according to the canonical worker contract.
```

## Manual UI instruction
Open the existing Scheduled Task `Taste Steam Review Dossier`, edit only its prompt/instructions field, replace the full current prompt with the block above, and save. Leave the task title, schedule/cadence, checkpoint size, production limits, and all Taste Semantic Producer settings unchanged.

## Changes
- No production run was started.
- No Scheduled Task was read or edited through automation/tool surfaces.
- No runtime/config/contract file was modified.
- Taste Semantic Producer, schedules, and limits were not changed.
- GitHub report write was attempted but blocked by OpenAI safety systems; no repository write occurred.
- A local fallback copy of this report was created for preservation.

## Validation
Architecture preflight passed:
1. Existing ownership remains unchanged: GitHub is control plane; the existing scheduled ChatGPT dossier worker is the constrained data plane.
2. The replacement is directly grounded in the active dossier contract, persistence bridge, canonical worker prompt, and execution ownership contract.
3. The replacement transfers no scope, ordering, retry, checkpoint advancement, completeness, validation, or canonical persistence responsibility from GitHub to ChatGPT.
4. It creates no new recurring stage, scheduler, queue, retry loop, quota, or backlog manager.

The replacement deliberately references the canonical worker prompt as authoritative and makes the required checkpoint/completion/early-stop invariants explicit in the live prompt, matching the alignment option accepted by the preceding recon.

## Unresolved
The required repository path `reviews/worker_reports/taste-dossier-live-prompt-alignment-01.md` could not be created because GitHub write attempts were blocked by OpenAI safety systems. The live Scheduled Task also remains unchanged until the user performs the manual UI edit.

## Status
`blocked`

## Recommended next step
Persist this already-prepared report to `reviews/worker_reports/taste-dossier-live-prompt-alignment-01.md` through an allowed repository write path; then the user manually replaces the live prompt of the existing `Taste Steam Review Dossier` Scheduled Task and Director performs acceptance planning. Schedule/limits and Taste Semantic Producer remain unchanged.

## Canonical source refs
- `CHAT_PROTOCOL.md` — blob `fe9fb2e415ee696aa6618d915266eefe47449ff0`
- `DIRECTOR_PROTOCOL.md` — blob `e6e586fa69b38872662f0df3a84fd1d927f75af5`
- `CHAT_CONTEXT.md` — blob `cab7fa7cf1e5dcae9d959ddfbd5a24e2cbfc0b56`
- `WORKER_TASK_TASTE_DOSSIER_LIVE_PROMPT_ALIGNMENT_01.md` — blob `99413a8d6815993c73bc8d0d4fa6260dfee85933`
- `reviews/worker_reports/taste-dossier-run-stop-recon-01.md` — blob `a444e5e1152ec036f180fd92471b56c96e69240d`
- `config/taste_steam_review_dossier_worker_prompt.md` — blob `4d10febaa09f0431e2b6150e6a793e105b60e3d7`
- `config/taste_steam_review_dossier_contract.json` — blob `fc636a84d7542c025fa785abd6fa7abe85a116b9`
- `config/taste_steam_review_dossier_persistence_bridge.json` — blob `515ee3efd3e5c9c9bdf0d35db9f46a115788cbba`
- `config/execution_ownership_contract.json` — blob `96a02f5c51e09c60cde31aacd19323ead8d985e0`

## Efficiency / reusable lesson
none