# KOF XV high priority without Deep — diagnostic report

## 1. Task

Task ID: `kof-xv-high-priority-without-deep-diagnostic-01`

Mode: `READ-ONLY / RECON`

Goal: explain why `THE KING OF FIGHTERS XV` appeared as `Приоритет: 2 из 391` even though Deep was not completed and the card had no short Russian description, no displayed personal reason, and no displayed confirmed personal risks.

No Fast, Dossier, Deep, rebuild, deploy, ranking mutation, card mutation, or Scheduled Task action was performed.

## 2. Pinned current truth

The exact published state matching the observed `2 из 391` is pinned to commit:

- `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`
- accepted Pages deploy run recorded by the Director board: `36432075275`
- `data/production/visual/current.json` blob: `6ab10f96d4a821a9e8d627d1dc84d1c1845669fa`
- payload generated at `2026-09-28T13:54:22.355393+00:00`
- payload item count: `391`

That snapshot reproduces the observed default local queue exactly:

1. `Severed Steel` — 71.8
2. `THE KING OF FIGHTERS XV` — 68.0
3. `MY HERO ONE'S JUSTICE 2` — 67.1

The repository continued to advance during this diagnosis. A later pinned `main` at `11e9ff705d9d0f7c9c86021f1e2bb7706d708fe0` contains a newer 381-item visual payload (blob `77ca2cbbb83695055d76e99577d37f98e1c57464`). KOF XV is still Fast-effective there, with score 68 and Deep waiting for Dossier. The causal explanation below is intentionally pinned to the 391-item deployed snapshot rather than mixing moving snapshots.

## 3. Exact product identity

Canonical visual identity in the matching snapshot:

- family/work ID: `game:1498570`
- Steam AppID: `1498570`
- Taste subject key: `App_1498570`
- title: `THE KING OF FIGHTERS XV`

The visible offer is the Steam AppID 1498570 offer; the offer title contains `THE KING OF FIGHTERS XV Deluxe Edition`, but the ranking/card work identity is the exact base family `game:1498570`.

## 4. Current semantic state

For the matching 391-item snapshot:

- Fast / PASS 1: `completed`, outcome `fit`
- Dossier: `not_ready`; canonical Dossier work says `missing_dossier`
- Deep / PASS 2: `waiting_for_dossier`; `pass2_attempted=false`
- effective personalized source: `fast`
- semantic source: `progressive_pass1`
- overall analysis state: `analyzed_fit`
- analysis tier: `1`

The exact current Fast state for `game:1498570` is not a placeholder. It was accepted at `2026-09-24T04:44:04+00:00`, outcome `analyzed_fit`, fit level `moderate`, confidence `medium`, with normalized factors:

- gameplay/mastery: 90
- development/variety: 76
- structure/pacing/direction: 82
- identity/hooks: 84
- breadth of match: 78

Its stored positive evidence says the profile has confirmed enjoyment of fighting games with distinctive fighters and mastery, and that KOF XV's 3-on-3 roster/team mastery matches those preferences.

There is no KOF XV entry in the pinned `progressive_pass2_state.json`, so there is no current or stale Deep result being inherited into this score. A separate reusable Taste-cache index entry exists as `INCLUDE / moderate`, but the visual explicitly selects `effective_analysis_source=fast`; that cache is not the active stage source for the displayed score.

The missing visible personal reason does not mean the personal analysis is absent. The card has `why_fit=[]` while the Fast state contains semantic evidence. The explanation projection is fail-closed separately from the scoring projection, so the card can have a valid Fast score while refusing to show an insufficiently grounded user-facing reason.

## 5. Exact priority calculation

### Visible `Приоритет: 2 из 391`

This number is **not** the producer field `priority_rank`.

In `web/app.js`, the header is rendered from the local queue cursor:

`Приоритет: ${pos+1} из ${queueCount()}`

The default setting is `urgency_first=false`.

The Progressive UI sorts the default queue as:

1. analysis tier ascending;
2. within tier 1, `total_score` descending;
3. title as deterministic tiebreaker.

KOF XV is tier 1 because its Fast result is completed `fit`. Its `total_score=68.0`, so it was second in the 391-item default local queue.

