# Grounded Negative Implement 01

Status: **BLOCKED — implementation complete; canonical production acceptance is correctly fail-closed while the existing scheduled Taste worker processes the current grounded-negative work queue.**

This report records the implementation and acceptance outcome only. The previous diagnosis and contract design are not repeated here.

## Implemented runtime contract

The approved grounded-negative scheme is now wired into the existing Taste/runtime path:

- structured grounded negatives are canonical Taste fields (`negative_analysis_status`, `negative_findings`, compatibility `negative_evidence` projection);
- normal completion requires `complete_with_confirmed_negative` with at least one structured finding;
- truthful inability to ground a downside is represented as `incomplete_no_confirmed_negative` with empty findings/evidence and remains unresolved for normal paid-card readiness;
- legacy free-text `negative_evidence` never upgrades readiness by itself;
- the existing `data/production/pre_ai/chatgpt_taste_queue.jsonl` is reused with work code `resolve_grounded_negative_analysis`;
- valid existing Taste verdicts/factors are preserved during negative-only backfill;
- the final visible mapper admits validated findings by stable category/code rather than English keyword matching;
- `other_grounded_taste_risk` is a no-drop escape hatch with ranking score 0;
- a normal paid card is not accepted unless at least one current structured Taste negative survives into visible grounded-risk provenance.

No new queue, scheduler, polling loop, or retry owner was created.

## Files implemented

### Canonical contracts / shared validation

- `config/taste_result_contract.json` -> `TASTE-SEMANTIC-RESULT-V4`
- `config/taste_cache_entry_contract.json` -> `TASTE-CACHE-ENTRY-BINDING-V4`
- `scripts/taste_negative_contract.py`
- `scripts/taste_cache_common.py`

### Existing cache / projection / queue route

- `scripts/build_taste_cache_index.py`
- `scripts/build_pre_ai_chatgpt_payload.py`
- `scripts/ingest_taste_results.py`
- `scripts/process_taste_inbox.py`
- `.github/workflows/build-taste-entry-index.yml`

The compact per-entry index remains schema v2 for fit-cache compatibility. Grounded-negative readiness is an orthogonal sidecar, so legacy valid fit hits are not invalidated merely because they predate the new negative-analysis contract.

### Final card / mapper route

- `scripts/grounded_negative_visual.py`
- `scripts/normalize_visual_media_urls.py`
- `scripts/validate_card_explanations.py`

The existing daily visual route already invokes `normalize_visual_media_urls.py` before final validation/commit. That existing point now performs the structured grounded-negative finalization and fails closed before commit if a normal paid card lacks a current grounded Taste witness.

The legacy text keyword mapper may still execute earlier in the legacy builder, but it is no longer authoritative for accepted output: final risk/fit state is rebuilt from structured findings before acceptance. Therefore unfamiliar but valid grounded findings are not lost because their evidence wording misses a keyword list.

### Regressions

- `scripts/validate_taste_v3_contract.py` now validates the V4 contract while retaining its existing filename/workflow hook.
- `scripts/test_grounded_negative_contract.py`
- `scripts/test_card_explanation_policy.py` invokes the new grounded-negative regressions through the already-existing daily CI path.

No separate CI scheduler/workflow was introduced for the semantic worker.

## Negative-only backfill immutability

When a current cache-hit INCLUDE row needs only `resolve_grounded_negative_analysis`, the accepted worker result shape contains only identity/binding fields plus negative-analysis fields.

The ingest path validates the current accepted cache entry and copies it as the immutable base. It permits changes only to:

- `negative_analysis_status`
- `negative_findings`
- compatibility `negative_evidence`

It preserves the existing values for verdict, fit level, reason code, positive evidence, normalized Taste factors, profile/model/semantics bindings, fingerprint, candidate-context binding, and original evaluation timestamp.

An attempted negative-only result containing a field such as `verdict` is rejected rather than silently rewriting the accepted Taste evaluation.

## Current production work state

The existing GitHub-owned preparation path has already rebuilt current artifacts with the new contract.

### Effective Taste cache/index

- compact Taste entries: **819**
- grounded-negative ready: **0**
- grounded-negative unresolved: **819**
- current negative status class: **819 `legacy_missing`**

This is intentional migration behavior: the old entries remain reusable for their accepted fit semantics, but legacy free text is not treated as V4 completion proof.

### Current consumer family partition

- source families: **621**
- current Taste queue: **599**
- ready without AI: **0**
- deterministic exclusions without AI: **22**
- complete family partition: **true**

The 22 deterministic exclusions are outside paid-card negative readiness:

- deal excludes even if strong: **7**
- valid cached Taste below moderate: **15**

### Existing Taste queue work split

Of the **599** rows in the existing `chatgpt_taste_queue.jsonl`:

