# Worker report — Dossier V1 explicit manual one-shot authorization 01

- **Task:** `WORKER_TASK_DOSSIER_V1_EXPLICIT_MANUAL_ONE_SHOT_AUTHORIZATION_01.md`
- **Worker slots:** ЧАТ 7 — original authorization implementation; **НОВЫЙ ЧАТ 1** — bounded L3-01 frozen rollover collision repair on the same PR.
- **Status:** `READY_FOR_NARROW_INDEPENDENT_DELTA_QA` — L3-01 repair proposed, not merged or activated. **Fresh independent exact-final-HEAD delta L3 review and Director approval are mandatory.**
- **Repository:** `kentrap2011-hub/steam-kz-deals-2`, base `main`.
- **Branch:** `implement/dossier-v1-manual-one-shot-authorization-01`.
- **Draft PR:** [#322](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/322).

## Root cause / bounded design

`config/execution_ownership_contract.json#explicit_manual_semantic_worker_chats` explicitly authorized Russian descriptions and Progressive Deep but had **no Dossier V1 manual role**. The observed user-launched normal Dossier stopped before its run-start marker on that authority gate. Prior manual Dossier activity is not treated as proof of historical permission or evidence of a later intentional ban.

### Four-question architecture preflight

1. **Current owner:** GitHub control plane owns the exact Dossier work/ordered three-game groups, marker Git-parent authority, cache/validation/ingest, attempts/recovery/completeness, and publication. Existing Scheduled ChatGPT Dossier owns only bounded evidence research and candidate/terminal transport.
2. **Authorization:** the task authorizes a separate fresh user-invoked Dossier V1 data-plane exception; `config/execution_ownership_contract.json` now expresses it. The existing `config/taste_steam_review_dossier_runtime_prompt.md`, `config/taste_steam_review_dossier_worker_prompt.md`, V2 semantic schema/web-evidence contract and terminal receipt schema remain authoritative.
3. **Control-plane transfer:** none. The one-shot uses the existing immutable Git marker parent to freeze GitHub-owned index/descriptor/work/cache/binding authority, with GitHub-only strict ingest and canonical state transitions.
4. **Recurring system:** none. No new scheduler, queue, quota, retry/recovery authority, confirmation receipt, or group identity. No workflow dispatch of semantic work.

### Concurrency / security finding

The existing Dossier **does not have Deep's separate confirmed run-start receipt**. GitHub validates nonce-only marker creation, its actual single Git parent, immutable index/descriptors, candidate introduction/lineage, and current/late cache eligibility on ingest. No second manual confirmation gate should be invented.

A manually launched and an hourly scheduled invocation can both freeze the same pending group. This does **not** imply exclusivity, and no global ChatGPT lock is added. Each marker has its own immutable parent. The group output uses the same exact deterministic create-only candidate/terminal path, so competing producers must stop on collision and **never** overwrite/alternate/retry. For a **current-snapshot** group, simultaneous candidate and terminal are quarantined without consuming an attempt. Independent L3 review subsequently detected an old-snapshot frozen rollover gap; the narrow repair below extends the same fail-closed rule to two valid, distinct-marker outcomes bound to the **same immutable old group**. Rollover and stale bindings remain GitHub-classified; manual worker cannot relabel old groups or count them as current accepted. Exact fresh compatible cached Dossiers are reusable only from the frozen parent; partial overlaps cannot promote a group.

One bounded residual risk remains: simultaneous runs may duplicate **unpublished research effort** before the first create-only winner. This does not grant either worker scheduling or canonical acceptance authority. Independent L3 should verify live concurrency/transport semantics before approving the change.

## Changed files

1. `config/execution_ownership_contract.json`: added narrowly scoped `dossier_v1_one_shot` under existing manual exceptions; Deep and Russian exceptions left byte-for-byte semantically unchanged.
2. `config/taste_steam_review_dossier_manual_one_shot_prompt.md`: brief canonical user launcher, linking existing runtime/worker/schemas and explicit frozen/competing-run fail-closed rules.
3. `scripts/test_taste_dossier_manual_one_shot_authorization.py`: authorization/negative-mode tests; role parity and static canonical guardrails; disposable Git tests of marker parents, create-only collision, current-snapshot conflict, **and distinct-marker old-snapshot candidate/terminal collision after rollover with independent sibling, quarantine and replay assertions**.
4. `.github/workflows/validate-execution-ownership.yml`: run the bounded offline regression under the existing ownership CI, with PR/push path filters. **No new Actions workflow and no production/schedule behavior change.**
5. This report.
6. `scripts/taste_steam_review_dossier_buffered.py`: L3-01 correction of the existing GitHub-owned old-snapshot frozen transport classification only; group identity aggregation after strict validation and quarantine of **both** conflicting valid transports before cache persistence or terminal archive.

**Intentionally unchanged:** Dossier semantic/runtime worker prompts; `config/taste_steam_review_dossier_contract.json`, web-evidence and terminal schemas; Dossier V2/shadow pilot; real group queue/marker/state/cache; Fast/Deep/ranking, production, Scheduled Tasks and other exception scopes.

## Verification and acceptance gates

- Static scope review: no production files, existing semantic inputs, marker formats or scheduler changed. Existing Dossier runtime owns liveness and exact descriptor serialization.
- Targeted regression: `python scripts/test_taste_dossier_manual_one_shot_authorization.py` (disposable Git fixture; no real Dossier or workflow dispatch).
- Existing ownership regression: `python scripts/validate_execution_ownership.py`, plus unchanged existing Russian/Deep validations in the same workflow.
- **GitHub CI:** [Validate execution ownership run 40642145406](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40642145406) **SUCCESS** at implementation SHA `efb2733a734bb1a4ce51b9fac97b3968bb68f80e`: ownership validator, all five new Dossier manual one-shot tests, existing workflow-production authority and Russian description regressions PASS. Final report-only/workflow-path commit must also be verified against CI. A green suite is **not** independent L3 security acceptance.
- **Required next gate:** Director registers a genuinely independent L3 reviewer; review exact final diff, real branch CI and collision/late-marker/terminal behavior. Only Director may subsequently choose merge. No merge/activation or semantic manual launch by this worker.

## Known operational constraint

Remote GitHub is reachable through the connected GitHub API; local container git checkout cannot resolve `github.com` (DNS), so real repository tests were not run locally. CI verification must be taken from GitHub Actions; do not claim tests passed without a successful run record.

## L3-01 bounded frozen-rollover repair — NEW ЧАТ 1 (2026-10-28)

- **Accepted independent finding:** `reviews/worker_reports/dossier-v1-pr322-manual-auth-l3-independent-qa-01.md` (PR #330, current main). Original review verdict was `CHANGES_REQUIRED` due to cross-marker old-group outcome collision outside the five original tests. Original PR #322 was kept draft.
- **Explicit repair authorization:** `WORKER_TASK_DOSSIER_V1_PR322_FROZEN_ROLLOVER_COLLISION_REPAIR_01.md` from main; PR #322 comment #6464264261.
- **Source change:** `_frozen_rollover_transports` retains marker-parent, descriptor, strict candidate/terminal validation, compatible-frozen-cache binding, consumed-audit, deterministic path and create-only transport checks. Only **validated, unconsumed** frozen candidate/terminal results are grouped by `(snapshot_id, sequence, group_sha256)`. If both types exist for a group, each source file is routed to `frozen_rejected` under the existing retryable `frozen_authority` quarantine before `apply_buffered_drain` can write cache, archive semantic terminal or mark a consumed semantic attempt. Independent unrelated frozen groups continue normally. No new authority, retry, receipt, schedule, policy or production writes.
- **Regression:** `scripts/test_taste_dossier_manual_one_shot_authorization.py::test_two_marker_old_snapshot_candidate_terminal_collision_is_fail_closed` uses disposable Git with two actual marker commits with different parents, a compatible daily rollover, two distinct valid outcomes for old group 1, and a valid candidate for independent old group 2. Asserts 2 conflict quarantines, 0 frozen terminal archives, 0 consumed/failed attempts, no cache writes for conflicted items, successful independent group cache reuse, current group 1 remains pending, and idempotent second drain. Existing one-sided rollover/terminal/replay/binding regressions remain in `scripts/test_taste_dossier_frozen_invocation_rollover.py`.
- **Implementation commits (before this report-only update):** `b2640095bbf17e45aa2f9c9c4207289bf6a7766a` (source), `19d49a9646b3ca914e45c118c28dd282f7fd1ec7` (source + focused regression).
- **CI at exact tested implementation head `19d49a9646b3ca914e45c118c28dd282f7fd1ec7`:** [Validate execution ownership #40672988568](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40672988568) SUCCESS, including **6/6** offline Dossier manual tests; [Validate buffered Steam review dossier runtime #40672988580](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40672988580) SUCCESS, including existing frozen invocation rollover suite. Other exact-head checks and final report-only HEAD CI must be confirmed before independent delta QA.
- **Source-of-truth boundary:** changes exist only on `implement/dossier-v1-manual-one-shot-authorization-01` (the existing PR #322), not on `main`. `CURRENT_TASK.md` and other active worker handoffs were left untouched; no scheduled task, runtime semantic worker, producer, cache or production state was invoked.
- **Final HEAD convention:** the code/test head above precedes this report update. The branch HEAD after saving this report is the immutable reviewer target and must be read from PR #322 and matched to exact-head CI by the independent reviewer; a report commit cannot include its own SHA.

## Outcome

`READY_FOR_NARROW_INDEPENDENT_DELTA_QA`. Repair in existing draft PR #322; do not merge or launch live Dossier until the independent L3 reviewer accepts the **final** PR head and required GitHub Actions checks, followed by Director approval.
