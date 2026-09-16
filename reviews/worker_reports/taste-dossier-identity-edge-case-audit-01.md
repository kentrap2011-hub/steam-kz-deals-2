# Taste Dossier Identity Edge-Case Audit 01

Task: `taste-dossier-identity-edge-case-audit-01`  
Mode: `READ-ONLY / RECON`  
Final status: `complete`  
Audit baseline: `main` @ `d6db0c4996fa8c8bf11dcd52f1fc5e7ea7fec1c4`  
Current prepared snapshot: `b5d4cdf8aa2eacf81f2e4fe7e37d23d44305cc8f6952b71516ffbb435eeb5023`

## Executive summary

The current V2 dossier population contains identity-shape risks beyond the already proven `Sub_87601` package/app mismatch.

The separate package-identity fix is expected to address the known package-title + contained-appid hybrid if it normalizes/excludes package rows **before** the dossier layer performs first-occurrence `appid` dedupe. It does **not** cover at least three other classes already present in the current prepared population:

1. explicit non-game/addon content entering the single-game dossier layer;
2. `App_...` rows whose Steam app/product represents multiple independent games or a multi-game hub/collection;
3. release/version identities where the current title semantics and stored Steam release date are not a single obvious year/version pair.

These are not reasons to invalidate bundles/packages as user-visible offers. The invariant is narrower: every item handed to the V2 single-game dossier worker must describe one coherent game release identity, or fail/exclude upstream with a machine-readable reason.

The highest-priority uncovered issue is already the **first item of `g000001`**: `App_2378500`, `Baldur's Gate 3 - Digital Deluxe Edition DLC`. The current package-fix task does not cover it. Therefore a rerun of live V2 acceptance immediately after only the package fix would still exercise an unguarded non-game identity before the known `Sub_87601` position.

## Architecture preflight

Result: **PASS for read-only recon/report publication.**

Authoritative ownership is consistent across `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md`, `PROJECT_DECISIONS.md` / `TASTE-007`, and `config/execution_ownership_contract.json`:

- GitHub owns candidate scope, ordering, identity mapping, grouping, validation, persistence, and progress.
- The Scheduled ChatGPT worker owns bounded semantic research for the exact identity supplied by GitHub.
- The worker must not repair identity by choosing another app, base game, edition, remake, remaster, package member, or release.
- V2 identity is fail-closed: exact title + release/version identity must resolve before semantic evidence is publishable.

Important implementation observation: `scripts/taste_steam_review_dossier_daily.py` builds dossier scope by first occurrence of `appid` and the prepared work item/descriptor carries essentially `key`, `appid`, `title`, fingerprints/reason/path fields. Queue-side shape data such as `family_id`, `bundle_members`, `semantic_condition.base_appids`, `requires_ai_base_support`, and `release_date` is not preserved into the worker descriptor. Therefore the semantic worker is intentionally unable to repair product shape, and some version/year context that would help distinguish re-releases is also absent by the time live web evidence starts.

That places the corrections found below upstream of the semantic worker: purchase-family/canonical-product classification, dossier-scope construction, and descriptor identity contract.

## Audit coverage

The audit used only `kentrap2011-hub/steam-kz-deals-2` on `main`.

Checked:

- current queue source: `data/production/pre_ai/chatgpt_taste_queue.jsonl`;
- current work manifest/index and current group descriptors;
- `g000001` and `g000002` directly for early-group risk;
- full current queue content with structural and lexical probes for package/bundle/addon/edition/remaster/re-release/collection/DLC patterns and representative product descriptions;
- current dossier builder and identity/web-evidence contracts;
- prior live V2 acceptance report;
- separate `WORKER_TASK_TASTE_DOSSIER_PACKAGE_IDENTITY_FIX_01.md` to bound expected coverage.

Population accounting on this snapshot:

- queue rows eligible for dossier work: **619**;
- unique prepared `appid` identities: **618**;
- first-occurrence `appid` dedupe removals: **1**;
- prepared worker groups: **62**;
- completed at audit baseline: **0**.

The single dedupe removal is material, not benign: `appid 304240` occurs first as the malformed `Sub_87601` bundle identity and later as the coherent `App_304240` game identity, so first-occurrence dedupe preserves the wrong shape.

This was a broad bounded audit of the full current queue identity set, not a manual external-store verification of all 618 products. Counts below are exact where structural fields make them exact; otherwise they are deliberately stated as lower bounds / bounded prevalence.

## Taxonomy

