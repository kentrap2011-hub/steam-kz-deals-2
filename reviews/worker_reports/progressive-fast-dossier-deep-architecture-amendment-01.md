# Progressive Fast / Dossier / Deep Architecture Amendment 01

Task: `progressive-fast-dossier-deep-architecture-amendment-01`  
Status: `complete_architecture_amendment`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Base/source of truth: `main`  
Deep/PASS 2 production semantic execution: **OFF**

## Old model -> new model

Old pre-activation model:
- PASS 1 was the normal lightweight path.
- PASS 2 was a one-shot recovery path only for current exact PASS 1 `analysis_incomplete`.
- one consumed unresolved PASS 2 attempt permanently removed that generation/work identity from automatic PASS 2 eligibility.

Canonical replacement:
1. **Быстрый разбор / Fast / PASS 1** — provisional early personalized analysis.
2. **Подготовка досье / Dossier** — independent neutral evidence preparation; it never decides fit/not-fit.
3. **Глубокий разбор / Deep / technical PASS 2** — eventual authoritative personalized analysis for every current eligible game.

Deep no longer requires any prior Fast attempt or Fast `analysis_incomplete`. Exact-compatible canonically accepted current Dossier evidence is the evidence gate. Deep may run before Fast; authoritative Deep completion suppresses future Fast work for the same current identity, while Fast completion never suppresses eventual Deep coverage.

The old recovery-only activation plan is superseded. Existing GitHub-owned recomputation hooks, exact binding, liveness, serialized writer protection and zero-attempt projection behavior are preserved as reusable inactive scaffolding and must be adapted before any Deep activation.

## Effective-result precedence

For the current Progressive staged result:
1. trustworthy current completed Deep `analyzed_fit` / `analyzed_not_fit` => authoritative effective personalized truth;
2. otherwise trustworthy current completed Fast fit/not-fit may remain provisional effective truth;
3. otherwise use the existing unresolved/not-analyzed projection.

Deep incomplete/error does not erase a still-valid Fast provisional fit/not-fit result. Fast/Deep histories remain separate; Deep never rewrites Fast provenance. Existing separately canonical reusable Taste-cache compatibility rules are unchanged by this architecture-only amendment and must not be presented as Fast/Deep stage completion without exact stage provenance.

## Normal Deep first pass vs recovery

- every current eligible Deep identity gets exactly one **normal first-pass** attempt once an exact-compatible accepted Dossier is ready;
- successful Deep fit/not-fit is authoritative completion for that current identity;
- unresolved/technical first-pass failure does **not** count as authoritative completion;
- that exact identity moves into separate GitHub-owned non-blocking recovery state and does not block unrelated normal first-pass work;
- no blind automatic retry loop and no hidden arbitrary recovery quota exist;
- every recovery attempt requires a fresh GitHub-owned authorization tied to a concrete condition:
  - materially changed canonically accepted Dossier/evidence; or
  - corrected runtime/validation defect material to the prior failure; or
  - explicit canonical GitHub recovery action with recorded reason;
- recovery attempts/history are accounted separately from the one normal first-pass attempt;
- if recovery is unresolved, the identity returns to recovery-owned state and needs a new concrete recovery authorization before another attempt.

`deep_normal_first_pass_complete` and `deep_all_current_authoritative_complete` are explicitly distinct metrics.

## UI stage-state contract

GitHub must emit producer-owned per-game fields; browser inference from arbitrary history/files/timestamps is forbidden.

- Fast: `not_started | completed | incomplete | error`, with completed outcome `fit | not_fit`.
- Dossier: `not_ready | accepted | failed_or_recovery`.
- Deep: `not_started | waiting_for_dossier | eligible_or_pending | completed | incomplete_or_recovery`, with completed outcome `fit | not_fit`.
- Deep recovery detail: `none | recovery_owned | recovery_eligible | recovery_pending`.
- Effective source: `deep | fast | none`.

Russian labels are canonicalized as `Быстрый разбор`, `Подготовка досье`, `Глубокий разбор`. This is sufficient for the future three small pixel-style card indicators; final visual design is intentionally not implemented here.

## Statistics-page metric contract

The future compact `Статистика` control leads to a dedicated three-section page. Every section uses its own named denominator; scopes are never merged when they differ.

**Быстрый разбор**
- `fast_total_current_scope`
- `fast_attempted_count`
- `fast_completed_fit_count`
- `fast_completed_not_fit_count`
- `fast_incomplete_count`
- `fast_error_count`
- `fast_skipped_due_to_authoritative_deep_count`
- `fast_remaining_count`

**Подготовка досье**
- `dossier_total_current_scope`
- `dossier_accepted_count`
- `dossier_pending_count`
- `dossier_failed_or_recovery_count`
- `dossier_normal_first_pass_complete`
- `dossier_all_accepted_or_recovered_complete`

