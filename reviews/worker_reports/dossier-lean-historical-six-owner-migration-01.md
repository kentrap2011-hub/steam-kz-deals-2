# Historical six Lean Dossier — exact owner migration source report

Task ID: `dossier-lean-historical-six-owner-migration-01`  
Worker: NEW physical ЧАТ 2  
Repo / base: `kentrap2011-hub/steam-kz-deals-2` / `main`  
Source PR: [#497](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/497), branch `fix/dossier-lean-historical-six-owner-migration-20261126`  
**Source-only: never merged or dispatched by this worker; zero live accepted in frozen sandbox.**

## Authority, immutable provenance and exact scope

- New permission provenance: following source PR #494 merge (main `b481cf9a7432602fbc4e611967f1bbc7cd0c39b8`) and the director explanation that historical six were still **0/6**, the owner explicitly said **«Разрешаю»** for exact old six only. This is not authorization for a fresh trial, semantic Research/Assembly, production, Deep, repeated manual GitHub operations, or general/indefinite retries.
- Trial: `dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4`.
- Frozen sandbox: `refs/heads/sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4` at **`d1b9a9e78dcde879a03370682ade4969763fd9d1`**; directly read back GitHub ref unchanged.
- Original claim control ref: `refs/heads/dossier-lean-auto-attempts/cdcdb4951e2fc98336729af75b954da4` at **`6df354d024b0e3104ee408e815a1e5d141fb8e84`**; directly read back unchanged. Claim is on that ref, **not main**; never delete, force-update, or replay it.
- Claim document on original immutable claim SHA: `data/control/dossier_notes_v2/auto_writer_attempts/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4.json`. Binding: marker `b267882dd3d056a1fc18d6a3fb75380ac38bd9cd`, original source main `4ccf23005166a1ae3c35800e1b38e0c295e29d8e`, owner source run `45243093290`, failed automatic run `45628656098`, attempt 1, immutable pairs SHA256 **`6bfadc047557d514ab3e4ee2de2f7959c686958891fe7300bee0f24eb0d9c14f`**.
- That SHA256 was recomputed as `sha256(json.dumps(exact_pairs(), ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))` over the six original Research + Assembly commit pairs from `config/dossier_notes_v2_isolated_lean_acceptance.json`, matching claim exactly.
- Exact AppIDs `1000010, 102600, 1029690, 49520, 499180, 501590`: all six original frozen **typed Assembly receipts** exist and have `phase=assembly`, `disposition=strict_item_valid_pending_existing_atomic_group_ingest`, `canonical_acceptance=false`, and the original immutable receipt blob SHAs. No sandbox accepted store/receipt directories exist (0+0, not 6+6).
- Original GitHub Actions run [#45628656098](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45628656098): completed **failure**, owner `kentrap2011-hub`, main source SHA matches claim. Most recent relevant owner push [#45740018123](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45740018123): completed **success**, but its result was `historical_spent_claim_awaits_scoped_owner_migration`, `writer_launched=false`. Both runs are historical evidence, not jobs to rerun.

## Architecture preflight and exact source change

1. Owner: GitHub and GitHub Actions under `config/execution_ownership_contract.json`; current interactive chat is source developer/operator only.
2. Authority: existing `config/dossier_lean_writer_auto_ready_v1.json#retry_lifecycle` historical migration route and owner's new exact permission, with original `config/dossier_notes_v2_isolated_lean_acceptance.json` strict immutable binding.
3. No transfer of queue, lease, retry, completeness, writer, or persistence from GitHub into ChatGPT. Existing trusted `main` auto-ready workflow and original shared writer only.
4. No new schedule, recurring job, arbitrary queue, trial selection, retry loop, or production path.

In `config/dossier_lean_writer_auto_ready_v1.json` change **only** historical migration fields: `historical_live_retry_authorized=false -> true`, `historical_migration_grant=null -> exact six-field object` (`trial_id`, `old_claim_sha`, `old_failed_auto_run_id`, `original_sandbox_head`, `immutable_pair_digest`, `owner_decision`). All source IDs/hash proofs are exact. No global opt-in flags, manual strict writer, canonical Lean/Deep toggles or TTL/year/source map changed.

**Truthful QA correction:** existing `scripts/dossier_lean_writer_auto_ready.py::policy` demanded a literal `owner_decision=explicit_new_exact_trial_recovery_after_L3_review`, incorrectly implying an L3 occurred for PR #494, while that review had an explicit owner waiver. Replaced that exact literal with **`explicit_owner_approved_exact_six_recovery_2026_11_26`**; this is ONLY a claim of exact owner permission, **not** an L3 certification. The previous narrow PR activation QA waiver is not a blanket waiver for this source PR. An independent L3/security QA of this *new authorization/source correction* must be completed or explicitly newly waived before Director merge.

Added `scripts/test_dossier_lean_writer_auto_ready.py` active-grant assertions and adversarial negatives for changed trial, spent claim, old run, frozen sandbox, digest, forged L3 decision, disabled-live-with-grant and enabled-live-with-null-grant. Existing strict writer/real disposable six+six suites remain untouched. No external semantic or runtime jobs were executed during source work.

## Trigger and gates

- Existing `.github/workflows/dossier-lean-writer-auto-ready.yml` listens to owner push to `main` changing existing `config/dossier_lean_writer_auto_ready_v1.json` (also specified owner source files). It uses reviewed `main`, shared `taste-steam-review-dossier-canonical-writer` concurrency lock, and never takes sandbox workflow source. Script `require_activation_git_change` independently verifies authentic main `before/after` ancestor commits and changed existing permitted Git object blob. An ordinary unrelated push or added-only policy file cannot authorize migration.
- Once Director reviews **exact final source PR HEAD**, all mandatory checks and independent QA (or new explicit waiver), Director may merge once. This **merge is a separate Director action**, not a worker dispatch or live-success proof.
- After merge: verify the **new** authenticated owner push Actions run ID (never rerun #45540222575, #45591943959, #45603534459 or #45628656098), append-only attempt journal (historical attempt 2 then max total 3), max 30-minute lease and minimum 2-minute backoff, no same-source retry, unchanged original claim/sandbox source authority, exact remote sandbox committed 6 Lean docs + 6 accepted receipts, no duplicates/collisions. If the workflow is blocked, report actual reason; never silently force the control ref.
- **Not evidence of actual six+six:** source PR merge, local tests, GitHub CI, policy `true`, and prior successful but no-op owner run.
- Main state at branch creation: `aefb48dcdebc5ed7c8fa2378e38298ab377facd6`. Source PR final HEAD and required check run IDs must be recorded after the report/any handoff commits; neither CI PASS nor L3 is presumed before observed.

## Worker handoff

**Status at report creation: `BLOCKED_CI_PENDING_INDEPENDENT_L3`.** Draft [PR #497](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/497) is ready for source verification but **not for unreviewed merge**, and actual historical Lean acceptance remains **0/6**. Director should check exact final HEAD required CI, obtain independent L3 on this new authorization delta (or a *new* explicit waiver), then decide merge. Only then observe the GitHub-owned auto event and remote 6+6 result; no further manual GitHub action from the user is required.
