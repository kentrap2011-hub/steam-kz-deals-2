# Taste Package Member Dossier Aggregation 01

Task: `WORKER_TASK_TASTE_PACKAGE_MEMBER_DOSSIER_AGGREGATION_01.md`  
Mode: `IMPLEMENT_AND_VALIDATE`  
Status: `complete_ready_for_director_review`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Correction target: open PR `#31`  
Implementation branch: `worker/taste-dossier-package-identity-fix-01`  
Validated correction head: `34d824a1e77d4e5a7889aa7ca3c7e0ea14adae0e`

## Executive summary

This task corrects the earlier PR `#31` behavior that treated a multi-game package as an identity ambiguity to block before dossier work.

The corrected model is:

1. keep the package/store offer as the commercial entity;
2. expand only its authoritative meaningful game members from `semantic_condition.base_appids`;
3. create/reuse one exact single-game dossier node per member `appid`;
4. globally reuse that same dossier node when the same appid also appears as a standalone game candidate;
5. derive package Taste from the best qualifying independent member-game Taste signal, never from an average across package size;
6. never create a second package semantic producer/work item when independent member games already own the semantic work;
7. keep package/edition quality penalties outside Taste.

For the concrete control `Sub_87601`, the package is no longer blocked and is never sent to the dossier worker as `bundle title + contained appid`. It expands to exactly:

- `304240` — `Resident Evil`;
- `339340` — `Resident Evil 0`.

The four costume DLC appids present in the package metadata (`381710`, `381711`, `381712`, `381713`) do **not** become dossier targets.

## Architecture preflight

Result: **PASS**.

The correction preserves the established execution ownership boundary:

- **GitHub** remains owner of canonical package/member identity expansion, global dossier appid dedupe, package→member mappings, Taste-member aggregation, queue construction, grouping, validation, persistence, and progress.
- The existing **Steam review dossier Scheduled ChatGPT worker** still receives only exact single-game descriptor identities and performs bounded semantic evidence research for those exact identities.
- The existing **Taste Semantic Producer** remains unchanged. It continues to evaluate exact independent game Taste subjects; it is not made package-aware and no second producer is created.
- No scheduler, poller, queue owner, retry owner, checkpoint owner, or cadence was added.

The implementation is consistent with `PROJECT_DECISIONS.md` / `TASTE-007`: semantic web-evidence work remains bound to one coherent game identity; package decomposition is resolved by the GitHub control plane before that worker boundary.

## Why the correction belongs in GitHub, not the semantic worker

The canonical family graph and current Taste queue already contain the authoritative package structure:

- fixed package family type: `franchise_bundle`;
- authoritative meaningful games: `base_appids`;
- package store identity: `Sub_...`;
- package member names/appids: `bundle_members`.

The underlying base games also remain independent canonical game families with their own Taste subjects. Therefore GitHub can deterministically map package members to existing game semantic nodes without asking ChatGPT to guess package composition or invent a second semantic identity.

The dossier worker remains deliberately unable to repair/remap package identity. It receives only exact per-game work items.

## Dossier member expansion rule

The corrected dossier projection in `scripts/taste_steam_review_dossier_web.py` follows this rule:

- ordinary non-package `App_...` rows remain one exact dossier identity;
- package rows are recognized by `Sub_...` identity or the canonical package semantic condition;
- the **only** authoritative member-game appids are `semantic_condition.base_appids`;
- `bundle_members` is used only to resolve the exact title for those authoritative appids;
- arbitrary package members outside `base_appids` are ignored for dossier purposes;
- if an authoritative base appid cannot resolve to exactly one member title, the package expansion fails closed with a machine-readable reason rather than guessing;
- each resolved game becomes an `App_{appid}` dossier node;
- all nodes are globally deduplicated by appid.

A separate manifest-level `package_member_mappings` structure preserves the package/store identity and records which exact game dossier nodes serve it. The mapping digest is included in snapshot identity construction, so prepared work is bound to the exact package-member mapping used at preparation time.

## Exact `Sub_87601` result

Current canonical package evidence:

- package key: `Sub_87601`;
- package title: `Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle`;
- authoritative `base_appids`: `304240`, `339340`;
- package `bundle_members`: `304240`, `339340`, `381710`, `381711`, `381712`, `381713`.

Corrected dossier result:

| Role | appid | Exact dossier title | Dossier node |
|---|---:|---|---|
| meaningful game member | `304240` | `Resident Evil` | `App_304240.json` |
| meaningful game member | `339340` | `Resident Evil 0` | `App_339340.json` |
| costume DLC | `381710` | not a target | none |
| costume DLC | `381711` | not a target | none |
| costume DLC | `381712` | not a target | none |
| costume DLC | `381713` | not a target | none |

