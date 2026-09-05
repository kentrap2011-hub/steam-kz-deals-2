# DIRECTOR TASK BOARD

## Current rules
- Keep two independent worker slots busy when safe.
- User will not pay extra for automation/inference.
- No autonomous IMPLEMENT without separate approval.

## Review checkpoint
- Latest System Audit: `reviews/system_audits/director-orchestration-phase2a-audit-01.md` — accepted.
- `system_audit_due: false` now.
- `taste_baseline_review_due: true` after Taste Step 3 completion.

## Completed Chat 1
Task: `WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md`
Report: `reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
Status: `complete`.
Chat 1 implementation slot is free. Final Taste acceptance still requires an independent review.

## Next Chat 1
Task: `WORKER_TASK_TASTE_STEPS_1_3_CURRENT_REVIEW_01.md`
Mode: `READ-ONLY / TASTE REVIEW`
Expected report: `reviews/taste_reviews/taste-steps-1-3-current-review-01.md`
Status: `ready_fresh_chat_1`.

## Completed Chat 2
Task: `WORKER_TASK_ZERO_INCREMENTAL_COST_DIRECTOR_AUTOMATION_RECON_01.md`
Report: `reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`
Status: `complete_recon_no_implementation`.
Conclusion: the preferred zero-additional-cost candidate is direct GitHub Copilot CLI in GitHub Actions using included Copilot allowance. It is quota-bounded, not guaranteed unlimited. Almost all Phase 2A/2B control/security machinery can be reused.
Chat 2 recon slot is free.

## Next Chat 2
Task: `WORKER_TASK_COPILOT_CLI_ZERO_COST_LIVE_READONLY_PILOT_01.md`
Mode: `IMPLEMENT`
Expected report: `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-01.md`
Status: `ready_fresh_chat_2`.
Exact representative task: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`.
Expected automatic semantic report: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`.
Hard gates: zero extra payment, one READ_ONLY_RECON pilot only, no second dispatch, no autonomous IMPLEMENT, fail closed if included allowance is unavailable.

## Stopped route
The separately billed OpenAI API automation route is stopped by user policy and must not be retried.

## Other queued
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence.

## Next decision
1. Fresh Chat 1 runs mandatory independent Taste Review.
2. Fresh Chat 2 runs bounded zero-cost Copilot CLI live read-only pilot.
3. Consume exact reports independently.
4. A successful new provider pilot triggers independent System Audit before general acceptance.
