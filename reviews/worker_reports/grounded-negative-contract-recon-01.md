# Grounded Negative Contract Recon 01

Status: **implementation-grade proposal only; no production code, router, queue, or scheduler changes were made in this task.**

This report continues from `reviews/worker_reports/card-negative-analysis-gap-01.md`. It does not repeat that diagnosis. The design below closes the identified seam between Taste semantics, the existing GitHub-owned Taste queue, negative-risk mapping, and paid-card readiness.

## Decision summary

1. Introduce a new Taste result/cache generation (proposed `TASTE-SEMANTIC-RESULT-V4` / cache entry V4) with an explicit `negative_analysis_status` and structured `negative_findings`.
2. A normal completed negative analysis has exactly one semantic state: `complete_with_confirmed_negative`, and it requires at least one grounded structured finding.
3. The truthful no-proof state is `incomplete_no_confirmed_negative`. It is admissible as a worker result but is **not** normal paid-card readiness.
4. Reuse the existing `data/production/pre_ai/chatgpt_taste_queue.jsonl` and scheduled Taste worker. The one new canonical work code is:

   `resolve_grounded_negative_analysis`

5. Do not invalidate/re-evaluate otherwise-valid Taste verdicts and normalized factors merely to migrate this contract. A fit cache hit can remain a fit cache hit while being independently `negative-unresolved` and re-entering the same Taste queue for only the missing semantic work.
6. Replace raw-text phrase parsing in `map_negative_evidence` with a structured code/category flow. Raw evidence remains preserved for provenance; downstream risk code/text no longer depends on English wording matching a narrow mapper.
7. A paid card is normal-ready only when the current bound Taste result contains at least one confirmed structured negative and that finding survives as at least one grounded visible Taste risk. An unresolved negative analysis blocks normal paid-card admission; no synthetic fallback minus is allowed.

---

## A. Taste result schema

### Proposed V4 fields

Keep the existing identity/binding/verdict fields and add the following required result fields whenever `work_required` contains `evaluate_taste_fit` or `resolve_grounded_negative_analysis`:

```json
{
  "negative_analysis_status": "complete_with_confirmed_negative",
  "negative_findings": [
    {
      "category": "repetition",
      "code": "unchanged_repetition",
      "evidence": "The core loop repeatedly asks the player to perform the same actions under largely unchanged conditions.",
      "risk_text_ru": "Основной цикл заметно повторяет одни и те же действия без достаточного изменения условий — такой повтор для тебя быстро становится утомительным."
    }
  ],
  "negative_evidence": [
    "The core loop repeatedly asks the player to perform the same actions under largely unchanged conditions."
  ]
}
```

`negative_analysis_status` enum is deliberately only:

- `complete_with_confirmed_negative`
- `incomplete_no_confirmed_negative`

There is **no** normal `complete_no_negative` state. Under the desired product contract, “reviewed but no downside can currently be grounded” is an exceptional/incomplete state, not a normal completed paid-card state.

### Finding shape

Every `negative_findings[]` object requires:

- `category`: canonical broad category enum;
- `code`: canonical stable finding/risk code;
- `evidence`: non-empty raw grounded candidate evidence, bound by the existing `candidate_context_sha256` and `profile_blob_sha` submission bindings;
- `risk_text_ru`: non-empty Russian user-facing risk statement directly supported by `evidence` plus the bound canonical taste profile. It must not introduce a new game fact or a user preference that is not grounded by those inputs.

Initial category/code catalog should reuse the current downstream semantic risk codes so cutover does not rename established risks:

| category | code |
|---|---|
| `repetition` | `unchanged_repetition` |
| `activity_balance` | `low_active_gameplay` |
| `direction` | `directionlessness` |
| `management_routine` | `management_routine` |
| `difficulty_friction` | `difficulty_punishment` |
| `stealth_friction` | `stealth_restart_pressure` |
| `other_grounded` | `other_grounded_taste_risk` |

`other_grounded_taste_risk` is an intentional escape hatch for a real, grounded downside that does not fit the first taxonomy. It prevents a valid negative from disappearing merely because the taxonomy has not yet received a dedicated code. It should have neutral/no ranking penalty until explicitly assigned one; it is still valid for the visible-minus readiness invariant.

### Status consistency rules

For `complete_with_confirmed_negative`:

