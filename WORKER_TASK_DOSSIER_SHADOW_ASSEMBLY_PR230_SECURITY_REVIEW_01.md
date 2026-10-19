# WORKER TASK — INDEPENDENT PR #230 SECURITY AND INTEGRATION REVIEW 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`
Task ID: `dossier-shadow-assembly-pr230-security-review-01`
Mode: `READ-ONLY AUDIT / SECURITY REVIEW`
Output: ONE permanent top-level GitHub PR #230 Conversation comment, plus concise chat report. Do NOT open a second PR or change source files.

## Start and authority

First read `CHAT_PROTOCOL.md` from current `main` and complete START gate. Then read this task **in full**, relevant `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md` only if explicitly acting as Director (normally no), the ownership contract, original shadow Assembly contracts and minimal `PROJECT_ROUTES.md` entries. Work exclusively in `kentrap2011-hub/steam-kz-deals-2`; if a GitHub tool selects another repo, stop and switch before doing anything. This is an **independent** review: do not trust the author’s report as proof, and do not reuse the original implementation chat.

## Exact PR under audit

- PR: https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230
- Expected PR base: `main`.
- Expected PR code head as assigned: `f7e02689cf73b54b068fd042ba4abe7270a1871c`. If changed, fetch the newer head and precisely identify the changed diff; no unacknowledged substitution.
- Expected title: `Fix isolated shadow Assembly Python handoff via original GitHub checkout`.
- PR is DRAFT / OPEN at assignment time. Do not merge or mark ready for review.
- Prior QA report: `reviews/worker_reports/dossier-shadow-assembly-github-python-handoff-fix-01.md` on the PR branch, not yet in `main`.
- Original sandbox (immutable source): `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`, original Assembly marker `2c2649fb98322507cd3758ff0ff7992128f94de0`, original issuer GitHub Action run `39054131983`.
- Canonical Python inspect has already genuinely run in read-only GitHub PR workflow `39212984487`, reporting exactly 12 `ready`, 2 `research_transport_invalid` (2124120 SULFUR and 2138710 Sifu), 4 `research_not_submitted`. These are transport/readiness results only, not accepted Dossiers. Separate synthetic tests passed. **Real `publish` and real semantic Assembly HAVE NOT run.**

## One focused independent QA mission

Inspect actual PR diff (all seven changed files), full security-critical workflow and adapter, original frozen `scripts/dossier_shadow_18_assembly_stage_b.py`, Research transport/validation helpers, pinned schema/contracts, and exact GitHub Actions run/logs/artifact as needed. Independently test or reason about concrete fail-closed scenarios, with file:line evidence; do not review unrelated architecture.

Evaluate each gate as PASS, FAIL or UNVERIFIED:

1. **Actor and workflow authority.** `pull_request` cannot publish. Only exact `workflow_dispatch(operation=publish)` on `main`, first run attempt, correct repository and permitted actor, with explicit Director confirmation, may write. Check YAML expression/permissions pitfalls, dangerous event contexts, caller-input substitution and whether PR checkout can obtain write credentials.
2. **Original immutable authority.** Running the workflow from updated main must not replace or reinterpret original sandbox-era marker, frozen queue, original Research commits, pinned blobs or original Stage B Python/strict schemas. Validate both checkouts, real HEAD/remote ancestry, fixed 18 order and no alternate marker or Research rewrites.
3. **Submission Git transport.** Exactly one new typed semantic file per original ready game under `reviews/dossier_shadow_offline/handoff/dossier-shadow-calibration-20261011-6x3/<appid>.json` on `handoff/dossier-shadow-18-assembly-typed`, with actual introducing single-parent create-only commit, unchanged blob, exact three semantic fields, safe path and no identity source switch. Include branch/history race and stale pointer checks.
4. **Canonical validation / no bypass.** Only original Python `inspect` can declare per-AppID `ready`; only original `build_candidate`/`verify_candidate` plus strict V2 and source/privacy rules determine sandbox candidate publication. Preserve two known invalid and four missing; do not allow `research_incomplete` to be silently misclassified as canonically accepted.
5. **Write isolation and atomicity.** Exact one-file single-parent sandbox candidate commit; no main/production, `data/ai_inbox`, `data/control`, Deep, ranking or current Dossier writes. Test collision, double submit, dirty checkout, non-fast-forward branch race, and possible commit/branch mutation between verification and push.
6. **Operational feasibility.** End-to-end procedure after merger is implementable through actually available GitHub connector permissions (create handoff branch, create file, Actions manual dispatch and read results). Do not claim fully proven LIVE production or real semantic handoff from synthetic tests; distinguish reproducible facts from assumptions. Check whether strict sequential `original_order_gate` could trap later games if earlier ready cannot produce an output.
7. **Tests and artifact.** Review final PR HEAD and actual completed GitHub runs. Confirm that read-only Python used authentic original sandbox history and recorded 12/2/4. Decide if tests meaningfully cover forbidden permissions, wrong file path, invalid metadata, source tampering, orphaned commits, and atomic push. Identify remaining *blocking* risks versus acceptable separately gated future real-operation risks.

In particular review a **potential ordering deadlock**: `original_order_gate` refuses later `ready` games until earlier ready games have candidates. The pilot previously required nonblocking handling of missing/invalid siblings. Check whether a previous ready game whose semantic attempt is blocked/unavailable would unexpectedly prevent all subsequent independently ready games; assess compatibility with original contract rather than assuming the new gate is correct.

## Report and acceptance

Post one durable top-level PR #230 Conversation **comment** (not APPROVE, REQUEST_CHANGES or PR merge) with title `INDEPENDENT QA — PR #230 Assembly Python handoff`, directly via `mcp__GitHub__add_comment_to_issue` or equivalent authorized GitHub connector. PR comments are the authoritative durable review report for this read-only assignment; no code/report-branch changes. If comment publication is unavailable, explicitly say so and provide a complete copyable report in chat; never pretend it was saved.

Your PR comment must contain:
- exact PR SHA reviewed, original sandbox SHA and GitHub run IDs;
- 7 gate results, concise file/line evidence for each failure;
- reproducible actionable blockers and whether they were verified or suspected;
- one **final verdict**: `PASS_FOR_DIRECTOR_MERGE_REVIEW`, `CHANGES_REQUIRED` or `UNVERIFIED_BLOCKED`;
- explicit unchanged boundary: zero semantic Assembly launched, zero published Assembly results.

Rules: NO code edits; no PR approvals/merge; no workflow dispatch; no Git commit, branch, marker, retry or recovery; NO Research, real Assembly, Scheduled Task or production operations. No changing existing PR head or original sandbox. The Director will handle any remediation as a separate scoped task or approve merge afterward.

Stop after the GitHub comment and short final report containing the comment link (or transparent write blocker).
