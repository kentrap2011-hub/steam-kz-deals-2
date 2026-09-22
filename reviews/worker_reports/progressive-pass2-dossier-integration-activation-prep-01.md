# Progressive PASS 2 Dossier Integration + Activation Prep 01

Task: `progressive-pass2-dossier-integration-activation-prep-01`  
Status: `complete_ready_for_activation`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Base/source of truth: `main`  
Production PASS 2 semantic execution: **OFF**

## Architecture preflight

- GitHub remains the sole PASS 2 control-plane owner for eligibility, order, exact binding, attempt accounting, persistence and visual projection.
- The implementation reuses only the existing Progressive-owned `scripts/progressive_pass2.py::recompute_eligibility` through `scripts/build_progressive_pass2_work.py`; no second eligibility predicate exists.
- Scheduled ChatGPT remains a future bounded semantic data plane only. Interactive chat has no production execution role.
- No new queue owner, daemon, retry loop, polling expiry scheduler, recurring producer or second state authority was introduced.
- The minimum complete input-change set is: canonical Dossier persistence, PASS 1 durable state persistence, daily/current generation-binding-freshness rebuild, plus PASS 2 attempt persistence so consumed work cannot race later projections.

## Exact recomputation trigger graph

| Canonical event | GitHub boundary | Action |
| --- | --- | --- |
| accepted/recovered Dossier persistence | `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml` | run `python scripts/build_progressive_pass2_work.py` after canonical Dossier ingest/validation |
| PASS 1 durable transition, including to/from current `analysis_incomplete` | `.github/workflows/ingest-progressive-pass1.yml` | run the same builder after PASS 1 ingest |
| current semantic generation/work identity, Dossier compatibility/freshness preparation | `.github/workflows/build-pre-ai-store-snapshot.yml` | run the same builder after current PASS 1/Dossier preparation |
| future PASS 2 attempt persistence | `.github/workflows/ingest-progressive-pass2.yml` + `scripts/ingest_progressive_pass2.py` | recompute current authorization before accepting artifacts, persist attempt, then rebuild work |

All four GitHub writers use the existing `taste-steam-review-dossier-canonical-writer` concurrency group with `cancel-in-progress:false`. This prevents a later rebased writer from replacing PASS 2 work with a projection derived from older canonical inputs.

Wall-clock Dossier expiry does not require polling. Prepared work carries exact `dossier_expires_at_utc`; the future worker must check exact compatibility binding + exact expiry immediately before semantic execution, and GitHub recomputes full current authorization, including canonical Dossier SHA/freshness/binding and PASS 1 identity, again before accepting any PASS 2 result/terminal receipt.

## Exact files changed

Implementation/contract/control-plane paths:
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/ingest-progressive-pass1.yml`
- `.github/workflows/ingest-progressive-pass2.yml`
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `.github/workflows/validate-progressive-pass2-core.yml`
- `CURRENT_TASK.md`
- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`
- `config/execution_ownership_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/progressive_personalization_contract.json`
- `scripts/ingest_progressive_pass2.py`
- `scripts/progressive_pass2.py`
- `scripts/test_progressive_pass2.py`
- `scripts/test_progressive_pass2_integration.py`

Durable completion path:
- `reviews/worker_reports/progressive-pass2-dossier-integration-activation-prep-01.md`

## Validation — P2INT-01..13

