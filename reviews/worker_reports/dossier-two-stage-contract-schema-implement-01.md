# ЧАТ 2 — Dossier two-stage contract/schema P1 (inactive)

**Task:** `WORKER_TASK_DOSSIER_TWO_STAGE_CONTRACT_SCHEMA_IMPLEMENT_01.md`  
**Repository:** `kentrap2011-hub/steam-kz-deals-2` · **base:** `main` · **branch:** `feat/dossier-two-stage-contract-schema-01`  
**Accepted design:** PR #171; `reviews/worker_reports/dossier-two-stage-research-assembly-architecture-01.md`  
**Mode:** IMPLEMENT / CONTRACTS / SCHEMAS / INACTIVE. **New semantic workers are not implemented.**

## 1. Exact files

**New only:**
- `config/dossier_research_package_v1.schema.json`
- `config/dossier_research_acceptance_receipt_v1.schema.json`
- `config/dossier_assembly_assignment_v1.schema.json`
- `config/dossier_assembly_result_v1.schema.json`
- `config/dossier_assembly_receipt_v1.schema.json`
- `config/dossier_two_stage_interfaces_contract.json`
- `scripts/dossier_two_stage_contract_guard.py` — offline contract fixture guard only; **not** active ingest, staging or retry logic.
- `scripts/test_dossier_two_stage_contract_schemas.py` — 15 deterministic fixture scenarios (plus status iteration and negative subtests).
- `.github/workflows/validate-dossier-two-stage-contract-interfaces.yml` — **PR-only**, read-only validation job; no schedule/dispatch/production write.
- `reviews/worker_reports/dossier-two-stage-contract-schema-implement-01.md`

**No current Dossier/Deep/Steam/ranking/UI/translation/workflow producer/worker files were edited.** The existing one-stage validator, prompt, ingestion code and transport remain unchanged.

## 2. Research V1

Strict Draft 2020-12 JSON Schema `DOSSIER-RESEARCH-PACKAGE-V1`, schema_version 1. One game per frozen assignment. All objects reject unknown keys. Immutable assignment includes marker anchor/nonce, exact group/snapshot/item hashes, AppID, title, source queue, original worker/evidence V2 binding, and Research contract hash. Identity contains explicitly nullable **original work release year**, exact-product corroborators and referenced identity sources; storefront release year is never substituted.

Research records safe HTTPS/public_ref locators, optional normalized physical source identity, source type/role, player-feedback surface/acquisition, factual date/null, language, product binding, parent-child joins, locally unique source/feedback/finding refs and observed feedback `observed=true`. Finding supports must resolve to actual observed player feedback, not to unrelated aggregate source metadata. Neutral paraphrase only; source duplicates cannot inflate independent support. Exactly 12 canonical dimension audit entries, route state, Russian-state observations, strength/weakness investigation, unresolved material gaps and explicit completion status. Unknown facts remain null/unknown; **no JSON Schema default can manufacture evidence**.

The package has a canonical serialization algorithm marker; the actual accepted SHA-256 of the *validated entire package* is issued in the separate GitHub-owned acceptance receipt, never trusted from an unverified worker claim. Package acceptance means only structural/safe evidence, not Dossier or Deep acceptance.

## 3. Assembly V1

`DOSSIER-ASSEMBLY-ASSIGNMENT-V1` contains the exact original frozen Research assignment plus an accepted GitHub-only Stage-A receipt, accepted package hash, accepted receipt Git blob binding, separate Stage-B marker, contract/prompt digest, canonical target V2 binding and an exact predeclared create-only output path.

`DOSSIER-ASSEMBLY-RESULT-V1`: exactly one typed outcome, either a provisional V2 dossier candidate or a safe disposition. Typed cases: assembled candidate ready; exact-source revisit required/resolved; narrow gap lookup required/resolved; unresolved semantic gap; source unavailable; invalid/duplicate Research evidence; stale package/binding mismatch; runtime/tool failure. P1 guard rejects payload/outcome disagreement and immutable binding mismatch. A provisional V2 candidate is **not canonical acceptance**: full existing V2 strict semantic/provenance/temporal checks remain the final gate, not replaced by the lightweight envelope.

