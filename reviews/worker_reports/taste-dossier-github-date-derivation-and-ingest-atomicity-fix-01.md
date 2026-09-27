# Taste Dossier GitHub-derived dates + ingest atomicity fix 01

## 1. Final status

`complete_ready_for_director_acceptance`

Task: `WORKER_TASK_TASTE_DOSSIER_GITHUB_DATE_DERIVATION_AND_INGEST_ATOMICITY_FIX_01.md`.

Implementation PR: #99, `worker/taste-dossier-github-date-ingest-atomicity-01` -> `main`.

Implementation validation head: `4001c581f28b6424cd35d6a5700b5769f8b0dda7`.

No production Dossier recovery, Tiny Snow rerun, stale g000001 reconciliation, Deep recovery, backlog processing, or Scheduled Task action was performed.

## 2. Architecture preflight

The task stays inside the existing ownership boundary:

- GitHub remains the control plane for deterministic transformations, temporal classification, strict validation, canonical persistence, failed-group quarantine, audit, recovery eligibility and completeness.
- Scheduled ChatGPT remains bounded semantic/evidence collection plus immutable create-only candidate transport.
- Moving temporal classification to GitHub removes semantic judgment from the worker rather than introducing a second validator.
- No scheduler, queue, retry loop, crawler, backlog manager, second canonical validator, or ChatGPT-owned prepublication gate was added.
- The canonical 365-day boundary remains unchanged.
- TASTE-012 current/historical completeness remains strict; TASTE-014 bounded retrieval, TASTE-015 coverage sufficiency, exact-product identity, privacy, pragmatic evidence modes and non-blocking per-group progress remain in force.

`python scripts/validate_execution_ownership.py` passed in the final implementation Dossier gate.

## 3. User-approved simplification

The worker now owns only factual temporal input:

- concrete `publication_date: YYYY-MM-DD` when actually known;
- `publication_date: null` when genuinely unknown;
- no age-in-days calculation;
- no worker choice of `recent`, `older`, or `unknown`.

GitHub owns the mechanical classification. This implements the user-approved simplification instead of adding another prompt-memory rule or a ChatGPT-side self-validation layer.

## 4. Previous temporal responsibility model

Previously the semantic worker supplied both publication dates and persisted `freshness`. The strict GitHub validator then checked that worker-authored freshness against the canonical 365-day rule.

That duplicated a deterministic responsibility across the semantic worker and GitHub. Tiny Snow demonstrated the failure mode: a candidate could contain temporal contradictions before create-only publication even though the canonical 365-day validator itself was correct.

The old model also allowed parent-source freshness to become an unnecessary intermediate representation for evidence whose actual support lived in child `player_feedback_records`.

## 5. New GitHub-derived date model

`scripts/taste_steam_review_dossier_strict.py` now derives temporal state deterministically:

- date known and age <= 365 days relative to dossier `generated_at_utc` date -> `recent`;
- date known and age > 365 days -> `older`;
- date unknown -> `unknown`.

Source-level `freshness` is no longer required worker input. If an older candidate still supplies a valid freshness token, strict validation canonicalizes/overwrites it from the factual source date. Canonical output can therefore retain the derived field for compatibility without treating it as worker authority.

For observation-level temporal qualification, GitHub uses the actual bound `player_feedback_record.publication_date`, not a guessed or inherited parent-page freshness value.

## 6. Candidate/schema/binding changes

The compatibility binding was changed explicitly so an old immutable candidate is not silently reinterpreted under the new semantics:

- schema revision: `github-derived-temporal-classification-2026-09-27`;
- evidence contract revision: `github-derived-temporal-classification-2026-09-27`;
- worker prompt revision: `web-evidence-v2-github-derived-temporal-classification-v1`;
- Dossier control contract revision: `nonblocking-per-group-progress-github-derived-temporal-2026-09-27`.

`freshness` was removed from required worker source fields while remaining an allowed canonical/compatibility field. The worker prompt now requires factual dates/null and explicitly forbids worker age classification.

Old accepted production Dossiers were not manually rewritten. Normal GitHub-owned projection/rebuild/refresh remains the compatibility mechanism.

## 7. Current-state temporal semantics

