# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: true
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 1
last_system_audit_report: `reviews/system_audits/director-orchestration-phase1-audit-01.md`
mobile_post_incident_audit_pending: false

### Recurring triggers

Set `system_audit_due: true` when:
- 3 material production IMPLEMENT/ACCEPTANCE changes have closed since the last audit;
- a user-visible missing/incorrect game/giveaway/ranking or unobserved automatic-process incident has been stabilized;
- a new queue/scheduler/provider/identity authority/ranking gate/semantic runtime/ownership boundary has been accepted or is at its acceptance gate.

A completed audit resets `material_changes_since_last_system_audit` to 0 and records its report.

### Current audit state

Phase 2A orchestration security/state boundary is technically complete but not yet systemically accepted.

Audit task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2A_SYSTEM_AUDIT_01.md`

Expected report:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`

Implementation under audit:
`reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`

Validated head:
`bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`

Do not enable Phase 2B live worker dispatch and do not provision `OPENAI_API_KEY` until this audit accepts the boundary.

Previous completed audit:
`reviews/system_audits/director-orchestration-phase1-audit-01.md`
closure accepted.

## Taste Reviewer

taste_reviewer_chat_established: true
taste_baseline_review_due: false
last_taste_review_report: `reviews/taste_reviews/baseline-01.md`

### Current Taste implementation sequence

Internal ordered sequence:
1. evidence state / confidence / reconsideration semantics — technically complete;
2. play role + relative start priority — technically complete;
3. reconsideration commercial bridge + wishlist-good-deal override — next.

The current plan is to keep steps 1–3 as one bounded internal sequence and run one independent current Taste Review after step 3 and regenerated controls, before final material acceptance.

`taste_baseline_review_due` remains false only because step 3 has not yet completed and no intermediate step is being independently accepted/deployed as a completed product semantic boundary.

After step 3 report exists, a current Taste Review becomes mandatory before final acceptance of the combined new semantics.

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

Reviewer recommendations remain advisory and must not be auto-converted into product policy.

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
