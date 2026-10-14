# ЧАТ 1 — исторические Deep-разборы на сайте: карточки и статистика

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: deep-history-site-cards-stats-01
Worker slot: НОВЫЙ физический ЧАТ 1
Mode: IMPLEMENT, one bounded isolated PR, no self-merge
Report: reviews/worker_reports/deep-history-site-cards-stats-01.md

## START and authoritative baseline
Before any task-specific work, read current main CHAT_PROTOCOL.md fully and execute START, then CHAT_CONTEXT.md, CURRENT_TASK.md, relevant Progressive/site publication PROJECT_ROUTES.md, config/execution_ownership_contract.json, config/progressive_personalization_contract.json and accepted Deep history contract in config/progressive_pass2_contract.json. Previous source implementation is already MERGED: PR #222 merge d273e707fa00087fe2d36d1383cb39431c0747c0; inspect its two worker reports only as needed. Previous Deep site-mirror task `WORKER_TASK_DEEP_SITE_MIRROR_UI_STATISTICS_IMPLEMENT_01.md` is historically complete and NOT this new version-history feature. Work only in kentrap2011-hub/steam-kz-deals-2. If precise Git source commit metadata is strictly required to prove a profile-version date, bounded READ-ONLY access is expressly allowed to kentrap2011-hub/stopgame-ratings-data for pinned `gaming_taste_live.json` commit metadata ONLY; never write there. If tools default to any other repository, stop and switch.

## Goal / user-approved visible behavior
The new Deep producer history is merged but prior completed analyses can remain invisible in current website cards and Statistics after any profile-content change. Make completed historic work visible without treating old scores as current.

1. Every exact current-scope game card with a canonically accepted Deep completion in current V1 history, legacy V2 root or legacy revision_history must show the **LAST successfully completed Deep** even if its profile is old or its current Deep authority is now incompatible. Show original verdict, retained available explanation/evidence, **actual accepted Deep date**, label `Устаревший разбор` when outdated, otherwise `Актуальный разбор`. Never substitute an incomplete/failed result for a prior successful completion. If never successful, say so clearly. No guessed historical verdict/evidence.
2. Show the date of the **latest current taste-profile content version** alongside the Deep analyzed date, and (where attested) the profile version/date belonging to the historical result. Source timestamps must be tied to proven Git metadata and exact pinned content/blob SHA, distinguishing same-content new commits from true content revision (punctuation counts). If Git-attested profile content-change date cannot be established, render an explicit neutral `Дата версии профиля неизвестна` instead of analysis/build/deploy time. Do not silently omit the date limitation from report.
3. Site Statistics must expose unique game counts by profile-content version and current-scope partition: current-compatible completed, outdated/history-only completed, and never completed; include current target and current remaining. Avoid overlapping legacy 30+43 migration double-count. Keep date/freshness semantics consistent across cards and Statistics and explain to ordinary users.
4. **Strict score separation:** a stale historical Deep may be displayed for reading but cannot silently become current authoritative Deep rating, score, recommendation, ranking or override provisional up-to-date result. Browser only presents producer-owned fields; no new browser-side semantic calculations. Preserve Fast/Dossier three-stage truth, existing site status and publication freshness/quarantine behavior.
5. Preserve exact identity/edition matching and all existing app UI states. No fabricated completed versions from historical Git commits absent canonical state. Missing legacy restorations belong to a separately authorized evidence-backed migration, not automatic replay.

## Scope and architecture
Inspect only minimal relevant `scripts/progressive_personalization.py`, visual payload publication path, `web/index.html` and associated existing site JS/CSS for cards/statistics, existing tests/contracts. If necessary, make a bounded producer projection/pin-provenance change with correct contract versioning and isolated validation; do not move runtime ownership or introduce another web API/scheduler. Do not edit GitHub canonical Deep/Dossier/Fast states, manifests, live visual payload by hand; do not run semantic analyses, mass rerun, amend attempt/recovery or order, trigger Dossier research, change Scheduled Tasks, Fast scoring, ranking or two-stage Deep cutover. The independent icon task is COMPLETE and user confirmed the new gamepad visible on Android; do not change the favicon/icon/PWA files.

## Required tests and acceptance
- Distinct-current vs outdated vs never-completed UI; old successful followed by incomplete, exact different game/edition, duplicated accepted revisions, real result fields and null dates.
- Profile punctuation revision vs byte-identical commit; Git-proven dates where possible, otherwise explicit unknown.
- Versioned per-profile counts, current/old/never partition arithmetic, overlapping legacy migration dedup; old Deep must not enter ranking.
- Existing UI, site-task, Deep-PASS2, visual publication regressions as relevant; PR CI and self-contained screenshot/browser proof when available. Do not claim page deployed/visible before Director merges and Pages deploy verified.
- Create branch/PR and compact report at exact path. Include changed-file scope, tests/run IDs, evidence and known gaps, single Director next step. DO NOT MERGE; stop.

If a provenance gate cannot be closed under canonical ownership, implement only safely proven display/data portions, report a truthful bounded blocker and leave unsupported profile dates explicitly unknown; do not broaden into unapproved pipeline migration.
