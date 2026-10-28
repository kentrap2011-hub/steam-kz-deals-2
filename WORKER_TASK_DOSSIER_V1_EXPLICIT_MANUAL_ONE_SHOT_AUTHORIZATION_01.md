# ЧАТ 7 — восстановить явный ручной одноразовый запуск обычного Dossier

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Task ID: `dossier-v1-explicit-manual-one-shot-authorization-01`
Worker: **НОВЫЙ физический ЧАТ 7**
Mode: bounded IMPLEMENT, one isolated PR for Director and independent L3 security acceptance; **no semantic execution**.
Worker report: `reviews/worker_reports/dossier-v1-explicit-manual-one-shot-authorization-01.md`

## START and observed issue

Read full current `CHAT_PROTOCOL.md`, execute START; read `CHAT_CONTEXT.md`, `PROJECT_ROUTES.md`, exact `config/execution_ownership_contract.json`, entire `config/taste_steam_review_dossier_runtime_prompt.md` and `config/taste_steam_review_dossier_worker_prompt.md`, original schema/evidence/terminal contracts and relevant ownership tests. Work ONLY in named repository.

A **user-explicitly launched** normal Dossier semantic chat stopped before creating a run-start marker because `execution_ownership_contract.json#explicit_manual_semantic_worker_chats` names Russian descriptions and Progressive Deep but not Dossier. Previous manual Dossier chats had run; repository history suggests this exception was never codified, not that a recent explicit prohibition was newly imposed. Preserve uncertainty about why past chats proceeded; do not retrofit historical authorizations.

## Single authorized implementation

1. Architecture/authority preflight: verify existing scheduled Dossier runtime, GitHub-owned exact group queue, one nonce-only run-start marker, GitHub Git-parent frozen authority, exact descriptor order/bindings, cache semantics, prepublication validation rules, create-only buffered/terminal transport, canonical validation/ingest and failed-group/recovery accounting. Identify any **actual** conflict between scheduled and user-launched invocations before enabling; do not assume manual launch is safe merely because Deep allows it.
2. Add a **narrow, separately user-initiated Dossier V1 one-shot exception** in the ownership contract; only an explicitly invoked isolated semantic worker may use the existing Dossier runtime. The normal interactive developer/operator remains barred from general backlog execution. Require one fresh user request per invocation. No recurring/manual scheduler, quota, retry or secondary queue. Scheduled Dossier stays unchanged and owns no new permissions; GitHub continues to select work and own results.
3. Create one **short canonical manual launcher** under `config/` referencing the current existing runtime, worker and schemas, with no duplicated semantic rules. Align only exact cross-contract wording where needed to remove true authority contradictions. Do not modify semantics, scope, rank, V2 pilot, production state, Scheduled Tasks, run-start marker format, group identity, recovery or data artifacts.
4. Provide targeted regression tests on explicit authorization, scheduled/manual parity, conflicting concurrent/stale invocation guardrails, frozen Git-parent authority, create-only paths, disabled unsupported modes and preserved Deep/Russian exception behavior. Don't trigger any real Dossier invocation or workflow dispatch as a test. Preserve the existing legitimate cache/receipt acceptance path.
5. Review impact on all existing ownership boundaries and any already-authorized role. Since this changes L3 execution authority, include clear **independent L3 QA required before merge** and any residual blocker; no self-acceptance.

## Exit

One implementation PR (not report-only) with focused tests and report `reviews/worker_reports/dossier-v1-explicit-manual-one-shot-authorization-01.md`. Leave PR open for Director and independent QA. No automatic activation, execution, semantic research, or task/scheduler changes. No second implementation or standalone QA PR unless Director separately registers and authorizes it. Result `READY_FOR_DIRECTOR_L3_QA` or `BLOCKED_AUTHORITY` with precise blocker and commit/CI refs.
