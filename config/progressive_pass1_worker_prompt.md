# Progressive Personalized Deals — PASS 1 Scheduled Worker Contract

Repository: `kentrap2011-hub/steam-kz-deals-2`
Branch/source of truth: `main`

This is the bounded semantic data-plane contract for Phase B / PASS 1.

## Invocation-start authority

GitHub is the only control-plane owner. At the start of every invocation:

1. Resolve the exact current `main` revision once.
2. Read `config/progressive_pass1_contract.json` and `data/production/pre_ai/progressive_pass1_work.json` from that exact revision.
3. Freeze that manifest's exact `semantic_generation_id`, top-level `profile_pin`, and ordered `items` for this invocation. Do not reload/reselect the manifest between items.
4. Require every item `profile_pin_sha256` to equal the frozen top-level `profile_pin.pin_sha256`.
5. Read `gaming_taste_live.json` only through the frozen pin's exact repository/path at `resolved_commit_sha` (never mutable `main` and never remembered profile context), verify Git blob SHA, byte count and content SHA256, parse it once, and use those exact pinned bytes throughout the invocation.
6. If the exact pinned profile cannot be fetched or verified, fail closed without creating a result.
7. Never rebuild, reorder, expand, retry or invent work. Never start PASS 2.

The worker does not own queue state, attempt counts, completeness, retry policy, publication or site ordering.

## Asynchronous item traversal

Traverse only the frozen invocation-start `items`, in their exact GitHub order, while runtime/tool budget safely permits.

For each item:

- Check only its exact deterministic `submission_path`.
- If that exact path already exists, interpret it only as `already submitted; do not recreate`; do not infer acceptance, attempt consumption, fit/not-fit, canonical progress, or manifest advancement. Continue to the next frozen item.
- A stale, similarly named, wrong-generation or wrong-path artifact is never a submitted marker for the current item.
- If the exact path is absent, execute the item and create exactly one result at that path with create-only semantics.
- After creating A, do not wait for GitHub to ingest A, increment counts, remove A, or rebuild/advance the manifest before starting B.
- A caught per-item failure should produce that item's typed `analysis_incomplete` result when possible and must not block unrelated later frozen items.
- Visit each frozen item at most once in this invocation. If GitHub later removes a rejected transport path, do not loop back and retry it in the same invocation.

There is no fixed batch quota. Transport existence never means canonical acceptance; GitHub alone owns acceptance and attempt state.

## Evidence strategy

PASS 1 is coverage-first and lightweight. Use the exact candidate-specific semantic input plus the lightest contract-valid public evidence necessary to decide fit. Do not require merely for PASS 1 a Steam Review Dossier, Russian Steam review, exhaustive multi-source research, or deep recovery. Stop semantic depth as soon as a trustworthy fit/not-fit decision is possible.

If evidence is insufficient or unavailable, return `analysis_incomplete` and continue. Price, discount, wishlist, historical price, deal quality, popularity/review percentage and sale urgency are forbidden as Taste evidence.

## Outcomes

Every result uses `schema_version: 1`, `contract: "PROGRESSIVE-PASS1-RESULT-V1"` and exactly echoes `semantic_generation_id`, `profile_pin_sha256`, `work_id`, `family_id`, `taste_subject_key`, `appid`, `taste_fingerprint`, and `candidate_context_sha256`.

### analyzed_fit

Use only for trustworthy moderate/strong fit. Require `fit_level`, `confidence` (`medium|high`), non-empty candidate-specific `positive_evidence`, and all five normalized `taste_factors`. If base support is required but unresolved, use `analysis_incomplete/base_support_unresolved`.

### analyzed_not_fit

Use only for a completed trustworthy below-threshold or confirmed-negative conclusion. Require `confidence`, `not_fit_basis`, and non-empty candidate-specific `not_fit_evidence`. Lack of information is never not-fit.

### analysis_incomplete

Use when fit/not-fit cannot be established without deeper recovery. `issue_code` is one of `insufficient_evidence`, `evidence_unavailable`, `worker_failure`, `base_support_unresolved`. Exact malformed current Fast transport retains the repository's existing one-shot terminal-incomplete policy; this task does not create a Fast retry path.

## Privacy / persistence

Persist only contract result fields. Do not persist usernames, SteamIDs/account/profile identities, author/profile URLs, private chain-of-thought, secrets, commercial signals as Taste evidence, or unsupported causal claims.

## Completion boundary

PASS 1 completion is GitHub-owned. When the frozen invocation-start item list has been traversed or runtime/tool budget cannot safely start another item, stop. Do not begin recovery or PASS 2.
