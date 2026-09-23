# Progressive Fast/Deep coactivation stale-guard audit 01

Date: 2026-09-23  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Branch/source of truth: `main`  
Audit baseline head before report write: `c1b920828b655e28e131734a91f37d0560445777`  
Mode: READ-ONLY / RECON, except this durable report  
Final status: `complete_additional_analogues_found`

## Executive result

The confirmed PASS 1 ingest defect is independently reproduced from repository/runtime evidence: current canonical architecture and both current Progressive work manifests allow and use `pass1_active=true` together with `pass2_active=true`, while `scripts/ingest_progressive_pass1.py` still rejects that exact state by requiring `pass2_active=false`.

No second production runtime mutual-exclusion/pre-Deep blocker was found in the bounded current production paths required by this task. Current PASS 1 build/contract validation, Deep build/eligibility/ingest/recovery, all inspected shared canonical writers, pre-AI recomputation, and visual/projection validation are compatible with simultaneous Fast+Deep activation.

Additional analogues were found in the guardrail/documentation layer:
1. PASS 1 regression fixtures already model `true/true`, but they do not execute the production ingest guard, so validation can pass immediately before the live ingest fails.
2. The main Progressive validation workflow does not include `scripts/ingest_progressive_pass1.py` in its monitored/compiled/executed validation surface.
3. `PROJECT_ROUTES.md` and historical PPD-004/PPD-005 text in `PROJECT_DECISIONS.md` still contain inactive/pre-activation statements. They are not runtime authority, but they are stale operational guidance after production activation.

## Canonical target state

Current canonical contracts agree on `FAST-DOSSIER-DEEP-V1`:

- `config/progressive_personalization_contract.json`: Fast and Deep do not globally wait for each other; Deep requires neither a prior Fast attempt nor Fast `analysis_incomplete`; Deep may run before Fast; Deep is production-active.
- `config/progressive_pass1_contract.json`: PASS 2 is active/implemented/production-active; Deep is independent from Fast.
- `config/progressive_pass2_contract.json`: `implemented=true`, `active=true`; activation guard has `pass2_active=true`, `deep_active=true`, and production execution authorized.
- `config/execution_ownership_contract.json`: GitHub remains control-plane owner for Fast/Deep scope, ordering, attempts, recovery, persistence, recomputation, and completeness.
- `config/daily_execution_contract.json`: active Phase B PASS 1 and active Phase C PASS 2 both declare `pass2_active=true`.

Current generated state also agrees:
- `data/production/pre_ai/progressive_pass1_work.json`: `pass1_active=true`, `pass2_active=true`, 560 total / 100 attempted / 460 remaining.
- `data/production/pre_ai/progressive_pass2_work.json`: `pass1_active=true`, `pass2_active=true`, 560 Deep coverage target, 1 first-pass attempt, 27 currently ready/pending Deep items.

## AUD-01 — confirmed incident independently verified

Incident evidence was read, not replayed:

- game: Friends vs Friends
- appid: `1785150`
- work_id: `4a85ac1f78ca5a8812a59631c715058f36032959b997b8be2504018c1100eed0`
- create-only result commit: `63ceb92cc4a3628b987a5ee537cb22ca30c35be8`
- failed ingest run: `35812546365`
- failed job: `107027073507`
- exact failure: `Progressive PASS 1 work activation flags are invalid`
- current PASS 1 projection at audit: 100 attempted / 460 remaining

Run `35812546365` checked out current `main`, passed the PASS 1 semantic regression step, then failed specifically in `Ingest independent PASS 1 item artifacts`. The subsequent PASS 2 recompute, PASS 1 revalidation, and canonical commit steps were skipped.

Commit `63ceb92...` added only the exact immutable PASS 1 result artifact. That artifact is still present on `main`, bound to the expected work id/appid, with `outcome=analysis_incomplete` and `issue_code=insufficient_evidence`. This audit did not process, replace, delete, rename, replay, or overwrite it.

The current manifest still has Friends vs Friends as sequence 1, confirming that the failed ingest left canonical Fast progress at 100/560 rather than accepting the result.

## Findings

