# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: false
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 1
last_system_audit_report: `reviews/system_audits/director-orchestration-phase2a-audit-01.md`
mobile_post_incident_audit_pending: false

### Recurring triggers

Set `system_audit_due: true` when:
- 3 material production IMPLEMENT/ACCEPTANCE changes have closed since the last audit;
- a user-visible missing/incorrect game/giveaway/ranking or unobserved automatic-process incident has been stabilized;
- a new queue/scheduler/provider/identity authority/ranking gate/semantic runtime/ownership boundary has been accepted or is at its acceptance gate.

A completed audit resets `material_changes_since_last_system_audit` to 0 and records its report.

### Current audit state

Latest completed audit:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`
Status: `PASS`.
Closure: `accepted`.

The separately billed OpenAI API worker route is stopped by user cost policy.

Zero-cost recon:
`reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`
identified direct GitHub Copilot CLI in Actions using included Copilot entitlement as the preferred quota-bounded zero-additional-payment candidate.

First Copilot pilot task:
`reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-01.md`
closed `blocked` before dispatch because the immutable semantic report path already existed from historical Phase 2B evidence. No Copilot provider execution occurred, so this did not reach a provider acceptance gate and does not trigger System Audit.

A future successful real Copilot provider pilot must set `system_audit_due: true` before provider acceptance/general use.

## Taste Reviewer

taste_reviewer_chat_established: true
taste_baseline_review_due: false
last_taste_review_report: `reviews/taste_reviews/taste-steps-1-3-current-review-01.md`
taste_integrated_production_verification_pending: true

### Current Taste implementation sequence

1. evidence state / confidence / reconsideration semantics — technically complete;
2. play role + relative start priority — technically complete;
3. reconsideration commercial bridge + wishlist-good-deal override — technically complete;
4. independent current Taste Review — complete.

Independent review conclusion:
`ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`.

There are no blocking semantic findings in Steps 1–3. The combined semantic boundary is accepted.

Important observability limitation:
- current semantic production materialization remains degraded on unresolved semantic backfill;
- the persisted ranking lookup is stale pre-change output and must not be cited as proof of live post-Steps-1–3 ordering;
- after legitimate semantic completion, one bounded regenerated control snapshot remains pending before claiming the accepted semantics are materially visible in current production.

Taste Reviewer advisory recommendations remain advisory and are not automatically converted into product policy.

### Baseline controls

Key durable controls include:
- `Trine 4` family-play positive;
- `HighFleet` strong negative start-priority control for dry/technical felt burden;
- `Tails of Iron 2` secondary/palate-cleanser role;
- `High On Life` moderate full/main-game candidate;
- `Sifu` strong current pre-play interest;
- `Batman: Arkham` replay-positive anchor;
- `RDR2` primary open-world positive;
- context-sensitive interpretations for `directionlessness`, `unchanged_repetition`, `management_routine`, and `puzzle_pacing`.

### Mandatory recurring triggers

A Taste Review is required before acceptance of any material change to:
- Taste eligibility;
- personal-fit weights/scores;
- personal-fit ranking order;
- personal-preference exclusion thresholds;
- wishlist-vs-Taste priority semantics.

It is also due after a user reports a likely taste mismatch once commercial/data availability causes have been ruled out.

## Role refs

- `SYSTEM_AUDITOR_ROLE.md`
- `TASTE_REVIEWER_ROLE.md`
- canonical taste profile: `USER_TASTE_PROFILE.md`
