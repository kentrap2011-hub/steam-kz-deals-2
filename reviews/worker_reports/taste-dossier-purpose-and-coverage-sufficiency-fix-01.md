# Worker report — Taste Dossier purpose + coverage sufficiency fix 01

## 1. Final status

`complete_ready_for_director_acceptance`

Task: `WORKER_TASK_TASTE_DOSSIER_PURPOSE_AND_COVERAGE_SUFFICIENCY_FIX_01.md`.

Implementation merged through PR #96. Squash merge commit: `d8061c470cff903fc13ca7f4f5038e95ff232bee`.

## 2. Architecture preflight

Verified before editing:

- GitHub remains owner of Dossier scope/order, binding, validation, persistence, first-pass/recovery state and completeness.
- Scheduled ChatGPT remains a bounded neutral semantic evidence producer with create-only transport.
- Dossier remains profile-agnostic; downstream Deep remains the personalized stage.
- No new scheduler, queue, retry daemon, backlog manager, second producer or numeric work quota was introduced.
- No fixed minimum number of reviews, sources, searches, pages, observations or covered dimensions was introduced.
- Exact-product identity, Russian evidence, temporal/freshness, privacy/provenance and create-only transport rules remain strict.
- TASTE-014 semantic/adaptive boundedness remains active.
- No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action was performed.
- No Dossier or Deep recovery was authorized or manually run.

## 3. Proven defect

The accepted diagnostic `progressive-deep-insufficient-evidence-diagnostic-01.md` established the dominant root cause `DOSSIER_TOO_THIN`: current Dossiers could be structurally valid yet semantically too narrow for downstream Deep analysis.

The implementation closes the specific class of defect where a narrow observation such as localization/menu behavior, generic social enjoyment, one isolated complaint, or one descriptive mechanic could be labeled `research_state:"sufficient"` / `stop_reason:"evidence_stable"` while material exact-product player-experience evidence remained reasonably discoverable.

## 4. Purpose wording added

The active worker prompt and evidence/control contracts now state that Dossier is a neutral, profile-agnostic evidence package for a later personalized Deep semantic worker.

The Dossier worker must provide a sufficiently complete, balanced, evidence-grounded picture of actual game experience. It must not read/use the user's Taste profile to choose evidence, cherry-pick favorable/unfavorable evidence, score personal fit, or decide include/exclude.

A valid observation is explicitly evidence, not proof that the Dossier is complete.

## 5. Completeness-over-speed rule

The active rules now make semantic completeness and downstream usefulness higher priority than throughput, ordinary latency, minimizing tool calls, or processing more games per invocation.

One valid fact, one usable source, one Russian item, one positive or one complaint is not a semantic stop gate.

This does not authorize unbounded crawling. Equivalent-route suppression, materially distinct-route semantics, exact binding/liveness, ordinary invocation runtime/tool blockers, and fail-closed behavior remain the bounds.

## 6. Coverage-check design

A compact machine-readable `evidence.coverage` attestation is now required for persisted sufficient/stable Dossiers.

Canonical neutral dimensions:

1. `core_play_mechanics`
2. `controls_game_feel`
3. `progression_development_unlocks`
4. `variety_repetition_over_time`
5. `difficulty_mastery_learning_friction`
6. `pacing_structure_direction`
7. `exploration_mission_activity_structure`
8. `multiplayer_coop_dependence`
9. `story_characters_identity_hooks`
10. `recurring_strengths`
11. `recurring_complaints_tradeoffs`
12. `technical_performance_localization_regional`

Each dimension is classified exactly once as:

- `covered`;
- `not_material_or_not_applicable`;
- `exhausted_unavailable`;
- `materially_unresolved`.

A `covered` dimension binds to real final observation indices. A non-covered state binds no observation index. Any `materially_unresolved` dimension rejects a persisted sufficient/stable Dossier.

Closure basis is one of:

- `broad_neutral_picture`;
- `compact_central_experience`;
- `sufficient_after_route_exhaustion`.

The attestation also requires affirmative neutral investigation of meaningful strengths and weaknesses/trade-offs. This is investigation balance, not fabricated one-pro/one-con symmetry.

There is no completeness score and no minimum count of sources/reviews/searches/pages/observations/covered dimensions.

## 7. Narrow-topic anti-stop behavior

The worker prompt now explicitly treats these as anti-stop shapes while material distinct routes remain reasonably discoverable:

- localization/menu-language only;
- generic “fun with friends” only;
- one descriptive mechanic without sustained-experience context;
- one isolated complaint without reasonable corroboration when broader evidence is available;
- aggregate sentiment without concrete player-experience content.

Such evidence may be serialized as useful evidence, but it cannot alone justify a stable Dossier unless the neutral coverage gate genuinely closes or material routes are exhausted under the existing fail-closed rules.

## 8. Validator/schema changes

Changed:

- `config/taste_steam_review_dossier_schema.json`
  - revision `purpose-coverage-sufficiency-2026-09-25`;
  - requires structured `evidence.coverage`;
  - adds coverage dimension/state/closure enums;
  - persisted sufficient Dossier stop reason remains `evidence_stable`.

- `scripts/taste_steam_review_dossier_strict.py`
  - validates exact coverage dimension classification;
  - validates bound observation indices;
  - rejects `materially_unresolved`;
  - enforces balanced-investigation attestations;
  - enforces route-exhaustion closure consistency;
  - rejects a sufficient/stable payload with no covered central-experience dimension unless the route-exhaustion closure explicitly accounts for unavailable central evidence.

Existing strict Russian/provenance/identity/source-mix gates keep their prior failure ordering before the new coverage gate.

## 9. Files changed

PR #96 changed:

- `.github/workflows/validate-taste-dossier-buffered.yml`
- `CURRENT_TASK.md`
- `PROJECT_DECISIONS.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier_strict.py`
- `scripts/taste_steam_review_dossier_test_fixture.py`
- `scripts/test_taste_dossier_contract_contradictions_fix.py`
- `scripts/test_taste_dossier_identity_provenance_generation_fix.py`
- `scripts/test_taste_dossier_purpose_coverage_sufficiency.py`
- `scripts/test_taste_dossier_semantic_bounded_retrieval.py`
- `scripts/test_taste_dossier_transient_author_fallback.py`
- `scripts/test_taste_dossier_validator_generator_parity_fix.py`
- `scripts/test_taste_steam_review_dossier_contract_gaps.py`
- `scripts/test_taste_steam_review_dossier_semantic_consistency.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`

Durable semantic rationale added as `TASTE-015` in `PROJECT_DECISIONS.md`.

`PROJECT_ROUTES.md` did not require an update because the operational route/ownership did not change.

## 10. Tests/workflows with exact refs

PR validation head: `11c92c6a3d2c060344f97cf323b5412ecd7eef24`.

- `Validate buffered Steam review dossier runtime` — run #163, run id `36058048358`: **success**.
  - compilation: success;
  - execution ownership: success;
  - daily snapshot: success;
  - buffered submission: success;
  - same-day preservation: success;
  - strict recovery: success;
  - prepublication parity: success;
  - contract gaps: success;
  - language binding: success;
  - semantic consistency: success;
  - semantic bounded retrieval: success;
  - purpose and coverage sufficiency / COV-01..COV-15: success;
  - transient-author fallback: success;
  - Steam Store review-card parent: success;
  - contract contradiction closeout: success;
  - identity/provenance generation: success;
  - validator-generator parity: success;
  - package identity: success;
  - story DLC scope: success;
  - parallel candidate validation/nonblocking group behavior: success;
  - canonical-writer coalescing liveness: success.

- `Validate backlog dispositions` — run #1198, run id `36058048369`: **success**.

