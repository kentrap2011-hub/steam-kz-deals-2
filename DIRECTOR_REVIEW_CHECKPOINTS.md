# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: true
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 0
last_system_audit_report: `none`

### First trigger condition

The first trigger has been satisfied:
- `taste-runtime-trigger-status-01` now has a saved report and Director decision (direct continuation is needed because exact cadence/manual trigger remain unverified);
- `giveaway-igdb-implement-prep-01` reached its durable blocker on Twitch/IGDB credentials, and the IGDB route is now fallback while an alternative identity route is investigated.

Run the first System Audit before assigning the next ordinary backlog implementation unless the user explicitly prioritizes a more urgent time-sensitive incident/task. Existing direct continuations already in progress may finish first.

### Recurring triggers

Also set `system_audit_due: true` when:
- 3 material production IMPLEMENT/ACCEPTANCE changes have closed since the last audit;
- a user-visible missing/incorrect game/giveaway/ranking or unobserved automatic-process incident has been stabilized;
- a new queue/scheduler/provider/identity authority/ranking gate/semantic runtime/ownership boundary has been accepted.

A completed audit resets `material_changes_since_last_system_audit` to 0 and records its report.

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