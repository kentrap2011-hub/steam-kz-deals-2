# Card negative analysis gap 01 — worker report

Date: 2026-09-02

### Task

Task ID: `card-negative-analysis-gap-01`.

This was a bounded read-only diagnosis of the current negative-analysis route only. The existing positive-explanation audit/design was not repeated, no production game was manually curated, no ranking/Taste/discount logic was changed, and no negative was invented to fill a card.

The investigation was frozen to repository snapshot:
- `1d0abef62948912466aaf42c5ee4c352b2ba7544`

Primary inspected artifacts/code:
- `data/production/visual/current.json`
- `data/production/visual/ranking_lookup/_manifest.json`
- `scripts/refine_visual_ranking.py`
- `scripts/build_final_visual_payload.py`
- `scripts/card_explanation_policy.py`
- `scripts/validate_card_explanations.py`
- `scripts/ingest_taste_results.py`
- `config/taste_result_contract.json`
- `data/cache/taste_fit.json`
- `data/cache/taste_fit.entry_overlay.json`
- real post-fix generated sample from workflow run `33547075019`, job `99987114449`.

### Canonical negative-analysis route

The current ownership chain is:

1. **Semantic negative input** — existing scheduled Taste worker.
   - Canonical contract: `config/taste_result_contract.json` (`TASTE-SEMANTIC-RESULT-V3`).
   - Semantic owner: `existing_scheduled_chatgpt_taste_worker`.
   - GitHub owns queue scope/bindings, validation and persistence.
   - Negative semantic output is the required field `negative_evidence` in each Taste result.

2. **Persistence / admission** — `scripts/ingest_taste_results.py`.
   - `negative_evidence` must exist and be an array.
   - Its elements, when present, must be non-empty strings and cannot contain forbidden commercial evidence.
   - However `INCLUDE` requires only two positive evidence items; it does **not** require any negative evidence.
   - A non-empty negative list is required only for `reason_code == exclude_direct_conflict`.
   - Therefore `INCLUDE + negative_evidence=[]` is a valid canonical persisted semantic result today.

3. **Grounded risk mapping / heuristic candidates** — `scripts/refine_visual_ranking.py`.
   - Each string from `taste_entry.negative_evidence` is passed through `map_negative_evidence()`.
   - The mapper recognizes a small lexical family only: repetition/grind, reading/passive gameplay, directionlessness, management/routine/resources/crafting, punishment/difficulty and stealth.
   - A recognized semantic negative becomes a candidate with source `taste_negative_evidence`.
   - `structural_risks()` also derives heuristic candidates from tags/descriptions such as platforming, puzzles, exploration, management and old-design friction. Those default to source `derived`.
   - Confirmed modern-Windows friction and confirmed absence of Steam achievements are emitted as source `confirmed_practical`.

4. **Final visual producer** — `scripts/build_final_visual_payload.py`.
   - `explanation_risk_candidates()` combines mapped `negative_evidence` plus structural/practical candidates.
   - `apply_card_explanation_policy()` delegates player-facing visibility to `card_explanation_policy.visible_risk_payload()`.
   - Ranking/scoring intentionally keeps the full candidate set, including heuristics; visible negative text is a separate fail-closed concern.

5. **Visible negative policy** — `scripts/card_explanation_policy.py`.
   - Grounded sources are exactly `taste_negative_evidence` and `confirmed_practical`.
   - `visible_risk_payload()` drops `derived`/heuristic candidates from user-facing output.
   - If no grounded row survives, final visible `risks=[]`, `risk_codes=[]`, `risk_provenance=[]`, and `risk_status.grounding='none'`; it does not fabricate a filler downside.
   - This fail-closed suppression is correct and should not be weakened.

6. **Output validation** — `scripts/validate_card_explanations.py`.
   - If a visible risk exists, the validator requires matching status/code/provenance and a grounded source.
   - It rejects the old inconsistent state where `has_described_risk=false` still has visible negative text.
   - It does **not** reject a card with no visible grounded negative.
   - There is no readiness assertion of the form `grounded negative present OR negative analysis explicitly incomplete`.

So the canonical final producer is not accidentally deleting already-grounded risks. The principal gap occurs earlier: negative evidence is optional-in-practice for included semantic results, free-text evidence can fail the narrow mapper, and the final validator treats the resulting empty grounded-negative state as a normal valid card.

Exact implementation refs at the frozen snapshot:
- final visual producer blob: `2c7b264233191e7304a37aba41bd7f96f4b71cea`
- risk refiner / mapper blob: `757caca50fcfd167bd4eeded97f69b1b4d391eaa`
- visible explanation policy blob: `96105545d3e3d724f2828e2d34313e18e5a7c833`
- output validator blob: `ce645827e7aa81b2487b400901c423bb8e9a7746`
- Taste ingest validator blob: `776787ced9060b4210c798a18cc04239703edc0c`
- Taste semantic contract blob: `1766d14d71892199e4da44bbade627772e0411c4`.

