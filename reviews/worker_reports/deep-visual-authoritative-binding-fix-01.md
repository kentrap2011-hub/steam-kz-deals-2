# Deep visual authoritative binding fix 01

## Task

- Task ID: `deep-visual-authoritative-binding-fix-01`
- Task file: `WORKER_TASK_DEEP_VISUAL_AUTHORITATIVE_BINDING_FIX_01.md`
- Repository/source of truth: `kentrap2011-hub/steam-kz-deals-2@main`
- Mode: `IMPLEMENT / VALIDATE`
- Implementation PR: #102, `Fix authoritative Deep visual binding`
- Final status: `blocked`
- Dossier production/state/semantics, semantic backlog execution and Scheduled Tasks were not investigated or changed.

## Architecture preflight

Confirmed before writes:

- GitHub/GitHub Actions remains the owner of Progressive state projection, validation, persistence and visual publication under `config/execution_ownership_contract.json`.
- `config/progressive_personalization_contract.json` makes trustworthy current completed Deep/PASS 2 authoritative over Fast for the same current identity.
- Browser presentation remains read-only; no browser-side semantic inference was added.
- This change adds no scheduler, queue, retry loop, recurring stage, semantic-scope change, Deep recovery change, Dossier change or Scheduled Task change.

## Accepted root cause

Accepted diagnosis from `reviews/worker_reports/deep-visual-statistics-staleness-diagnostic-01.md` remained valid on fresh `main`.

`scripts/grounded_negative_visual.py::apply_to_document()` treated compatible cache and `progressive_pass1` as current personalized bindings, but omitted trustworthy authoritative `progressive_pass2`. Full visual builds therefore projected current Deep correctly and then failed with `personalized card binding is not current/INCLUDE` before persistence.

No pipeline-wide re-diagnosis was performed.

## Changes

Merged in PR #102:

1. `scripts/grounded_negative_visual.py`
   - added `has_current_personalized_binding(game, projection)`;
   - compatible `cache_hit` and existing `progressive_pass1` behavior is preserved;
   - `progressive_pass2` is accepted only when the projected card also proves:
     - `analysis_resolution_pass == 'pass2'`;
     - `pass2_attempted is True`;
     - `deep_stage_state == 'completed'`;
     - `deep_stage_outcome` is `fit` or `not_fit`;
     - `effective_analysis_source == 'deep'`;
     - `analysis_state` is authoritative `analyzed_fit` or `analyzed_not_fit`.
   - a bare/stale `analysis_semantic_source='progressive_pass2'` is therefore insufficient and remains fail-closed.

2. `scripts/test_progressive_personalization.py`
   - regression for `projection_status=ai_required + current authoritative Deep analyzed_fit`: no erroneous binding RuntimeError;
   - authoritative Deep `analyzed_not_fit` remains excluded from visible fit ordering consistently with the canonical contract;
   - stale/non-current Deep still raises the binding RuntimeError;
   - existing Fast and compatible-cache admission remain unchanged.

3. `CURRENT_TASK.md`
   - task was marked in progress during implementation; final blocked state is recorded separately after this report.

No Dossier files, Deep semantic conclusions/results, recovery state, queues, schedulers or Scheduled Task configuration were modified.

## Validation

Focused validation:

- PR #102 head: `507ca5469ad5253806006b692869a72419be581b`.
- `Validate Progressive PASS 2 core` PR run `36338449599` / run #221: **success**.
- Job `108673701184`: **success**.
- The workflow explicitly ran `python scripts/test_progressive_personalization.py`; regression output: `progressive personalization Phase A fallback / Phase B regression: ok`.
- `Validate backlog dispositions` PR run `36338449625` / #1291: **success**.
- Branch push PASS 2 validation run `36338431765` / #220: **success**.
- PR #102 merged cleanly to `main` as `54eea6427ff3a5a03643507865d5a02442737831`.
- Post-merge `Validate Progressive PASS 2 core` run `36338505305` / #222: **success**.

The PR validation also showed current authoritative Deep state was non-zero, proving the regression was exercised against an architecture where Deep is active.

## Published result

The Deep-binding defect itself is repaired: after merge, full visual builds pass the formerly failing Deep personalized-binding stage.

Evidence:

- `Build daily visual payload` run `36338505197` / #803:
  - `Build and refresh canonical visual payload once`: **success**;
  - log: `visual progressive items=405 total=409 fit=25 incomplete=0 not_analyzed=380`;
  - log: `VISUAL_FINAL_BUILD=BUILT`;
  - the old `personalized card binding is not current/INCLUDE` failure did not recur.