- `negative_findings` length MUST be >= 1;
- every finding MUST pass the structured shape and code/category allowlist;
- `negative_evidence` MUST equal the ordered projection `[finding.evidence for finding in negative_findings]` during the V4 compatibility period;
- no empty evidence or empty `risk_text_ru` is valid.

For `incomplete_no_confirmed_negative`:

- `negative_findings` MUST be `[]`;
- `negative_evidence` MUST be `[]`;
- the worker is explicitly saying it cannot ground a real downside from the currently bound evidence;
- the worker MUST NOT invent a weak/generic downside to make the record complete.

`negative_evidence` remains temporarily as a raw-evidence compatibility mirror because current cache/downstream code already uses it. It is no longer the readiness signal. A later major contract may remove that duplicate after all consumers use `negative_findings`.

### Why empty `negative_evidence` cannot encode readiness

An empty array only describes the content of one field. It cannot distinguish:

- “negative analysis was performed and no grounded downside could be confirmed”, from
- “negative analysis was not requested, was skipped, was lost, or is legacy data from before the invariant existed”.

Readiness is a semantic state, so it must be represented explicitly. For legacy V2/V3 cache entries where `negative_analysis_status` is absent, the safe interpretation is **negative-unresolved**, regardless of whether the legacy raw array happens to be empty or non-empty. Legacy raw negatives can be reused as worker input/provenance, but they should be recoded by the semantic worker rather than promoted through the old phrase mapper as proof of V4 completion.

---

## B. Integration with the existing GitHub-owned Taste queue

### Canonical work code

Use exactly:

`resolve_grounded_negative_analysis`

Do not create another queue, workflow scheduler, polling loop, or ChatGPT-owned backlog.

### Queue predicate

The existing pre-AI queue builder should treat fit-cache validity and negative-analysis readiness as separate dimensions.

For a family that has already survived deterministic deal gating and can still become a paid visual card:

1. **New / stale Taste evaluation** (`taste_projection.status == ai_required`):
   - current work remains `evaluate_taste_fit` + `evaluate_normalized_taste_factors`;
   - add `resolve_grounded_negative_analysis` to the same `work_required` array;
   - append `resolve_base_support_condition` when already required by the family.

2. **Valid Taste cache hit with `verdict == INCLUDE`**:
   - if cached `negative_analysis_status == complete_with_confirmed_negative` **and** derived confirmed finding count >= 1, no negative work is required;
   - otherwise add/re-add the same family to `chatgpt_taste_queue.jsonl` with `work_required` containing `resolve_grounded_negative_analysis` (plus any already-required base-support work).

3. **Valid Taste cache hit with `verdict == EXCLUDE`**:
   - no grounded-negative completion is required for visual readiness because the candidate cannot produce a paid recommendation card.

4. **Worker returns `incomplete_no_confirmed_negative` for an INCLUDE candidate**:
   - persist that truthful state;
   - on the next GitHub preparation cycle the same predicate still evaluates unresolved, so the item remains/re-enters the existing Taste queue;
   - GitHub continues to own retry/unresolved/completeness state. The scheduled Taste worker merely consumes the explicit work item.

### Projection/index representation

Do **not** make the new negative requirement part of the existing fit cache-hit predicate in a way that forces a full taste re-evaluation. Instead extend the compact Taste entry index/projection with derived readiness metadata, e.g.:

```json
{
  "negative_analysis_status": "complete_with_confirmed_negative",
  "confirmed_negative_count": 1,
  "negative_analysis_ready": true
}
```

For legacy entries, `negative_analysis_status` is nullable/absent in the compatibility reader and `negative_analysis_ready` is derived as `false`.

The fit cache hit remains based on the current app/profile/model/semantics/fingerprint/context bindings. This preserves valid prior verdicts/factors while allowing a targeted semantic backfill.

### Targeted-ingest safety

For a cache-hit item whose only Taste work is `resolve_grounded_negative_analysis`, ingestion must not allow the worker to silently rewrite the previously accepted fit verdict, fit level, reason code, normalized factors, or bindings.

Shortest safe behavior:

- treat the current bound cache entry as the immutable base;
- validate the returned identity/bindings against queue/current entry;
- update only `negative_analysis_status`, `negative_findings`, and the compatibility `negative_evidence` projection for this work code;
- preserve all other Taste semantics byte-for-byte/value-for-value.

For a work item that also contains `evaluate_taste_fit`, ingestion continues to accept the full new semantic result normally.

