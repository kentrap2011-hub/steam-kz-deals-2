# WORKER TASK — inactive Dossier GitHub final acceptance and group writer integration 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth / base: `main`
Task ID: `dossier-async-github-final-integration-01`
Physical developer slot: **НОВЫЙ ЧАТ — ЧАТ 2**
Mode: **IMPLEMENT INACTIVE GITHUB-OWNED INTEGRATION / OFFLINE TEST / PR-ONLY**

## Scope and why it is needed

PR #185 confirmed that the existing fully async `Research → Assembly` inspector can validate individual items but does **not** connect them to an actual GitHub-owned final three-game group assembler/ingest/shared canonical writer. PR #184 confirms the semantic-stage helpers interoperate in disposable Git. Both QA PRs are merged. Implement the **inactive, non-authoritative** adapter/consumer that would later allow GitHub—not ChatGPT—to validate individual exact submitted chains and atomically finalize their original strict ordered three-game Dossier group, with no activation.

This is **not** authorization to turn on a workflow, schedule a task, publish canonical Dossiers, change Deep eligibility, or process real games now.

## START and owner preflight

1. Read current `CHAT_PROTOCOL.md` and execute START gate. Read `CHAT_CONTEXT.md`, this task and findings in `reviews/worker_reports/dossier-async-github-chain-acceptance-qa-01.md` fully from latest `main`. Work in this repo only; if another repository is selected, stop/correct.
2. Read only relevant `PROJECT_ROUTES.md` route, `config/execution_ownership_contract.json`, `config/dossier_two_stage_interfaces_contract.json`, `config/dossier_two_stage_staging_contract.json`, `config/dossier_two_stage_async_buffer_contract.json`, `scripts/dossier_two_stage_async_buffer.py`, `scripts/taste_steam_review_dossier_buffered.py` and current strict group acceptance/ingest ownership contracts. Preserve their authority.
3. Before writes, establish the exact existing GitHub-owned **shared writer domain**, locking, immutable source and canonical acceptance APIs. Reuse existing paths, strict validators, idempotence and provenance rules. If ownership or inactive interface is ambiguous, stop at a documented blocker; do not invent a second final writer, scheduler, queue, retry manager, or path.

## Required inactive integration

- Add a separately gated, **offline executable-in-tests only** GitHub control-plane adapter for eventual strict chain verification of exact preauthorized Research and Assembly **Git-submitted** bytes (commit/path/blob/raw SHA/canonical SHA/marker ancestry/plan/source/prompt/hash). Nothing is accepted just because the semantic worker marked it ready or a GitHub receipt is claimed.
- Each item receives a **typed, stable local inspection disposition** (valid-and-pending-original-group, missing/not-yet-submitted, invalid/quarantined, non-ready semantic gap, etc.) with no guessed retry, zero false acceptance, and no blocking of independently authorized siblings.
- Assemble **only the exact original ordered complete three-game group** when all three items satisfy strict chain and V2 item requirements. Pass it to the **existing** strict `validate_buffer_artifact` / final acceptance architecture. Group cannot be partially accepted; one invalid game prevents that group's canonical acceptance, **not** unrelated groups' processing or semantic liveness.
- Use existing GitHub-owned lock / atomic transaction / canonical writer semantics **only through a clearly inactive isolated interface**. Prevent double-commit, replay, duplicate path, stale snapshot and half-published states; model idempotent recovery only from GitHub-authorized receipts. Do not create a parallel canonical cache or bypass existing group writer.
- Show both negative and positive disposable-Git offline tests: Research A unaccepted while Assembly A submitted; three valid exact chains form one strict ready group; one bad item blocks only its original group's atomic acceptance; independently valid next group proceeds; tampered/stale Research or Assembly, forged receipt, altered marker/plan, retry/replay, missing item, race/collision and incorrect original ordering fail closed; current one-stage Dossier and Deep readiness remain unchanged. Include no real production data.
- Build a **PR-only** validation workflow and tests. All new execution entry points must fail closed when `active=false` / `authorized_for_canonical_ingest=false`, and offline testing must be explicitly separated from any live GitHub Actions production workflow. No new production workflow trigger, shared writer mutation, existing pipeline activation or Scheduled Task change.
- The separate PR #185 **Research original release-year contradiction** is assigned to ЧАТ 1. Do **not** edit P1 `validate_research` or its tests. Define this fix as a required cross-PR acceptance prerequisite: never declare the integrated bridge safe while that known XFAIL is unresolved. Fail closed rather than paper over it, and include a joint retest dependency in your report.

## Parallel ownership and escalation

ЧАТ 1 owns Research original-year validation only (`WORKER_TASK_DOSSIER_RESEARCH_ORIGINAL_YEAR_BINDING_FIX_01.md`). You own the **new inactive GitHub final-acceptance integration adapter**, distinct test/PR-only workflow/report and its isolated interface. Do not edit Research validator, stage worker prompts, Research worker helpers, or ЧАТ 1 files. Shared strict final validator, canonical cache, production writer and active workflow modifications are explicitly **out of scope** unless the only safe outcome is to stop and report a follow-up for Director authorization. Do not merge speculative code that invents bypasses.

## Deliverables and stop

Focused branch and PR (not merged by worker), report `reviews/worker_reports/dossier-async-github-final-acceptance-integration-01.md`, documented strict acceptance transition diagram or contract, isolated positive/negative Git test evidence, exact existing writer/lock handoff and remaining activation blockers, especially ЧАТ 1's Research-year correction and future real-evidence parity/shadow quality.

No real semantic execution, live source fetch, production commit/ingest, migration, Deep/Fast/ranking/UI/Steam/translation changes, Scheduled Tasks/automations, secrets, other repos or `manual-shell-write.yml`. Future actual activation/cutover requires **separate explicit user authorization**.
