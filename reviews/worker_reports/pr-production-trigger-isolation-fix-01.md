# PR production trigger isolation fix 01

## 1. Task

Task: `WORKER_TASK_PR_PRODUCTION_TRIGGER_ISOLATION_FIX_01.md`

Mode: `IMPLEMENT / VALIDATE`

Goal: keep pull-request validation available while preventing any PR-only `workflow_run` from entering a workflow job that can mutate canonical production state on `main`.

Architecture preflight confirmed before implementation:
- GitHub Actions remains the control-plane owner under `config/execution_ownership_contract.json` and `config/daily_execution_contract.json`;
- the change stays inside the existing GitHub orchestration chain;
- no scheduler, queue, retry owner, semantic worker, or ChatGPT Scheduled Task was added or changed.

## 2. Incident reconstruction

The incident is confirmed from GitHub run metadata:

1. `Steam KZ production shortlist` run `37119438688`
   - event: `pull_request`
   - conclusion: `success`
   - head branch: `fix/fresh-deal-discovery-refresh-fix-01`
   - head SHA: `b738677364086feeba35d863006464b08efb056b`
   - started: `2026-10-03T11:22:20Z`
2. `Build mailing-optimized feed` run `37119485890`
   - event: `workflow_run`
   - conclusion: `success`
   - created: `2026-10-03T11:23:17Z`
   - run metadata head branch: `main`
   - head SHA: `7a53dc8a3ca6f247711df38733e403271872825d`
3. `Build pre-AI deterministic payload` run `37119499934`
   - event: `workflow_run`
   - conclusion: `success`
   - created: `2026-10-03T11:23:30Z`
   - head branch: `main`
4. Canonical pre-AI commit `7361a45644055276305347eb621ff8a5a8d1c9e3`
   - message: `Refresh atomic pre-AI payload`
   - committed: `2026-10-03T11:24:09Z`
   - parent: `7a53dc8a3ca6f247711df38733e403271872825d`

The upstream PR run itself did not execute the production `collect` job: `.github/workflows/steam-test.yml` already limits PRs to its deterministic `regression` job. The breach happened downstream.

## 3. Unsafe edge

The exact incident edge was:

`Steam KZ production shortlist` successful PR run
→ `Build mailing-optimized feed` `workflow_run`.

Before the fix, the downstream job authorized every successful run of the named workflow:

```yaml
github.event_name != 'workflow_run' ||
github.event.workflow_run.conclusion == 'success'
```

It did not require the triggering run to come from `main`.

The mailing workflow then explicitly checked out `ref: main`, built canonical mailing/cache outputs, committed them, and pushed to `main`. Its own observed GitHub run metadata therefore appeared as a `main` run. The next consumer, `Build pre-AI deterministic payload`, already had a correct `success + head_branch == main` guard, but by that point the unauthorized PR trigger had already been converted into a successful main-headed mailing run. Pre-AI therefore accepted that downstream run and wrote canonical production state.

## 4. Workflow-run audit

All current repository workflows containing `workflow_run` were audited, including every job that contains `git push`.

### Unsafe and fixed

- `Steam KZ production shortlist` → `Build mailing-optimized feed` / `build`.
- `Build mailing-optimized feed` → `Build compact feed ingest validation` / `validate`.
- `Update Steam KZ deals` → `Build compact deal feed` / `build`.
- `Checkpoint SteamDB history` → `Build SteamDB cache classification` / `build`.
- `Validate SteamDB true-miss runtime resolutions` → `Checkpoint SteamDB history` / `checkpoint`.
- `Build SteamDB cache classification` → `Export SteamDB miss manifest` / `export`.
- The `Build daily visual payload` workflow had two mutating alternate jobs, `giveaway_refresh` and `commercial_refresh`, that could be selected for a `workflow_run` event without first proving main-source authority. Both are now guarded.

### Already safe

- `Build mailing-optimized feed` / `Checkpoint SteamDB history` → `Build pre-AI deterministic payload` / `build`: already required successful `main`.
- `Export SteamDB miss manifest` → `Ingest SteamDB runtime submissions` / `ingest`: already required successful `main`.
- `Build daily visual payload` full `build` job: already required successful `main`.
- `Build daily visual payload` → `Deploy visual mailing`: already required successful `main`; repository contents permission is read-only and publication is to Pages rather than a canonical repository write.

### Non-mutating / out of mutation scope

- `Build daily visual payload` `scope` only classifies the requested refresh and does not push canonical state.
- `Build daily visual payload` `no_build_receipt` is a fail-closed receipt path and does not push canonical state.

The durable audit route is recorded in `PROJECT_ROUTES.md`, and the reusable failure recipe is recorded in `KNOWN_WORKER_PITFALLS.md`.

## 5. Fix

Every audited production-mutating `workflow_run` job now uses the same explicit production-source rule:

```yaml
github.event_name != 'workflow_run' ||
(github.event.workflow_run.conclusion == 'success' &&
 github.event.workflow_run.head_branch == 'main')
```

For a `workflow_run`, production authority is therefore:

- upstream conclusion is `success`; and
- upstream `head_branch` is exactly `main`.

The upstream workflow name remains routing information, not sufficient production authority by itself.

Direct existing entrypoints remain unchanged:
- `workflow_dispatch`;
- direct `push` triggers already defined by each workflow;
- the scheduled `Steam KZ production shortlist` production collection.

PR validation in `steam-test.yml` remains enabled and unchanged.

## 6. Regression coverage

Added `scripts/test_workflow_run_production_authority.py`, wired into `Validate execution ownership`.

It deterministically proves:

1. successful `workflow_run` from `main` is authorized;
2. successful feature/PR branch `workflow_run` is rejected;
3. the exact PR #140 feature branch shape `fix/fresh-deal-discovery-refresh-fix-01` is rejected;
4. failed and cancelled `main` upstream runs are rejected;
5. direct `workflow_dispatch`, `push`, and `schedule` entrypoints remain allowed by the common authority predicate;
6. PR validation and the non-PR production collector split remain present in `steam-test.yml`;
7. every current `workflow_run` job containing `git push` must contain all three authority markers;
8. the exact audited mutating-job set is pinned so a new or removed edge forces explicit reclassification.

The audited mutating set currently contains 11 jobs, and all 11 pass the guard audit.

## 7. PR self-trigger safety note

Implementation PR #141 did not run `Steam KZ production shortlist` at all because its changed paths did not match that workflow's PR path filter.

The PR head `a55d03d78e90854f16c4064cb69f83b0c908b1e7` ran only the expected read-only validation workflows:
- `Validate execution ownership` — `37122063033`;
- `Validate Progressive PASS 2 core` — `37122062988`;
- `Validate backlog dispositions` — `37122062969`;
- `Validate package purchase value` — `37122062966`.

No semantic worker, Dossier/Deep worker, or production workflow was manually dispatched for validation.

## 8. Validation

Before merge:
- branch was synchronized with `main@f3835b23b62631167c69f0f4a58958dc87e7fa6e`;
- compare state was `behind_by=0`;
- PR #141 was mergeable;
- all required PR checks were green;
- `Validate execution ownership` was explicitly rerun immediately before merge;
- rerun job `111200693837` completed successfully, including `Validate workflow-run production authority`;
- the production-source guard was re-read from the current PR head immediately before merge.

Implementation was merged as `da71fb7578c5fe467da0ce8e3decfbc62a6465a4`.

After merge:
- `Validate execution ownership` push run `37122344406` succeeded on the merge commit;
- job `111200784880` passed both `Validate component ownership boundaries` and `Validate workflow-run production authority`;
- current `main` was re-read after subsequent production commits and still contains the new guard and regression file;
- legitimate main-source `workflow_run` routing remained active. Examples include `Build compact feed ingest validation` run `37122354870`, `Build SteamDB cache classification` run `37122358586`, `Export SteamDB miss manifest` runs `37122356876` / `37122372741`, `Ingest SteamDB runtime submissions` runs `37122374215` / `37122389197`, and `Build daily visual payload` run `37122383917`.

Two post-merge pre-AI runs, `37122354888` and `37122358723`, were correctly admitted as successful-main upstream paths but then failed independently at the existing discovery freshness gate:
`discovery_source_older_than_allowed,candidate_universe_not_rebuilt_for_current_production_cycle`, with discovery timestamp `2026-09-23T23:12:47.031485+00:00`. This is downstream fail-closed behavior, not a trigger-authority regression, and it was not changed in this task.

## 9. Exact PR/commit/run refs

Incident:
- PR-validation shortlist run: `37119438688`
- unintended mailing run: `37119485890`
- unintended pre-AI run: `37119499934`
- unintended canonical pre-AI commit: `7361a45644055276305347eb621ff8a5a8d1c9e3`

Implementation:
- branch: `fix/pr-production-trigger-isolation-01`
- final tested implementation head: `a55d03d78e90854f16c4064cb69f83b0c908b1e7`
- PR: `#141`
- merge commit: `da71fb7578c5fe467da0ce8e3decfbc62a6465a4`

PR validation:
- execution ownership: `37122063033`
  - initial job: `111199975563`
  - required pre-merge rerun job: `111200693837`
- PASS 2 core: `37122062988`
- backlog dispositions: `37122062969`
- package purchase value: `37122062966`

Post-merge authority validation:
- execution ownership run: `37122344406`
- job: `111200784880`

## 10. Status

`implementation_complete_ready_for_director_acceptance`

No ChatGPT Scheduled Task was created, changed, enabled, disabled, paused, or resumed. No semantic worker was run. No canonical production data was manually edited.

## 11. Recommended next step

Director reviews this report and records acceptance of the merged PR-production-trigger isolation fix.