The canonical producer-owned urgency-aware `priority_rank` for KOF XV in that same snapshot was **12**, not 2.

### KOF XV score: 68.0 / 100

Personal score: **45.0 / 60**

- Taste factors: **41.7 / 50**
  - gameplay/mastery 90 → 16.2 / 18
  - development/variety 76 → 9.1 / 12
  - structure/pacing/direction 82 → 6.6 / 8
  - identity/hooks 84 → 6.7 / 8
  - breadth of match 78 → 3.1 / 4
- Wishlist: **0 / 4**
- Achievements: **1.25 / 3** (quality 4/5, not confirmed previously played)
- Duration: **2 / 3** (unknown duration band)
- Confirmed-risk penalty: **0**

Purchase score: **23 / 40**

- absolute RUB saving: `1748 - 437 = 1311 ₽` → **14 / 20**
- current price `437 ₽` → **9 / 12**
- price history: current `437 ₽` vs historical minimum `285 ₽`, classified `well_above_history` → **0 / 8**

Effects requested by the task:

- current price: **yes**, +9
- absolute sale saving: **yes**, +14
- discount percent `75%`: **no direct score**; V2 scores absolute RUB saving, not percentage
- historical minimum: **yes**, but here it contributes 0 because the current price is well above the historical minimum
- sale deadline `2026-10-08T07:00:00+00:00`: classified `later_or_unknown`; it does not affect the default visible queue because urgency mode is off
- `Показ №13`: **no score/rank effect**
- unresolved/exploration/random boost: **none**
- missing Deep penalty: **none while a trustworthy Fast fit/not-fit is effective**
- missing Dossier penalty: **none in score**; it only prevents Deep from becoming eligible
- missing all current semantic analysis: not a numeric penalty, but such an item is placed into a lower analysis tier and sorted by deterministic purchase score instead

## 6. Why missing Deep does or does not block rank

Missing Deep intentionally does **not** block a high position when a trustworthy current Fast result exists.

Canonical Progressive precedence is:

1. current completed Deep fit/not-fit is authoritative;
2. otherwise current completed Fast fit/not-fit may remain the provisional effective personalized truth;
3. otherwise unresolved/not-analyzed projection is used.

Deep is eventual authority, not a prerequisite for showing/ranking a valid Fast result. KOF XV therefore legitimately belongs to analysis tier 1 before Deep exists.

This is not an exploration queue and KOF XV did not receive a bonus for being unresearched. It is the opposite: genuinely not-analyzed cards are in a lower tier. KOF XV is high because it **is already analyzed by Fast** and that Fast result gives it 45 personal points, plus 23 purchase points.

There is also no stale Deep inheritance: PASS 2 has no KOF XV entry in the pinned state, Dossier is missing, and Deep has not been attempted.

## 7. Nearby-card comparison

Matching default local queue:

| Local position | Game | Effective source | Deep | Personal | Purchase | Total |
|---|---|---|---|---:|---:|---:|
| 1 | Severed Steel | Deep | completed / fit | 46.8 | 25 | 71.8 |
| 2 | THE KING OF FIGHTERS XV | Fast | waiting for Dossier | 45.0 | 23 | 68.0 |
| 3 | MY HERO ONE'S JUSTICE 2 | Deep | completed / fit | 36.1 | 31 | 67.1 |

Why KOF is below #1:
- Severed Steel is +1.8 personal and +2 purchase, for +3.8 total.

Why KOF is above #3:
- MY HERO has a stronger deal component (+8 purchase), but KOF has a much stronger personal component (+8.9 personal), leaving KOF +0.9 total.

Both neighboring cards have completed Deep. Their existence proves that Deep completion itself receives no standalone ranking bonus. The rank comes from the resulting factors/scores, not from the stage label.

## 8. Meaning of Показ №13

`Показ №13` is browser-local display history stored in `localStorage`.

The per-game local record starts with `seen=0`. The badge renders `Показ №${seen+1}`; therefore `Показ №13` means the local browser record had 12 prior counted displays before the current one.

