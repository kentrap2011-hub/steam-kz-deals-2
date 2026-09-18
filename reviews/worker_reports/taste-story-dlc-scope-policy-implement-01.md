# Taste Story DLC Scope Policy Implement 01 — Durable Report

## 1. Task / repo / mode
- Task: `taste-story-dlc-scope-policy-implement-01`
- Task file: `WORKER_TASK_TASTE_STORY_DLC_SCOPE_POLICY_IMPLEMENT_01.md`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## 2. Architecture preflight
Preflight passed before implementation writes:
- GitHub remains the control plane and owns dossier eligible scope, immutable daily snapshot/group plan, ordering, progress, persistence, retry/recovery interpretation, and validation.
- The existing canonical dossier contract already authorizes GitHub to select the full current eligible Taste backlog scope.
- Scheduled ChatGPT remains only the bounded semantic evidence data plane; no scope decision moved into the scheduled worker or interactive chat.
- No new recurring worker, queue, retry/healing loop, backlog, or classification service was introduced.
- The change is located in the existing GitHub-owned daily dossier preparation path and preserves group size `3` plus buffered maximal-contiguous-prefix architecture.

## 3. Exact canonical rule implemented
Only DLC/add-on products with **positively confirmed substantial playable narrative content** may create an independent Taste/Steam-review-dossier semantic obligation.

Included only with positive product-metadata evidence such as a new/standalone story campaign, narrative/story expansion, story chapter/episode, story questline/quests, new storyline, or separate playable adventure. Digital Deluxe/Deluxe upgrade, OST/soundtrack, artbook, cosmetics/skins, weapon/item/equipment/currency/resource packs, bonus songs/digital extras, supporter/founder packs without story, and entitlement/container products do not create an independent Taste semantic object. Mixed story + bonus/cosmetic DLC remains eligible only when the story component is independently positively confirmed and substantial.

## 4. Actual owning scope path / files
Canonical flow:
`data/production/pre_ai/chatgpt_taste_queue.jsonl`
→ `scripts/taste_steam_review_dossier_web.py::resolve_dossier_scope_identities`
→ `classify_story_dlc_scope` before dossier identity projection
→ `build_daily_work_manifest_web`
→ `scripts/build_taste_steam_review_dossier_work.py` snapshot/rebind/group-plan creation
→ GitHub-generated worker index/group descriptors.

Owning/affected implementation files:
- `config/taste_steam_review_dossier_contract.json`
- `scripts/taste_steam_review_dossier_web.py`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/test_taste_story_dlc_scope.py`
- `scripts/test_taste_steam_review_dossier_same_day_preservation.py`
- `.github/workflows/validate-taste-dossier-buffered.yml`
- `.github/workflows/build-pre-ai-store-snapshot.yml`

## 5. Positive story eligibility evidence model
Positive inclusion uses the canonical Taste queue `short_description`, derived from existing Steam Store product metadata. The production classifier recognizes bounded substantial-story signals for campaign, narrative/story expansion, chapter/episode, questline/quests, storyline, and separate playable adventure.

A title may contribute to a negative/container classification, but **title is never the only positive story truth source**. Positive story eligibility is derived from descriptive product metadata, not `type=DLC` or a title regexp alone.

## 6. Fail-closed ambiguity semantics
For an add-on/DLC row:
- explicit entitlement/container signal → excluded as non-story independent identity;
- positive substantial story signal in product description → eligible;
- explicit non-story bonus-content metadata → excluded;
- otherwise → `story_content_unproven_excluded`.

Thus missing/inconclusive story metadata never silently includes a DLC. This is the required false-negative-over-false-positive behavior.

## 7. Machine-readable classification model
Canonical classifications:
- `story_dlc_eligible`
- `non_story_dlc_excluded`
- `story_content_unproven_excluded`

Each classification records `appid`, `title`, `classification`, `eligible`, compact `reason`, `evidence_source`, and matched signals. The manifest exposes this under `story_dlc_scope` with policy revision `story-dlc-positive-evidence-v1`.

The policy revision and classification digest are bound into snapshot identity/preservation compatibility, so a pre-policy same-day snapshot cannot be silently preserved.

## 8. Backlog-wide compact classification summary
The activated GitHub rebuild machine-classified the entire current eligible queue; no manual DLC-by-DLC web audit was used.

Current activated summary:
- source queue rows: **732**
- DLC-like considered: **1**
- story-eligible: **0**
- non-story excluded: **1**
- ambiguous excluded fail-closed: **0**
- resulting eligible/prepared dossier scope: **731**

Current backlog representative examples:
- `non_story_dlc_excluded`: `2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC`
- `story_dlc_eligible`: none present in the current prepared backlog
- `story_content_unproven_excluded`: none present in the current prepared backlog

Deterministic regressions provide representative positive, ambiguous, mixed-content, season-pass, soundtrack/artbook/cosmetic/item-pack cases where the current production backlog has no member of that category.

## 9. STORY-DLC-01..08 results
Focused CI run **35361991694** completed successfully. The dedicated story-DLC regression step ran **8 tests** and returned `OK`.

Results:
- STORY-DLC-01 — BG3 Digital Deluxe excluded: PASS
- STORY-DLC-02 — OST/artbook/cosmetic/item-pack fixtures excluded: PASS
- STORY-DLC-03 — confirmed story expansion included: PASS
- STORY-DLC-04 — ambiguous DLC fail-closed: PASS
- STORY-DLC-05 — mixed story + cosmetics included with independent story proof: PASS
- STORY-DLC-06 — season pass/container not independent story identity: PASS
- STORY-DLC-07 — base game unaffected: PASS
- STORY-DLC-08 — regenerated current group plan excludes `2378500`: PASS

The same focused workflow also passed the execution-ownership validator and the existing dossier/package/parallel-buffer regression suites.

## 10. Explicit BG3 Digital Deluxe result
`appid 2378500 — Baldur's Gate 3 - Digital Deluxe Edition DLC` is classified:
- classification: `non_story_dlc_excluded`
- eligible: `false`
- reason: `product_metadata_confirms_bonus_or_non_story_addon_content`
- evidence source: canonical Taste queue Steam product description
- matched signals: `digital_deluxe`, `soundtrack`, `artbook`, `cosmetic`, `digital_extras`

