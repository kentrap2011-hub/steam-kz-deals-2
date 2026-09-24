# Progressive Deep Worker — bounded production runtime contract

This is the bounded semantic-worker contract for production authoritative Deep analysis under `FAST-DOSSIER-DEEP-V1`. Production execution is allowed only while the exact observed invocation-start `config/progressive_pass2_contract.json#implemented` and `#active` are both true.

## Establish one immutable observed view and run-start marker

At the start of every invocation:

1. Read the exact current `main` commit once as `observed_main_commit`.
2. Read `config/progressive_pass2_contract.json` and `data/production/pre_ai/progressive_pass2_work.json` from exactly `observed_main_commit`. If Deep is inactive or no current items exist, stop cleanly without creating a run-start marker.
3. Freeze the manifest's exact ordered items, work modes, immutable identities, top-level profile pin, Dossier path/SHA/compatibility/expiry bindings, and every recovery authorization id/reason/condition from exactly that observed immutable commit. Never add work absent from this frozen view.
4. Verify every item pin equals the frozen top-level profile pin. Fetch `gaming_taste_live.json` only at the pin's exact immutable repository/path/commit, verify blob SHA, byte count and content SHA256 once, parse once, and use those exact profile bytes throughout the invocation. Never switch to mutable/latest profile state.
5. Generate one fresh lowercase 32-hex `run_start_nonce` and create exactly one file, with create-only semantics, at:
   `data/ai_inbox/progressive_pass2/run_starts/{observed_main_commit}--{run_start_nonce}.json`

   The file must contain exactly:
   - `schema_version: 1`
   - `contract: "PROGRESSIVE-PASS2-RUN-START-MARKER-V1"`
   - `observed_main_commit`
   - `run_start_nonce`

   Do not add a worker timestamp to this marker.
6. Record the Git commit created by that create-only marker as `run_start_anchor_commit`. Do not create a second marker in the same invocation.

The marker MUST exist before semantic execution begins.

## Provisional semantic execution before GitHub confirmation

After the marker exists, semantic analysis MAY begin immediately, but only provisionally and only against the exact frozen `observed_main_commit` view from steps 1–4.

- Do not reread mutable `main`, the manifest, Dossier state, recovery authorization, live profile or GitHub progress to refresh the provisional view.
- Provisional semantic work has no canonical effect, consumes no semantic attempt by itself, and MUST NOT be serialized or published as a result or terminal execution receipt before confirmation.
- Deep eligibility remains independent from Fast/PASS 1. Never require a Fast result, attempt, failure or global Fast completion.
- Exact Dossier bytes/identity/binding may be examined provisionally from the frozen observed view, but the trusted freshness boundary is not known until GitHub confirms the marker. Final publication eligibility must therefore use the GitHub-confirmed `run_started_at_utc` against those same frozen bytes.

## Mandatory publication gate

Before publishing the FIRST Deep result or terminal execution receipt from this invocation, obtain the GitHub-owned receipt at:

`data/cache/progressive_pass2_run_start_receipts/{run_start_anchor_commit}.json`

The receipt must:

- have `contract: "PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1"`;
- have `status: "confirmed"`;
- reference the exact `run_start_anchor_commit`;
- carry the exact marker path and `run_start_nonce` lineage;
- have `run_start_authority_commit == observed_main_commit`;
- supply `run_started_at_utc` from the marker commit's Git committer time.

Never substitute a time chosen by the semantic worker.

If the receipt is `rejected`, inconsistent, unsafe, confirms a different authority, or otherwise fails the exact lineage/authority checks:

- discard all provisional semantic work from this invocation;
- publish no Deep result;
- publish no Deep terminal execution receipt;
- consume no semantic attempt;
- stop the invocation;
- do not create a second marker.

If the receipt is merely absent when the first provisional semantic outcome becomes ready, use only this bounded wait/recheck sequence while runtime/tool budget safely permits:

1. read once immediately;
2. if absent, wait about 5 seconds and read once more;
3. if still absent, wait about 10 additional seconds and read once more;
4. if still absent, publish nothing and stop.

This is at most three receipt reads after the first outcome becomes ready and at most about 15 seconds of additional waiting. Do not convert it into an unbounded polling loop, retry daemon, queue manager, or repeated marker creation. Receipt absence never authorizes publication.

After a confirmed receipt is obtained, validate each frozen item's exact Dossier from `observed_main_commit` using the trusted `run_started_at_utc`: exact path, content SHA256, compatibility binding, app/work identity and expiry must be valid at that confirmed boundary. Recovery items must carry the exact GitHub-prepared recovery authorization fields. An item invalid at that trusted boundary produces no artifact; continue to later frozen items.

Once this one receipt is confirmed and bound to the exact observed authority, do not reread or revalidate mutable `main`, manifest order, Dossier content/binding/expiry, live profile, recovery authorization projection or GitHub progress between games. Any such change after the confirmed boundary belongs to the next invocation.

## Asynchronous traversal and transport

Traverse only executable items from the frozen observed/confirmed order while runtime/tool budget safely permits.

For each item:

- If its exact `result_submission_path` or exact `terminal_execution_submission_path` already exists, do not rerun it. This means only `already submitted; do not recreate`, never canonical acceptance or attempt consumption. Continue to the next frozen item.
- Otherwise execute semantic analysis using the frozen profile, semantic input and frozen Dossier evidence. The first item's analysis may already have been computed provisionally before confirmation.
- Publish at most one create-only artifact: a valid `PROGRESSIVE-PASS2-RESULT-V1`, or only after an authorized semantic attempt actually started but no accepted result can be produced, a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1`.
- Echo all immutable work/Dossier/recovery fields exactly and additionally include the invocation-wide `run_start_anchor_commit`, GitHub-confirmed `run_start_authority_commit`, and GitHub-confirmed `run_started_at_utc`.
- After submitting A, do not wait for GitHub ingest, attempt advancement, manifest rebuild or sibling removal before starting B.
- Never revisit an item in the same invocation. If GitHub later rejects and removes an invalid transport, that does not authorize a same-invocation retry.

Never overwrite, rename, delete, or invent an alternate transport filename. A stale/similarly named path is not a marker for the current item.

## Semantic outcomes

A trustworthy fit may return `analyzed_fit`; a trustworthy completed negative may return `analyzed_not_fit`; unresolved evidence returns `analysis_incomplete`. Insufficient evidence is never a completed negative. Do not use price, discount, sale urgency, wishlist, purchase value or other commercial signals for the semantic judgment.

## Ownership boundary

GitHub alone owns Deep scope/order, run-start confirmation truth, exact run-start acceptance proof, normal-first-pass accounting, recovery ownership/authorization, validation, canonical persistence, terminal receipts, future eligibility recomputation, completeness and producer projection. The worker never chooses retry eligibility or recovery scope.

The run-start confirmation is an anti-race publication guard. Semantic computation before confirmation is speculative only; no semantic artifact may cross the GitHub boundary before the exact confirmation is durable.

Invalid technical transport consumes no semantic attempt. GitHub may persist its rejection receipt and remove the invalid active inbox candidate; only a later invocation's then-current GitHub run-start view can authorize another submission. The worker never turns a freed path into its own retry decision.

Do not modify Fast/PASS 1 state, Dossier state/workflows, Deep GitHub state/recovery authorization/accounting, visual projection, or Scheduled Task settings.
