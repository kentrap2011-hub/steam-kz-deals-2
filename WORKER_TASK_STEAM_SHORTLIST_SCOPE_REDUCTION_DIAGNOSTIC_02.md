# WORKER TASK — Steam shortlist scope reduction diagnostic 02

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02`
Worker slot: `ЧАТ 1`
Mode: `READ-ONLY / DIAGNOSTIC / OFFLINE SIMULATION`

## Why this task exists

The Steam Reviews/publication blocker is fixed and accepted through PR #155.

That fix exposed the real current funnel instead of the artificially small queue created by missing review data.

Fresh canonical state now shows approximately:

- 60,632 paid eligible items after source/local gates;
- 7,972 broad shortlist items;
- 2,522 paid shortlist items;
- ~2,134 current Dossier pending items;
- ~2,301 current Deep coverage target.

Before the review path was fixed, the shortlist had been around 609 and the semantic queues were much smaller. The old small size was partly caused by missing review data and therefore must NOT be restored by reintroducing review failures.

The user wants roughly ~100 best visible offers, but does NOT want a blind raw top-N cutoff before semantic analysis.

The purpose of this task is to determine how to reduce the semantic candidate pool much further while preserving strong candidates.

## START gate

Read current:
- `CHAT_PROTOCOL.md`;
- current top of `DIRECTOR_TASK_BOARD.md`;
- relevant Steam discovery/shortlist route in `PROJECT_ROUTES.md`;
- current production manifest/funnel;
- current shortlist selection logic;
- current canonical product rules affecting paid candidates;
- current Wishlist handling;
- current Deep/Dossier scope-generation path only as needed to understand which shortlist rows become semantic work.

Do not inspect unrelated systems.

## Hard boundary

Diagnostic only.

Do not:
- change production code;
- change thresholds;
- write a new shortlist;
- change Dossier/Deep queues;
- change ranking;
- change Scheduled Tasks;
- rerun semantic workers.

Offline simulations against current canonical data are encouraged.

## Questions to answer

### 1. Why exactly did 609 become 2,522?

Quantify the increase by reason/category.

At minimum break down current selected candidates by:
- which refined reason(s) admitted them;
- how many pass only one weak/generic reason;
- how many pass strong-fit / strong-niche / high-confidence routes;
- DLC vs base games vs packages/bundles where identifiable;
- review-count bands;
- rating bands;
- price bands;
- discount bands;
- fit-tag/core-tag count;
- Wishlist presence;
- existing accepted Deep fit/not-fit if available;
- already known direct-user-rated titles if available.

Identify which admission rules contribute most to the explosion.

### 2. Simulate stronger deterministic gates

Test several bounded candidate-reduction strategies on current canonical data.

Do not choose only by raw count.

For each strategy report:
- resulting candidate count;
- how many current known positive Deep results it retains/drops;
- how many current Wishlist games it retains/drops;
- how many directly user-rated/reference games it retains/drops when identifiable;
- how many current strong commercial opportunities it retains/drops;
- how many packages/bundles it retains/drops;
- how much DLC it removes;
- likely semantic cost/risk.

### 3. Candidate strategies to test

At minimum test combinations involving:

- stricter minimum review count;
- stricter rating thresholds;
- stronger requirement for core taste tags;
- rejecting candidates admitted only by generic commercial reasons;
- stronger rules for `exceptional_discount` when taste evidence is weak;
- stronger rules for `mainstream_quality` when personal-fit evidence is weak;
- stricter handling of `strong_niche_fit`;
- popularity floor that still permits genuinely strong niche games;
- preserving all Wishlist games as an explicit protected lane;
- preserving known directly-rated/reference games where relevant;
- DLC-specific narrowing that does not silently assume ownership data already exists;
- package/bundle preservation as a distinct valuable lane;
- deterministic pre-ranking into a semantic-analysis pool larger than the final ~100 but much smaller than 2,500.

Do not silently remove bundles/packages.

Do not use a popularity-only rule that destroys niche-but-relevant games.

### 4. Target bands

Simulate at least these approximate semantic-pool bands:

- conservative: ~700–1000;
- balanced: ~300–600;
- aggressive: ~150–300.

These are diagnostic bands, not hard quotas.

The final recommendation should explain which band best protects recall for a final site target of roughly 100 offers.

### 5. No blind top-N

A hard `take first 300` after arbitrary sort is not acceptable as the primary solution.

If a deterministic pre-ranking followed by a cap is proposed, prove:
- the ranking inputs are transparent;
- protected lanes (Wishlist, packages/bundles, strong known-fit evidence) cannot be accidentally crowded out;
- the cap is applied only after meaningful deterministic quality/fit gates;
- the user can understand why an item was admitted/excluded.

### 6. Explain the old ~300 state correctly

Do not recommend returning to old behavior simply because the old queue was smaller.

Explicitly distinguish:
- legitimate filtering;
- accidental shrinkage caused by review-data failure;
- any historical rules that were actually stricter.

## Deliverable

Create:
`reviews/worker_reports/steam-shortlist-scope-reduction-diagnostic-02.md`

Required contents:

1. exact current funnel;
2. exact reason the pool expanded;
3. current admission-rule contribution table;
4. at least 3 reduction strategies;
5. simulated counts for each;
6. retention/loss of known-good/Deep/Wishlist/reference candidates;
7. DLC/package effects;
8. recommended strategy;
9. exact product tradeoffs requiring user/Director choice;
10. smallest follow-up implementation task, but DO NOT implement it.

Final statuses:
- `diagnostic_complete_recommendation_ready`
- `diagnostic_complete_user_choice_required`
- `blocked_missing_canonical_data`