- **576** are targeted grounded-negative backfill for otherwise-valid cache-hit INCLUDE evaluations;
- **23** are full/new/stale Taste evaluations and request normal Taste work plus `resolve_grounded_negative_analysis`;
- **0** current otherwise-eligible rows are negative-ready without semantic work.

Targeted rows carry the already accepted `resolved_taste_fit` and request `resolve_grounded_negative_analysis` (plus an already-existing `resolve_base_support_condition` where applicable). They are not transformed into full Taste reevaluations.

If the existing Taste worker cannot confirm a grounded minus for one of these items, it must return `incomplete_no_confirmed_negative`; the item remains/re-enters the same GitHub-owned unresolved queue state. It must not manufacture a weak/generic downside merely to make the card pass.

## Deterministic regression result

The canonical daily route executed the implementation regressions successfully, including:

- `TASTE_V4_CONTRACT_VALIDATION=PASS`
- `CARD_EXPLANATION_POLICY_TESTS=PASS`
- `GROUNDED_NEGATIVE_CONTRACT_TEST=PASS`

The regressions prove at least:

- complete-with-confirmed-negative cannot have zero findings;
- incomplete-no-confirmed-negative cannot carry fake findings/evidence;
- invalid category/code pairs are rejected;
- empty evidence and empty Russian risk text are rejected;
- legacy free text remains negative-unresolved;
- a valid grounded finding whose English evidence does not match legacy mapper keywords survives;
- `other_grounded_taste_risk` survives with neutral ranking score 0;
- heuristic-only and confirmed-practical-only risks cannot satisfy the mandatory Taste witness;
- negative-only ingest cannot rewrite accepted fit semantics;
- normalized Taste-factor scoring behavior remains unchanged.

## Canonical production acceptance

Smallest existing production route used: `.github/workflows/build-daily-visual-payload.yml`.

Acceptance run:

- GitHub Actions run id: **33600489704**
- implementation head tested: `d9bf84c27a3919c68a0b85ed678e2c6cc7d512c9`
- regression/contract stages: **PASS**
- final visual acceptance: **FAIL-CLOSED / BLOCKED AS DESIGNED**

The builder reached the new canonical grounded-negative finalizer and stopped with `RuntimeError: grounded negative readiness incomplete for normal paid visual` on current `cache_hit + INCLUDE` entries whose V4 state is still `negative_analysis_status=null`, `confirmed_negative_count=0`, `negative_analysis_ready=false`.

This is the required stop behavior. No partially analyzed replacement visual payload was committed as a normal ready result.

## Blocker / exact unblock condition

**Blocker owner:** the already-existing scheduled Taste semantic runtime, not a new implementation component.

**Current work source:** `data/production/pre_ai/chatgpt_taste_queue.jsonl`.

**Required work code:** `resolve_grounded_negative_analysis`.

**Current queued work:** 599 rows total = 576 targeted negative backfills + 23 full Taste evaluations.

The implementation task must therefore stop here rather than manually synthesizing or processing semantic backfill. Production acceptance becomes unblocked only as the existing scheduled Taste worker returns grounded V4 results through the normal Taste inbox/ingest path. Confirmed findings will make eligible rows ready; truthful `incomplete_no_confirmed_negative` results remain unresolved and continue to block normal-card completeness for those rows.

No new queue/scheduler is necessary or permitted.

## Implementation commits

- `a06c34819c5f66e2cb1850340efda790dc3d1c36` — grounded-negative shared contract helpers
- `67ee0f8c2d59226ad74c4f2462e60b40c5d02efc` — Taste result V4 contract
- `bc4940b479b5ded1aa9602d47ddd3bc6345c9b7f` — cache V4 compatibility contract
- `372b6019e09b1257b89dcec3a46e86aef73527f0` — cache validation
- `f6f90a096714e29b2ab91ed8ba5aa59c2a2f364c` — negative readiness in compact Taste index
- `74adc6a05b7bcc8c5312c135b56bace93e15c7ad` — existing Taste queue routing
- `c3314c049d1124342b662661ee9fa66500162710` — immutable negative-only ingest
- `8b2a1a58b492500f82a17fe0bcb008147207f3b0` — structured final visual mapper/readiness gate
- `7e21aa5157dd2d23f3f363797b5dc190d4753e20` — existing daily finalization hook
- `bd40e520b87f58063c25d2fdfe4176aa821639f2` — paid-card explanation validator
- `c7a6a94bb8f23d571824ab838192a1762c408876` — V4 contract regressions
- `832228a741dd5cb79d79e3c756b82f7e5a72fe06` — mixed Taste inbox transaction proof
- `afe75a695ebccb0b46447165e2d6f92f3a3e86e1` — existing index workflow compatibility
- `5e2873cc3c0eec6ffebce48f9e5ebb1dbb9fc6eb` — grounded-negative mapper/readiness tests
- `d9bf84c27a3919c68a0b85ed678e2c6cc7d512c9` — run new regressions through existing explanation test path
