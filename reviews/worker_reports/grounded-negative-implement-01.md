# Grounded Negative Implement 01

## Task

Implemented the approved grounded-negative contract through the existing Taste/runtime path without creating a queue, scheduler, polling loop, retry owner, or manual semantic backfill.

Implemented files:

- `config/taste_result_contract.json` -> `TASTE-SEMANTIC-RESULT-V4`
- `config/taste_cache_entry_contract.json` -> `TASTE-CACHE-ENTRY-BINDING-V4`
- `scripts/taste_negative_contract.py`
- `scripts/taste_cache_common.py`
- `scripts/build_taste_cache_index.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/ingest_taste_results.py`
- `scripts/process_taste_inbox.py`
- `scripts/grounded_negative_visual.py`
- `scripts/normalize_visual_media_urls.py`
- `scripts/validate_card_explanations.py`
- `scripts/validate_taste_v3_contract.py` (existing filename retained for the existing workflow hook; validator now exercises V4)
- `scripts/test_grounded_negative_contract.py`
- `scripts/test_card_explanation_policy.py`
- `.github/workflows/build-taste-entry-index.yml`

Implementation commits:

- `a06c34819c5f66e2cb1850340efda790dc3d1c36`
- `67ee0f8c2d59226ad74c4f2462e60b40c5d02efc`
- `bc4940b479b5ded1aa9602d47ddd3bc6345c9b7f`
- `372b6019e09b1257b89dcec3a46e86aef73527f0`
- `f6f90a096714e29b2ab91ed8ba5aa59c2a2f364c`
- `74adc6a05b7bcc8c5312c135b56bace93e15c7ad`
- `c3314c049d1124342b662661ee9fa66500162710`
- `8b2a1a58b492500f82a17fe0bcb008147207f3b0`
- `7e21aa5157dd2d23f3f363797b5dc190d4753e20`
- `bd40e520b87f58063c25d2fdfe4176aa821639f2`
- `c7a6a94bb8f23d571824ab838192a1762c408876`
- `832228a741dd5cb79d79e3c756b82f7e5a72fe06`
- `afe75a695ebccb0b46447165e2d6f92f3a3e86e1`
- `5e2873cc3c0eec6ffebce48f9e5ebb1dbb9fc6eb`
- `d9bf84c27a3919c68a0b85ed678e2c6cc7d512c9`

## Contract / compatibility

Canonical new semantic state:

- `negative_analysis_status = complete_with_confirmed_negative`
- `negative_analysis_status = incomplete_no_confirmed_negative`

There is no normal `complete_no_negative` state.

Each V4 `negative_findings[]` row is validated as exactly:

- canonical `category`
- stable canonical `code`
- non-empty grounded `evidence`
- non-empty grounded `risk_text_ru`

Supported initial codes preserve the existing dedicated downstream risk identities and add the no-drop escape hatch:

- `unchanged_repetition`
- `low_active_gameplay`
- `directionlessness`
- `management_routine`
- `difficulty_punishment`
- `stealth_restart_pressure`
- `other_grounded_taste_risk`

`other_grounded_taste_risk` survives as a visible grounded risk with ranking score `0`.

Validation is fail-closed:

- complete + zero findings -> reject;
- incomplete + findings/evidence -> reject;
- category/code mismatch -> reject;
- empty evidence -> reject;
- empty `risk_text_ru` -> reject;
- V4 compatibility `negative_evidence` must equal the ordered projection of `negative_findings[].evidence`.

Legacy V2/V3 entries remain valid compatibility inputs for fit reuse. Missing V4 negative state always derives:

- `confirmed_negative_count = 0`
- `negative_analysis_ready = false`

Legacy free-text `negative_evidence` never promotes such an entry to ready.

Fit cache identity/profile/model/semantic/fingerprint/context checks remain in force. Grounded-negative migration is deliberately orthogonal to accepted fit semantics, so valid existing verdicts/factors are not invalidated solely to acquire V4 negative fields.

The compact per-entry fit index remains schema v2 for existing projection compatibility; V4 negative readiness is projected as a sidecar keyed to the same entries.

## Queue / ingest

The only semantic queue remains:

`data/production/pre_ai/chatgpt_taste_queue.jsonl`

Exact work code:

`resolve_grounded_negative_analysis`

Routing implemented:

- new/stale full Taste evaluation requests `evaluate_taste_fit`, `evaluate_normalized_taste_factors`, and `resolve_grounded_negative_analysis` together;
- valid cache-hit `INCLUDE` with unresolved negative state re-enters the same queue for `resolve_grounded_negative_analysis`;
- valid cache-hit `INCLUDE` already negative-ready does not request this work;
- cache-hit `EXCLUDE` does not require negative-readiness backfill for paid-card readiness;
- an `incomplete_no_confirmed_negative` result remains unresolved and is requeued by the next normal GitHub preparation cycle;
- already-existing `resolve_base_support_condition` work is preserved when applicable.

Negative-only ingest is explicitly immutable for accepted Taste semantics. The accepted worker result shape contains identity/context fields plus only negative-analysis fields. The merge copies the current accepted entry as its base and may update only:

- `negative_analysis_status`
- `negative_findings`
- compatibility `negative_evidence`

The existing verdict, fit level, reason code, positive evidence, normalized factors, profile/model/semantics bindings, fingerprint, candidate-context binding, and original evaluation timestamp are preserved. A negative-only result attempting to submit an unrelated field such as `verdict` is rejected.

