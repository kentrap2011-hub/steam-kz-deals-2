# Steam semantic queue priority implementation 01

Status: `implementation_complete_ready_for_director_acceptance`

Task: `STEAM-SEMANTIC-QUEUE-PRIORITY-IMPLEMENT-01`

## Scope and ownership

- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- GitHub control-plane owner: `config/execution_ownership_contract.json`.
- Canonical queue-order policy: `config/progressive_pass2_contract.json#ordering`.
- Existing producer/orderer: `scripts/build_progressive_pass2_work.py`.
- Existing eligibility owner remains `scripts/progressive_pass2.py::recompute_eligibility`.
- Work manifest remains `data/production/pre_ai/progressive_pass2_work.json`.
- No worker prompt, Scheduled Task, scheduler, retry owner, Dossier semantic judgment, site ranking, Deep Stage 1 scoring, or Deep Stage 2 calibration logic was changed.

## Ordering before this change

The existing GitHub producer ordered already-eligible normal Deep work by:

1. known sale end ascending;
2. deterministic purchase score descending;
3. family ID ascending.

The purchase score was the existing canonical purchase breakdown. Sale expiry therefore had direct semantic-work priority even though it did not change eligibility.

## Ordering after this change

The producer still receives the exact list returned by `recompute_eligibility`; it only reorders copies of those work items.

New precedence:

1. subjects with **no authoritative Deep history** before subjects that have authoritative Deep history when both require work;
2. semantic queue priority score descending;
3. stable `family_id` ascending.

Sale expiry is not a priority factor. There is no hard top-N, reserve lane, exclusion, quota, or new queue owner.

## Exact definition of “never Deep analyzed”

For this operational priority, “never Deep analyzed” means **no historically authoritative accepted Deep completion in the current canonical PASS 2 state**.

The family is treated as having authoritative Deep history if either the current root entry or any `revision_history[].state` has:

- `authoritative_completed == true`; and
- outcome `analyzed_fit` or `analyzed_not_fit`.

Consequences:

- authoritative fit counts as prior Deep analysis;
- authoritative not-fit counts as prior Deep analysis;
- legacy authoritative state retained in revision history counts;
- `analysis_incomplete`, recovery-owned state, and failed/invalid transport do not by themselves count as authoritative Deep history.

This classification changes ordering only. It does not revive, suppress, rewrite, or otherwise mutate authoritative Deep state.

## Priority score

The queue score is operational only; it is not a personal taste score and does not alter final site ranking.

Scale: 0–100.

- Steam positive rating: 40 points, normalized as `clamp(global_positive_percent / 100, 0, 1)`.
- Steam review confidence: 20 points, normalized as `min(1, log1p(global_count) / log1p(100000))`.
  - logarithmic confidence makes more reviews useful without letting raw popularity grow linearly and dominate niche games;
- current price: 20 points.
  - reuses the existing canonical current-price band component from `config/final_ranking_policy.json` through `priority_ranking.build_purchase_breakdown`;
  - normalized as `price_component_points / price_component_max`;
- current discount: 20 points, normalized as `clamp(discount_percent / 100, 0, 1)`.

Missing numeric signals contribute zero for that factor. No wishlist or personal-taste factor is part of this queue score.

## Eligibility / candidate-count proof

The change is downstream of `progressive_pass2.recompute_eligibility`.

`order_normal_items()`:

- accepts the existing eligible work-item list;
- copies each item;
- computes temporary ordering values only;
- performs a stable deterministic sort;
- assigns `sequence`;
- removes all temporary priority fields before writing the manifest.

It does not add or remove items and it does not modify immutable work IDs or authorization bindings.

Deterministic regression `scripts/test_semantic_queue_priority.py` proves the input/output candidate count and family/work-ID sets are identical and no `deferred_reserve` / `excluded` disposition is created.

Current production snapshot additionally shows:

- Deep current coverage target: 2301;
- first-pass attempted: 166;
- authoritative completed: 147;
- waiting for Dossier: 2135;
- ready/pending work: 0;
- current `items`: empty.

Because there are zero current ready work items, a truthful production top-20/top-30 before/after list cannot be produced without executing or fabricating semantic work. No semantic worker was run for this validation.

## Validation

Added `scripts/test_semantic_queue_priority.py` and wired it into `.github/workflows/validate-progressive-pass2-core.yml`.

The regression proves:

- exact eligible candidate count and work identities are preserved;
- no item becomes deferred/excluded because of ordering;
- no-authoritative-history cohort precedes prior-authoritative cohort at equal commercial/quality inputs;
- both authoritative fit and authoritative not-fit count as prior Deep history;
- legacy authoritative revision history counts;
- incomplete/recovery and absent failed transport do not count as authoritative history;
- Steam rating monotonicity;
- logarithmic review-confidence monotonicity and saturation;
- lower-price monotonicity via the existing canonical price component;
- higher-discount monotonicity;
- deterministic family-ID tie-break;
- Wishlist/package/DLC lanes are not filtered by the orderer;
- authoritative Deep state is read-only;
- the producer does not touch frozen Stage 1/Stage 2 contracts or worker prompts.

Validation run on implementation/config head `e17743d5e099cd4fcb1ff736d1901b90f9cd6608`:

- `Validate Progressive PASS 2 core` run `37600971315`: **success**.

An earlier implementation head `a5149751e4f42f4b32d1501445d82a17b28b6055` also passed the same workflow in run `37600717191`.

## Stage 2 overlap / conflict check

Active Chat 2 branch found: `implement/deep-stage2-calibration-worker-01`.

Its compared implementation surface contains:

- `.github/workflows/validate-deep-stage2-calibration.yml`;
- `CURRENT_TASK.md`;
- `config/deep_stage2_manual_worker_prompt.md`;
- `data/cache/deep_stage2_state.json`;
- `data/production/pre_ai/deep_stage2_work.json`.

This task changes the current PASS 2 queue-order policy/producer/test validation surface instead. There is no Deep Stage 1/Stage 2 implementation-file overlap. `CURRENT_TASK.md` is only a shared operational handoff document and is updated minimally at closeout.

Frozen PR #156 interfaces are unchanged.

## PR

- PR: #158 — `Prioritize never-analyzed semantic queue work`
- branch/head: `implement/steam-semantic-queue-priority-01`
- validated implementation/config head: `e17743d5e099cd4fcb1ff736d1901b90f9cd6608`

## Remaining risks

- Current production has zero ready Deep items, so the first real production ordering sample will appear only when GitHub naturally has multiple eligible work items again; no semantic execution was performed merely to manufacture a sample.
- The review-confidence cap (100,000) deliberately saturates very large review counts; this is an operational confidence normalization, not a statement that games above that count are equal in quality.
- Current-price priority deliberately inherits the existing canonical price bands, so prices inside one band can tie. This preserves monotonic non-worsening behavior without creating a parallel price scale.

No first-wave/deferred-reserve gating was introduced. The prior diagnostic recommendation for that production direction is superseded by the user decision implemented here.