- **P2INT-01 PASS:** focused integration regression proves a canonical exact-compatible accepted Dossier plus matching current PASS 1 incomplete state creates eligible work without manual queue construction.
- **P2INT-02 PASS:** buffered/unaccepted transport has zero authority; a missing canonical Dossier loader result remains `no_canonically_accepted_dossier`.
- **P2INT-03 PASS:** PASS 1 ingest itself invokes the common PASS 2 builder, so later transition to current `analysis_incomplete` with an already accepted Dossier does not wait for another Dossier event.
- **P2INT-04 PASS:** leaving `analysis_incomplete` or changing current generation/work identity removes stale authorization.
- **P2INT-05 PASS:** expiry or compatibility mismatch removes eligibility; future worker liveness checks exact expiry/binding before execution and GitHub reauthorizes from current truth before ingest.
- **P2INT-06 PASS:** recomputation is idempotent and does not mutate `progressive_pass2_state`; projection consumes zero attempts.
- **P2INT-07 PASS:** mixed regression proves one expired/stale sibling does not block another valid sibling.
- **P2INT-08 PASS:** PASS 1 semantic policy/attempt history and Dossier evidence/identity/freshness/recovery semantics are unchanged.
- **P2INT-09 PASS:** acceptance observation on current snapshot preserves g000001/g000002 as `failed_or_invalid_pending_recovery` and g000003/g000004 as `accepted`; current forward progress also has g000005/g000006 accepted. Failed groups were not used as PASS 2 truth.
- **P2INT-10 PASS:** PASS 2 remains inactive; current PASS 2 durable state has zero entries/attempts; no production PASS 2 result or terminal receipt was created.
- **P2INT-11 PASS:** the exact future single-task operator configuration and activation ordering are fixed below; no runtime scheduler choice is left to the operator.
- **P2INT-12 PASS:** PR validation succeeded: `Validate Progressive PASS 2 Phase C core` run `35764806818`, `Validate Taste Steam Review Dossier` run `35764806854`, and `Validate backlog mode` run `35764806771`. PASS 2 run logged `items=4 active=False` and `PROGRESSIVE_PASS2_INACTIVE_PROJECTION=PASS eligible=4`.
- **P2INT-13 PROCEDURAL PASS GATE:** this exact report must be committed to `main` and then reread from `main` before the worker sends its final response. The closing read is the evidence for this non-self-referential gate.

## Current inactive production projection

Acceptance observation from current `main` after automatic GitHub recomputation:

- PASS 2 work blob: `685bc5e83a9c81797367950fa03934ab7ec571ae`
- `pass2_active=false`
- current `analysis_incomplete=60`
- Dossier waiting `56`
- PASS 2 eligible `4`
- PASS 2 attempted `0`
- durable PASS 2 state entries `0`
- current eligible appids: `1102190`, `113020`, `1093290`, `1018800`
- Dossier group progress at observation: accepted/failed/pending `4/2/178`

This is projection-only state. Live PASS 1/Dossier production may legitimately change the eligible identities/count after this evidence point; any later execution must use only the then-current GitHub manifest.

Inactive proof remains canonical:
- `config/progressive_pass2_contract.json#active=false`
- `config/progressive_personalization_contract.json#phase_b_execution.pass2_active=false`
- `config/progressive_personalization_contract.json#phase_c_pass2_design.active=false`
- `config/execution_ownership_contract.json#progressive_personalization_phase_c_pass2_core.pass2_active=false`
- `config/progressive_pass1_contract.json#pass2.active=false`
- no Scheduled Task with exact title `Progressive PASS 2 Worker` existed in the read-only scheduler inventory at acceptance time.

## Exact future Scheduled Task configuration

**Title:** `Progressive PASS 2 Worker`  
**Initial state:** disabled  
**Timing mode:** exact schedule  
**Cadence:** once per hour at minute 30  
**Operational timezone rule:** `Europe/Samara` (same canonical production timezone; the hourly rule is anchored to local `:30`)  
**Schedule:**
```text
BEGIN:VEVENT
RRULE:FREQ=HOURLY;BYMINUTE=30;BYSECOND=0
END:VEVENT
```

**Exact compact loader/prompt:**
```text
Operate only as the bounded Progressive PASS 2 semantic worker for repository kentrap2011-hub/steam-kz-deals-2, branch main. At the start of every invocation, first read the latest config/progressive_pass2_worker_prompt.md from main fully, then read and obey config/progressive_pass2_contract.json. If implemented != true or active != true, stop cleanly without creating any artifact. Use only the current GitHub-owned data/production/pre_ai/progressive_pass2_work.json and its exact order, work IDs, immutable bindings, dossier paths, result paths and terminal-receipt paths. Immediately before semantic execution of each item, apply the liveness checks required by the canonical worker prompt. Never choose, rebuild, reorder, expand, retry or reinterpret scope; never modify PASS 1, Dossier state, eligibility, ordering, accounting, visual state or scheduler settings. Create only the exact create-only PASS 2 result or terminal execution receipt authorized by the current manifest and canonical prompt. Stop cleanly when no current items remain or when runtime/tool budget no longer safely permits another item. GitHub remains the control plane for eligibility, order, validation, persistence, attempts, recomputation and visual projection.
```

