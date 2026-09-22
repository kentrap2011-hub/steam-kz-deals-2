# Progressive PASS 2 Phase C Core Implement 01

Task: `progressive-pass2-phase-c-core-implement-01`  
Status: `complete_core_ready_for_director_acceptance`  
Production activation: **OFF** (`pass2_active=false`)

## Architecture preflight

- Owner remains GitHub control plane under `config/execution_ownership_contract.json`.
- Canonical Progressive design already assigned PASS 2 eligibility, ordering, state, attempt accounting and UI projection to GitHub.
- This implementation does not transfer control-plane decisions to Scheduled ChatGPT or interactive chat.
- No second scheduler, quota, global completion gate, automatic retry loop, or Dossier-owned state machine was introduced.
- Dossier-owned contracts, prompts, ingest/recovery scripts and workflows were not modified.
- Scheduled Task creation/edit/enable/run was not performed.

## Implemented surfaces

Core:
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_result_schema.json`
- `config/progressive_pass2_execution_receipt_schema.json`
- `config/progressive_pass2_worker_prompt.md`
- `scripts/progressive_pass2.py`
- `scripts/build_progressive_pass2_work.py`
- `scripts/ingest_progressive_pass2.py`
- `data/cache/progressive_pass2_state.json`
- `data/production/pre_ai/progressive_pass2_work.json`

Integration/provenance:
- `config/progressive_personalization_contract.json`
- `config/execution_ownership_contract.json`
- `scripts/progressive_personalization.py`
- `scripts/build_final_visual_payload.py`
- `scripts/progressive_visual_activation_routing.py`
- `.github/workflows/ingest-progressive-pass2.yml`
- `.github/workflows/build-daily-visual-payload.yml`
- `web/progressive-personalization-ui.js`

Validation:
- `scripts/test_progressive_pass2.py`
- `scripts/test_progressive_visual_activation_routing.py`
- `web/progressive-personalization-ui.test.js`
- `.github/workflows/validate-progressive-pass2-core.yml`

## State / work / result / receipt model

- PASS 2 durable budget key is exactly current `semantic_generation_id + work_id`.
- Eligibility requires a current exact PASS 1 `analysis_incomplete` entry plus a canonical accepted Dossier from `data/cache/taste_steam_review_dossiers/App_<appid>.json`.
- Dossier unlock is fail-closed on appid, work title, release year when exposed, resolved identity, exact current compatibility binding and freshness.
- Buffered/unaccepted Dossier artifacts never count as accepted truth.
- Prepared work binds the PASS 1 identity plus exact Dossier content SHA-256, full compatibility binding and deterministic `authorization_id`.
- Work projection and Dossier waiting consume zero attempts.
- A budget is consumed only by:
  1. an exact-bound accepted `PROGRESSIVE-PASS2-RESULT-V1`; or
  2. a GitHub-canonicalized terminal execution receipt derived from an exact-bound authorized execution submission.
- Invalid/stale result or receipt artifacts do not consume an attempt.
- A consumed budget never resets because the Dossier changes while generation/work remains the same.
- A genuinely new generation/work identity creates a new budget.
- Items are independent; invalid/failed siblings do not roll back accepted siblings.
- PASS 1 state/history is read-only to PASS 2.

## State projection and UI provenance

- PASS 2 `analyzed_fit` -> current `analyzed_fit`.
- PASS 2 completed negative -> current `analyzed_not_fit` and remains excluded by the existing publication rule.
- PASS 2 unresolved/terminal failure -> current `analysis_incomplete`, with no second automatic retry for the same budget.
- Producer stamps `analysis_resolution_pass: "pass2"`; browser code does not infer PASS 2 from history/source.
- User labels:
  - PASS 1 fit unchanged: `Разобрана · подходит вам`
  - PASS 2 fit: `Разобрана · PASS 2`
  - PASS 2 unresolved: `Разбор не завершён · PASS 2`
  - untouched: `Ещё не разобрана`
- Visual provenance now binds the PASS 2 state blob, so an accepted PASS 2 state change routes through the existing full Progressive visual rebuild path.

## Validation matrix

- P2CORE-01 — **PASS**: incomplete without canonical accepted Dossier waits; zero attempts.
- P2CORE-02 — **PASS**: exact accepted fresh compatible Dossier creates exactly-bound eligible work.
- P2CORE-03 — **PASS**: stale/wrong-app/wrong-work/wrong-release/ambiguous/compatibility-mismatch fail closed; zero attempts.
- P2CORE-04 — **PASS**: work/result identity binds generation/work/appid/Dossier SHA/full binding/authorization.
- P2CORE-05 — **PASS**: work projection alone leaves PASS 2 state unchanged.
- P2CORE-06 — **PASS**: exact accepted result consumes one attempt; replay is ignored.
- P2CORE-07 — **PASS**: only exact valid terminal execution receipt consumes the unresolved terminal attempt.
- P2CORE-08 — **PASS**: same generation/work cannot auto-retry after an attempt even with a new Dossier.
- P2CORE-09 — **PASS**: changed generation/work creates a new budget and old state is non-current.
- P2CORE-10 — **PASS**: invalid item does not block a valid sibling.
- P2CORE-11 — **PASS**: PASS 2 eligibility is independent from unrelated PASS 1 not-analyzed work; no global PASS 1 completion gate.
- P2CORE-12 — **PASS**: PASS 1 history remains unchanged while PASS 2 becomes the current projection.
- P2CORE-13 — **PASS**: explicit machine provenance reaches the card label; browser inference is regression-tested away.
- P2CORE-14 — **PASS**: contract/work remain inactive, initialized PASS 2 durable state is empty, no production PASS 2 result or attempt was created.
- P2CORE-15 — **PASS**: branch diff contains no Dossier-owned contract/prompt/ingest/recovery/workflow modification.
- P2CORE-16 — **PASS**: implementation/report were committed to `main` in squash commit `670e2cfb6991d955a9503637d72345a523ebca7a`; the durable report was then reread from `main` before this closeout update.

Focused CI:
- tested branch head: `116f5a2e8350398fc3bab5e8442fbd0f2978d74d`
- workflow: `Validate Progressive PASS 2 core`
- run: `35710488760`
- conclusion: `success`
- checks include Python compilation, PASS 2 core, PASS 1 regression, personalization, unresolved-row preservation, visual routing, UI provenance, and inactive production eligibility dry-run.
- production-shape dry-run recomputed eligibility with `pass2_active=false`, preserved an empty PASS 2 durable state and performed no execution.

## Deferred dependency

Automatic eligibility recomputation after canonical Dossier persistence is intentionally not wired here. The reusable Progressive-owned entrypoint is `scripts/progressive_pass2.py::recompute_eligibility` / `scripts/build_progressive_pass2_work.py`; future wiring must call it after canonical Dossier persistence without changing Dossier evidence, recovery or persistence semantics.

## References

- accepted design: `config/progressive_personalization_contract.json#phase_c_pass2_design`
- accepted amendment report: `reviews/worker_reports/progressive-pass2-dossier-ready-gate-amendment-01.md`
- PASS 2 contract: `config/progressive_pass2_contract.json`
- tested branch head before merge: `116f5a2e8350398fc3bab5e8442fbd0f2978d74d`
- implementation squash on `main`: `670e2cfb6991d955a9503637d72345a523ebca7a`

## Next step

Create one separate director-reviewed activation task that wires canonical Dossier persistence to the existing PASS 2 recomputation entrypoint, validates that boundary, and only then decides production activation.
