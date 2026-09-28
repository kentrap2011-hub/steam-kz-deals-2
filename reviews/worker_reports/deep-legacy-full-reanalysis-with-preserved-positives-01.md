# Deep legacy full reanalysis with preserved positives 01

## Task

Task ID: `deep-legacy-full-reanalysis-with-preserved-positives-01`.

Implement a finite one-off GitHub-owned migration for CURRENT authoritative old-contract Deep results that still project `legacy_not_evaluated`, while preserving accepted positive evidence, fully evaluating frozen negative/mixed Dossier evidence under PPD-009, retaining the old Deep revision as audit history, leaving Dossier independent, and leaving Scheduled Task configuration unchanged.

This worker chat implemented and validated the control path only. It did not author production per-game semantic conclusions.

## Architecture preflight

Preflight proved that the previous PASS 2 runtime could not safely express this migration as either `normal_first_pass` or `recovery`:

- `normal_first_pass` would incorrectly consume/rewrite first-pass accounting for already completed Deep identities;
- `recovery` would falsely reinterpret completed authoritative results as recovery-owned work;
- mutating the old result in place would destroy audit history;
- a second semantic scheduler/worker would violate execution ownership.

The selected architecture keeps GitHub as control plane and the existing Progressive Deep Worker as the only semantic data plane. A bounded third work mode, `legacy_full_reanalysis`, is used only for the finite manifest. No scheduler, retry daemon, queue owner, backlog manager, ranking weight, or penalty code was added.

## Canonical migration decision

Added `PROJECT_DECISIONS.md#PPD-010` before runtime changes.

PPD-010 defines:

- migration ID `deep-legacy-full-reanalysis-with-preserved-positives-01`;
- fixed GitHub-owned scope and immutable migration authority;
- exact preserved positive/baseline evidence rules;
- frozen Dossier authority and run-start publication guard;
- separate migration accounting;
- completed revision promotion + old revision history;
- incomplete migration fallback to prior completed Deep truth;
- no migration rediscovery after terminal completion;
- no Dossier or Scheduled Task ownership change.

The PASS 2 contract is version 11 and explicitly models separate migration attempt/history/accounting semantics.

## Frozen scope

Migration authority:

`97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a`

Frozen at:

`2026-09-28T04:01:33Z`

Manifest:

`data/control/progressive_pass2_legacy_full_reanalysis_manifest.json`

Frozen scope:

- total targets: **30**;
- prior `analyzed_fit`: **26**;
- prior `analyzed_not_fit`: **4**;
- stale older-generation legacy rows excluded: **2**;
- current new-format PPD-009 rows excluded by construction;
- incomplete/recovery-owned rows excluded by construction.

All 30 target Dossier byte SHA-256 values were independently recomputed against the migration authority and matched their accepted Deep bindings before the manifest was prepared.

## Positive-evidence reuse

For old `analyzed_fit` targets:

- the exact accepted `positive_evidence` array is embedded in immutable migration provenance;
- a migrated `analyzed_fit` result is rejected with zero attempt if it adds, rewrites, removes, or replaces that array;
- the worker prompt explicitly forbids fresh positive web/Dossier research;
- positive projection retains migration provenance back to the prior accepted Deep authorization.

For old `analyzed_not_fit` targets:

- the accepted old not-fit evidence is retained as the existing unfavorable/decision baseline;
- the migration cannot fabricate absent positive evidence merely to force a fit;
- if evidence cannot support a responsible completed conclusion, `analysis_incomplete` is allowed without displacing the old authoritative result.

## Frozen Dossier evidence

Each target binds:

- exact Dossier path;
- exact Git blob/content SHA-256;
- exact web-evidence compatibility binding;
- generated/expiry timestamps;
- migration authority commit.

`validate_run_start_authority` keeps the existing PASS 2 V2 run-start publication guard but, for `legacy_full_reanalysis`, reads semantic Dossier bytes from the migration authority and evaluates them at the frozen migration time.

Regression coverage creates a two-commit synthetic repository where a later commit changes the Dossier and proves that the migration still consumes the earlier frozen Dossier SHA rather than the later bytes.

## Changes

Implemented:

- `PROJECT_DECISIONS.md` — PPD-010;
- `PROJECT_ROUTES.md` — canonical migration route;
- `config/progressive_pass2_contract.json` — migration contract/accounting/observability;
- `config/progressive_personalization_contract.json` — current-vs-history revision semantics;
- `config/progressive_pass2_result_schema.json` — migration result identity/provenance;
- `config/progressive_pass2_execution_receipt_schema.json` — migration terminal receipt identity/provenance;
- `config/progressive_pass2_worker_prompt.md` — bounded worker semantics, preserved-positive rule, frozen-Dossier rule;
- `scripts/progressive_pass2.py` — manifest validation, migration authorization/work, frozen run-start evidence, evidence guards, result validation, revision history, terminal fallback, metrics;
- `scripts/build_progressive_pass2_work.py` — finite migration projection using the existing Deep work manifest;
- `scripts/ingest_progressive_pass2.py` — exact confirmed run-start required and no mutable-Dossier fallback for migration;
- `scripts/progressive_personalization.py` — separate migration observability;
- `data/control/progressive_pass2_legacy_full_reanalysis_manifest.json` — immutable 30-target manifest;
- `data/production/pre_ai/progressive_pass2_work.json` — prepared 30-item migration work;
- `scripts/test_deep_legacy_full_reanalysis.py` — focused PPD-010 regression;
- `.github/workflows/validate-progressive-pass2-core.yml` — full-history checkout + migration regression;
- `scripts/test_progressive_pass2.py` — normal-vs-migration projection invariants.

No Dossier semantic/prompt/recovery/schedule file and no Scheduled Task setting was changed.

## Dossier parallelism proof

Dossier remains an independent neutral evidence stage.

The migration:

- does not pause Dossier;
- does not edit Dossier prompt, state, recovery, queue, or schedule;
- uses the already accepted Dossier bytes frozen at the migration authority;
- treats later Dossier writes as later repository truth and does not substitute them into this migration;
- preserves the existing shared canonical-writer serialization;
- does not require whole-`main` stability after the migration evidence authority;
- preserves the existing V2 run-start confirmation before any semantic artifact may be published.

The regression proving later-Dossier non-substitution passed in the final CI run.

## Execution state

Control-plane implementation is complete and migration work is durably prepared.

Current prepared migration state on `main` after PR #109 merge:

- total: **30**;
- pending: **30**;
- submitted: **0**;
- accepted: **0**;
- accepted completed: **0**;
- changed fit outcome: **0**;
- unchanged fit outcome: **0**;
- incomplete/unresolved: **0**;
- confirmed risk: **0**;
- caution: **0**;
- completed no relevant negative: **0**;
- complete: **false**.

Normal Deep work remains separately accounted; after the post-merge deterministic rebuild the current production projection records **38** ordinary ready/pending items and pauses their emission without consuming/reordering their normal/recovery attempts while the finite migration is active. The increase from the earlier branch snapshot reflects later independent Dossier/pre-AI progress; it does not alter the fixed 30-target migration scope.

PR #109 is merged into `main`. The external Progressive Deep Worker has not yet naturally consumed the migration: canonical state remains 30 pending / 0 submitted / 0 accepted. This chat did not trigger, reschedule, modify, or impersonate semantic execution.

## Validation

Final validated implementation commit:

`08c1753cedbd0a99674933b3057ed496dd46bed6`

GitHub Actions:

- PR validation: `Validate Progressive PASS 2 core` run **294**, run ID **36378520359** — **success**;
- PR validation: `Validate backlog dispositions` run **1339**, run ID **36378520358** — **success**;
- post-merge `Validate Progressive PASS 2 core` run **295**, run ID **36406259940** — **success**;
- post-merge `Validate backlog dispositions` run **1340**, run ID **36406259846** — **success**;
- post-merge `Build pre-AI deterministic payload` run **216**, run ID **36406259871** — **success**;
- post-merge `Build daily visual payload` run **824**, run ID **36406323648** — **success**;
- post-merge `Deploy visual mailing` run **864**, run ID **36406389623** — **success**.

Within the final PR PASS 2 core run 294, all relevant steps passed, including:

- Compile PASS 2 Python;
- Progressive async traversal + invalid transport regression;
- Deep parallel frozen-start regression;
- PASS 2 core regression;
- PASS 2 Dossier integration regression;
- Deep balanced negative assessment regression;
- **Deep legacy full reanalysis regression**;
- PASS 2 canonical-writer staging regression;
- PASS 1 regressions;
- Progressive personalization regression;
- Current staged projection accounting;
- unresolved/visual/UI provenance regressions;
- active production eligibility recomputation without consuming attempts.

The dedicated PPD-010 regression verifies all material task invariants, including:

1. exact current old-contract scope only;
2. stale/new-format exclusions;
3. exact preserved positives and no fresh-positive invention;
4. exact frozen Dossier bytes;
5. later Dossier non-substitution;
6. grounded synthetic `fit -> not_fit` acceptance;
7. fit retained with caution/risk;
8. fit-level/confidence/taste-factor revision;
9. complete old revision history;
10. completed migration promotion;
11. incomplete migration fallback;
12. existing risk-code-only scoring;
13. caution with no risk penalty;
14. complete negative-candidate evaluation requirement;
15. normal/recovery attempt accounting unchanged;
16. invalid transport zero-effect/fail-closed;
17. finite terminal no-rediscovery behavior.