This is preferable to forcing every legacy cache hit through a full Taste re-evaluation just to acquire the missing negative readiness fields.

---

## C. Mapper redesign: structured finding -> stable risk

### Replace phrase matching

`refine_visual_ranking.py::map_negative_evidence` must stop deciding whether a negative is valid by substring matching raw English prose.

Replace that flow with a `map_negative_findings`-style transformation whose admission is structural:

```text
Taste V4 negative_findings[]
    -> validate category/code pair
    -> preserve raw evidence + bound provenance
    -> emit stable risk code
    -> emit persisted risk_text_ru (no phrase re-interpretation)
    -> source = taste_negative_evidence
    -> optional ranking score from a GitHub-owned code catalog
```

The mapper MUST NOT inspect `finding.evidence` to decide whether the finding survives.

### Stable downstream form

A mapped row should retain at least:

```json
{
  "code": "unchanged_repetition",
  "score": 4,
  "text": "Основной цикл заметно повторяет одни и те же действия без достаточного изменения условий — такой повтор для тебя быстро становится утомительным.",
  "source": "taste_negative_evidence",
  "category": "repetition",
  "evidence": "The core loop repeatedly asks the player to perform the same actions under largely unchanged conditions."
}
```

For the six existing dedicated codes, the GitHub-owned catalog may retain the current deterministic ranking scores. `risk_text_ru` is already persisted semantic output and should be passed through rather than regenerated from English phrases.

For `other_grounded_taste_risk`, preserve `risk_text_ru`, expose the risk, and default to neutral/no ranking penalty until a dedicated taxonomy/ranking rule is added. The important contract is **never drop a grounded finding because its raw prose is unfamiliar**.

### Provenance

Keep the current fail-closed grounded source identity (`taste_negative_evidence`) so `card_explanation_policy.py` continues to distinguish grounded semantic risks from `derived` heuristics.

Extend risk provenance so debugging can trace a visible minus back to:

- `taste_subject_key` / current card subject;
- finding `code` and `category`;
- raw `evidence` (or an exact persisted reference/hash to it);
- current `candidate_context_sha256` and `profile_blob_sha` already bound by the Taste result.

Derived structural heuristics remain useful for ranking/inspection but **do not satisfy** the mandatory confirmed-negative readiness invariant.

Likewise, existing `confirmed_practical` risks may remain additional user-visible risks, but they should not substitute for the mandatory completed Taste negative-analysis witness. Keeping the gate Taste-owned avoids coupling readiness to later practical-enrichment timing.

---

## D. Stop rule / completion semantics

### Normal-complete paid card

A paid recommendation card is `normal_complete` only if all existing paid-card prerequisites are satisfied **and** all of the following are true for its current bound Taste subject:

1. Taste verdict is `INCLUDE` at the current profile/model/semantics/fingerprint/context binding.
2. `negative_analysis_status == complete_with_confirmed_negative`.
3. `negative_findings` contains at least one valid finding.
4. Structured mapping emits at least one grounded Taste risk with `source == taste_negative_evidence`.
5. The final explanation payload has `risk_status.has_described_risk == true` and at least one visible risk whose provenance points to that Taste finding.

This creates an end-to-end witness: semantic finding -> structured mapper -> grounded visible minus.

### Exceptional/incomplete state

For an otherwise-eligible INCLUDE candidate:

```text
negative_analysis_status == incomplete_no_confirmed_negative
```

means:

- semantic analysis is not complete for normal-card purposes;
- the candidate stays unresolved in the GitHub-owned Taste work state;
- it must not be emitted as a normal ready paid card;
- no generic “possible downside”, heuristic-only risk, or fabricated weak negative may be inserted to satisfy the invariant.

Recommended fail-closed production behavior at cutover: an unresolved paid candidate counts as incomplete preparation and prevents replacement of the last successful normal paid visual payload, rather than silently dropping the candidate and claiming complete coverage. If product policy later wants an acknowledged exceptional omission, that must be a separate explicit completeness policy change; it should not be implicit in this mapper/readiness fix.

---

## E. Minimal safe implementation plan

### 1. Contract + validators first

- Bump `config/taste_result_contract.json` to V4 and add `negative_analysis_status` + structured `negative_findings` rules above.
- Bump `config/taste_cache_entry_contract.json` with V4 required fields for new entries while keeping V2/V3 compatibility readers.
- Treat old entries missing the new status as fit-reusable but negative-unresolved.
- Extend `scripts/validate_taste_v3_contract.py` (rename/version as appropriate) and cache validation tests before changing production queue behavior.