Full evaluation rows retain normal full semantic ingest behavior.

## Structured mapper

Final grounded Taste risk admission is now structural rather than phrase-based:

`validated negative finding -> category/code catalog -> persisted risk_text_ru -> grounded provenance`

The structured mapper does not inspect English evidence wording to decide whether the finding survives. Raw evidence is retained in final Taste-risk provenance together with category/code.

Grounded semantic source remains:

`taste_negative_evidence`

`other_grounded_taste_risk` guarantees that a real validated negative outside the initial dedicated taxonomy is still visible while carrying neutral ranking score `0`.

Existing `derived` heuristic risks remain separate and cannot satisfy the mandatory grounded-negative readiness invariant. `confirmed_practical` risks may still appear as additional visible risks, but cannot substitute for the required Taste-owned negative witness.

The legacy text keyword mapper can still execute earlier inside legacy builder code, but it is no longer acceptance-critical: the existing final visual path re-canonicalizes accepted risk/fit state from structured findings before final validation and commit. Therefore unfamiliar valid grounded evidence cannot disappear from an accepted card merely because it misses the old phrase list.

## Readiness gate

A normal paid card is explanation-ready only when the end-to-end witness exists:

1. current bound Taste projection is a valid cache hit;
2. current accepted Taste verdict is `INCLUDE`;
3. `negative_analysis_status == complete_with_confirmed_negative`;
4. at least one valid structured finding exists;
5. structured mapping emits at least one `taste_negative_evidence` risk;
6. final visible risk payload contains at least one such Taste risk with code/category/raw-evidence provenance;
7. `risk_status.grounded_taste_negative_witness == true`.

If the negative analysis is unresolved, finalization raises before normal visual acceptance/commit. It does not synthesize a generic minus, does not expose heuristic suspicion as fact, and does not output a claim equivalent to “no risks found”.

The finalizer also recomputes the existing risk-dependent fit cap/commercial branch from the structured risk set before the normal priority finalization. No paid-ranking weights, discount rules, wishlist rules, or normalized Taste scoring semantics were redesigned.

## Validation

Focused deterministic coverage is executed through existing test/workflow hooks. The canonical run produced:

- `TASTE_V4_CONTRACT_VALIDATION=PASS`
- `CARD_EXPLANATION_POLICY_TESTS=PASS`
- `GROUNDED_NEGATIVE_CONTRACT_TEST=PASS`

Covered regressions include:

- complete-with-confirmed-negative cannot have zero findings;
- incomplete state cannot contain fabricated findings/evidence;
- invalid category/code pair is rejected;
- empty evidence/risk text is rejected;
- legacy fit entry remains fit-reusable but negative-unresolved;
- unfamiliar valid evidence survives structured mapping;
- `other_grounded_taste_risk` survives with score `0`;
- heuristic-only risk cannot satisfy readiness;
- confirmed-practical-only risk cannot satisfy mandatory Taste readiness;
- negative-only ingest cannot rewrite verdict/fit/reason/factors/bindings;
- truthful incomplete result has no fabricated fallback;
- normalized Taste factor scoring remains unchanged.

Smallest existing canonical production route exercised:

`.github/workflows/build-daily-visual-payload.yml`

Acceptance run:

- GitHub Actions run id: `33600489704`
- implementation head exercised: `d9bf84c27a3919c68a0b85ed678e2c6cc7d512c9`
- contract/regression stages: PASS
- final visual acceptance: fail-closed on unresolved grounded-negative readiness, as designed.

The finalizer stopped on current `cache_hit + INCLUDE` cards with `negative_analysis_status=null`, `confirmed_negative_count=0`, `negative_analysis_ready=false`. No partially analyzed replacement visual was committed as normal-ready.

Current GitHub-produced readiness/work counts:

- effective compact Taste entries: **819**
- negative-ready entries: **0**
- negative-unresolved entries: **819**
- legacy-missing negative status: **819**
- source families: **621**
- existing Taste queue rows: **599**
- targeted negative-only backfill rows: **576**
- full/new/stale Taste evaluation rows: **23**
- ready without AI: **0**
- deterministic exclusions without AI: **22**
- family partition complete: **true**

The 22 deterministic exclusions are 7 deal exclusions even if strong plus 15 valid cached Taste-below-moderate exclusions; they do not require paid-card negative-readiness backfill.

## Production state

The implementation is deployed and behaving as designed, but production is waiting on the already-existing scheduled Taste semantic runtime.

Current blocker source:

`data/production/pre_ai/chatgpt_taste_queue.jsonl`

Current blocker work code:

`resolve_grounded_negative_analysis`

Exact pending semantic work: **599 rows = 576 targeted grounded-negative backfills + 23 full Taste evaluations**.

The implementation worker intentionally did not process these games manually. The existing scheduled Taste worker must return V4 semantic results through the normal Taste inbox/ingest path. A confirmed grounded finding can make an eligible row ready. A truthful `incomplete_no_confirmed_negative` result remains unresolved and continues to block normal-card completeness for that row.

No second queue, scheduler, or runtime was introduced.

Efficiency / reusable lesson: `separate semantic readiness from fit-cache validity so contract migrations can reuse accepted fit results and request only the missing semantic dimension through the existing owned queue`

## Status

blocked

## Recommended next step

Allow the already-existing scheduled Taste worker to consume the current 599-row queue with `resolve_grounded_negative_analysis`; after its normal inbox ingestion, rerun the existing canonical daily visual route and verify the resulting bounded top-N sample.