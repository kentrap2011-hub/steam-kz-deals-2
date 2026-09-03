# Visual freshness release 01 — production blocked report

- Task: `visual-freshness-release-01`
- Requested release branch: `worker/visual-freshness-release-01`
- Status: **blocked — accepted fix landed unchanged; production verification could not satisfy the full release acceptance proof without leaving scope**
- Accepted implementation branch: `worker/visual-freshness-chain-fix-01`
- Accepted implementation head: `4080030e686d6b04fcc666069819aa46df18da7a`
- Release PR: `#13` (`Release accepted visual freshness chain`)
- Release landing commit on `main`: `ddbf25d855f3ed7b86aca5ecbebb834e87178012`
- `main` at report-branch cut: `07bf7fabd0ceda3e3428da2139cc535096b0192f`

## Scope and transfer

The already implemented and accepted visual-freshness change was released without redesign. PR #13 was cleanly mergeable and changed only the accepted scoped files:

- `.github/workflows/build-daily-visual-payload.yml`
- `.github/workflows/deploy-visual.yml`
- `scripts/visual_freshness_receipt.py`
- `scripts/test_visual_freshness_receipt.py`
- `reviews/worker_reports/visual-freshness-chain-fix-01.md`

No Epic giveaway implementation, mobile feed/cache, ITAD/IGDB implementation, or Taste/ranking semantic change was added as part of this release.

The accepted branch head remained `4080030e686d6b04fcc666069819aa46df18da7a`; the release was merged rather than rewritten.

### Task-file documentation drift

The task's `Read first` list named root files `AGENTS.md`, `PROJECT_STATE.md`, and `RUNBOOK.md`. All three returned 404 from the repository's current `main`, and repository search did not locate alternate copies. The two required visual-freshness worker reports were available and were reviewed. This documentation drift did not require a production-code change and was not used as a reason to expand release scope.

## Production verification

### Canonical build

- Workflow: `Build daily visual payload`
- Run ID: `33788418064`
- Run number: `190`
- Event: `push`
- Head SHA: `ddbf25d855f3ed7b86aca5ecbebb834e87178012`
- Conclusion: **failure**
- Run: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33788418064

The freshness implementation itself executed successfully before/after the failing builder step:

- `Validate visual freshness receipt contract`: **success**
- `scripts/test_visual_freshness_receipt.py`: `VISUAL_FRESHNESS_RECEIPT_TESTS=PASS cases=fresh,degraded,stale_mismatch`
- `Create durable visual freshness receipt`: **success** (`if: always()`)
- `Upload visual freshness receipt`: **success** (`if: always()`)

The canonical payload build failed at `Build and refresh canonical visual payload once` with:

```text
ChatGPT production payload is not complete
```

That step exited with code 1 before a new canonical visual payload could be validated/committed.

The freshness receipt correctly represented the failed/no-fresh-build cycle instead of falsely claiming freshness:

```text
FRESHNESS_RECEIPT fresh_build=false outcome=degraded/no_fresh_build reason=build_reported_no_fresh_change
```

The receipt was bound to the production run environment:

- `WORKFLOW_RUN_ID=33788418064`
- `WORKFLOW_RUN_ATTEMPT=1`
- `EVENT_NAME=push`
- `WORKFLOW_HEAD_SHA=ddbf25d855f3ed7b86aca5ecbebb834e87178012`
- `HISTORY_READY=true`

### Receipt publication proof

The build published the expected artifact despite the failed canonical payload build:

- Artifact name: `visual-freshness-receipt`
- Artifact ID: `9906332740`
- Artifact size: `605` bytes
- Digest: `sha256:5c4ed633324518ad3c68d6dbe7c45d354ea9249af441b5867a589f4c1621fd5c`
- Source workflow run: `33788418064`
- Source head SHA: `ddbf25d855f3ed7b86aca5ecbebb834e87178012`
- Artifact: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33788418064/artifacts/9906332740

