# TASTE REVIEW — BASELINE 01

Role: dedicated Taste Reviewer
Mode: advisory review; no production code changes
Report: `reviews/taste_reviews/baseline-01.md`

## Read first

- `TASTE_REVIEWER_ROLE.md`
- `USER_TASTE_PROFILE.md`
- `DIRECTOR_REVIEW_CHECKPOINTS.md`
- the smallest canonical taste/ranking evidence needed to review current outcomes

Do not perform broad repository archaeology.

## Goal

Build the first durable understanding of Dmitry's game taste and independently test whether the current recommendation/filtering system is squeezing the selection too hard or prioritizing games in ways that do not fit him.

## Work

1. Build/update `USER_TASTE_PROFILE.md` from explicit/canonical evidence only.
2. Separate strong facts from tentative inferences.
3. Use a bounded current sample containing:
   - top recommendations;
   - near-cutoff games;
   - excluded strong-deal or wishlist candidates when available;
   - known positive and negative controls.
4. Look specifically for:
   - duplicated penalties;
   - one weak negative signal overpowering several strong positives;
   - overly narrow eligibility;
   - underweighted explicit user interest/wishlist;
   - inconsistent treatment of similar games;
   - ranking that is technically valid but intuitively wrong for this user.
5. Ask the user a small number of targeted comparison questions if the evidence cannot distinguish between plausible taste models.

## Boundaries

Do NOT:
- modify production code/config/weights;
- judge deal quality as personal taste;
- accept current ranking merely because it is canonical;
- invent preferences from genre stereotypes;
- drift into runtime/CI/system auditing.

## Report

Save `reviews/taste_reviews/baseline-01.md` with:
- profile confidence;
- sample reviewed;
- what the system currently gets right;
- strongest taste mismatches;
- whether selection pressure appears `too_tight`, `too_loose`, `approximately_balanced`, or `cannot_determine`;
- up to 3 recommended tests/changes for Director review;
- unresolved taste questions.

The Taste Reviewer advises only. The Director decides any implementation.