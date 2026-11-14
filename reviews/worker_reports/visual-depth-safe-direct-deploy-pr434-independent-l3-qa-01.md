# Independent L3 QA — PR #434 depth-safe direct visual → Pages dispatch

**Task:** visual-depth-safe-direct-deploy-pr434-independent-l3-qa-01  
**Repository:** `kentrap2011-hub/steam-kz-deals-2` only  
**Mode:** independent source READ-ONLY QA; this report is the sole proposed write in a separate REPORT-ONLY draft PR  
**Verdict:** **CHANGES_REQUIRED** — do not merge #434 yet; no deployment was performed.

## 1. Exact source HEAD / diff / authority snapshot

- Source: [PR #434](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/434), open draft, **HEAD `25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43`**, base `main` (`04616932e03440d47d8aaa59e5b106393cbb91c2` at inspected PR snapshot). HEAD was re-read immediately before this verdict; **no drift** from assigned head.
- Exact **nine** source changed files, independently checked: `.github/workflows/build-daily-visual-payload.yml`; `.github/workflows/deploy-visual.yml`; `.github/workflows/validate-execution-ownership.yml`; `scripts/visual_deploy_dispatch.py`; `scripts/test_visual_deploy_dispatch.py`; `scripts/test_site_publication_resilience.py`; `PROJECT_ROUTES.md`; `PROJECT_DECISIONS.md`; `reviews/worker_reports/visual-depth-safe-direct-pages-dispatch-implement-01.md`. No unexplained source write-set.
- Reference: [RECON PR #433](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/433), report at `reviews/worker_reports/site-nov11-83-vs-100-pages-deploy-recon-01.md` in its own head `968735453aceae0c95aa9b279a0ea0b47630c3ec`. November 11 nightly build had **100** canonical items, but no fourth `workflow_run`-chained deploy. Old November 10 payload with 17 expired offers yields 83 visible when filtered; this is conditional evidence, not independent live HTTP read-back.
- Source author's report inspected at `reviews/worker_reports/visual-depth-safe-direct-pages-dispatch-implement-01.md` in exact source head. No source implementation has been edited by this QA.

## 2. Architectural authority / preflight

- Owner: **GitHub Actions control plane**, per `config/execution_ownership_contract.json`. The nightly production is one cycle, and Pages is a read-only consumer of canonical `data/production/visual/current.json`, per `config/daily_execution_contract.json` and `CHAT_CONTEXT.md`.
- `config/site_publication_resilience_contract.json` retains exact global integrity checks and local presentation isolation, without inventing browser fallbacks.
- PR design replaces the unsupported fourth `workflow_run` hop by `workflow_dispatch` from `dispatch_deploy`; no new scheduler, semantic queue, ChatGPT production responsibility, retry loop, or live Steam query. This architecture is permissible **if** the dispatch provenance and scoped paths are fail-closed.
- GitHub token recursion permits a `workflow_dispatch` exception, but normal workflow-owned `push` must not be relied on as an Actions trigger. The existing source `workflow_run` entry was removed from Deploy; `Build site current status` workflow_run, `push`, and legacy inputless manual `workflow_dispatch` remain.
- Producer has workflow-level `contents: write`, but the **new dispatch job alone** grants `actions: write`, `contents: read`; `needs: [scope, giveaway_refresh, commercial_refresh, build]` and `always() && github.ref == 'refs/heads/main' && needs.scope.result == 'success' && (one producer success)`. Pages retains `actions: read`, `contents: read`, `pages: write`, `id-token: write` and `group: pages, cancel-in-progress: true`. The privilege boundary on the producer is appropriately job-local.

## 3. Verified positives and negatives — measured versus static

**Exact-HEAD GitHub CI evidence (measured, all conclusion SUCCESS):**
- [Validate execution ownership](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416440) — confirmed job step `Test exact visual-to-Pages direct dispatch (offline only)` actually succeeded (not merely declared).
- [Validate site publication resilience](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416483) — actual validate job success.
- [Validate site deploy isolation (PR only)](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416495) — success.
- [Validate backlog dispositions](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416601) — success.
- [Validate site task registry and page](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416543) — success.
- [Validate Progressive PASS 2 core](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416345) — success.
- [Validate package purchase value](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43044416337) — success.

`scripts/test_visual_deploy_dispatch.py` directly calls `verify_dispatch_authority`, covering three successful scopes, exact deterministic degraded receipt, successful complete run, and negatives: wrong run ID/attempt/repository/workflow/main producer branch/event/SHA, failed workflow/job, wrong job/scope, incomplete job list, wrong/absent receipt, material-drift abort/no-build. Wiring assertions check workflow subscriptions, permissions, dispatch fields and receipt-verifier invocation. **These are synthetic positive/negative assertions that succeeded in GitHub CI, not real Pages publication tests.**

**Independent code/path inspection**:
- [Producer job](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/.github/workflows/build-daily-visual-payload.yml#L699-L730) sends paired original run ID/attempt after successful producer job; uploaded original receipt is a prerequisite of successful producer completion.
- [Deploy attestation](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/.github/workflows/deploy-visual.yml#L69-L116) checks a paired nonempty dispatch and fetches exact run metadata, attempt-scoped jobs and artifact; missing artifacts fail closed.
- [New helper](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/scripts/visual_deploy_dispatch.py#L21-L104) checks producer GitHub run identity, main branch, allowed event, original matching typed receipt, successful completed producer job and matching scope; checks job, not whole workflow conclusion, because dispatch is still in progress. Real historical producer run `42933371526` API metadata uses the expected workflow `path`, `workflow_run` event, repository, main and attempt fields.
- [Existing receipt verifier](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/scripts/visual_freshness_receipt.py#L398-L591) validates current canonical/staged bytes, blob/commit, appropriate scope material, and a precisely material-bound `deterministic_refresh_preserved_semantic_history` degraded observation; the new helper disallows non-persisted no-build/aborted receipts.
- Manual without inputs and status-only workflow_run remain intentionally supported; push is independently unbound and **must not** be misreported as producer-attested.
- **Locally re-executed exact-head Python tests: NOT_EXECUTED.** Container cannot resolve `github.com` to clone the exact revision; no local GitHub source tree is available. GitHub exact-HEAD CI and direct source review are the measured/static evidence, respectively. No GitHub Actions rerun, manual dispatch or Pages publish was attempted.

## 4. Findings requiring changes

### F1 — Direct commercial-only dispatch loses its scoped classification (functional regression)

**Confirmed code path:** in [Deploy `Classify canonical visual mutation`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/.github/workflows/deploy-visual.yml#L214-L279), the original receipt is parsed **only when** `EVENT_NAME == 'workflow_run'` (lines 217–220). New legitimate producer delivery has `EVENT_NAME == 'workflow_dispatch'`, even though the verified receipt was downloaded and attested earlier. Hence `receipt={}`, `receipt_is_commercial=false`, and a genuine `freshness_scope=commercial_only` cannot take the `commercial_only` classification. It incorrectly falls back to `general` (absent a separate giveaway-only diff), invoking full/general Russian description checks and [staging optional sections with `--scope general`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/.github/workflows/deploy-visual.yml#L291-L340) instead of the existing bounded-commercial path. This is a deterministic workflow-path regression and coverage gap, regardless of whether a specific live attempt eventually publishes successfully.

**Minimal expected fix:** make the classifier consume an **already attested** direct-dispatch receipt as well as the former eligible receipt path; prove `commercial_only` is restored for a verified direct producer, while forged/unbound manual, ordinary push and status-only cases are not upgraded. Add workflow-level/path fixture asserting downstream scope and stage mode for `workflow_dispatch + commercial_only`; test the wrong/missing receipt case.

### F2 — Direct-dispatch consumer does not enforce main ref (authority gap)

**Confirmed code path:** producer issues `gh workflow run ... --ref main` and checks its own `github.ref`, and helper checks **producer run** `head_branch=main`. But [Deploy job `if`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/.github/workflows/deploy-visual.yml#L52-L67) permits **every** `workflow_dispatch`; [paired-input validation](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43/.github/workflows/deploy-visual.yml#L69-L84) only verifies completeness. No check rejects a `workflow_dispatch` **itself** executing on `refs/heads/nonmain` with paired valid producer inputs. It checks original producer branch, not the consumer dispatch ref. This fails the assignment's exact-main/ref gate and leaves a manual/off-main replay route. It is not an observed exploit or production attempt.

**Minimal expected fix:** fail closed when a **paired direct producer dispatch** has `github.ref != refs/heads/main` (and ensure trusted repository identity is checked at the dispatch entrypoint); preserve expressly permitted inputless legacy manual behavior. Add a negative for non-main consumer dispatch ref, not only for non-main producer run. Document whether/how a real producer-originated dispatch is distinguished from a manual replay; present implementation does not itself attest initiating GitHub actor.

## 5. Residual regression/race risks and what is NOT proved

- The source's `pages` concurrency group has `cancel-in-progress: true`. A separate push/status-only deploy racing with a direct nightly deploy may cancel it. Existing current-canonical blob checks protect visual integrity at validation time, but **event ordering, scheduling and live winner/liveness were not exercised**. Exact one-deploy outcome under real overlap is **UNVERIFIED**; do not present a static CI test as proof of no race.
- New `dispatch_deploy` is `always()` with an **any-success** producer condition. Scope normally chooses one job; simultaneous giveaway/commercial flags, competing artifacts with the same name, or one successful sibling + one failed sibling are not exhaustively represented by synthetic fixtures. Any future handling must fail closed rather than dispatch a falsely fresh receipt.
- Run/attempt artifact binding and exact source metadata are inspected, but GitHub `actions/download-artifact@v4` and job-list API execution were not tested end-to-end in a live direct dispatch.
- **No new nightly post-merge chain** has occurred for PR #434, which remains draft and unmerged. A successful CI suite is not deployment acceptance. No independent live response SHA, `generated_at_utc`, or 100-current-active-item read-back was obtained in this L3 task; it must not be inferred from a Pages job's success.

## 6. Verdict + one minimal next step

**CHANGES_REQUIRED** at exact source HEAD `25bedb4f01ff7c85cb2e038c2fd15b2106bdaa43`. The direct handoff architecture and much of the attestation are sound, and the seven required exact-HEAD CI runs are green; however **F1** breaks a permitted scoped deploy and **F2** leaves the new consumer's main-ref authority unguarded. Both are testable and confined to the implementation source PR.

**One bounded next step:** return **PR #434 to its implementation worker** for the two minimal fixes plus dedicated positive/negative dispatch-event/ref/scope tests, then obtain a fresh exact-HEAD CI set and a new independent L3 assessment. No independent QA auto-merge. Only after director merge gate can the **ordinary unattended nightly** producer → direct Pages dispatch → Pages success → independent live-URL JSON read-back (current 100 active offers) establish production acceptance.

**QA write boundary:** only this new report file in a separate REPORT-ONLY draft PR; no source/production/workflow/cache/registry/Board/`CURRENT_TASK.md` changes, no GitHub Actions dispatch/rerun, no Steam collection, no Scheduled Tasks or semantic worker.
