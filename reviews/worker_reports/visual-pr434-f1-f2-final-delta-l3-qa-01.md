# PR #434 F1/F2 final delta L3 QA — technical fixes verified, independence blocked

- **Task:** `visual-pr434-f1-f2-final-delta-l3-qa-01`
- **Repository:** `kentrap2011-hub/steam-kz-deals-2`, source of truth `main`
- **Assessment mode:** source **READ-ONLY**, exact-HEAD scoped delta; sole proposed write is this report in its own REPORT-ONLY draft PR
- **Formal verdict:** **BLOCKED — independent L3 reviewer separation is not satisfied**. Both F1/F2 are **technically PASS** on static source inspection and exact-HEAD GitHub CI, but the same physical ChatGPT conversation previously authored the two source-fix commits, so this review cannot credibly certify *independent* L3. **Do not treat this report as release approval or auto-merge authority.**

## 1. Exact source baseline, HEAD, write-set and drift

- Earlier independent baseline: [QA PR #437](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/437), source PR #434 HEAD `25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43`, verdict **CHANGES_REQUIRED** with findings F1 (commercial-only classifier ignores direct-dispatch receipt) and F2 (consumer main ref not enforced).
- Current [source PR #434](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/434) exact HEAD **`c4ea30bab8e89609ccbdbba1b34ace91b6858c80`**, still open draft and unmerged; branch `fix/visual-depth-safe-dispatch-20261111`.
- GitHub exact compare `25bedb4… → c4ea30b…`: **ahead by two commits**, `e6fd64b8ef279debfef98f03eeed73579d6b5e6f` and `c4ea30bab8e89609ccbdbba1b34ace91b6858c80`, with **only two changed files**:
  1. `.github/workflows/deploy-visual.yml` (+21/-4)
  2. `scripts/test_visual_deploy_dispatch.py` (+95/-0)
- The wider PR #434 still changes its original nine files; the direct-producer job, helper `scripts/visual_deploy_dispatch.py`, and original material/receipt verifier are **not touched by this two-commit delta**. Before this verdict, source HEAD and exact compare were re-read; **no further source drift** was found.

## 2. F1 commercial-only scope — technically PASS

| Case | Source evidence and result |
| --- | --- |
| Direct producer event + paired original run ID + attested commercial receipt | **PASS.** `deploy-visual.yml` classifier now accepts `EVENT_NAME=workflow_dispatch` with a nonempty `DIRECT_PRODUCER_RUN_ID` when the previously downloaded receipt file exists (roughly L225–245). It recognizes `fresh_build=true`, `freshness_scope=commercial_only`, `full_visual_freshness=false`, and `produced_visual.commit_sha==visual_commit`. |
| Commercial integrity | **PASS unchanged.** Classification additionally demands `paid_list_freshness.status=published`, commercial scope marker, no new paid IDs, unchanged protected semantic and description fields on retained items, and unchanged giveaway content/provenance (L247–281). Otherwise classifier falls back to `general`; it does **not** promote a changed semantic payload to scoped commercial. |
| Correct downstream stage | **PASS static wiring.** The `commercial_only` output feeds `Accept preserved semantic payload`, bypasses the *general-only* Russian-description diagnostic, and sets `scripts/stage_site_optional_sections.py --scope commercial_only` (roughly L298–357). |
| Inputless legacy manual / push | **PASS.** With no paired original run ID the new branch does not consume the receipt on `workflow_dispatch`; push also does not consume it. An unbound event cannot obtain commercial-only classification through this new receipt path. |
| Status-only / giveaway-only | **PASS.** Status `workflow_run` exits early as `status_only`; giveaway-only structural check exits before commercial classification and is unchanged. General/unrecognized commercial cases retain `general`. |
| Missing, forged, wrong-run receipt | **PASS on workflow ordering and baseline attestation; new classifier alone does not authenticate.** Paired dispatch must first download an artifact and complete exact producer run/attempt/repo/workflow/main/job/receipt attestation; missing artifact or inconsistent receipt causes failure before the classifier. The later `visual_freshness_receipt.py verify-receipt` still binds staged canonical bytes. This is code-path evidence, not an end-to-end live forgery exercise. |

**Test quality:** `test_commercial_receipt_on_direct_dispatch()` extracts the *actual embedded Python classifier* from the workflow, creates a disposable Git repository with before/after price-only commits, writes a synthetic `commercial_only` receipt referencing the latter commit, and executes the classifier as a subprocess. It asserts commercial classification with a paired ID, general classification for inputless `workflow_dispatch` and push, and status-only for the status workflow (test lines ~156–215). It does not merely search for strings. The fixture bypasses the preceding attestor by design; the baseline negative `verify_dispatch_authority` tests and workflow ordering provide the separate authority evidence.

## 3. F2 consumer main authority — technically PASS

| Case | Result |
| --- | --- |
| Paired direct dispatch from `refs/heads/main` | **PASS** job condition and bash input validation permit it. |
| Paired direct dispatch from a non-main consumer ref, even with valid main producer | **REJECTED.** New job-level condition requires `github.ref == 'refs/heads/main'` for `workflow_dispatch` with nonempty producer ID (workflow L54–60). Bash input guard additionally fails if `GITHUB_REF != refs/heads/main` with paired producer ID (L72–90). This tests the *consumer ref*, not just the producer branch. |
| Run ID without attempt, or attempt without run ID | **REJECTED** by existing bash completeness checks (L80–87); tests exercise both. |
| Legacy inputless manual on main or non-main | **ALLOWED as before**, remains unbound/not producer-authenticated. |
| Existing status-only workflow_run and push | **UNAFFECTED** by the new `workflow_dispatch`-specific main-ref condition. |

**Test quality:** `test_direct_dispatch_main_ref_guard()` extracts the *actual bash input-validation block*, runs it via `bash -c` with environment combinations, and asserts acceptance/rejection for paired main/non-main, inputless main/non-main, and both incomplete-pair negatives (test lines ~135–153). GitHub job-level expression is verified by direct workflow inspection and static wiring assertions; no real off-main Actions run was dispatched.

## 4. Exact-HEAD CI and execution evidence

All seven GitHub pull-request checks were re-queried for source HEAD **`c4ea30bab8e89609ccbdbba1b34ace91b6858c80`**; every workflow finished **SUCCESS**, and corresponding run jobs were checked:

| Required check | GitHub Actions run | Outcome |
| --- | --- | --- |
| Validate execution ownership | [43100869881](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869881) | SUCCESS; actual `Test exact visual-to-Pages direct dispatch (offline only)` step SUCCESS |
| Validate site publication resilience | [43100869926](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869926) | SUCCESS |
| Validate site deploy isolation (PR only) | [43100869821](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869821) | SUCCESS |
| Validate backlog dispositions | [43100869843](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869843) | SUCCESS |
| Validate site task registry and page | [43100869860](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869860) | SUCCESS |
| Validate Progressive PASS 2 core | [43100869914](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869914) | SUCCESS |
| Validate package purchase value | [43100869812](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43100869812) | SUCCESS |

Read the execution-ownership job log: it explicitly runs `python scripts/test_visual_deploy_dispatch.py` and emits `VISUAL_DIRECT_DEPLOY_DISPATCH_TESTS=PASS`. **Measured:** GitHub Actions executed exact-HEAD offline tests. **Locally re-executed in this session:** **NOT_EXECUTED** (no exact checkout made); source code and tests independently inspected here. No manual dispatch, workflow rerun, Pages upload, or production mutation was performed.

## 5. Retained authority / scope, and unverified liveness

- Two-commit delta does not edit `scripts/visual_deploy_dispatch.py`, producer job, or `scripts/visual_freshness_receipt.py`; existing exact run/attempt/repository/source-job/receipt checks remain. Original `dispatch_deploy` still restricts dispatch to successful main producer scope and sends original run ID/attempt using job-local `actions: write`.
- `Bind staged publication to triggering build freshness receipt` still requires exact `verify-receipt` for paired direct dispatch and excludes unbound manual/push from fresh-source claims. The verified deterministic persisted-degraded `degraded/no_fresh_build` distinction remains; baseline helper rejects unauthorized no-build/aborted material. Copy from canonical visual to staged `web/data/current.json` is unchanged.
- Visual producer `workflow_run` subscription remains removed; status-only `Build site current status` subscription, push, and legacy manual remain. No new recurring stage or ChatGPT control plane was introduced.
- **NOT_TESTED (not a F1/F2 delta blocker):** `pages` concurrency `cancel-in-progress: true` during overlapping status/push/nightly deploy; live GitHub `workflow_dispatch` / artifact download and job API execution; unattended post-merge nightly producer→Pages chain; live Pages URL read-back and current active item count. PR CI success does not establish production release acceptance.

## 6. Final verdict and one next step

**Technical delta finding:** **F1 PASS / F2 PASS**, with no source regression confirmed by delta inspection and exact-HEAD CI. On technical grounds alone, this HEAD appears ready for a separately independent merge-gate review; runtime/liveness remains a post-merge acceptance condition.

**Formal task verdict: `BLOCKED` (independence/provenance conflict, not a discovered code defect).** In this same physical ChatGPT conversation, the assistant earlier wrote both F1/F2 implementation commits `e6fd64b8…` and `c4ea30ba…` into source PR #434. Thus the conversation cannot also provide the genuinely *independent* L3 sign-off requested by this task; reporting `PASS_FOR_DIRECTOR_MERGE_REVIEW` without qualification would conceal an authorship conflict. This does not invalidate exact-HEAD GitHub CI or the code-path evidence.

**One bounded next step:** have a **separate physical QA conversation that did not implement F1/F2** perform a brief, READ-ONLY delta check against the pinned two source heads and seven exact-HEAD CI runs, then issue `PASS_FOR_DIRECTOR_MERGE_REVIEW` or a concrete correction if warranted. Do not merge/deploy based solely on this same-chat assessment. After an independently reviewed merge, observe one ordinary unattended nightly chain and check published live JSON.

**Scope of this report:** only this new report file in a separate draft PR; no changes to source PR #434, old QA PR #437, workflows, production, `CURRENT_TASK.md`, Board, registry, caches, or Scheduled Tasks.