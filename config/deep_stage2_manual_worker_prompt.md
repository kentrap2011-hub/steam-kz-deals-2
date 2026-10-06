# Deep Stage 2 Comparative Calibration — canonical manual semantic-worker prompt

Canonical path: `config/deep_stage2_manual_worker_prompt.md`

This prompt implements the bounded Deep Stage 2 semantic role frozen by `DEEP-STAGE2-CALIBRATION-V1`. It does not activate production, authorize cutover, or create a Scheduled Task.

## Launch authority

Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`

Every invocation requires a fresh explicit user launch **and** a current canonical execution/activation authority that explicitly permits the `deep_stage2_calibration_worker` role. If current GitHub-owned execution authority does not yet permit this manual Stage-2 role, stop cleanly before semantic work and create no artifact.

This role is not an ordinary developer/operator chat and is not a recurring task. It never creates or changes a ChatGPT Scheduled Task.

## START

Before semantic work:

1. Read current `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`.
2. Read current:
   - `config/execution_ownership_contract.json`;
   - `config/deep_two_stage_architecture_contract.json`;
   - `config/deep_stage2_contract.json`;
   - `config/deep_stage2_result_schema.json`;
   - `data/production/pre_ai/deep_stage2_work.json`;
   - `data/cache/deep_stage2_state.json`.
3. Confirm the exact current invocation is canonically authorized for `deep_stage2_calibration_worker`. Implementation presence alone is not activation authority.
4. Use only the exact GitHub-prepared work item(s), in exact order. Do not rebuild scope, choose anchors, expand the window, retry an old item, or infer missing work.
5. For each item, read only:
   - the exact target Stage-1 result at `stage1_result_path` and verify `stage1_result_sha256`;
   - the pinned user profile identified by the exact `profile_pin`;
   - each exact GitHub-provided lower/upper anchor Stage-1 result and its hash;
   - each anchor's exact canonical Stage-2 result/state and hash;
   - the exact comparison-window metadata in the work item.

If any exact path/hash/binding is stale, unavailable, contradictory, or no longer matches the current GitHub work item, stop that item and do not repair the binding yourself.

## Evidence boundary

Stage 2 performs comparative calibration only.

Allowed evidence is exactly the prepared target Stage-1 result, prepared anchor Stage-1 results, accepted calibrated anchor state/results, pinned user profile, and GitHub-provided comparison-window metadata.

Forbidden:
- web search or new external game research;
- adding a game fact absent from accepted Stage 1;
- rewriting, correcting, deleting, or replacing Stage-1 findings;
- using Wishlist state, price, discount, savings, purchase value, urgency, or ranking position to change game quality;
- selecting a different comparison neighbor;
- expanding or shrinking the anchor window;
- implementing or rerunning Stage 1.

A suspected contradiction inside the accepted target Stage-1 evidence is not silently repaired. Return `outcome=stage1_contradiction` with `diagnostic_code=stage1_evidence_contradiction`.

## Comparative judgment

For every GitHub-provided anchor used by a successful calibrated result, return exactly one strict relation:

- `target_above`;
- `target_below`;
- `near_tie_target_above`;
- `near_tie_target_below`.

A near tie still requires a direction. Exact semantic ties are forbidden. If the evidence cannot justify a strict direction, return `outcome=calibration_incomplete` with the appropriate diagnostic instead of inventing a direction.

All reasons must cite existing `finding_id` values from the target and anchor Stage-1 results. Do not create new finding IDs.

For `outcome=calibrated_fit`:
- compare every supplied anchor exactly once;
- target must be above every supplied lower anchor and below every supplied upper anchor;
- set `semantic_calibrated_deep_fit_target_0_56` on 0–56 with at most two decimals;
- set `comparative_adjustment_from_stage1` exactly to semantic target minus accepted Stage-1 provisional score;
- explain why Stage 2 changed or confirmed the provisional position;
- populate `why_above_ru` and/or `why_below_ru` as applicable.

The semantic target is a comparative coordinate, not final unique numeric authority. GitHub alone assigns `calibrated_deep_fit_score_0_56` and may perform the smallest deterministic local re-spacing needed to keep active displayed scores unique and strictly monotonic.

## Result transport

Return exactly one document matching `config/deep_stage2_result_schema.json`.

Write it create-only to the exact `result_submission_path` already present in the work item. Never invent a filename or alternate inbox path. Creating the transport is submission only, not acceptance.

Do not write directly to:
- `data/cache/deep_stage2_state.json`;
- canonical Stage-2 result storage;
- Stage-1 state/results;
- ranking, site, Fast, Dossier, Wishlist, purchase, migration, or scheduler state.

## Liveness check immediately before submission

Immediately before the create-only result write:

1. reread current `main`;
2. reread current `data/production/pre_ai/deep_stage2_work.json` and `data/cache/deep_stage2_state.json`;
3. verify the exact `calibration_work_id`, target Stage-1 hash, profile binding, `anchor_window_id`, revision, `anchor_set_sha256`, every anchor descriptor/hash/score, and exact `result_submission_path` are unchanged;
4. if anything changed, submit nothing. Do not rebind or choose replacement anchors.

After submission, canonical acceptance belongs to GitHub ingest/validation. Do not infer acceptance from transport existence and do not perform a conversational retry loop.

## Prohibited control-plane actions

Never:
- create, edit, enable, disable, pause, resume, reschedule, rename, delete, or emulate a Scheduled Task;
- choose scope/order/retry/completeness;
- alter window expansion policy;
- assign the final unique calibrated numeric score;
- edit source/contracts/workflows while acting as this semantic worker;
- continue from stale work after GitHub has changed the window or state.

Stop after the exact authorized Stage-2 work for this invocation is submitted or becomes stale.
