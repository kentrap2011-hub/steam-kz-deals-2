# Dossier V2 — Assembly pre-submit evidence/shape guard (ЧАТ 2)

**Task:** `dossier-v2-assembly-presubmit-evidence-quality-guard-01`  
**Role:** inactive-V2-only bounded IMPLEMENT / offline TEST, one **draft source PR**, independent L3 delta QA required before director merge.  
**Base:** `main` at `e141d5d3b77a8d8ea0be38249b61b59265ee1cb5`.  
**Verdict:** **READY_FOR_INDEPENDENT_L3_DELTA_QA** (conditional on checking exact-head PR CI; not a production-approval verdict).

## Authority / START / preflight

Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task, V2 route in `PROJECT_ROUTES.md`, architecture decisions and `config/execution_ownership_contract.json`. GitHub remains control-plane owner of frozen assignments, strict validation, receipts and persistence. `config/dossier_research_notes_v2_contract.json` has `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`. This task permits **only** prompt, one already-existing V2 offline test and this report; it does not transfer responsibility to ChatGPT or create a stage/queue/retry/schedule. The other active worker investigates V1 separately.

Read prior independent original18 QA report (PR #324) and original18 mismatch diagnosis (PR #331). They establish **18 Research + 18 Assembly** original submissions, **14 sandbox stored with matching receipts, four writer invalid**, **0 canonical live V2 acceptance**; no pilot rewrite is authorized.

## Pinned immutable examples (read-only)

- **AppID 206420, Saints Row IV: Re-Elected**: original Assembly commit `911d869268118f0b145c3c7d5baf59811a82b933`, candidate Git blob `0b8bdb111a7361bf66b69c52a8910c606d7f55aa`. Observations 4 and 7 (1-based) carry `evidence_status=historical`, cite only `source-002` with `evidence_role=durable_trait`, and lack the required recent dated `current_state` feedback. `taste_steam_review_dossier_strict.py::_validate_observations` explicitly rejects this role/time mismatch. Its earlier typed receipt claimed readiness, but the original writer reported only `invalid`; **first runtime exception is not established**.
- **AppID 1607130, Lust Theory - Season 1**: original Assembly commit `1eed1d8079c786aa25d3411b58238f87691995ac`, candidate Git blob `15f1f29c166b7c00fb8e357e6fbf7eccfa4eeba0`. `outcome=assembly_missing_evidence` accurately describes login/age-gated access and sparse player evidence, but `operations[0].access=access_blocked` is outside the existing five-value schema enum. A future *new* terminal candidate may use `unknown` plus an exact limitation description, never imply the reviews were inspected.

## Changes in this PR — strict three-file write set

1. `config/dossier_two_stage_autonomous_assembly_v2_worker_prompt.md`: added **one mandatory pre-submit checklist** covering canonical operation enum and truthful blocked access; frozen AppID/title/edition and original work-vs-Steam date; independent verifiable player-feedback sources; `historical` role plus recent **dated** current-state feedback and patch-sensitive freshness; typed `assembly_missing_evidence`/`assembly_semantic_conflict` where evidence is insufficient. Preserved two allowed **pre-publication** mechanical corrections, one immutable submission and strict final validation.
2. `scripts/test_dossier_research_notes_v2.py`: added **three offline adversarial test methods**, with multiple positive/negative subcases, on the existing synthetic Git fixture. They check (a) 206420-like `historical` with durable-only support fails; even historical-only without recent-current fails; both roles plus recent dated current-state support passes pre-submit; (b) 1607130-like out-of-enum `access_blocked` fails, while honest `unknown` + typed `assembly_missing_evidence` passes pre-submit but remains non-accepted terminal; (c) immutable wrong AppID or title/edition in final Dossier fails. Synthetic feedback is not asserted to be real.
3. This worker report.

**No changes** to strict validator, JSON schema, shared writer, V1, Deep, Fast, production, frozen original18 candidates/receipts, workflows, ownership contracts, schedules, execution state, task/Board or GitHub Actions dispatch.

## Verification and evidence limits

- **Static/read-only checks:** original candidate fields and schema enum inspected at exact immutable Git commits; the current validator guards and `prepare_assembly_transport` precheck compared. No reproducible validator weakening or proven shared-code bug; leave both untouched.
- **Offline test inventory:** `scripts/test_dossier_research_notes_v2.py` contains **55 test methods (52 existing + 3 new)**, including multi-case subtests. The PR CI path is `.github/workflows/validate-dossier-research-notes-v2.yml`, which also runs separate receipt and strict writer tests.
- **Executed local tests:** **0**. The local environment cannot resolve github.com to check out the repository; no sandbox runtime replay or executed strict check is claimed.
- **Exact-head CI:** **PENDING** when report first created; verify completed workflow run at the exact PR HEAD before approving/merging. CI is not evidence of independent semantic source truth.

**Known unresolved evidence limits:** Nine of eighteen original pilot quality grades remain independently unverified. SULFUR (`2124120`) was built from pre-1.0 player evidence; the reported 2026-10-28 release boundary needs a *separately authorized* independent post-1.0 review and exact build/freshness evidence. Age-gated review bodies, actual product feedback breadth, independent source diversity and the first 206420 runtime error are not established by a textual checklist. **NO_GO remains for production, original18 replay, pilot promotion and Deep readiness.**

## Risk, rollback, independent review

Primary risk: workers may ignore the pre-submit checklist, and synthetic fixtures prove structural prechecks only, not real source verification or future worker behavior. This change is not self-enforcing CI for semantic truth. Roll back by closing this isolated unmerged draft PR or reverting **only** its prompt and V2 test addition after authorized review; immutable pilot/canonical state never changes.

Independent focused **L3 delta QA** must inspect prompt semantics, exact-head CI, positive/negative historical evidence and access enum behavior, exact title/AppID protection, preservation of terminal/incomplete outcomes, and all inactive flags before any director decision. No self-merge.