| ID | path | stale assumption | production reachability | impact | fix scope |
|---|---|---|---|---|---|
| F-01 | `scripts/ingest_progressive_pass1.py:37-38` | **Same root-cause class: yes.** Production ingest still requires `pass1_active=true && pass2_active=false`, a pre-Deep mutual-exclusion rule that directly contradicts current `true/true` canonical work. | **Yes; confirmed live.** Run `35812546365` failed here on the current Friends vs Friends result. | Blocks Fast ingest. Because the shared writer exits at this step, that invocation also never reaches its subsequent Deep recompute/revalidation/commit steps. | Change only this activation guard to accept the canonical coactive state while remaining fail-closed for invalid flags; do not alter the existing result artifact or attempt state manually. |
| F-02 | `scripts/test_progressive_pass1.py:114-117, 141`; `.github/workflows/ingest-progressive-pass1.yml` PASS 1 validation step | **Same migration class: yes, guardrail analogue.** The regression fixture was migrated to `pass1_active=true, pass2_active=true`, but it tests PASS 1 core semantics rather than the production ingest entrypoint/guard. | **Yes as a false-negative guardrail.** The incident run proves the regression can pass immediately before production ingest rejects the same activation state. | Allows a coactivation-breaking ingest predicate to ship undetected; it does not itself mutate or block Deep independently. | Add a focused ingest activation regression that exercises the production guard (or a pure helper used by it), proving canonical `true/true` is accepted and incompatible flag combinations still fail closed. |
| F-03 | `.github/workflows/validate-progressive-pass2-core.yml` path filters / compile & regression steps | **Same root-cause class: no; coverage gap.** The activation validation surface covers PASS 1 tests and the PASS 1 workflow but not `scripts/ingest_progressive_pass1.py` itself. | CI/validation path, not a direct production predicate. | A future change or stale guard isolated to PASS 1 ingest can evade the principal Fast/Deep activation validator. | Add `scripts/ingest_progressive_pass1.py` and the focused activation regression to the validation trigger/compile/test surface. |
| DOC-01 | `PROJECT_ROUTES.md:245,247` | **Runtime root-cause class: no.** The Progressive route still says Deep is “still inactive” and that Scheduled ChatGPT is usable only “after later activation”. | No runtime reachability; navigation/operational guidance only. Canonical contracts take precedence. | Can send later workers toward the pre-activation model and cause repeated rediscovery or a wrong repair premise. | Bounded route refresh after/in the implementation follow-up; no production logic change. |
| DOC-02 | `PROJECT_DECISIONS.md:583,591,603,619` (PPD-005 / PPD-004 historical status/boundary text) | **Runtime root-cause class: no.** Historical decisions retain “inactive / adaptation required before activation” boundary wording without a later durable activation annotation in this decision log. | No runtime reachability; rationale/history only. Machine contracts are current authority. | Creates rationale ambiguity even though current contracts/runtime are active. | Preserve historical rationale but add a clear supersession/activation annotation in a bounded documentation follow-up. |

### Root-cause history for F-01

The stale guard was introduced by commit `3302fe62944b07d17b42bf85b6d530a9ab6dac35` (“Add independent item-level PASS 1 ingest”) while PASS 2 was still inactive.

Immediately before production activation (parent `5511e1499f2f70ec5273ca1caae16e410ff1f640`):
- `scripts/progressive_pass1.py` required PASS 2 to remain inactive;
- `scripts/build_progressive_pass1_work.py` emitted `pass2_active=false`;
- `scripts/test_progressive_pass1.py` fixtures emitted `pass2_active=false`;
- `scripts/ingest_progressive_pass1.py` required `pass2_active=false`.

Activation commit `36113dcd6e29307006f2d1dca6e4a5a6063b6a39` (“Activate Progressive Deep production from fresh main”) migrated the contracts, PASS 1 builder, PASS 1 contract loader, PASS 1 tests, Deep tests, producer/projection checks and visual activation routing to active/coactive Deep. It did **not** modify `scripts/ingest_progressive_pass1.py`. This is therefore a bounded activation-migration omission, not evidence that canonical architecture is ambiguous.

