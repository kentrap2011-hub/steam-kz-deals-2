# Progressive Deep Worker — bounded production runtime contract

This is the bounded semantic-worker contract for production authoritative Deep analysis under `FAST-DOSSIER-DEEP-V1`. Production execution is allowed only while the frozen invocation-start `config/progressive_pass2_contract.json#implemented` and `#active` are both true.

## Establish one immutable run-start view

At the start of every invocation, before any semantic execution:

1. Read the exact current `main` commit once as `observed_main_commit`. This initial read is only the proposed start state; it is not yet semantic authority.
2. Read `config/progressive_pass2_contract.json` and `data/production/pre_ai/progressive_pass2_work.json` from that exact commit. If Deep is inactive or no current items exist, stop cleanly without creating a run-start marker.
3. Generate one fresh lowercase 32-hex `run_start_nonce` and create exactly one file, with create-only semantics, at:
   `data/ai_inbox/progressive_pass2/run_starts/{observed_main_commit}--{run_start_nonce}.json`

   The file must contain exactly:
   - `schema_version: 1`
   - `contract: "PROGRESSIVE-PASS2-RUN-START-MARKER-V1"`
   - `observed_main_commit`
   - `run_start_nonce`

   Do not add a worker timestamp to this marker.
4. Record the Git commit created by that create-only marker as `run_start_anchor_commit`. Then wait only for the GitHub-owned confirmation receipt at:
   `data/cache/progressive_pass2_run_start_receipts/{run_start_anchor_commit}.json`
5. The receipt must have `contract: "PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1"` and `status: "confirmed"`. If it is absent, rejected, inconsistent, or cannot be read safely, stop this invocation before semantic execution. Do not create a second marker in the same invocation.
6. Take `run_start_authority_commit` and `run_started_at_utc` only from that confirmed GitHub receipt. Never substitute a time chosen by the semantic worker. GitHub defines the authority as the actual first parent of the create-only marker commit and the start time as that marker commit's Git committer time.
7. Read the contract and Deep work from exactly the confirmed `run_start_authority_commit`. Freeze the manifest's exact ordered items, work modes, immutable identities, top-level profile pin, Dossier path/SHA/compatibility/expiry bindings, and every recovery authorization id/reason/condition for the whole invocation. Never add work absent from this frozen view.
8. Verify every item pin equals the frozen top-level profile pin. Fetch `gaming_taste_live.json` only at the pin's exact immutable repository/path/commit, verify blob SHA, byte count and content SHA256 once, parse once, and use those exact profile bytes throughout the invocation.
9. At this single confirmed invocation boundary, validate each frozen item's exact Dossier from `run_start_authority_commit`: exact path, content SHA256, compatibility binding, app/work identity and expiry must be valid at the GitHub-confirmed `run_started_at_utc`. Recovery items must carry the exact GitHub-prepared recovery authorization fields. An item already stale/expired/unauthorized at this boundary is not executable and produces no artifact; continue to later frozen items.

After this one GitHub confirmation is established, do not reread or revalidate mutable `main`, manifest order, Dossier content/binding/expiry, live profile, recovery authorization projection, or GitHub progress between games. Any such change after the confirmed boundary belongs to the next invocation.

Deep eligibility is independent from Fast/PASS 1. Never require a Fast result, attempt, failure, or global Fast completion.

## Asynchronous traversal and transport

Traverse only executable items from the frozen run-start order while runtime/tool budget safely permits.

For each item:

- If its exact `result_submission_path` or exact `terminal_execution_submission_path` already exists, do not rerun it. This means only `already submitted; do not recreate`, never canonical acceptance or attempt consumption. Continue to the next frozen item.
- Otherwise execute semantic analysis using the frozen profile, semantic input and frozen Dossier evidence.
- Publish at most one create-only artifact: a valid `PROGRESSIVE-PASS2-RESULT-V1`, or only after an authorized semantic attempt actually started but no accepted result can be produced, a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1`.
- Echo all immutable work/Dossier/recovery fields exactly and additionally include the invocation-wide `run_start_anchor_commit`, GitHub-confirmed `run_start_authority_commit`, and GitHub-confirmed `run_started_at_utc`.
- After submitting A, do not wait for GitHub ingest, attempt advancement, manifest rebuild or sibling removal before starting B.
- Never revisit an item in the same invocation. If GitHub later rejects and removes an invalid transport, that does not authorize a same-invocation retry.

Never overwrite, rename, delete, or invent an alternate transport filename. A stale/similarly named path is not a marker for the current item.

## Semantic outcomes

A trustworthy fit may return `analyzed_fit`; a trustworthy completed negative may return `analyzed_not_fit`; unresolved evidence returns `analysis_incomplete`. Insufficient evidence is never a completed negative. Do not use price, discount, sale urgency, wishlist, purchase value or other commercial signals for the semantic judgment.

## Ownership boundary

GitHub alone owns Deep scope/order, one-time run-start confirmation, exact run-start acceptance proof, normal-first-pass accounting, recovery ownership/authorization, validation, canonical persistence, terminal receipts, future eligibility recomputation, completeness and producer projection. The worker never chooses retry eligibility or recovery scope.

Invalid technical transport consumes no semantic attempt. GitHub may persist its rejection receipt and remove the invalid active inbox candidate; only a later invocation's then-current GitHub run-start view can authorize another submission. The worker never turns a freed path into its own retry decision.

Do not modify Fast/PASS 1 state, Dossier state/workflows, Deep GitHub state/recovery authorization/accounting, visual projection, or Scheduled Task settings.
