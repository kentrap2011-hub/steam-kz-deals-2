# Taste dossier transient author dedupe fallback implement 01 — durable report

## 1. Task / repo / mode

- Task: `taste-dossier-transient-author-dedupe-fallback-implement-01`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base/source of truth: `main`
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`
- Durable status: `complete_ready_for_live_acceptance`

## 2. Architecture/privacy preflight

Architecture preflight passed before the first implementation write.

- GitHub remains control plane owner for canonical scope, immutable group plan, validation, persistence, recovery and activation.
- Scheduled ChatGPT remains a bounded semantic evidence worker; no repository-local Python runtime was added as a Scheduled-worker prerequisite.
- No control-plane responsibility was transferred to the interactive chat.
- No new queue, recurring stage, retry/healing loop, secret service, reviewer registry or cross-game reviewer mapping was created.
- Group size remains 3 and the buffered maximal-contiguous-prefix architecture is unchanged.
- Raw reviewer identity is not canonical state.

## 3. Exact fallback model

The evidence model now has two identity paths.

1. `stable_locator` — preferred normal path with the existing stable non-profile item URL or neutral item-level `public_ref`.
2. `transient_author_deduped` — fallback only when a concrete individual player-feedback item is actually inspected on a reliable exact-product player-feedback collection/source and no acceptable neutral stable item locator is obtainable.

Fallback serialization requires:
- `identity_mode: "transient_author_deduped"`;
- dossier-local sequential `feedback_id` values `fallback-001`, `fallback-002`, ...;
- a neutral dossier-local parent `source_id` of the `source-NNN` form;
- parent `feedback_surface_mode: "concrete_item_collection"`;
- a non-profile HTTPS exact-product collection/source URL;
- normal non-identifying publication-date/language/source metadata when known;
- no fallback item `url` or `public_ref`;
- no cross-run identity claim.

The parent collection is provenance only; it is never itself a feedback record or mention.

## 4. Why direct username/SteamID hash was rejected

A direct deterministic hash of a public username, Steam/account identifier or profile identity is not treated as anonymization. Public identifiers can be enumerable or otherwise re-identifiable, so their direct hashes would still create persistent reviewer linkage.

The implementation therefore persists neither raw reviewer identity nor a direct hash/predictable pseudonym derived from it. The canonical fallback identifier is only a dossier-local sequence number unrelated to the observed author value.

## 5. Preferred stable locator path

The stable path remains first and strongest.

The worker prompt explicitly orders retrieval as:
1. try a neutral stable item identity first;
2. only if that fails and a concrete item plus distinguishable author identity is visible, use transient author dedupe;
3. persist no author identity;
4. serialize reduced-strength fallback evidence.

Existing stable-locator item-level URL/`public_ref`, alias normalization, parent/child relationship and exact-product checks remain intact. A fallback collection-only Steam Store parent is not accepted as a normal stable-locator parent.

## 6. Transient author dedupe mechanics

Author/account/profile identity may be read only transiently in worker memory for same-product dedupe.

- The same transient author observed more than once for the same product produces one fallback record unless an ordinary stable item locator proves distinct physical feedback items.
- Distinct fallback records are allowed only when distinct authors were actually observed on distinct concrete items.
- After dedupe, author values are discarded.
- The worker is instructed not to intentionally write the raw value into candidate artifacts, canonical cache, URLs, refs, source ids, feedback ids, reports or logs.
- Fallback ids restart as dossier-local `fallback-NNN`; they are not reviewer identities.

## 7. Persisted schema shape and proof no identity persists

Machine-readable changes were made in:
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `scripts/taste_steam_review_dossier_strict.py`;
- `scripts/taste_steam_review_dossier_compact_provenance.py`.

The strict validator rejects fallback records that persist an item/profile URL or `public_ref`, use a non-local fallback id, use a non-local fallback parent source id, or contain detectable author/profile identity fields/URLs. The compact provenance policy also remains fail-closed for profile-scoped URLs and now explicitly requires direct-author-hash anonymization to remain disabled.

AUTHOR-FB fixtures serialize only opaque local fallback ids and safe collection provenance; the transient test tokens do not appear in the resulting dossier JSON.

## 8. Deterministic recurrence/count semantics including mixed stable+fallback

`mention_count` remains the exact count of distinct bound feedback records.

Strength is deterministic:
- `anecdotal`: exactly 1 total bound record;
- `limited`: at least 2 total distinct bound records; valid fallback records may contribute;
- `moderate`: requires at least 3 bound `stable_locator` records;
- `strong`: requires at least 5 bound `stable_locator` records.

Therefore:
- fallback-only evidence is capped at `limited` no matter how many fallback cards are present;
- in a mixed set, fallback records count in `mention_count` and can help reach `limited`;
- fallback records never count toward the 3-stable threshold for `moderate` or 5-stable threshold for `strong`.

This rule is enforced by the canonical strict validator for observations and conflicts, not only documented in prose.

## 9. Russian gate interaction

A valid Russian/mixed `transient_author_deduped` record can satisfy `evidence.russian_attempt = "found_and_used"` when it is bound to an observation/conflict.

Aggregate review counts, locale rendering, store metadata or collection surfaces without a concrete inspected item still cannot create a feedback record, mention or `found_and_used` state.

Source-agnostic Russian retrieval and existing hard 8-search / 16-page ceilings remain unchanged. The prompt additionally prevents wasting the entire remaining budget repeatedly chasing a neutral locator after a valid fallback is already available, unless stronger stable evidence is reasonably obtainable.

## 10. Strict validator changes and confirmation stable path was not weakened

Canonical strict validation now:
- distinguishes `stable_locator` from `transient_author_deduped`;
- requires the old item-level stable locator semantics for normal records;
- requires no item locator plus a safe concrete-item collection parent for fallback;
- requires sequential dossier-local `fallback-NNN` ids;
- requires neutral local `source-NNN` ids for fallback parents;
- rejects profile-scoped fallback parent URLs and detectable persisted author/profile fields;
- enforces fallback recurrence strength caps for observations and conflicts;
- retains exact Steam appid checks on exposed product-level player-feedback sources;
- retains the Russian used-record gate.

The only Steam Store relaxation is a narrowly marked `concrete_item_collection` source that may parent fallback records. It remains invalid as a feedback record/mention itself and cannot be used to bypass the normal stable-locator path.

## 11. AUTHOR-FB-01..12 results

PR CI run `35365900891` (workflow run #77, `Validate buffered Steam review dossier runtime`) passed. The focused regression step executed 12 tests and reported `Ran 12 tests ... OK`.

- AUTHOR-FB-01: PASS — neutral recommendation id remains stable/preferred.
- AUTHOR-FB-02: PASS — fallback accepted with no persisted author data.
- AUTHOR-FB-03: PASS — repeated same transient author dedupes before serialization.
- AUTHOR-FB-04: PASS — two distinct transient authors produce two local records and `limited`.
- AUTHOR-FB-05: PASS — 3/5 fallback-only records cannot claim `moderate`/`strong`.
- AUTHOR-FB-06: PASS — mixed stable+fallback uses stable-only thresholds above `limited`.
- AUTHOR-FB-07: PASS — profile-scoped diagnostic shape can be inspected transiently; profile URL does not persist and a leaked profile parent is rejected.
- AUTHOR-FB-08: PASS — aggregate/store page without concrete-item mode remains invalid.
- AUTHOR-FB-09: PASS — valid Russian fallback can satisfy `found_and_used`.
- AUTHOR-FB-10: PASS — wrong exact appid remains rejected.
- AUTHOR-FB-11: PASS — direct-hash/identity-derived local-id workaround is rejected by the chosen local-id format.
- AUTHOR-FB-12: PASS — current Crown Trick/Hellish Quart collection-card fixture is usable without persistent reviewer identity, and the post-story-DLC group shape is preserved.

The same PR run also passed ownership validation and the existing dossier regression suite. Backlog disposition run `35365900912` (run #741) passed.

## 12. Crown Trick / Hellish Quart diagnostic fixture result

The deterministic fixture proves the diagnostic blocker is removed for the intended case:

- Crown Trick (`1000010`): concrete Russian collection-card feedback can serialize as valid fallback evidence when distinct authors are transiently observable and no neutral stable item locator is available.
- Hellish Quart (`1000360`): a profile-scoped recommendation may be inspected transiently, but persisted fallback state contains neither the profile URL nor reviewer identity; the safe exact-product collection parent is persisted instead.

This does not claim that a live Scheduled run has already collected those reviews. The task intentionally stops before live acceptance.

## 13. Exact identity/story-DLC preservation

Exact-product identity remains fail-closed; AUTHOR-FB-10 verifies wrong-appid fallback provenance is rejected.

Current activated snapshot retains `story-dlc-positive-evidence-v1`. Its story-DLC audit reports:
- considered: 1;
- story eligible: 0;
- non-story excluded: 1;
- ambiguous excluded: 0.

`Baldur's Gate 3 - Digital Deluxe Edition DLC` appid `2378500` is classified `non_story_dlc_excluded`, is not present in `ordered_appids`, and is not present in `g000001`.

