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
- `taste_integrated_production_verification_pending: true`.
- current Taste blocker: canonical semantic runtime not advancing current V5 scope.

## Completed Chat 1 — Taste production materialization acceptance
Task: `WORKER_TASK_TASTE_STEPS_1_3_PRODUCTION_MATERIALIZATION_ACCEPTANCE_01.md`
Report: `reviews/worker_reports/taste-steps-1-3-production-materialization-acceptance-01.md`
Status: `blocked_semantic_runtime`.

Accepted high-level outcome from durable report:
- remaining Taste Reviewer maintenance recommendations are implemented and regression-covered;
- current V5 semantic scope is `701` unresolved / `0` resolved;
- publication completeness is false;
- old visual output is explicitly rejected as Steps 1–3 acceptance evidence;
- no second semantic scheduler, parallel queue or manual bulk semantic processing was introduced;
- HighFleet deterministic confirmed-negative guard is green, but live semantic materialization is still pending;
- current site is **not** ready for user verification.

This implementation/acceptance chat may be deleted after Director consumes the report.

## Next Chat 1 — Taste semantic runtime recovery recon
Task: `WORKER_TASK_TASTE_SEMANTIC_RUNTIME_RECOVERY_RECON_01.md`
Mode: `READ-ONLY / RECON`
Expected report: `reviews/worker_reports/taste-semantic-runtime-recovery-recon-01.md`
Status: `ready_fresh_chat_1`.
Purpose: recover/identify the intended canonical scheduled semantic producer or define the smallest canonical zero-cost recovery path without creating a second scheduler. Stay on Taste.

## Chat 2 — zero-cost Copilot live pilot revision 02
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_02.md`
Mode: `IMPLEMENT`
Expected report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`
Status: `ready_fresh_chat_2` unless already created/running by user.
Representative task: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md`.
Expected semantic report: `reviews/worker_reports/epic-ru-availability-source-probe-02.md`.
This infrastructure pilot is independent and may run in parallel. Its result may become relevant to a future canonical semantic-runtime migration only if the provider path is actually proven and accepted.

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
- semantic/Russian-description completion must use the existing canonical runtime or an explicitly accepted canonical migration; do not create another active scheduler.

## Next decision
1. Fresh Chat 1 runs semantic-runtime recovery recon and stays strictly on the Taste unblock path.
2. Chat 2 may independently continue the zero-cost Copilot pilot.
3. Do not ask the user to verify the site yet.
4. After the recovery recon, choose exactly one bounded restore/reconnect/migration/user-evidence action.