No worker descriptor contains the multi-game bundle title.

## Dossier reuse / duplicate-appid proof

The package row and standalone game rows are projected before one global appid dedupe map.

Regression coverage uses the real current rows:

- `Sub_87601`;
- `App_304240` — `Resident Evil`;
- `App_339340` — `Resident Evil 0`.

The projection produces exactly two dossier nodes, not four and not a package hybrid:

- one node for appid `304240`;
- one node for appid `339340`.

The later direct `App_...` row is the canonical exact key/title authority for the same appid while the package association remains separate metadata. Thus standalone `Resident Evil` and the package member reuse the same `App_304240` cache/dossier identity; the earlier package occurrence cannot shadow or duplicate it.

The test observes `eligible_row_count = 3`, `deduplicated_row_count = 2`, `prepared_required_count = 2`, and exactly two worker descriptor items for those appids.

## Package Taste aggregation rule

New helper: `scripts/taste_package_member_aggregation.py`.

Policy identifier: `best-qualifying-member-no-average-v1`.

Rules:

- each authoritative package `base_appid` maps to its existing independent game Taste subject;
- only independent game-family types participate; addon/DLC and package families are not member Taste authorities;
- known `INCLUDE / strong` outranks `INCLUDE / moderate`;
- ties follow canonical `base_appids` order;
- any known `strong` or `moderate` member keeps the package Taste-eligible even when another member is weak or unresolved;
- an unresolved/weak member therefore cannot automatically negate a known qualifying member;
- no numerical or qualitative average across member count exists;
- if no member currently qualifies and at least one member is unresolved, the package waits on the existing member-game semantic work rather than creating package semantic work;
- if all member games are resolved below threshold, the package is not Taste-eligible on ordinary Taste grounds;
- package/edition quality, filler composition, duplicate-content quality, price, savings, and commercial route quality remain outside this Taste rule.

## Strong-member proof

Focused regression constructs a two-game package with:

- member A: `INCLUDE / strong`;
- member B: `EXCLUDE / below_moderate`.

Result:

- aggregation status: `resolved_eligible`;
- package Taste eligible: `true`;
- selected member: member A;
- selected fit: `strong`;
- no average field or package-size dilution is used.

The same regression then changes member B from weak to unresolved/`ai_required`; member A still keeps the package eligible.

In the actual pre-AI builder, only `member_semantic_pending` or a selected member's required evidence/negative backfill causes temporary semantic deferral. `resolved_eligible` continues through the existing package store/deal/purchase/card context unchanged. The package family/store identity is not replaced by the member identity; only the Taste signal is selected from the member.

## Commercial/package preservation proof

This correction does not remove packages from the commercial pipeline:

- `build_pre_ai_family_graph.py` was not changed;
- package store identity, package primary key/title, prices, deal scenarios, package economics, purchase routes, ranking, visual/UI generation, and mailing/discovery code were not changed;
- `scripts/build_pre_ai_chatgpt_payload.py` keeps `source_taste_row` for package-side wishlist/commercial context and uses the member signal only as effective Taste evidence;
- a resolved eligible package continues into the same `ready_context` / purchase-decision path;
- when member semantics are incomplete, the package is temporarily semantically deferred while its existing independent member game family owns the missing AI work; no package AI duplicate is created.

This is semantic dependency handling, not deletion of the store/package offer.

## Existing semantic producer / immutable pin boundary

No current active Taste pin was modified.

An older active exact pin can contain a historical `Sub_...` row while the pin itself stores only its exact pinned key/appid/fingerprint/context binding and does not carry authoritative package member `base_appids`. This correction deliberately does **not** enrich or reinterpret an already-pinned work unit using a newer queue/family snapshot.

That would violate pin provenance.

Therefore:

- current immutable pins remain unchanged;
- package-member aggregation applies when future canonical pre-AI payload/queue construction has the authoritative package member binding;
- fresh dossier snapshot preparation after activation uses the corrected member expansion;
- no historical pin is silently rebound to new member identities.

## Files changed in PR #31 by this correction

- `scripts/taste_package_member_aggregation.py`
  - canonical member-subject indexing;
  - best-qualifying-member/no-average Taste policy;
  - price/deal-blind package-member semantic aggregation.
- `scripts/taste_steam_review_dossier_web.py`
  - package → authoritative member-game dossier expansion;
  - global appid reuse/dedupe;
  - package→dossier mapping metadata and snapshot binding;
  - fail-closed unresolved member-title behavior.
- `scripts/build_pre_ai_chatgpt_payload.py`
  - uses independent member Taste results for `franchise_bundle` families;
  - prevents package from becoming a second semantic subject;
  - preserves package commercial context and existing deal/card path;
  - records aggregation policy/counts in the payload contract/manifest.