## 14. PR / CI / merge refs

- Implementation PR: #56 — `Taste dossier transient author fallback`.
- Final green dossier PR CI: run `35365900891`, run #77 — success.
- Companion backlog disposition CI: run `35365900912`, run #741 — success.
- Implementation merge commit: `96834ac23950196b31c0a791c15391fbe83eb711`.
- GitHub-owned activation workflow: `Build pre-AI deterministic payload`, run `35365972092`, run #135 — success.
- Activation atomic pre-AI commit: `e56a141d34b51ad0f91fa19eafcabb5e3eddc728`.
- A later unrelated `Refresh commercial visual payload` commit `0a98bc492d6ce4bda9240fd64c16121106a62533` is currently above the activation commit on `main`; the dossier snapshot/binding below remains the activated state.

## 15. Activation/binding/snapshot state

Normal GitHub-owned activation/rebuild completed successfully. No manual rebind or progress repair was used.

- snapshot id: `99c3601ff39f62af05be2b529854516dcd7e9ba3570948aa6e8c257d62bba8b8`
- prepared: `730`
- completed: `0`
- remaining: `730`
- expected sequence: `1`
- group count: `244`
- canonical checkpoint/group size: `3`
- current checkpoint count: `3`
- stale inbox quarantined during rebuild: `0`
- evidence contract revision: `transient-author-dedupe-fallback-2026-09-18`
- worker schema revision: `transient-author-dedupe-fallback-2026-09-18`
- worker prompt revision: `web-evidence-v2-transient-author-fallback-v1`
- story-DLC policy revision: `story-dlc-positive-evidence-v1`

