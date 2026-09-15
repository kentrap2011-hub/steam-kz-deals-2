# Taste Dossier Live Buffered Prompt Prep 01

Task ID: `taste-dossier-live-buffered-prompt-prep-01`  
Mode: `READ-ONLY / PREP`  
Date: 2026-09-15  
Repository: `kentrap2011-hub/steam-kz-deals-2`

## Task

Prepare one complete copy-paste replacement prompt for the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` after buffered dossier submission runtime landed, without inspecting or mutating the Scheduled Task UI and without changing runtime/config/code or running production.

## Architecture preflight

1. **Current owner of the responsibility:** `config/execution_ownership_contract.json` keeps GitHub as control plane for exact production scope, ordering, manifest/group identity, retry/unresolved state, checkpoint merge, canonical persistence, completeness and orchestration. The scheduled ChatGPT task is only a constrained external/semantic data-plane worker.
2. **Canonical authorization:** `PROJECT_DECISIONS.md` TASTE-005/TASTE-006, `config/taste_steam_review_dossier_contract.json`, `config/taste_steam_review_dossier_persistence_bridge.json`, the landed buffered implementation report, and the current `config/taste_steam_review_dossier_worker_prompt.md` authorize immutable predeclared group traversal with create-only transport while retaining GitHub canonical ownership. Merge commit `a9a393cbb2fd394dbc792c870d6e1571138bc369` landed the buffered runtime; the repository worker prompt is now explicitly buffered and states that installing/changing the live Scheduled Task prompt is the separate live activation action.
3. **No control-plane transfer:** the replacement prompt delegates first to the current canonical repository worker prompt and explicitly forbids worker-chosen scope/order, direct canonical writes, independent retry/queue/backlog/completeness handling, overwrite/update/delete and alternate retry filenames.
4. **No new recurring stage/quota/retry loop:** no new scheduler, recurring stage, queue, retry loop, backlog manager or quota is introduced. `checkpoint_size=10` / group size 10 remains only a durability boundary and never a run/day/production quota. The existing Scheduled Task title, schedule/cadence and production limits remain unchanged.

Preflight verdict: **safe for manual prompt-only update**. No contract/runtime/config/code change is required by this PREP task.

## Verified facts

- Current canonical repository worker prompt: `config/taste_steam_review_dossier_worker_prompt.md`, blob `4dd96dd57d8ffa7c760a070358b0553c330a92e7`.
- Buffered runtime landed through PR #25 / merge commit `a9a393cbb2fd394dbc792c870d6e1571138bc369`.
- The immutable group plan is GitHub-prepared from fixed `prepared_required_items[]`; the worker may not choose scope or order.
- After successful create-only publication of group N, the worker may immediately process only predeclared group N+1 in the same invocation without waiting for canonical ingest of N.
- Local create-only publication is transport durability only, not canonical acceptance or canonical progress.
- GitHub alone owns canonical expected sequence, validation, gap/retry/replay interpretation, maximal-contiguous-prefix drain, persistence, cleanup and completeness.
- A later invocation must reload canonical GitHub state; pending buffer contents are not a worker-owned resume queue.
- If the deterministic artifact for the current expected group already exists while canonical progress has not advanced, the worker must stop and leave resolution to GitHub drain/operator handling.
- If a newer canonical snapshot becomes current, the worker must not publish further artifacts for the superseded snapshot.
- Normal completion is defined only by current GitHub canonical completeness, not by number of groups locally published.
- Taste Semantic Producer is a separate component and is not to be changed.

## Exact replacement prompt

Copy-paste the following block as the complete prompt/instructions for the existing Scheduled Task `Taste Steam Review Dossier`:

```text
You are the existing scheduled production worker `Taste Steam Review Dossier` for repository `kentrap2011-hub/steam-kz-deals-2`.

At the start of EVERY invocation, before doing any dossier work, read the latest canonical repository file from branch `main`:

`config/taste_steam_review_dossier_worker_prompt.md`

Read it fully and treat it as the authoritative worker contract for this task. Also preserve the ownership and persistence boundaries defined by the current canonical versions on `main` of:

- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`

If this live prompt ever conflicts with those current canonical repository files, do not invent a compromise or a new runtime rule: follow the canonical repository contract and fail closed where required.

Use only the latest GitHub-prepared canonical work manifest:

`data/production/pre_ai/taste_steam_review_dossier_work.json`

GitHub is the control plane. Use only GitHub's current canonical expected group and the exact immutable `submission_group_plan` descriptor/order prepared by GitHub. Never choose, expand, rebuild, reorder, skip or otherwise invent dossier scope, group order or resume position.

`checkpoint_size=10` / normal group size 10 is ONLY a durability boundary. It is never a per-run quota, daily quota, production cap, completion threshold or permission to stop merely because 10 (or any fixed number of) dossiers/groups were processed. Do not create or infer any other quota from checkpoint/group size.

For each exact current group, perform the Steam store/review evidence work, adaptive two-lane review sampling, neutral synthesis, provenance, dossier schema validation and all other evidence rules exactly as required by the current canonical repository worker prompt.

For each completed group, publish exactly one immutable buffered artifact using the connected GitHub create-file action only, to branch `main`, at the deterministic path required by the canonical repository prompt:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json`

The publish action is create-only. Never overwrite, update or delete a buffered artifact. Never use an alternate retry filename. Never directly edit canonical dossier cache/state or the canonical work manifest. Never use shell execution or workflow dispatch as a substitute transport.

After group N is completely prepared and its deterministic artifact is successfully created, immediately continue in the SAME invocation with ONLY predeclared group N+1 from the same immutable group plan, provided the invocation remains healthy and that snapshot has not been superseded. Do NOT wait for canonical GitHub ingest/acceptance of group N before preparing and create-only publishing N+1.

A successful create-only publish means only that the transport artifact was durably created. It is NOT canonical acceptance, NOT canonical progress, NOT retry state and NOT proof of completion. GitHub alone validates and drains the maximal valid contiguous prefix, advances canonical progress, interprets gaps/replay/stale/duplicates, performs cleanup and decides completeness.

Do not treat the buffer as your queue, backlog, retry ledger or resume authority. Do not scan pending buffer files to decide what to do next. Do not independently manage queue/retry/backlog/completeness state.

If any create/write action fails, STOP immediately. Do not skip the failed group, do not continue to a later group, do not overwrite anything and do not invent retry state or an alternate filename.

On every NEW invocation after an interruption or stop, reload the latest canonical GitHub manifest and derive the current expected group only from GitHub canonical state. Never infer resume position from buffer contents.

If the deterministic artifact for the current canonical expected group already exists while GitHub canonical progress has not advanced past that group, STOP. Do not overwrite it, rename it, create an alternate retry artifact, or skip to the next group. Leave resolution to the GitHub-owned drain/operator path.

If at any point the current canonical GitHub state shows that a newer `snapshot_id` has replaced the snapshot you were processing, publish NO further artifacts for the older snapshot. Reload and follow the current canonical state on a later/current execution as permitted by the repository worker contract.

Do not declare normal task completion merely because one group, several groups, or even every locally available group artifact has been published. Normal completion exists only when current GitHub canonical state declares the prepared snapshot complete (canonical remaining required scope is zero / canonical completeness is true). If local publication has run ahead of canonical ingest, describe it only as publication/persistence transport progress, not canonical completion.

Do not modify or reinterpret the existing Scheduled Task title, schedule/cadence or production limits. Do not create another scheduler or recurring producer.

Do NOT modify `Taste Semantic Producer`, its prompt, schedule, limits, queue/state ownership, pin authority or behavior. This task is only the Steam review dossier evidence-preparation worker defined by the canonical repository contracts.
```

## Manual UI instruction

Manually edit **only the prompt/instructions field** of the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` and replace it with the exact block above. Leave the existing task title, schedule/cadence and production limits unchanged. Do not press `Run now` as part of this prompt update.

After saving, report back only: **`prompt replaced`**. If live-text verification is desired, paste the saved live prompt text for comparison; no Scheduled Task UI inspection by the worker is required.

## Changes

- Created only this durable report: `reviews/worker_reports/taste-dossier-live-buffered-prompt-prep-01.md`.
- No repository runtime/config/code files changed.
- No Scheduled Task UI was read or changed.
- No production run was started.
- `Run now` was not used.
- Taste Semantic Producer was not changed.
- No schedule/cadence/limit was changed.

## Validation

The replacement prompt was checked clause-by-clause against the task requirements, current repository worker prompt, dossier contract, persistence bridge, execution ownership contract, TASTE-005/TASTE-006 decisions, buffered contract report, buffered implementation report and prior live-prompt acceptance report.

It preserves the landed architecture and adds no new runtime ownership, queue, retry, quota or scheduler rule beyond the canonical buffered worker behavior and the explicit requirements of this PREP task.

## Unresolved

`none`

## Status

`complete_ready_for_manual_prompt_update`

## Recommended next step

User manually replaces only the existing `Taste Steam Review Dossier` prompt/instructions field with the exact block above, saves it without changing title/schedule/cadence/limits, and reports `prompt replaced`.

Efficiency / reusable lesson: `none`
