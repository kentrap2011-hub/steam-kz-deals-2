# Progressive Deep PR #323 — Stage-1 CI blocker disposition 01

- Task: `progressive-deep-pr323-stage1-ci-blocker-disposition-01`; ЧАТ 5.
- Status: **FIX_READY_FOR_DIRECTOR_REVIEW** (subject to exact-head Actions verification; independent PR must be reviewed and merged by Director, never by this worker).
- Source of truth: `main` at branch creation `fcbbec1eacdc81cca88193283e97d49e294d1091`.
- Implementation branch: `fix/progressive-deep-stage1-ci-zero-normal-queue-01` (separate from open PR #323, whose code/branch is untouched).

## Root cause and evidence

- PR #323 HEAD `703e92428c02933bab615baa5db0d8384f6d61aa`: focused lexical and PASS2 runs 40673538888 / 40673538950 succeeded. The [Stage-1 CI run 40673538906](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40673538906) failed at `scripts/test_deep_stage1_migration_pr_preview.py:61`, demanding `len(fresh['items']) == scope['normal_pass2_eligible_count'] > 0`. Its Stage-1 unit check passed; preview check failed. PR #323 changes PASS1/PASS2 lexical validators, so the Stage-1 workflow runs under path filters, but its failing assertion and producer code are unchanged between that PR and `main`.
- Current `main` committed `data/production/pre_ai/progressive_pass2_work.json` states `projection_status=current_github_owned_fast_dossier_deep_v1_projection`, 641 current games, 45 first-pass attempted, 43 authoritative completed, two recovery-owned, **596 waiting for Dossier**, zero eligible `items` / `pass2_eligible_count`. This is committed snapshot evidence, **not** a claimed direct observation of the pure fresh recompute inside the failed CI run. The pure recompute assertion did not print the count before aborting.
- `config/progressive_pass2_contract.json` defines accepted Dossier readiness, authoritative completion, and recovery-owned exclusion; no guaranteed strictly positive current normal queue. `scripts/progressive_pass2.py::recompute_eligibility` permits waiting, completed, recovery-owned, and runnable identities; `scripts/build_progressive_pass2_work.py` emits the current scope as it exists. `config/deep_two_stage_migration_contract.json` remains `frozen_not_active` with `mass_migration_authorized=false`. Stage-1 migration preview reconciles the **full current bindings plus accepted one-stage Dossier**, not only normal runnable PASS2 items.
- The `> 0` test assertion was therefore an obsolete time-dependent premise, not a requirement of the canonical contract. It could turn a legitimate empty normal queue into a red CI gate, entirely independently of the lexical fix. No producer/source/semantic change is required.

## Minimal fix, safety and acceptance

- Replace the incorrect positive-queue premise with **strict recovery-aware Deep accounting**: exact generated list against normal eligible count; ready/pending matching actual list; recovery pending as subset; remaining first-pass work equal to Dossier waiting plus runnable non-recovery; current total equal to attempted plus unattempted remaining. Preserve existing generation, profile/Dossier identity rejection, stale committed-snapshot rejection, zero authorization, strict Stage-1 validation and byte-for-byte no-write checks.
- Add synthetic regression where two games already finished one-stage Deep and one is waiting for Dossier: **zero normal PASS2 items is legitimate**, while inactive Stage-1 migration preview still prepares exact two accepted-Dossier-bound candidates, does not materialize/execute, and preserves the waiting game.
- Ownership preflight: GitHub retains scope/order/provenance/validation/persistence, while semantic workers remain non-active for Stage 1. No queue/rerun/marker/scheduler/production/cutover/migration/recovery or ranking write; no commercial regex change. Only PR-read-only tests and this report.
- This separate PR's CI must be checked on its **exact HEAD**; success here does not by itself mark PR #323 green. After Director-approved integration, refresh or rerun the required check on PR #323's then-current head; do not merge the worker PR automatically.

## Required-check classification and director decision

- [GitHub API rulesets query](https://api.github.com/repos/kentrap2011-hub/steam-kz-deals-2/rulesets?includes_parents=true) returned `[]` to this connection. `GET /branches/main/protection` returned HTTP 403 `Resource not accessible by integration`. Therefore branch-protection required checks **cannot be confirmed**. PR `mergeable=true`/`unstable` does not establish that the red Stage-1 check is optional. Repo admin/Director should inspect effective required checks in GitHub UI before merging PR #323.
- Suggested decision: review/merge this dedicated minimal Stage-1 test-correction PR only after exact-head CI success, update PR #323 from the new `main` as appropriate and reverify Stage-1 and lexical checks at the new HEAD, then decide PR #323 independently. If CI is not green, retain blocked status and diagnose the next exact failure instead of bypassing it.

## Check disposition

- Existing pre-fix failing CI: 40673538906, isolated to Stage-1 preview nonempty invariant.
- No repository clone or local full-suite execution in this ChatGPT environment: outbound git DNS unavailable. Exact-head GitHub Actions is the authoritative execution check. No semantic execution was attempted.
- Existing cross-cutting guidance `KNOWN_WORKER_PITFALLS.md#PITFALL-005` already forbids pinning generic validation to a historical live snapshot; same failure mode applies to hardcoded nonempty queue assumptions. No separate policy change is necessary.
