# Independent L3 delta QA — Dossier V2 PR #368

**Task:** `dossier-v2-pr368-evidence-guard-l3-qa-01` · **Worker:** new ЧАТ 2 · **Mode:** independent focused READ-ONLY QA of source, one report-only DRAFT PR.  
**Source:** [PR #368](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/368), branch `fix/dossier-v2-assembly-presubmit-evidence-guard-01`.  
**Exact source HEAD checked twice:** `090ac91386422149264454fff8d3807a83856bfb`; PR remains OPEN/DRAFT/unmerged. **Base:** `main`, source PR base SHA `e141d5d3b77a8d8ea0be38249b61b59265ee1cb5`.  
**Verdict:** **PASS_FOR_DIRECTOR_MERGE_REVIEW**, strictly for the bounded inactive V2 worker prompt and synthetic regressions. **NOT** production, original18 replay, pilot promotion, Deep, or proof of real player evidence.

## START, source inventory and independent scope

Read `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`, the exact worker task in `main` and relevant V2 route in `PROJECT_ROUTES.md`; checked V2 contract, original18 audit/mismatch reports, Assembly result schema, `scripts/dossier_research_notes_v2.py::candidate_assembly / inspect_assembly / prepare_assembly_transport`, shared `scripts/taste_steam_review_dossier_strict.py`, existing synthetic fixture and V2 CI workflow. No other repository, no semantic Research/Assembly, no pilot/writer/Actions dispatch, no merge or source edits.

GitHub's complete [source diff](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/368/files) and independently enumerated changed-file list both contain **exactly three files**:
1. `config/dossier_two_stage_autonomous_assembly_v2_worker_prompt.md` — one pre-submit evidence/shape checklist (+7 lines).
2. `scripts/test_dossier_research_notes_v2.py` — three new synthetic test methods, shared fixture imports and helper.
3. `reviews/worker_reports/dossier-v2-assembly-presubmit-evidence-quality-guard-01.md` — implementation report.

**No** source PR changes to schema, strict validation, shared writer/producer, V1, Research Notes contract, frozen original18 candidate/receipt/store, runtime, ownership, queues, retry, schedules, workflows, Board or CURRENT_TASK. No active-flag change. Source PR is not self-merged.

## Checklist and actual validation

- **Immutable identity:** pre-submit prompt demands frozen exact AppID/title/edition/assignment; actual preflight checks exact `assignment`/`research_transport` against GitHub-frozen work and final strict validates `expected_appid` and `expected_title`. `game_identity.release_year` is deliberately **not** pinned to old Research `old_year` (known Sifu original-year vs Steam edition-date conflict); the prompt correctly requires independent work-date vs Steam-date disambiguation. This is a human evidence requirement, **not a machine-attested original-year check**.
- **Operation fields:** JSON Schema permits `operations[].kind` only `source_revisit / independent_discovery / targeted_gap_lookup / identity_disambiguation / conflict_resolution / technical_normalization / result_self_correction` and `access` only `opened / inspected_collection / search_result_only / unvisited_reference / unknown`; `access_blocked` is forbidden. Prompt tells worker to mark login/age/tool restriction `unknown`, explicitly describe lack of inspection. Preflight validates **the exact supplied document**, not only a reconstructed candidate.
- **Player evidence and temporal roles:** prompt rejects Research Notes/snippets/aggregates/other editions as verified final evidence; it requests directly attributable original-player feedback and source/date/role checks. The unchanged strict `_validate_observations` rejects `historical` without **both** bound historical-role support and a **recent dated current_state** support record, and rejects `current` without recent dated current-state evidence. An assertion about SULFUR 1.0 cannot be certified from old feedback.
- **Honest incomplete:** `assembly_missing_evidence` and `assembly_semantic_conflict` must have `final_dossier=null` and a diagnostic; they can pass transport preflight but remain item-local nonaccepted dispositions. The prompt retains **at most two** mechanical, **pre-publication** corrections, one immutable create-only submission and no semantic retry.
- **Strict continuity:** `prepare_assembly_transport` still runs `validate_dossier_strict` on ready dossiers, refuses stale binding/occupied create-only path; `inspect_assembly` independently rechecks strict after Git introduction. There is **no bypass, disabled guard, relaxed enum or weakening** in PR #368.

| Targeted case | Observed check | Result |
| --- | --- | --- |
| 206420-style historical on durable-only support | `test_presubmit_206420_like_historical_needs_role_and_recent_current_feedback` → strict error `historical claim lacks historical feedback` | **NEGATIVE PASS** |
| Historical role but no **bound** recent current-state feedback | same test → `historical/fixed claim lacks recent dated current-state check` | **NEGATIVE PASS** |
| Historical role + recent dated bound `current_state` fixture | same test → `ready_for_create_only_submission`, `canonical_acceptance=false`, no created output | **POSITIVE PASS** (precheck only) |
| 1607130-style `access_blocked` | `test_presubmit_1607130_like_invalid_access_enum_rejected` → `unparseable` | **NEGATIVE PASS** |
| Login-gated `unknown` + truthful typed terminal | same test → precheck PASS; disposable local Git introduction and `inspect_assembly` return `assembly_missing_evidence`, not canonical accepted | **POSITIVE PASS** (incomplete only) |
| Forged final AppID/key and wrong title/edition | `test_presubmit_final_dossier_cannot_rebind_original_appid_or_edition` → `final_strict_or_group_rejected` in both subcases | **NEGATIVE PASS** |

**Evidence provenance of table:** actual GitHub CI ran all three methods on the **exact source HEAD**, and source code was independently read to verify the fixtures call the real `prepare_assembly_transport`/strict path with concrete exception codes and assertions. These are not empty tests. Local offline replay by this QA chat: **0**; this report does not claim a separate executed reproduction. The synthetic `web_dossier` fixture manufactures dates/roles/reviews for structural QA, **not** factual testimony. A distinct stale-but-bound / undated-`current_state` negative subcase is not added by this PR; shared strict dates are inspected statically, and the required missing-bound-current-state negative is covered. This is an **optional future regression extension**, not evidence of current bypass.

## Exact HEAD CI (not inherited from preceding implementation HEAD)

Confirmed GitHub `fetch_commit_workflow_runs` for `090ac913...` and actual latest-attempt job steps/logs:

- [Inactive Research Notes V2 and autonomous Assembly, run 41436228732](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41436228732): **SUCCESS**, job `synthetic-v2`. Raw job log: **55/55 Notes V2**, **15/15 receipt** and **1/1 shared strict writer** = **71/71** offline tests, plus syntax and inactive flags guard. Three new presubmit methods explicitly logged `ok`. Workflow step label still says 14 receipts; actual runner logged **15**.
- [Inactive eventual-chain QA, run 41436228714](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41436228714): **SUCCESS**, all job steps.
- [Backlog dispositions, run 41436228736](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41436228736): **SUCCESS**, all job steps.
- [Site task registry, run 41436228722](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41436228722): **SUCCESS**, all job steps.

Combined legacy commit status endpoint returned **no statuses** (not a failed check); four associated PR Actions runs were present and completed successfully. No claim of unexposed external branch-protection check. Source HEAD re-read unchanged before report publication.

## Architecture preflight, residual risk and recommendation

1. GitHub remains the owner of exact assignments, lineage, receipts, strict validation, retry and persistence; semantic worker only produces externally supported data through authorized transport.
2. `config/dossier_research_notes_v2_contract.json` still has `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`. The existing scoped original18 authorization is sandbox-only, one-use and zero-retry, **not** a global activation.
3. No source change transfers GitHub control-plane ownership to interactive/scheduled ChatGPT.
4. No new recurring stage, schedule, queue, quota, retry loop or pilot write.

**Material limits:** 14/18 isolated sandbox stored, four rejected, 0 live V2 canonically accepted (per pinned original18 audits); **9/18 quality grades remain independently unchecked**, some review bodies remain age/login-gated; historical exact runtime first error for 206420 unproven; SULFUR pre-1.0 feedback does not establish post-2026-10-28 current player state; no actual new semantic validation or real player-review truth attested by this PR or CI. The checklist is worker-facing, not enforced proof of real source inspection. Preserve original frozen outcomes and receipts.

**Director recommendation:** PR #368 is suitable for **director merge review of this narrow prompt/test hardening**, **not automatic merge**. Do not launch original18 again or enable pilot promotion, production, canonical writer, new semantic Research or Deep. If future use requires source-truth assurance, request a **separately authorized bounded RECON/CONTRACT** for actual observed review evidence and a machine-checkable quality/evidence model; do not mislabel this checklist as such a guard. No repair required inside this PR from focused L3 QA.

**Final status:** `PASS_FOR_DIRECTOR_MERGE_REVIEW`.