`DOSSIER-ASSEMBLY-RECEIPT-V1` is GitHub-owned, bound to the exact result hash/path, package identity and typed outcome. Receipts forbid canonical acceptance, Deep eligibility and retry/recovery authorization. The Research acceptance receipt is separately versioned and requires the package content hash, Git blob/commit, original identity and validation revision.

## 4. Exact-source-first, ownership, lifecycle

Machine contract `DOSSIER-TWO-STAGE-INTERFACES-V1` freezes supplemental order: accepted package → revisit **exact provided source** for a **named existing gap** → narrow lookup only after the source genuinely lacks that fact → unresolved typed GitHub disposition. An inaccessible page is **not** proof of factual absence or semantic exhaustion. Every gap lookup binds its `gap_id`, original source, exact AppID/title/work-year and a single named field/dimension. Broad new game research, new themes and invented dates/languages/identity are prohibited. No arbitrary fixed source or review quota.

P1 offline guard checks shape, cross-reference graph, duplicate local IDs, source/feedback parent modes/languages, source physical identity, 12 distinct dimensions, missing bindings, exact Research receipt hash, Assembly accepted-package identity, safe public locators, private/profile/raw-content fields and narrow-lookup dependency. It is **not an online prepublication validator**, nor authorization to skip existing strict ingest. P2 will implement the real GitHub-owned historical marker/parent verification, actual accepted-receipt provenance, canonical blob/hash resolution, source alias normalization parity, safe evidence/privacy enforcement, staging claims and atomic validation.

The contract defines future **inactive** Research and Assembly state vocabulary but no queue, staging, claim, retries, generation transition or recurrence engine. GitHub exclusively owns all scope/sequence, acceptance, retries/recovery, state and persistence. Final groups remain the same immutable groups of three, accepted by the existing strict Dossier group validator/ingest under the same shared writer.

## 5. Compatibility and feature gate

Explicit `implemented=true`, `active=false`, `authoritative=false`; semantic execution, staging/claim and canonical ingest separately disallowed. New `data/ai_inbox/dossier_research/` and `data/ai_inbox/dossier_assembly/` namespaces are **inactive**, not the existing `data/ai_inbox/taste_steam_review_dossiers/` transport. Current accepted Dossiers, existing Dossier V2 cache, Deep references and old prompt/contract hashes remain untouched. Automatic migration/rebinding of old hashes is forbidden. Activation requires separate tasks, real parity/shadow testing and explicit Director cutover authorization.

Architecture preflight: GitHub remains control-plane owner; the new PR-only test job changes no runtime/scheduler authority, no recurring production stage, new quota, active retry loop, staging writer or queue. No Scheduled Task or automation was created/edited/run.

## 6. Validation evidence

- `python -m unittest discover -s scripts -p 'test_dossier_two_stage_contract_schemas.py' -v` (requires `jsonschema>=4.21,<5`).
- `python -m unittest discover -s scripts -p 'test_taste_dossier_github_date_derivation.py' -v` (existing active one-stage Dossier).
- `python -m unittest discover -s scripts -p 'test_dossier_deep_release_year_identity_compatibility.py' -v` (existing Dossier/Deep boundary).
- PR-only workflow installs its own `jsonschema`, runs the three deterministic suites and has **no production permissions**.

**Verified:** PR-only workflow `Validate inactive Dossier two-stage interfaces` run `37806079484`, job `113410585094` — **success** on implementation SHA `e037228ddcc9f577f1c0335b3a1a5477b13b8795`; 15/15 P1 deterministic fixture tests green; 9/9 active one-stage GitHub factual-date tests green; existing `test_dossier_deep_release_year_identity_compatibility.py` executed directly and succeeded (the earlier unittest discovery matched 0 tests and was corrected). `Validate backlog dispositions` is an independent PR regression. These are schema/compatibility checks, not live two-stage execution or production proof. Fixtures are unit-test data only and are not written to any production inbox.

## 7. Scope and next task

No Research semantic worker prompt; no Assembly semantic worker prompt; no GitHub stage engine; no modifications to current Dossier order, per-group progress/recovery, final acceptance rules, Deep or publication; no production candidate/package artifacts; no scheduler changes.

**Recommended next task (not started): P2 — GitHub-owned deterministic staging helpers/validators, frozen authority and package hash checks, structural/privacy validation, Assembly preflight and atomic writer integration.** Do not activate Research/Assembly until later parity, inactive shadow and explicit cutover.
