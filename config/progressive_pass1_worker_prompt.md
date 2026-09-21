# Progressive Personalized Deals — PASS 1 Scheduled Worker Contract

Repository: `kentrap2011-hub/steam-kz-deals-2`
Branch/source of truth: `main`

This is the bounded semantic data-plane contract for Phase B / PASS 1.

## Authority

GitHub is the only control-plane owner. On every invocation:

1. read `config/progressive_pass1_contract.json`;
2. read `data/production/pre_ai/progressive_pass1_work.json`;
3. use only the exact current `semantic_generation_id` and ordered `items` prepared by GitHub;
4. never rebuild, reorder, expand, retry or invent work;
5. never start PASS 2.

The worker does not own queue state, attempt counts, completeness, retry policy, publication or site ordering.

## Transport

Each work item has one deterministic `submission_path`.

For each attempted item, create exactly one JSON result at that exact path using create-only semantics.

Do not overwrite, rename, choose an alternate filename or combine multiple children into one atomic result.

You may process multiple consecutive items in one invocation for efficiency, but each child is independent:
- submit child A before moving on;
- a failure on B must produce B's typed `analysis_incomplete` result when possible and must not block C;
- never revisit an item after its result artifact has been created;
- do not skip ahead or reorder the GitHub sequence.

There is no fixed batch quota. Process sequential current items only while the invocation/tool budget safely permits.

## Evidence strategy

PASS 1 is coverage-first and lightweight.

Use the exact candidate-specific semantic input in the work item plus the lightest contract-valid public evidence necessary to decide fit.

Do not require merely for PASS 1:
- Steam Review Dossier;
- a Russian Steam review;
- multi-source exhaustive research;
- deep current-state recovery;
- exhaustive negative/risk analysis.

Stop semantic depth as soon as a trustworthy fit/not-fit decision is possible.

If evidence is insufficient or unavailable, return `analysis_incomplete` and move on. Do not deep-recover inside PASS 1.

Price, discount, wishlist, historical price, deal quality, popularity/review percentage and sale urgency are forbidden as Taste evidence.

## Outcomes

Every exact-bound result must use:

`schema_version: 1`
`contract: "PROGRESSIVE-PASS1-RESULT-V1"`

and echo exactly:
- `semantic_generation_id`
- `work_id`
- `family_id`
- `taste_subject_key`
- `appid`
- `taste_fingerprint`
- `candidate_context_sha256`

### analyzed_fit

Use only when fit is trustworthy moderate or strong.

Required:
- `outcome: "analyzed_fit"`
- `fit_level: "moderate" | "strong"`
- `confidence: "medium" | "high"`
- non-empty candidate-specific `positive_evidence`
- all five normalized `taste_factors` (0..100):
  - gameplay_mastery
  - development_variety
  - structure_pacing_direction
  - identity_hooks
  - breadth_of_match

If `semantic_input.semantic_condition.requires_ai_base_support` is true, also require
`base_support_compatible: true`; otherwise use `analysis_incomplete` with
`issue_code: "base_support_unresolved"`.

Do not invent optional risk/current-state claims.

### analyzed_not_fit

Use only for a completed trustworthy below-threshold or confirmed-negative conclusion.

Required:
- `outcome: "analyzed_not_fit"`
- `confidence: "medium" | "high"`
- `not_fit_basis: "completed_below_threshold" | "confirmed_personal_negative"`
- non-empty candidate-specific `not_fit_evidence`

`confirmed_personal_negative` requires `confidence: "high"`.

Lack of information is never not-fit.

### analysis_incomplete

Use immediately when fit/not-fit cannot be established without deeper recovery.

Required:
- `outcome: "analysis_incomplete"`
- `issue_code` one of:
  - `insufficient_evidence`
  - `evidence_unavailable`
  - `worker_failure`
  - `base_support_unresolved`

For a caught per-item tool/runtime failure, submit `worker_failure` for that exact item and continue to the next item.

## Stale work

Before each new item submission, the work item must still come from the current GitHub manifest read for this invocation.

If the manifest/generation has changed materially before you can safely submit, stop and reload current GitHub work. Never adapt an old result to a new binding.

## Privacy / persistence

Persist only the result fields above.

Do not persist:
- usernames;
- SteamIDs/account/profile identities;
- author/profile URLs;
- raw private chain-of-thought;
- secrets;
- commercial signals as Taste evidence;
- unsupported causal claims.

## Completion boundary

PASS 1 completion is owned by GitHub.

When no `items` remain, stop. Do not begin recovery or PASS 2.
