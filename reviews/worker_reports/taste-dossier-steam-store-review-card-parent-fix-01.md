# Taste dossier Steam Store review-card parent fix 01

## 1. Task / repo / mode

- Task: `taste-dossier-steam-store-review-card-parent-fix-01`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Source of truth / base: `main`.
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`.
- Scope stayed limited to the Steam Store exact-app parent-collection semantics required for concrete individual review cards used by the existing transient-author fallback.

## 2. Architecture preflight

Architecture preflight passed before the first implementation write.

- GitHub remains the control-plane owner of canonical scope, immutable group planning, strict validation, buffered ingestion, persistence, recovery and completeness.
- Scheduled ChatGPT remains the bounded semantic/evidence worker; this task did not move canonical ownership into interactive chat or the scheduled worker.
- No new recurring stage, scheduler, queue, retry/healing loop, reviewer database, cross-run author mapping or Steam-specific retry path was created.
- Existing group size `3`, atomic full-group publication and maximal-contiguous-prefix semantics remain unchanged.
- Existing Story-DLC, package/pricing/ranking/giveaway/UI and source-agnostic Russian discovery ownership remain unchanged.

## 3. Exact defect proven by live acceptance

The task-provided live acceptance result is treated as authoritative production evidence.

Before this fix, snapshot `99c3601f…ba8b8` expected `g000001` with Crown Trick (`1000010`), Hellish Quart (`1000360`) and Tetris® Effect: Connected (`1003590`) at canonical progress `0/730`.

Hellish Quart and Tetris had usable Russian concrete player-review cards. Crown Trick had an exact-product Steam Store page exposing 120 Russian-language reviews and visibly inspectable concrete Russian review cards, but the active semantics could be read as broadly forbidding a Steam Store app page from being a `player_feedback` source at all. The existing fallback serialization, however, requires its collection parent to classify as a player-feedback surface. That parent/source semantic contradiction left Crown Trick at `existence_established_retrieval_unresolved`, so atomic `g000001` could not be published.

## 4. Exact narrow source-rule change

The existing `feedback_surface_mode:"concrete_item_collection"` model was retained; no new source kind or alternate evidence path was introduced.

For an exact-product Steam Store `/app/{appid}/` page:

- the page itself is still not a player-feedback record, review item or mention;
- when one or more concrete individual review cards are actually visible and inspected on that exact page, the page may be serialized only as the parent collection provenance for `transient_author_deduped` child records;
- that parent uses the exact-app Store URL, `feedback_surface_mode:"concrete_item_collection"`, `player_feedback:true`, and a review-surface source type (`steam_reviews` or `store_user_reviews`);
- in this parent role, `player_feedback:true` means that the surface contains the inspected player-feedback children. It does not convert the Store page or its aggregate summary into a feedback item.

The strict validator now expresses and enforces that narrow distinction.

## 5. What remains forbidden

The following remain forbidden and unchanged:

- treating the Steam Store app page itself as a feedback record or mention;
- turning aggregate review counts, ratings, percent-positive values, language totals or review-summary metadata into mentions;
- satisfying `found_and_used` from aggregate Russian review population alone;
- using the Store app page itself as a normal stable item locator;
- bypassing a neutral stable locator when an accepted one is available;
- persisting usernames, display names, SteamIDs/account ids, vanity ids, profile URLs, direct hashes or predictable author-derived tokens;
- cross-run author identity mapping;
- cross-product/appid substitution, base-game-for-DLC substitution or title-only loose matching;
- weakening recurrence thresholds or normal parent/item alias guards.

## 6. Persisted parent/child schema semantics

The persisted Store parent is source-level collection provenance only:

- exact `store.steampowered.com/app/{exact_appid}/...` URL;
- `feedback_surface_mode:"concrete_item_collection"`;
- `player_feedback:true` as a surface classification;
- review-surface source type.

The persisted child is the existing privacy-safe fallback record:

- `identity_mode:"transient_author_deduped"`;
- dossier-local sequential `fallback-NNN`;
- neutral dossier-local `source-NNN`;
- no child item/profile `url` or `public_ref`;
- author identity discarded after same-product transient dedupe.

Only child records can become bound player-feedback mentions.

## 7. Russian gate interaction

Aggregate Store data remains existence/discovery metadata only. A count such as `120 Russian reviews` cannot satisfy `found_and_used`.

A Russian/mixed concrete review card that is actually inspected, transiently deduped and serialized as a valid fallback child can satisfy `found_and_used` when that child is bound to an observation/conflict. Existing unresolved Russian-existence states remain fail-closed for complete dossier publication.

## 8. Exact-product identity preservation

Exact-product safeguards remain unchanged.

- Store parent appid exposed by the URL must equal the exact dossier appid.
- A mismatched Steam appid is rejected.
- Base-game evidence does not satisfy an exact DLC/edition dossier.
- Story-DLC scope policy is unchanged.
- No title-only loose matching was added.

## 9. Confirmation transient-author privacy/recurrence rules unchanged

TASTE-010 privacy and recurrence rules were not relaxed.

- Stable locator remains the preferred/strongest path.
- Fallback is allowed only after an acceptable neutral item locator is unavailable.
- Author identity is transient worker-memory dedupe material only and is never persisted or hashed.
- `anecdotal` still requires exactly 1 bound record.
- `limited` still requires at least 2 total bound records and may include fallback records.
- `moderate` still requires at least 3 bound `stable_locator` records.
- `strong` still requires at least 5 bound `stable_locator` records.
- Fallback-only evidence remains capped at `limited`.

## 10. STORE-CARD-01..11 results

All eleven focused regressions passed in PR validation run `35372210241` (run #83), job `105688590510`.

1. STORE-CARD-01: Store page itself remains invalid as a stable feedback item — passed.
2. STORE-CARD-02: aggregate Russian count remains existence/discovery metadata only — passed.
3. STORE-CARD-03: Crown Trick exact-app concrete-card fallback is accepted — passed.
4. STORE-CARD-04: no author identity/profile/direct-hash persistence — passed.
5. STORE-CARD-05: Store page is parent collection provenance only — passed.
6. STORE-CARD-06: stable locator remains preferred — passed.
7. STORE-CARD-07: exact appid mismatch is rejected — passed.
8. STORE-CARD-08: fallback recurrence caps remain unchanged — passed.
9. STORE-CARD-09: a valid Russian fallback child can satisfy `found_and_used` — passed.
10. STORE-CARD-10: no concrete card means no fallback — passed.
11. STORE-CARD-11: current three-game `g000001` candidate shape validates — passed.

The same run also passed compilation, execution-ownership validation, daily snapshot, buffered submission, same-day preservation, strict recovery, prepublication parity, contract-gap, language-binding, semantic-consistency, existing transient-author fallback, package identity, Story-DLC and parallel/maximal-contiguous-prefix regressions. Backlog-disposition run `35372210373` (run #754) also passed.

## 11. Crown Trick fixture result

The deterministic Crown Trick fixture uses exact appid `1000010`, exact Store parent `https://store.steampowered.com/app/1000010/?l=russian`, `feedback_surface_mode:"concrete_item_collection"`, and one or more `transient_author_deduped` child records with no persisted author identity.

