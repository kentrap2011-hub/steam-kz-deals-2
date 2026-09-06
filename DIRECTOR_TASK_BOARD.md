# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.

## Review checkpoint
- Latest System Audit: `reviews/system_audits/director-orchestration-phase2a-audit-01.md` — accepted.
- `system_audit_due: false` now.
- `material_changes_since_last_system_audit: 1`.
- `taste_baseline_review_due: false`.
- latest Taste Review: `reviews/taste_reviews/taste-steps-1-3-current-review-01.md` — `ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`.
- integrated post-backfill Taste production verification remains pending before claiming live materialization.

## Completed Chat 1
Task: `WORKER_TASK_TASTE_STEPS_1_3_CURRENT_REVIEW_01.md`
Report: `reviews/taste_reviews/taste-steps-1-3-current-review-01.md`
Status: `ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`.
No blocking Taste findings. Steps 1–3 semantic boundary is accepted. The chat may be deleted.

## Next Chat 1
Task: `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`
Mode: `IMPLEMENT`
Expected report: `reviews/worker_reports/giveaway-itad-identity-implement-01.md`
Status: `ready_fresh_chat_1`.
Reason: direct continuation of the user's high-priority giveaway correctness path; independent of orchestration provider pilot.

## Completed Chat 2
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_01.md`
Report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-01.md`
Status: `blocked` before dispatch.
Reason: the exact semantic report path `reviews/worker_reports/epic-ru-availability-source-probe-01.md` already existed as immutable historical Phase 2B blocked-closeout evidence. Copilot CLI was not executed, no quota/auth conclusion was reached, and no provider boundary changed. This chat may be deleted.

## Next Chat 2
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_02.md`
Mode: `IMPLEMENT`
Expected report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`
Status: `ready_fresh_chat_2`.
Exact representative task: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md`.
Expected automatic semantic report: `reviews/worker_reports/epic-ru-availability-source-probe-02.md`.
Hard gates: zero extra payment; built-in GitHub/Copilot entitlement path only; one READ_ONLY_RECON pilot only; no second dispatch; no autonomous IMPLEMENT; no paid fallback; fail closed on unavailable entitlement/quota/auth.

## Stopped route
The separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Other queued
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence.

## Next decision
1. Fresh Chat 1 runs giveaway ITAD identity implementation.
2. Fresh Chat 2 runs Copilot CLI zero-cost live pilot revision 02.
3. Consume exact reports independently.
4. If Copilot revision 02 succeeds, set System Audit due before accepting/generalizing the new provider boundary.
