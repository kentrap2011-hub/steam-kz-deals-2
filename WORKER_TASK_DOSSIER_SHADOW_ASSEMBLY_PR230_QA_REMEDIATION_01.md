# WORKER TASK — PR #230 INDEPENDENT QA REMEDIATION 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Existing implementation PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230
Existing implementation branch: `fix/dossier-shadow-assembly-github-python-handoff-01`
Task ID: `dossier-shadow-assembly-pr230-qa-remediation-01`
Worker slot: `СУЩЕСТВУЮЩИЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1 (автор PR #230, прямое продолжение той же PR-задачи)`
Mode: `IMPLEMENT / VALIDATE / PR UPDATE` — only address the specific review findings.
Durable result: `reviews/worker_reports/dossier-shadow-assembly-pr230-qa-remediation-01.md` in existing PR branch, plus concise PR #230 Conversation comment with exact CI/commit links.
Review authority: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230#issuecomment-6264321596
Review verdict on head `f7e02689cf73b54b068fd042ba4abe7270a1871c`: `CHANGES_REQUIRED`.

## Mandatory START / repo scope

First **fully** read latest `CHAT_PROTOCOL.md` on `main` and complete START gate. Then read THIS task fully before looking for implementation. Read `CHAT_CONTEXT.md`, relevant `PROJECT_ROUTES.md`, `config/execution_ownership_contract.json`, original isolated Assembly contracts, the specific PR #230 changed code and **the complete independent QA comment**. Respect architecture preflight before changes. Work only in `kentrap2011-hub/steam-kz-deals-2`. If tool opens any other repository or source target is ambiguous, stop and correct the target.

This is NOT semantic Assembly, NOT Research, NOT Scheduled Task, and NOT a new branch/PR implementation task. Resume the **same existing PR #230 branch**, reconcile any base divergence carefully without touching the original experimental sandbox.

## Verified boundaries at assignment

