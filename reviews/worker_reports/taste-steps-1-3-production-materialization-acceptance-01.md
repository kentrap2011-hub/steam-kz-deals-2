# Taste Steps 1–3 — Production Materialization Acceptance 01

Status: `blocked_semantic_runtime`

Worker task: `WORKER_TASK_TASTE_STEPS_1_3_PRODUCTION_MATERIALIZATION_ACCEPTANCE_01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Priority: `VERY_HIGH_USER_PRIORITY`
Scope: Taste Steps 1–3 only.

## Executive result

The remaining independent Taste Reviewer maintenance recommendations are implemented and regression-covered, but the production acceptance gate is **not** ready for user verification.

The current canonical V5 pre-AI scope is still fail-closed at:

- semantic scope: `701`
- resolved semantic rows: `0`
- unresolved semantic rows: `701`
- publication allowed by semantic completeness: `false`
- runtime observability: `no_current_scope_progress_observed`
- canonical semantic runtime owner: `scheduled ChatGPT production task`
- last successful semantic execution observed by the repository: `2026-09-01T21:03:08+00:00`
- current scope source mailing update: `2026-09-03T18:53:27.390807+00:00`
- current-scope semantic progress observed: `false`

Therefore the old/current visual snapshot is explicitly rejected as Steps 1–3 acceptance evidence. No completion of the semantic backfill was fabricated, and no second semantic scheduler or parallel queue was created.

`complete_ready_for_user_verification` is **not** claimed.

## Canonical ownership and runtime identity

`config/execution_ownership_contract.json` remains canonical and unchanged by this task:

- GitHub/GitHub Actions own the control plane: scope, queue construction, retry/unresolved state, validation, cache merge, completeness, downstream rebuild and fail-closed publication gating.
- `scheduled ChatGPT production task` owns the constrained external semantic data plane.
- interactive chat is explicitly not a production execution engine/backlog manager.

Runtime inspection from this operator session exposed no scheduled tasks in the available ChatGPT task service. That observation does **not** prove that an external task cannot exist under another runtime/account, but it means this session cannot inspect the required existing producer identity/enabled state/cadence/next run.

The repository itself also records:

- `scheduler_platform_enabled_state = not_exposed_to_repository`
- `expected_cadence_or_next_run_state = not_exposed_to_repository`
- no current-scope progress after the current source snapshot

Because the canonical owner is known but the current semantic scope is not being advanced by an inspectable/live owner, the allowed task status is `blocked_semantic_runtime`.

## Proof that no scheduler/queue duplication was introduced

No semantic automation/task was created from this interactive session.

The new workflow `.github/workflows/validate-taste-step123-maintenance.yml` is an acceptance/maintenance validator only:

- triggers: `push` and `workflow_dispatch`; no cron/scheduled semantic loop;
- it does not consume or manufacture semantic results;
- it does not define a second semantic queue;
- it runs deterministic regressions and production-observability checks;
- it persists only `data/cache/taste_steps123_production_acceptance.json` so current acceptance truth is inspectable in the repository.

The canonical semantic work input remains `data/production/pre_ai/chatgpt_taste_queue.jsonl`, owned by the existing production architecture.

## A1 — durable positive-exception regressions

Implemented durable regression protection for the two explicit positive anchors in `USER_TASTE_PROFILE.md`:

- `Batman: Arkham` — confirmed strong replay-positive anchor;
- `Red Dead Redemption 2` — strong confirmed open-world positive anchor.

Regression behavior:

- generic structural labels such as repetition, complexity, open-world structure or directionlessness cannot become a strong confirmed personal negative by themselves;
- a synthetic `generic_feature_hypothesis` is rejected as an invalid origin for confirmed personal-negative evidence;
- safe fallback remains insufficient/non-confirmed rather than fabricating dislike;
- no broad genre-positive bonus or new ranking rule was added.

Primary regression coverage:

- `scripts/test_taste_evidence_states.py`
- `scripts/test_taste_step123_maintenance_guards.py`

## A2 — durable profile provenance / revalidation guard

Implemented the smallest fail-closed maintenance guard for static title-specific play-role/start-priority calibrations.

`config/play_priority_context_contract.json` now binds every static title-specific calibration to explicit canonical profile evidence fragments for:

- Sifu
- High On Life
- Amnesia: The Bunker
- Terminator: Resistance
- Tails of Iron 2
- Trine 4

`scripts/play_priority_context.py` now validates that binding when the contract is loaded.

The guard fails visibly when:

- a required canonical evidence fragment is materially changed/removed; or
- the set of static title-specific calibrations drifts without matching revalidation coverage.

Unrelated profile edits do not invalidate all calibrations via a coarse whole-file hash.

No role/start values, purchase logic, Taste fit weights or final ranking weights were changed by this maintenance guard.

## Validation and acceptance infrastructure

Implemented:

- `scripts/test_taste_steps123_production_acceptance.py`
- `data/cache/taste_steps123_production_acceptance.json`
- acceptance execution inside `.github/workflows/validate-taste-step123-maintenance.yml`

The acceptance harness reads current committed production inputs:

- `data/production/pre_ai/chatgpt_payload.json`
- `data/production/pre_ai/taste_projection.json`
- `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- `data/production/visual/current.json`

