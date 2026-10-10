# WORKER TASK — Dossier async GitHub eventual-chain / strict acceptance QA 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth / base: `main`
Task ID: `dossier-async-chain-qa`
Physical worker: **НОВЫЙ ЧАТ — ЧАТ 2**
Mode: **INACTIVE; OFFLINE STRICT CHAIN VALIDATION QA; PR-ONLY**

## Objective
Independently prove the current GitHub-owned eventual Research→Assembly chain validator **cannot** accept invalid chains as canonical Dossier or Deep-ready. Validate strict original **atomic three-game group** boundary and independent item error isolation. PRs #179/#181/#182 have already merged to `main`. No production activation or real semantic execution.

## START and authority
Read current `CHAT_PROTOCOL.md`, execute START gate, then current `CHAT_CONTEXT.md` and this task **fully** from `main`. Operate only in repository `kentrap2011-hub/steam-kz-deals-2`; correct a wrong tool-selected repository immediately.

Consult targeted `PROJECT_ROUTES.md` sections and current `config/execution_ownership_contract.json`, `config/dossier_two_stage_interfaces_contract.json`, `config/dossier_two_stage_staging_contract.json`, `config/dossier_two_stage_async_buffer_contract.json`, existing P1/P2/async validation helpers and strict final V2 Dossier schema/validator. Do not broadly rescan the project.

GitHub is sole authority for preauthorization, original Research/Assembly binding, strict Research validity, final item/group acceptance, retry/recovery, and Deep readiness. Inactive semantic workers never self-accept or choose new work.

## Bounded QA requirements
- Only **disposable isolated Git-history fixtures**, not real game evidence, actual production writes or live runs.
- Exercise **existing** eventual GitHub chain validation with submitted but unaccepted Research; verify exact Git commit/path/blob/raw SHA-256/canonical SHA-256, true marker first-parent, original Research authorization, Assembly frozen plan and binding, prompt/schema and final candidate.
- Fail closed for later rejected Research A, mismatched Research bytes, stale/overwritten/duplicate submission, foreign work/plan/marker, invalid/privacy-unsafe Research evidence, forged accepted receipt, invalid Assembly candidate, shifted group, forged Deep readiness and unauthorized retry.
- Prove invalid A cannot become canonical/Deep-ready while valid B/C remain independently checkable after GitHub lag; no per-item acceptance may bypass the **original strict atomic 3-game final group** boundary. Keep current one-stage production validator unchanged.
- Explicitly report whether this is **offline chain validation only** or whether any live GitHub final-ingest/writer integration exists. If absent, document the exact missing interface for separate authorization; **do not implement/activate it** under this task.
- Add independent test + PR-only CI as justified, preferably `scripts/test_dossier_two_stage_eventual_chain_qa.py` and `.github/workflows/validate-dossier-async-chain-acceptance-qa.yml`; run relevant existing regressions. Correct only bounded new offline QA scaffolding; report, do not silently change shared or production strict authority.

## Parallel isolation
ЧАТ 1 owns Research→Assembly **helper interoperability** (`WORKER_TASK_DOSSIER_ASYNC_END_TO_END_COMPATIBILITY_01.md`). Do not change their helper implementations, owned E2E test/workflow/report, or shared control-plane contracts.

## Deliverables
One focused branch and PR against `main`, green offline CI, report `reviews/worker_reports/dossier-async-github-chain-acceptance-qa-01.md` with negative cases, actual strict group and integration findings, exact tests/PR and nonactivation statement. **Do not merge your own PR.**

No live semantic execution, synthetic production data, canonical cache modification, Deep/Fast/ranking/UI/translation/Steam changes, Scheduled Tasks or automations, secrets, `manual-shell-write.yml`, or other repositories.
