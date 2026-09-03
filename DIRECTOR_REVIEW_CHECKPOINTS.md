# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: false
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 0
last_system_audit_report: `reviews/system_audits/system-audit-02.md`
mobile_post_incident_audit_pending: true

### First trigger condition

The first trigger has been satisfied and baseline audit completed.

### Recurring triggers

Set `system_audit_due: true` when:
- 3 material production IMPLEMENT/ACCEPTANCE changes have closed since the last audit;
- a user-visible missing/incorrect game/giveaway/ranking or unobserved automatic-process incident has been stabilized;
- a new queue/scheduler/provider/identity authority/ranking gate/semantic runtime/ownership boundary has been accepted.

A completed audit resets `material_changes_since_last_system_audit` to 0 and records its report.

### Current audit state

`System Audit 02` completed on 2026-09-03 and satisfied the previously due checkpoint.

Key dispositions from `reviews/system_audits/system-audit-02.md`:
- semantic execution heartbeat/observability: `closed`;
- semantic incompleteness visibility: `partially_closed` because canonical degraded truth is not yet visibly surfaced in the user-facing feed;
- visual stale-success: `partially_closed` because the accepted fix is not yet active on production `main`;
- legacy one-shot Taste writer ambiguity remains a bounded risk hypothesis;
- current mobile feed incident remains active and was not treated as stabilized/accepted by the audit.

Because the mobile incident was still active during this audit, set `system_audit_due: true` again after that incident is actually stabilized and user-accepted, unless a later audit has already covered the exact stabilized failure class. Until stabilization, `mobile_post_incident_audit_pending: true` is a reminder, not a current blocking due checkpoint.

## Taste Reviewer

taste_reviewer_chat_established: true
taste_baseline_review_due: false
last_taste_review_report: `reviews/taste_reviews/baseline-01.md`

### Baseline result

Baseline review completed. Current overall selection-pressure classification: `cannot_determine`, with evidence against both simplistic global interpretations (`too strict` or `too loose`). The strongest current concern is conditional/context loss: role, felt burden, optionality/density, and unknown-vs-negative treatment can be mis-modeled.

Key durable controls recorded by the reviewer include:
- `Trine 4` confirmed family-play positive;
- `HighFleet` strong negative start-priority control for dry/technical felt burden;
- `Tails of Iron 2` secondary/palate-cleanser role rather than main-game priority;
- `High On Life` moderate full/main-game candidate;
- `Sifu` strong current pre-play interest;
- `Batman: Arkham` replay-positive anchor;
- `RDR2` primary open-world positive;
- context-sensitive interpretations for `directionlessness`, `unchanged_repetition`, `management_routine`, and `puzzle_pacing`.

Reviewer recommendations are advisory only and must not be auto-converted into production policy changes. Any material Taste/ranking policy implementation still requires Director review and, before acceptance, a current Taste Review checkpoint.

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