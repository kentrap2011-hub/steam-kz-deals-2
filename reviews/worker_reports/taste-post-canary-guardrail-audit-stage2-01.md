# Taste Post-Canary Guardrail Audit — Stage 2

- task_id: `taste-post-canary-guardrail-audit-stage2-01`
- lifecycle: `in_progress`
- started_utc: `2026-09-10T06:48:37Z`
- completed_checks: `5/7`
- next_action: `check 6`

## Checks

1. Current one-game preparation freezes the live profile from an immutable repository commit and verifies exact content: `PASS`
   - `scripts/build_taste_current_main_canary.py` treats `kentrap2011-hub/stopgame-ratings-data:gaming_taste_live.json` as the canonical authority required by policy, not committed `taste_projection.json`.
   - `freeze_current_live_profile()` resolves canonical `main`, fetches `gaming_taste_live.json` with `?ref=<resolved commit>`, validates decoded bytes against the advertised Git blob SHA, records SHA256 and byte count, and writes an immutable commit-pinned binding/snapshot.
   - `validate_frozen_profile_binding()` rechecks byte count, Git blob SHA and SHA256 against the frozen snapshot.
   - Predecessor implementation report confirms the stale committed projection authority was deliberately removed from this preparation path and the focused current-main validation proved the exact frozen blob propagated through projection, payload and prepared tuple.

2. Parallel profile changes are handled safely with bounded fail-closed retries: `PASS`
   - The same `freeze_current_live_profile()` performs head-before / commit-pinned file fetch / head-after confirmation. If head changed before freeze completion, that candidate is discarded and the next attempt starts from the newer head.
   - Once a stable head is confirmed, all later preparation is bound to the immutable frozen snapshot; a later live-profile change cannot rewrite or mix the tuple.
   - `PROFILE_FREEZE_MAX_ATTEMPTS = 3`; churn across all attempts raises a retry-later `CanaryError` and stops rather than looping indefinitely.
   - Predecessor focused tests explicitly passed for update-before-freeze selecting the newer state, update-after-freeze preventing mixed versions, and continuous churn failing closed after the bounded attempts.

3. Semantic producer/ingest path enforces generation 2, exact bindings and the V5 fence: `PASS`
   - Current `config/taste_result_contract.json` is canonical `TASTE-SEMANTIC-RESULT-V5`, with active producer `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`, active generation `2`, and mismatch policy `reject_before_ingest`.
   - `.github/workflows/ingest-taste-batch.yml` runs producer-fence regression, the active producer fence, normalized-factor validation and transactional proof before `process_taste_inbox.py`.
   - `scripts/taste_producer_fence.py` refuses any contract other than V5 and rejects producer-id or producer-generation mismatch against the active fence.
   - `scripts/ingest_taste_results.py` requires current profile blob/model/semantics/source bindings and exact queue `appid`, `taste_fingerprint` and `candidate_context_sha256` before accepting a result; V5 evidence/negative validation is invoked with `require_v5=True`.
   - The real Chernobylite acceptance predecessor recorded the same current path passing the producer fence with generation 2 and exact immutable tuple bindings before canonical ingest.

4. Evidence sufficiency, normalized factor validation and price-blind/non-review-sentiment protections remain active: `PASS`
   - `scripts/taste_evidence_contract.py` requires all V5 evidence fields, constrains evidence state/confidence/basis combinations, requires sufficient evidence to map to an INCLUDE strong/moderate fit with medium/high confidence, and keeps public/review quality findings separate with `personal_relevance: unresolved`.
   - `scripts/taste_cache_common.py::validate_taste_factors()` requires exactly the five canonical factor IDs, numeric non-boolean values, each within `0..100`.
   - `scripts/ingest_taste_results.py` requires `taste_factors` whenever the queue requests `evaluate_normalized_taste_factors`, validates them, requires at least two explicit positive evidence items for INCLUDE, and validates positive/negative evidence text.
   - The ingest path rejects price/discount/wishlist/SteamDB/historical-price/sale/commercial fragments as Taste evidence; current V5 contract explicitly sets `price_blind: true`, lists commercial inputs and `review_sentiment_or_percentage_as_fit_evidence` as forbidden, and states public review sentiment percentage is not Taste evidence.
   - The Chernobylite real acceptance predecessor proved these guards on one actual result: evidence/factors passed and no forbidden commercial/price/review fields were used as Taste-fit evidence.

5. Normal daily operation requires no user pause, quiet window or manual profile freeze: `PASS`
   - Checks 1–2 establish that preparation itself resolves the current canonical profile, freezes an immutable commit/file snapshot, detects a concurrent pre-freeze update, retries at most three times, and then uses only the frozen snapshot for the tuple.
   - A later profile update is handled by immutable tuple binding plus fail-closed ingest validation; it does not require the user to hold the profile still.
   - The implementation predecessor explicitly identifies the former defect as a preparation-time binding defect rather than a reason for a user-controlled quiet window, and its concurrency tests proved the replacement behavior.
   - Stage 1 separately verified the existing Taste Semantic Producer Scheduled Task is enabled on the permanent daily schedule; normal operation therefore has an existing automated trigger and no manual freeze step.
