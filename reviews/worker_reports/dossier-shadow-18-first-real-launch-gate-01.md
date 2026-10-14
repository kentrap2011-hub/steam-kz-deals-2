# Worker report — Dossier 18 frozen Research: first real launch gate

Task: `WORKER_TASK_DOSSIER_SHADOW_18_FIRST_REAL_LAUNCH_GATE_01.md` (`dossier-shadow-18-first-real-launch-gate-01`)  
Worker: **ЧАТ 2**; mode **READ-ONLY / ACCEPTANCE, report-only PR**  
Repository: `kentrap2011-hub/steam-kz-deals-2`; base `main`  
Observed main HEAD (2026-10-14 check, **diagnostic only**, NOT a precommitted launch value): `7200f63ab2f1013571b7984036a84e5c4cca5fc7`.

## Disposition: GO for a separately Director-authorized manual GitHub publication attempt; NO-GO for Research/Assembly semantics

**REAL SANDBOX FREEZE: NOT PUBLISHED.** The actual GitHub ref `refs/heads/sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research` returned **404** from Git refs API, independently corroborated by an exact-name branch search returning zero matches, including on a fresh repeat immediately before preparing this report. Thus no verified **real** marker commit, marker parent, or durable buffer blob exists to cite. No PR fixture, stdout proposal, offline receipt, or test-created Git commit is substituted for this authority. If the ref appears after this inspection, **do not dispatch again**: first read its original Git parent/marker/buffer lineage with the strict frozen verifier.

