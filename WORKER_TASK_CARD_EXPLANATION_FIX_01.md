# WORKER TASK — CHAT 2

Task ID: `card-explanation-fix-01`
Mode: `IMPLEMENT / FIX`
Report: `reviews/worker_reports/card-explanation-fix-01.md`

## Goal

Fix only the one concrete remaining acceptance defect from `card-explanation-implement-01`:

`Middle-earth™: Shadow of Mordor™: positive lacks explicit personal-taste link`

Do not repeat the audit or redesign the explanation system.

## Read first

- `reviews/worker_reports/card-explanation-implement-01.md`
- current `scripts/card_explanation_policy.py`
- current canonical final producer and validator involved in that report

## Required work

1. Trace only why the current visible positive explanation for `Middle-earth™: Shadow of Mordor™` passes the producer but fails the explicit personal-taste-link validator.
2. Fix the smallest systemic rule/policy mismatch so the result either:
   - contains a valid explicit game-specific -> personal-taste link, or
   - fails closed to no positive explanation if grounded personal linkage is insufficient.
3. Do not special-case the game title/app ID unless the root cause is truly identity-specific and justified; prefer a general policy fix.
4. Preserve the existing fail-closed behavior for weak/generic positives and grounded-risk rules.
5. Rerun focused behavioral tests and the canonical real generated top-30 explanation gate.

## Acceptance

- `CARD_EXPLANATION_POLICY_TESTS=PASS`;
- top-30 generated explanation validator passes with zero violations;
- no generic fallback praise returns;
- no price/discount/rank-only Taste rationale;
- no unrelated ranking, giveaway, package, duration, translation or UI behavior changes.

## Hard boundaries

Do NOT:
- repeat broad audit/recon;
- manually patch production payload;
- add per-game hand-authored explanation data;
- weaken validator merely to make it green;
- change ranking weights or eligibility.

## Done when

The canonical real generated sample passes the explanation quality gate with zero violations and no scoped blocker remains.

## Report

Save `reviews/worker_reports/card-explanation-fix-01.md` with:
- Task
- Root cause
- Changes
- Validation / workflow run refs
- Status: exactly one of `complete`, `blocked`, `needs_fix`, `needs_user_decision`
- Recommended next step
- `Efficiency / reusable lesson: none | <short candidate/ref>`

Final response must include report path and exact commit/run refs.