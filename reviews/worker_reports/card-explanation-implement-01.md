# Card explanation implementation 01 — worker report

Date: 2026-09-01

Task: `WORKER_TASK_CARD_EXPLANATION_IMPLEMENT_01.md`

## Status

`implemented_behavioral_tests_pass_generated_sample_failed`

The implementation is present in `main` and the focused behavioral policy tests pass, but the first canonical real generated top-30 acceptance sample found one remaining positive-explanation violation. Therefore this worker task must not be represented as fully accepted/complete yet.

No attempt was made in this reporting step to redo or change the implementation.

## What changed

A shared deterministic explanation policy was added in `scripts/card_explanation_policy.py`.

Positive explanation behavior:
- player-facing `why_fit[]` is derived only from sufficiently specific bound Taste positive evidence;
- generic eligibility/score/rank/discount language is not converted into praise;
- if available evidence is too weak or generic, the positive block fails closed (`why_fit=[]`) instead of emitting the former generic fallback;
- producer output records `why_fit_status` and `why_fit_provenance`.

Negative explanation behavior:
- existing risk candidates may still exist for scoring/ranking;
- a player-facing `risks[]` bullet is emitted only when its provenance is allowed by the policy (`taste_negative_evidence` or `confirmed_practical`);
- heuristic/derived-only candidates may continue to affect the pre-existing scoring semantics, but they are not automatically converted into visible personal negatives;
- producer output records `risk_codes`, `risk_status`, and `risk_provenance`;
- no grounded described risk means an empty visible risk block rather than a fabricated filler.

A generated-output validator was added and wired into the canonical visual workflow before the Russian-description gate. It validates a bounded top-30 generated sample for generic/commercial positives, explicit personal-fit linkage, positive provenance, no-risk consistency, and grounded visible risk provenance.

Ranking weights/formulas, giveaway logic, package economics, duration semantics, translation semantics, and unrelated UI behavior were not intentionally changed by this task.

## Canonical producer ownership after the change

The authoritative final card producer remains:

- `scripts/build_final_visual_payload.py`

It now reapplies the shared explanation policy for both the full canonical build path and deterministic refresh path before the final visual payload is accepted.

Positive reasons are initially generated in:

- `scripts/build_visual_feed_v2.py`

using `card_explanation_policy.positive_reasons(...)`, and are then re-evaluated by the final canonical producer so stale/older explanation fields do not survive the final writer.

Visible risks are finalized in:

- `scripts/build_final_visual_payload.py`

via the shared `card_explanation_policy.visible_risk_payload(...)` policy over the current risk-candidate set. `scripts/refine_visual_ranking.py` remains the source of existing risk-candidate/scoring semantics; the explanation policy controls player-facing visibility and provenance, not ranking math.

The canonical workflow gate is:

- `.github/workflows/build-daily-visual-payload.yml`

with focused policy tests before build and generated top-30 explanation validation after generation and before the Russian-description acceptance gate.

## Behavioral test results

Canonical workflow run:
- run: `33541727232`
- job: `99969364294`
- head SHA: `d40db7ee637e29b40a3c35fb3a343a378d8b1fd8`

Focused explanation policy test result:

`CARD_EXPLANATION_POLICY_TESTS=PASS count=5`

Covered behavior includes:
- specific gameplay evidence produces a concrete personalized positive reason;
- generic/commercial/eligibility-only signals do not produce praise;
- heuristic-only risk does not become a visible negative;
- grounded negative evidence is preserved over a stronger heuristic-only candidate and output is deterministic;
- unrelated card fields are not inputs to or mutated by the explanation policy.

Other pre-existing checks reached before the generated sample also passed in the same job, including priority ranking validation, duration contract/tests, commercial refresh tests, fixed package tests, and Russian-description quality-rule tests.

## Real generated sample result

The canonical workflow generated/refreshed a real visual payload in the runner workspace:

`VISUAL_FINAL_BUILD=BUILT mode=deterministic_refresh items_refreshed=442 media_keys=438 package_qualifying=8 package_strict=8 package_equivalence=1 package_touched=19 ai_queue=3`

Then `scripts/validate_card_explanations.py data/production/visual/current.json 30` inspected the real top-30 generated sample.

Observed sample summary:
- sample size: `30`;
- visible positive cards: `3`;
- omitted positive cards: `27`;
- visible risk cards: `2`;
- cards with no visible risk: `28`;
- violation count: `1`.

First five sample titles reported by the validator:
1. `Decarnation`
2. `The Last Soldier of the Ming Dynasty`
3. `Plague Inc: Evolved`
4. `The Black Grimoire: Cursebreaker`
5. `Orbo's Odyssey`

Acceptance result:

`CARD_EXPLANATION_VALIDATION=FAIL count=1`

Exact remaining violation:

`Middle-earth™: Shadow of Mordor™: positive lacks explicit personal-taste link`

The workflow job therefore correctly failed at the new generated-card explanation gate instead of allowing this sample through as accepted.

## Remaining limitations

1. `Middle-earth™: Shadow of Mordor™` still has a visible positive explanation that does not satisfy the validator's explicit personal-taste-link invariant. This is the concrete remaining implementation/acceptance defect discovered by the real sample.
2. Because the workflow stopped at the explanation validator, the generated workspace payload from this run was not accepted/committed by the later canonical commit step.
3. This run did not reach the later Russian-description gate. That gate is a separate pre-existing concern and is not evidence for or against the explanation fix in this run.
4. The policy is intentionally fail-closed and currently recognizes a bounded set of specific positive-evidence patterns. As a result, many cards may legitimately have no visible positive explanation until evidence/pattern coverage is enriched; the top-30 sample showed 27 omitted positives. This is preferable to a fabricated generic positive but is still a coverage limitation.
5. Existing heuristic risk candidates can still participate in the unchanged scoring/ranking path. The new invariant only prevents heuristic-only candidates from becoming visible player-facing negatives without grounded provenance.

## Exact commit refs

Task-state activation:
- `5000b6bd00b77ed615edf417558a6cef8f4aca67` — mark card explanation worker active.

Implementation and guards:
- `353bc86d0814c0a1921689f9ab3f23c55d565fce` — add grounded shared card explanation policy (`scripts/card_explanation_policy.py`).
- `a6d7daf3de79f36fbe18721d5182934946aa35e6` — ground positive card explanations in `scripts/build_visual_feed_v2.py`.
- `df67452288a1c37ab56e74bdff797c9760bdfd2b` — enforce grounded final card explanations in `scripts/build_final_visual_payload.py` while preserving scoring/ranking semantics.
- `5c223cd68b065463cd5354a9202bc039badf2960` — add focused card explanation policy checks.
- `7652eae02db7c48bffce4b9cf31e49429af57e8e` — add generated-card explanation validator.
- `d40db7ee637e29b40a3c35fb3a343a378d8b1fd8` — wire focused policy test and generated top-30 gate into the canonical visual workflow.

Current `main` observed before writing this report was `98c0411c76527cb23c0dfde0fe6c8e3b91f8fb6c`; that commit is unrelated parallel backlog work and has `d40db7ee637e29b40a3c35fb3a343a378d8b1fd8` as its parent.

## Acceptance conclusion

The architectural/behavioral fix is installed and focused tests pass, and the new gate successfully detects an actual remaining defect in real generated output. Final status is therefore not `complete`: implementation is present, behavioral tests pass, but real generated top-30 acceptance currently fails on exactly one card.