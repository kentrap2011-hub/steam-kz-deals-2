# WORKER TASK — Dossier async Research → Assembly compatibility QA 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth / base: `main`
Task ID: `dossier-async-e2e-qa`
Physical worker: **НОВЫЙ ЧАТ — ЧАТ 1**
Mode: **INACTIVE; OFFLINE E2E COMPATIBILITY TESTS; PR-ONLY**

## Objective
On the current merged `main`, test whether Research helper (PR #181) and Assembly helper (PR #182) actually interoperate against the fully async preauthorization contract (PR #179). All three PRs are already merged. This is **not** live semantic execution or activation.

## START and canonical authority
Read current `CHAT_PROTOCOL.md`, execute START gate, then read `CHAT_CONTEXT.md` and this task **fully** from current `main`. Stay strictly within `kentrap2011-hub/steam-kz-deals-2`; correct a wrong GitHub repo before any action.

Read only relevant `PROJECT_ROUTES.md` sections and current:
- `config/execution_ownership_contract.json`
- `config/dossier_two_stage_interfaces_contract.json`
- `config/dossier_two_stage_staging_contract.json`
- `config/dossier_two_stage_async_buffer_contract.json`
- `scripts/dossier_two_stage_research_worker.py`
- `scripts/dossier_two_stage_assembly_semantic_worker.py`
- `scripts/dossier_two_stage_async_buffer.py`
- exact Research package / async Assembly candidate schemas and existing tests.

GitHub owns frozen scope, order, binding, provenance, retry, eventual acceptance and original atomic 3-game Dossier ingestion. Neither semantic worker may independently select/retry games, write canonical Dossier, create a scheduler or wait for another item's GitHub acknowledgment.

## Bounded acceptance proof
- Build **disposable local Git fixtures**, never write test games/results into the actual production `data/` paths.
- Use the **actual merged APIs of both workers**, not just two isolated passing suites: frozen GitHub Research authorization → exact Research package/immutable original Git transport → frozen Assembly authorization → Assembly candidate referencing precisely those submitted bytes **before** GitHub Research acceptance.
- Validate exact marker parent, original work/plan blob, item/group order, Research commit/path/Git blob/raw and canonical SHA-256, prompt/schema bindings, immutable output names and future validator identity.
- Show 12+ items/four three-game groups do not hit the former eight-open-slot cap; Research A and Assembly A require **no** previous GitHub receipt, and B/C continue if A is missing, invalid, stale, duplicate or late-rejected. Missing Research is a local zero-attempt case, not a request for self-issued retry.
- Fail closed for wrong item, reordering, tamper, duplicate create-only destination, moving-main rebinding, unapproved new work, forged acceptance. Retain existing one-stage production behavior and inactive flags.
- When actual helper interfaces cannot interoperate, implement only a minimal **inactive test/helper interoperability fix** within your owned area. If correction requires shared control-plane contracts, production paths, runtime writers or canonical validators, stop and report a separate precise follow-up task instead of expanding scope.

## Parallel isolation
ЧАТ 2 owns independent **GitHub eventual-chain acceptance QA** (`WORKER_TASK_DOSSIER_ASYNC_GITHUB_CHAIN_ACCEPTANCE_QA_01.md`). Do not edit Chat 2's task, tests, workflow or report, final chain checker, shared staging contracts or task plan. Prefer new files `scripts/test_dossier_two_stage_end_to_end_compatibility.py`, `.github/workflows/validate-dossier-async-end-to-end-compatibility.yml`.

## Deliverables
One focused implementation branch and PR, offline green CI with Research/Assembly + existing relevant regressions, report `reviews/worker_reports/dossier-async-end-to-end-compatibility-01.md` including exact test outcomes, PR link, risks and remaining activation blockers. **Do not merge your own PR.**

No real semantic game runs, no production inbox/cache/queue modification or invented data, no live/shadow activation, no Scheduled Tasks/automations, secrets, `manual-shell-write.yml`, other repositories, or changes to Deep/Fast/ranking/site/translation.