**Глубокий разбор**
- `deep_total_current_coverage_target`
- `deep_first_pass_attempted_count`
- `deep_authoritative_completed_count`
- `deep_completed_fit_count`
- `deep_completed_not_fit_count`
- `deep_incomplete_or_recovery_count`
- `deep_waiting_for_dossier_count`
- `deep_ready_or_pending_count`
- `deep_normal_first_pass_remaining_count`
- `deep_remaining_until_all_authoritative_count`
- `deep_normal_first_pass_complete`
- `deep_all_current_authoritative_complete`

## Canonical files changed

Architecture contracts:
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/execution_ownership_contract.json`

Compact durable rationale/navigation:
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`

Operational handoff only:
- `CURRENT_TASK.md`

No Dossier evidence contract, site ranking weight, Deep runtime script, schema executor, workflow execution path, Scheduled Task or production Deep state was changed.

## Validation ARCH-01..16

- **ARCH-01 PASS:** Deep eligibility explicitly requires neither prior Fast attempt nor Fast `analysis_incomplete`.
- **ARCH-02 PASS:** Deep target is `all_current_eligible_games`.
- **ARCH-03 PASS:** Fast is explicitly provisional, lightweight and independent.
- **ARCH-04 PASS:** authoritative completed Deep suppresses future Fast for the same current identity.
- **ARCH-05 PASS:** Fast fit/not-fit success never suppresses eventual Deep.
- **ARCH-06 PASS:** completed Deep fit/not-fit is authoritative effective result over Fast.
- **ARCH-07 PASS:** Deep incomplete/error preserves a still-valid Fast provisional result.
- **ARCH-08 PASS:** Dossier remains independent neutral evidence preparation and never decides fit/not-fit.
- **ARCH-09 PASS:** unresolved normal Deep first pass enters separate non-blocking GitHub recovery state instead of permanent completion.
- **ARCH-10 PASS:** recovery forbids blind retry and hidden arbitrary quota; every recovery attempt requires fresh concrete GitHub authorization.
- **ARCH-11 PASS:** normal Deep first-pass completeness and eventual all-current authoritative completeness are separate metrics.
- **ARCH-12 PASS:** explicit producer-owned Fast/Dossier/Deep per-item states are defined for UI.
- **ARCH-13 PASS:** dedicated statistics fields/denominators are canonicalized separately for Fast, Dossier and Deep.
- **ARCH-14 PASS:** prior GitHub recomputation/exact-binding/liveness/zero-attempt wiring is preserved as reusable inactive scaffolding; the old recovery-only predicate/activation plan is marked superseded.
- **ARCH-15 PASS:** Deep remains inactive. Fresh-main validation: `progressive_pass2_contract.active=false`, Progressive `pass2_active=false`, ownership `pass2_active=false`, daily mirrors `false`, durable PASS 2 state entries `0`. The existing work manifest still has 4 inactive projection items and no production execution was performed by this task.
- **ARCH-16 PASS GATE:** this exact durable report is committed to `main` and must be reread from `main` after commit before the worker sends the final response.

## Exact refs

Prior reusable landed work:
- PASS 2 core implementation: `670e2cfb6991d955a9503637d72345a523ebca7a`
- Dossier integration/recomputation wiring: `1f7c09b8681a48842d928f7bdb5ff9da79165728`

Architecture amendment commits before report:
- `a432b20f4ea6fbadeba072fa721343f5855386df` — Progressive three-stage model / precedence / UI + statistics contract
- `cd1a51311faec176689486af2b4439cc50fcffa4` — PASS 1 recast as provisional Fast
- `17d58b32b895d50708a5f29df48e5ad85b28d731` — PASS 2 recast as eventual Deep + first-pass/recovery architecture
- `6de86c869363d3372598384802f97d6483e56001` — GitHub ownership amendment
- `cdee512ab1bc48a9fd73101568f462a452151a90` — durable decision supersession / PPD-004
- `9d0f062aeef4d2076b5a161b33bc26bc1f48ba40` — updated project route

Fresh-main canonical blobs at validation:
- Progressive personalization: `7513455305b43fd6e9855bb609880d57e8d9581a`
- PASS 1: `46b50d894df7268e56ac25b0bb7249a0adb48806`
- PASS 2: `5df196873d395121f2ecf84e8fd5a7a0564234eb`
- execution ownership: `b1d12388cb93b9de8b8a28dda5455a7c411dcde5`
- PASS 2 state: `6e8e3cb2fc5f0d04958ad3753ed1b13fdb50b99c`
- inactive PASS 2 work projection: `685bc5e83a9c81797367950fa03934ab7ec571ae`

A concurrent unrelated `main` commit was observed during this task; an outdated write was rejected with HTTP 409 and was reapplied only after rereading fresh `main`. No force update or overwrite was used.

## Final status

`complete_architecture_amendment`

## Recommended next step

Create exactly one bounded **runtime-adaptation** task that changes the inactive Deep/PASS 2 eligibility/state/projection/tests from the superseded Fast-incomplete-only predicate to `FAST-DOSSIER-DEEP-V1`, including explicit first-pass/recovery accounting and producer-owned stage/statistics fields, while keeping Deep inactive throughout that task.
