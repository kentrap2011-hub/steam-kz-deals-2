# WORKER TASK — prospective Dossier shadow trial plan + site Deep count discrepancy QA 01

Repository: `kentrap2011-hub/steam-kz-deals-2`; base/source of truth: `main`.
Physical developer: **НОВЫЙ ЧАТ — ЧАТ 2**.
Task ID: `dossier-shadow-trial-plan-and-site-counts-01`.
Authorization: **bounded read-only diagnosis and inactive planning / offline tests / PR only**.

## Two distinct deliverables, one read-only worker; NO live semantic trial

**A. Prepare a specific prospective shadow quality plan**, using the already accepted **inactive** shadow-quality diagnostics of PR #191, its protocol `reviews/dossier_two_stage_shadow_trial_protocol.md` and current accepted one-stage Dossier. Produce a concrete pre-registration template: proposed diverse, non-cherry-picked sample-selection policy and proposed group/sample scale **clearly labelled recommendation, not authorization**; how GitHub freezes exact original groups and accepted one-stage counterpart/writer receipt, independent evidence auditors, measurable quality dimensions, material omission/source/year/privacy failures and planned review/stop/adjudication/rollback gates. Do not select or freeze actual live games, infer fake accepted baselines or invent threshold approval. Distinguish suggested numerical thresholds from **user-approved** ones; no user approval exists yet. Prepare an operator-ready plan for a *later separately authorized* real-evidence shadow run. No semantic worker invocation or active pipeline.

**B. Investigate the user's apparent live-site discrepancy: "8 games with deep analysis and 9 without, but statistics show 14 suitable".** This is a separate bounded **read-only** publication/UI diagnosis. Before reading implementation code, establish the different exact **denominators/scopes**. Director checked canonical producer on 2026-10-11 about 09:22 UTC:
- `data/production/site/current_status.json` `processing_status.deep_completed_fit_count=14`, `deep_completed_not_fit_count=6`, `deep_incomplete_or_recovery_count=2`, `deep_total_current_coverage_target=303`.
- GitHub `data/production/visual/current.json` at that moment had **297 cards**, among them **14** `deep_stage_state=completed` and `deep_stage_outcome=fit`, **2** `incomplete_or_recovery`, and **281** `not_analyzed`. Its `processing_status.analyzed_fit_count=14`.
- User visually counted **8** deep and **9** without in their displayed UI subset. It is **not established** that these 17 cards have the same scope as 14 global suitable Deep games. All 14 Deep-fit cards existed in the then-current **producer** payload; don't assume 6 were lost or claim a bug without evidence.
- Check, in bounded target paths only: latest producer's `processing_status` and Deep-derived card fields → final visual payload → deploy/web bundle route → browser filtering, saved local queue/view, "active/current/wishlist" selection, toggles and queue limits. Identify which metric is global vs which subset the user counted, whether Deep completed-but-not-fit is suppressed as designed, and whether any true stale/hidden/expiring/filtered Deep-fit cards contradict product behavior.
- Reproduce with PR-only deterministic test/fixture **if possible**; distinguish genuine producer/UI mismatch from expected subset behavior and user-local state that cannot be observed remotely. If local state/specific active filter is essential and cannot be inferred, report **exact screenshot/settings/local-state questions** rather than guessing. Provide concise explanation of `14` versus `8+9` and a six-item candidate-accounting appendix (which global Deep-fit cards are not in view, **only if evidence permits**).
- **No UI/production fix in this PR.** If confirmed defect, report separately authorized minimal correction/test task. The site question has no dependency on the shadow trial and must be reported as a separate section.

## START / file isolation

1. Read latest `CHAT_PROTOCOL.md` fully from `main`, execute START gate; read `CHAT_CONTEXT.md`, this task and only relevant `PROJECT_ROUTES.md` (Deep/site statistics and visual publication route, Dossier quality route), current accepted PR #191 report and protocol.
2. Operate **only** in `kentrap2011-hub/steam-kz-deals-2`. Read narrow relevant contracts/status, not broad repository history. For visual payload >1MB use immutable Git blob tooling, never assume `fetch_file` empty content means empty producer.
3. Do not alter any Research validator, final bridge/flag (ЧАТ 1 owns it), active Dossier/Deep/Fast/ranking, production `data/`, web filtering, canonical cache, publication workflow or scheduler. A read-only proof script/test is allowed only with disposable/synthetic fixtures.

## Deliverables
One focused branch and PR (**do not merge own PR**) with two separate reports:
- `reviews/worker_reports/dossier-shadow-trial-prospective-plan-01.md` — concrete future authorization-ready sampling/reviewer/evidence/stop plan, explicitly NOT executed.
- `reviews/worker_reports/site-deep-count-14-vs-ui-8-plus-9-diagnostic-01.md` — actual scope reconciliation, per-stage counts, evidence of any mismatch, recommended next decision; no speculative loss of data.

Optionally one supplementary inactive plan/spec and one isolated non-mutating test/CI for site counts; keep change surface modest. Existing PR #191 harness should be reused, not duplicated. Never run live semantic workers or future shadow sampling, never create/change Scheduled Tasks/automations, no production writes/activation/Deep Stage1 migration/Fast shutdown, no other repo or `manual-shell-write.yml`.
