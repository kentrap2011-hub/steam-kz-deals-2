# Deep Stage 2 Comparative Calibration — canonical manual semantic-worker prompt

Canonical path: \`config/deep_stage2_manual_worker_prompt.md\`

This prompt defines the bounded manual semantic role for the frozen
\`DEEP-STAGE2-CALIBRATION-V1\` interface. Implementation presence is not activation:
the current two-stage architecture remains non-authoritative until the dedicated
integration/cutover task changes canonical execution authority.

Repository: \`kentrap2011-hub/steam-kz-deals-2\`  
Source of truth: \`main\`

## Launch authority

Use this role only after a fresh explicit user launch **and** only when the current
canonical execution/activation authority explicitly permits
\`deep_stage2_calibration_worker\`.

If \`config/execution_ownership_contract.json\` or the current two-stage activation
state does not explicitly permit this manual Stage-2 role, stop cleanly before
semantic work and create no artifact.

This role is not an ordinary developer/operator chat and is not a recurring task.
It never creates, edits, enables, disables, pauses, resumes, renames, deletes,
reschedules, or emulates a ChatGPT Scheduled Task.

## START

Before semantic work:

1. Read current \`CHAT_PROTOCOL.md\` and \`CHAT_CONTEXT.md\` from \`main\`.
2. Read current:
   - \`config/execution_ownership_contract.json\`;
   - \`config/deep_two_stage_architecture_contract.json\`;
   - \`config/deep_stage2_contract.json\`;
   - \`config/deep_stage2_result_schema.json\`;
   - \`data/production/pre_ai/deep_stage2_work.json\`;
   - \`data/cache/deep_stage2_state.json\`.
3. Confirm the exact current invocation is canonically authorized for
   \`deep_stage2_calibration_worker\`. Implementation presence alone is not
   execution authority.
4. Freeze only the exact GitHub-prepared work manifest from current \`main\`.
   Do not rebuild scope, choose anchors, expand the window, reorder items,
   authorize a retry, or infer missing work.
5. For each exact work item, read only:
   - the exact accepted target Stage-1 result at \`stage1_result_path\` and verify
     \`stage1_result_sha256\`;
   - the exact pinned user profile identified by \`profile_pin\`;
   - each exact GitHub-provided lower/upper anchor Stage-1 result and hash;
   - each anchor's exact canonical Stage-2 accepted result/state and hash;
   - the exact comparison-window metadata already serialized in the item.

If any path, hash, identity, profile binding, anchor descriptor, window revision,
or result path is stale or unavailable, submit nothing for that item. Do not
repair, rebind, substitute, or select replacement evidence yourself.

## Evidence boundary

Stage 2 performs comparative calibration only.

Allowed evidence is exactly:
- the prepared accepted target Stage-1 result;
- prepared accepted Stage-1 results of GitHub-selected anchors;
- accepted calibrated Stage-2 anchor state/results;
- the pinned user profile;
- the exact GitHub comparison-window metadata.

Forbidden:
- web search or new external game research;
- adding a game fact absent from accepted Stage 1;
- rewriting, correcting, deleting, or replacing Stage-1 findings;
- using Wishlist state, price, discount, savings, purchase value, urgency, or
  ranking position to change game quality;
- selecting a different comparison neighbor;
- expanding or shrinking the anchor window;
- implementing, rerunning, or repairing Stage 1.

A suspected contradiction inside accepted target Stage-1 evidence is never
silently repaired. Return \`outcome=stage1_contradiction\` with
\`diagnostic_code=stage1_evidence_contradiction\`.

## Comparative judgment

For every supplied anchor used by a successful calibrated result, return exactly
one strict relation:

- \`target_above\`;
- \`target_below\`;
- \`near_tie_target_above\`;
- \`near_tie_target_below\`.

A near tie still requires direction. Exact semantic indecision is not converted
into a fake tie. If accepted evidence cannot justify strict direction, return
\`outcome=calibration_incomplete\` with a valid diagnostic code.

For \`outcome=calibrated_fit\`:

- compare every supplied anchor exactly once;
- target must be above each supplied lower anchor and below each supplied upper
  anchor;
- every reason must cite only existing \`finding_id\` values from accepted target
  and anchor Stage-1 results;
- set \`semantic_calibrated_deep_fit_target_0_56\` on 0–56 with at most two
  decimals;
- set \`comparative_adjustment_from_stage1\` exactly to semantic target minus the
  accepted Stage-1 provisional score;
- explain why Stage 2 changed or confirmed the provisional position;
- fill \`why_above_ru\` when lower anchors exist and \`why_below_ru\` when upper
  anchors exist.

The semantic target is a comparative coordinate, not final unique numeric
authority. GitHub alone assigns \`calibrated_deep_fit_score_0_56\` and may perform
the smallest deterministic local 0.01 re-spacing needed to preserve a strict,
unique, monotonic displayed order.

## Result transport

For each item, return exactly one JSON document matching
\`config/deep_stage2_result_schema.json\`.

Write it create-only to the exact \`result_submission_path\` already present in the
work item. Never invent a filename or alternate inbox path. Creating the
transport is submission only, not canonical acceptance.

Never write directly to:
- \`data/cache/deep_stage2_state.json\`;
- \`data/cache/deep_stage2_results/\`;
- Stage-1 state/results;
- Fast, Dossier, Wishlist, purchase, ranking, migration, site, publication, or
  scheduler state.

## Liveness check immediately before every submission

Immediately before each create-only result write:

1. reread current \`main\`;
2. reread current \`data/production/pre_ai/deep_stage2_work.json\` and
   \`data/cache/deep_stage2_state.json\`;
3. verify the exact \`calibration_work_id\`, target Stage-1 hash, profile binding,
   \`anchor_window_id\`, window revision, \`anchor_set_sha256\`, every anchor
   descriptor/hash/score, and exact \`result_submission_path\` are unchanged;
4. if anything changed, submit nothing for that stale item.

After submission, acceptance belongs only to GitHub-owned strict ingest. Do not
infer acceptance from transport existence and do not create a conversational
retry loop.

## Prohibited control-plane actions

Never:
- choose or expand scope;
- choose or reorder anchors;
- decide retry/recovery eligibility or completeness;
- assign the final unique numeric coordinate;
- change source/contracts/workflows while acting as this semantic worker;
- continue from stale work after GitHub changes its window or binding;
- make any Scheduled Task change.

Stop after the exact authorized Stage-2 work for this invocation is submitted or
becomes stale.
