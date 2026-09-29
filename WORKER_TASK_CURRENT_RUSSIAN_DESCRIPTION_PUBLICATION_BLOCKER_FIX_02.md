# WORKER TASK — CURRENT RUSSIAN DESCRIPTION PUBLICATION BLOCKER FIX 02

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `current-russian-description-publication-blocker-fix-02`
Mode: `DIAGNOSE -> CONTRACT-FIRST IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/current-russian-description-publication-blocker-fix-02.md`

## User decision

Fix the current Russian-description publication blocker.

Do NOT weaken or bypass:
`Require meaningful Russian descriptions before canonical commit`.

Do NOT insert one-off handwritten descriptions into production data.

The goal is to make the normal GitHub-owned description acquisition/fallback path correctly cover the currently failing case(s), while preserving fail-closed publication.

## Why this task exists

The recently accepted Deep-first ranking implementation is already merged, but fresh canonical visual publication is blocked by the Russian-description gate.

The stale Deep Statistics diagnostic also proved that fresh Deep state is not reaching the site because the last canonical visual remains old. A successful fresh visual build is therefore required before the new ranking and fresh statistics can become visible.

### Prior related fix

PR #103:
- title: `Fix Russian description fallback before translation`
- merge commit: `f950944b1e9e7ee4433e0ed90c4d262b6ac24c91`
- task: `russian-description-publication-blocker-fix-01`

That fix:
- preserved GitHub ownership;
- kept the meaningful-Russian gate strict;
- added exact-app official Steam `/api/appdetails?cc=kz&l=russian` as a fallback when `IStoreBrowseService/GetItems(language=russian)` was not `good_ru`;
- covered the known `App_1213210` case;
- retained semantic translation only as fallback.

The current failures happen after PR #103, so do not assume the old bug simply returned. Identify the new failing case(s) and why the existing fallback path still leaves them invalid.

## Known failing publication evidence

Recent full build failures reached the final Russian-description gate after the canonical visual had otherwise been generated.

Examples already established:
- run `36453797991` — failed Russian-description validation, 1/26 personalized cards invalid;
- run `36453933968` — failed, 2/28;
- run `36454341915` — failed, 4/32;
- run `36454921288` — failed, 4/32;
- run `36457892914` — failed, 1/18.

For run `36457892914`:
- head: `85f55df8ee542ebfc47f82d9f7c15dbef2b46141`
- `Build and refresh canonical visual payload once` succeeded;
- `Validate generated card explanations` succeeded;
- `Require meaningful Russian descriptions before canonical commit` failed;
- commit/persist steps were skipped.

Do not infer the specific failing AppID from counts alone. Retrieve the exact validation evidence/log/artifact or deterministically reproduce the validator against the pinned source state.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. `PROJECT_ROUTES.md` section “Russian game descriptions — direct Steam source to publication”;
4. relevant Russian-description rules in `PROJECT_RULES.md`;
5. the accepted task/report for PR #103 if present;
6. `config/execution_ownership_contract.json`;
7. current description queue/status contracts and runtime;
8. `scripts/validate_russian_descriptions.py`;
9. only the smallest acquisition/visual/workflow files necessary.

## Architecture preflight

Before implementation prove:
- GitHub remains owner of direct description acquisition, deterministic fallback selection, validation, persistence and publication;
- browser remains read-only presentation and must not fetch/repair descriptions itself;
- interactive ChatGPT does not manually populate production translations;
- Scheduled Tasks are unchanged;
- Fast/Dossier/Deep semantics and results are unchanged;
- no ranking weights or Deep-first ordering rules are changed;
- the meaningful-Russian gate remains fail-closed;
- semantic translation fallback remains bounded by its existing canonical contract and is not replaced by hidden ad-hoc generation.

## Phase A — exact diagnosis

Pin the current failing full-build case on fresh `main`.

For every card that currently fails the meaningful-Russian gate, record:
- family ID / AppID / title;
- why the card is in the visual build;
- exact final `description_status`;
- exact source locale / source quality / source path;
- StoreBrowse Russian result;
- official Steam appdetails Russian result;
- whether a translation queue row exists;
- whether an accepted translation cache row exists and is compatible/current;
- exact validator reason for rejection.

