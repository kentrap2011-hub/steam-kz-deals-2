# Worker report — Taste story DLC scope policy implement 01

## 1. Task / repo / mode

- Task: `taste-story-dlc-scope-policy-implement-01`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`
- Implementation PR: #51
- Status: `complete_ready_for_live_acceptance`

## 2. Architecture preflight

1. **Current owner:** GitHub repository / GitHub Actions owns business rules, exact production scope, queue construction, validation, persistence, retry/completeness and canonical dossier snapshot state under `config/execution_ownership_contract.json`.
2. **Canonical authority permitting this change:** the user-approved task changes a Taste/dossier eligibility business rule, so the owning policy is `config/taste_steam_review_dossier_contract.json`, with implementation in the existing GitHub-owned dossier scope producer.
3. **Ownership boundary:** no responsibility moved to Scheduled ChatGPT or the interactive chat. Scheduled ChatGPT still consumes only GitHub-prepared immutable groups and does not classify scope.
4. **No new orchestration:** no recurring worker, queue, retry loop, checkpoint model, backlog manager or scheduler was added. Existing checkpoint size remains 3 and existing maximal-contiguous-prefix buffered architecture is unchanged.

## 3. Exact canonical rule implemented

Independent DLC/add-on Taste and Steam-review-dossier semantic scope now requires **positive confirmation of substantial playable narrative content** from canonical Steam product metadata.

Eligible examples include a confirmed new story campaign, story/narrative expansion, story chapter/episode, story questline/storyline, or equivalent separate playable adventure.

Digital Deluxe / Deluxe Upgrade, soundtrack/OST, digital artbook, cosmetic/skin packs, weapon/item/equipment/currency/resource packs, bonus songs, digital extras, supporter/founder packs without story content, and equivalent non-story add-ons do not create an independent Taste/dossier obligation.

Season pass / container identity is not itself promoted to story-DLC semantic scope merely because it grants child story DLC.

Ambiguous DLC fails closed.

## 4. Actual owning scope path / files

Canonical path:

1. `data/production/pre_ai/chatgpt_taste_queue.jsonl` — GitHub-produced current Taste queue.
2. `scripts/taste_steam_review_dossier_web.py::resolve_dossier_scope_identities()` — actual pre-dossier identity scope projection.
3. `scripts/taste_steam_review_dossier_web.py::classify_story_dlc_scope()` — new add-on story gate before dossier identity projection.
4. `scripts/taste_steam_review_dossier_web.py::build_daily_work_manifest_web()` — fixed daily scope/snapshot construction and machine-readable classification summary.
5. `scripts/build_taste_steam_review_dossier_work.py` — same-day compatibility / snapshot identity / normal GitHub-owned rebuild.
6. `.github/workflows/build-pre-ai-store-snapshot.yml` — canonical activation path.

Supporting canonical policy/rationale:
- `config/taste_steam_review_dossier_contract.json`
- `PROJECT_RULES.md`
- `PROJECT_DECISIONS.md` → TASTE-009
- `PROJECT_ROUTES.md`

## 5. Positive story eligibility evidence model

Positive inclusion uses the canonical Taste queue `short_description`, which is already derived from Steam product metadata by the existing producer path:
- StoreBrowse basic product info when available;
- Steam AppDetails `short_description` fallback when needed.

Positive story inclusion is matched only against the product description, not title alone. Title may support an obvious negative/container classification, but title wording is not sufficient positive proof.

The classifier records:
- exact appid/title;
- classification;
- eligible boolean;
- compact reason;
- evidence source;
- matched story/non-story/container signals.

No manual web audit or new external classification service was introduced.

## 6. Fail-closed ambiguity semantics

If an add-on has canonical Taste semantic work but available canonical Steam product metadata does not positively prove substantial playable story content, it is classified:

`story_content_unproven_excluded`

and is removed before dossier identity projection.

This intentionally prefers false negatives over spending dossier research on an unproven cosmetic/bonus/utility DLC.

## 7. Machine-readable classification model

Canonical states:
- `story_dlc_eligible`
- `non_story_dlc_excluded`
- `story_content_unproven_excluded`

The work manifest now includes:
- `story_dlc_scope_policy_revision`
- `story_dlc_scope_sha256`
- `story_dlc_scope`

The scope summary is snapshot-bound. The policy revision is also a same-day compatibility guard, so a pre-policy snapshot cannot be silently preserved after this rule changes.

Active policy revision:
`story-dlc-positive-evidence-v1`

## 8. Backlog-wide compact classification summary

Fresh canonical activation inspected the entire current GitHub-prepared Taste queue mechanically; no manual DLC-by-DLC web review was used.

Current live summary:
- DLC-like/add-on items considered: **1**
- story eligible: **0**
- non-story excluded: **1**
- ambiguous excluded fail-closed: **0**

Representative current non-story exclusion:
- appid `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC`
- classification: `non_story_dlc_excluded`
- matched metadata signals: `digital_deluxe`, `soundtrack`, `artbook`, `cosmetic`, `digital_extras`

Deterministic regression fixtures additionally cover positive story expansion, ambiguous add-on, mixed story+cosmetics, OST/artbook/cosmetic/equipment packs and season-pass container behavior.

## 9. STORY-DLC-01..08 results

All required regressions passed in PR workflow `Validate buffered Steam review dossier runtime`, run **#72 / 35361991694**, job `test` success.

- **STORY-DLC-01 — BG3 Digital Deluxe excluded:** PASS.
- **STORY-DLC-02 — obvious soundtrack/artbook/cosmetic/item pack excluded:** PASS.
- **STORY-DLC-03 — real story expansion included:** PASS.
- **STORY-DLC-04 — ambiguous DLC fail-closed:** PASS.
- **STORY-DLC-05 — mixed story + cosmetics with independently confirmed story content included:** PASS.
- **STORY-DLC-06 — season pass/container not promoted from child story DLC:** PASS.
- **STORY-DLC-07 — base game unaffected:** PASS.
- **STORY-DLC-08 — regenerated current group plan excludes appid 2378500:** PASS.

The same canonical activation workflow also reran the story-DLC regression successfully before committing the refreshed pre-AI state.

## 10. Explicit BG3 Digital Deluxe result

appid `2378500` is now:

- `classification = non_story_dlc_excluded`
- `eligible = false`
- reason: `product_metadata_confirms_bonus_or_non_story_addon_content`
- evidence source: canonical Steam product-description metadata already carried in the Taste queue.

After activation:
- absent from `ordered_appids`;
- absent from all canonical required dossier groups;
- no longer creates an independent Taste/dossier semantic obligation.

## 11. Package / base-game semantics preserved

Preserved:
- base games are not passed through the add-on classifier;
- exact appid identity remains unchanged;
- existing package/member aggregation remains unchanged;
- package/container identity does not inherit child story identity;
- pricing/package economics are unchanged.

Pre-change canonical manifest:
- `package_member_mapping_count = 2`
- `identity_blocked_count = 0`

Post-activation canonical manifest:
- `package_member_mapping_count = 2`
- `identity_blocked_count = 0`

The existing package identity regression also passed in PR CI.

## 12. PR / CI / merge refs

Implementation PR: **#51 — Enforce story-only DLC Taste dossier scope**

PR head before merge:
`f5befce70411c0c41a6632d037a5dea04ab553e4`

Required PR validation:
- `Validate buffered Steam review dossier runtime` run **35361991694 / #72** — success.
- `Validate backlog dispositions` run **35361991698 / #732** — success.
- execution ownership validation inside dossier run — success.
- Story DLC semantic scope regression — success.
- package identity / semantic consistency / same-day preservation / buffered submission / recovery regressions — success.

Squash merge:
`9bb7e481cbf55bc4f8e511f596ce7e4b8c19e812`

## 13. Activation result

Normal GitHub-owned activation ran automatically from the merged canonical paths.

`Build pre-AI deterministic payload`
- run: **35362043187**
- run number: **#134**
- conclusion: **success**
- all build, package, Taste projection, dossier preparation, dossier regression, translation validation and atomic commit steps: success.

Push-side execution ownership validation:
- run **35362043145 / #171**
- conclusion: success.

Atomic refreshed pre-AI state commit:
`d9c93c64dc24b4e4a0edac98d84619aac1629f45`

No manual rebind, progress repair, immutable candidate edit or old-snapshot rewrite was performed.

## 14. New snapshot / group-plan state

Canonical post-activation state:

- snapshot id: `43e76bafd2ca0fe1dbe9a2edead920d335d55859b80038222279394b68bfb7aa`
- eligible scope count: **731**
- prepared: **731**
- completed: **0**
- remaining: **731**
- expected sequence: **g000001**
- group count: **244**
- group size: **3**
- appid `2378500` in ordered scope: **no**
- appid `2378500` in group plan: **no**

Exact new `g000001`:
1. `App_1000010` — Crown Trick
2. `App_1000360` — Hellish Quart
3. `App_1003590` — Tetris® Effect: Connected

The existing Crown Trick / Hellish Quart item-level locator problem is intentionally unchanged by this task.

## 15. PROJECT_DECISIONS ref

Canonical rationale:
`PROJECT_DECISIONS.md` → **TASTE-009 — Story DLC only in independent Taste/dossier scope**

Landed with implementation merge:
`9bb7e481cbf55bc4f8e511f596ce7e4b8c19e812`

## 16. Russian retrieval / provenance rules unchanged

Unchanged:
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- strict item-level locator/provenance rules;
- Russian existence/retrieval gate;
- source-agnostic diversification requirements.

This task only changes which DLC is allowed to reach dossier scope.

## 17. Scheduled Task Run now / settings

- Scheduled Task **Run now was not launched**.
- Scheduled Task settings were not changed.
- No new Scheduled Task or recurring semantic worker was created.

## 18. Unresolved

No implementation/activation blocker remains.

Separate pre-existing Crown Trick / Hellish Quart item-level locator-contract/retrieval issue remains out of scope and unchanged.

## 19. Status

`complete_ready_for_live_acceptance`

## 20. Exactly one recommended next step

Return this report to Director so Director can decide whether to live-test the new `g000001` or resolve the separate Crown Trick / Hellish Quart locator-contract issue before any Scheduled Task Run now.

## 21. Efficiency / reusable lesson

The reusable route is now explicit: inspect `taste_steam_review_dossier_work.json.story_dlc_scope` for backlog-wide DLC classification instead of manually auditing DLC, and trace scope changes through `classify_story_dlc_scope() -> build_daily_work_manifest_web() -> build_taste_steam_review_dossier_work.py`.

The policy revision is bound to same-day snapshot compatibility, preventing a changed semantic-scope rule from being masked by preservation of an already-prepared snapshot. Focused regressions make BG3 Digital Deluxe and all required story/non-story/ambiguous/container cases executable rather than dependent on repeated rediscovery.
