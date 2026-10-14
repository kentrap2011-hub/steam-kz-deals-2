# ЧАТ 2 — легализовать существующий ручной одноразовый запуск Progressive Deep

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: progressive-deep-manual-one-shot-authorization-01
Worker: NEW physical ЧАТ 2 (prior Dossier report-only task has ended)
Mode: bounded IMPLEMENT, isolated PR, no self-merge
Worker report: reviews/worker_reports/progressive-deep-manual-one-shot-authorization-01.md

## User-approved scope
2026-10-14: user explicitly authorized manual one-shot Deep operation and reported manual Deep has been the only working invocation method for weeks. This is authorization to codify the EXISTING semantic Deep invocation surface, not to execute Deep right now or introduce a new data-plane, scheduled job, automation, retry owner, or processing queue. Do not assume the external scheduled task's current UI configuration has been independently verified.

## START
Fully read latest CHAT_PROTOCOL.md from main and execute START gate, then CHAT_CONTEXT.md, relevant PROJECT_ROUTES.md, config/execution_ownership_contract.json, config/progressive_pass2_contract.json, full config/progressive_pass2_worker_prompt.md, and appropriate ownership validation scripts/tests. Work ONLY in named repository; switch if tools open another. Consult other worker reports only if narrowly relevant; do not touch in-flight Deep UI or Dossier tasks.

## Implementation
1. Add an explicit `progressive_deep_one_shot` exception to `config/execution_ownership_contract.json#explicit_manual_semantic_worker_chats` (as appropriate to existing schema): user initiates EACH invocation; same canonical `config/progressive_pass2_worker_prompt.md` and `config/progressive_pass2_contract.json`; same existing GitHub control plane, exact prepared work scope/order/immutable profile and Dossier identity, result/terminal paths, create-only transport, confirmation, persistence and attempt/recovery/completeness accounting. No manual creation of scope, retry or recovery authority. Normal interactive developer session is NOT thereby authorized as a general backlog worker.
2. Align contradictory Deep ownership text in `config/progressive_pass2_contract.json` and only any other exact contract that requires it: ordinary interactive chat stays development-only, **explicitly user-launched isolated one-shot manual Deep** becomes allowed. Preserve `implemented=true`, `active=true`, `production_active`, existing run-start V2 marker → ACTUAL GitHub Git-parent frozen invocation authority → confirmed GitHub receipt BEFORE first result/terminal transport, liveness/expiry at pinned boundary, recovery/migration/score-evidence behavior, no Fast prerequisite, exact queue, and eventual two-stage plans.
3. Create one compact canonical copyable `config/progressive_pass2_manual_one_shot_prompt.md` that directs each manually launched worker to read latest CHAT_PROTOCOL.md/START + CHAT_CONTEXT.md and full GitHub worker prompt, PASS2 and ownership contracts, then follow existing marker/freeze/confirm/result logic exactly. It must NOT instruct per-item re-reading of mutable `main` after freeze. Each invocation stops when frozen work is empty or budget unsafe, and reports submitted vs GitHub-accepted honestly. Do not duplicate the long canonical worker rules into launcher. Require fresh explicit user invocation each time; no Scheduled Tasks.
4. Add or adjust focused validation verifying cross-contract consistency, both launcher and unchanged existing V2 marker/receipt boundaries, plus no unintended change to existing manual Russian-description worker. Run relevant isolated regressions and GitHub Actions PR checks. Version contracts as appropriate; keep existing site/UI/producer unaffected.

## Hard boundaries
No Scheduled Task or automation creation, modification, enable/disable, deletion, or user-setting action. No Deep semantic execution in this developer chat; no active `data/production/**`, `data/cache/**`, `data/ai_inbox/**`, `data/control/**` writes; no Dossier, Fast, rank, recovery, queue, ingest, manifest, visual or two-stage Deep cutover modifications. Do not edit `web/**`, `config/progressive_personalization_contract.json`, `scripts/progressive_personalization.py`, `CURRENT_TASK.md`, or original Dossier shadow reporter's files: open UI PR #224 and Dossier report PR #225 are separate.

## Completion
Create an isolated PR and compact worker report at the required path with exact modified contracts, PR checks, unresolved issues and a single Director acceptance step. Do not self-merge. Do NOT manually invoke the semantic worker. Stop after reporting.
