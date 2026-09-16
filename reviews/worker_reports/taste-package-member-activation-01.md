# Taste Package Member Activation 01

Task: `WORKER_TASK_TASTE_PACKAGE_MEMBER_ACTIVATION_01.md`  
Task ID: `taste-package-member-activation-01`  
Mode: `ACTIVATE / VALIDATE`  
Status: `complete_ready_for_live_acceptance`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`

## Executive summary

The accepted package-member dossier/Taste correction from PR `#31` is activated in production through the repository-owned GitHub/GitHub Actions path.

PR `#31` was merged without changing its accepted semantic policy. Canonical post-merge activation exposed two ordinary deterministic activation defects at the publication/snapshot integration boundary. Both were corrected narrowly, validated by repository PR checks, merged, and re-run through the same canonical production workflow. No alternate control plane, scheduler, retry owner, manual production artifact rewrite, or Scheduled ChatGPT run was introduced.

The final canonical activation run produced a fresh identity-policy-aware dossier snapshot:

- snapshot: `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`;
- prepared at: `2026-09-16T12:51:02+00:00`;
- prepared for Samara date: `2026-09-16`;
- package identity policy revision: `package-member-dossier-aggregation-v1`;
- package mappings: `1`;
- prepared required dossiers: `618`;
- completed required dossiers: `0`;
- remaining required dossiers: `618`;
- immutable worker groups: `62`;
- canonical expected live sequence: `1`.

The rejected pre-activation snapshot was `b5d4cdf8aa2eacf81f2e4fe7e37d23d44305cc8f6952b71516ffbb435eeb5023`, so the canonical snapshot identity changed as required.

For `Sub_87601`, the fresh manifest now binds exactly two reusable game dossier identities:

- `App_304240` — `304240` — `Resident Evil`;
- `App_339340` — `339340` — `Resident Evil 0`.

The package title is not paired with a contained appid as a fake game dossier identity. The package is also not reintroduced into the Taste semantic queue as a second semantic subject.

## Architecture preflight

Result: **PASS**.

The activation preserves established execution ownership:

- GitHub/GitHub Actions owns canonical pre-AI construction, package/member identity binding, dossier scope preparation, immutable group planning, reconciliation, validation, persistence, and canonical progress;
- the existing Scheduled ChatGPT Steam review dossier worker remains only the bounded semantic evidence worker for exact game descriptor identities;
- the Taste Semantic Producer contract is unchanged;
- package Taste remains `best-qualifying-member-no-average-v1`;
- package/edition quality remains a separate downstream concern and was not implemented here;
- DLC behavior was not broadened or redesigned;
- no scheduler, recurring quota, backlog manager, retry owner, checkpoint owner, or alternate control plane was added.

The production package mapping is sourced from the canonical GitHub-owned family graph while semantic work remains owned by exact independent game subjects. This preserves the accepted boundary: commercial package identity is retained without turning the package into a second semantic producer/work item.

## Accepted PR #31 activation

Accepted implementation head before merge:

- PR: `#31` — `Aggregate multi-game packages through member game dossiers`;
- accepted/validated head: `34d824a1e77d4e5a7889aa7ca3c7e0ea14adae0e`;
- accepted durable report status: `complete_ready_for_activation`;
- prior owning validation workflow: run `35085789722`, job `104760158900`, conclusion `success`;
- deterministic suite in that accepted report: `38/38 OK`.

Immediately before activation, PR `#31` still pointed to the accepted head and was mergeable with its required validation green.

Normal repository merge path was used:

- PR `#31` merge commit: `c148877520787ba13b52a4faa8c83d6e271faf46`;
- merge landed in `main` on `2026-09-16`;
- no manual production artifact edit was used to simulate activation;
- no Scheduled ChatGPT action was used.

## Canonical activation/preparation path

The repository-defined canonical path was the automatic push-triggered workflow:

- workflow: `Build pre-AI deterministic payload`;
- file: `.github/workflows/build-pre-ai-store-snapshot.yml`;
- trigger: merge/push to `main` on owned paths;
- no manual workflow dispatch was required for the completed activation.

