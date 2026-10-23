# ЧАТ 1 — короткий маршрут директора и защита правил от устаревания

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: director-typed-fastpath-anti-aging-implement-01
Worker slot: ЧАТ 1 (НОВЫЙ физический чат; прежний ЧАТ 1 завершил работу)
Mode: limited IMPLEMENT + own report + draft PR; no merge

## START and basis

Follow current CHAT_PROTOCOL.md START gate and *bounded* architecture preflight. Confirm this registered assignment in current main file, registry and top Board entry; don't scan historical Board or unrelated source. Read only relevant DIRECTOR_PROTOCOL.md passages and worker reports:
- PR #248 (Chat 5): reviews/worker_reports/director-role-context-regression-diagnosis-01.md
- PR #251 (Chat 6): reviews/worker_reports/director-audits-followthrough-action-plan-01.md
- PR #253 (Chat 7): reviews/worker_reports/director-governance-aging-resilience-review-01.md
PR #241 previous accepted governance changes are baseline, not wholesale review subject.

## Strict user decision

User explicitly approved **small DIRECTOR_PROTOCOL.md change** and **rejected new GitHub CI/Actions/validators** for director governance, due to concern about Dossier and Deep workflow overhead. No new automated or recurring check, no expansion of any existing validation, no modification of Dossier/Deep/Research/Assembly or production. Existing repo-required GitHub checks must not be disabled or bypassed.

## Objective

Edit **only** DIRECTOR_PROTOCOL.md (plus own report path reviews/worker_reports/director-typed-fastpath-anti-aging-implement-01.md); make director governance robust against future rule accumulation:
1. Near top (target within first 120 lines), one short typed decision map: `STATUS` («Проверь ЧАТ N»), `DECIDE` («Что дальше?»), `REGISTER` («Назначь задачу»), `MERGE` («Принимай PR»). Define minimal sufficient evidence and explicit stop-condition for each. When evidence missing, report UNKNOWN / BLOCKED and ask worker to investigate; never run worker-level code audit just for STATUS.
2. Keep established START, task identity/authority, current Board/registry source-of-truth, registration-before-dispatch, exact PR/CI and independent exact-HEAD QA/fail-closed merge unchanged. Current top Board + *addressed record* allowed; don't require full Board/registry reads for STATUS.
3. Add **one compact anti-aging governance-change review rule**: any future proposal that increases director obligations must identify canonical owner, what requirement is replaced/retired (or why a truly new risk requires an additive change), the delta in mandatory operational reading and why targeted retrieval is insufficient, plus one status/unsafe-merge walkthrough before acceptance. This is a HUMAN worker QA/reviewer procedure during future requested changes, not a new standing Director task or automatic GitHub check.
4. Preserve concise human communication: observations do not automatically become defects or work orders, proposals need user authorization; Director never self-expands user scope or performs worker technical implementation.
5. Replace/deduplicate overlapping normative clauses where possible rather than stacking new ones. Target <=45 net new lines and visible typed map in first 120 lines; if strict numbers conflict with preserved safety, justify smallest necessary exception rather than compromise authority.
6. Offer in final report 4 actual route walkthroughs + stale handoff and unsafe PR / change-aging scenarios. Distinguish static text assertions vs unprovable model behavior. Do not claim permanent prevention.

## Scope / deliverables

Only changes: DIRECTOR_PROTOCOL.md and reviews/worker_reports/director-typed-fastpath-anti-aging-implement-01.md. One small draft PR; exact final HEAD, changed-file list, comparison to Chat 6/7 six acceptance points; existing CI status if triggered. NO code, workflows, new CI/validator/scripts/tests, scheduled tasks, board/registry/task re-registration, handoff/bootstrap edits, GitHub settings, automation, live V2, Dossier, Deep or site modifications. Do not merge. Independent ЧАТ 2 is separately registered for follow-up QA, not to be run by you.