- `scripts/test_taste_dossier_package_identity_fix.py`
  - corrected package-member regression suite, including real `Sub_87601` fixture and strong+weak policy.
- `.github/workflows/validate-taste-dossier-buffered.yml`
  - PR-only compilation and regression coverage for the new helper and consumer integration.

No package economics, ranking, UI, giveaway, duration, translation, DLC classifier, semantic producer, or scheduler implementation was changed.

## Correction-specific commits

Key correction commits on PR branch:

- `2375c25f3d9260607971d6e1c36c129b2f208623` — deterministic package-member Taste aggregation helper;
- `f2b04aebfa6b41f3ba39da95c4a6e3c27e417591` — expand packages into member game dossiers;
- `a0251ef17ce68c31f4701b5c86c8a3e28cb9747c` — aggregate package Taste in existing pre-AI consumer path;
- `cb386757a9482116e9632b020ea73435a5765d16` — package-member dossier/Taste regressions;
- `9b5bff2945bb363e4d8cd3c6c5c6b2819bf532a7` — wire correction into owning PR validation;
- `268485772348593bf113279371cea23d7db67094` — correct canonical dossier-store mapping path;
- `dc6a51cda18c96a88119401646ea0f4f1529b9c8` — align regression with canonical dossier-store path;
- `34d824a1e77d4e5a7889aa7ca3c7e0ea14adae0e` — synchronize correction branch with current `main` before final validation.

PR `#31` remains **open and unmerged**. Its title/body were updated to describe the corrected package-member aggregation behavior rather than the superseded multi-game blocking behavior.

## Validation

Owning PR workflow: `Validate buffered Steam review dossier runtime`.

An intermediate corrected run (`35085219955`) exposed a deterministic typo in the new diagnostic mapping path (`dossier_store` vs canonical `dossier_store_dir`). That defect was corrected; no validation was weakened.

Final validation after synchronizing current `main`:

- PR head: `34d824a1e77d4e5a7889aa7ca3c7e0ea14adae0e`;
- base: `main @ a1a5daf2bf6ef41433a7cc8ce163b8ea9143a9c0`;
- merge-ref: `ec260654cce779eb850ab7572076056ef50af38c`;
- run: `35085789722`;
- job: `104760158900`;
- conclusion: `success`.

Validation commands included Python compilation of:

- `scripts/taste_package_member_aggregation.py`;
- `scripts/build_pre_ai_chatgpt_payload.py`;
- `scripts/taste_steam_review_dossier_web.py`.

Regression results:

- daily snapshot: `9/9 OK`;
- buffered submission: `8/8 OK`;
- same-day preservation: `3/3 OK`;
- strict recovery: `12/12 OK`;
- package member aggregation: `6/6 OK`;
- total deterministic tests: `38/38 OK`.

The package suite proves all task-critical behaviors:

1. normal single-game dossier identity remains unchanged;
2. a package can expand to member-game dossiers rather than being blocked as multi-game;
3. package + standalone occurrence of the same appid reuse one dossier node;
4. `Sub_87601` produces exact `Resident Evil` / `Resident Evil 0` game identities;
5. the four costume DLC members are not dossier targets;
6. strong + weak package membership remains Taste-eligible on the strong member;
7. strong + unresolved also remains Taste-eligible on the known strong member;
8. no-qualifying + unresolved waits on member-game semantics rather than creating package semantic work;
9. the V2 worker exact-title/exact-appid identity contract remains unchanged.

## Definition of Done status

- normal single game: **PASS**;
- multi-game package expands to two or more game dossiers: **PASS**;
- same appid standalone/package reuse: **PASS**;
- strong+weak best-member rule, no averaging: **PASS**;
- `Sub_87601` exact two-game control: **PASS**;
- package/commercial path preserved: **PASS**;
- DLC broadening avoided: **PASS**;
- deterministic correction tests green: **PASS**;
- prior dossier/web-evidence regressions green: **PASS**.

## Production side effects

None.

This worker did **not**:

- merge PR `#31`;
- manually dispatch a production GitHub workflow;
- press Scheduled Task `Run now`;
- change Scheduled Task settings/UI;
- change the Taste Semantic Producer;
- create a second producer/scheduler;
- rewrite production queue/cache/receipt or active pin state;
- prepare/activate a fresh production dossier snapshot;
- deploy the site/UI.

All workflow runs used for implementation validation were automatic PR checks.

## Next step

**Director reviews PR `#31` and this report. If accepted, Director owns merge/activation and fresh canonical pre-AI/dossier preparation before any next live acceptance run.**

A separate package/edition-quality task may apply package-level quality penalties downstream of member Taste aggregation, but it must not dilute or rewrite the per-game Taste rule implemented here.