## Negative evidence — inspected paths compatible with simultaneous Fast+Deep activation

### PASS 1 build / contract / projection
- `scripts/progressive_pass1.py` now requires the current PASS 1 contract to declare PASS 2 production-active.
- `scripts/build_progressive_pass1_work.py` explicitly emits `pass1_active=true`, `pass2_active=true`.
- Fast work suppression is only for an exact current **authoritative completed Deep** result; unresolved/waiting/recovery Deep does not suppress independent Fast work.
- `scripts/test_progressive_pass1.py` fixtures and contract assertions use active Deep; the defect is that this test does not exercise the ingest guard, not that its semantic model is stale.

### PASS 2 build / eligibility / ingest / recovery
- `scripts/progressive_pass2.py::dossier_is_eligible` explicitly treats Fast/PASS 1 parameters as irrelevant to `FAST-DOSSIER-DEEP-V1` eligibility.
- `scripts/progressive_pass2.py::recompute_eligibility` considers all current Progressive identities; Fast `analysis_incomplete` is counted only for compatibility/observability and is not an eligibility gate.
- `scripts/build_progressive_pass2_work.py` emits coactive `pass1_active=true` and current contract-driven `pass2_active=true`.
- `scripts/ingest_progressive_pass2.py` requires active Deep and recomputes exact current authorization immediately before persistence; it explicitly does not use Fast as a Deep prerequisite.
- `scripts/authorize_progressive_pass2_recovery.py` requires a current recovery-owned Deep identity, accepted compatible Dossier, and explicit recovery condition; it has no Fast prerequisite.
- `config/progressive_pass2_worker_prompt.md` explicitly forbids requiring Fast result/attempt/failure/global completion.
- `scripts/test_progressive_pass2.py` and `scripts/test_progressive_pass2_integration.py` cover Deep eligibility with empty Fast state, successful Fast state, active production state, recovery ownership, and no blind retry.