This value is absent from the ranking signature and absent from `ProgressivePersonalizationUI.compareGames()`. It does not alter analysis tier, total score, canonical `priority_rank`, or local automatic order.

## 9. User-facing explanation

The important correction is: **KOF XV was not “without analysis”. It was without Deep, but it already had a completed Fast analysis.**

Fast gave it a real factorized personal score of 45/60. Together with 23/40 for the deal, the total was 68/100. In the default UI mode, all analyzed-fit cards are grouped first and sorted by total score, so 68 points put KOF XV second among 391 cards in the exact deployed snapshot.

What made the situation look wrong is the presentation:

- the large header says `Приоритет: 2 из 391`, although that number is actually the **local feed position**, not canonical `priority_rank`;
- the same snapshot's canonical urgency-aware rank was #12;
- the card had no Russian short description and no displayed personal reason, even though a completed Fast result and normalized taste factors existed;
- Deep was correctly shown as unfinished.

So the ranking mechanics are consistent with the contracts, but the UI is misleading about what “Приоритет” means and makes a Fast-analyzed card look less analyzed than it actually is.

## 10. Changes

Report only:

- created `reviews/worker_reports/kof-xv-high-priority-without-deep-diagnostic-01.md`

No production state, ranking, card data, Fast/Dossier/Deep state, workflow, deploy, or Scheduled Task was changed.

## 11. Unresolved

None required to explain the observed `2 из 391`.

The repository moved to newer visual snapshots while the diagnosis was running, so the live queue position can change independently. This does not alter the cause of the exact 391-item observation.

## 12. Status

`complete`

Diagnosis: **mechanically expected ranking behavior with misleading UI wording/presentation; no ranking/projection defect was found for KOF XV.**

## 13. Recommended next step

Exactly one bounded follow-up:

**UI-only clarification task:** rename the large card header from `Приоритет: N из M` to `Позиция в ленте: N из M`, and when the canonical `priority_rank` differs, show it separately as `Рейтинг со срочностью: №X`. Do not change scoring, Progressive tiering, Fast/Dossier/Deep semantics, or queue behavior.

## 14. Exact commit/artifact refs

Observed deployed snapshot:

- commit: `d6d1b6a0ca15a243459b4007df6edaccfb78e39a`
- Pages deploy run: `36432075275`
- visual blob: `6ab10f96d4a821a9e8d627d1dc84d1c1845669fa`
- Fast state blob: `7ada757c14f44ee62001b04a6f05d62d306913dd`
- Deep state blob: `f4eda46acbece7056df60a18f66f35b6920c5935`
- Dossier work blob: `e2420837c25a7f6c4077aea24aedd332c07669c4`
- PASS 2 work blob: `bad9db34fe8a7def41000e228d257a29fb73b37a`
- reusable Taste entry index blob: `0de031e76e7b38e2d85318509c5293b642925e54`
- `config/final_ranking_policy.json` blob: `8f47210502edc082ff032048af21c3c8855f3230`
- `config/progressive_personalization_contract.json` blob: `06ff5768742c5b224addc6815cb88463d5eb501d`
- `web/app.js` blob: `c05395979a967fdd125b4d19d774df4725a94db2`
- `web/progressive-personalization-ui.js` blob: `139e3867854cf201f4dda283de1d935e7c97b11d`

Later pinned repository truth during report preparation:

- `main`: `11e9ff705d9d0f7c9c86021f1e2bb7706d708fe0`
- later visual blob: `77ca2cbbb83695055d76e99577d37f98e1c57464`
- later item count: `381`
- KOF XV remained `effective_analysis_source=fast`, score 68, Deep `waiting_for_dossier`

## 15. Efficiency / reusable lesson

For future “why is this card at position N?” diagnostics, first distinguish three values before inspecting semantic history:

1. the large UI feed position from local queue state;
2. producer-owned canonical `priority_rank`;
3. Progressive analysis tier and tier-specific score.

The bounded route is then:

`web/app.js` → `web/progressive-personalization-ui.js` → exact pinned visual item → only that item's Fast/Dossier/Deep state.

This avoids mistaking a local feed position for canonical rank and avoids broad state/history searches when the UI label itself is the first source of ambiguity.
