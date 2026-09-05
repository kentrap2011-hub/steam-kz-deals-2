# WORKER TASK — PLAY ROLE AND START PRIORITY IMPLEMENT 01

Task ID: `play-role-and-start-priority-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/play-role-and-start-priority-implement-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`

## Context

This is internal Taste IMPLEMENT step 2 of the ordered three-step sequence from:
`reviews/worker_reports/taste-review-recommendations-gap-recon-01.md`

Step 1 is complete and technically validated:
`reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`

Do not implement step 3 (reconsideration commercial bridge / wishlist-good-deal override) yet.

## Goal

Add one canonical producer-owned context layer that keeps these concepts separate:

1. price-blind personal fit / evidence state;
2. **play role** — what place a game should occupy for this user;
3. **relative start/queue priority** — how soon it is worth starting relative to other suitable games;
4. commercial purchase urgency/value — unchanged separate authority.

The project must no longer infer all of these from one scalar score or from sale urgency.

## Required semantics

### Play role

Use a small explicit role vocabulary, equivalent to:
- `main_full` — full/main game candidate;
- `secondary_palate_cleanser` — secondary / lighter parallel game;
- `family_coop` — family/co-op context;
- `unresolved` — not enough title-specific evidence to assign a stronger role.

If the current architecture supports a better bounded naming scheme, it may be used, but meanings must remain explicit and stable.

### Relative start priority

Use a small explicit queue-priority vocabulary, equivalent to:
- `high`;
- `ordinary`;
- `low`;
- `unresolved` if evidence is insufficient.

This is **not** sale urgency and must not be derived from discount/deal end.

### Provenance / confidence

Persist enough provenance/confidence so a role/priority is not silently invented from franchise identity or one generic feature.

Franchise history is a weak prior only. It cannot impose a hard role cap on a new title without title-specific evidence.

## Calibrated controls

At minimum prove these controls without expanding the user questionnaire:

- `Sifu` — strong current pre-play interest; high start priority / main candidate should be representable independently of sale urgency.
- `High On Life` — full/main candidate with moderate/ordinary queue priority; wishlist does not automatically mean “play next”.
- `Amnesia: The Bunker` — main/full + ordinary queue is representable; scarcity/threat remain contextual, not generic negatives.
- `Terminator: Resistance` — moderate/ordinary queue with franchise interest; sale urgency remains a separate commercial label.
- `Tails of Iron 2` — `secondary_palate_cleanser` survives downstream even when raw fit is strong.
- `Trine 4` — confirmed family-play positive is representable as family/co-op role without being confused with solo main priority.
- `TMNT: Splintered Fate` — franchise history remains a weak prior; title-specific evidence may resolve main/secondary independently.
- `HighFleet` — confirmed negative evidence from step 1 remains strong and must not gain artificial high start priority.

## Architecture constraints

Prefer one dedicated semantic/context contract outside the reusable Taste-fit cache, e.g.:
`config/play_priority_context_contract.json`

and one producer/helper, e.g.:
`scripts/play_priority_context.py`

Exact filenames may vary only if there is a clearly better existing canonical owner. Do not create a second ranking/sorting authority.

The current final ranking/order may consume the context only where explicitly necessary. If role/start priority can be represented truthfully without changing score weights, prefer that.

Potential current surfaces identified by recon:
- `config/final_ranking_policy.json` only if canonical order truly needs it;
- `scripts/build_visual_feed_v2.py`;
- `scripts/build_final_visual_payload.py`;
- `scripts/priority_ranking.py` only if unavoidable;
- `scripts/build_ranking_lookup.py`;
- `web/app.js` for truthful role/start-priority display if current UI lacks it;
- `PROJECT_RULES.md` / `PROJECT_DECISIONS.md` for the durable distinction.

## Must preserve

- Step 1 evidence-state semantics unchanged.
- `confirmed_negative` remains non-overridable.
- Taste remains price/discount/wishlist blind.
- Sale urgency remains a separate commercial dimension.
- Existing default mobile score/urgency toggle behavior remains truthful.
- No wishlist-good-deal override yet.
- No bundle/reconsideration commercial bridge yet.
- No new scheduler/semantic runtime.
- No broad questionnaire.

## Regression requirements

At minimum add focused deterministic tests proving:
1. role is not identical to fit score;
2. start priority is not identical to commercial urgency;
3. wishlist does not imply high start priority;
4. strong fit may still be `secondary_palate_cleanser`;
5. family/co-op role survives downstream separately from solo/main queue;
6. franchise prior cannot hard-cap role without title-specific evidence;
7. confirmed-negative candidate cannot receive high start priority;
8. current urgency label/toggle invariants remain green;
9. existing Taste V5 evidence-state tests remain green;
10. no second automatic ranker/sorter is introduced.

## Acceptance boundary

This is internal step 2, not final acceptance of the complete Taste Reviewer handoff.

Technical validation is required now.

If steps 1–3 remain one bounded internal sequence, run one independent current Taste Review after step 3 and regenerated controls before final material acceptance. If Director chooses to accept/deploy this step independently, current Taste Review becomes mandatory before that acceptance.

## Done when

Save:
`reviews/worker_reports/play-role-and-start-priority-implement-01.md`

Include:
1. Status
2. Exact role/start-priority contract
3. Files changed
4. How role differs from fit
5. How start priority differs from sale urgency
6. Control/regression results
7. Ranking/UI impact, if any
8. Proof no wishlist/commercial bridge was implemented
9. Whether step 3 can safely start
10. Exact commits/runs/artifacts
11. One bounded next step only

Status exactly one:
- `complete`
- `blocked`
- `needs_followup_fix`
