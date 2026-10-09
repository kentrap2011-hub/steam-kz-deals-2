# ЧАТ 2 — Dossier Research → Assembly P2 GitHub staging/control-plane

**Task:** user-authorized P2 after accepted architecture PR #171 and inactive interfaces PR #173.
**Mode:** implementation, **inactive**. Base `main`; branch `implement/dossier-two-stage-inactive-staging-p2-01`.
**Status:** implemented with verification tracked by PR CI. No production or semantic activation.

## Scope/files

Added:
- `config/dossier_two_stage_staging_contract.json`: explicit non-active GitHub-owned stage policy, paths and lifecycle, writer integration still forbidden while inactive;
- `config/dossier_research_rejection_receipt_v1.schema.json`: typed sanitized Research rejection/incomplete/exhausted receipts;
- `config/dossier_two_stage_staging_state_v1.schema.json`: immutable per-game Research/Assembly state;
- `scripts/dossier_two_stage_staging.py`: Git-based validated, **side-effect-free** proposed create-only Research receipts + state, and Assembly assignment + state;
- `scripts/test_dossier_two_stage_staging.py`: isolated temporary Git repository with actual commits, marker-parent provenance, non-active staging transition tests;
- `reviews/worker_reports/dossier-two-stage-staging-p2-01.md`: this report.

Modified only `.github/workflows/validate-dossier-two-stage-contract-interfaces.yml` to add P2 tests to its **existing PR-only read-only** validation. No main production/workflow file touched, specifically **not** `.github/workflows/build-pre-ai-store-snapshot.yml`, no commercial refresh workflow changes and no current Dossier ingest/writer edits. No Scheduled Task or automation modified.

## Architecture preflight

GitHub remains the only possible owner of scope, ordering, recovery, retries, assignment/marker history, transport acceptance and canonical persistence, per `config/execution_ownership_contract.json`, existing active Dossier contracts and inactive `config/dossier_two_stage_interfaces_contract.json`. The accepted PR #171 architecture authorizes a **non-active implementation target**, not a new ongoing producer. Neither interactive worker, Research nor Assembly chooses games/retries or publishes canonical results. No new schedule, recurring task, production queue or batch quota.

## Stage A — frozen Research intake and validation

`receive_research(repo, marker_commit, prepared_work_path, package_commit)` is inert and returns a proposed pair of GitHub-owned **create-only** files; it does not write to production. It reconstructs an actual Git marker single parent and its nonce-only marker file, verifies marker commit changed only that file, loads a GitHub-prepared assignment *from its actual marker parent* (without worker-chosen marker SHA/nonce), validates the exact existing Dossier group descriptor and still-pending worker-index scope frozen in that parent, and validates exact Research schema content hash. Frozen marker -> package introduction must remain on first-parent lineage. Package Git commit must introduce the single exact predeclared file; content is read from Git object bytes, with Git blob SHA verified.

Structural/schema/reference/privacy/safe locator/product/12-dimension validation is performed using the P1 strict guard plus P2 source URL normalization and physical-source dedupe. A package cannot invent a Research contract digest, use an alternate AppID/title/snapshot/group/item binding, or turn a material incomplete package into Assembly-ready. Accepted whole-package content SHA-256 is derived by GitHub from canonical JSON (no worker-supplied hash); real Git blob and introduction commit are recorded in the accepted receipt. Distinct typed sanitized rejection receipts preserve original Git origin and raw-content digest, while avoiding raw payload/log copies and **consuming no normal Dossier semantic attempt**. Untrusted Git origin/marker fails before producing even a purported authoritative rejection.

The Research state `--research.json` and accepted/rejected receipt path are immutable unique paths; duplicate/replayed/stale/mismatched transport returns fail-closed rather than overwrite, rename or retry. A new Research submission cannot trigger an independent scheduler, retry engine or Deep eligibility.

## Stage B — exact accepted-package assignment only

`prepare_assembly(repo, marker_commit, plan_path)` loads the predeclared GitHub-only Assembly plan from the Stage-B marker's real Git parent. Stage B can be assigned only after an accepted Research receipt and matching immutable Research state have been committed on the frozen first-parent history; rejected/incomplete/exhausted states cannot authorize it. The original Research package Git blob/content/hash, accepted receipt Git blob and original marker/group binding are checked again against Git history.

Assembly assignment copies **exact** original game/item/snapshot/group/contract binding and Git-accepted package SHA, exact V2 Dossier target binding, GitHub-predeclared Assembly id, Stage-B frozen marker, prompt/contract digests and create-only Assembly path. It emits the `--assembly.json` state as a separate proposed create-only artifact, without running Stage B semantic analysis. Neither state asserts a canonical Dossier acceptance or Deep readiness.

## Inactive and compatibility invariants

`config/dossier_two_stage_interfaces_contract.json` stays `active=false, authoritative=false, authorized_for_staging_or_claims=false, authorized_for_canonical_ingest=false`. New `config/dossier_two_stage_staging_contract.json` has `active=false, executable_in_production=false, authoritative=false`. There is **no CLI or GitHub Actions production ingestion trigger**. The planner returns deterministic artifacts for future GitHub-writer integration only; no durable Research/Assembly production files are created in this task. All fixture commits are in disposable temporary repositories.

The existing one-stage Dossier V2 worker, result transport, canonical validator/group ingest/cache/progress, Deep eligibility, historical results, old prompt hashes and group-of-three acceptance authority are unchanged. Other active UI, ranking, Steam, commercial refresh and translations are unchanged.

## Tests and validation

PR-only CI:
`python -m unittest discover -s scripts -p 'test_dossier_two_stage_staging.py' -v` — 25 deterministic Git-history, acceptance/rejection/assembly/lifecycle/replay/stale/privacy tests.
Existing P1 schema tests and Dossier/Deep compatibility checks are retained in the same CI job.

**Verified CI:** implementation head `4e0d88d250dd1a1e1c8098ee13f064e5a27f5be2`.
- `Validate inactive Dossier two-stage interfaces` run `37902329468`, job `113727538743` — **success**.
- P2: **25/25** isolated temporary-Git staging tests passed, including rejected Research transport, real blob/first-parent/marker verification, immutable accepted receipt, stale/mismatch/collision refusals, accepted-only Assembly and disabled production authority.
- P1: **15/15** prior strict schema/binding fixtures passed.
- Current one-stage Dossier GitHub-derived date regression: **9/9** passed.
- Existing Dossier/Deep release-year compatibility script: **success**.
- `Validate backlog dispositions` run `37902329500` — **success**.
- First P2 CI on PR #175 found one overly specific test diagnostic assertion for a nonexistent Assembly plan path (actual code correctly rejected it earlier at Git provenance); assertion corrected without weakening the rejection.

These tests prove offline frozen Git provenance and deterministic staging plans, not production acceptance, publication or actual shared writer serialization.

Note: these tests validate the **offline GitHub-owned transition planning**, not the final shared writer atomic Git commit/cancel coalescing, which must remain a separate integration step. An authorized future integration must serialize receipt + state / assignment + state commits with the existing canonical-writer and recheck all create-only paths under lock. Connecting this to current production workflows would conflict with the concurrent commercial-refresh worker and is deliberately **not attempted**.

## Next boundary

After PR review, future P3/P4 semantic roles can be implemented inactive against these interfaces. A separately authorized shared GitHub writer integration under existing Dossier serialization is still required **before** activation; never silently switch the inactive gate on. No semantic worker, production processing, recovery, scheduler change or cutover was executed.
