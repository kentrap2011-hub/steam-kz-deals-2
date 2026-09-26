# Worker report — Taste Dossier pragmatic evidence model fix 01

## 1. Final status

`complete_ready_for_director_acceptance`

Task: `WORKER_TASK_TASTE_DOSSIER_PRAGMATIC_EVIDENCE_MODEL_FIX_01.md`.

Authoritative implementation continuation: PR #98, branch `worker/taste-dossier-pragmatic-evidence-01`.

Superseded PR #97 was not used for continuation or merge.

Implementation PR #98 was squash-merged to `main` as:

- merge commit: `d3b0e40256b31b5444fe7c5ddd8ced49c078b81c`.

Normal GitHub-owned pre-AI projection activation then completed successfully and pushed:

- projection commit: `c54267ecc55b2e7af32cb05031b2ba872348572d`.

No Scheduled Task action, manual Tiny Snow recovery, Dossier recovery, Deep recovery, or manual production backlog replay was performed.

## 2. Architecture preflight

Confirmed and preserved:

- GitHub remains the control plane for Dossier scope, immutable group planning, binding, strict validation, canonical persistence, recovery eligibility and completeness.
- Scheduled ChatGPT remains only the bounded neutral semantic/web evidence producer with create-only candidate transport.
- Dossier remains profile-agnostic; personalized interpretation remains downstream Deep responsibility.
- Exact product identity remains fail-closed at AppID/product/release/DLC/edition/remake/remaster/sequel boundaries.
- Persisted raw review/post/search-result text, snippets, quotes, usernames, author/account/profile identity, profile URLs and direct/reversible author-derived hashes remain forbidden.
- No new scheduler, queue, retry daemon, crawler, persistent author registry or external evidence store was introduced.
- No fixed source/review/search/page quota was introduced.
- TASTE-014 semantic/adaptive bounded retrieval remains active.
- TASTE-015 neutral downstream-ready coverage sufficiency remains active.
- TASTE-012 temporal completeness remains active.
- Buffered group size remains a transport/durability boundary, not a semantic quota.

The architecture change is limited to evidence usability/provenance semantics and the strict validator rules that previously made permanent per-review identity or transient-author fallback prerequisites.

## 3. Old evidence-model problem

The old TASTE-008/TASTE-010 path treated exact-product Russian-feedback existence and usable player-feedback evidence as requiring an attributable item-level record. A stable neutral locator was preferred; when unavailable, the fallback required transient author/account identity for same-product dedupe.

That model rejected useful evidence when:

- concrete player-feedback text was directly visible in a search/discovery result;
- the result was confidently bound to the exact target product;
- no stable per-item URL/public ref was exposed;
- no permissible transient-author fallback was available;
- or the target page could not later be opened even though usable content had already been observed.

The production trigger was Tiny Snow / appid `1002560`: concrete Russian player feedback was visible in a search result, but a later direct open returned a 436-like transport failure and the old contract forced an unresolved Russian state.

The model also encoded stable-locator numeric recurrence thresholds that made auditability mechanics part of evidence strength rather than optional traceability.

## 4. New allowed evidence modes

The active model now has three explicit acquisition modes:

1. `stable_item`
   - safe neutral item URL or `public_ref` is available;
   - remains the preferred auditability mode;
   - all exact stable-child parent/AppID checks remain strict.

2. `inspected_collection_item`
   - a concrete individual player-feedback card/item was directly inspected on a safe exact-product collection;
   - no child URL/ref is required;
   - no author identity is required or persisted;
   - parent provenance uses `feedback_surface_mode:"concrete_item_collection"` and strict `exact_product_binding`.

3. `search_result_observation`
   - the search/discovery result representation itself directly exposes concrete player-authored/player-feedback content;
   - no snippet/raw text is persisted;
   - no child locator or author identity is required;
   - source provenance uses `feedback_surface_mode:"search_result_representation"` and strict `exact_product_binding`;
   - later failure to open the target page does not invalidate already observed usable content.

A query string, domain hit, locale, aggregate review count/rating or result row without concrete player-authored content remains discovery metadata only.

## 5. Exact-product safety

Locator relaxation did not relax identity.

For locatorless collection/search observations, strict `exact_product_binding` is required with one of:

- `source_appid`;
- `source_title_release`;
- `source_appid_title_release`.

The validator requires these values to match the exact dossier AppID/title/resolved release year according to the selected basis.

Regressions reject:

- wrong AppID;
- base-game feedback used for an exact DLC/edition;
- old/original release evidence used for a remaster/remake where release identity differs;
- sequel/prequel confusion;
- similarly named unrelated product;
- generic source/domain result without exact-product binding;
- query wording alone as identity evidence.

Stable Steam child AppID/container checks remain unchanged for `stable_item`.

A real validation gap found during PR closeout was also fixed: an aggregate-looking `public_ref` such as `120-russian-reviews` could previously pass the generic stable machine-token heuristic. Explicit aggregate/count/rating-style refs are now rejected as stable feedback-item locators, preserving PRAG-04.

## 6. Russian gate changes

