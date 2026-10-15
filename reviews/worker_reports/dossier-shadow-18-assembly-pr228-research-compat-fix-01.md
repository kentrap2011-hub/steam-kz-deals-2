# Worker closeout — dossier-shadow-18-assembly-pr228-research-compat-fix-01

- Worker: ЧАТ 2. Existing implementation PR **#228 only**; one original 18-item sandbox.
- Date: 2026-10-15.
- Scope: Stage B compatibility with **merged Research PR #227**; no self-merge.
- Real trial status: **BLOCKED / NOT EXECUTED**. No real Research freeze,
  Research feasibility marker, semantic Research, Assembly marker, Assembly
  result, or A/B/C assessment is claimed. Only disposable synthetic Git fixtures.

## Root causes and exact resolution

1. Wrong former Stage B ref `sandbox/dossier-shadow-calibration-20261011-6x3`
   replaced with the ONLY Research publisher constant imported from
   `scripts/dossier_shadow_research_trial_publish.py::BRANCH`:
   `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`.
2. The former Stage B test `frozen_trial.sandbox_semantics_authorized=True`
   directly contradicted merged Research PR #227. **Original frozen_trial
   MUST remain status=blocked** with original sandbox reviewer and semantic
   flags false. Stage B uses only the independently GitHub-created feasibility
   direct-child commit checked by the existing
   `scripts/dossier_shadow_research_feasibility.py::authorized_trial`.
3. Frozen Assembly buffer binds Research marker, original immutable Research
   buffer SHA, feasibility authorization **commit/path/blob SHA**, immutable
   original 18-item assignment order and exact semantic prompt/contract.
   Each submitted Research commit must be downstream of the distinct Research
   authorization and undergo `inspect_authorized_transport` (which calls
   canonical Research `inspect_transport`), with original source/privacy,
   Git single-added-file provenance and unchanged current blob.
   Missing A consumes zero attempts; B and C may proceed independently.
4. Stage B manual issuer takes exactly two real 40-hex inputs: original
   Research marker and separate feasibility authorization commit. It is
   workflow_dispatch-only on the imported original sandbox ref with run
   attempt 1, exact repository/workflow identity and create-only buffer then
   marker commits. No second scheduler, buffer validator or canonical writer.
5. Research submissions AFTER the Research authorization and BEFORE the
   Assembly issuer are permitted. An actual Research commit must have its own
   original single-add Git provenance; an operator's JSON/path cannot authorize
   itself. The Stage B code never runs semantics.

## Original immutable PR #227 authority

Research PR #227 merged to main on 2026-10-15 at
`7d4a39b8ede4e858ae9ef58442c6cdb34df227fe`; its accepted
`config/dossier_shadow_research_feasibility_contract_v1.json`,
`scripts/dossier_shadow_research_feasibility.py` and workflow
`.github/workflows/authorize-dossier-shadow-research-feasibility.yml`
are NOT edited in this PR. Exact original publisher remains
`scripts/dossier_shadow_research_trial_publish.py`. The feasibility
auth commit MUST add only
`reviews/dossier_shadow_offline/trials/<trial>/authorizations/research-feasibility-v1.json`,
have exactly the original frozen Research marker as its Git parent, and
bind the marker-parent source/contract/prompt/schema/Research buffer Git
blobs. Actual GitHub remote first-parent chain is required.

## Exact future GitHub issuer and manual semantic sequence

This is **not** permission to dispatch any of these workflows in this worker:

1. After Director merges PR #228 and verifies all accepted issuer scripts and
   workflows are in `main`, manually run the ORIGINAL Research frozen
   publisher from main using its own documented exact inputs; it creates the
   one original `...-frozen-research` branch and genuine create-only Research
   buffer + original Research run-start marker. Independently attest successful
   GitHub Actions publisher run, branch, first-parent and frozen marker parent.
   DO NOT create a second sandbox branch.
2. Run `authorize-dossier-shadow-research-feasibility.yml` on **main** with
   `expected_main_sha`, `original_marker_commit` and exact confirmation
   `AUTHORIZE_DOSSIER_SHADOW_18_FEASIBILITY_ONCE`. Require first-attempt
   success and GitHub's original-marker direct-child create-only authorization
   commit on the same original sandbox branch, strictly matching immutable
   original parent blob pins. Old `frozen_trial` status still BLOCKED.
3. Only through a separately explicitly user-launched Research one-shot, use
   `config/dossier_shadow_research_feasibility_one_shot_prompt.md` and its
   existing authorized trial / submitted immutable Research transport route.
   Do NOT run semantics in this developer chat. Actual submitted Research
   packages must be on that branch after authorization.
4. Run `issue-dossier-shadow-18-assembly.yml` via explicit GitHub
   `workflow_dispatch` with **ref**
   `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`,
   `research_marker_commit=<actual original Research marker SHA>`, and
   `research_feasibility_authorization_commit=<exact direct-child auth SHA>`.
   Precondition: this workflow and Stage B scripts were inherited by original
   marker parent from main. Stage B freezes its plan as exactly one new file
   then introduces exactly one new marker path in a second single-parent commit.
   On any source/ref conflict, STOP without retry/rebase.
5. Independently retrieve the **actual GitHub Actions issuer run** by its ID:
   verify exact workflow path, `workflow_dispatch`, `run_attempt=1`, correct
   repository and original sandbox branch, successful conclusion, step summary
   and the corresponding two actual new commits and Git parents. Match actual
   marker Git path/blob, marker issuer ID, frozen plan's exact feasibility
   commitment and original Research ancestry. A value in marker JSON alone is
   NOT independent issuer attestation; inability to prove this blocks semantic
   invocation.
6. Only a separately user-launched Assembly one-shot operator uses frozen
   `inspect` with exact `assembly_marker_commit` and submitted immutable
   Research AppID->introducing-commit bindings to select `ready` items.
   Create-only Assembly transports remain ONLY under
   `reviews/dossier_shadow_offline/trials/<trial>/assembly/`. No canonical
   Dossier acceptance or Deep permission is implied; A/B/C is later.

## Validation and safety

- Synthetic joint Git fixture covers original BLOCKED marker, separate
  direct-child feasibility authorization, immutable original branch/18 items,
  actual create-only Research commits after authorization, B/C ready with A
  missing or invalid, strict provenance, forbidden authority mutation,
  wrong branch/marker/authorization, stale Research and Assembly buffer, extra
  production-side writes and issuer identity fail-closed checks.
- Existing Research feasibility suite, original Research source/privacy and
  standalone 18-game baseline, existing async Assembly, strict final three-game
  and one-stage Dossier suites are included in dedicated PR CI.
- Verified correction code/merge head `cbc8b1bc48c037f8d417fc629f9ee1cc8b665792`:
  Stage B joint Research feasibility → Assembly PR CI **SUCCESS** (run
  `38776182442`); existing inactive eventual-chain QA **SUCCESS**
  (`38776182479`); backlog dispositions **SUCCESS** (`38776182951`);
  execution ownership validation **SUCCESS** (`38776171659`).
  These are disposable synthetic/offline checks, NOT a genuine freeze or
  actual semantic Research/Assembly proof. The final report-only commit
  requires the normal PR CI check again on its own exact SHA.
- No changes to `data/production`, canonical Dossier, cache/inbox/control,
  Deep, Fast, ranking, site, Scheduled Tasks, Director Board or
  `CURRENT_TASK.md`. No semantic analysis executed, no new implementation
  PR created, PR #228 remains open for Director review.