### Initial post-merge activation run

Automatic run after PR `#31`:

- run: `35096701673` (`run_number=121`);
- job: `104795718225`;
- head: `c148877520787ba13b52a4faa8c83d6e271faf46`.

All deterministic construction, dossier preparation, reconciliation, and dossier control-plane regressions reached success. The final atomic publication step then failed only because an optional inbox directory did not exist and the workflow staged it with a fatal hard `git add`:

`data/ai_inbox/taste_steam_review_dossiers`

This was an ordinary deterministic activation defect, not a new product/architecture decision.

### Activation defect repair #1 — optional inbox publication

PR `#32` changed only the atomic publication staging of the optional dossier inbox so an absent optional directory is non-fatal, matching the workflow's existing optional quarantine handling.

Evidence:

- repair commit: `e5af416a7bab0d3298af63d65602ed9e4b5c2fc5`;
- changed files: only `.github/workflows/build-pre-ai-store-snapshot.yml`;
- semantic/scheduler behavior changed: none;
- validation run: `35097179506`, job `104797261524`, conclusion `success`;
- merge commit: `68711a9accd7f2d61701a1646b8f030e41f10bff`.

The next automatic canonical run succeeded through atomic publication and produced production commit:

- `41fdb153430f6753201c091be5cfc821678acfd5` — `Refresh atomic pre-AI payload`.

That successful run exposed the second activation defect: the same-day dossier builder preserved the pre-fix snapshot solely because its date matched the current Samara date, so the old hybrid identity snapshot could survive a policy activation.

### Activation defect repair #2 — same-day policy migration and package mapping seam

PR `#33` corrected only the activation integration boundary.

The fixed-daily invariant remains unchanged for snapshots already carrying the current identity policy revision. A same-day snapshot created before `package-member-dossier-aggregation-v1` is now rebuilt through the canonical builder rather than silently preserved.

During PR validation, the current production queue also exposed the expected accepted semantic state: `Sub_87601` is intentionally absent from `chatgpt_taste_queue.jsonl` because member game families own the semantic work. The original package mapping implementation expected the package row itself to still be in that queue, which would have forced either loss of package mapping or reintroduction of a duplicate package semantic subject.

The activation repair therefore binds commercial package/member identity from the already canonical `family_graph.json` while leaving the semantic queue game-only:

- franchise bundle authoritative members come from canonical `base_appids`;
- exact member titles come from canonical independent base-game families;
- package mapping is bound into snapshot identity;
- package `source_row_appid` is explicitly `null` rather than borrowing a contained game appid;
- worker descriptors remain exact `App_...` game identities;
- no package semantic duplicate is created.

Evidence:

- same-day migration commit: `f7d90dbecabe7a6d86551311ec399b7b6cb5d068`;
- migration regression commit: `f01c92831eae41aab70787eb200087862ff5e801`;
- canonical family-graph mapping repair: `ce304e95fec4252875dd96403db90944ec634fe6`;
- live-state identity regression: `4c027173a12849c66fa35a6c89bd1fa211a29f0a`;
- final PR `#33` validation run: `35098141931`;
- validation job: `104800526489`;
- conclusion: `success`;
- PR `#33` merge commit: `be45ef21aea4679dd7df9fff720331aca08f3ad8`.

No validation was weakened to accommodate production drift. Instead, the regression now proves the accepted state: package absent from semantic queue, exact member games present, package mapping retained separately by the control plane.

## Final canonical activation run

Automatic canonical run after PR `#33`:

- workflow: `Build pre-AI deterministic payload`;
- run: `35098200208` (`run_number=123`);
- job: `104800717795`;
- head: `be45ef21aea4679dd7df9fff720331aca08f3ad8`;
- conclusion: `success`;
- completed: `2026-09-16T12:51:11Z`.

Every owned stage succeeded, including:

- package purchase snapshot;
- family graph;
- Taste projection;
- ChatGPT consumer bundle;
- fresh dossier backlog preparation;
- nonfatal dossier inbox reconciliation;
- dossier control-plane regressions;
- active Taste pin preserve/ensure step;
- Russian translation validation/build;
- atomic pre-AI publication.

The run published:

- `6aeeaaaa98ff831c1c4982293759453cfa8caa53` — `Refresh atomic pre-AI payload`.

A later automatic commercial visual refresh (`7954ffd12edfcc642337a424f7ddf8473d480364`) was unrelated and was preserved untouched.

## Fresh snapshot comparison

### Previous rejected snapshot

- snapshot id: `b5d4cdf8aa2eacf81f2e4fe7e37d23d44305cc8f6952b71516ffbb435eeb5023`;
- prepared for: `2026-09-16`;
- source queue SHA-256: `77ca8dc22b3b334465722c0cdd6ba0522af71e55e8fde100ff7afb678e1bff79`;
- source rows: `619`;
- eligible scope: `618`;
- prepared required: `618`;
- completed required: `0`;
- it did not carry the active package-member identity policy revision;
- it contained the rejected hybrid package/game identity for `Sub_87601`.

### Fresh activated snapshot

- snapshot id: `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`;
- prepared at UTC: `2026-09-16T12:51:02+00:00`;
- prepared for: `2026-09-16`;
- source queue SHA-256: `9260ea6c22621cc46b53eda894f1eafd7b398d0d290e861e34697d60b4b9757b`;
- source rows: `618`;
- eligible rows: `618`;
- unique appids: `618`;
- deduplicated duplicate rows: `0` in the current game-only queue;
- identity policy revision: `package-member-dossier-aggregation-v1`;
- identity blocked: `0`;
- package member mappings: `1`;
- prepared required: `618`;
- completed required: `0`;
- remaining required: `618`;
- full backlog complete: `false`;
- worker groups: `62`;
- canonical expected sequence: `1`.

The snapshot id, source queue digest, row count, identity policy binding, and package mapping all changed coherently after activation. This is a genuinely fresh canonical snapshot, not preservation of the rejected pre-fix same-day snapshot.

## `Sub_87601` identity proof

The fresh manifest contains exactly one package-member mapping for:

- package key: `Sub_87601`;
- family id: `bundle:Sub_87601`;
- commercial title: `Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle`;
- `source_row_appid`: `null`;
- member count: `2`;
- member appids: `304240`, `339340`;
- aggregation semantics: `per_game_dossier_reuse_by_appid`.

Exact member dossier identities:

| Appid | Title | Dossier key | Dossier path |
|---:|---|---|---|
| `304240` | `Resident Evil` | `App_304240` | `data/cache/taste_steam_review_dossiers/App_304240.json` |
| `339340` | `Resident Evil 0` | `App_339340` | `data/cache/taste_steam_review_dossiers/App_339340.json` |

Fresh worker projection confirms these are ordinary exact game descriptors:

- sequence `33` contains `App_304240 / 304240 / Resident Evil`;
- sequence `36` contains `App_339340 / 339340 / Resident Evil 0`.

No worker descriptor pairs the package title with either contained appid.

The four non-authoritative costume DLC package members from the accepted control case remain outside the package dossier mapping and are not created as package-derived dossier targets:

- `381710`;
- `381711`;
- `381712`;
- `381713`.

DLC behavior was not broadened.

## Global reuse / semantic ownership proof

The current semantic queue contains the two independent exact game subjects and intentionally does **not** contain `Sub_87601` as a second semantic subject.

Therefore:

- `App_304240` owns the `304240` semantic/dossier identity once;
- `App_339340` owns the `339340` semantic/dossier identity once;
- the commercial package references/reuses those same dossier identities through manifest mapping;
- no duplicate package worker item is created;
- current queue `deduplicated_row_count=0` is coherent because duplicate package semantic rows are not emitted in the first place;
- package commercial identity is still retained in the canonical family graph and fresh dossier manifest.