`evidence.russian_attempt="found_and_used"` now depends on what was actually observed and used, not on whether a permanent per-item locator or author identity exists.

It is valid when a bound Russian/mixed support record is obtained through:

- `stable_item`;
- `inspected_collection_item`;
- `search_result_observation`.

The retained unresolved states are narrowed:

- `existence_established_retrieval_unresolved` means Russian exact-product activity exists but no usable concrete Russian/mixed feedback content was observed after required materially distinct routes were genuinely exhausted.
- `existence_established_access_unresolved` means a directly observed access/tool blocker prevented observing usable concrete Russian/mixed feedback.

Neither missing locator, missing author identity, nor target-page failure after usable search-result content was already observed is sufficient to force an unresolved state.

Aggregate-only Russian activity still cannot satisfy `found_and_used`.

## 7. Dedupe / recurrence simplification

`feedback_id` and `mention_count` remain as dossier-local compatibility/bookkeeping fields:

- all feedback records use sequential dossier-local `feedback-NNN` join ids;
- these ids are not global review identities;
- `mention_count` equals the number of distinct bound local support records;
- it is not a review-population truth, auditability score, coverage threshold or Dossier-completion requirement.

Recurrence is now qualitative and evidence-grounded:

- one observed concrete support record may establish only `anecdotal`;
- stronger recurrence may be supported by multiple materially independent observations/sources;
- no recurrence level requires N stable locators;
- transient author identity is not a validity or recurrence prerequisite;
- obvious duplicate/aliased stable items and equivalent resurfacing must not inflate support.

The old fixed 3-stable-locator / 5-stable-locator thresholds are no longer active.

## 8. Provenance / privacy behavior

Persisted provenance answers:

> Where was the information observed, and by what acquisition mode?

It no longer tries to establish a permanent globally unique reviewer/review identity for every observation.

Persisted safe fields include source-level URL/public ref, domain/source type, language/freshness/evidence role, exact-product binding when required, acquisition mode, publication date when available and dossier-local join ids.

Still forbidden:

- raw review/post bodies;
- search-result snippets;
- verbatim quotes/excerpts;
- usernames/display names;
- Steam/account/profile IDs;
- author identity;
- profile URLs;
- direct/reversible author hashes or predictable author-derived pseudonyms.

The transient-author fallback is explicitly superseded as an evidence-validity requirement. No persistent author registry was introduced.

## 9. Schema / validator changes

The active semantic binding is:

- evidence contract revision: `pragmatic-observed-feedback-2026-09-26`;
- worker schema revision: `pragmatic-observed-feedback-2026-09-26`;
- worker prompt revision: `web-evidence-v2-pragmatic-observed-feedback-v1`.

Strict validation now checks:

- allowed acquisition mode;
- strict source/result exact-product binding for locatorless modes;
- stable-item physical identity when a stable locator is used;
- safe source provenance;
- no author/profile/raw-content persistence;
- observation/conflict support binding;
- exact language projection;
- Russian-attempt consistency;
- temporal completeness;
- full TASTE-015 coverage attestation.

It no longer rejects otherwise usable observed evidence solely because:

- no child item URL exists;
- no stable public item ref exists;
- no transient author is retained;
- a target page failed to open after a usable search-result representation had already been observed.

The validator continues to reject aggregate-only metadata as feedback evidence.

## 10. Files changed

PR #98 changed:

- `.github/workflows/validate-taste-dossier-buffered.yml`
- `PROJECT_DECISIONS.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier_compact_provenance.py`
- `scripts/taste_steam_review_dossier_strict.py`
- `scripts/taste_steam_review_dossier_test_fixture.py`
- `scripts/test_taste_dossier_contract_contradictions_fix.py`
- `scripts/test_taste_dossier_identity_provenance_generation_fix.py`
- `scripts/test_taste_dossier_pragmatic_evidence_model.py`
- `scripts/test_taste_dossier_semantic_bounded_retrieval.py`
- `scripts/test_taste_dossier_steam_store_review_card_parent.py`
- `scripts/test_taste_dossier_transient_author_fallback.py`
- `scripts/test_taste_dossier_validator_generator_parity_fix.py`
- `scripts/test_taste_steam_review_dossier_contract_gaps.py`
- `scripts/test_taste_steam_review_dossier_prepublication.py`
- `scripts/test_taste_steam_review_dossier_semantic_consistency.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`

Durable rationale was added as `PROJECT_DECISIONS.md#TASTE-016`.

`PROJECT_ROUTES.md` was not changed because the operational route/ownership did not change.

## 11. PRAG-01..PRAG-15 results

All explicit PRAG regressions passed in PR Dossier validation run #184.

