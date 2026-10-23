# ЧАТ 4 — Pages deployed bytes and freshness after PR #238
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: pages-live-publication-readback-audit-01
Worker slot: ЧАТ 4
Mode: READ-ONLY / RECON: separate report-only draft PR
Report: reviews/worker_reports/pages-live-publication-readback-audit-01.md

## Obligatory start, authority and scope
Fully read current main CHAT_PROTOCOL.md and CHAT_CONTEXT.md; execute START gate, relevant PROJECT_ROUTES.md, DIRECTOR_PROTOCOL.md and architecture preflight. Read this exact task file from main and verify matching entries in config/director_task_plan.json and DIRECTOR_TASK_BOARD.md, including successful registration CI, before work. Use ONLY repository kentrap2011-hub/steam-kz-deals-2. Never search, inspect or modify other repositories; if a tool opens another repo, STOP and switch back. Do not treat this text alone as registration authority. Save a concise worker report, with exact GitHub refs/CI, confirmed/unknown facts, changes, validation, unresolved, final status and one recommended next step.

## Task
1. Compare exact main source, canonical data/production/visual/current.json blob and freshness receipts, GitHub Actions Build daily visual payload and Deploy visual mailing run/artifact chronology after merged PR #238 (bb0d8bb7426c0e0afd277f7a3d7f5c808c2ca981). Distinguish failed/skipped/success from real Pages release.
2. Locate actual Pages URL through grounded repository configuration/deployment evidence, then READ ONLY retrieve deployed browser code and web/data/current.json/status/giveaways/tasks where accessible. Compare verified byte hashes, source commits, timestamps, number/IDs of offers, actual KZT prices/discounts/end dates, expired-offer behavior and Fast/Deep/statistics freshness. Keep producer freshness vs build freshness vs deploy freshness vs browser cache separate. If byte readback denied, mark UNVERIFIED, do not guess.
3. Use historical report-only PR #236 and accepted code PR #238 for context; do not reimplement old fixes. Find first verified divergence and recommended separate authorization for real Deploy/QA (or bounded fix only on evidence). Critical core binding, price/material, hashes and receipts always fail closed; optional-section fix cannot relax that boundary.

## Prohibitions / acceptance
No workflow_dispatch, deploy, production data, semantic work, Schedule Tasks, PR merges or changes outside distinct report file. CURRENT_TASK.md must not erase other work. One report-only draft PR and concise evidence-based report including exact run/commit/hash refs, unknowns, next Director decision. A merged source PR does NOT count as live publication.