One earlier CI run, PASS 2 core run **286** / ID **36378193436**, failed only because `deepcopy` was referenced without importing it in the new observability code. The import was added; subsequent run 288 passed, the final PR run 294 passed, and the post-merge run 295 also passed.

## Published result

No production per-game migration result has been published yet.

This is intentional and required by the semantic execution boundary: PR #109 is now merged and the 30-item migration is current GitHub truth, but only the existing canonical Progressive Deep Worker may create the semantic reanalysis results. At the post-merge check it had not yet naturally started this migration.

The ordinary post-merge visual pipeline completed successfully, but no migration-specific card/ranking change is claimed because there is still no accepted migration semantic result.

## Changed outcomes

No production outcome changes are claimed because semantic execution has not yet occurred.

The regression proves the control path permits an old fit result to become not-fit when grounded negative evidence supports that and separately permits fit level/confidence/taste factors/risk/caution state to change while exact old positive evidence remains preserved.

Operator observability includes both:

- `changed_fit_outcome_count` / `unchanged_fit_outcome_count` — strictly verdict changes;
- `changed_result_count` / `unchanged_result_count` — broader semantic revision diagnostics.

## Remaining / unresolved

Remaining semantic work on current `main`: **30 migration targets**; current migration state is **30 pending / 0 submitted / 0 accepted**.

There is no known implementation defect after final CI.

End-to-end persistence/card/ranking/Pages validation is intentionally not executed yet because no canonical external semantic migration result exists. Per the task boundary, this report does not claim the games were re-evaluated.

## Status

`complete_ready_for_director_acceptance`

The control path, contracts, immutable scope, prepared work, audit history, observability, Dossier parallelism, merge, and post-merge rebuild/validation are complete. Production semantic execution remains correctly owned by the existing Progressive Deep Worker and has not yet naturally consumed the prepared migration.

## Recommended next step

**Let the existing Progressive Deep Worker consume the prepared migration on its next natural invocation, then validate canonical persistence; do not manually trigger or change its Scheduled Task.**

## Exact PR/commit/run/artifact/migration refs

- repository: `kentrap2011-hub/steam-kz-deals-2`;
- base/source of truth: `main`;
- PR: **#109** — `Add one-off legacy Deep full reanalysis migration` — **merged**;
- implementation branch: `worker/deep-legacy-full-reanalysis-01`;
- merge commit: `5219062702be4b9f07e075bfd704bc6d50caf90c`;
- post-merge verified `main`: `949cfc7883e55bc8746d309c5e76ed6e0ec3fb73`;
- validated code head: `08c1753cedbd0a99674933b3057ed496dd46bed6`;
- migration authority: `97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a`;
- migration ID: `deep-legacy-full-reanalysis-with-preserved-positives-01`;
- migration manifest: `data/control/progressive_pass2_legacy_full_reanalysis_manifest.json`;
- canonical prepared work: `data/production/pre_ai/progressive_pass2_work.json`;
- canonical Deep state: `data/cache/progressive_pass2_state.json`;
- worker prompt: `config/progressive_pass2_worker_prompt.md`;
- decision: `PROJECT_DECISIONS.md#PPD-010`;
- result transport: `data/ai_inbox/progressive_pass2/results/`;
- terminal transport: `data/ai_inbox/progressive_pass2/execution_receipts/`;
- run-start markers: `data/ai_inbox/progressive_pass2/run_starts/`;
- run-start receipts: `data/cache/progressive_pass2_run_start_receipts/`;
- final PR PASS 2 CI run: **294**, ID `36378520359`, success;
- final PR backlog validation: **1339**, ID `36378520358`, success;
- post-merge PASS 2: **295**, ID `36406259940`, success;
- post-merge backlog validation: **1340**, ID `36406259846`, success;
- post-merge pre-AI build: **216**, ID `36406259871`, success;
- post-merge visual build: **824**, ID `36406323648`, success;
- post-merge deploy: **864**, ID `36406389623`, success;
- diagnostic failed run fixed during implementation: PASS 2 run **286**, ID `36378193436`.

## Efficiency / reusable lesson

This task took longer than a small patch for three concrete reasons: the migration required a contract-first architecture change rather than reusing recovery incorrectly; all 30 frozen Dossiers had to be byte-verified at one immutable authority; and GitHub CI exposed one missing import before final validation. The GitHub connector also limited large parallel file reads, so Dossier verification was deliberately batched without changing scope/authority.

Reusable improvement: for future finite semantic migrations, define a generic GitHub-owned revision-migration envelope up front — fixed manifest, prior-revision snapshot, immutable evidence authority, distinct attempt history, current-result promotion rule, and separate observability. That prevents repeatedly adapting normal-first-pass/recovery semantics and makes frozen-scope migrations smaller and easier to validate.