| Class | Representative current examples | Count / bounded prevalence | Can block V2 before group publish? | Wrong-review attribution risk if allowed through? | Likely correction owner/layer | Covered by current package-identity fix? |
|---|---|---:|---|---|---|---|
| **A. Valid single-game offer / coherent exact release** | `App_1034860` — `GRANDIA HD Remaster`; `App_373420` — `Divinity: Original Sin - Enhanced Edition`; `App_728740` — `Sniper Elite V2 Remastered`; `App_798460` — `Ni no Kuni Wrath of the White Witch™ Remastered` | Many; edition/remaster keywords are common and are **not errors by themselves** | No, if exact app/title/release resolves | Low if exact identity binding is obeyed | No correction needed; normal V2 identity gate | N/A |
| **B. Package-title + contained-appid hybrid / duplicate-appid shadow** | `Sub_87601`, appid `304240`, `Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle`; later coherent row `App_304240`, appid `304240`, `Resident Evil` | **1 explicit `bundle:Sub_...` row; exactly 1 current appid dedupe collision** | **Yes — proven live blocker** in prior acceptance | High: package evidence/reviews can be attributed to one contained game | Upstream purchase-family → dossier-scope normalization, before appid dedupe | **Yes, expected**, provided fix runs before dossier dedupe |
| **C. Explicit non-game/addon entering single-game dossier layer** | `App_2378500`, appid `2378500`, `Baldur's Gate 3 - Digital Deluxe Edition DLC`; queue marks `family_id=addon:App_2378500`, `requires_ai_base_support=true`, base appid `1086940` | **1 explicit `addon:App_...` row** in current queue | **Yes / fail-closed likely**, because V2 contract is for one game release; currently `g000001` item 1 | High if DLC reviews are treated as base-game dossier evidence | Queue → dossier-scope entity-type guard | **No** |
| **D. `App_...` product is a multi-game collection/hub** | `App_1042550` — `Digimon Story Cyber Sleuth: Complete Edition` (description names both Cyber Sleuth and Hacker’s Memory); `App_1213210` — `Command & Conquer™ Remastered Collection` (C&C + Red Alert family content); `App_564310` — `Serious Sam Fusion 2017 (beta)` (description calls it a central hub for several existing Serious Sam games); `App_952060` — `Resident Evil 3` (description says it also includes `Resident Evil Resistance`) | **≥4 unambiguous current rows** from bounded content scan; additional anthology/collection candidates exist | Yes, if exact-one-game resolution rejects them; otherwise may pass a superficial appid check | **High**: one Steam app/product review surface can cover more than one independent game/mode/product | Canonical product-shape classifier + dossier-scope guard for app-backed compilations | **No** — these are already `App_...`, not package hybrids |
| **E. Release/version identity is semantically ambiguous** | `App_691450` — `Misao - 2024 HD Remaster`, stored `release_date=25 Oct, 2017`; `App_564310` — `Serious Sam Fusion 2017 (beta)`, stored `release_date=24 Nov, 2009`; `App_1048540` — `Kao the Kangaroo: Round 2 (2003 re-release)`, stored `release_date=31 May, 2019` | **≥3 obvious embedded-year/current-release ambiguity cases**; more renamed/remastered/anniversary listings exist | Yes, because TASTE-007 requires exact title + release-year/version resolution | **High** if reviews for original/current re-release/remaster are mixed; otherwise fail-closed | Canonical release/version normalization + descriptor identity fields | **No** |
| **F. Legitimate historical-year-in-title re-release** | `App_4249100` — `Resident Evil (1996)`, Steam-side stored release `1 Apr, 2026`; `App_4249110` — `Resident Evil 2 (1998)`, stored release `1 Apr, 2026`; `App_4249120` — `Resident Evil 3 Nemesis (1999)`, stored release `1 Apr, 2026` | **3 adjacent clear examples** | Not inherently; exact appid/current Steam release can be coherent | Medium if title year is mistaken for current Steam release year | Identity contract must distinguish historical title qualifier from current app release year | **No fix should rewrite these merely because years differ** |
| **G. Current edition name paired with legacy app release date / renamed listing** | `App_4570` — `Warhammer 40,000: Dawn of War - Anniversary Edition (Classic)`, stored `7 Aug, 2007`; `App_55150` — `Warhammer 40,000: Space Marine - Anniversary Edition`, stored `5 Sep, 2011`; also current `Enhanced` / `Executive` / `Definitive` names on older appids | Several candidates; bounded lexical class, not all are defects | Possible: exact-title/year web search can see current edition name but legacy app date | Medium-high, especially when external reviews distinguish launch edition from later relabel/rework | Canonical release/version model and descriptor provenance | **No** |

### Notes on class boundaries

