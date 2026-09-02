# SYSTEM AUDIT — BASELINE 01

Role: `SYSTEM AUDITOR`
Mode: `READ-ONLY / AUDIT`
Report: `reviews/system_audits/baseline-01.md`

## Read first

- `SYSTEM_AUDITOR_ROLE.md`
- `DIRECTOR_REVIEW_CHECKPOINTS.md`
- `DIRECTOR_TASK_BOARD.md`
- only the smallest current canonical reports/evidence needed for findings

Do NOT perform broad Git-history archaeology.

## Why this audit is due

The mandatory first checkpoint has fired after the current Trine 4 and giveaway-identity tracks reached stable operational boundaries.

Recent incidents that justify the audit include:
- Trine 4 existed with a live valid discount but was absent from the user-visible list because semantic readiness was unresolved;
- queue presence did not itself prove that semantic processing was running or monitored;
- giveaway analysis required exact cross-store identity and exposed dependency/provider-operability risk around Twitch/IGDB;
- ITAD is now only a proposed alternative pending explicit permission, not an accepted production dependency.

## Goal

Independently test whether the whole current system reliably produces the intended user-visible result, rather than merely whether individual stages pass their local checks.

## Required audit lenses

Use bounded evidence only. Look specifically for:
1. automatic work that can sit queued without a known execution/completion signal;
2. data/readiness gates that can silently remove valid user-relevant games;
3. downstream rebuild/deploy stages whose success is assumed rather than proven end-to-end;
4. external-provider or identity dependencies that create hidden single points of failure;
5. duplicated mechanisms, ownership ambiguity, or avoidable complexity;
6. tests that validate data shape while missing user-visible behavior;
7. stale/incomplete data that degrades the feed without a clear alert;
8. fail-closed rules that are safe locally but may squeeze the final choice too aggressively at system level.

Do not turn this into a Taste Review. Personal taste quality belongs to `TASTE_REVIEWER_ROLE.md`.

## Output discipline

Maximum 5 significant findings.

For each finding include:
- user impact;
- exact evidence/ref;
- severity: `high | medium | low`;
- certainty: `proven | risk_hypothesis`;
- one bounded verification/fix candidate.

Then recommend at most 2 Director tasks, ordered by impact.

If a suspected issue is not proven, say so explicitly. Do not invent architecture problems merely to fill the quota.

## Hard boundaries

Do NOT:
- implement fixes;
- change code/config/contracts;
- redesign the whole architecture;
- investigate historical commits broadly;
- audit personal taste quality;
- process production items manually;
- create new queues/schedulers/providers.

## Completion

Save report to:
`reviews/system_audits/baseline-01.md`

Status exactly one:
- `complete`
- `blocked`
- `needs_user_decision`

End with at most 2 recommended next tasks and exact refs.