Required tests:

- `complete_with_confirmed_negative` + zero findings -> reject;
- `incomplete_no_confirmed_negative` + non-empty findings/evidence -> reject;
- invalid category/code pair -> reject;
- empty evidence or empty `risk_text_ru` -> reject;
- legacy entry without status -> accepted only as compatibility input and derives `negative_analysis_ready=false`.

### 2. Index/projection readiness without invalidating fit

- Extend `build_taste_cache_index.py` compact entry generation with negative status/count readiness metadata.
- Extend `build_pre_ai_taste_projection.py` to expose `negative_analysis_ready` separately from `status == cache_hit`.
- Do **not** change `taste_semantics_sha256` merely to force this migration; the current valid fit result should remain reusable.

Tests:

- old V3 cache hit remains a fit cache hit but negative-unresolved;
- V4 complete entry is both fit-cache-hit and negative-ready.

### 3. Existing queue + ingest

- In `build_pre_ai_chatgpt_payload.py`, add `resolve_grounded_negative_analysis` under the exact predicate in section B.
- New evaluations always request the work code.
- INCLUDE cache hits that are not negative-ready re-enter the same queue even when no other AI work is needed.
- Extend `ingest_taste_results.py` to validate/persist V4 findings and perform a targeted merge for negative-only cache-hit work.
- Update the existing scheduled Taste worker instructions to honor the new `work_required` code; do not create a new worker/scheduler.

Tests:

- INCLUDE cache hit + unresolved -> queued with `resolve_grounded_negative_analysis`;
- INCLUDE cache hit + complete finding -> not queued for negative work;
- EXCLUDE cache hit -> not queued for negative readiness;
- negative-only ingest cannot change verdict/fit/reason/factors/bindings;
- truthful incomplete result persists and is requeued by the next GitHub preparation cycle.

### 4. Structured mapper

- Replace `map_negative_evidence` phrase detection with direct structured finding mapping.
- Preserve the current grounded source class and raw provenance.
- Keep `other_grounded_taste_risk` as the no-drop escape hatch with neutral/no ranking penalty.

Tests:

- a valid finding whose English evidence contains none of the old mapper keywords still produces a visible grounded risk;
- `other_grounded_taste_risk` survives mapping;
- `derived` heuristic-only risk still cannot satisfy grounded readiness.

### 5. Paid-card readiness gate

- Upgrade `validate_card_explanations.py` and final payload admission so normal paid cards require the end-to-end grounded Taste risk witness from section D.
- Unresolved negative analysis is a preparation failure/incomplete state, not `risks=[]` normal output.

Tests:

- paid card with no grounded Taste risk -> reject normal readiness;
- paid card with only `confirmed_practical` or `derived` risk -> does not satisfy the mandatory Taste gate (though practical risk may still be displayed as an additional risk);
- paid card with structured confirmed Taste finding -> passes;
- mapper cannot erase a valid structured finding without causing a validator failure.

### 6. Cutover / backfill

Use a two-phase cutover on the existing runtime:

1. Deploy V4 read/write/index/projection/queue support and let GitHub enqueue legacy INCLUDE cache hits as `resolve_grounded_negative_analysis` without invalidating their existing fit verdicts/factors.
2. Drain/backfill that work through the existing scheduled Taste worker and normal Taste inbox ingestion.
3. When the current otherwise-eligible paid scope has zero negative-unresolved entries, atomically enable the structured mapper + strict paid-card readiness gate.
4. From then on, any newly unresolved candidate remains in the same queue and blocks normal completeness until a real grounded minus is confirmed.

Do not bootstrap V4 completion by running legacy raw strings through the old phrase mapper. That would encode the exact loss mechanism this contract is intended to remove.

---

## Recommended implementation boundary

The smallest correct change is **not** “require `negative_evidence` to be non-empty”. That would make fabrication the easiest way to pass validation and would still leave the phrase mapper as a loss point.

The correct boundary is:

```text
explicit semantic completion state
+ structured grounded findings
+ existing GitHub-owned unresolved/requeue ownership
+ code-based no-drop mapping
+ final normal-card readiness witness
```

No new queue, no new scheduler, and no ChatGPT-owned retry state are required.