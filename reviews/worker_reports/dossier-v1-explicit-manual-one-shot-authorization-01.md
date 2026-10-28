# Worker report — Dossier V1 explicit manual one-shot authorization 01

- **Task:** `WORKER_TASK_DOSSIER_V1_EXPLICIT_MANUAL_ONE_SHOT_AUTHORIZATION_01.md`
- **Worker slot:** ЧАТ 7 (implementation only, not a semantic worker).
- **Status:** `READY_FOR_DIRECTOR_L3_QA` — proposed change only. **Independent L3 security QA and Director merge approval are mandatory; not self-accepted or activated on main.**
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

A manually launched and an hourly scheduled invocation can both freeze the same pending group. This does **not** imply exclusivity, and no global ChatGPT lock is added. Each marker has its own immutable parent. The group output uses the same exact deterministic create-only candidate/terminal path, so competing producers must stop on collision and **never** overwrite/alternate/retry. If candidate **and** terminal are present simultaneously for one group, existing GitHub buffered drain quarantines their conflict without consuming an attempt. Rollover and stale bindings remain GitHub-classified; manual worker cannot relabel old groups or count them as current accepted. Exact fresh compatible cached Dossiers are reusable only from the frozen parent; partial overlaps cannot promote a group.

One bounded residual risk remains: simultaneous runs may duplicate **unpublished research effort** before the first create-only winner. This does not grant either worker scheduling or canonical acceptance authority. Independent L3 should verify live concurrency/transport semantics before approving the change.

## Changed files

1. `config/execution_ownership_contract.json`: added narrowly scoped `dossier_v1_one_shot` under existing manual exceptions; Deep and Russian exceptions left byte-for-byte semantically unchanged.
2. `config/taste_steam_review_dossier_manual_one_shot_prompt.md`: brief canonical user launcher, linking existing runtime/worker/schemas and explicit frozen/competing-run fail-closed rules.
3. `scripts/test_taste_dossier_manual_one_shot_authorization.py`: authorization/negative-mode tests; role parity and static canonical guardrails; disposable Git tests of two markers, actual parent freezes, create-only path collision and candidate/terminal conflict.
4. `.github/workflows/validate-execution-ownership.yml`: run the bounded offline regression under the existing ownership CI, with PR/push path filters. **No new Actions workflow and no production/schedule behavior change.**
5. This report.

**Intentionally unchanged:** Dossier runtime and semantic prompts; `config/taste_steam_review_dossier_contract.json`, web-evidence and terminal schemas; Dossier V2/shadow pilot; real group queue/marker/state/cache; Fast/Deep/ranking, production, Scheduled Tasks and other exception scopes.

## Verification and acceptance gates

- Static scope review: no production files, existing semantic inputs, marker formats or scheduler changed. Existing Dossier runtime owns liveness and exact descriptor serialization.
- Targeted regression: `python scripts/test_taste_dossier_manual_one_shot_authorization.py` (disposable Git fixture; no real Dossier or workflow dispatch).
- Existing ownership regression: `python scripts/validate_execution_ownership.py`, plus unchanged existing Russian/Deep validations in the same workflow.
- **GitHub CI:** [Validate execution ownership run 40642145406](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40642145406) **SUCCESS** at implementation SHA `efb2733a734bb1a4ce51b9fac97b3968bb68f80e`: ownership validator, all five new Dossier manual one-shot tests, existing workflow-production authority and Russian description regressions PASS. Final report-only/workflow-path commit must also be verified against CI. A green suite is **not** independent L3 security acceptance.
- **Required next gate:** Director registers a genuinely independent L3 reviewer; review exact final diff, real branch CI and collision/late-marker/terminal behavior. Only Director may subsequently choose merge. No merge/activation or semantic manual launch by this worker.

## Known operational constraint

Remote GitHub is reachable through the connected GitHub API; local container git checkout cannot resolve `github.com` (DNS), so real repository tests were not run locally. CI verification must be taken from GitHub Actions; do not claim tests passed without a successful run record.

## Outcome

`READY_FOR_DIRECTOR_L3_QA` (proposal committed in a single isolated open PR; pending independent security acceptance).
