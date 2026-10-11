# WORKER TASK — Dossier Research original release-year consistency fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth / base: `main`
Task ID: `dossier-research-original-year-fix-01`
Physical developer slot: **НОВЫЙ ЧАТ — ЧАТ 1**
Mode: **IMPLEMENT BOUNDED FAIL-CLOSED FIX / OFFLINE VALIDATE**

## Scope and evidence

PR #185 identified an **unresolved** defect: existing P1 `validate_research` can accept a Research package whose `identity.original_work_release_year` disagrees with the same original work's `sources[*].exact_product_binding.original_work_release_year`. The known-gap regression in `scripts/test_dossier_two_stage_eventual_chain_qa.py` was marked **XFAIL**, not fixed. PR #184/#185 have been merged as offline QA only. Fix this exact defect in Research's **inactive** validation path, not the production one-stage path.

## START / ownership

1. Read the actual current `CHAT_PROTOCOL.md` from `main` and execute START gate. Read current `CHAT_CONTEXT.md`, this entire task, and the exact finding in `reviews/worker_reports/dossier-async-github-chain-acceptance-qa-01.md`.
2. Work **only** in `kentrap2011-hub/steam-kz-deals-2`; if GitHub selects another repo, stop/switch. Run architecture preflight against `config/execution_ownership_contract.json`, `config/dossier_two_stage_interfaces_contract.json`, `config/dossier_two_stage_staging_contract.json`, `config/dossier_two_stage_async_buffer_contract.json`. Review the narrow relevant `PROJECT_ROUTES.md` section and existing P1 `validate_research`/Research source-binding schema/tests, not a broad repository scan.
3. GitHub is sole owner of authorization, frozen exact bindings, canonical ingest, retry and final acceptance. No semantic-worker authority transfer, runtime activation or production edits.

## Required correction and acceptance

- Reproduce the specific contradictory original-work-year fixture from merged PR #185; make it a **normal passing negative test**, removing or updating its XFAIL only within task ownership.
- Enforce strict same-original-work-year consistency between Research identity and each relevant source `exact_product_binding` under current schema/semantic rules, including subtle cases (missing or unresolved identity, aliases/versions, conflicting corroborators). Do not invent missing years, silently coerce or rewrite evidence. Fail closed with useful local diagnostic when an explicit contradiction cannot be reconciled.
- **Preserve** the accepted distinction between an original work's release year and the Steam storefront/publication year or a port/remaster's release date. Do not wrongly reject legitimate cross-platform or cross-kind source evidence merely because a Steam date differs. Source precision and original-product identity must remain intact.
- Verify both a normal valid Research package and the bad fixture through actual P1 validation, existing P2 `receive_research`, and downstream inactive GitHub item-chain/strict candidate/group tests as appropriate. An invalid Research package must not become `accepted_structural_evidence`, accepted canonical Dossier, or Deep-ready; unrelated games continue without semantic-worker head-of-line blocking.
- Add negative and positive isolated fixtures (same original-year, mismatch, legitimate storefront-year difference, unresolved original identity/years, multiple-source contradiction, incomplete sources, and one-stage regression). Use only disposable/temp/test data. Prefer the smallest fail-closed P1 validation fix and tests.
- Maintain `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false` and the current one-stage production authority. Do not loosen strict final validator or change source evidence standards.

## Parallel file ownership

ЧАТ 2 independently implements the **inactive GitHub final acceptance/group writer bridge** in `WORKER_TASK_DOSSIER_ASYNC_GITHUB_FINAL_ACCEPTANCE_INTEGRATION_01.md`. You own the **Research P1 validation logic and Research-owned test/CI**; do not edit ЧАТ 2's integration writer/adapter, new tests, workflow, task, report, or shared Director registry. The final bridge must eventually use this corrected strict Research validator, but neither worker waits for the other's PR to write its own isolated implementation. If shared interface changes are unavoidable, report precisely to Director instead of racing edits.

## Deliverables / prohibitions

A focused implementation branch and PR against latest `main`, green isolated CI (including known-gap regression now **PASS, not XFAIL**), plus report `reviews/worker_reports/dossier-research-original-year-binding-fix-01.md` with exact files, positive/negative matrix, CI evidence, residual risks. **Do not self-merge.**

No real game semantic analysis, no production data, canonical writer activation, Scheduled Tasks creation/modification, Deep/Fast/ranking/UI/translation/Steam changes, secrets, other repos or `manual-shell-write.yml`. No activation or production readiness claims from isolated tests.
