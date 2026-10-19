# Worker report — dossier-shadow-assembly-github-python-handoff-fix-01

Task: `WORKER_TASK_DOSSIER_SHADOW_ASSEMBLY_GITHUB_PYTHON_HANDOFF_FIX_01.md`  
Mode: developer-only, isolated shadow, no Research / semantic Assembly / one-shot issuer / Scheduled Tasks.  
Status: **implementation proposed, full acceptance subject to PR CI and Director review**.

## Independently checked before changes

- Repository: `kentrap2011-hub/steam-kz-deals-2`, `main` as base.
- Original sandbox head is exact Assembly marker `2c2649fb98322507cd3758ff0ff7992128f94de0`; original Assembly buffer first parent is `9782ab8492aadc744c23ec0425abf8d2d877590e` with Git blob `5c7e66db7d3880098c0cd85f0690661c9655cd09`.
- Original Research marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, direct-child separate Research authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`.
- Original issuer GitHub Action [39054131983](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39054131983) completed successfully, `workflow_dispatch`, `run_attempt=1`, original sandbox branch. Original marker Git author is GitHub Actions.
- GitHub commit listing independently confirmed exact **14** original single-file Research-introduction commits, pinned verbatim in `config/dossier_shadow_18_github_python_handoff_pins_v1.json`. The other **4** AppIDs are `1508750`, `1607130`, `1849000`, `1857090` (not submitted). Neither QA findings for `2124120` and `2138710` nor `research_incomplete` may be converted into `ready` without real Python inspect.
- In developer container, GitHub DNS is unavailable: `git ls-remote https://github.com/... refs/heads/main` fails `Could not resolve host: github.com`. This reproduces why a ChatGPT-local Python executable cannot inspect authentic Git ancestry. GitHub Actions issuer already demonstrated checkout and Python operational viability.

## Architecture preflight

1. Current owner: GitHub Actions control plane (`config/execution_ownership_contract.json`, `config/dossier_two_stage_interfaces_contract.json`, original shadow Stage B).
2. Authority: exact isolated task and original frozen issuer/auth/Stage B contract. Code does **not** alter their pinned semantics.
3. Semantic ChatGPT can create exactly one **typed** `{outcome,payload,supplemental_operations}` submission in a dedicated nonproduction Git branch through available GitHub `create_branch` and `create_file` connector operations; ChatGPT does not execute canonical inspect/build/verify or create candidates. GitHub Action owns all those Python steps and the only sandbox candidate commit.
4. No recurring schedule, new scope/queue selection, retries, alternate marker/issuer, canonical Dossier acceptance, production or Deep mutation. Original order and per-row independent invalid/missing behavior remain authoritative.

## Proposed complete handoff (inactive until separately reviewed and merged)

1. Install `.github/workflows/validate-dossier-shadow-18-github-python-handoff.yml` on **main**, not retroactively on historical sandbox.
2. Workflow `pull_request` validation: run synthetic Git fixtures with mocked semantics; then `actions/checkout@v4` full **original sandbox** checkout, verify marker HEAD and execute `scripts/dossier_shadow_18_assembly_stage_b.py::inspect` through pinned `scripts/dossier_shadow_18_github_python_handoff.py`. Store exact immutable diagnostics as GitHub Actions artifact. `inspect` is read-only; no actual Assembly semantic work.
3. Director may later explicitly invoke `workflow_dispatch(operation=inspect)` on main to regenerate immutable per-AppID readiness, without changing frozen branch.
4. Separately authorized future semantic operator reads only GitHub `ready` rows, works from exact submitted Research evidence, and uses GitHub connector `create_file` to create the exact `reviews/dossier_shadow_offline/handoff/dossier-shadow-calibration-20261011-6x3/<appid>.json` as a **single file** on branch `handoff/dossier-shadow-18-assembly-typed`, itself initially created with `create_branch`. File contains **only** the three semantic fields, no GitHub authority wrappers. This is one typed transport, not a new queue or new marker; creation alone never submits or accepts an Assembly candidate.
5. Director-approved operator manual `workflow_dispatch(operation=publish, appid, semantic_commit, explicit_confirmation)` is locked to main, original repository, first attempt and owner actor, with `contents: write` only for that job. The action fetches exact original Git submission and checks one-parent, one-added-file, original Git introducing SHA, original unchanged blob, original fixed order and `ready`. Canonical ORIGINAL Python `build_candidate` then delegates to existing async Assembly schema/source-first/privacy/strict V2 validators; only the exact `reviews/.../assembly/gXXXXXX/<appid>--<id>.json` path can be newly committed. BEFORE pushing, ORIGINAL `verify_candidate` proves real Git introduction/lineage/equality. Non-fast-forward push fails closed; no rebase, retry, overwrite, canonical writer or new approval marker.
6. The workflow and adapter cannot run from a historical sandbox `main` implementation tree: workflow code lives on main, but validation execution imports original Stage B and dependencies **from the sandbox checkout**, preserving the marker-era code and original immutable Git inputs.

## Rejection and privacy invariants

- Real two invalid QA packages must be judged by original canonical Research Python; synthetic tests verify two wrong-original-Git-origin records are rejected item-locally, and four missing records remain missing. *QA semantic deficiencies are not silently declared structurally invalid if the existing validator does not itself prove that result; any discrepancy must fail the Director's acceptance gate.*
- Invalid Research, candidate collision, wrong source/old year, extra transport field, rewritten semantic blob, tampered marker/buffer, production path, source privacy, non-exact V2 Dossier, wrong original order, and racing sandbox push are fail-closed.
- No Research or Assembly semantics executed by this worker. No existing sandbox files modified. No Published/Accepted dossiers or Deep readiness implied.

## Current verification / CI

- Existing original Stage B fixture: `scripts/test_dossier_shadow_18_assembly_stage_b.py`.
- Added focused tests: `scripts/test_dossier_shadow_18_github_python_handoff.py`.
- PR-only GitHub CI and immutable original read-only inspect: `.github/workflows/validate-dossier-shadow-18-github-python-handoff.yml`.
- **CI IDs and genuine per-AppID diagnostics must be recorded after the GitHub PR run.** Until then the proposal is NOT a claim that Assembly is unblocked.

## Safe Director next step

Review CI's genuine `frozen-shadow-18-python-inspect` artifact and validate the two known QA defects against canonical results. Accept the narrow PR only if the exact real 18-row Python inspect passes and security/typed transport are independently reviewed; do not launch semantic Assembly or repeat the issuer from this worker.
