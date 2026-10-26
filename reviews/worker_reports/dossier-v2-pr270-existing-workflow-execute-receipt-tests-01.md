# ЧАТ 3 — PR #270: existing V2 workflow receipt tests

**Status:** `TESTS_PASSED` (synthetic/offline only). **PR #270 remains draft, unmerged and inactive.**

## Scope / architecture preflight
- Repository: `kentrap2011-hub/steam-kz-deals-2`, source of truth `main`; exact existing PR branch `implement/dossier-v2-research-per-item-receipts-01`.
- `config/execution_ownership_contract.json`: GitHub owns validation and control plane; interactive chat only changed the existing PR validation workflow.
- `config/dossier_research_notes_v2_contract.json` on PR branch: `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`.
- No new workflow, schedule, retry, queue, production writer, semantic run, real Research/Assembly, or canonical persistence.

## Exact change
Updated **only** existing `.github/workflows/validate-dossier-research-notes-v2.yml` in PR #270: one additional command `python scripts/test_dossier_notes_v2_per_item_receipts.py -v` (existing Python 3.11 + jsonschema runner); added the receipt helper and regression file to the existing `pull_request.paths` list. Code for the receipt helper and 14 tests was already present on the PR branch.

**Tested implementation/workflow head:** [`4e78cc36dcb80e1ac7f63b1832226ffd5ba20125`](https://github.com/kentrap2011-hub/steam-kz-deals-2/commit/4e78cc36dcb80e1ac7f63b1832226ffd5ba20125).

## Executed GitHub proof
- Existing workflow: [run #38, attempt 1](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40287779143), `pull_request`, PR #270 head `4e78cc36...`, job [`synthetic-v2`](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40287779143/job/121455415289).
- Exact command logged: `python scripts/test_dossier_notes_v2_per_item_receipts.py -v`.
- **Target suite: 14 tests, 14 PASS, 0 FAIL, 0 ERROR; `Ran 14 tests in 13.760s — OK`.**
- Existing companion Notes V2 suite: **37 PASS, 0 FAIL** (`Ran 37 tests — OK`). Syntax / disabled-activation guard: success.
- The GitHub runner checked out the PR's code; no other PR's green checks are used as evidence. No manual duplicate run.

## Covered regressions and residual boundary
- **A rejected, B progresses:** `test_remote_failure_for_a_does_not_prevent_b` with disposable bare-Git remote; wrong bindings and malformed candidate fail closed.
- **Duplicate/stale-head/remote collision:** `test_remote_duplicate_stale_parent_and_spoofed_github_fail_closed` plus create-only replay and two local branches; no overwrite or fabricated confirmation.
- **False GitHub acknowledgement:** disposable remote may set `remote_git_confirmed` but does **not** set `github_receipt_confirmed` or `canonical_acceptance`; fake token rejected; noncanonical result preserved.
- **Critical remaining untested path:** *successful* authenticated GitHub REST read-back and real remote write under valid issuer authority was **not exercised**. Fixtures use a local bare Git remote, not live GitHub. This suite proves synthetic implementation invariants, **not** live Research authorization, semantic correctness, or production/canonical acceptance. Any true live trial requires independent explicit authorization.

**Disposition:** `TESTS_PASSED` for the 14 Git-only regression tests. Keep PR #270 unmerged/inactive pending independent exact-final-head acceptance; do not launch real Research/Assembly or infer a cutover.
