# Taste Dossier semantic bounded retrieval 01 — durable worker report

**Date:** 2026-09-23  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`  
**Branch / source of truth:** `main`  
**Task:** `WORKER_TASK_TASTE_DOSSIER_SEMANTIC_BOUNDED_RETRIEVAL_01.md`  
**Final status:** `complete_ready_for_director_acceptance`

## Executive result

The active Taste Steam Review Dossier worker no longer has a hard per-game numeric ceiling of 8 web-search queries or 16 opened/read source pages.

The replacement is **semantic/adaptive bounded stopping**, not another numeric quota:

- stop immediately when evidence is sufficient;
- otherwise continue only through mandatory or materially promising **distinct** retrieval routes;
- do not retry materially equivalent query/locale/endpoint/list/index variants merely because another variant exists;
- revisit a route only when a materially new factual lead changes what is being queried;
- fail closed when all reasonably discoverable mandatory materially distinct routes are exhausted and critical evidence remains insufficient;
- stop safely on a directly observed runtime/tool/transport blocker or current snapshot/plan/binding liveness change;
- ordinary invocation runtime remains the outer runtime boundary.

Search-query and opened-page counts remain observable diagnostics only. They are not semantic stop gates.

## START gate and architecture preflight

The task was started from the current `CHAT_PROTOCOL.md` and the required START material was read before implementation, including:

- `CHAT_CONTEXT.md`;
- `PROJECT_ROUTES.md`;
- `CURRENT_TASK.md`;
- `KNOWN_WORKER_PITFALLS.md`;
- `PROJECT_DECISIONS.md`;
- the task file itself;
- the active Dossier worker/runtime/schema/evidence/control-plane/persistence/ownership contracts;
- the required prior Dossier retrieval and fail-closed-ledger reports.

Architecture conclusion:

1. GitHub remains the control plane for scope, ordering, retry/recovery, validation, persistence and completeness.
2. Scheduled ChatGPT remains only the bounded semantic candidate-generation/create-only transport data plane.
3. The change belongs inside the existing worker/evidence stopping semantics; no architecture redesign or new recurring stage is required.
4. Existing anti-loop protection is preserved and strengthened semantically: equivalent-route repetition is forbidden, source diversification is by materially distinct surface class, exact-product identity remains fail-closed, and route exhaustion is explicit.
5. Worst-case execution is bounded by semantic route exhaustion plus ordinary invocation runtime/tool/liveness boundaries, not by an arbitrary query/page ordinal.
6. No new scheduler, queue, retry daemon, checkpoint authority or persistence owner was added.

## Before / after

### Before

The active machine evidence contract contained:

- `max_web_search_queries: 8`;
- `max_opened_or_read_source_pages: 16`;
- `bounded_limit_reached` as an accepted stop reason;
- Russian/retrieval wording that could terminate on a hard numeric bound;
- ledger semantics where a query/page budget could be named as the reason a required next route was not executed.

The worker prompt also explicitly described the 8-search / 16-page ceilings.

### After

The active machine evidence contract now exposes:

- `max_web_search_queries: null`;
- `max_opened_or_read_source_pages: null`;
- `numeric_limits_active: false`;
- `counts_are_semantic_stop_gates: false`;
- `outer_runtime_boundary: "ordinary_invocation_runtime"`;
- semantic stop reasons:
  - `evidence_stable`;
  - `required_materially_distinct_routes_exhausted`;
  - `runtime_tool_or_liveness_blocker`.

The contract also explicitly records:

- numeric query/page count is not a stop gate;
- materially equivalent route retry is forbidden;
- route revisit requires a materially new factual lead;
- discovery chooses the most promising materially distinct public player-feedback surface rather than enumerating arbitrary sites.

The worker prompt now states that boundedness is semantic/adaptive rather than a fixed per-game search/page count.

## Fail-closed ledger migration

The existing fail-closed execution ledger was preserved. No new durable logging/persistence surface was created.

For evidence/retrieval stops:

- `search_queries_used` remains an actual diagnostic counter;
- `opened_pages_used` remains an actual diagnostic counter;
- `search_query_limit:null` explicitly states that no finite numeric search-query limit exists;
- `opened_page_limit:null` explicitly states that no finite numeric opened-page limit exists;
- the counters may not by themselves justify `stop_gate`, route exhaustion, non-execution, or `why_not_executed`;
- `search budget exhausted` and `page/open budget exhausted` were removed as count-derived reasons;
- required route state remains explicit for Russian, source-diversification, temporal and identity routes;
- a pending mandatory materially distinct route must execute while it is reasonably discoverable, the binding remains live, and no directly observed blocker prevents it.

This preserves observability without reintroducing a hidden numeric stop rule.

## Evidence semantics intentionally unchanged

The task did **not** weaken or redefine:

- exact-product title/year/appid binding;
- wrong base-game/DLC/edition/sequel/remake/remaster rejection;
- Russian-attempt requirement and existence/retrieval gate;
- early multi-source/source-agnostic diversification;
- temporal pre-stop current-state verification;
- stable-locator and transient-author fallback privacy rules;
- author-independent dossier-local internal IDs;
- language binding and evidence-language projection;
- recurrence/evidence-strength derivation;
- strict prepublication/buffered validation;
- create-only transport;
- group size and per-group nonblocking progress;
- GitHub-owned failed-group recovery/completeness;
- Scheduled Task ownership boundaries.

`PROJECT_DECISIONS.md` now contains **TASTE-014**, which supersedes only the numeric 8/16-bound portions of TASTE-008, TASTE-010, TASTE-012 and earlier implementation reports. Their remaining evidence/identity/privacy/temporal rationale remains historical and active where not superseded.

## Exact implementation files changed

The implementation merged through PR **#94** and changed these source/control/regression files:

1. `config/taste_steam_review_dossier_worker_prompt.md`
2. `config/taste_steam_review_dossier_web_evidence_contract.json`
3. `scripts/test_taste_dossier_semantic_bounded_retrieval.py` — new focused SEMBOUND regression
4. `scripts/test_taste_steam_review_dossier_semantic_consistency.py`
5. `scripts/test_taste_steam_review_dossier_strict_recovery.py`
6. `scripts/test_taste_steam_review_dossier_contract_gaps.py`
7. `scripts/test_taste_dossier_contract_contradictions_fix.py`
8. `scripts/test_taste_dossier_identity_provenance_generation_fix.py`
9. `.github/workflows/validate-taste-dossier-buffered.yml`
10. `PROJECT_DECISIONS.md`

The task did not change the Dossier schema, Dossier control-plane ownership contract, persistence bridge, runtime traversal prompt or Scheduled Task regulation because no structural schema/ownership/scheduling change was required.

Operational handoff status was separately updated in `CURRENT_TASK.md`.

## PR and activation

Implementation PR:

- PR: **#94**
- merged to `main`
- squash merge commit: `915e9eec9795215df02a6c214f4b65dabddffa14`

Normal main-owned deterministic activation then ran automatically:

- workflow: **Build pre-AI deterministic payload**
- run: **#185**
- run id: `35896659610`
- result: **success**
- generated projection commit: `cf3215f35d0d883701ab116eb530734dd3072533`

Post-activation canonical projection was read from fresh `main` and confirmed:

- work/index evidence contract revision: `semantic-bounded-retrieval-2026-09-23`;
- work/index worker prompt revision: `web-evidence-v2-semantic-bounded-retrieval-v1`;
- work/index bindings are equal;
- current snapshot after deterministic rebuild: `dd4c807895c244011f1a1898661ed258299c6c523777137158181210583de91c`;
- the active projection therefore no longer carries the old numeric-bound semantic binding.

Additional main push checks after merge:

- **Validate execution ownership** run #197: success;
- **Validate backlog dispositions** run #1092: success.

## Validation

PR validation run used:

- workflow: **Validate buffered Steam review dossier runtime**
- run: **#148**
- run id: `35896487993`

All task-relevant Dossier steps were **success**:

- compile focused Dossier runtime/regressions;
- execution ownership validation;
- daily snapshot regression;
- buffered submission regression;
- same-day preservation regression;
- strict recovery regression;
- prepublication parity regression;
- contract-gap regression;
- language binding regression;
- semantic consistency regression;
- **semantic bounded retrieval regression**;
- transient author fallback regression;
- Steam Store review-card parent regression;
- contract contradiction closeout regression;
- identity provenance generation regression;
- validator-generator parity regression;
- package identity regression;
- story DLC semantic scope regression;
- parallel candidate validation and nonblocking per-group regression.

### Unrelated baseline workflow failure

The overall PR workflow conclusion was red only because its final **Canonical-writer coalescing liveness regression** checks a Progressive PASS 1 workflow staging invariant unrelated to this Dossier retrieval task.

The failure was:

- expected literal staged path `data/cache/taste_steam_review_dossiers`;
- current base-main `.github/workflows/ingest-progressive-pass1.yml` delegates staging to `scripts/stage_progressive_pass1_canonical_writer.sh` and does not contain that literal path;
- the same source/test mismatch already existed in PR base `e5ac4bfc0e9c61c763c25fa56dd81ec1fbf2fce1`;
- this task did not modify Progressive PASS 1 staging, Fast/Deep behavior, or that canonical-writer test.

Therefore no task-relevant Dossier regression became red or was weakened by this change. The unrelated Progressive PASS 1 baseline defect was intentionally not repaired outside scope.

## SEMBOUND acceptance matrix

| Gate | Status | Evidence |
|---|---|---|
| SEMBOUND-01 | PASS | Active worker/evidence contract has no hard 8-query ceiling; `max_web_search_queries=null`; focused regression guards removal. |
| SEMBOUND-02 | PASS | Active worker/evidence contract has no hard 16-page ceiling; `max_opened_or_read_source_pages=null`; focused regression guards removal. |
| SEMBOUND-03 | PASS | Focused regression evaluates search ordinals 9 and 11 and confirms count-only stopping is false. |
| SEMBOUND-04 | PASS | Focused regression evaluates opened-page ordinal 17 and confirms count-only stopping is false. |
| SEMBOUND-05 | PASS | `evidence_stable` remains valid and prompt explicitly stops immediately when evidence is sufficient. |
| SEMBOUND-06 | PASS | Materially equivalent route retries are forbidden; revisit requires a materially new factual lead. |
| SEMBOUND-07 | PASS | A still-pending mandatory materially distinct route must execute while discoverable/live/safe; premature unresolved is forbidden. |
| SEMBOUND-08 | PASS | Exhausted required materially distinct routes + critical insufficiency remains fail-closed/no publication. |
| SEMBOUND-09 | PASS | Ledger uses actual counters with null limits; counts cannot justify stop/exhaustion/non-execution; count-derived “budget exhausted” reasons removed. |
| SEMBOUND-10 | PASS | Ownership regression confirms GitHub control plane, create-only semantic worker role, and no new scheduler/queue/retry/checkpoint/persistence owner. |
| SEMBOUND-11 | PASS | All task-relevant existing Dossier regressions listed above passed; post-merge deterministic activation and ownership validation succeeded. |

## Scheduled Task / Production Dossier confirmation

This task did **not**:

- create a Scheduled Task;
- edit, enable, disable, pause, delete or reschedule a Scheduled Task;
- run the Taste Dossier Scheduled Task;
- run Production Dossier semantic research;
- create a second recurring stage;
- create a new retry loop/queue/scheduler;
- publish or repair any semantic Dossier candidate.

The only post-merge production-side activity was the repository's normal **deterministic GitHub-owned pre-AI projection rebuild**, which refreshed the content-complete worker binding. It did not execute ChatGPT semantic Dossier research.

## Final state

**`complete_ready_for_director_acceptance`**

The hard 8-search / 16-page per-game stopping ceilings are removed from the active Dossier semantics and are not replaced by another arbitrary number. Boundedness is now semantic/adaptive, while exact-product, Russian, temporal, privacy/provenance, fail-closed, create-only transport and GitHub ownership constraints remain intact.
