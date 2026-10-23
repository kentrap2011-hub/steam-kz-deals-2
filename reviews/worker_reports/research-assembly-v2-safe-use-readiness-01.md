# ЧАТ 1 — Research → Assembly V2: safe-use technical readiness

**Task:** `research-assembly-v2-safe-use-readiness-01`; [canonical task](../../WORKER_TASK_RESEARCH_ASSEMBLY_V2_SAFE_USE_READINESS_01.md).  
**Outcome:** `INACTIVE_IMPLEMENTATION_DRAFT_FOR_INDEPENDENT_QA`; **real-trial authority: BLOCKED / NOT GRANTED**.  
**Scope:** only `kentrap2011-hub/steam-kz-deals-2`; base `main` at `e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e` (merged Director [PR #242](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/242)).  
**Draft PR:** [#243](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/243), branch `implement/research-assembly-v2-safe-use-readiness-01`. Exact final PR HEAD and successful CI must be independently rechecked immediately before Director consideration; do not treat earlier CI as final-HEAD evidence.

## START / authority / architecture preflight

Re-read current `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, exact task file, `PROJECT_ROUTES.md` Notes V2 section, `DIRECTOR_PROTOCOL.md`, `PROJECT_DECISIONS.md`, `config/director_task_plan.json`, `DIRECTOR_TASK_BOARD.md`, `config/execution_ownership_contract.json`. Registry ID, task path, ЧАТ 1 and Board assignment all match merged #242. Director #242 registration HEAD `116ed28543d15753314019cd4e0f20860b791466`: required [site registry](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39961762153) and [backlog](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39961762208) checks SUCCESS.

Architecture ownership: GitHub alone owns original 18-item work scope, fixed six triples, exact identity/edition/assignment, new-run authorization and one-use marker, order, retries/attempt accounting, immutable transports, per-item disposition, canonical strict writer and Deep gate. Research and Assembly remain separate **bounded semantic data-plane stages** only when separately authorized. This developer task is **inactive technical code + synthetic test** scope, not semantics or operation. No change to control-plane ownership, no new queue, recurring stage, retry logic or scheduler. `config/dossier_research_notes_v2_contract.json` remains `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`; `config/dossier_two_stage_interfaces_contract.json` also remains inactive.

## What is already implemented vs not implemented

| Link | Status on base main | Evidence and limit |
| --- | --- | --- |
| Original exact 6 groups × 3 AppIDs, original AppID/title/edition/full-assignment digest | Offline implemented | `config/dossier_notes_v2_pinned_original_research_buffer_v1.json` checked as original Git blob `c8a6b6f515162f431c0e3d86175376114c0acf7e` by `scripts/dossier_research_notes_v2.py::_original_rows`. Source assignments, not newly guessed game names |
| Prospective versioned manifest, marker, one-add provenance | Offline implemented; prospective-only | `_manifest`, `frozen_assignment`, `manifest_blueprint`, `submitted_research`; no authenticated live issuer/nonce confirmation or real V2 trial |
| Sparse Notes (no sources/year/12-dimension gate), per-item isolation | Offline implemented; synthetic tested | `validate_notes`, `classify_research`, `frozen_assembly_traversal`; unsafe/invalid/missing A does not block B/C; missing != semantic attempt |
| Independent Assembly, strict final V2 validation | Offline implemented; synthetic tested | `assembly_work`, `candidate_assembly`, `inspect_assembly`, `prepare_assembly_transport`; unverified Research leads not accepted findings; no third semantic stage |
| Stable original publish prefix, independently appointed reviewers | Helper interface only | `checked_typed_publish_prefix` and `verify_independent_reviewers`; future real authenticated lookup, appointment receipt and Director confirmation currently ABSENT |
| Per-item receipts; existing atomic three-game strict acceptance | Proposal/readiness only | `item_receipt_blueprint`, `original_group_readiness`, `taste_steam_review_dossier_strict.py`; no GitHub-persisted V2 receipts, no live `strict_item_valid` → canonical three-member shared-writer integration |
| Runtime execution | ABSENT | Existing `.github/workflows/validate-dossier-research-notes-v2.yml` is PR-only offline validation (no dispatch); two V2 semantic prompts and `scripts/dossier_two_stage_versioned.py` are not actual scheduled/executable runtime activation |

Historical evidence is read-only in [PR #235](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/235) design, [PR #234](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/234) superseded strict adapter, [PR #233](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/233) gap diagnosis; [PR #232](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232) remains open/blocked `CHANGES_REQUIRED`. No PR232 source or ownership change is made by this PR.

## Implemented in draft PR #243

Only `scripts/dossier_research_notes_v2.py` and `scripts/test_dossier_research_notes_v2.py` are edited. Entire change is inactive and additive to existing V2 checks:

1. `_assert_unchanged_since`: first-parent Git history must show **zero** subsequent edits to exact original manifest, new run marker, submitted Research or submitted Assembly path. Detect a malicious/accidental edit **followed by byte-perfect restoration**, previously missed by latest-HEAD blob/raw equality.
2. `prepare_assembly_transport` re-runs exact `assembly_work` from the original immutable marker, manifest, AppID and introduced Research commit and requires identical work projection before any proposed write; stale/forged handoff or changed Research fails closed.
3. `checked_typed_publish_prefix` requires the current candidate to be the last verified typed-prefix member, previous prefix statuses to remain `candidate_already_submitted`, and immutable prefix ordering. Existing synthetic two-successive-candidate sequence remains valid. This **does not** repair old PR232 publisher; no V2 live publish hook is created.
4. `item_receipt_blueprint` forbids Assembly-only outcomes as Research status, and Research-completeness status as Assembly; receipt body receives privacy/size validation. Semantic attempts remain `unknown`, canonical acceptance always false.
5. `verify_independent_reviewers` refuses reused role appointment refs and non-boolean truthy approval callbacks; three distinct authentic account IDs remain required. **A stubbed callback in a fixture is never real identity/appointment evidence**.

Additional disposable-Git negative tests: manifest/marker/Research/Assembly rewritten then restored; stale and forged Assembly work; skip-ahead second typed target and false earlier published status; phase-confused or unsafe receipt; duplicate reviewer receipt and string approval; four explicitly missing IDs beside **14 synthetic empty safe notes** across the unchanged six triples. Baseline tests separately cover SULFUR `current_state` vs `identity` (substantive), Sifu `www` normalized locator and 2022-vs-2023 original-work conflict (must not be silently resolved), strict invalid final, unsafe/private references and full group readiness. All semantic inputs here are fictional synthetic fixtures, not real Research or trial results.

## Confirmed invariants and limits

- Original historical 18 remain: g3 `1508750,1517180,1533420`; g8 `1590230,1599600,1607130`; g13 `1849000,1857090,1868140`; g15 `1999170,1999360,2009010`; g18 `206420,2067050,2076140`; g20 `2124120,213610,2138710`. Actual old inspect proved **12 structurally ready, 2 transport-invalid (SULFUR, Sifu), 4 missing**; not 14 semantically accepted. Four missing worker attempt histories **UNKNOWN**. Their historical bytes/markers cannot be relabelled/reused or overwritten.
- New V2 allows missing/yearless/zero-source safe Research Notes without inventing roles, source visits or completeness. Assembly independently investigates identity/year/edition and evidence, corrects substantive errors only with independent sources and logs; strict final Dossier V2 still governs. No accepted item, Deep-ready result, group ingest, reviewer approval, or real trial outcome follows from any synthetic test.
- GitHub-attested real issuer, durable receipt writer, live async per-item handoff, user-authorized one-shot execution, **authenticated reviewer lookup plus owner-confirmed separate A/B/C appointment**, exact original order under live two-publication transport, and canonical shared-writer parity are **CONTRACT_BLOCKED / unimplemented**. The existing Python hooks can validate fixture-level structure but cannot themselves authenticate GitHub user appointments or grant live semantics.

## Required pre-activation checklist (separate Director decisions)

1. Independent ЧАТ 2 reviews **exact #243 HEAD**, diff, source/PR-only CI, untouched V1/PR232/production, disposable Git ancestry, no unapproved activation. No self-QA/merge.
2. Separate bounded GitHub-owned **contract + issuer** design/implementation for entirely new immutable V2 trial ID/namespace and genuine one-time human authorization, attest the original buffer and 18 immutable assignments/titles/editions; prove one-create-only manifest/marker binding, no historical replay, post-marker race and duplicate prevention. Obtain fresh independent CI/QA.
3. Implement actual GitHub receipt persistence, committed per-item evidence verification, per-item quarantine, cross-invocation ordering and **strict final same-original-three atomic writer** within existing shared-writer lock; require replay/idempotence/failed A and success B/C negative tests, with actual source and semantic policy checks. Do not activate before QA.
4. Authenticated independent reviewer A/B/C GitHub identities and **separate Director-appointed** receipt verification; not regex, role label, fixture mock or self-assertion.
5. Conduct source-quality/evidence audit and strict V2 parity, including original-work year, exact edition identity, independent player-source physical provenance and negative/positive feedback coverage; unknown insufficiency stays unresolved, not inferred solved.
6. Director explicitly permits **one** prospective fixed-same-18 semantic Research trial only *after* all technical and reviewer gates, then separately Assembly/candidate publish and canonical integration. No implied retries, backfill, production/Deep cutover, scheduled task or Deploy permission.

## Validation / handoff

- New targeted synthetic suite is `python scripts/test_dossier_research_notes_v2.py -v`, Python 3.11 with `jsonschema==4.23.0`; targeted PR workflow `Validate inactive Research Notes V2 and autonomous Assembly` is the authoritative CI proof once SUCCESS at **final #243 HEAD**. `Validate site task registry and page` and required backlog checks must also be checked for this exact HEAD.
- Local checkout unavailable in this chat's container (GitHub host DNS inaccessible); **no claim that tests ran locally**. Tests are to be independently verified by GitHub Actions and QA. Synthetic code changes cannot certify live semantic correctness.
- `CURRENT_TASK.md` is shared historic operational handoff; untouched to avoid overwriting other active work. This task's complete durable report is this dedicated file.

**Final worker status:** `INACTIVE_IMPLEMENTATION_DRAFT_FOR_INDEPENDENT_QA` (provided exact-head CI green; otherwise `CI_BLOCKED`). **Recommended next step:** Director registers NEW independent ЧАТ 2 exact-HEAD QA for draft PR #243; do not merge or authorize real Research/Assembly before its verdict and separate live-contract gate.
