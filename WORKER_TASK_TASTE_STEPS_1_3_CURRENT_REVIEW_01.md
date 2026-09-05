# WORKER TASK — Independent Current Taste Review, Steps 1–3

## Task ID
`taste-steps-1-3-current-review-01`

## Mode
`READ-ONLY / TASTE REVIEW`

## Expected report
`reviews/taste_reviews/taste-steps-1-3-current-review-01.md`

## Role
Read and obey `TASTE_REVIEWER_ROLE.md` plus `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md`, `USER_TASTE_PROFILE.md`.

## Goal
Independently review the combined current Taste semantics after technical completion of:
1. V5 evidence state/confidence/reconsideration;
2. play role + relative start priority;
3. commercial reconsideration + wishlist-good-deal bridge.

This is mandatory before final material acceptance. Do not implement fixes in this task.

## Required sources
Read at minimum:
- `reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`
- `reviews/worker_reports/play-role-and-start-priority-implement-01.md`
- `reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
- `reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`
- current Taste/contracts/producers on `main`
- current regenerated production/control outputs as available
- previous `reviews/taste_reviews/baseline-01.md`

## Review questions
- Are the new evidence states semantically coherent with the user's actual taste model?
- Does `confirmed_negative` remain genuinely non-overridable?
- Does `reconsiderable` mean uncertainty/possible commercial rescue rather than hidden positive fit?
- Do role/start fields improve recommendations without becoming price/discount-driven?
- Does wishlist + canonical good deal bypass only weak/insufficient eligibility without faking moderate/strong fit?
- Can fixed-package value make a reconsiderable purchase commercially reasonable without rewriting Taste?
- Are warnings/risks/provenance preserved?
- Are baseline controls still sensible: Sifu, High On Life, Amnesia Bunker, Terminator Resistance, Tails of Iron 2, Trine 4, TMNT Splintered Fate, HighFleet, Batman Arkham, RDR2?
- Does current ranking/output show any material regressions, weird promotions, or contradictions?

## Required conclusion
Report one of:
- `ACCEPT`
- `ACCEPT_WITH_ADVISORY_RECOMMENDATIONS`
- `REJECT_NEEDS_FIX`

Separate blocking findings from advisory ideas. Reviewer recommendations are advisory and must not silently become product policy.

No product/code changes. Save only the exact report path above.
