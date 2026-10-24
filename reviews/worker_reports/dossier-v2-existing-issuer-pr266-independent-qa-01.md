# Independent QA — Dossier V2 reuse of existing manual issuer, PR #266

**Task:** `dossier-v2-existing-issuer-pr266-independent-qa-01` (НОВЫЙ ЧАТ 2, independent QA).  
**Verdict: `CHANGES_REQUIRED`.** Do **not** merge PR #266 as a verified issuer adaptation yet.  
**Reviewed exact implementation HEAD:** `1d46b84aff35feee0aca68fc8ad9f3154a330036` (PR #266 still open, draft; HEAD checked again immediately before this report).  
**Evidence:** existing `main` task/protocol, PR #266 changed-file list and exact HEAD source, original issuer evidence PR #264, merged inactive V2 PRs #239/#243, five GitHub Actions runs attached to that PR head. No real issuer, grant, manifest, marker, Research, Assembly, canonical ingest, production or deploy attempted.

## Scope / whitelist

All and only seven expected paths changed in PR #266:

1. `.github/workflows/authorize-dossier-shadow-research-feasibility.yml`
2. `.github/workflows/publish-dossier-shadow-research-freeze.yml`
3. `config/dossier_research_notes_v2_contract.json`
4. `reviews/worker_reports/dossier-v2-existing-issuer-adapt-implement-01.md`
5. `scripts/dossier_shadow_research_feasibility.py`
6. `scripts/dossier_shadow_research_trial_publish.py`
7. `scripts/test_dossier_research_notes_v2.py`

No new workflow, CI, validator, scheduler, new production or Fast/Deep writer. Both existing workflows remain manually dispatched, main-ref / first-attempt restricted, with a `v1` default selector. The existing V1 issuer functions and fixed original V1 constants are preserved in code; the version switch dispatches `v1` to the old functions. The historical V1 Git ref/Research/Assembly artifacts were not mutated. **V1 backward compatibility: PASS for inspected paths and existing offline regressions**; no V1 real dispatch was repeated.

V2 remains inactive: `manual_v2_issuer.enabled=false`; human grant commit/blob/actor fields are null; global `active`, `authorized_for_semantic_execution`, `authorized_for_canonical_ingest`, `production_enabled` are false. V2 dispatcher requires its distinct confirmation, actual GH Actions event/ref/repository/workflow/SHA/first attempt; `v2_grant` also checks an exact immutable single-add grant, original group pins and matching Actions actor ID. V1 historical marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f` and approval `2a726cf6731c0fc1e7bc809474627383c107ef9b` do not serve as V2 grants. These are meaningful fail-closed gates **with current inactive configuration**.

## BLOCKER QA-266-01 — fabricated V2 freeze can be laundered by real post-marker authorization

**Location:** `scripts/dossier_shadow_research_feasibility.py` lines ~383–433 (`publish_v2_authorization`), ~328–381 (`verify_v2_authorization`), `scripts/dossier_research_notes_v2.py` lines ~200–230 (`_manifest`), and `scripts/dossier_shadow_research_trial_publish.py` lines ~317–374 (`local_v2_freeze` / `publish_v2`).

**Observed by independent code-path inspection (not a live exploit run):**

- Legitimate `local_v2_freeze` uses `commit_new` twice and explicitly checks **source → marker** adds only the manifest and marker. But this creator-side check is **not re-established by the downstream V2 authorizer**.
- The V2 authorizer takes a caller-supplied `marker_commit` and checks that the named canonical remote sandbox ref points to it. `_manifest` checks the marker commit adds only its nonce file and that its direct parent contains the right 18-game manifest. It does **not** require the manifest-parent commit to be exactly one added file with a single parent; nor does it require the manifest's parent (freeze source) to descend from the approved human-grant/main checkout.
- `verify_v2_authorization` checks its authorization commit is one added path directly on the supplied marker. It still cannot identify which workflow/run created that **earlier marker**. `v2_expected_authorization` records the post-marker authorization actor/run ID, **not authenticated freeze issuer run identity**.
- Therefore, **once V2 enablement and the future grant exist**, a writer able to put a syntactically valid counterfeit manifest + marker on the predeclared remote branch (for example a manifest commit containing an extra unapproved file, or ancestry outside the approved freeze source) can satisfy the authorizer's current branch/shape checks. A separate legitimate authorization dispatch from the granted actor could then append an apparently valid authorization to a branch which was **not proved to have been frozen by the approved GH workflow**. The remote lease prevents a race/replay; it does not prove creator provenance of the old ref.

This violates the requested full manifest-parent/tree provenance and GH-origin guarantee for V2. The current disabled mode prevents any real launch today, but **current inactivity is not a substitute for future correct validation**.

**Minimum correction for ЧАТ 1, no new CI/workflow required:** reuse the already-existing Git plumbing to independently enforce *both* original manifest-parent single-add/single-parent/no-hidden-tree-change and approved freeze-source ancestry/bindings at post-marker authorization. Require separately checked, real first-attempt GH freeze run evidence (correct workflow, run/event/ref, source SHA, actor and successful run) before treating a supplied remote marker as an issued freeze; do not infer it from the marker Git author or from the later authorizer run. Document precisely which evidence can be checked by existing issuer code and which must remain a **manual separate pre-semantic attestation**. Add negative disposable-Git cases to the **existing** `scripts/test_dossier_research_notes_v2.py` for a forged manifest parent with an additional file, source history not containing the approved grant/main, and legitimate-looking marker/authorization on a forged remote branch. No real workflows to run.

## Authority and operational residual risks

- `v2_grant` validates the scoped grant's committed bytes and configured GitHub actor ID; it does **not independently authenticate the user's out-of-band decision or the grant PR approval**, and it does not query GitHub collaborator permission. Before any future enablement, the Director/operator must establish that the grant was genuinely approved by the user and that actor ID belongs to a trusted authorized operator. An ordinary commit or chat text is not proof.
- GitHub Actions `GITHUB_ACTOR_ID` / event / run ID are stronger than author-label claims for the **current dispatch**; evidence of completed real freeze/authorization runs and their actual GitHub records is still absent. Existing synthetic fixtures do not supply that.
- Any successful future V2 issuer is **control-plane issuance only**: separately gated semantic Research, independent Assembly/reviewers/source-quality, durable per-item GitHub receipts, original atomic 3-game writer and later canonical ingest/production decisions remain unresolved/blocked. PR #266 must not be read as approval of those paths.

## Existing exact-PR-head CI evidence and independent test limitation

GitHub Actions API independently identifies PR head `1d46b84aff35feee0aca68fc8ad9f3154a330036`, pull_request event, all five completed runs below with `success`. Workflow logs also show the code was checked out from PR's **synthetic merge ref** `63c0addaf2c3b9c9b60c073cd45faf859ef3be66` (merging the named head into base `eddea98e8abe242077c7438ad3b9526a2aa0f686`), not a standalone checkout of the implementation HEAD. This is normal PR validation, but must not be mislabelled as direct detached-head execution.

| Existing GitHub run | Result | Independently checked detail |
|---|---|---|
| [40071944871](../../actions/runs/40071944871), inactive Notes V2/Assembly | SUCCESS | **46/46 synthetic unit tests**, including nine new issuer-adapter cases; scripts syntactically checked |
| [40071945118](../../actions/runs/40071945118), original V1 publisher/feasibility | SUCCESS | **12 feasibility + 7 publisher + 8 original Research trial = 27/27** V1-oriented tests; disposable original freeze and proposal checks |
| [40071944771](../../actions/runs/40071944771), inactive eventual chain | SUCCESS | Original strict group, async, staging, schema and downstream offline regressions |
| [40071945076](../../actions/runs/40071945076), backlog dispositions | SUCCESS | Existing validation step passed |
| [40071944765](../../actions/runs/40071944765), site task registry | SUCCESS | Existing registry/UI validation step passed |

The developer's 46-case success claim **is supported by the GH log**. QA reviewed the new cases and original V1 checks but **did not rerun tests locally**: the connected source was inspected through GitHub; the isolated analysis container has no GitHub network access or authorized checkout of this repository. No synthetic test of the specific unhandled forged-parent path exists in this PR, so no false PASS assertion is made.

## Acceptance decision / handoff

**CHANGES_REQUIRED**: request one bounded V2-only fix in ЧАТ 1 for QA-266-01 plus the missing adversarial regression tests, preserving V1 functions/workflow defaults, without new CI, Actions, automations or architecture. Obtain a new exact HEAD and existing CI results, then perform fresh independent QA on that revision. The present PR #266 should **not** be merged based on this report. Neither this report nor later code merge would authorize a live V2 dispatch or Research/Assembly.

**Report-only scope:** this file is the only change on the independent QA branch; no implementation edits, markers, grants, GitHub dispatch, semantic execution, workflow/config mutation, merge or scheduled task were performed.
