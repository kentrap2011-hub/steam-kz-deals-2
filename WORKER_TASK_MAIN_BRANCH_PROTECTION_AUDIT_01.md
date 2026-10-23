# ЧАТ 3 — main branch protection audit
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: main-branch-protection-audit-01
Worker slot: ЧАТ 3
Mode: READ-ONLY / RECON: separate report-only draft PR
Report: reviews/worker_reports/main-branch-protection-audit-01.md

## Obligatory start, authority and scope
Fully read current main CHAT_PROTOCOL.md and CHAT_CONTEXT.md; execute START gate, relevant PROJECT_ROUTES.md, DIRECTOR_PROTOCOL.md and architecture preflight. Read this exact task file from main and verify matching entries in config/director_task_plan.json and DIRECTOR_TASK_BOARD.md, including successful registration CI, before work. Use ONLY repository kentrap2011-hub/steam-kz-deals-2. Never search, inspect or modify other repositories; if a tool opens another repo, STOP and switch back. Do not treat this text alone as registration authority. Save a concise worker report, with exact GitHub refs/CI, confirmed/unknown facts, changes, validation, unresolved, final status and one recommended next step.

## Task
1. Verify fresh main protected flag, repository/org rulesets and GitHub permission limits. Earlier verified protected=false and [] rulesets; recheck. Audit exact required candidate workflows/status checks on PR #239, #238, #241 and current representative PR; separate skipped/not-triggered checks from successful checks.
2. Produce practical administrator-only activation plan: status checks safe on *all* PR paths, independent approvals/re-review after HEAD changes, direct push/force/delete protection, bot nightly production updates, bypass/emergency recovery avoiding repo lockout. Distinguish controls actually available to this repo and connector from unverified ones; list manual UI/API settings or prerequisites only if evidenced.
3. No new workflow edits or GitHub branch/ruleset settings writes, no admin actions, no deploy/semantics/merge. Only one report Markdown in its own draft PR. CURRENT_TASK.md must not overwrite other current handoffs.

## Acceptance and next
Deliver current facts, evidence and viable minimum configuration with administrator dependencies, exact scope and constraints. Director/user separately decides whether to apply settings. Report-only QA may be bounded; do not claim protection enabled.