Post-merge normal GitHub activation:

- merge commit: `d8061c470cff903fc13ca7f4f5038e95ff232bee`;
- `Validate execution ownership` — push run #206, run id `36058130164`: **success**;
- `Validate backlog dispositions` — push run #1199, run id `36058130261`: **success**;
- `Build pre-AI deterministic payload` — push run #200, run id `36058130032`: **success**;
- atomic pre-AI result/current main after that run: `efc335509349df42bdac16f1e975f5cf868ef978`.

Fresh `main` inspection after run #200 confirmed both:

- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`;
- `data/production/pre_ai/taste_steam_review_dossier_work.json`

carry:

- evidence contract revision `purpose-coverage-sufficiency-2026-09-25`;
- worker schema revision `purpose-coverage-sufficiency-2026-09-25`;
- worker prompt revision `web-evidence-v2-purpose-coverage-sufficiency-v1`.

Thus deterministic GitHub projection activation is aligned with the new semantic binding.

## 11. COV-01..COV-15 results

All focused cases passed in run #163:

- **COV-01 PASS** — Jurassic World Evolution 2 / 1244460: localization-only + material unresolved core/progression/variety is rejected.
- **COV-02 PASS** — Rubber Bandits / 1206610: generic social-fun slice cannot close with sustained variety/repetition materially unresolved.
- **COV-03 PASS** — Retrowave / 1239690: isolated repetition complaint cannot close while broader central driving/variation coverage is unresolved.
- **COV-04 PASS** — Terraformers / 1244800: one core-loop anecdote cannot skip material progression/variety coverage.
- **COV-05 PASS** — FINAL FANTASY VI / 1173820: story/pacing slice cannot skip material combat/progression/variety coverage.
- **COV-06 PASS** — Severed Steel / 1227690, Need for Speed Heat / 1222680, Scars Above / 1196090 preserve exact appid/title/corroborator identity under the broader coverage contract.
- **COV-07 PASS** — Lake / 1118240 proves one compact, directly central player-experience property may still validate; no source/review-count quota is introduced.
- **COV-08 PASS** — Potion Craft / 1210320 proves one compact long-horizon progression/repetition property may still validate.
- **COV-09 PASS** — no minimum reviews/sources/searches/pages/covered-dimension count/completeness score.
- **COV-10 PASS** — Dossier stays neutral/profile-agnostic; no personal-fit judgment moves into Dossier.
- **COV-11 PASS** — Russian retrieval, provenance/privacy and exact-product guards remain strict.
- **COV-12 PASS** — temporal completeness rules remain intact.
- **COV-13 PASS** — no new scheduler/queue/retry/backlog owner.
- **COV-14 PASS** — buffered traversal plus GitHub-owned persistence/recovery remain unchanged.
- **COV-15 PASS** — completeness-over-speed is explicitly bounded by semantic/adaptive route, runtime/tool and liveness controls.

## 12. Natural production observations

No real failed Dossier or Deep item was manually rerun or recovered.

The normal post-merge GitHub `Build pre-AI deterministic payload` run #200 completed successfully and generated a new current Dossier work/index projection bound to the new coverage contract/schema/prompt revisions. This is the only production-facing activation observed for this task.

No external Scheduled Task action was performed.

## 13. Unresolved

None within this task's authorized scope.

Existing historical Dossier/Deep outcomes are intentionally not recovered or replayed by this task. Any later recovery remains GitHub-owned and separately authorized.

## 14. Director recommendation

Accept `taste-dossier-purpose-and-coverage-sufficiency-fix-01`.

The active Dossier contract now encodes the intended division of labor: Dossier gathers a neutral, sufficiently complete evidence picture; Deep performs personalization. Stable completion is semantic rather than count-based, compact decisive Dossiers remain valid, and strict validation now has a machine-readable coverage gate capable of rejecting explicit material coverage gaps without introducing a profile score or fixed research quota.