Classify each failure into one of these or an evidence-backed equivalent:
- StoreBrowse and appdetails both have valid Russian but runtime fails to select them;
- appdetails Russian exists but is malformed/HTML/truncated and current normalization rejects it incorrectly;
- exact-app identity mismatch/edition mismatch prevents reuse;
- direct Russian truly unavailable and translation fallback should have been prepared but was not;
- translation exists but is stale/incompatible/not consumed;
- visual producer loses a valid description after acquisition;
- validator incorrectly rejects an otherwise valid meaningful Russian description;
- another exact cause.

Do not implement until the first failing case is proven.

## Phase B — implementation

Implement the smallest general fix for the proven failure class.

Requirements:
- no per-game hardcoded description text;
- no AppID-specific bypass unless the AppID is only a regression fixture and runtime logic is generic;
- preserve exact-app/source provenance;
- prefer direct official Russian Steam text when valid;
- if direct Russian is genuinely unavailable, use only the already-authorized translation pipeline;
- preserve fail-closed behavior for English/non-Russian/garbage/empty/boilerplate descriptions;
- do not publish English text as a fallback;
- do not weaken “meaningful” checks just to make the build green.

If multiple current failures share distinct root causes, fix only the minimum set necessary to make the current canonical build pass, but keep each fix generic and covered by regression.

## Required regressions

At minimum:
1. reproduce the current failing AppID(s) before the fix;
2. prove they become `ready_ru` or equivalent valid canonical state after the fix;
3. preserve PR #103 App_1213210 regression;
4. preserve non-Russian fail-closed control;
5. wrong AppID / wrong edition description cannot be reused;
6. English official description cannot pass as Russian;
7. empty/boilerplate Russian cannot pass meaningful gate;
8. accepted compatible translation fallback still works when both official Russian sources fail;
9. stale/incompatible translation remains rejected;
10. final visual validation passes for the repaired current cards;
11. score/ranking/stage fields are unchanged by description repair.

## Publication validation

After merge, use the normal GitHub-owned publication path only.

Required evidence:
- fresh full visual build actually executes; workflow-level `success` with skipped build is not sufficient;
- `Require meaningful Russian descriptions before canonical commit` passes;
- a new canonical `data/production/visual/current.json` commit is persisted;
- deployed Pages payload is based on that new visual commit;
- the deployed payload includes the already-merged Deep-first ranking fields/order;
- the deployed Statistics block is newer than the stale visual commit `2202a668cad11f67f0659aa6bcfe5e6cf34bb9ab`.

### Important stale-snapshot race boundary

The accepted stale-statistics diagnostic separately identified a rebase race in the visual persistence path.

Do NOT silently broaden this task into that race fix.

If the Russian-description repair makes a full build possible but publication then hits or reproduces the stale-snapshot rebase race, stop with a precise report and recommend the already-defined separate stale-snapshot race implementation task. Do not combine both fixes unless absolutely required to complete publication and explicitly justified by the current canonical architecture.

## Hard prohibitions

Do not:
- run Fast/Dossier/Deep semantic workers;
- manually write translation cache entries;
- hand-author game descriptions;
- weaken Russian validation thresholds globally without evidence;
- change ranking weights or RANK-013;
- change scheduler/queue/retry ownership;
- change Scheduled Tasks;
- fix unrelated Atelier positive-explanation mapping in this task.

## Report

Write:
`reviews/worker_reports/current-russian-description-publication-blocker-fix-02.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Pinned failing build`
4. `Exact failing games`
5. `Root cause`
6. `Relation to PR #103`
7. `Changes`
8. `Regression coverage`
9. `Meaningful-Russian gate proof`
10. `Fresh-main reconciliation`
11. `Publication validation`
12. `Deep-first / Statistics publication evidence`
13. `Changes not made`
14. `Unresolved`
15. `Status`
16. `Recommended next step` — exactly one bounded next step or `none`
17. exact PR/commit/run/artifact refs
18. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
