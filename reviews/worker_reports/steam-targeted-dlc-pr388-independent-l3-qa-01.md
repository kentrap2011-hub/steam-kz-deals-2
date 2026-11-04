# Independent L3 source QA — targeted Steam DLC PR #388

- **Task:** `steam-targeted-dlc-pr388-independent-l3-qa-01`
- **Worker:** physical ЧАТ 3 (independent reviewer)
- **Date:** 2026-11-03
- **Verdict:** **PASS_FOR_DIRECTOR_MERGE_REVIEW**
- **Source PR:** https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/388
- **Exact reviewed source HEAD:** `b03ea8197ca106829cb0d58b1caf05a9bf5b0c6d`
- **PR status at verification:** open, non-draft, mergeable according to GitHub (not a substitute for Director's current merge gate)
- **Mode:** read-only independent source/CI review; this report is the sole file in a separate report-only DRAFT PR. No modifications to source PR #388.

## Scope and authorities

Completed START gate from `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`. Read the task, targeted `PROJECT_ROUTES.md` route, `config/execution_ownership_contract.json`, `config/daily_execution_contract.json`, `config/mailing_policy.json#paid_discovery`, `config/taste_steam_review_dossier_contract.json` (ownership, daily preparation, freshness), `scripts/discovery_freshness.py`, source PR #388's **entire five-file patch**, original implementation report, the complete changed code and tests, collector's targeted-DLC entrypoint, and `.github/workflows/steam-test.yml`.

Five changed files in source PR: `scripts/steam_targeted_paid_lanes.py`, `scripts/test_steam_targeted_paid_lanes.py`, `PROJECT_ROUTES.md`, `CURRENT_TASK.md`, and the original developer's worker report. No source/workflow/index/freshness/schedule/semantic changes elsewhere in the patch.

Architecture preflight: GitHub owns paid discovery, full source scope, validation, retry/completeness and Dossier work/index construction; source PR changes only existing deterministic GitHub collector logic. The current policies authorize complete suitable-base parent-targeted KZ DLC lookups (not global category1=21), KZT/discount gates, existing 01:00 preparation and fail-closed current-cycle freshness. This patch adds **no** scheduler, semantic runner, independent queue, retry loop, quota, new ownership or freshness-cutoff override.

## Independent source-path assessment

| Path/invariant | Independent observation |
|---|---|
| Parent ID normalization | `_canonical_appid` accepts positive exact Python `int` and nonempty ASCII decimal strings without leading zero; rejects `bool`, `float` (including `100.0`), zero, negatives, padded/Unicode/ambiguous strings, containers and null. Duplicates `100`/`'100'` become one canonical parent. |
| Parent metadata and relation | `_check_fetched_identity` rejects non-dict and present but noncanonical/mismatched `steam_appid`. `type == 'game'` required; omitted `dlc` means empty list; explicitly `dlc: null`, string, dict, tuple or invalid member raises and stops collection, rather than silently dropping members. |
| Duplicate membership | Valid `[301, 300, 300, '300', 301]` yields numerically sorted membership `['300','301']`. A mixed valid/invalid list fails as a whole. |
| Shared DLC and deduplicated fetch | `reverse[appid]` merges all eligible parents. One DLC AppID is fetched once, even if repeated in a parent's list and present under more than one parent. `verified_base_appids` is numerically sorted; candidate insertion follows sorted DLC IDs. |
| DLC metadata | Explicit `steam_appid` must match fetched AppID; `type == 'dlc'` required for acceptance. Non-DLC entries are not promoted to DLC. A qualifying DLC's present `fullgame.appid` must be canonical and one of its verified reverse parents; malformed present `fullgame` is rejected. Missing `fullgame` remains allowed because the independently fetched parent list is the required membership evidence. |
| Paid constraints | `price_overview.currency == 'KZT'` required, `final`/discount must be exact integers, `0 < final <= 450000` minor units (4500 KZT) and `discount_percent >= 50`. Existing `paid_source_rejection_reason` still runs; no new permissive price or quality fallback. |
| Rate limits, determinism | Existing `RELATION_WORKERS=3`, shared 0.9s request throttle, 25s HTTP timeout, numerical sorting and no global DLC traversal remain. Parent async completion order cannot reorder `reverse`/output. |
| Failed upstream fetch | Appdetails HTTP/429, missing `success` or `data`, and per-DLC retrieval failures propagate; `steam_partial_publish_runner.py` catches failures at `targeted_dlc_relations` and exits before replacing stable paid publication. |
| Production-to-Dossier chain | Collector remains sole GitHub-owned source producer. `discovery_freshness.py` retains 18h/current-Samara-cycle checks and aligned complete source bindings. Dossier work/index is still prepared by the ordinary GitHub pre-AI pipeline; neither the report nor PR #388 runs it. |

**Negative/positive fixture audit:** The new tests cover repeated valid IDs, cross-parent membership, one lookup per unique DLC, invalid member IDs, invalid relation container, malformed parent/base, mismatch in `steam_appid`, contradictory/malformed `fullgame`, simulated parent/DLC HTTP failures, and non-DLC exclusion. Existing tests cover KZT/discount acceptance/rejection, source/quality gating, independent Sub lane and visible 100 limit. No substantive unsafe fail-open or newly unguarded fail-closed path was found within the changed scope.

**Non-blocking limits:** Tests simulate 429 as `RuntimeError`, not a real `requests.HTTPError`; production runner catches `Exception` so real HTTP failures still abort safely. There is no separate new fixture for omitted `dlc` and omitted `fullgame`, though their behavior is clear from the source and existing tests. The stricter rejection of explicitly null `dlc` is intentional and can stop a production cycle if Steam emits that ambiguous response. Invalid `fullgame` on a **non-qualifying** DLC offer may be bypassed by the earlier paid gate, but such an offer is never published and this ordering predates the PR. None is a merge-blocking regression found in the changed scope.

## Exact-head GitHub CI

All three required GitHub Actions runs explicitly bind to source **HEAD `b03ea8197ca106829cb0d58b1caf05a9bf5b0c6d`** and PR #388:

| Required check | Run | Job | Conclusion |
|---|---|---|---|
| `regression` | https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41575792437 | `regression` | **success** (compile, policy checks, full deterministic regression step) |
| `validate` | https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41575792446 | `validate` | **success** |
| `backlog-disposition` | https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41575792602 | `backlog-disposition` | **success** |

In `41575792437`, `collect` is explicitly **skipped** for `pull_request`, as the unchanged workflow contract requires. This is not live production evidence. No independent live Steam request or local full-repository test run was performed by this reviewer; evidence is source inspection and GitHub's actual exact-head CI.

## Incident provenance and post-merge gate

Original scheduled failure: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41362591621, error `DLC relationship contains duplicates/invalid identities: 239140`. The old predicate conflated valid duplicate membership with invalid identities; **the raw parent DLC list was not captured**, so this QA does **not** claim the observed production failure was definitely caused by duplicates. The source change correctly separates cases, but only real ordinary collection can prove incident resolution.

Separately, pre-AI failure https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41498105517 failed on stale discovery. Source PR tests do not prove fresh current-cycle catalog, mailing, pre-AI output or a new Dossier index/prompt binding. Do **not** manually run GitHub Actions, manually rewrite generated worker indexes or trigger Dossier semantic work to paper over that missing production evidence.

## Verdict and sole next actor

**PASS_FOR_DIRECTOR_MERGE_REVIEW**, limited to the reviewed exact source HEAD and GitHub CI. The intended conservative duplicate normalization is correctly scoped and does not weaken the observable identity/relationship fail-closed gates. No source edits requested.

**Next actor: Director.** Reconfirm source PR #388 LIVE HEAD, required exact-HEAD CI, this independent QA report, current mergeability and permissions, then apply the previously authorized implementation merge without an unnecessary second approval if all gates still pass. After merging source PR #388, observe **ordinary scheduled** Steam collection → optimized mailing → pre-AI success, verify fresh Dossier work/index and current worker-prompt binding. A successful PR merge alone is not proof of restored auto-Dossier preparation.

No extra QA worker, source PR rewrite, manual production invocation, index write or self-merge was requested/performed.
