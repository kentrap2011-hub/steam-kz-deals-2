# Dossier V2 — existing manual issuer adaptation (bounded draft)

Task: `dossier-v2-existing-issuer-adapt-implement-01`; source `main` at `eddea98e8abe242077c7438ad3b9526a2aa0f686`. This is a prospective *inactive* implementation, not an actual issuer, Research or Assembly launch.

## Reused mechanism

The **existing** original manual GitHub Actions freeze and separate one-use feasibility issuer remain the only control-plane entrypoints. Their V1 functions, freeze/nonce commit structure, strict single-added-path checker, Git main SHA lease, GitHub workflow identity/first-attempt gate, create-only remote branch lease, post-push re-fetch and direct-child authorization are reused for a new fixed V2 version. The 18 games/six triples are not reselected: `dossier_research_notes_v2._original_rows()` reconstructs exact title/edition/assignment SHA from the pinned original V1 buffer Git blob `c8a6b6f515162f431c0e3d86175376114c0acf7e`. Historical V1 marker `bb63cc29` and authorization `2a726cf6` are explicitly disallowed as V2 grants.

## Changed files

- `config/dossier_research_notes_v2_contract.json`: **disabled by default** version-specific namespace/branch, fixed trial/manifest/authorization locations, distinct manual confirmations and unresolved scoped human grant fields (`commit`, `blob_sha`, `github_actor_id` all null). Existing `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false` remain unchanged.
- `scripts/dossier_shadow_research_trial_publish.py`: optional `--version v2`; shared real Git create-only freeze + strict V2 original-18 manifest/marker parent; requires **separate committed human grant**, trusted exact GitHub Actions actor ID, first-attempt manual dispatch, checked-out exact main and unused separate remote ref **before any V2 write**. Original `v1` CLI/default gate/algorithm remains unchanged.
- `scripts/dossier_shadow_research_feasibility.py`: optional `--version v2`; separate direct-child create-only V2 authorization bound to original scope, marker SHA/parent/nonce, frozen manifest blob, V2 code/contract blobs, **scoped original-human-grant SHA/blob and GitHub actor/run IDs**. Same old-ref atomic lease and remote re-fetch. V2 structure verifier explicitly *does not* authorize semantics.
- Both pre-existing `.github/workflows/publish-dossier-shadow-research-freeze.yml` and `.github/workflows/authorize-dossier-shadow-research-feasibility.yml`: one optional version selector defaulting to `v1`, forwarded to the existing scripts. No new workflow, CI check or scheduler.
- `scripts/test_dossier_research_notes_v2.py`: adds disposable Git regression cases for actual versioned freeze/additive authorization, legacy dispatcher gate, immutable original pins, disabled/missing grant, forged actor/ref/attempt, historical SHA refusal, parent/path/rewrite and remote duplicate/race refusal.
- This report only.

## Threat and activation boundary

No V2 scope grant exists on current main; `manual_v2_issuer.enabled=false` is checked before the real V2 publisher can touch local/remote Git. No workflow has run or been dispatched for V2, no real V2 manifest, marker, approval, semantic worker, result/receipt/ingest, production, Fast/Deep or scheduled task was changed. A Git commit or a ChatGPT prompt is not authenticated human permission. A prospective future grant must be separately approved, committed exactly once, pinned and bound to the actual Github Actions dispatch actor. Freeze and post-marker authorization remain two distinct human-confirmed workflow invocations; success must be independently proved by first-attempt GitHub run records, not by commit author labels. Issuer code cannot enable Research, Assembly or canonical ingest.

## Tests and QA

The existing Notes V2 unittest runner (not new CI) has been extended with disposable local Git tests. **Actual existing GitHub checks pending on the draft PR.** Final HEAD, check results and admissible QA status must be recorded after those checks, not guessed. V1 original freeze/authorization code and historical control-plane refs were not executed or modified.

**Next separate gate:** independent ЧАТ 2 QA on the exact final draft PR HEAD. Even after successful QA/merge, a fresh human-grant scope decision, later exact manual issuer invocation with authenticated GitHub runs, and separate Research semantic approval are all required. No automatic activation.

Status: `IMPLEMENTED_INACTIVE_PENDING_EXISTING_TESTS_AND_INDEPENDENT_QA`.
