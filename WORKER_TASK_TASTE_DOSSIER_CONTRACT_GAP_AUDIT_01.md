# WORKER TASK — Taste Dossier Contract Gap Audit 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-contract-gap-audit-01`
Mode: `READ / AUDIT / RECON`

## Goal
Systematically look for additional contract/schema/prompt/validator mismatches of the same general class as the recent live failures: states the worker can legally/predictably emit or publish even though they contradict another active rule, cannot be audited mechanically, or are only discovered after immutable publication.

This is a read-only audit. Do not implement fixes.

A separate worker is fixing the already-known live defects. This audit should find **new** gap classes, not duplicate the known ones.

## Baseline pinning
At task start, record the exact `main` commit SHA you are auditing as `audit_baseline_sha` and keep the substantive audit pinned to that revision even if `main` moves while this task is running.

If the parallel implementation lands before you start, audit the newer baseline. If it lands after you start, do not chase moving main; note that your report is pinned to the recorded baseline.

## Known defects — exclude from “new finding” count
Do not present these as newly discovered findings:

1. Missing pre-publication equivalence to canonical strict validation.
2. Username/display-name/author-profile/review-excerpt leakage through compact provenance.
3. Recovery of the currently blocked immutable invalid artifacts.
4. Aggregate Steam review totals being used as `mention_count`.
5. `?l=russian` / Russian Store UI being treated as Russian player feedback.
6. Recurrence not matching bound player-feedback evidence.
7. The already observed Hellish Quart current-state mismatch, DEEEER source-mix mismatch, and Sniper Elite 5 unbound Russian `found_and_used` mismatch.

You may use these as examples of the failure pattern, but the purpose is to find other classes that would survive after those are fixed.

## Read first / START gate
Follow `CHAT_PROTOCOL.md` START gate fully, then read at minimum:
- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- relevant `CURRENT_TASK.md` state;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md` for active Taste dossier/web-evidence decisions;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-02.md`;
- `reviews/worker_reports/taste-dossier-evidence-guard-batch3-implement-01.md`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-03.md`;
- active dossier worker prompt;
- active dossier schema;
- active web-evidence contract;
- strict validator;
- buffered/group validator/drain;
- worker group/manifest binding and freshness compatibility logic only as needed to test cross-field invariants.

Run architecture preflight before deeper audit.

## Audit method
Build a compact matrix of active requirements and where each is enforced:

- prompt only;
- schema only;
- strict validator;
- buffered/group validator;
- snapshot/freshness binding;
- canonical ingestion;
- not mechanically enforced.

Then search specifically for contradictions/gaps where:

- prompt requires something but schema/validator permits its opposite;
- schema permits two fields that cannot both be semantically true;
- validator checks counts/flags but not the relationship that gives them meaning;
- a source can be classified in a way that mechanically satisfies a stronger claim than its locator/evidence role warrants;
- temporal status can contradict source freshness/evidence role in a way not already covered;
- `research_state`, `overall_strength`, `source_mix_status`, `russian_attempt`, `stop_reason`, `conflicts`, identity/corroborators, observation categories/statuses, provenance source roles, feedback records, or freshness can form impossible/incoherent combinations;
- exact title/release/appid/version identity can be internally inconsistent while still passing;
- duplicate evidence can be represented under multiple IDs and thereby inflate recurrence/source diversity despite dedupe rules;
- one physical review/discussion item can be aliased through multiple URLs/source IDs/feedback IDs and counted more than once;
- the same player-feedback record can improperly support materially different claims without enough clause/source specificity;
- source pages that are indexes/search result pages/aggregates can masquerade as attributable individual feedback records;
- professional/editorial sources can accidentally satisfy player-feedback requirements;
- language and mixed-language classifications can falsely satisfy Russian-specific evidence;
- `current`, `historical`, `durable`, `uncertain` states can be internally inconsistent with summary/conflict semantics beyond the already-known Hellish example;
- source/public-reference/date combinations allow fabricated precision or non-auditable references;
- group-level validation can accept an artifact whose individual dossiers are valid but cross-group/snapshot invariants are contradictory;
- freshness/version binding can preserve incompatible evidence across contract/prompt/schema changes;
- a worker can continue to later groups after a semantically failed prior group even if publication is not yet canonical;
- fail-closed states can accidentally be interpreted downstream as positive/complete evidence.

Do not invent theoretical edge cases that cannot be emitted by the actual current worker shape. Favor gaps that are reachable under the active prompt/schema and demonstrate them with the smallest deterministic fixture or existing artifact shape.

## Depth requirement
For each candidate finding:

1. prove the active rule that should hold;
2. prove the current enforcement path that fails to guarantee it;
3. construct or identify the smallest schema-valid/worker-plausible counterexample;
4. determine whether current strict validation accepts or rejects it;
5. classify impact:
   - semantic false positive;
   - semantic false negative;
   - privacy/content-contract leak;
   - temporal misclassification;
   - identity mismatch;
   - evidence double-counting;
   - stale compatibility/freshness risk;
   - control-plane/recovery risk;
6. recommend the narrowest owner/layer for a future fix.

Do not assign subjective severity scores or rank findings. Separate proven reachable defects from speculative hardening ideas.

## Bounded scope
Audit only the Taste Steam review dossier subsystem and its direct binding/ingestion boundary.

Do not audit or change:
- downstream Taste-fit scoring;
- ranking/pricing/commercial rules;
- package edition-quality scoring;
- Scheduled Task UI/model selection;
- unrelated semantic producers;
- other repositories.

Do not run Scheduled Task `Run now`.
Do not publish dossier artifacts.
Do not mutate canonical queue/cache/progress/receipts.

## Output expectations
The report should distinguish three buckets:

- `proven_new_gap`: reachable contradiction accepted or insufficiently guarded by current machinery;
- `already_known_or_parallel_fix`: real but already covered by the parallel implementation task;
- `hardening_only`: plausible but no reachable counterexample proven.

For every `proven_new_gap`, include a minimal reproducible fixture/field combination in prose or compact JSON fragments, but do not store raw player review content.

If no additional proven gaps exist after a thorough audit, say so explicitly rather than manufacturing findings.

## Durable report
Publish to `main`:
`reviews/worker_reports/taste-dossier-contract-gap-audit-01.md`

Report must include:
- `audit_baseline_sha`;
- architecture preflight;
- enforcement matrix summary;
- all proven new gaps with exact active-rule and validator/contract evidence;
- minimal reachable counterexamples;
- known/parallel-fix items explicitly excluded from new finding count;
- hardening-only observations separately labeled;
- whether any proven gap can silently pass canonical ingestion;
- whether any proven gap can block immutable recovery/publication;
- exactly one next step.

Allowed final statuses:
- `complete_new_gaps_found`
- `complete_no_additional_proven_gaps`
- `blocked`

The next step should be a bounded IMPLEMENT task only if one or more `proven_new_gap` findings exist; otherwise the next step should be to proceed with live acceptance after the parallel known-defect implementation completes.

Ensure the durable report is in `main` before completion. Stop after report publication.