- PR #230: OPEN / DRAFT, exact existing head `f7e02689cf73b54b068fd042ba4abe7270a1871c`. Main separately advanced through director task assignment.
- Original sandbox: `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`.
- Immutable original Assembly marker: `2c2649fb98322507cd3758ff0ff7992128f94de0`. Buffer parent: `9782ab8492aadc744c23ec0425abf8d2d877590e`. Original Research marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, research feasibility authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`.
- Assembly authority issuer: GitHub Action `39054131983`, successful first attempt; MUST NOT run again.
- Exact-head CI `39212984487`: authentic read-only original Python inspect = **12 ready**, **2 invalid** (`2124120` SULFUR, `2138710` Sifu), **4 Research not submitted** (`1508750`, `1607130`, `1849000`, `1857090`). Transport readiness is NOT canonical acceptance of Dossier/Deep.
- Independent read-only QA report in GitHub PR #230 comment `6264321596`: `CHANGES_REQUIRED`. No real Assembly semantics or candidate publish has run.

## Required scoped fixes — all must be closed or explicitly BLOCKED

### A. Remove cross-game deadlock — BLOCKER (reproduced)

Current adapter `scripts/dossier_shadow_18_github_python_handoff.py::original_order_gate` disallows B when earlier A is ready but A has no candidate. This is unacceptable for independently ready original 18-game items: A may be unavailable without blocking B/C.

- Preserve exact original frozen 18-row manifest and ordering for traversal/reporting, original AppID membership and per-AppID `status=ready` from authentic `inspect`.
- Remove the new **cross-ready candidate publication prerequisite** while preserving per-item no-retry/collision/identity and strict one-shot checks.
- Add regression: A `ready` but not processed (semantic unavailable), B/C `ready` and independently publishable without retrying A; invalid/missing siblings do not block others.
- Do NOT change original Stage B's semantics, Research or queue. No worker-chosen new ordering.

### B. Freeze executable and strict-schema authority — BLOCKER (verified guard absent)

Original adapter imports `scripts/dossier_shadow_18_assembly_stage_b.py` plus transitive helpers and reads strict config/schemas from mutable `sandbox` checkout HEAD. A post-marker change to Python or schema could be executed even with a valid frozen marker/buffer.

- Ensure executing code, imported validators/helpers and strict schemas/contracts are **pinned to immutable original marker-era authority**, e.g., separate verified frozen checkout for execution + checked data/branch checkout for legitimate later create-only candidate receipts. Design must demonstrably preserve compatibility with the original Stage B `Git` provenance calls, source manifest, real marker and original submitted Research commits.
- Independently attest that **every post-marker sandbox commit** is a permitted one-parent, one-add-only original Assembly candidate artifact; reject edits of scripts/config/schema, Research, buffer/marker, extra files, rewritten candidates, merges or unexpected ancestry.
- Add targeted negative regression tampering one Python helper OR Stage B file and one strict schema/config in post-marker sandbox history, even when sandbox HEAD == fetched remote. Both must fail closed. Confirm legitimate one-file descendant candidate still passes.
- Do not replace original Python validators, relax schemas, mutate marker/issuer, or introduce new authority.

### C. Handoff remote-ref race / withdrawn commit — HARDENING

- `semantic_submission` currently checks commit against once-fetched `origin/handoff/dossier-shadow-18-assembly-typed` tip, not current remote state.
- Pin and prove exact approved semantic introducing commit and handoff tip; fail closed if remote branch is rewritten/withdrawn/changed between fetch, validation and final candidate publication. Select a minimally sufficient lease/refetch/check policy without inventing a recovery/retry loop.
- Cover stale/orphan/withdrawn semantic commit, branch ref drift, mutation/overwrite, extra-file/wrong-path typed introduction in tests; preserve exact typed 3-field transport and original single-parent introduction.

### D. Workflow authority and actual operability — SECURITY + FEASIBILITY

- Reverify `pull_request` job has read-only permissions and cannot publish.
- For manual `publish`, verify branch/main/repo, first attempt, intended actor, explicit operation and narrowly scoped contents write. The public confirmation string alone does **not** prove human authorization: specify/document how the Director/user explicitly authorizes each one-off semantic candidate publish outside the workflow (recorded consent/provenance), and do not claim automatic enforcement if only procedural.
- Prove a realistic operator runbook for **GitHub Actions UI manual `workflow_dispatch`** if the connected ChatGPT GitHub plugin cannot dispatch; do not invent a callable connector action. Without user authorization, do not trigger real `publish` or create typed game results. If testing of UI is appropriate and genuinely read-only, require separate explicit permission before dispatching `inspect`.
- Include risks of race between validating GitHub refs and final push, ensure no overwrite/rebase/force/retry, no unsafely tolerated dirty checkout.
- Document how one human-operated dispatch per separately authorized candidate coexists with frozen 18 order, no auto-retries and no production acceptance. Do not create a new scheduler or semantic backlog manager.

### E. CI, proof and report — exact acceptance checks

- Update and extend PR-only synthetic Git fixture tests to cover A–D. Include unauthorized event/actor/branch/inputs rejection, original authority tamper checks, handoff tip races, exact one-file staging, race non-fast-forward, invalid/missing never becoming ready or canonical acceptance.
- Rerun original canonical Python real `inspect` in GitHub full original sandbox checkout; **exact expected unchanged 12/2/4**, and assert original 14 Research files/marker unchanged. Keep fixture-only semantic tests separate from genuine read-only Research inspection.
- Recheck all CI for **final PR head**, including Dossier chain acceptance and backlog checks if applicable. Do not regard earlier passing runs on `f7e02689...` as validating new changes.
- Update `reviews/worker_reports/dossier-shadow-assembly-pr230-qa-remediation-01.md` in existing PR, with every independent QA finding (PASS/CLOSED/BLOCKED), precise path/line, actual CI run IDs, remaining untested real-world operations, and direct link to QA comment.
- Add a concise **top-level GitHub PR #230 Conversation comment** explaining what changed, new head, CI, what remains unverified. Do **not** self-approve the PR or write over the independent review comment.
- Keep PR in DRAFT until independent re-review / Director acceptance. No self-merge.

## NONNEGOTIABLE EXCLUSIONS

- Only fix and test PR #230; NO new PR, production activation, semantic Assembly launch, real game candidate creation, retry of prior Research, reissue of original marker or buffer, alternate sandbox, new work queue/order, bulk schema simplification, permissive validation fallback, schedule/automation creation/change, Deep/Fast/ranking/cache/site modifications.
- Do NOT update original 14 Research JSON, original frozen Assembly buffer, marker, source scripts/contract of historical sandbox or main outside existing PR review.
- Do NOT mark result as live end-to-end proven from fixture-only tests.
- If B or D cannot safely be resolved with existing contracts/permissions, declare `BLOCKED_CONTRACT` or `BLOCKED_RUNTIME` with exact evidence and stop implementation rather than publishing an illusory full fix.

## Completion boundary

Stop after correcting the **same** draft PR #230, passing final-head CI and writing the report/comment, or after a truthful blocking report. No automatic resumption of semantic Assembly. The Director will independently re-review the delta and decide on merge.