It explicitly refuses to use current visual rows as Steps 1–3 acceptance evidence while semantic completeness is false.

## Relevant commits

Implementation/validation commits observed on `main`:

- `d48ca2145da2585145077265543e25d1ea7fce50` — bind play-priority calibrations to Taste evidence
- `742bfe18020012a5dd70f16b7efefa18322fada1` — add Taste positive-exception/provenance maintenance guards
- `e8858e17620076d58efcb79302b5e4b6c6fb9da8` — add maintenance validation workflow
- `688cc8af88e413033e6763bef1938fb2aa5cc1a7` — enforce profile revalidation guard in producer-owned play-priority contract loading
- `2293386bf9db81e8229c45a9f19bf69f0b37c0fc` — test material profile-evidence change and calibration coverage drift
- `bff786cf25645ece9ef82f620afef2bc6ebe8006` — add Batman/RDR2 positive-exception regressions
- `544364c0210afaa4cf56101aee2b04b1ef64708a` — include positive exceptions in maintenance CI
- `bbe9b6d56ee577814328ed709525ec44f4379afb` — add Steps 1–3 production acceptance harness
- `d549b4454a73369e0f15946481c86afd4548609e` — run production acceptance harness in CI
- `001fab3a86daa1247009f877a3c24964fb96a3de` — make deterministic acceptance snapshot persistable
- `91e9a7d38616300e121104b037ad53c416317923` — persist acceptance observability snapshot in CI
- `baa9c13bf3098c207eb84e735a8a04aba20ab36a` — bot commit of current acceptance snapshot

## CI / run evidence

Run `34010651477`, job `101425759891`: `success`.

Passed stages:

1. role/start behavior + profile provenance maintenance regressions;
2. Taste evidence-state regressions including Batman/RDR2 exceptions;
3. production materialization acceptance gate;
4. deterministic acceptance snapshot persistence.

Key deterministic results from the successful validation chain:

- Sifu: `main_full / high`
- High On Life: `main_full / ordinary`
- Amnesia: The Bunker: `main_full / ordinary`
- Terminator: Resistance: `main_full / ordinary`
- Tails of Iron 2: `secondary_palate_cleanser / ordinary`
- Trine 4: `family_coop / ordinary`
- TMNT: Splintered Fate: `unresolved / unresolved`
- HighFleet confirmed-negative guard: `unresolved / low`
- wishlist invariance: PASS
- sale-urgency invariance: PASS
- ranking-field immutability: PASS
- profile current-evidence guard: PASS
- material profile-evidence change fails closed: PASS
- calibration-coverage drift fails closed: PASS
- Batman positive-exception regression: PASS
- RDR2 positive-exception regression: PASS

## Current production semantic truth

Authoritative committed `data/production/pre_ai/chatgpt_payload.json` at acceptance time:

- schema version: `5`
- status: `degraded`
- source family count: `803`
- AI queue count: `701`
- deterministically excluded without AI: `102`
- resolved semantic count: `0`
- unresolved semantic count: `701`
- publication completeness: `false`

This current V5 state supersedes earlier historical queue/backfill snapshots for this acceptance. In particular, no older ranking snapshot or historical queue count is used to claim completion.

## 10-control current production acceptance table