- **PRAG-01 PASS** — Tiny Snow / appid 1002560: exact-product Russian search-result evidence validates without per-item locator; simulated target open status 436 does not erase already observed evidence; Russian state is `found_and_used`.
- **PRAG-02 PASS** — exact-product collection card supports evidence without stable child URL/ref or author identity.
- **PRAG-03 PASS** — `stable_item` remains valid and first in preferred auditability order.
- **PRAG-04 PASS** — aggregate-only Russian activity is not a feedback record; closeout additionally fixed aggregate-like stable `public_ref` acceptance.
- **PRAG-05 PASS** — query text alone cannot satisfy exact-product binding.
- **PRAG-06 PASS** — wrong AppID, DLC/base-game mismatch, release/remaster mismatch, sequel, similar-title and generic-domain cases fail closed.
- **PRAG-07 PASS** — raw snippet/author fields and profile-scoped provenance are rejected.
- **PRAG-08 PASS** — duplicate/aliased stable surfacing cannot inflate support.
- **PRAG-09 PASS** — no hidden stable-locator minimum remains for recurrence/sufficiency.
- **PRAG-10 PASS** — Russian `found_and_used` accepts search-result and collection modes.
- **PRAG-11 PASS** — unresolved Russian states represent genuine lack of usable concrete content/access, not locator unavailability.
- **PRAG-12 PASS** — TASTE-015 still rejects materially unresolved/narrow coverage.
- **PRAG-13 PASS** — TASTE-012 historical/current temporal checks remain strict.
- **PRAG-14 PASS** — no scheduler/queue/retry/crawler/persistent author registry was added; GitHub ownership remains intact.
- **PRAG-15 PASS** — buffered validation/traversal and GitHub persistence/recovery ownership remain unchanged.

## 12. Workflow / run refs

Final PR head before merge:
`43e76b553c4e6ca46a6f9f4e871e7ff758b5cadf`.

PR validation:

- `Validate buffered Steam review dossier runtime` — run #184, run id `36212911900`: **success**.
  - compilation: success;
  - execution ownership: success;
  - daily snapshot: success;
  - buffered submission: success;
  - same-day preservation: success;
  - strict recovery: success;
  - prepublication parity: success;
  - contract-gap: success;
  - language binding: success;
  - semantic consistency: success;
  - semantic bounded retrieval / TASTE-014: success;
  - purpose and coverage sufficiency / TASTE-015: success;
  - pragmatic observed evidence / PRAG-01..15: success;
  - superseded transient-author compatibility: success;
  - Steam Store review-card parent: success;
  - contract contradiction closeout: success;
  - identity provenance generation: success;
  - validator-generator parity: success;
  - package identity: success;
  - story DLC scope: success;
  - parallel/nonblocking group behavior: success;
  - canonical-writer coalescing liveness: success.

- `Validate backlog dispositions` — run #1227, run id `36212911901`: **success**.

Post-merge push validation on merge commit `d3b0e40256b31b5444fe7c5ddd8ced49c078b81c`:

- `Build pre-AI deterministic payload` — run #203, run id `36212950419`: **success**.
- `Validate execution ownership` — run #207, run id `36212950383`: **success**.
- `Validate backlog dispositions` — run #1228, run id `36212950417`: **success**.

## 13. Projection / binding activation

The normal GitHub-owned pre-AI build created and pushed:

- `c54267ecc55b2e7af32cb05031b2ba872348572d` — `Refresh atomic pre-AI payload`.

Fresh `main` after that commit was read directly.

Current Dossier projection:

- snapshot: `b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`;
- prepared date: `2026-09-26`;
- required items: `444`;
- group count: `148`;
- next pending sequence: `1`;
- accepted/completed items at activation: `0`;
- remaining required items: `444`.

Both:

- `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `data/production/pre_ai/taste_steam_review_dossier_work.json`

carry the same active binding:

- evidence contract revision: `pragmatic-observed-feedback-2026-09-26`;
- worker schema revision: `pragmatic-observed-feedback-2026-09-26`;
- worker prompt revision: `web-evidence-v2-pragmatic-observed-feedback-v1`;
- evidence contract SHA-256: `d8fe0bbb2b98db51fe373dc76758e16281869d0a8cb5e8823ba92a2541dd1cc4`;
- worker schema SHA-256: `466e43c6cb7d59e44f6c3077fc270660a3917bcaee86363b84430141425b4c22`;
- worker prompt SHA-256: `2fc41f2efe961775e447ff6f073ab716adac1c00b9597f28b659e8551a6497a4`.

This confirms normal projection activation rather than manual binding surgery.

## 14. Production observations

No real Dossier semantic production group was manually executed by this worker.

No Tiny Snow group was manually retried or recovered.

No Scheduled Task was run, edited, enabled, disabled, paused, renamed, rescheduled or recreated.

The only production-facing action was the normal GitHub-owned post-merge deterministic projection rebuild triggered by repository changes.

## 15. Unresolved

None within the authorized implementation/validation scope.

The new snapshot is intentionally pending semantic Dossier work under the existing Scheduled worker/control-plane architecture. This task does not authorize executing that backlog or manually recovering historical groups.

## 16. Director recommendation

Accept `taste-dossier-pragmatic-evidence-model-fix-01`.

The Dossier evidence model now accepts trustworthy exact-product player feedback based on what the worker actually observed rather than requiring a permanent identity for every individual review. Exact product safety, privacy, temporal truth, TASTE-014 boundedness, TASTE-015 coverage sufficiency and GitHub control-plane ownership remain strict. Tiny Snow's specific locator/open-failure class is regression-covered without making aggregate/query-only evidence admissible.
