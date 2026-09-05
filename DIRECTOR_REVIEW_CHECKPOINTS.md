# DIRECTOR REVIEW CHECKPOINTS

Durable control state for mandatory independent reviews.

The Director must read this file before assigning a new ordinary backlog task whenever a worker slot becomes free.

## System Auditor

system_audit_due: false
first_system_audit_trigger: `satisfied_2026-09-02`
material_changes_since_last_system_audit: 0
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

Phase 2A security/state/cloud-worker boundary is accepted.

The separately billed OpenAI API Phase 2B route reached a real read-only Codex execution but is stopped by user cost policy after API credits were unavailable. Do not ask the user to fund that route.

Zero-cost recon completed at:
`reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`

It identifies direct GitHub Copilot CLI in Actions using built-in `GITHUB_TOKEN` and included Copilot entitlement as the preferred quota-bounded zero-additional-payment candidate. No live Copilot pilot has yet been accepted, so no new provider boundary is accepted yet.

No System Audit is currently due. A successful Copilot-provider live pilot reaches a new provider acceptance gate and must trigger an independent System Audit before that provider boundary is materially accepted for general orchestration.

## Taste Reviewer

taste_reviewer_chat_established: true
taste_baseline_review_due: true
last_taste_review_report: `reviews/taste_reviews/baseline-01.md`

### Current Taste implementation sequence

Internal ordered sequence:
1. evidence state / confidence / reconsideration semantics — technically complete;
2. play role + relative start priority — technically complete;
3. reconsideration commercial bridge + wishlist-good-deal override — technically complete after owner self-recheck.

Step 3 durable report:
`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
Status: `complete`.

A fresh independent current Taste Review over combined Steps 1–3 is now mandatory before final material acceptance of the new semantics.

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