### Production incidence

#### Canonical committed production snapshot

At frozen `main` SHA `1d0abef62948912466aaf42c5ee4c352b2ba7544`:
- `data/production/visual/current.json` blob: `e86805bcf45c6e9c579e108f8635dc8eb6f8c8b3`
- canonical ranking manifest says `item_count=442`.

That committed payload still predates the provenance-aware card-explanation production acceptance. Its old `risk_status` schema does not preserve enough source provenance to truthfully split all 442 committed cards into `grounded` versus `heuristic` after the fact. In particular, some old risk codes can arise from more than one source class. Therefore this report does **not** fabricate a full-catalog grounded count from the stale schema.

The old production artifact does contain neutral/no-confirmed-risk states and the previous audit had already shown the old filler inconsistency, but those old fields are not sufficient evidence for a precise modern grounded/heuristic classification.

#### Current producer behavior — real generated production sample

The best bounded programmatic measurement of the current provenance-aware producer is the real canonical build workspace generated after the explanation fix:
- workflow: `Build daily visual payload`
- run: `33547075019`
- job: `99987114449`
- head: `d2aa975ed71d2f1ec17626266f025b4268c1b1b5`
- rebuilt items: `442`
- validator command: `python scripts/validate_card_explanations.py data/production/visual/current.json 30`

Top-30 result:
- sample size: `30`
- cards with at least one visible grounded negative: `2`
- cards with no visible grounded negative: `28`
- share without grounded visible negative: `93.3%`
- old filler/no-negative wording shown by the current policy: `0` (empty negative block is used instead)
- explanation violations: `0`
- `CARD_EXPLANATION_VALIDATION=PASS`.

This is systemic in the bounded sample, not a rare edge case: more than nine out of ten top-30 cards reached the current explanation gate without a grounded negative, and that state was accepted as valid.

The committed 442-card production payload and this 30-card current-producer sample must not be conflated: exact full-catalog provenance incidence cannot be reconstructed from the stale committed schema, while the real post-fix generated top-30 provides direct evidence of the current behavior.

### First missing-evidence point

The gap is mixed, with three proven failure classes before final visibility plus one intentional visibility rule.

#### Cause A — no source negative was required/collected for an included result

This is the earliest and most fundamental completeness gap.

`ingest_taste_results.py` accepts an `INCLUDE` result with `negative_evidence=[]`; only positive evidence has a minimum-count requirement for INCLUDE.

Concrete persisted example from `data/cache/taste_fit.json` (blob `069ee4e5f2e7b09a173b64b99358bb0fe3ea0d71`):
- `App_241930` / Middle-earth: Shadow of Mordor
- verdict: `INCLUDE`
- fit: `strong`
- two explicit positive evidence strings
- `negative_evidence: []`.

This card therefore reaches downstream mapping with no semantic negative to map. Nothing is “lost” in the final producer; the negative analysis was never complete under the user's product rule.

Classification: **no source evidence collected / semantic completeness contract gap**.

#### Cause B — a negative consideration can be placed in the wrong semantic field

Concrete persisted example from the same Taste cache:
- `App_784150`
- verdict: `INCLUDE`, fit `moderate`
- one `positive_evidence` sentence ends with: `complexity risk keeps the fit at moderate.`
- `negative_evidence: []`.

A limiting concern was recognized semantically, but it was embedded in positive evidence instead of being represented as negative evidence. The downstream negative route only reads `negative_evidence`, so this concern cannot become a grounded visible negative.

Classification: **semantic evidence routing/classification gap**.

#### Cause C — valid supplied negative evidence can be discarded by the lexical mapper

Concrete current Taste-v3 overlay example from `data/cache/taste_fit.entry_overlay.json` (blob `387b9dd56115996f2bcc2232d3be592446131df1`, `entry_count=806`):
- `App_1011670`
- verdict: `INCLUDE`, fit `moderate`
- negative evidence: `Ragdoll physics may reduce the precision that usually strengthens movement-focused play.`

That is an explicit negative evidence string already bound to the Taste result. But `map_negative_evidence()` has no category/keywords for ragdoll physics, movement/control precision, or imprecise movement. The string therefore creates no `taste_negative_evidence` risk candidate.

Classification: **evidence exists but current free-text mapper does not recognize it**.

This is important because merely making `negative_evidence` non-empty would not close the problem: the current consumer can still silently lose semantically valid negatives.

#### Cause D — heuristic candidates are intentionally not exposed

Example: `puzzle_pacing` is structurally derived from puzzle tags/descriptions. Its source is `derived`; the visible policy rejects it unless there is independently grounded evidence.