The previous publisher implementation **PR #218** was merged on 2026-10-13 at `c23d952418edca8adbc8e6db0a69ba89698830b4`. Its **final PR head** `80e2d491030ef2df06ac5c475817e715070e0b73` has two completed successful workflow runs:
- **Validate Dossier shadow GitHub-frozen Research publisher (PR only)**: [Actions #38201155850](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38201155850), success.
- **Validate backlog dispositions**: [Actions #38201155837](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38201155837), success.

The exact Git blobs of the manual publisher workflow, publisher Python script, PR-only validation workflow, and publisher negative test script on inspected `main` equal the corresponding blobs on the *tested final* PR #218 head: respectively `2eed6346d4c0e5050cd51d28a39cef895532359d`, `9db3b44e1a3c7954b588b2fba42e28265ccdb44a`, `4ddb9dcf90015bc2e84025eae933ce202936e2ef`, `7abc6e9b2cb6712cf09f4775ab9424cab4e0dbea`. No new untested publisher-code drift was detected. **No repeat** of the previously proven historical receipts, 114-source/year/date audits, disposable CI QA, or other unrelated checks was performed.

## Exact allowed publication contract and residual risk

Current `.github/workflows/publish-dossier-shadow-research-freeze.yml`:
- Name: **Publish frozen Dossier 18 Research trial (manual, once)**.
- **Only** event: `workflow_dispatch`. There is no `push`, `pull_request`, `schedule`, or implicit semantic run. The job explicitly requires `refs/heads/main`, first run attempt, and `contents: write` permission; it has a single-use concurrency group with `cancel-in-progress: false`.
- Both inputs are **required strings**, spelled `expected_main_sha` (exact *40-hex current main* SHA) and `confirmation` (literal `PUBLISH_DOSSIER_SHADOW_18_ONCE`). The Python gate checks the matching `GITHUB_SHA`, `HEAD`, live remote `main`, exact workflow identity and event; a drift fails closed. **Compute expected SHA immediately before dispatch**, not from this report: `main` is changing independently.
- The exact fixed original group order is **[3, 8, 13, 15, 18, 20]**, six indivisible 3-game groups / **18 exact ordered AppIDs**: `1508750,1517180,1533420;1590230,1599600,1607130;1849000,1857090,1868140;1999170,1999360,2009010;206420,2067050,2076140;2124120,213610,2138710`. Both previously disputed-year games `213610` and `2138710` are retained, not silently excluded or adjudicated here.
- Original immutable historic source: `95a4bf4990a60082ecb3302da5bc7f23b618d93e`; writer work blob `ef40fc186aabc79dfd24c72864dbe43817a56039`; audit blob `8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b`. The publisher derives all original frozen assignments by the existing strict `--propose-buffer` verifier; it does not reselect scope or reinterpret old evidence.
- The **only permitted new published file paths**, on the isolated sandbox branch: `reviews/dossier_shadow_offline/trials/dossier-shadow-calibration-20261011-6x3/research_buffer.json` in a first single-parent Git commit, followed by **one added** `reviews/dossier_shadow_offline/trials/dossier-shadow-calibration-20261011-6x3/run_starts/<32-hex-nonce>.json` in its own single-parent marker-only commit. Branch creation uses an absent-ref remote push lease, not overwrite/replay.
- The publisher requires the original `frozen_trial` result to remain `blocked` for sandbox semantics even after writing and remote re-fetch. `config/dossier_shadow_research_trial_contract_v1.json` retains `standalone_sandbox_semantics_approved=false`, `reviewer_roles_finalized=false`, `canonical_production_authority_active=false` and `production_execution=false`.

**Remaining unproven runtime condition (not a discovered defect):** an actual Actions dispatch has not occurred, so the effective GitHub Actions token's ability to push the new sandbox ref and the complete live run have **not** been demonstrated by PR-only CI. If the action fails because of token/repository/branch policy or unexpected live head drift, record the exact Actions error; do **not** synthesize a branch/marker, rerun the failed publication or bypass the gate in a developer chat. There is no confirmed new blocking defect in the unchanged publisher source.

## Director GO/NO-GO card — single next step and required proof

**Next owner: Director, not this worker. Exactly one separate live action, only after Director consciously authorizes it:**

1. Open GitHub **Actions → Publish frozen Dossier 18 Research trial (manual, once) → Run workflow**. Choose branch **main**. **Immediately before clicking**, read the *then-current* `main` SHA and confirm the sandbox ref still does not exist. Set `expected_main_sha=<that exact 40-hex SHA>`, `confirmation=PUBLISH_DOSSIER_SHADOW_18_ONCE`; dispatch **once**, without rerun. If branch already exists, skip this action and verify it instead. This report **does not** constitute the dispatch approval or perform it.

**Required after-run read-only verification before claiming publication:** the Action finished successfully; summary and remote ref show **the same 40-hex `marker_commit`** on `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`; marker commit has **exactly one Git parent**, equal to reported **`buffer_commit`**; marker-only path and parent buffer-only path each have a single `A` diff; reported **`buffer_blob_sha`** equals the buffer's real Git blob in that parent; `frozen_trial` revalidates the original fixed source, six grouped bindings, all 18 ordered assignment IDs, old writer receipt bindings and frozen schema/contract/prompt blob hashes from that marker parent. Record real SHA values and run ID **only after** successful publication.

**Even after a verified marker:** the state becomes `published_real_GitHub_marker_and_buffer` but **`sandbox_research_invocation_ready=blocked`**; a separate Director decision must first explicitly approve sandbox-only semantics, appoint **independent blinded reviewers A and B** and separate **adjudicator C**, and define review/quality stop rules. Only then separately authorize a bounded one-shot semantic Research worker against the precise verified `shadow_marker_commit` and `research_buffer_path`; Research and later Assembly each need their own actual authority. No automatic activation of two-stage Dossier or change to one-stage production follows from publication.

## Isolation and scope

This worker read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, the named task, relevant Dossier routes / `CURRENT_TASK.md` context, ownership/trial contracts, previous accepted publisher task/report, current manual workflow and exact PR-only publisher/test proof. Ownership preflight: **GitHub** continues to own sample selection, durable immutable buffer, marker and validation; this report takes **no** control-plane or semantic authority. No unresolved architecture decision was converted into implementation.

**The entire proposed PR diff consists of this one report file.** No changes to `CURRENT_TASK.md`, `web/**`, `scripts/progressive_personalization.py`, `config/progressive_pass2_contract.json`, `data/production/**`, `data/cache/**`, `data/ai_inbox/**`, `data/control/**`, workflow/scripts/contracts, Deep history UI/stats, ranking, Fast, visual or site statuses. No marker/branch publication, Actions dispatch, Research/Assembly worker, semantic call, production write, Scheduled Task action, recovery/retry or queue edit. **No self-merge.** Stop after report.

Final task status: **`launch_gate_ready_for_separate_manual_director_dispatch`; actual publication `blocked_pending_Director_action`; sandbox semantics `blocked_pending_separate_authorization`.**
