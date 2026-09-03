# WORKER TASK — MOBILE FEED REGRESSION GATE 01

Task ID: `mobile-feed-regression-gate-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/mobile-feed-regression-gate-01.md`

## Source decision

Direct bounded follow-up from:
`reviews/system_audits/mobile-post-incident-audit-01.md`

The mobile client incident itself is accepted and closed on the affected Android device. Do not redesign or debug the accepted cache-first implementation.

The only remaining proven gap is that the focused regression:
`tests/feed-bootstrap.test.js`
passes when run directly but is not included in the canonical Pages deploy regression gate.

## Goal

Make the existing mobile feed bootstrap/cache/lifecycle regression a required part of the normal Pages deployment gate.

## Required change

Add:
`node tests/feed-bootstrap.test.js`
(or the exact equivalent invocation of that existing test)
to the canonical Pages deploy regression step/path that already runs the current UI regressions.

Then prove one ordinary passing canonical Pages run exercises the test.

## Boundaries

Do NOT:
- modify `web/feed-bootstrap.js` behavior;
- modify `web/app.js`;
- redesign caching/render/lifecycle behavior;
- add new mobile tests beyond what is strictly needed to wire the existing test into the gate;
- change visual-freshness semantics except for any unavoidable merge-state compatibility after its separate accepted release;
- fix Epic/ITAD/Taste work;
- add another workflow or release path.

If the visual-freshness release lands first, wire the test into the resulting canonical deploy workflow without changing that accepted freshness logic.

## Acceptance

Pass only if:
1. canonical Pages deploy gate invokes `tests/feed-bootstrap.test.js`;
2. the existing focused test passes there;
3. one normal Pages run proves the gate is active;
4. no client behavior changed.

## Completion

Save:
`reviews/worker_reports/mobile-feed-regression-gate-01.md`

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`

Final answer must include exact report path, production ref and Pages run ID.