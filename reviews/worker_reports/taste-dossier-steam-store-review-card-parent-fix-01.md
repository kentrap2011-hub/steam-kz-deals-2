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

The activation rebuild recomputed the current canonical dossier scope at 702 rather than the earlier 730. This delta is now fully closed and is **not** caused by the Steam Store review-card parent implementation.

The implementation merge commit `355e93452636415e8b5f8ba84d197883315b566f` still carried the pre-existing snapshot `99c3601ff39f62af05be2b529854516dcd7e9ba3570948aa6e8c257d62bba8b8` with `730/730` prepared/remaining and source queue SHA `674bba67f999c5ecb58de647e3134fa2881773d84c017cf8f2185a3d45acbd88`. The count changed only in the subsequent normal GitHub-owned activation commit `6137ef1e7210eaa1b693a40237f638ddadbba178`, whose Store snapshot was freshly observed at `2026-09-18T17:05:35.036065+00:00`.

The previous Store snapshot had been observed at `2026-09-18T16:02:26.886958+00:00`. The 28 removed dossier items all belonged to offers whose previous canonical discounted option ended at exactly `2026-09-18T17:00:00+00:00`. After the activation-time Store refresh:
- 20 of those 28 no longer had any active discounted purchase option and were removed before family/Taste queue construction with canonical reason `no_active_discounted_purchase_option`;
- 8 still had a discounted purchase option, but Store selected a different current option via `current_lowest_discounted_option_after_source_change`; all 8 then failed the canonical deal gate even for assumed strong Taste (7 by absolute price/budget gate, 1 by symbolic-discount gate);
- additions to dossier scope were exactly `0`.

The arithmetic also reconciles exactly:
- family count `791 -> 770` because 21 previously active paid-offer families became inactive;
- one of those 21, `App_2903950` (Master Detective Archives: RAIN CODE Plus), was already excluded from the old AI/Taste queue by `deal_excludes_even_if_strong`, so only 20 of those 21 affected dossier scope;
- 8 still-active families became newly `deal_excludes_even_if_strong`;
- therefore dossier source queue `731 -> 703` and eligible dossier scope `730 -> 702`, a net `-28`;
- deterministic exclusions changed `60 -> 67` because the already-excluded `App_2903950` left the family partition (-1) while 8 newly changed current offers entered the deal-excluded bucket (+8), net +7.

No Taste eligibility rule, mailing source population, mechanical eligibility rule or Story-DLC policy changed across this boundary:
- mailing source timestamp stayed `2026-09-17T23:21:42.271350+00:00`;
- mailing source item count stayed `826`;
- mechanically excluded count stayed `20`;
- Story-DLC policy revision stayed `story-dlc-positive-evidence-v1`;
- Story-DLC scope SHA stayed `71acd585e2b86d17187db0dae6668f0b7fa9e5da3d206ac982d5fa6bbff41a7a`.

Therefore the `730 -> 702` movement is a normal independent current-offer/deal recomputation caused by the 17:00 UTC sale boundary, not a side effect of this implementation.

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

The earlier activation-time scope-count question `730 -> 702` is now resolved. Machine-derived before/after comparison proves the delta came from normal current-offer refresh and downstream deal gating at the 17:00 UTC sale boundary, not from the Steam Store review-card parent fix. No scope-count blocker remains.

## 18. Status

`complete_ready_for_live_acceptance`

## 19. Exactly one recommended next step

Return to Director. Director decides whether to perform one live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the resulting compatible `g000001`.

## 20. Efficiency / reusable lesson

The main avoidable detour was that two older regressions asserted the exact previous prompt revision/error text rather than the semantic fail-closed behavior. CI exposed those stale assertions sequentially before the new STORE-CARD suite could run. The reusable rule already exists in `KNOWN_WORKER_PITFALLS.md -> PITFALL-001`: when changing implementation/copy/contract markers, update dependent static guards atomically and prefer observable semantic behavior over brittle exact-string checks.

This task now has a dedicated STORE-CARD-01..11 suite wired into the canonical dossier CI, so future changes to Store parent/child semantics, exact appid, privacy or recurrence rules will fail in one focused place instead of requiring live rediscovery.

## 21. Scope-count closeout — machine-derived 730 -> 702 appendix

### 21.1 Canonical before/after boundary

| Field | Before activation | After activation |
|---|---:|---:|
| commit carrying state | `355e93452636415e8b5f8ba84d197883315b566f` | `6137ef1e7210eaa1b693a40237f638ddadbba178` |
| dossier snapshot | `99c3601ff39f62af05be2b529854516dcd7e9ba3570948aa6e8c257d62bba8b8` | `2db923b8171bcf30caa2a6a0b2e36f4bc21c63143265a92648969d3748f79319` |
| source queue rows | 731 | 703 |
| eligible dossier scope | 730 | 702 |
| additions | 0 | — |
| removed | — | 28 |
| Store snapshot observed_at_utc | `2026-09-18T16:02:26.886958+00:00` | `2026-09-18T17:05:35.036065+00:00` |
| active paid discounted Store entries | 825 | 804 |
| inactive source candidates | 1 | 22 |
| family count | 791 | 770 |
| deterministic exclusions | 60 | 67 |

### 21.2 Reason groups

