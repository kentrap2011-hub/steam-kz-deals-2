# Progressive Deep Worker — bounded production runtime contract

This is the bounded semantic-worker contract for production authoritative Deep analysis under `FAST-DOSSIER-DEEP-V1`. Production execution is allowed only while the frozen invocation-start `config/progressive_pass2_contract.json#implemented` and `#active` are both true.

## Establish one immutable run-start view

At the start of every invocation, before semantic execution:

1. Resolve the exact current `main` commit once and record it as `run_start_authority_commit`.
2. Record the invocation boundary UTC time as `run_started_at_utc`.
3. Read `config/progressive_pass2_contract.json` and `data/production/pre_ai/progressive_pass2_work.json` from exactly `run_start_authority_commit`. If `implemented != true` or `active != true`, stop cleanly.
4. Freeze the manifest's exact ordered items, work modes, immutable identities, top-level profile pin, Dossier path/SHA/compatibility/expiry bindings, and every recovery authorization id/reason/condition for the whole invocation. Never add work absent from this frozen view.
5. Verify every item pin equals the frozen top-level profile pin. Fetch `gaming_taste_live.json` only at the pin's exact immutable repository/path/commit, verify blob SHA, byte count and content SHA256 once, parse once, and use those exact profile bytes throughout the invocation.
6. At this invocation boundary, validate each frozen item's exact Dossier from `run_start_authority_commit`: exact path, content SHA256, compatibility binding, app/work identity and expiry must be valid at `run_started_at_utc`. Recovery items must carry the exact GitHub-prepared recovery authorization fields. An item already stale/expired/unauthorized at this boundary is not executable and produces no artifact; continue to later frozen items.

After this boundary is established, do not reread or revalidate mutable `main`, manifest order, Dossier content/binding/expiry, live profile, recovery authorization projection, or GitHub progress between games. Any such change after invocation start belongs to the next invocation.

Deep eligibility is independent from Fast/PASS 1. Never require a Fast result, attempt, failure, or global Fast completion.

## Asynchronous traversal and transport

Traverse only executable items from the frozen run-start order while runtime/tool budget safely permits.

For each item:

- If its exact `result_submission_path` or exact `terminal_execution_submission_path` already exists, do not rerun it. This means only `already submitted; do not recreate`, never canonical acceptance or attempt consumption. Continue to the next frozen item.
- Otherwise execute semantic analysis using the frozen profile, semantic input and frozen Dossier evidence.
- Publish at most one create-only artifact: a valid `PROGRESSIVE-PASS2-RESULT-V1`, or only after an authorized semantic attempt actually started but no accepted result can be produced, a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1`.
- Echo all immutable work/Dossier/recovery fields exactly and additionally include the invocation-wide `run_start_authority_commit` and `run_started_at_utc`.
- After submitting A, do not wait for GitHub ingest, attempt advancement, manifest rebuild or sibling removal before starting B.
- Never revisit an item in the same invocation. If GitHub later rejects and removes an invalid transport, that does not authorize a same-invocation retry.

Never overwrite, rename, delete, or invent an alternate transport filename. A stale/similarly named path is not a marker for the current item.

## Semantic outcomes

A trustworthy fit may return `analyzed_fit`; a trustworthy completed negative may return `analyzed_not_fit`; unresolved evidence returns `analysis_incomplete`. Insufficient evidence is never a completed negative. Do not use price, discount, sale urgency, wishlist, purchase value or other commercial signals for the semantic judgment.

## Ownership boundary

GitHub alone owns Deep scope/order, exact run-start acceptance proof, normal-first-pass accounting, recovery ownership/authorization, validation, canonical persistence, terminal receipts, future eligibility recomputation, completeness and producer projection. The worker never chooses retry eligibility or recovery scope.

Invalid technical transport consumes no semantic attempt. GitHub may persist its rejection receipt and remove the invalid active inbox candidate; only a later invocation's then-current GitHub run-start view can authorize another submission. The worker never turns a freed path into its own retry decision.

Do not modify Fast/PASS 1 state, Dossier state/workflows, Deep GitHub state/recovery authorization/accounting, visual projection, or Scheduled Task settings.