### Duplicate-task guard

Before any future creation, read scheduler inventory and count tasks whose title is exactly `Progressive PASS 2 Worker`:
- count `0`: create exactly one task with the configuration above, initially disabled;
- count `1`: do not create another; verify its exact prompt/schedule/state and reuse only that task;
- count `>1`: fail closed; do not enable or run any copy until a separately authorized deduplication action leaves exactly one configured task.

Acceptance-time count was `0`, but activation must recheck rather than rely on this historical observation.

### Exact activation order

1. Apply the duplicate guard. Ensure exactly one correctly configured `Progressive PASS 2 Worker` exists **disabled**. Do not use `Run now`.
2. Make one repository activation change on a fresh branch from current `main`, preserving all existing semantics. In the same reviewed activation commit set:
   - `config/progressive_pass2_contract.json#active=true`; set its runtime status/activation-guard fields consistently to active/authorized;
   - `config/progressive_personalization_contract.json#phase_b_execution.pass2_active=true`;
   - `config/progressive_personalization_contract.json#phase_c_pass2_design.active=true` and its status/integration text consistently active;
   - `config/execution_ownership_contract.json#progressive_personalization_phase_c_pass2_core.pass2_active=true` and status consistently active;
   - `config/progressive_pass1_contract.json#pass2.active=true` as the metadata mirror;
   - `config/daily_execution_contract.json#progressive_personalization_phase_a.pass2_active=true` and `#progressive_personalization_phase_b_pass1.pass2_active=true` as execution-contract mirrors.
3. Merge that activation commit to `main`. Before touching the task, require the relevant GitHub validations to pass and verify from fresh `main` that every activation flag is true, `progressive_pass2_work.json#pass2_active=true`, its generation/bindings are current, and PASS 2 attempt state has not changed merely from activation/recompute.
4. Enable the single verified Scheduled Task. Do not create a second task.
5. Invoke **one** first `Run now` on that enabled task. Do not manually construct work and do not run interactive PASS 2.
6. After that run, inspect GitHub before any second manual run: require `Ingest Progressive PASS 2 item` success for any submitted artifact; verify each consumed attempt is attached only to the exact then-current generation/work/appid/Dossier SHA/binding/authorization; verify PASS 2 work is recomputed, sibling items remain independent, PASS 1/Dossier semantic state was not mutated by PASS 2, and any resolved visual item carries the existing explicit PASS 2 provenance. Also recheck scheduler cardinality is exactly one.

If activation produces zero eligible items, the first run is a valid clean no-op; do not fabricate work or retry outside GitHub control.

## Exact refs

- implementation PR: `#86`
- implementation squash on `main`: `1f7c09b8681a48842d928f7bdb5ff9da79165728`
- PASS 2 validation run: `35764806818`
- Dossier validation run: `35764806854`
- backlog validation run: `35764806771`
- acceptance PASS 2 work blob: `685bc5e83a9c81797367950fa03934ab7ec571ae`
- acceptance PASS 2 state blob: `6e8e3cb2fc5f0d04958ad3753ed1b13fdb50b99c`
- acceptance Dossier work blob: `c0ed7333617a1c7359450f7f9da645393e0e4f2e`
- durable report: `reviews/worker_reports/progressive-pass2-dossier-integration-activation-prep-01.md`

## Final status

`complete_ready_for_activation`

PASS 2 integration is complete and live as a GitHub-owned inactive projection; semantic production remains unauthorized and unexecuted.

## Recommended next step

Exactly one next step: run a separate director-reviewed **PASS 2 production activation** action using the activation order and exact single Scheduled Task configuration above; do not activate or run PASS 2 from this task.
