# WORKER TASK — Taste Dossier Semantic Consistency Gap Audit 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-semantic-consistency-gap-audit-01`
Mode: `READ / VALIDATE`

## Goal

Independently audit the active Taste dossier generation contract/prompt/schema/validator for other semantic self-consistency failures similar in spirit to the live `g000002` Blacksad defect.

This task is read-only except for its final durable report. Do not implement fixes.

The known Blacksad defect is already assigned to a separate implementation worker. Do not duplicate that implementation work. Use it only as the motivating example of the class of failure to search for.

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully. Read the minimum relevant canonical material, including:

- `CHAT_CONTEXT.md`;
- `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md`;
- `config/execution_ownership_contract.json`;
- active Taste dossier contract/schema/web-evidence contract/worker prompt;
- strict canonical validator and parallel-buffer validator/status logic;
- `reviews/worker_reports/taste-dossier-contract-gap-audit-01.md`;
- `reviews/worker_reports/taste-dossier-contract-gaps-implement-01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-validation-implement-01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-02.md`.

Pin the audit baseline to the current `main` commit at task start and report that SHA. If another worker changes `main` during this audit, do not silently mix baselines; note the pinned baseline and, only if cheap, re-check whether a proven gap still exists on the newer main before finalizing.

Run architecture preflight before conclusions.

## Scope of audit

Look specifically for mismatches where the worker can produce internally contradictory or semantically unsupported fields that either:

A. pass strict validation and could contaminate canonical data; or
B. are reliably rejected by strict validation but are still plausible under the worker prompt/contract, causing avoidable production stalls like the Blacksad case.

Prioritize A over B.

Audit at least these consistency families without assuming they are broken:

- observation/conflict language summaries versus bound feedback-record languages;
- `russian_attempt` versus actual used RU/mixed feedback;
- `source_mix` versus actually bound/used source records;
- `mention_count` / recurrence strength versus distinct bound player-feedback identities;
- observation/conflict `source_ids` versus `player_feedback_ids` parent-source relationships;
- freshness/current-state claims versus publication dates and source age;
- current/historical/durable/uncertain status versus the evidence actually bound;
- player-feedback versus official/professional/context-only source type;
- item-level public refs versus list/search/index/aggregate surfaces;
- physical feedback aliasing / duplicated sources through equivalent locators;
- compact-provenance privacy/content rules versus prompt examples/instructions;
- conflicts versus observations using inconsistent semantics for the same underlying evidence;
- dossier-level summary/overall claims that may outrun the strongest supported observation/conflict;
- any other duplicated/free-form derived field where one field can contradict the authoritative bound records.

Also inspect whether prompt/schema examples or wording can reasonably cause the worker to violate an already-existing validator rule even when the validator itself is correct. Treat that as a generation-contract gap, distinct from an acceptance gap.

## Proof standard

Do not report speculative concerns as proven gaps.

For each reported gap, provide a minimal deterministic counterexample or exact reachable shape and classify it as one of:

- `acceptance_gap`: strict validator currently permits bad/inconsistent data;
- `generation_contract_gap`: strict validator rejects it, but active prompt/contract plausibly permits or encourages the bad shape;
- `hardening_only`: not currently reachable under active prompt/contract, but worth noting separately.

For `acceptance_gap`, prove that the current canonical strict path accepts the counterexample or lacks the necessary check.

For `generation_contract_gap`, prove both:

1. the active worker instructions do not clearly prevent the shape; and
2. the strict validator rejects it or the live system has already demonstrated it.

Do not count the already-known Blacksad language mismatch itself as a new finding unless you identify a broader distinct rule beyond the known defect.

## Existing protections that must not be re-reported as new without new evidence

The following were already intentionally implemented and should be treated as known controls unless you prove a distinct remaining hole:

- expired dossier rejection;
- physical feedback/source alias normalization;
- rejection of review-list/search/index/vague refs as counted feedback items;
- 365-day recent/older coherence;
- bidirectional Russian-attempt consistency;
- feedback-bound conflict recurrence;
- content-complete compatibility binding;
- compact provenance identity/profile/content guard;
- aggregate Steam counts not creating mention_count;
- Russian-rendered store page not counting as player feedback;
- contiguous-prefix canonical acceptance;
- parallel buffering behind an invalid group.

## Live candidate review

As bounded supporting evidence, inspect the recent live current-snapshot candidate shapes from `g000002` and `g000003` only if still available or reconstructable from Git history. Use them to look for additional consistency issues, but do not turn this into broad production artifact mining.

Do not inspect unrelated historical repositories or unbounded artifact history.

## No implementation

Do not edit prompt, schema, validator, workflow, routes, runtime or candidates. Do not run Scheduled Task. Do not create test production artifacts.

You may run existing tests or bounded local validation experiments needed to prove a gap, provided they do not mutate canonical state.

## Final report

Publish to:

`reviews/worker_reports/taste-dossier-semantic-consistency-gap-audit-01.md`

Allowed final statuses:
- `complete_no_new_proven_gaps`
- `complete_new_gaps_found`
- `blocked`

The report must include:

- pinned baseline SHA;
- architecture preflight;
- audit method and bounded scope;
- explicit exclusion of the already-known Blacksad defect from the new-gap count;
- a table of each proven new gap with classification (`acceptance_gap` / `generation_contract_gap` / `hardening_only`), exact reachable shape, why current controls do or do not catch it, impact, and smallest recommended response;
- explicit list of audited consistency families with `protected` / `gap found` / `not provable` result;
- whether any live `g000003` content exposed an additional issue;
- whether any prompt/schema wording is materially out of sync with strict validator behavior;
- no implementation changes made;
- exactly one next step.

If new proven gaps exist, the next step should be a bounded implementation task after Director review, not automatic fixing in this chat.

If no new proven gaps exist, next step should be Director review followed by live acceptance after the separate known-defect fix lands.

Ensure the durable report is in `main` before completion. Stop after report publication.