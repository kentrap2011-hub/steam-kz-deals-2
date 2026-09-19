# Taste Dossier Temporal Pre-Stop Retrieval Gate Implement 01

## Summary

Status: `complete_ready_for_live_acceptance`.

The Scheduled Taste Steam Review Dossier worker now performs temporal completeness checking before it may declare `research_state:"sufficient"` / `stop_reason:"evidence_stable"` for current-state-sensitive observations. A draft `historical` technical observation without a bound recent `current_state` source must continue bounded exact-product retrieval while budget remains; if the temporal state is still unresolved after bounded research, the existing `uncertain` path is used instead of forcing `historical`.

Evidence semantics, the strict validator, privacy/provenance/language rules, early multi-source diversification, and the 8-search / 16-page ceilings were not weakened or expanded.

## Start Gate

The START gate was completed before task-specific implementation. The worker read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `CURRENT_TASK.md`, `PROJECT_ROUTES.md`, the task file `WORKER_TASK_TASTE_DOSSIER_TEMPORAL_PRESTOP_RETRIEVAL_GATE_IMPLEMENT_01.md`, relevant `PROJECT_DECISIONS.md` entries, `config/execution_ownership_contract.json`, and the relevant prior dossier diagnostic/implementation reports.

Only repository `kentrap2011-hub/steam-kz-deals-2` was used.

## Findings

The existing temporal evidence semantics were already correct: current technical claims require recent current-state support; historical/fixed technical claims require historical evidence plus a recent current-state check; unresolved temporal state has an existing `uncertain` representation.

The defect was ordering. The worker could decide that evidence was stable before checking whether a proposed current-state-sensitive `historical` observation had the recent current-state source already required by the contract. The strict validator correctly rejected that result later, but the retrieval opportunity had already been stopped.

## Accepted Root Cause

Accepted root cause: `recent_source_retrieval_miss`.

This task found no strict-validator gap requiring semantic relaxation or validator redesign.

## Architecture Preflight

GitHub remains the control plane and strict authority for scope, bindings, deterministic state, validation, progress, and recovery. The existing Scheduled ChatGPT worker remains the owner of bounded external retrieval and semantic synthesis.

The fix adds no scheduler, queue, recurring worker stage, daemon, fixed retry loop, fixed website quota, or new quota. Ownership boundaries remain unchanged.

## Pre-Stop Gate Design

The worker prompt now requires this ordering:

`collect evidence -> draft/plan observations -> temporal completeness check -> targeted recent retrieval if required -> re-evaluate temporal status -> only then decide sufficient/evidence_stable -> serialize candidate`

For current-state-sensitive topics such as bugs, performance, compatibility, technical state, localization, and regional/service state:

- proposed `historical` is not temporally complete until historical evidence and a bound `evidence_role:"current_state"` + `freshness:"recent"` source are both present;
- if recent support is missing and either search or page-read budget remains, bounded exact-product recent player-feedback retrieval continues;
- the worker cannot set `research_state:"sufficient"` or use `stop_reason:"evidence_stable"` while that required recent check is missing;
- after retrieval, the worker re-evaluates the observation as existing `historical`, `current`, or `uncertain` semantics require;
- unresolved state uses `uncertain`; old evidence alone is not enough to force `historical`;
- durable gameplay/story/art/music/structure traits are not subjected to this additional gate;
- hard bounds do not authorize fabrication of a historical resolution.

## Implementation

Merged implementation changes:

- `config/taste_steam_review_dossier_worker_prompt.md`: added the temporal pre-stop completeness gate and explicit stop ordering.
- `config/taste_steam_review_dossier_web_evidence_contract.json`: advanced only the worker prompt binding revision to `web-evidence-v2-temporal-prestop-retrieval-gate-v1`.
- `scripts/test_taste_steam_review_dossier_semantic_consistency.py`: added focused TEMPORAL-PRESTOP regressions.
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`: aligned the expected prompt-binding revision only.
- `scripts/test_taste_dossier_contract_contradictions_fix.py`: aligned the expected prompt-binding revision only.
- `PROJECT_DECISIONS.md`: recorded TASTE-012.
- `CURRENT_TASK.md`: tracked and now closes this work item.

PR #66 was squash-merged as commit `6b032457e5373402d55633ea0a39da7f036151d6`.

## Focused Regressions

TEMPORAL-PRESTOP-01..11 cover:

- no historical technical stop before the required recent check;
- continued bounded retrieval when recent support is missing and budget remains;
- unchanged historical/current/uncertain semantics;
- unchanged durable-trait handling;
- preservation of early source-agnostic multi-source diversification;
- no Steam-only lane, fixed website quota, or new retry loop;
- unchanged 8/16 production ceilings;
- unchanged strict rejection of historical/fixed technical claims without recent current-state support;
- unchanged privacy, provenance, and language guards;
- no product/app/source hardcoding in the generic worker prompt.

Two pre-existing regression tests contained literal expectations for the previous `worker_prompt_revision`; only those metadata expectations were advanced to the new binding revision.

## Live Proof — 60 Seconds! Reatomized

Live proof was performed for exact appid `1012880` without publishing a production candidate.

The pre-stop check treated the old technical evidence as temporally incomplete before allowing any `evidence_stable` decision. Targeted exact-product recent retrieval then reached the Steam Community support collection:

`https://steamcommunity.com/app/1012880/discussions/1/`

and the concrete exact-product support topic:

`https://steamcommunity.com/app/1012880/discussions/1/573795560006462989/`