- Following normal production update, run `36338550470` / #804:
  - full visual build again reached `VISUAL_FINAL_BUILD=BUILT`;
  - log: `visual progressive items=393 total=397 fit=25 incomplete=0 not_analyzed=368`;
  - the Deep-binding failure again did not recur.

However the task's required end-to-end publication acceptance is **not complete**. Both builds subsequently failed at the independent Russian-description publication gate:

- invalid card: `game:1213210`, `Command & Conquer™ Remastered Collection`;
- `description_status: needs_translation`;
- validator result: `Russian description validation failed: 1/25 personalized cards are not meaningful Russian`.

Because that later gate failed:
- canonical visual persistence was skipped;
- deploy run `36338538312` / #841 was skipped after build #803;
- deploy run `36338577554` / #842 was skipped after build #804;
- no new Pages artifact exists for this repair;
- `data/production/visual/current.json` on current `main` still has the old blob `c0d351655280b84db0d65eb41e8c1488c65e1938`, so the required deployed non-zero Deep counters cannot yet be claimed.

Current canonical Deep after the normal production update is already non-zero:
- `data/production/pre_ai/progressive_pass2_work.json` blob `eb6bbfe035b54f8aec455d62c4eb1d465e8a6e1b`;
- total current coverage target: `398`;
- first-pass attempted: `30`;
- authoritative completed: `30`;
- completed fit: `26`;
- completed not-fit: `4`;
- incomplete/recovery: `0`;
- waiting for Dossier: `368`;
- ready/pending: `0`;
- remaining until all authoritative: `368`.
- current PASS 2 state blob: `dd0bbb5150fad574a1ef17bbe0eaab440de050d6`.

These values were not manually produced or processed by this task.

## Unresolved

One unrelated downstream publication prerequisite remains: the existing Russian-description gate rejects `game:1213210` because its current description is `needs_translation`.

This task does not modify that subsystem. Until the owning Russian-description path makes that card valid, the full visual build cannot persist and Pages cannot deploy, so the end-to-end Deep statistics publication acceptance cannot be completed here.

## Status

`blocked`

Implementation of the authoritative Deep binding is merged and validated. End-to-end publication is blocked only after that repaired stage by the independent Russian-description validation gate described above.

## Recommended next step

Create exactly one bounded follow-up for the existing GitHub-owned Russian-description path to make `game:1213210` pass the meaningful-Russian validation, then allow the normal full visual build and Pages deploy to run and verify that the deployed Deep counters/provenance match then-current canonical PASS 2 state; do not change Deep/Dossier semantics or process semantic backlog manually.

## Exact PR/commit/run/artifact refs

- Task: `WORKER_TASK_DEEP_VISUAL_AUTHORITATIVE_BINDING_FIX_01.md`
- Accepted diagnostic: `reviews/worker_reports/deep-visual-statistics-staleness-diagnostic-01.md`
- Implementation branch: `fix/deep-visual-authoritative-binding-01`
- Work-state commit: `a657cea276bfaa574104bf4c19472d576062d916`
- Producer fix commit: `d464df06310f12ac38d5968053c4628e74b4196d`
- Regression commit / PR head: `507ca5469ad5253806006b692869a72419be581b`
- PR: #102
- Merge commit: `54eea6427ff3a5a03643507865d5a02442737831`
- PR PASS 2 validation: `36338449599` / #221, job `108673701184`, success
- PR backlog validation: `36338449625` / #1291, success
- Post-merge PASS 2 validation: `36338505305` / #222, success
- First post-merge full visual build: `36338505197` / #803, build job `108673889384`; visual-build step success, later Russian-description gate failure
- Next normal full visual build: `36338550470` / #804, build job `108674011648`; visual-build step success, later same Russian-description gate failure
- Deploy after #803: `36338538312` / #841, skipped
- Deploy after #804: `36338577554` / #842, skipped
- New Pages artifact: none
- Current stale canonical visual blob: `c0d351655280b84db0d65eb41e8c1488c65e1938`
- Current PASS 2 work blob: `eb6bbfe035b54f8aec455d62c4eb1d465e8a6e1b`
- Current PASS 2 state blob: `dd0bbb5150fad574a1ef17bbe0eaab440de050d6`

## Efficiency / reusable lesson

The accepted diagnostic and `PROJECT_ROUTES.md` were sufficient to avoid re-diagnosing Deep → visual → deploy. The durable regression is now inside the existing Progressive validation gate, so future changes that again reject a fully current authoritative Deep binding should fail before merge.

The remaining delay in end-to-end acceptance was not caused by re-investigation of the original defect: it came from waiting for GitHub validation/build/deploy and then proving that a later independent Russian-description gate, rather than the repaired Deep guard, is the new publication boundary.