- A store package/bundle is not an error. `Sub_87601` is erroneous **at the dossier identity boundary** because a package title is paired with a contained single-game appid and then deduped as if it were that game.
- An edition/remaster/remake is not an error merely because the title differs from an original title. A coherent exact app/title/version should remain a normal dossier identity.
- An `App_...` key is not sufficient proof of “one game”. Current rows demonstrate that an app can be a compilation, hub, or include another independent game.
- A year inside a title can describe the historical work/version rather than the Steam app's current release date. Those cases need explicit version semantics, not an automatic mismatch rewrite.

## Early-group impact

### `g000001`

The current first group begins with two different identity-risk classes:

1. `App_2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC` — explicit addon/non-game dossier-layer mismatch.
2. `Sub_87601` / appid `304240` — known package/app hybrid — proven live V2 blocker.

The prior live acceptance stopped at item 2 and published no group artifact. That does **not** establish item 1 as semantically correct; it only means item 2 was the first fail-closed rejection encountered in that run.

After the package fix alone, item 1 remains unguarded unless a separate scope correction is made.

### `g000002`

`App_1042550` — `Digimon Story Cyber Sleuth: Complete Edition` appears in the next group. Its queue description explicitly spans two named games. This is not a `Sub_...` package hybrid, so the package fix is not expected to address it.

Thus identity risk is not confined to one malformed first group; it recurs in app-backed product shapes.

## Immediate blockers vs correctness risks

### Immediate / acceptance-blocking

- `Sub_87601` package/app hybrid — already proven to trigger V2 identity rejection before publication.
- Any explicit addon or multi-game app for which the exact-one-game identity gate correctly refuses to resolve one release. `App_2378500` is the earliest such uncovered row and is item 1 of the first group.

### Correctness risks even if a worker does not fail closed

- app-backed compilations/hubs whose review corpus covers multiple independent games;
- renamed/remastered/re-release apps where current title and legacy/current release-year semantics can point web search to a different version;
- descriptors that omit authoritative queue `release_date` and entity-shape provenance, forcing the semantic layer to rediscover information that GitHub already had upstream.

The dangerous failure mode is therefore dual: some rows stop a whole group, while others may appear to resolve and silently attach the wrong review population to a dossier.

## Package-identity fix coverage

The separate package task is correctly bounded for the known `Sub_87601` family:

- **Covered:** package/bundle title paired with a contained appid; multi-game package that must be excluded/fail-closed rather than choosing its first app; the `appid 304240` shadow if normalization/exclusion happens before first-occurrence appid dedupe.
- **Not covered:** explicit `addon:App_...` rows; app-backed (`App_...`) multi-game collections/hubs; release/version/year ambiguity; renamed listings; historical-year title qualifiers.

No reason was found to broaden that package task itself during this recon. The uncovered classes have different invariants and are safer as bounded follow-up tasks.

## Prioritized bounded follow-up tasks

1. **P0 — `TASTE_DOSSIER_NON_GAME_SCOPE_GUARD_01`**  
   Add a deterministic upstream dossier-scope guard for addon/DLC/non-game product types before worker grouping. Preserve user-visible offer eligibility separately. Required fixture: `App_2378500` must not reach a single-game dossier descriptor as an ordinary game.

2. **P0 — `TASTE_DOSSIER_APP_COLLECTION_IDENTITY_GUARD_01`**  
   Classify `App_...` products that represent multiple independent games/hubs/compilations and prevent forced single-game dossier identity unless an explicit safe mapping exists. Fixtures should include `App_1042550`, `App_1213210`, `App_564310`, and `App_952060`.

3. **P1 — `TASTE_DOSSIER_RELEASE_IDENTITY_NORMALIZATION_01`**  
   Preserve authoritative release/version provenance into the descriptor and explicitly model current Steam app release vs historical/original/version year. Fixtures should include `App_691450`, `App_564310`, `App_1048540`, the 2026 classic Resident Evil re-release rows, and anniversary-edition renamed listings.

4. **P1 — `TASTE_DOSSIER_IDENTITY_AUDIT_LINT_01`**  
   Add deterministic read-only validation covering duplicate appids with different keys/titles, same normalized title across appids/years, entity-type rows entering the wrong dossier layer, and obvious title-year/release-year candidates. This should surface future shape regressions before a 10-item V2 group is prepared.

## Recommended next step for Director

**Dispatch `TASTE_DOSSIER_NON_GAME_SCOPE_GUARD_01` before the next live V2 acceptance run, after/alongside completion of the separate package-identity fix.** This is the smallest uncovered blocker class with direct current evidence: `App_2378500` is already item 1 of `g000001`, and the package fix does not cover it.

## Restrictions / mutation check

No queue, builder, validator, prompt, schema, recovery state, production artifact, workflow, semantic producer, or `CURRENT_TASK.md` was changed. No workflow or Scheduled Task run was dispatched. The only mutation performed by this task is this durable worker report, as explicitly allowed.

Final status: `complete`