- **20 dossier items — current offer ended with no replacement discounted option.** All 20 had previous canonical discount end `2026-09-18T17:00:00+00:00`; the 17:05 Store refresh classified them `no_active_discounted_purchase_option`, so they never reached the new family/Taste queue.
- **8 dossier items — current offer changed, but replacement offer failed canonical deal gating.** All 8 had previous source deals ending at `2026-09-18T17:00:00+00:00`; the refresh selected a new current discounted option with `selection_method:"current_lowest_discounted_option_after_source_change"`. Seven failed `price_clearly_unreasonable_after_soft_target_evaluation`; one (Woodle Tree Adventures) failed `symbolic_discount_not_worth_mailing_attention`.
- **No additions.** Exact set comparison of old/new dossier work items produced `added_count=0`.

### 21.3 Full removed list

| AppID | Title | Canonical removal reason | Machine evidence |
|---:|---|---|---|
| 1186220 | Wire Lips | inactive current paid offer | old sale 91% / 261 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 1240590 | Sir Whoopass™: Immortal Death | inactive current paid offer | old sale 50% / 1250 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 1271710 | LEWDAPOCALYPSE Hentai Evil | replacement offer excluded even if strong | source 80% / 198 KZT -> current 10% / 8705 KZT (1651 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 1318690 | shapez | inactive current paid offer | old sale 90% / 290 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 1324340 | Made in Abyss: Binary Star Falling into Darkness | inactive current paid offer | old sale 85% / 1065 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 1449200 | AI: THE SOMNIUM FILES - nirvanA Initiative | inactive current paid offer | old sale 85% / 1395 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 2066020 | Soulstone Survivors | replacement offer excluded even if strong | source 30% / 2870 KZT -> current 21% / 4995 KZT (947 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 2162800 | shapez 2 - Factory | replacement offer excluded even if strong | source 50% / 2750 KZT -> current 9% / 8873 KZT (1683 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 2218750 | Halls of Torment | replacement offer excluded even if strong | source 25% / 1425 KZT -> current 9% / 14868 KZT (2820 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 2532550 | LIZARDS MUST DIE | inactive current paid offer | old sale 75% / 249 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 299460 | Woodle Tree Adventures | replacement offer excluded even if strong | source 81% / 228 KZT -> current 2% / 18305 KZT (3472 RUB); `symbolic_discount_not_worth_mailing_attention` |
| 311240 | Zero Escape: Zero Time Dilemma | inactive current paid offer | old sale 80% / 530 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 3187010 | Dinocop | inactive current paid offer | old sale 30% / 2450 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 3391500 | 侦探，请守护我的秘密吧！ | replacement offer excluded even if strong | source 65% / 1388 KZT -> current 14% / 4705 KZT (892 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 3612850 | The Lightkeeper | inactive current paid offer | old sale 30% / 1610 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 391540 | Undertale | inactive current paid offer | old sale 75% / 462 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 4000 | Garry's Mod | replacement offer excluded even if strong | source 50% / 1125 KZT -> current 40% / 14862 KZT (2819 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 413410 | Danganronpa: Trigger Happy Havoc | inactive current paid offer | old sale 90% / 265 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 413420 | Danganronpa 2: Goodbye Despair | inactive current paid offer | old sale 50% / 1325 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 473950 | Manifold Garden | inactive current paid offer | old sale 75% / 1300 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 477740 | Zero Escape: The Nonary Games | inactive current paid offer | old sale 80% / 780 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 555950 | Danganronpa Another Episode: Ultra Despair Girls | inactive current paid offer | old sale 80% / 780 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 564230 | Fire Pro Wrestling World | inactive current paid offer | old sale 80% / 780 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 567640 | Danganronpa V3: Killing Harmony | inactive current paid offer | old sale 70% / 1410 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 590380 | Into the Breach | replacement offer excluded even if strong | source 80% / 820 KZT -> current 33% / 4212 KZT (799 RUB); `price_clearly_unreasonable_after_soft_target_evaluation` |
| 648580 | 428: Shibuya Scramble | inactive current paid offer | old sale 80% / 1200 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 912450 | YU-NO: A girl who chants love at the bound of this world | inactive current paid offer | old sale 85% / 900 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |
| 948740 | AI: The Somnium Files | inactive current paid offer | old sale 80% / 1040 KZT ended 17:00 UTC; activation Store snapshot => `no_active_discounted_purchase_option` |

### 21.4 Reconciliation of the extra family-graph removal

Family count fell by 21, while only 20 of those newly inactive families were present in the old dossier source queue. The remaining newly inactive family was:

- `App_2903950` — Master Detective Archives: RAIN CODE Plus. Its old 50% / 3950 KZT offer also ended at 17:00 UTC, but it was **already absent from the old dossier queue** because both strong and moderate deal scenarios were `EXCLUDE` with `price_clearly_unreasonable_after_soft_target_evaluation`. When that offer became inactive, it moved out of the family partition but did not remove an additional dossier item.

This explains why family count changed by -21 while dossier scope changed by -28 through the combined -20 inactive-queue effect plus -8 newly deal-excluded active replacements.

### 21.5 Closeout conclusion

Classification: **normal independent current-offer/deal recomputation; not an implementation side effect**.

Status remains `complete_ready_for_live_acceptance`. No new implementation is warranted from the `730 -> 702` observation. CONTRA-01..03 remain untouched and belong to their separate follow-up task. Scheduled Task `Run now` was not launched.

