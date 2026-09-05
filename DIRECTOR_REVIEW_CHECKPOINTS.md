# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: false
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 0
last_system_audit_report: `reviews/system_audits/director-orchestration-phase1-audit-01.md`
mobile_post_incident_audit_pending: false

### Recurring triggers

Set `system_audit_due: true` when:
- 3 material production IMPLEMENT/ACCEPTANCE changes have closed since the last audit;
- a user-visible missing/incorrect game/giveaway/ranking or unobserved automatic-process incident has been stabilized;
- a new queue/scheduler/provider/identity authority/ranking gate/semantic runtime/ownership boundary has been accepted.

A completed audit resets `material_changes_since_last_system_audit` to 0 and records its report.

### Current audit state

Latest completed audit:
- report: `reviews/system_audits/director-orchestration-phase1-audit-01.md`;
- status: `complete`;
- selected systemic closure: `accepted`;
- Phase 1 shadow orchestration is safe to use as the foundation for a separately gated Phase 2;
- Phase 1 remains shadow-only and is not authorized to dispatch real workers, call OpenAI/Codex, mutate product state, or gain write authority.

No System Audit is currently due.

## Taste Reviewer

taste_reviewer_chat_established: true
taste_baseline_review_due: false
last_taste_review_report: `reviews/taste_reviews/baseline-01.md`

### Current Taste implementation sequence

Internal ordered sequence:
1. evidence state / confidence / reconsideration semantics — technically complete;
2. play role + relative start priority — next;
3. reconsideration commercial bridge + wishlist-good-deal override — later.

The current plan is to keep these as one bounded internal sequence and run one independent current Taste Review after step 3 and regenerated controls, before final material acceptance. If any step is accepted/deployed independently as a completed material Taste boundary, a current Taste Review is required before that acceptance.

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