Package Taste policy remains `best-qualifying-member-no-average-v1`; this activation did not implement package-size averaging or edition-quality penalties.

## Progress / stale-result safety

Activation did not manually advance dossier progress.

Fresh canonical state is:

- prepared required: `618`;
- completed required: `0`;
- remaining required: `618`;
- canonical expected sequence: `1`.

Therefore no stale or invalid buffered result was accepted as completed progress merely because activation occurred. The canonical workflow ran its existing nonfatal inbox reconciliation and dossier control-plane regressions before publication, and the resulting manifest still begins at zero completed work.

No production queue/cache/progress/receipt file was manually rewritten to force success. Production artifacts were generated and committed by the owning GitHub Actions workflow.

## Next expected live group

Canonical next live work is immutable group sequence `1` of `62` for snapshot `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`.

Descriptor:

`data/production/pre_ai/taste_steam_review_dossier_worker_groups/6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53/g000001.json`

It contains exactly ten coherent game identities, indices `[0,10)`:

1. `App_2378500` — `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC`;
2. `App_1000360` — `1000360` — `Hellish Quart`;
3. `App_1003590` — `1003590` — `Tetris® Effect: Connected`;
4. `App_1003890` — `1003890` — `Blacksad: Under the Skin`;
5. `App_10150` — `10150` — `Prototype™`;
6. `App_1015940` — `1015940` — `Welcome to Elk`;
7. `App_1018800` — `1018800` — `DEEEER Simulator: Your Average Everyday Deer Game`;
8. `App_1025440` — `1025440` — `Fantasy General II`;
9. `App_1029690` — `1029690` — `Sniper Elite 5`;
10. `App_1034860` — `1034860` — `GRANDIA HD Remaster`.

The next live group is therefore known, immutable, and identity-coherent before any Scheduled ChatGPT acceptance is attempted.

## Scheduled Task / UI boundary

No ChatGPT Scheduled Task `Run now` action was performed in this task.

No Scheduled Task prompt, cadence, schedule, or settings were edited. No UI-only Scheduled Task state was required to complete activation/validation.

## Production side effects actually performed

Performed:

- merged accepted PR `#31` into `main`;
- allowed the repository's automatic canonical activation workflow to run;
- fixed the optional-inbox atomic publication defect through PR `#32`;
- fixed the pre-policy same-day preservation and live package-mapping integration seam through PR `#33`;
- allowed the final automatic canonical workflow to generate and publish the fresh pre-AI/dossier artifacts;
- preserved unrelated automatic visual-refresh work.

Not performed:

- no Scheduled ChatGPT `Run now`;
- no Scheduled Task settings/UI edits;
- no manual alternate workflow/control plane;
- no manual advancement of dossier progress/checkpoints;
- no manual production artifact rewrite to force a passing state;
- no Taste Semantic Producer redesign;
- no package/edition-quality implementation;
- no DLC policy broadening;
- no other repository access or modification.

## Definition of Done

- START/architecture gate completed: **PASS**;
- accepted PR `#31` activated: **PASS**;
- merge landed in `main`: **PASS**;
- canonical GitHub-owned preparation route used: **PASS**;
- fresh post-activation snapshot published: **PASS**;
- old rejected same-day snapshot not preserved: **PASS**;
- package-member mapping bound into snapshot identity: **PASS**;
- `Sub_87601` hybrid descriptor removed: **PASS**;
- `App_304240` exact identity coherent: **PASS**;
- `App_339340` exact identity coherent: **PASS**;
- package semantic duplicate avoided: **PASS**;
- stale buffered result not accepted as activation progress: **PASS**;
- canonical progress remains unmanipulated: **PASS**;
- next expected live group known: **PASS**;
- DLC behavior unchanged: **PASS**;
- package/edition quality not implemented: **PASS**;
- no live Scheduled Task run: **PASS**.

## Next step

Director may perform the next live Steam-review web-evidence acceptance using the existing Scheduled ChatGPT worker against canonical expected group sequence `1` of snapshot `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`.