The concrete topic is dated 16 July 2026 and reports a black screen on startup, which is within the existing <=365-day recent window on 19 September 2026. Therefore the recent current-state retrieval happened before a stop decision, as required.

This recent evidence does not automatically resolve every older technical sub-issue. It shows why the old composite cannot be mechanically retained as `historical`: current sub-issues must be represented under existing current semantics, while unresolved sub-issues/composites use `uncertain`.

## Budget Accounting

Live proof used:

- web searches: `2 / 8`;
- opened/read source pages: `2 / 16`.

No budget limit was increased.

## Activation

PR #66 merged to `main` as `6b032457e5373402d55633ea0a39da7f036151d6`.

That normal push triggered the GitHub-owned `Build pre-AI deterministic payload` workflow, run 141. It completed successfully and emitted activation commit `ca2904b770dc431efdc386279841aeb452b89bc1`.

No workflow was manually dispatched for activation.

The changed prompt binding intentionally invalidated compatibility with the previous dossier snapshot/work progress. Activation therefore occurred through the ordinary GitHub-owned deterministic backlog rebuild. No stale payload or stale work progress was manually rebound to the new contract.

## Active Snapshot

Active dossier snapshot after activation:

- snapshot: `bbb40469f96be618ec10fa7fc6b9edca8ccd56e8f2e73442529a47de76164902`;
- group count: `245`;
- canonical expected sequence: `1`;
- prepared/completed/remaining: `734 / 0 / 734`;
- full backlog complete: `false`;
- worker prompt revision: `web-evidence-v2-temporal-prestop-retrieval-gate-v1`;
- worker prompt SHA256: `78d491811cba9aa95ec2fe005bde1bc32482bd861503ac1885b716306c966fef`;
- evidence contract revision remains `contract-contradictions-fix-2026-09-18`.

The active `g000001` contains appids `1003890`, `1012880`, and `1018800`. A later unrelated `main` commit for the commercial visual payload did not change this active dossier snapshot or binding.

## Immutable State Verification

The old immutable candidate:

`593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26--g000002--bc1342223f730d0b4991f3e8d04e496cb8171fb6345db90938e946e7d6cbed89.json`

was not edited, repaired, replaced, or reissued.

During normal activation reconciliation Git recorded it as a rename from `data/ai_inbox/taste_steam_review_dossiers/` to:

`data/quarantine/taste_steam_review_dossier_inbox/stale/593378be74141105830ebe7f1fb94d8942f7427bc1abb7f05430b6bfccc69a26/`

with `0 additions / 0 deletions / 0 changes`. The artifact bytes therefore remained unchanged while the incompatible stale snapshot was quarantined.

## Validation

PR validation completed successfully after stale revision-expectation metadata was aligned. The green dossier suite covered compile checks, execution ownership, daily snapshot regression, buffered submission, strict recovery, semantic consistency, Steam review robustness, language/provenance, weak-positive counterexamples, Store-card scarcity, pre-publication, contract contradictions, strict package behavior, story-DLC handling, and parallel buffering.

The normal GitHub-owned activation workflow run 141 also completed successfully through deterministic backlog preparation, inbox reconciliation, fixed-daily snapshot checks, strict backlog projection, provenance/determinism/idempotence checks, atomic payload emission, and post-commit smoke validation.

Live retrieval additionally proved the new pre-stop behavior on exact appid `1012880` within the existing budget.

## Strict Validator Status

The strict validator was not weakened or redesigned. Its implementation remained unchanged through this fix, and it continues to reject historical/fixed technical claims that lack the required recent current-state check.

## Evidence Semantics Status

Evidence meanings are unchanged:

- `current` remains current;
- `historical` still requires the existing historical + recent-current-state conditions for current-state-sensitive claims;
- `durable` remains available for stable traits;
- `uncertain` remains the correct path for unresolved temporal state;
- the existing <=365-day recency rule is unchanged.

The task changes retrieval/stopping order, not evidence truth conditions.

## Privacy / Provenance / Language Guard Status

Privacy, author-independence, provenance, exact-language binding, and source-admissibility guards were not changed. Their regression coverage remained green.

## Diversification Regression Check

The active early multi-source diversification strategy is preserved. Targeted recent retrieval remains source-agnostic, may use a cheap usable exact-product player-feedback path when exposed, and diversifies after unusable stop-shapes.

No Steam-only retrieval lane, named-site quota, or new retry loop was introduced.

## Production Publication Status

No production candidate was published by this task.

The old immutable `g000002` was not re-published or replaced.

## Scheduled Task Status

Scheduled Task `Run now` was not invoked.

No Scheduled Task schedule or settings were changed by this task.

## Files Changed

Implementation/decision files changed by the task:

- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `scripts/test_taste_steam_review_dossier_semantic_consistency.py`
- `scripts/test_taste_steam_review_dossier_strict_recovery.py`
- `scripts/test_taste_dossier_contract_contradictions_fix.py`
- `PROJECT_DECISIONS.md`
- `CURRENT_TASK.md`
- this durable report

The normal GitHub-owned activation workflow separately regenerated deterministic dossier backlog/snapshot state for the new binding. Strict validator and dossier schema semantics were not changed.

## Final Status

`complete_ready_for_live_acceptance`

## Recommended Next Step

Return to Director for one clean production live acceptance against active snapshot `bbb40469f96be618ec10fa7fc6b9edca8ccd56e8f2e73442529a47de76164902` starting from expected `g000001` under the new binding; do not reuse or migrate stale `g000002`.
