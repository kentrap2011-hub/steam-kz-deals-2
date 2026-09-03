# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: true
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 2
last_system_audit_report: `reviews/system_audits/baseline-01.md`

### First trigger condition

The first trigger has been satisfied and baseline audit completed.

### Recurring triggers

Set `system_audit_due: true` when:
- 3 material production IMPLEMENT/ACCEPTANCE changes have closed since the last audit;
- a user-visible missing/incorrect game/giveaway/ranking or unobserved automatic-process incident has been stabilized;
- a new queue/scheduler/provider/identity authority/ranking gate/semantic runtime/ownership boundary has been accepted.

A completed audit resets `material_changes_since_last_system_audit` to 0 and records its report.

Current post-audit material changes:
1. `semantic-runtime-completion-fix-01` completed.
2. `semantic-runtime-completion-acceptance-02` accepted the new runtime observability/completeness control and stabilized the Trine-class unobserved-semantic-processing incident.

The recurring trigger has therefore fired before the numerical count reaches 3: an unobserved automatic-process incident was stabilized and the semantic-runtime control boundary was accepted. Existing direct continuation `visual-freshness-chain-fix-01` may finish first, but do not assign ordinary backlog work before the next System Audit.

## Taste Reviewer

taste_reviewer_chat_established: false
taste_baseline_review_due: true
last_taste_review_report: `none`

### Baseline trigger

Establish a dedicated Taste Reviewer chat when convenient; it is advisory and must not modify production code.

Its first job is a baseline review of whether the current recommendation system is over-constrained or mis-prioritized for Dmitry's actual game taste.

This baseline does not need to pre-empt a time-sensitive incident, but it must occur before accepting a future material Taste/ranking-policy change.

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