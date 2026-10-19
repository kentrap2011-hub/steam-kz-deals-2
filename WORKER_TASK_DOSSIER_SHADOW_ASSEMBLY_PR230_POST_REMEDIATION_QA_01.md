# WORKER TASK — PR #230 POST-REMEDIATION INDEPENDENT QA

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Worker: **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2**, independent of old QA and the implementation Chat 1.
Task ID: `dossier-shadow-assembly-pr230-post-remediation-qa-01`
Mode: **READ-ONLY / INDEPENDENT SECURITY + INTEGRATION RE-REVIEW**
PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230
Implementation branch: `fix/dossier-shadow-assembly-github-python-handoff-01`
Observed PR HEAD: `48db1de81294008e1f55e857c4a42c663184e8a3` (always re-fetch; no stale-head approval).
Output: one new top-level GitHub PR #230 Conversation comment and a short chat reply. No source commits or report files.

## Mandatory START, sources and boundaries

Fully read latest `CHAT_PROTOCOL.md` from `main` and complete START gate. Then fully read THIS task from `main`, `CHAT_CONTEXT.md`, the relevant narrow `PROJECT_ROUTES.md` section, `config/execution_ownership_contract.json`, and exact original isolated Assembly contracts / validators. Work **only** in `kentrap2011-hub/steam-kz-deals-2`; do not use another repo. Stop and correct an ambiguous tool repo target.

Fetch fresh PR #230 state (head/base/draft/merged/diff) and examine **full security-critical workflow and adapter**, not only the amended lines. Read the full original independent `CHANGES_REQUIRED` comment https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230#issuecomment-6264321596, claimed remediation comment https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230#issuecomment-6273611265, and the author report `reviews/worker_reports/dossier-shadow-assembly-pr230-qa-remediation-01.md` from the PR branch. These are claims to independently verify, not proof by themselves. Review the diff against original failing head `f7e02689cf73b54b068fd042ba4abe7270a1871c`, and verify final head `48db1de81294008e1f55e857c4a42c663184e8a3` unless it changed; if it changed, independently examine the newer head and its exact CI.

Original immutable sandbox `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`; original Assembly marker `2c2649fb98322507cd3758ff0ff7992128f94de0`, buffer parent `9782ab8492aadc744c23ec0425abf8d2d877590e`, Research marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, research feasibility authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`, original issuer run `39054131983` (DO NOT rerun). Authentic read-only inspect counted 18: **12 ready**, 2 invalid (SULFUR `2124120`, Sifu `2138710`), 4 Research missing (`1508750`, `1607130`, `1849000`, `1857090`). These are **transport statuses**, not canonical accepted Dossiers.

At assignment candidate-head CI run `39297241772` (authentic original inspect/Stage B and handoff negative fixtures), `39297241824` (inactive eventual Dossier chain), `39297242033` (backlog) each SUCCEEDED on `48db1de81294008e1f55e857c4a42c663184e8a3`; publish job SKIPPED. Independently re-fetch actual GitHub run SHA, jobs and evidence. An intermediate chain failure `39296585463` was described as a pre-existing flaky SHA test; determine whether its residual risk remains, without unauthorized changes.

## Seven required gates — PASS / FAIL / UNVERIFIED for EACH

1. **Workflow and human authorization:** read-only `pull_request` cannot publish or acquire write token; narrowly scoped manual `workflow_dispatch(operation=publish)` checks exact main branch, repository, actor, first attempt, operation and input, with job-specific write rights only. A public confirmation string is NOT proof of independent human authorization; require externally recorded per-candidate Director/user consent and distinguish procedural versus enforced guards. Test forbidden inputs, event and actor logically.
2. **Immutable Stage B code and schema:** prove **executed** Stage B Python, transitive imports, strict validators/config/schema load from immutable original marker checkout, not mutable sandbox HEAD. Verify post-marker sandbox *entire Git history* is a linear single-parent one-add-only chain of permitted original candidate files. Detect code/helper/schema/Research/marker/buffer edits, extra paths, overwritten artifacts and merge commits, even if sandbox HEAD equals remote.
3. **Typed handoff provenance/races:** exact intended AppID/path, one-parent single-file introduced commit, only `outcome`, `payload`, `supplemental_operations`, pinned blob and remote tip. Check stale/withdrawn/orphan commit, branch rewrite, wrong path/extra file, refetch checks at build/verify/pre-push; identify remaining unpreventable two-ref network race rather than claiming atomicity.
4. **Canonical readiness and strict validation:** only ORIGINAL Python `inspect` may mark each game ready; only ORIGINAL `build_candidate` and `verify_candidate` with original strict V2/source-first/privacy validation can authorize candidate bytes. Invalid/missing Research must never become ready; `research_incomplete` not silently promoted to accepted.
5. **Exact candidate publication:** no dirty checkout, staged extra paths, duplication, collision, non-fast-forward overwrite, force/rebase/auto-retry or write to main/production/Deep/Fast/ranking/normal Dossier. Require strict one-file direct-child verification and remote ancestry before ordinary push.
6. **Nonblocking progress and manual operability:** independently reproduce or falsify old cross-ready deadlock. Ready A without a candidate MUST NOT block ready B/C; preserve frozen 18 traversal/report order and per-item one-shot. Verify a feasible **human GitHub Actions UI** runbook after merge/default branch, not a nonexistent ChatGPT GitHub dispatch tool. No actual manual dispatch without new explicit authorization, including read-only inspect. No real semantic Assembly/publish test or claim.
7. **Regression quality and final-head CI:** examine targeted negative tests for tampered Python/schema, orphan/withdrawn/ref drift, forbidden actor/event/ref/operation, extra/wrong-path typed JSON, invalid/missing siblings, valid one-file candidate and non-fast-forward. Check the real inspect ran full original Git history with exact 12/2/4 and that final-head runs completed (distinguish skipped publish from success). Check the reported flaky P2 test and possible main drift. CI GREEN / mergeable=true alone does not mean security verified.

For each finding identify verified fact vs plausible residual risk, source `path:line`, actual CI/job or Git SHA; no unfounded PASS. Focus on original reviewer blockers, not unrelated issues. If any critical boundary remains unproven, state `UNVERIFIED` and why.

## Durable result and prohibited actions

Post exactly ONE new top-level comment to PR #230 via connected GitHub API (not a GitHub review/APPROVE). Heading: `INDEPENDENT RE-REVIEW — PR #230 after QA remediation`. The comment MUST include exact current PR SHA/base, seven gate verdicts and evidence, closure/nonclosure of each original QA finding, CI IDs, residual manual approval/dispatch and TOCTOU caveats, no real semantic/publish proof, ONE final verdict **`PASS_FOR_DIRECTOR_MERGE_REVIEW` / `CHANGES_REQUIRED` / `UNVERIFIED_BLOCKED`**, and one bounded next action.

Immediately before commenting, re-fetch PR head. If head drift makes review stale, either re-review new head or report `UNVERIFIED_BLOCKED`; never publish a stale PASS. If GitHub comment creation fails, give the complete report in chat and explicitly say no durable comment was posted.

STRICTLY FORBIDDEN: any code/source/task/Board/registry edits; new branch, PR or commit; PR approval, ready-for-review, merge; workflow dispatch, sandbox source/marker/research mutation, real Assembly, candidate publish/retry, production, Scheduled Tasks, or another repository. This worker may change **only the one GitHub PR Conversation comment**. Leave PR in DRAFT/UNMERGED. Director decides review acceptance, PR merge and any separately authorized real operation.

End with concise Russian summary and link to the new PR comment if published.
