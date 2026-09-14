# Taste Dossier Run Stop RECON 01

Status: `recon_complete_live_prompt_contract_drift_exact_stop_trigger_unobservable`

Date: 2026-09-14

## Scope

READ-ONLY / RECON of why the production Scheduled Task `Taste Steam Review Dossier` stopped after 30 dossiers/checkpoints instead of continuing the same prepared dossier snapshot to completion. No production Taste state, Scheduled Task configuration, scheduling, limits, queue, dossier backlog, or semantic producer settings were changed by this recon. The only write is this durable report.

## Confirmed live Scheduled Task prompt

The user supplied and explicitly confirmed the actual live prompt for Scheduled Task `Taste Steam Review Dossier`:

> Run the production Steam review dossier collector for Taste. Use the existing implemented production path for Steam review dossier collection, process the current eligible backlog according to production limits and state, persist produced dossier artifacts/state through the existing production mechanism, and report the run result. Do not modify Taste Semantic Producer scheduling or limits.

This live prompt is treated as authoritative evidence for this recon.

## Canonical repository prompt

Canonical repository prompt:

`config/taste_steam_review_dossier_worker_prompt.md`

Current blob SHA:

`4d10febaa09f0431e2b6150e6a793e105b60e3d7`

The canonical prompt explicitly requires all of the following:

- read the latest prepared `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2` manifest;
- process only the exact `current_checkpoint_items[]`, in order;
- treat checkpoint size (normally 10) only as an internal durability boundary, never as a run quota, daily quota, production limit, or overall scope limit;
- after an accepted checkpoint is ingested and the same-snapshot manifest advances, reload that updated manifest and continue the next checkpoint in the same Scheduled Task invocation when the advanced manifest is visible;
- stop normally only when `full_backlog_complete=true` and `remaining_required_count=0` for that same snapshot;
- stop early only when ingest has not completed yet after submission, or when a real platform/tool/runtime limit interrupts the invocation.

The same invariant is also explicit in `config/taste_steam_review_dossier_contract.json` (`fc636a84d7542c025fa785abd6fa7abe85a116b9`):

- semantic worker responsibility: `continue_successive_same_snapshot_checkpoints_in_same_run_until_complete_or_real_runtime_limit`;
- `checkpoint_size: 10`;
- checkpoint semantics: `internal_durability_boundary_not_scope_quota`;
- same-invocation rule: `continue_through_successive_same_snapshot_checkpoints_until_exhausted_or_real_platform_runtime_limit`;
- forbidden interpretations include `daily_cap`, `run_quota`, `production_limit`, `overall_scope_limit`, and `completion_after_first_checkpoint`.

`config/taste_steam_review_dossier_persistence_bridge.json` (`515ee3efd3e5c9c9bdf0d35db9f46a115788cbba`) additionally lists `checkpoint_as_quota` as forbidden.

## Live prompt versus canonical prompt

The live prompt is materially weaker than the canonical prompt.

The live prompt says to process the current eligible backlog “according to production limits and state,” but it does **not** explicitly say to:

- read `config/taste_steam_review_dossier_worker_prompt.md` as the authoritative worker contract;
- reload the same-snapshot work manifest after each accepted checkpoint;
- continue checkpoint after checkpoint in the same invocation;
- ignore checkpoint size as a run/production quota;
- continue until `full_backlog_complete=true` and `remaining_required_count=0`;
- use the canonical early-stop conditions.

Therefore the live prompt does **not** state the completion invariant clearly enough to guarantee the canonical behavior. “Process the current eligible backlog” points toward broad processing, but the phrase “according to production limits and state” leaves the worker to infer what the limits are. The canonical contract removes that ambiguity; the live prompt does not.

Conclusion on prompt sufficiency: **No. The live prompt is not sufficiently explicit to require checkpoint-by-checkpoint continuation to `full_backlog_complete=true`.**

## Confirmed production run evidence

The production run persisted three successive checkpoints of 10 dossiers each:

1. Submit commit `7b7dc465a1c4b60fd5c1fb57aadf8b11bf042e12` — `Submit Steam review dossier checkpoint`.
2. Ingest commit `71c7e9b428a0b27f31722266470312e448ecbbd1` — `Ingest Steam review dossier checkpoint`.
3. Submit commit `1279950c19cf6bb2dcdf9e25988fa984cb56e810`.
4. Ingest commit `72f73703f3a09813370caaf0f46163a4da1162dd`.
5. Submit commit `6a94f482810ebbcc84a990094ea6a4d89a3acfb3`.
6. Ingest commit `d9aecc014a9298cf10dab5f0a6de5ebb7707dfec`.

The current same-snapshot manifest is:

`data/production/pre_ai/taste_steam_review_dossier_work.json`

Manifest SHA:

`522d8a5f27a08ada96fb7669ca24889326af9385`

Relevant state:

- `snapshot_id = d75f0b64dc983883a3d97a29c1ba1e0f25c679060ffdb5de269c10fadf05a180`
- `prepared_required_count = 584`
- `checkpoint_size = 10`
- `checkpoint_semantics = internal_durability_boundary_not_scope_quota`
- `completed_required_count = 30`
- `remaining_required_count = 554`
- `current_checkpoint_count = 10`
- `full_backlog_complete = false`
- `status = work_required`

The arithmetic is exact: `30 + 554 = 584`.

Thus the task stopped with the same prepared snapshot still incomplete and with another normal 10-item checkpoint already available.

## Is 30 a real production/run limit?

**No. There is no repository contract or manifest evidence that 30 is any real limit.**

The only configured checkpoint size is 10, and the canonical contract explicitly states that checkpoint size is an internal durability boundary, not a quota. The persistence bridge explicitly forbids treating checkpoint boundaries as quota. The observed 30 is simply three accepted 10-item checkpoints.

No configured `30`-item run cap, production cap, daily cap, or overall scope cap was found or is expressed by the active dossier contract, persistence bridge, canonical worker prompt, or current work manifest.

## Cause classification

### Confirmed classification

`premature_worker_stop_with_live_prompt_contract_drift; no_real_30_limit`

The durable, confirmed defect is **instruction/contract drift between the live Scheduled Task prompt and the canonical repository worker prompt**. The live prompt does not bind the worker to the canonical same-invocation checkpoint loop or to the explicit completion condition. This makes a premature “run result” after several successful checkpoints permissible under the live wording even though it violates the canonical repository contract.

The repository evidence simultaneously rules out `30` as a legitimate production/run quota.

### What cannot be confirmed

The exact internal termination trigger of that ChatGPT invocation is not exposed by the available evidence. There is no authoritative telemetry here proving that the invocation ended because of a model decision, wall-clock limit, context limit, platform interruption, safety layer, client disconnect, or another hidden runtime condition.

Accordingly, no such hidden cause is claimed.

The narrow evidence-based statement is:

- the worker stopped prematurely after three successfully persisted checkpoints;
- the repository still required additional work;
- no real 30-item limit exists in the canonical production contract;
- the live prompt failed to explicitly require the canonical continuation invariant;
- the exact hidden runtime reason for termination after the third checkpoint is **unobservable from available telemetry**.

## Recommended next step

Update the existing live Scheduled Task prompt so it directly binds to the canonical worker contract. Prefer either the canonical prompt itself or an explicit instruction to read and follow `config/taste_steam_review_dossier_worker_prompt.md` as authoritative, including this mandatory invariant:

- after every successfully ingested checkpoint, reload the advanced manifest and continue the next checkpoint in the same invocation;
- do not treat checkpoint size as a run/daily/production limit;
- stop normally only at `full_backlog_complete=true` and `remaining_required_count=0`;
- stop earlier only when checkpoint ingest is not yet visible or a real platform/tool/runtime limit actually interrupts execution.

After that prompt correction, use the existing Scheduled Task again; it should resume from the remaining state of the latest prepared snapshot rather than changing scheduling or introducing a new limit/scheduler.

No change to Taste Semantic Producer scheduling or limits is recommended by this recon.
