# Taste Dossier Buffered Contract 01

Task ID: `taste-dossier-buffered-contract-01`  
Mode: `IMPLEMENT — CONTRACT ONLY`  
Date: 2026-09-14  
Repository: `kentrap2011-hub/steam-kz-deals-2`

## Final status

`blocked`

The requested canonical buffered-submission contract has been written, but the task cannot truthfully claim the required `production was not run` condition. The first allowed contract write to `config/taste_steam_review_dossier_contract.json` automatically matched the existing production workflow `push.paths` trigger and launched `Build pre-AI deterministic payload` run `34855356658`. That run succeeded and published production-state commits, including `a8095bd96a6a99f8f7addab0cb82dd6b7d5b9c50` (`Refresh atomic pre-AI payload`). No manual workflow dispatch or live Scheduled Task action was performed by this worker.

## Architecture preflight

1. **Owner:** `config/execution_ownership_contract.json` unambiguously keeps scope, ordering, retry/unresolved state, checkpoint merge, completeness, validation, canonical persistence and orchestration in GitHub. Scheduled ChatGPT remains a constrained semantic/data worker.
2. **Canonical authorization before this task:** current dossier V2 fixed the full daily `prepared_required_items[]`, but authorized only the mutable current-checkpoint submission path. The buffered RECON correctly concluded that future groups before canonical ingest required a contract change.
3. **No control-plane transfer:** the new contract permits only local traversal of exact immutable GitHub-predeclared groups after successful create-only publication. It does not give ChatGPT canonical progress, retry, gap, replay, stale, cleanup or completeness authority.
4. **No new ChatGPT queue/backlog manager:** buffer is transport only. GitHub remains the sole queue/retry/completeness owner. No new recurring stage or production quota is authorized.

Architecture preflight verdict before writes: safe for a contract-only additive change; `config/execution_ownership_contract.json` did not require modification.

## Files changed by this worker

- `config/taste_steam_review_dossier_contract.json`
  - commit `f208ebbd3009f5085564cf118c9d2841c6e505b0`
- `config/taste_steam_review_dossier_persistence_bridge.json`
  - commit `0c13fe0e7e0035860191841080cbdadcefd49771`
- `PROJECT_DECISIONS.md`
  - commit `bba236f1bcaeb1689d44e839fe4ff8b62e7ebd6e`
- this report

Per-commit diff inspection confirms the three implementation commits changed only the three files above. Other production-data changes visible in the moving `main` branch came from the automatically triggered production run, not from direct file edits in this task.

## What the canonical contract now authorizes

The dossier contract now authorizes, but does **not activate**, a buffered mode with these rules:

- GitHub fixes the full daily snapshot and order, then predeclares immutable contiguous groups, normally size 10.
- Every group identity binds `snapshot_id`, `prepared_required_sha256`, `sequence`, `start_index`, `end_index_exclusive`, exact ordered items/appids, `items_sha256`, `group_sha256`, `scope_source` and `source_queue_sha256`.
- Group identity is independent of mutable `remaining_required_items` / current `scope_sha256`.
- After successful create-only publication of group N, the worker may process only predeclared N+1 without waiting for canonical ingest N. This is local traversal only, not canonical progress.
- Each group is a separate immutable create-only transport artifact; multiple pending groups for one snapshot are allowed.
- Buffer is explicitly not canonical progress, retry state, a ChatGPT queue or completeness authority.
- Alternate retry filenames and worker overwrite/update/delete are forbidden.
- If the deterministic artifact for the current canonical expected group already exists while canonical progress has not advanced, a later worker invocation must not overwrite, rename, skip or invent retry state; it stops and leaves interpretation to GitHub.
- After interruption, a new invocation reloads GitHub canonical progress and starts from GitHub's expected group; it does not scan the buffer to invent resume order.

## GitHub drain / ownership rules

The persistence bridge now specifies the future GitHub-owned drain:

- a buffer push is only a wake-up signal;
- GitHub derives `expected_sequence` from canonical progress;
- GitHub validates exact predeclared group identity, order, range, hashes, provenance and every dossier;
- GitHub accepts only the maximal valid contiguous prefix;
- `expected=5; buffer=5,6,7,8` may accept `5,6,7,8`;
- `expected=5; buffer=5,6,8` accepts `5,6` and stops at missing `7`;
- malformed/stale-or-wrong-snapshot/reordered/out-of-scope/wrong-identity/invalid expected groups block later groups;
- stale old-snapshot artifacts cannot mutate the current snapshot;
- replay of an already accepted sequence cannot persist or advance canonical state again;
- cleanup belongs only to GitHub;
- all GitHub processes capable of mutating the dossier canonical manifest must share one serialized canonical-writer boundary, at minimum future buffer drain and daily pre-AI snapshot preparation;
- checkpoint size `10` remains a durability boundary, never a run/day/production quota.