### Shared canonical-writer workflows
The inspected writers all use `taste-steam-review-dossier-canonical-writer` with `cancel-in-progress: false` where applicable and contain no additional Fast/Deep mutual-exclusion gate:
- `.github/workflows/ingest-progressive-pass1.yml` — compatible orchestration except F-01 inside the called ingest script.
- `.github/workflows/ingest-progressive-pass2.yml` — reconciles Dossier, recomputes Deep, requires active Deep, ingests current authorized work.
- `.github/workflows/authorize-progressive-pass2-recovery.yml` — explicit GitHub-owned recovery authorization, no Fast gate.
- `.github/workflows/build-pre-ai-store-snapshot.yml` — builds current PASS 1 work, then current Dossier truth, then recomputes current PASS 2 work; can produce both active manifests in one canonical preparation.
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml` — canonical Dossier persistence/recovery followed by Deep recomputation; no Fast prerequisite.
- `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py` verifies canonical Dossier visibility can unlock Deep with an empty Fast state.

### Pre-AI generation / recompute
- The current pre-AI workflow already produced both active manifests currently on `main`.
- `scripts/build_pre_ai_store_snapshot.py` did not expose a separate activation-state gate in the bounded audit; orchestration is owned by the workflow above.
- No old “Deep only after global Fast completion” predicate was found in the current recompute path.

### Visual / projection generation and validation
- `scripts/progressive_personalization.py` emits and validates `pass1_active=true` together with `pass2_active=true`, with separate Fast/Dossier/Deep counters and Deep-authoritative/Fast-provisional precedence.
- `scripts/progressive_visual_activation_routing.py` treats both active flags as the compatible current state and forces rebuild on incompatible/stale projection state.
- `scripts/test_progressive_visual_activation_routing.py` fixtures model both stages active and explicit Deep stage fields.
- The root Progressive contract remains `phase_b` while the Deep technical substage is `phase_c_pass2`; current producer, contracts and validators agree on that representation, so it is not classified as a stale schema blocker.

## AUD-02 evidence boundary

GitHub code-search indexing returned no matches even for known present strings such as `pass1_active` and the exact incident error. Therefore AUD-02 was bounded without treating an empty search index as proof of absence.

The consumer inventory was instead bounded from:
1. the current `PROJECT_ROUTES.md` Progressive route;
2. all minimum production paths explicitly required by this task;
3. current Progressive/Dossier workflow-directory inventory;
4. `.github/workflows/validate-progressive-pass2-core.yml` dependency/path inventory;
5. `scripts/test_progressive_pass2_integration.py` shared-writer inventory;
6. activation commit `36113dcd...` changed-file set and the pre-activation parent for migration comparison;
7. current PASS 1/PASS 2 worker prompts and generated work manifests.

Within that bounded production consumer set, F-01 is the only production stale mutual-exclusion/pre-Deep blocker found.

## Ordered implementation fix set — not applied

1. **PASS 1 ingest activation guard:** in `scripts/ingest_progressive_pass1.py`, align the fail-closed guard to the current canonical coactive state. The smallest current-contract repair is to require `pass1_active=true` and `pass2_active=true`, not to remove activation validation entirely.
2. **Focused regression:** add a test around the ingest activation check proving current `true/true` succeeds and invalid/stale combinations fail closed. Existing `test_progressive_pass1.py` semantic coverage is insufficient because it bypasses the entrypoint guard.
3. **Validation ownership:** extend `validate-progressive-pass2-core.yml` so the PASS 1 ingest script and the new guard regression are in the activation-validation surface.
4. **Canonical recovery/acceptance after the fix:** do not edit or recreate Friends vs Friends. Let the normal GitHub-owned PASS 1 ingest path consume the already-existing exact artifact, then verify Fast counts advance and the same shared writer reaches Deep recomputation/commit. This must be a separate implementation/acceptance action, not this audit.
5. **Documentation cleanup:** boundedly refresh `PROJECT_ROUTES.md` and annotate PPD-004/PPD-005 as historical pre-activation boundaries now superseded by the current production-active contracts. Do not rewrite their historical rationale.

Architecture preflight for this fix set:
- responsibility owner: GitHub control plane;
- authority: current Progressive personalization/PASS 1/PASS 2 and execution-ownership contracts;
- no control-plane responsibility moves to Scheduled ChatGPT or an interactive chat;
- no new scheduler, recurring stage, queue owner, retry loop, checkpoint policy, or backlog manager is introduced.

## Validation gates

- **AUD-01 PASS** — confirmed PASS 1 defect independently verified from current manifest, exact artifact, commit, failed workflow/job, and exact failure log.
- **AUD-02 PASS (bounded)** — current activation-flag consumers bounded through canonical route/dependency/workflow inventories and required production paths; GitHub code-search index limitation is explicitly recorded.
- **AUD-03 PASS** — production stale mutual-exclusion scan complete for the bounded current paths; only F-01 is a production blocker, with additional guardrail/documentation analogues F-02/F-03/DOC-01/DOC-02.
- **AUD-04 PASS** — every finding classified by reachability, impact, root-cause relation, and minimum fix scope.
- **AUD-05 PASS** — compatible inspected paths are explicitly listed as negative evidence.
- **AUD-06 PASS** — no production state/work/cache/inbox/contract/site mutation, workflow dispatch/rerun, semantic work, or Scheduled Task mutation was performed; the Friends vs Friends artifact was read only.
- **AUD-07 PASS** — bounded ordered implementation fix set defined but not applied.
- **AUD-08 PENDING AT REPORT WRITE** — satisfied only after this report is committed to `main` and reread exactly from `main`.

## Read-only mutation ledger

Allowed mutation planned/performed by this task: this report only.

Not performed:
- no change to `scripts/ingest_progressive_pass1.py`;
- no PASS 1/PASS 2/Dossier state, work, cache, inbox, contract, or visual mutation;
- no replay/delete/overwrite/rename of the Friends vs Friends result;
- no workflow dispatch, rerun, or production semantic execution;
- no Scheduled Task read/write was needed for this repository-only stale-guard audit;
- no change to the separate Dossier Scheduled Task self-disable diagnosis;
- no source/test/workflow/documentation fix outside this report.

