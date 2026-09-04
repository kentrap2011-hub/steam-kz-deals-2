# WORKER TASK — WISHLIST GOOD-DEAL OVERRIDE RECON 01

Task ID: `wishlist-good-deal-override-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/wishlist-good-deal-override-recon-01.md`

## User rule

A game from the user's Steam wishlist should be able to enter the final paid-deal feed when the current deal is genuinely good, even if automatic Taste fit is weak/minimal.

Wishlist is an explicit user-interest signal in this scenario and may override the ordinary Taste eligibility/filter. It must not be reduced to a small score bonus that only applies after a game already passed the Taste gate.

A weak/ordinary discount does not have to override Taste.

Confirmed risks, poor purchase value, or other already-authoritative negative evidence must remain visible and must not be hidden by wishlist status.

## Goal

Map the exact current eligibility -> ranking -> final-feed path and define the smallest safe rule for:

`Steam wishlist + genuinely good deal -> may pass ordinary weak-Taste eligibility`

without changing production code yet.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_RULES.md`
- `USER_TASTE_PROFILE.md`
- current ranking/Taste contracts and only the exact code that owns wishlist eligibility, deal quality/history, Taste exclusion and final priority
- `DIRECTOR_REVIEW_CHECKPOINTS.md`

Do not perform broad history archaeology.

## Required checks

1. Identify the exact first gate where a wishlist item with weak/minimal Taste can currently be removed before final ranking.
2. Distinguish:
   - wishlist eligibility/override;
   - wishlist score bonus;
   - commercial/deal-quality eligibility;
   - hard/confirmed user-risk exclusions.
3. Identify the canonical existing signals that can define a `genuinely good deal` without inventing a hidden arbitrary constant. Prefer current deal-quality/history semantics already used by the project.
4. Determine the smallest explicit condition under which wishlist may override only the ordinary Taste gate.
5. Specify what must remain non-overridable, especially:
   - invalid/unavailable purchase;
   - clearly poor deal/value if current contracts treat it as disqualifying;
   - confirmed direct-conflict / hard exclusion if such a concept exists;
   - truthful risk/explanation visibility.
6. Verify whether the override should affect eligibility only, ranking score too, or both. Do not redesign scoring unless strictly necessary.
7. Produce focused regression cases at minimum:
   - wishlist + genuinely good deal + weak Taste -> present in final feed;
   - wishlist + weak/ordinary deal + weak Taste -> no guaranteed override;
   - non-wishlist + weak Taste -> existing behavior unchanged;
   - wishlist override does not erase confirmed risks or poor-value warnings;
   - strong existing Taste-positive behavior remains unchanged.
8. Identify the exact files/contracts an IMPLEMENT would need to change.
9. Classify Taste Review requirement. Because this changes wishlist-vs-Taste eligibility semantics, final implementation acceptance must require an independent Taste Review checkpoint.
10. Produce one bounded IMPLEMENT plan only.

## Boundaries

READ-ONLY / RECON only.

Do NOT:
- change ranking/Taste code;
- change weights or thresholds in this task;
- weaken commercial availability/price evidence;
- change giveaway logic;
- touch Epic/GOG RU availability work;
- create a second Taste state or parallel ranking implementation;
- process semantic queues manually;
- auto-convert Taste Reviewer advice into policy.

## Done when

Save:
`reviews/worker_reports/wishlist-good-deal-override-recon-01.md`

Include:
1. Task
2. Current path
3. Exact removal/gate point
4. Canonical good-deal signal
5. Proposed override semantics
6. Non-overridable protections
7. Regression plan
8. Exact implementation files
9. Taste Review requirement
10. One bounded IMPLEMENT plan
11. Status
12. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_user_decision`