`config/execution_ownership_contract.json` was not changed. GitHub remains control plane; Scheduled ChatGPT remains constrained semantic/data plane. Taste Semantic Producer ownership and behavior were not changed.

## Transition mechanism

The contract-first change deliberately retains the runtime-facing V2/V1 identifiers and current validated legacy values:

- dossier contract remains `TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2`, version `2`, status `active`;
- current manifest remains `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2`;
- current legacy create-only path `{snapshot_id}--{scope_sha256}.json` remains active;
- buffered transport is `authorized_not_activated`;
- current worker prompt remains current-checkpoint-only and was not edited;
- buffered activation requires future manifest group-plan support, validator/drain runtime, shared writer serialization, worker-prompt alignment, regression validation and Director acceptance.

This preserves compatibility with the current strict V2 loader, which requires the existing schema/version/status, scope source, checkpoint ownership/semantics, exact same-snapshot advance rule and TTL.

## Current snapshot migration rule

The new contract authorizes a future IMPLEMENT to migrate an unfinished fixed snapshot without rebuilding scope only when all of the following are proven from the existing manifest:

- preserve the same `snapshot_id`;
- derive the group plan only from existing `prepared_required_items[]`;
- prove `prepared_required_sha256` matches those items;
- prove `completed_required_count = prepared_required_count - remaining_required_count`;
- prove `remaining_required_items[]` is exactly `prepared_required_items[completed_required_count:]`;
- prove the accepted prefix lands on a group boundary unless the snapshot is already complete;
- treat groups fully inside that accepted prefix as already accepted, with no recreate/re-ingest;
- continue from the first unaccepted group;
- fail closed if exact prefix/suffix/order/boundary proof cannot be established.

No buffered migration was intentionally executed by this worker.

## Validation

Contract/doc validation performed:

- architecture preflight against execution ownership, current dossier contract/bridge, worker prompt, RECON, live-prompt acceptance, TASTE-004/TASTE-005 decisions and relevant worker pitfalls;
- read-back of both changed JSON contracts from `main`;
- per-commit diff inspection: only the intended contract/bridge/decision file changed in each implementation commit;
- compatibility comparison against `scripts/taste_steam_review_dossier_daily.py` strict V2 loader requirements;
- `config/execution_ownership_contract.json` remains at blob `96a02f5c51e09c60cde31aacd19323ead8d985e0`;
- `config/taste_steam_review_dossier_worker_prompt.md` remains at blob `4d10febaa09f0431e2b6150e6a793e105b60e3d7` and therefore does not activate buffered traversal;
- no ingest script, daily snapshot script, runtime manifest generator/schema implementation, GitHub Actions workflow file, live Scheduled Task, Taste Semantic Producer, schedule or limits were edited by this worker.

### Production-trigger blocker

The required no-production condition was violated by an automatic repository trigger:

- `.github/workflows/build-pre-ai-store-snapshot.yml` includes `config/taste_steam_review_dossier_contract.json` in its `push.paths` production trigger;
- commit `f208ebbd3009f5085564cf118c9d2841c6e505b0` therefore triggered run `34855356658` (`Build pre-AI deterministic payload`), event `push`, conclusion `success`;
- that run published production commit `a8095bd96a6a99f8f7addab0cb82dd6b7d5b9c50` and replaced the dossier work manifest with a newly prepared snapshot `243b8a97751bebc7a7e7e590ce95bbb9701e0bbebc90ed2a727cb2f8ef94647e` at `2026-09-14T14:24:37Z`;
- the previously accepted snapshot from the RECON/live-acceptance evidence was `d75f0b64dc983883a3d97a29c1ba1e0f25c679060ffdb5de269c10fadf05a180` with accepted progress `40/584` and `544` remaining.

This worker did not attempt to revert or manually rewrite production state because the task explicitly forbids production-state mutation, and a revert/push could trigger further production work. No further runtime IMPLEMENT was started.

## Blocker / Director decision required

The contract content itself is ready for review, but this task cannot be marked `complete_ready_for_director_acceptance` while also asserting that production was not run. The Director must decide how to handle the unintended snapshot refresh and whether the new current snapshot is acceptable or requires a separately authorized recovery.

For future contract-only writes to files listed in production `push.paths`, the write procedure must account for trigger suppression/isolation before committing to `main`; otherwise a nominally contract-only task can mutate production state.

## Next step

After Director review and resolution/acceptance of this blocker, the planned next architecture step remains a **separate buffered-submission IMPLEMENT task**. It should implement manifest group-plan representation, buffered drain/runtime validation, one shared serialized canonical-writer rule, workflow wake-up semantics and worker-prompt activation. This worker stops here and does not proceed to runtime implementation.

Efficiency / reusable lesson: production-trigger paths must be checked before direct `main` writes in future contract-only tasks; this task provides a concrete candidate for a reusable worker pitfall.