It validates successfully, including Russian `found_and_used` and fallback recurrence constraints. A Store-parent stable-locator attempt remains rejected.

## 12. Confirmation Hellish Quart/Tetris behavior not regressed

STORE-CARD-11 validates the exact current first-group ordering with:

- Crown Trick through the new Store concrete-card parent/fallback path;
- Hellish Quart through the existing accepted stable-record fixture behavior;
- Tetris® Effect: Connected through the existing accepted stable-record fixture behavior.

Existing transient-author, package identity, Story-DLC and parallel buffered suites also passed, so no regression was detected in the pre-existing Hellish Quart/Tetris-compatible paths.

## 13. PR / CI / merge refs

- Implementation branch: `worker/taste-dossier-steam-store-review-card-parent-fix-01`.
- Implementation PR: #59 — `Taste dossier Steam Store review-card parent fix`.
- Final green dossier CI: run `35372210241` (#83), job `105688590510` — success.
- Final green backlog-disposition CI: run `35372210373` (#754) — success.
- Squash merge to `main`: `355e93452636415e8b5f8ba84d197883315b566f`.
- Normal GitHub-owned activation/rebuild produced atomic pre-AI refresh commit `6137ef1e7210eaa1b693a40237f638ddadbba178`.
- No manual rebind or progress repair was performed.

## 14. Activation/binding/snapshot state

Current compatible activation state after the GitHub-owned rebuild:

- snapshot id: `2db923b8171bcf30caa2a6a0b2e36f4bc21c63143265a92648969d3748f79319`;
- prepared/completed/remaining: `702 / 0 / 702`;
- expected sequence: `1` (`g000001`);
- group count: `234`;
- canonical group size: `3`;
- evidence contract revision: `steam-store-review-card-parent-fix-2026-09-18`;
- worker schema revision: `steam-store-review-card-parent-fix-2026-09-18`;
- worker prompt revision: `web-evidence-v2-steam-store-review-card-parent-v1`;
- exact `g000001`:
  1. Crown Trick — appid `1000010`;
  2. Hellish Quart — appid `1000360`;
  3. Tetris® Effect: Connected — appid `1003590`.

The activation rebuild recomputed the current canonical source scope at 702 rather than the earlier live-acceptance 730. This implementation did not alter Taste eligibility, Story-DLC eligibility, group sizing or progress semantics, and it performed no manual scope/progress repair. The independent source-queue delta was not part of this narrow source-rule task; importantly, the exact first group remained unchanged and the new snapshot is bound to the new contract/schema/prompt hashes.

## 15. PROJECT_DECISIONS ref

`PROJECT_DECISIONS.md` TASTE-010 was amended with the 2026-09-18 Steam Store parent-collection clarification:

- Store app page remains storefront/aggregate provenance, not a feedback item;
- concrete review cards rendered inside it may parent transient-author fallback records;
- aggregate counts remain non-evidence/non-mentions;
- stable locator preference, privacy, direct-hash ban and recurrence caps remain unchanged.

## 16. Confirmation Run now/settings unchanged

Scheduled Task `Taste Steam Review Dossier` `Run now` was not launched in this task.

Scheduled Task settings were not changed. No second scheduled task or producer was created.

## 17. Unresolved

No implementation, CI, merge, binding or snapshot blocker remains.

The only remaining acceptance boundary is live runtime behavior of the existing Scheduled Task against the new compatible `g000001`; this task intentionally does not perform that live run.

The activation-time source-scope movement from the earlier 730 to current 702 was observed but not audited because it belongs to canonical source recomputation rather than this parent-source semantics fix. It does not change the exact live-acceptance target group.

## 18. Status

`complete_ready_for_live_acceptance`

## 19. Exactly one recommended next step

Return to Director. Director decides whether to perform one live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the resulting compatible `g000001`.

## 20. Efficiency / reusable lesson

The main avoidable detour was that two older regressions asserted the exact previous prompt revision/error text rather than the semantic fail-closed behavior. CI exposed those stale assertions sequentially before the new STORE-CARD suite could run. The reusable rule already exists in `KNOWN_WORKER_PITFALLS.md -> PITFALL-001`: when changing implementation/copy/contract markers, update dependent static guards atomically and prefer observable semantic behavior over brittle exact-string checks.

This task now has a dedicated STORE-CARD-01..11 suite wired into the canonical dossier CI, so future changes to Store parent/child semantics, exact appid, privacy or recurrence rules will fail in one focused place instead of requiring live rediscovery.