| Control | Current source/materialization state | Deterministic Step 2 expectation | Acceptance result |
|---|---|---|---|
| Sifu | `not_currently_materialized:not_in_current_source_scope` | `main_full / high` | Deterministic guard PASS; no live card acceptance possible in current source scope |
| High On Life | `semantic_pending_current_scope` (`App_1583230`) | `main_full / ordinary` | Role/start PASS; semantic materialization pending; current visual hit is not acceptance evidence |
| Amnesia: The Bunker | `semantic_pending_current_scope` (`App_1944430`) | `main_full / ordinary` | Role/start PASS; semantic materialization pending; current visual hit is not acceptance evidence |
| Terminator: Resistance | `not_currently_materialized:not_in_current_source_scope` | `main_full / ordinary` | Deterministic guard PASS; old/current visual presence is not current-source acceptance evidence |
| Tails of Iron 2 | `semantic_pending_current_scope` (`App_2473480`) | `secondary_palate_cleanser / ordinary` | Role/start PASS; semantic materialization pending; current visual hit is not acceptance evidence |
| Trine 4 | `semantic_pending_current_scope` (`App_690640`) | `family_coop / ordinary` | Role/start PASS; semantic materialization pending |
| TMNT: Splintered Fate | `not_currently_materialized:not_in_current_source_scope` | `unresolved / unresolved` | Conservative unresolved behavior PASS; current visual presence is not acceptance evidence |
| HighFleet | `semantic_pending_current_scope` (`App_1434950`) | confirmed negative -> `unresolved / low` | **Critical deterministic guard PASS; live semantic materialization still pending; old visual is rejected** |
| Batman: Arkham | `not_currently_materialized:not_in_current_source_scope` | positive exception regression | Generic-risk false-negative regression PASS; no current live materialization |
| Red Dead Redemption 2 | `not_currently_materialized:not_in_current_source_scope` | positive exception regression | Generic-risk false-negative regression PASS; no current live materialization |

For every control absent from the current source/commercial scope, the result is explicitly `not_currently_materialized`; deterministic fixture/regression evidence is supplementary only and is not mislabeled as live production evidence.

## HighFleet critical check

HighFleet is present in the current semantic scope as `App_1434950` and is still semantic-pending.

The post-Step-1/2 deterministic contract proves that an exact ready V5 `confirmed_negative` entry forces:

- `play_role = unresolved`
- `relative_start_priority = low`

This blocks the old bad semantic interpretation from being accepted as a new Steps 1–3 result.

However, the current production semantic row has not completed the V5 materialization. Therefore any old/current visual HighFleet card — including the previously observed stale strong/no-risk/`БРАТЬ СЕЙЧАС` form — is **not** used as acceptance evidence and must not be presented to the user as the new Taste behavior.

## Ranking / commercial invariants

This task did not modify the canonical final ranker or add a second sorter.

No ranking weight was added for:

- play role
- start priority
- Batman/RDR2 positive exceptions
- generic genre positivity

Wishlist/price/discount/sale urgency remain unable to resolve or raise play role/start priority.

## Site readiness

`ready_for_user_site_verification = false`

Reason:

- semantic completeness is false (`701 unresolved / 0 resolved`);
- current visual rows are explicitly rejected as post-Steps-1–3 acceptance evidence while that gate is false;
- no legitimate post-backfill canonical visual regeneration/deploy can be claimed from this task.

The public site must **not** be handed to the user as a verification target yet.

## Blocking condition and exact next action

Blocking condition: the canonical semantic producer is required by `config/execution_ownership_contract.json`, but current-scope progress is not observed and this session cannot inspect an enabled existing scheduled ChatGPT production task.

Minimal required external evidence/action:

1. expose/reconnect the **existing** scheduled ChatGPT semantic production task to an inspectable task service, or provide its inspectable task record;
2. the record must identify the same canonical producer and show at minimum task identity, enabled state, schedule/cadence, and recent/next execution state;
3. do **not** create a second/replacement semantic scheduler unless the canonical ownership contract is explicitly changed first;
4. after the existing producer legitimately processes the current V5 queue through the repository-defined result interface, GitHub control-plane completeness must reach an acceptable state;
5. only then run the normal downstream pre-AI/final visual/deploy chain and re-run this 10-control acceptance.

If the intended scheduled ChatGPT task no longer exists, ownership must be resolved canonically before implementation of any replacement. Interactive chat must not process the 701-row backlog manually.

## Final task status

`blocked_semantic_runtime`

Not ready for user site verification.