**Production proof satisfied:** the canonical visual build now durably publishes a truthful freshness receipt even when no fresh canonical visual build completes.

## Resulting `workflow_run` deploy

- Workflow: `Deploy visual mailing`
- Run ID: `33788465486`
- Run number: `259`
- Event: `workflow_run`
- Triggering build: `33788418064`
- Head SHA: `ddbf25d855f3ed7b86aca5ecbebb834e87178012`
- Conclusion: **skipped**
- Run: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33788465486

The deploy job contains the accepted gate:

```yaml
if: >
  github.event_name != 'workflow_run' ||
  (github.event.workflow_run.conclusion == 'success' &&
   github.event.workflow_run.head_branch == 'main')
```

Because the triggering canonical build concluded `failure`, the single deploy job was skipped before any steps ran. Therefore the production `workflow_run` did **not** execute the receipt-download step in this release verification cycle.

A separate push-triggered deploy run (`33788418084`) also occurred for the release merge and concluded `failure`; it is not evidence for the required `workflow_run` triggering-run binding and is not substituted for that proof.

## Exact triggering-run binding installed on production `main`

The accepted deploy workflow is present on production `main` and statically binds the receipt download to the exact triggering workflow run:

```yaml
- name: Download exact triggering build freshness receipt
  if: github.event_name == 'workflow_run'
  uses: actions/download-artifact@v4
  with:
    name: visual-freshness-receipt
    path: /tmp/visual-freshness-artifact
    github-token: ${{ github.token }}
    repository: ${{ github.repository }}
    run-id: ${{ github.event.workflow_run.id }}
```

This confirms that the accepted exact-run wiring is installed on `main`. It does **not** satisfy the stronger task requirement to prove from a production run that the deploy actually attempted that exact-run download, because run `33788465486` was skipped before steps executed.

## Blocked decision

The release task requires production evidence that all of the following occur in one normal chain:

1. the canonical build publishes its freshness receipt;
2. the resulting `workflow_run` deploy runs;
3. that deploy attempts to download the receipt from the exact triggering build run;
4. the exact triggering-run binding is thereby exercised in production.

Only (1) and the installed configuration for (3)/(4) were provable in this cycle. The canonical payload builder failed on the existing production-input readiness condition `ChatGPT production payload is not complete`, so the accepted deploy gate correctly skipped the `workflow_run` deploy.

Making this verification pass now would require changing or repairing a different production-input/build path, weakening/changing the accepted deploy gate, or otherwise expanding the task beyond releasing the already accepted freshness fix. The task's stop rule explicitly forbids redesigning the accepted solution to obtain release proof.

**Decision: blocked without changing the accepted fix.** No remediation of the canonical payload source, Epic flow, mobile feed/cache, ITAD/IGDB path, Taste/ranking semantics, or deploy success gate was performed.

## Production state at blocked closeout

- Accepted freshness implementation: **landed on `main`** at `ddbf25d855f3ed7b86aca5ecbebb834e87178012`.
- Truthful freshness receipt publication: **observed in production** on build run `33788418064`.
- Receipt artifact: **published successfully**, ID `9906332740`.
- Resulting `workflow_run` deploy: **created but skipped**, run `33788465486`.
- Exact triggering-run binding: **installed on production `main`**, but **not dynamically exercised** by the skipped deploy.
- Full release verification: **not satisfied; blocked pending separate upstream correction**.

## Re-verification exit criterion

A future normal canonical visual build with a complete production payload can close the remaining evidence gap without changing this accepted fix. For that run, record the successful canonical build run ID and receipt artifact, then record its resulting `workflow_run` deploy and verify that `Download exact triggering build freshness receipt` executes with `run-id` equal to that triggering build's `github.event.workflow_run.id`.

The final repository `main` SHA after this report is merged is recorded in the release execution response, because that SHA is created by the report merge itself and cannot be self-recorded inside the pre-merge report without creating another final SHA.