Current-state strictness was not weakened.

A `current` observation must have actual bound feedback whose source role is `current_state` and whose own feedback-record publication date GitHub derives as recent.

A `historical` observation must retain historical feedback and must also have actual bound recent dated current-state feedback for the present-state check.

A genuinely unknown feedback date derives to `unknown` and cannot satisfy a requirement for recent support. Current page accessibility never promotes unknown evidence to recent.

Mixed children under one source are classified independently from their own dates. A recent child can satisfy recent support; an old sibling remains old; an unknown sibling remains unknown.

Durable/historical evidence remains usable under the existing role semantics and was not globally rejected merely for being old.

## 8. Tiny Snow regression

Focused regression coverage uses Tiny Snow / appid `1002560` and the diagnostic failure shape:

- undated parent source + old dated supporting child -> current claim fails;
- undated parent source + recent dated supporting child -> current claim passes;
- the undated parent itself remains derived `unknown`;
- no parent accessibility/freshness laundering can turn the old child into recent.

This directly protects the root cause that triggered the task without rerunning Tiny Snow production.

## 9. Old staging failure

The diagnosed production workflow previously used:

`git add -A -- data/control data/quarantine data/audit 2>/dev/null || true`

In ingest run `36241650284`, `data/control` was absent. Git rejected the combined pathspec operation; `|| true` suppressed the failure. The intended failed-group audit modification and deterministic quarantine artifact therefore remained unstaged, and the subsequent rebase encountered a dirty worktree.

The failed-group classification itself had produced the intended audit/quarantine outputs; the defect was canonical Git staging atomicity.

## 10. New staging behavior

A real reusable helper was added: `scripts/stage_taste_dossier_canonical_writer.sh`.

In `stage` mode:

- mandatory canonical writer paths are checked and staged fail-closed;
- optional `data/control`, `data/quarantine`, and `data/audit` are handled independently;
- absence of one optional path does not suppress staging of another;
- unexpected Git/staging errors are not hidden.

The ingest workflow now invokes this helper instead of embedding the unsafe combined command.

Audit/quarantine remain intentional GitHub-owned canonical outputs committed atomically with corresponding progress/projection changes.

## 11. Clean-worktree proof

After the local canonical commit and before the existing fetch/rebase/push loop, the workflow executes:

`bash scripts/stage_taste_dossier_canonical_writer.sh assert-clean`

The helper checks exactly:

`git status --porcelain --untracked-files=all`

If any tracked or untracked path remains, it prints the exact porcelain output and exits non-zero before rebase. It does not stash, discard, auto-add unknown leftovers, or suppress the failure.

The focused temporary-Git regression proves both the clean success path and a dirty failure path containing the exact leftover `?? unexpected-leftover.txt`.

## 12. DATE regressions

`scripts/test_taste_dossier_github_date_derivation.py` covers the requested temporal cases:

- DATE-01: exactly 365 days old derives `recent`;
- DATE-02: 366 days old derives `older` and cannot satisfy a current claim;
- DATE-03: null date derives `unknown` and cannot satisfy recent support;
- DATE-04/05: Tiny Snow undated-parent old-child failure and recent-child success;
- DATE-06: mixed children under one source keep independent temporal states;
- DATE-07: unknown child does not satisfy current-state recent support;
- DATE-08: worker candidate is valid without choosing/serializing freshness;
- DATE-09: canonical strict output receives GitHub-derived source temporal state;
- DATE-10: historical TASTE-012 semantics require actual historical feedback plus a recent dated current-state check.

The final implementation Dossier gate executed the focused GitHub-derived temporal regression successfully.

## 13. Full validation results

Final implementation validation at head `4001c581f28b6424cd35d6a5700b5769f8b0dda7`:

- `Validate buffered Steam review dossier runtime` run `36312723478`: **success**.
  - compile: success;
  - execution ownership validation: success;
  - daily snapshot: success;
  - buffered submission: success;
  - same-day preservation: success;
  - strict recovery: success;
  - prepublication parity: success;
  - contract gaps: success;
  - language binding: success;
  - semantic consistency: success;
  - semantic bounded retrieval: success;
  - purpose/coverage sufficiency: success;
  - pragmatic observed evidence: success;
  - transient-author compatibility: success;
  - Steam Store review-card parent: success;
  - contract contradiction closeout: success;
  - identity provenance generation: success;
  - validator-generator parity: success;
  - package identity: success;
  - story DLC semantic scope: success;
  - parallel candidate validation/non-blocking per-group: success;
  - canonical-writer coalescing liveness: success;
  - GitHub-derived temporal classification regression: success;
  - canonical ingest atomic staging regression: success.
- `Validate Progressive PASS 2 core` run `36312723454`: **success**.
- `Validate backlog dispositions` run `36312723552`: **success**.

Earlier red PR runs were used as regression feedback while updating old anti-drift tests to follow the new staging helper and GitHub-derived temporal ownership. No failing check was bypassed or disabled.

## 14. Files changed

Implementation/runtime/contracts:

- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `.github/workflows/validate-taste-dossier-buffered.yml`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/stage_taste_dossier_canonical_writer.sh`
- `scripts/taste_steam_review_dossier_strict.py`

New focused regressions:

- `scripts/test_taste_dossier_github_date_derivation.py`
- `scripts/test_taste_dossier_ingest_atomic_staging.py`

Compatibility/anti-drift regressions updated:

- `scripts/test_progressive_pass2_integration.py`
- `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py`
- `scripts/test_taste_dossier_contract_contradictions_fix.py`
- `scripts/test_taste_dossier_identity_provenance_generation_fix.py`
- `scripts/test_taste_dossier_pragmatic_evidence_model.py`
- `scripts/test_taste_dossier_purpose_coverage_sufficiency.py`
- `scripts/test_taste_dossier_semantic_bounded_retrieval.py`
- `scripts/test_taste_dossier_validator_generator_parity_fix.py`
- `scripts/test_taste_steam_review_dossier_contract_gaps.py`
- `scripts/test_taste_steam_review_dossier_daily_snapshot.py`
- `scripts/test_taste_steam_review_dossier_parallel_validation.py`
- `scripts/test_taste_steam_review_dossier_prepublication.py`
- `scripts/test_taste_steam_review_dossier_semantic_consistency.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`

Durable/project state:

- `PROJECT_DECISIONS.md`
- `PROJECT_ROUTES.md`
- `CURRENT_TASK.md`
- this report.

No `data/...\` production file is part of PR #99.

## 15. Durable decisions/contracts changed

`PROJECT_DECISIONS.md` records TASTE-017: GitHub derives Dossier temporal state from factual publication dates and failed-group audit/quarantine must participate in atomic canonical staging with a clean-worktree proof before rebase/push.

`PROJECT_ROUTES.md` now names the real Dossier staging helper, focused DATE/staging regressions, bound-feedback temporal rule, atomic failed-group outputs and pre-rebase clean-worktree invariant.

`config/execution_ownership_contract.json` explicitly assigns deterministic recent/older/unknown derivation to GitHub and limits Scheduled ChatGPT to factual date/null input.

The Dossier contract/schema/evidence/prompt revisions change the semantic compatibility binding intentionally.

## 16. Production actions explicitly not performed

The implementation did **not**:

- run or edit any Scheduled Task;
- rerun Tiny Snow;
- rewrite the existing Tiny Snow candidate;
- manually edit accepted Dossier caches;
- reconcile/recover stale production g000001;
- authorize or execute Deep recovery;
- process backlog;
- hand-edit production audit/quarantine state.

Only source/contracts/tests/workflow/docs were changed. Any ordinary deterministic GitHub rebuild triggered by the eventual source merge is within the task's explicitly allowed control-plane behavior.

## 17. Unresolved

No implementation blocker remains.

The already-stale production g000001 / Tiny Snow state intentionally remains unresolved because this task explicitly excludes recovery/reconciliation. That is a separate post-acceptance Director decision.

## 18. Director recommendation

Accept the implementation if independent review confirms PR #99 and this report.

After acceptance, decide separately whether/how to reconcile the already-stale production g000001 state through the normal GitHub-owned recovery/reconciliation mechanism. Do not use an ad-hoc candidate rewrite, worker retry, or manual cache edit.
