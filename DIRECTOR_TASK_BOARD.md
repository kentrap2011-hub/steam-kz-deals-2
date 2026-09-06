# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.
- Do not move a user-priority semantic change to unrelated backlog work before its required production/user-verification gate is reachable.

## Review checkpoint
- Latest System Audit: `reviews/system_audits/director-orchestration-phase2a-audit-01.md` — accepted.
- `system_audit_due: false` now.
- `material_changes_since_last_system_audit: 1`.
- `taste_baseline_review_due: false`.
- latest Taste Review: `reviews/taste_reviews/taste-steps-1-3-current-review-01.md` — `ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`.
- `taste_integrated_production_verification_pending: true` until canonical post-backfill output is regenerated and bounded controls are verified.

## Completed Taste Review
Task: `WORKER_TASK_TASTE_STEPS_1_3_CURRENT_REVIEW_01.md`
Report: `reviews/taste_reviews/taste-steps-1-3-current-review-01.md`
Status: `ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`.
No blocking semantic findings. Steps 1–3 semantic boundary is accepted, but current persisted production/ranking output is stale and not yet suitable for final user verification.

## Next Chat 1 — Taste production materialization acceptance
Task: `WORKER_TASK_TASTE_STEPS_1_3_PRODUCTION_MATERIALIZATION_ACCEPTANCE_01.md`
Mode: `IMPLEMENT / ACCEPTANCE`
Expected report: `reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`
Status: `ready_fresh_chat_1`.

Purpose:
- implement remaining Taste Reviewer maintenance recommendations for Batman/RDR2 positive-exception regressions and role/start calibration revalidation provenance;
- preserve the canonical semantic runtime; no second scheduler/manual bulk queue;
- close or honestly report the current semantic-runtime/materialization gate;
- regenerate only through the canonical production path once legitimately complete;
- run integrated ten-control acceptance including critical HighFleet behavior;
- reach `complete_ready_for_user_verification` only when current published output is demonstrably post-Steps-1–3.

Do not start ITAD/giveaway work in Chat 1 until this Taste production/user-verification gate is resolved.

## Chat 2 — zero-cost Copilot live pilot revision 02
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_02.md`
Mode: `IMPLEMENT`
Expected report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`
Status: `ready_fresh_chat_2` unless already created/running by user.
Representative task: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md`.
Expected semantic report: `reviews/worker_reports/epic-ru-availability-source-probe-02.md`.
This infrastructure pilot is independent of Taste and may run in parallel.

## Giveaway ITAD identity
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Expected report: `reviews/worker_reports/giveaway-itad-identity-implement-01.md`
Status: `queued_high_priority_after_taste_user_verification_gate`.
Not forgotten; intentionally postponed because the user wants Taste made actually checkable first.

## Stopped route
The separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Other queued
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion must use the existing canonical runtime; do not create another scheduler.

## Next decision
1. Chat 1 stays on Taste through production materialization and user-verification readiness.
2. Chat 2 may independently run Copilot CLI zero-cost pilot revision 02.
3. Consume exact reports independently.
4. Only after Taste report says `complete_ready_for_user_verification` ask the user to check the real site/mobile output.