It is absent from the activated `ordered_appids`, `prepared_required_items`, and all groups in the canonical required dossier group plan.

## 11. Package/base-game semantics preserved
Preserved:
- ordinary base-game dossier eligibility;
- exact appid identity;
- existing package/member aggregation;
- package commercial identity separate from per-game dossier identity;
- pricing/package economics unchanged.

Existing package identity regression remained green in focused CI. The activated manifest still reports canonical package-member mappings while applying the DLC scope gate before independent add-on dossier projection.

## 12. PR / CI / merge refs
- Implementation PR: **#51 — Enforce story-only DLC Taste dossier scope**
- PR head: `f5befce70411c0c41a6632d037a5dea04ab553e4`
- Focused dossier CI: run **35361991694** — success
- Backlog disposition CI: run **35361991698** — success
- Merge commit: `9bb7e481cbf55bc4f8e511f596ce7e4b8c19e812`
- Post-merge execution-ownership run: **35362043145** — success
- Post-merge backlog validation run: **35362043205** — success

## 13. Activation result
Normal GitHub-owned activation occurred from the merge push through **Build pre-AI deterministic payload**, run **35362043187**, conclusion **success**.

The workflow:
- rebuilt the deterministic pre-AI payload through the existing canonical path;
- prepared a fresh daily full Steam review dossier backlog;
- generated a fresh worker projection/group plan;
- ran nonfatal inbox reconciliation through the existing recovery path;
- reran dossier regressions including the story-DLC suite;
- committed the atomic pre-AI payload as `d9c93c64dc24b4e4a0edac98d84619aac1629f45`.

No manual snapshot rebind, progress repair, immutable candidate edit, or ad-hoc g000001 edit was performed. Stale inbox quarantined count was `0`.

## 14. New snapshot / group-plan state
Activated canonical state:
- snapshot id: `43e76bafd2ca0fe1dbe9a2edead920d335d55859b80038222279394b68bfb7aa`
- prepared: **731**
- completed: **0**
- remaining: **731**
- canonical expected sequence: **1** (`g000001`)
- group count: **244**
- group size/checkpoint size: **3**
- status: `work_required`

Exact new `g000001`:
1. `1000010 — Crown Trick`
2. `1000360 — Hellish Quart`
3. `1003590 — Tetris® Effect: Connected`

This group changed only because the non-story BG3 Digital Deluxe object was removed from canonical scope; the Crown Trick/Hellish Quart locator/provenance semantics were not modified.

## 15. PROJECT_DECISIONS ref
`PROJECT_DECISIONS.md — TASTE-009: Story DLC only in independent Taste/dossier scope`, merged in implementation PR #51 / commit `9bb7e481cbf55bc4f8e511f596ce7e4b8c19e812`.

The user-approved rule is also recorded in `PROJECT_RULES.md — DLC в Taste / dossier semantic scope`, and the changed owning route is recorded in `PROJECT_ROUTES.md`.

## 16. Russian retrieval / provenance rules unchanged
Confirmed unchanged by this task:
- Russian existence/retrieval semantics;
- source diversification rules;
- item-level locator/provenance requirements;
- exact-appid evidence binding;
- dossier evidence contract and retrieval budget semantics.

The policy only changes which DLC may enter semantic dossier scope. It does not weaken or reinterpret evidence requirements for items that remain in scope.

## 17. Scheduled Task Run now / settings unchanged
Scheduled Task `Run now` was **not launched** for this implementation/activation. Scheduled Task settings were **not changed**. Activation used only the existing GitHub-owned pre-AI workflow triggered by the merged repository change.

## 18. Unresolved
No unresolved defect remains in the story-DLC scope policy itself.

The pre-existing Crown Trick / Hellish Quart item-level locator/provenance issue remains intentionally unresolved and out of scope. This task did not attempt to repair, bypass, or reinterpret it.

## 19. Status
`complete_ready_for_live_acceptance`

Implementation is merged, focused CI and ownership checks are green, normal GitHub activation succeeded, a fresh compatible snapshot/group plan is canonical, and the explicit BG3 Digital Deluxe regression is excluded.

## 20. Exactly one recommended next step
**Return to Director and let the Director decide whether to live-test the new `g000001` or resolve the existing Crown Trick/Hellish Quart locator-contract issue before any Scheduled Task Run now.**

Do not launch Scheduled Task from this worker.

## 21. Efficiency / reusable lesson
The reusable boundary is: **classify DLC once, deterministically, at the GitHub-owned semantic-scope gate using already-normalized product metadata, and bind the policy revision into snapshot compatibility.** This prevents downstream dossier workers from spending research budget on non-story add-ons and makes a policy change naturally invalidate/publish a fresh daily projection through the existing control plane.

A second reusable operational lesson from this execution: when another bounded worker lands the same task concurrently, stop the competing implementation, re-read fresh `main`, validate the landed implementation against the task checklist, and contribute only missing durable closeout instead of merging divergent duplicate policy code.