This is **not** the defect. Turning those heuristic suspicions into definitive downsides would violate the user's rule. They may be useful signals for deciding what needs semantic confirmation, but not as player-facing negatives by themselves.

#### Final-producer suppression bug?

No evidence of one was found for already-grounded candidates.

The final route explicitly carries recognized `taste_negative_evidence` and `confirmed_practical` into `visible_risk_payload()`, and the policy allows exactly those grounded sources. A code such as `unchanged_repetition` is generated from semantic negative evidence with source `taste_negative_evidence` and is eligible to remain visible.

Therefore the first missing-evidence point is normally upstream of visibility: missing semantic negative, misrouted semantic negative, or loss in the free-text-to-code mapper. The final fail-closed provenance filter then correctly refuses to turn remaining heuristics into facts.

### Product semantics

The current semantics conflate two very different states:

1. **analysis complete, grounded downside established**;
2. **no grounded downside currently established because negative analysis is incomplete/unresolved**.

The second state must not be interpreted or worded as “the game has no downsides”.

Recommended generic state model:

- `grounded_negative_ready`
  - at least one grounded negative with source/evidence/provenance is available;
  - normal completed explanation state.

- `negative_analysis_incomplete`
  - no grounded negative has yet been established;
  - may have heuristic candidates or may have no candidate at all;
  - explicitly means evidence is incomplete, **not** that the game is risk-free.

- an exceptional unresolved subtype/reason may record why the worker could not establish a grounded downside from authorized evidence, but it must still remain an incomplete/exceptional analysis state rather than a positive claim about the game.

For UI/readiness, the smallest safe product behavior is:
- keep ranking/commercial inclusion unchanged;
- do not fabricate or expose heuristic negatives;
- if a card remains visible before semantic completion, show a neutral analysis-status marker such as “анализ минусов ещё не завершён”, not a fake negative and not “рисков не найдено”;
- do not label that card's explanation analysis as complete/ready until grounded negative evidence exists or an explicitly authorized exceptional-unresolved policy has been satisfied.

Withholding the entire recommendation from ranking would couple this explanation-completeness defect to paid ranking/Taste behavior, outside this task's boundary. The safer bounded semantics are therefore **visible recommendation may remain, but its explanation readiness is explicitly incomplete and queued for completion**.

There is no existing canonical readiness field that fully expresses this negative-specific state today. The existing output validator only validates honesty of text that is present. Therefore a new ad-hoc UI-only flag should not be invented in isolation; the state needs to be bound to the existing semantic result/queue contract first.

### Scope of impact

**Systemic in the measured current-producer sample.**

Evidence:
- 28/30 top-ranked generated cards (`93.3%`) had no visible grounded negative;
- the validator still returned PASS;
- canonical Taste ingestion explicitly permits `INCLUDE + negative_evidence=[]`;
- current persisted Taste data contains included entries with empty negative evidence;
- at least one included result contains a negative concern in the wrong field;
- at least one Taste-v3 included result has explicit negative evidence that the narrow mapper cannot classify.

This is therefore not one bad title, one stale card, or one final-rendering bug. It is a contract/readiness + free-text mapping coverage gap across the semantic pipeline.

The investigation does **not** claim that 93.3% of all 442 committed production cards lack a groundable downside. The precise all-442 modern provenance split is not encoded in the currently committed pre-fix artifact. The proven statement is that the issue is systemic in the real current-producer top-30 and the architecture permits the same state catalog-wide.

Efficiency / reusable lesson: distinguish `absence of grounded evidence` from `evidence of absence` at the semantic-result contract, and use typed/provenanced semantic output rather than relying on an open-ended free-text keyword mapper for a readiness-critical field.

### Status

`complete`

The bounded diagnosis is complete. A real product defect is confirmed, but this READ-ONLY/RECON task did not implement it.

### Recommended next step

Create one bounded **CONTRACT/RECON** task for grounded-negative completeness on the existing Taste semantic architecture.

That task should define, before implementation:
- how a normal `INCLUDE` semantic result proves at least one grounded downside without incentivizing fabrication;
- an explicit exceptional/unresolved result state when authorized evidence is insufficient;
- a typed/provenanced negative category/code contract so valid semantic negative evidence is not silently lost by an open-ended lexical mapper;
- a GitHub-owned work/readiness code for visible recommendations whose negative analysis is incomplete;
- how the final payload exposes `negative_analysis_incomplete` while preserving empty user-facing `risks[]` until evidence is grounded;
- how the existing `existing_scheduled_chatgpt_taste_worker` receives that work through the existing GitHub queue/runtime path.

Do not create a second scheduler/runtime, do not manually process titles, and do not solve the gap by broadening heuristic visibility or forcing workers to invent one negative per game.