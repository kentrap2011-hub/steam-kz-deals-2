# Worker report — Dossier async end-to-end compatibility 01

- Task: `WORKER_TASK_DOSSIER_ASYNC_END_TO_END_COMPATIBILITY_01.md`
- Owner: NEW CHAT — ЧАТ 1
- Repository: `kentrap2011-hub/steam-kz-deals-2`; base: `main`
- Source baseline: `17a4ee599452b9c98c3d04b06c623db8bd7325ee` (2026-10-10).
- Implementation branch: `test/dossier-async-end-to-end-compatibility-01`
- PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/184 (OPEN, never self-merge)
- Status: **qa_complete_ready_for_director_review**; PR-only CI green; no production activation.

## Canonical preflight and isolation

`CHAT_PROTOCOL.md` START gate and `CHAT_CONTEXT.md` read. Task file read fully. Checked route in `PROJECT_ROUTES.md`, canonical `execution_ownership_contract.json`, two-stage interface/staging/async-buffer contracts and actual merged Research, Assembly and GitHub buffer source. Confirmed PR #179, #181, #182 are merged to `main`.

GitHub retains frozen scope, order, original Git provenance, item-state/strict validation, final atomic three-game Dossier acceptance and retries; worker helpers remain inactive, do not run live semantic research and do not treat submitted transport as a GitHub-accepted receipt. Architecture preflight: changes are only offline PR tests and a PR-only CI workflow; no new ownership, recurring scheduler, queue, retry manager, quota or production path is introduced.

## New acceptance evidence

- `scripts/test_dossier_two_stage_end_to_end_compatibility.py`: disposable GitFixture with real Research `frozen_research_batch`, `prepare_research_transport`, `inspect_existing_research_transport` and real Assembly `frozen_assembly_traversal`, `offline_assembly_candidate`, plus eventual GitHub `inspect_buffered_assembly_candidate`.
- Case 01: 12 exact games / four three-game groups, all Research candidates create-only; frozen Research and Assembly work without GitHub Research receipts or former eight-slot backpressure. Confirm marker first parent, plan/work blobs, prompt/contract/schema boundaries, original Git commit/path/raw SHA-256/Git blob/canonical SHA-256 and strict typed candidate identity.
- Case 02: Research A absent (local zero attempt) while B/C advance; malformed late A submitted and eventually quarantined without retroactively blocking B/C.
- Case 03: wrong Research item for Assembly plan, out-of-scope work, invented plan and later HEAD movement rejected/preserved as appropriate.
- Case 04: duplicate Research raw bytes not silently retried, modified Research candidate HEAD rejected, forged Assembly canonical acceptance rejected, create-only Assembly output collision rejected.
- No test fixture writes to this branch's production data; fixture Git histories reside inside temporary directories.
- `.github/workflows/validate-dossier-async-end-to-end-compatibility.yml`: PR-only, credentials not persisted, `jsonschema`, new cross-helper suite, both existing helper suites, P1/P2/buffer suites, one-stage Dossier date / Deep release-year compatibility and execution-ownership guard.

## CI outcomes (verified)

GitHub Actions run **38072636759**, job **114273050184**, head **24a8299d9633e3c877bff86f00018c1924315db8**:
https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38072636759 — **success**, all required steps green.

- Actual Research → Assembly 12-game cross-helper proof: **4/4 passed**.
- Existing inactive Research worker: **12/12 passed**.
- Existing inactive Assembly worker: **10/10 passed**.
- P1 strict contract/schema tests: **15/15 passed**.
- P2 GitHub staging/marker provenance: **25/25 passed**.
- Fully async GitHub buffer: **12/12 passed**.
- One-stage Dossier factual date: **9/9 passed**.
- **Total: 87/87 unittest cases passed**.
- Dossier → Deep release-year identity: `DOSSIER_DEEP_RELEASE_YEAR_IDENTITY_COMPATIBILITY=PASS`.
- Execution ownership: `ARCHITECTURE_OWNERSHIP_VALID`.

The first two pre-fix PR runs failed because the new test incorrectly supplied Assembly C's introduction commit when rechecking B. Test-only fix: retain each sibling's own immutable introduction commit; also avoid redundant suite discovery. No worker helper, shared validator, canonical control-plane, production or task plan was modified. The successful run above covers corrected source. This subsequent report-only commit does not change tested code.

## Risks / activation blockers

- Offline synthetic fixtures are not real-evidence semantic parity or shadow quality proof.
- Current Assembly output is staged-only and remains non-canonical until GitHub validates each Research → Assembly provenance chain and the existing strict V2 atomic three-game group ingest.
- Full production integration, activation authority, operator scheduler review and real semantic run are outside this task.
- Chat 2's independent eventual-chain acceptance QA remains separate and untouched.
- Research and Assembly `active=false`; one-stage Dossier remains production source of truth.
- Shared control-plane contracts and canonical validators were not changed.

## Worker handoff

Director reviews green PR #184; successful offline compatibility does not authorize activation. Do not self-merge. Any shared-control-plane incompatibility discovered by CI must become a separately scoped follow-up rather than an unapproved edit to shared validators/contracts.
