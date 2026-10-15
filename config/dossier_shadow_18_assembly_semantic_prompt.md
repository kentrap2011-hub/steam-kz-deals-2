# Dossier shadow 18 — isolated Assembly one-shot (NOT active today)

Trial: `dossier-shadow-calibration-20261011-6x3`. Original six groups:
`3,8,13,15,18,20`; exactly eighteen frozen original games.

**Currently REAL-BLOCKED until the ORIGINAL Research freeze and the
SEPARATE GitHub Research feasibility authorization are both real and
independently verified, plus a real Research package is submitted.**
Original `frozen_trial.status=blocked`, `standalone_sandbox_semantics_approved=false`,
and `reviewer_roles_finalized=false` remain intentionally unchanged. The
merged PR #227 separate `authorized_trial` is the only Research feasibility
permission; A/B/C quality review comes later.
This text is a future manually invoked semantic data-plane instruction, NOT
authority to start a Scheduled Task or to run from this developer chat.

## GitHub one-shot issuer (no semantic execution)

Use only the original publisher's existing sandbox branch:
`sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`. It must
contain the actual Research marker, buffer, direct-child authorization
and the implementation/workflow files inherited from main at original freeze.
NEVER create another sandbox branch. If the workflow file was not present
in main before original freeze and cannot load from the original sandbox
parent, STOP instead of inventing an alternate issuer. Run the manually
dispatched workflow `.github/workflows/issue-dossier-shadow-18-assembly.yml`
on **that exact branch**, supplying exactly two independently verified
40-hex GitHub-issued immutable inputs: `research_marker_commit` and
`research_feasibility_authorization_commit`. The latter must be the
separate **direct-child** authorization commit of the former, not a
worker-supplied flag or candidate JSON. Stage B calls the merged Research
`authorized_trial` gate; no original flags are enabled. The workflow produces
`reviews/dossier_shadow_offline/trials/<trial>/assembly_buffer.json`
as a create-only commit then a second **marker-only single-parent commit** under
`reviews/dossier_shadow_offline/trials/<trial>/assembly_run_starts/<nonce>.json`.
Its GitHub Action run identity must be independently verified as successful
and as having created this exact marker/branch. If a freeze commit races with
other writers or any first push fails, **stop**: no worker retry/rebase or
alternate marker. Never run this issuer using a worker-selected historical
HEAD, never run it on `main`, and never synthesize GitHub issuance in chat.

## Exact manual sandbox Assembly invocation — only after those gates

User explicitly launches a NEW one-shot semantic operator chat and supplies:
- `research_marker_commit=<actual original GitHub Research marker commit>`
- `research_feasibility_authorization_commit=<actual separate direct-child auth commit>`
- `assembly_marker_commit=<exact GitHub Actions marker commit>`
- `issuer_run_id=<verified GitHub Actions workflow run id>`
- `research_commits={ "<appid>": "<original Git introductory commit>", ... }`
  (missing entries mean **not submitted**, not a retry or a new work choice).

On the original exact sandbox branch, independently retrieve the actual
GitHub Actions issuer run via GitHub Actions UI or GitHub API. Verify exact
workflow path, `event=workflow_dispatch`, `run_attempt=1`,
`head_branch=sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`,
`conclusion=success`, and the run's recorded marker/authorization commits.
Cross-check actual Git first-parent chain, two create-only issuer commits,
frozen buffer blob and the original Research direct-child authorization.
The `issuer_run_id` claimed inside a marker JSON is NOT independently
verified authority; block semantics unless the matching GitHub run is proven. Use the read-only command
`python scripts/dossier_shadow_18_assembly_stage_b.py inspect
--assembly-marker-commit <sha> --research-commits '<JSON>'`.
The order is only the frozen eighteen original rows. The tool checks the
actual marker-parent Assembly buffer, unchanged Research manifest and exact
single-added Research package original Git commit/blob/raw SHA-256/canonical
SHA-256, original child AppID/title/year, post-feasibility Research commit lineage
and separate authorization provenance, original Research schema, physical
source/privacy checks and current HEAD unchanged transport. No mutable HEAD
Research substitution, no second plan, no output at `data/control/` or
`data/ai_inbox/`. A Research package is **submitted**, NOT GitHub accepted.

For each `status=ready` only, perform Assembly **from that submitted exact
Research package**, following
`config/dossier_two_stage_assembly_semantic_worker_prompt.md` section 3:
revisit the exact source for a named Research gap first; only if it genuinely
lacks that specific fact, a narrow one-gap one-product lookup. Preserve
twelve dimensions, original-work versus storefront year, conflicting evidence,
negative trade-offs and actual source/child provenance. No raw quoted player
text, profile/user/author information, private URLs, invented dates or synthetic
source verification. Do NOT run a source-review A/B/C gate before this Research
→ Assembly experiment, and do not mark any quality comparison as passed.

Build the exact candidate with
`scripts/dossier_shadow_18_assembly_stage_b.py::build_candidate(repo,
marker_commit=..., research_commits=..., appid=..., semantic={
"outcome": ..., "payload": ..., "supplemental_operations": ...})`.
This delegates ALL non-namespace validation to the **existing**
`DOSSIER-ASYNC-ASSEMBLY-RESULT-V1` schema, source-first checks, Research
validation, privacy gate and strict V2 dossier validator. The only path
difference is the physically isolated `reviews/.../assembly/gXXXXXX/<appid>--<id>.json`
rather than the forbidden canonical inbox path. The returned
`(exact_path, exact_payload)` is a proposal, not acceptance. Create **exactly**
that one new sandbox file in a single-parent create-only Git commit on the
marker-first-parent branch. No overwrite, collision rename, production state,
cache, Deep, Fast, ranking, site or Scheduled Task writes. Before claiming
submitted, verify its original introduction with `verify_candidate` and
obtain GitHub commit/blob proof. Full semantic attempt accounting belongs
only to the separately authorized operator and eventual GitHub receipt;
neither a missing file nor a typed diagnostic consumes an Assembly attempt.

For `research_not_submitted`, `research_transport_invalid` and
`candidate_already_submitted` never call semantics or fabricate a result.
Continue B and C if A is absent/invalid; never wait for sibling receipt,
whole-group completion or Research GitHub acceptance. Shared marker/buffer
or GitHub issuance mismatch is **invocation fatal**.

This pilot cannot canonically accept Dossier or grant Deep readiness. The
offline same-game A/B/C source-quality and strict original writer comparison
remains separate, using the existing
`scripts/dossier_shadow_18_assembly_sandbox.py`,
`scripts/dossier_shadow_quality_review_gate.py`, and strict final group
acceptance validators, with actual provenance and no invented reviewer score.
All production two-stage active flags remain false.