Exact activated `g000001`:
1. `App_1000010` — Crown Trick — `missing_dossier`
2. `App_1000360` — Hellish Quart — `refresh_required`
3. `App_1003590` — Tetris® Effect: Connected — `refresh_required`

Descriptor snapshot id and binding exactly match the worker index/work manifest.

The rebuilt canonical scope currently reports 730 prepared items rather than the prior 731. This report records the canonical GitHub-owned activation result as produced; no manual scope adjustment was made in this task.

## 16. PROJECT_DECISIONS ref

Added `TASTE-010 — Transient author identity may dedupe concrete feedback when neutral item identity is unavailable`.

It records:
- stable neutral item identity remains preferred;
- public concrete feedback is not discarded solely because the retrieval tool cannot expose its neutral id;
- author identity is transient dedupe-only;
- author identity/direct hashes do not persist;
- fallback auditability/recurrence is reduced;
- privacy, exact product identity, story-DLC policy and control-plane boundaries remain fail-closed.

## 17. Confirmation Run now/settings unchanged

Scheduled Task `Run now` was not invoked.

Scheduled Task settings were not changed.

No live Scheduled worker acceptance run was launched by this implementation task.

## 18. Unresolved

No implementation, CI, activation, binding or snapshot blocker remains.

Live acceptance behavior for the freshly activated `g000001` is intentionally not exercised here because the task explicitly prohibits `Run now`. That decision belongs to the Director.

## 19. Status

`complete_ready_for_live_acceptance`

## 20. Exactly one recommended next step

Return to Director so the Director can decide whether to perform one live acceptance against the fresh/current compatible `g000001`.

## 21. Efficiency / reusable lesson

When a public player-feedback item is visibly concrete but the retrieval surface withholds a neutral item id, the smallest privacy-preserving bridge is not a persistent reviewer pseudonym. Use identity only ephemerally to dedupe, erase it before serialization, persist an explicit lower-auditability local record, and make evidence-strength reduction mechanical in the validator. This preserves useful feedback without creating a reviewer identity system or weakening exact-product controls.
