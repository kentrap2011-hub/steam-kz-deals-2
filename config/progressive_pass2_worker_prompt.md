# Progressive Deep Worker — bounded production runtime contract

This is the bounded semantic-worker contract for production authoritative Deep analysis under `FAST-DOSSIER-DEEP-V1`. Production execution is allowed only while the exact observed invocation-start `config/progressive_pass2_contract.json#implemented` and `#active` are both true.

## Establish one GitHub-selected immutable run-start view

At the start of every invocation:

1. As an advisory preflight only, read the current `main` PASS 2 contract/work. If Deep is inactive or there are no current items, stop cleanly without creating a marker. This preflight commit is NOT the invocation authority and MUST NOT be used for semantic work.
2. Generate one fresh lowercase 32-hex `run_start_nonce` and create exactly one file, with create-only semantics, at:
   `data/ai_inbox/progressive_pass2/run_starts/{run_start_nonce}.json`

   The file must contain exactly:
   - `schema_version: 2`
   - `contract: "PROGRESSIVE-PASS2-RUN-START-MARKER-V2"`
   - `run_start_nonce`

   V2 deliberately contains no authority commit, no contract/work blob identity and no worker timestamp. The semantic worker is not allowed to choose any of those.
3. Record the Git commit created by that marker as `run_start_anchor_commit`. Read that commit's actual single Git parent as `run_start_authority_commit`. This parent, selected by GitHub when the marker was committed, is the exact immutable invocation authority. Do not create a second marker.
4. Read `config/progressive_pass2_contract.json` and `data/production/pre_ai/progressive_pass2_work.json` from exactly `run_start_authority_commit`. Record the exact Git blob SHA of each file. If Deep is inactive or the authoritative work view contains no items, do no semantic work and publish no semantic artifact.
5. Freeze the authoritative manifest's exact ordered items, work modes, immutable identities, top-level profile pin, Dossier path/SHA/compatibility/expiry bindings, exact result/terminal paths, every recovery authorization id/reason/condition, and every legacy-migration provenance field from exactly `run_start_authority_commit`. Never add work absent from this frozen view.
6. Verify every item pin equals the frozen top-level profile pin. Fetch `gaming_taste_live.json` only at the pin's exact immutable repository/path/commit, verify blob SHA, byte count and content SHA256 once, parse once, and use those exact profile bytes throughout the invocation. Never switch to mutable/latest profile state.

The marker MUST exist before authoritative freezing and semantic execution begin. If Dossier or another writer advances `main` before the marker commit, that newer state is naturally included in the marker parent and therefore in this invocation. If `main` advances after the marker commit, that later state belongs only to the next invocation.

## Provisional semantic execution before GitHub confirmation

After the marker exists and the exact marker-parent authority has been read/frozen, semantic analysis MAY begin immediately, but only provisionally and only against that exact immutable `run_start_authority_commit` view.

- Do not reread mutable `main`, the manifest, Dossier state, recovery authorization, live profile or GitHub progress to refresh or replace the marker-parent frozen view.
- Provisional semantic work has no canonical effect, consumes no semantic attempt by itself, and MUST NOT be serialized or published as a result or terminal execution receipt before confirmation.
- Deep eligibility remains independent from Fast/PASS 1. Never require a Fast result, attempt, failure or global Fast completion.
- For ordinary/recovery work, exact Dossier bytes/identity/binding may be examined provisionally from the frozen observed view, but the trusted freshness boundary is not known until GitHub confirms the marker. For `legacy_full_reanalysis`, use only the exact Dossier bytes at `migration_provenance.migration_authority_commit` and assess their validity at `migration_provenance.migration_frozen_at_utc`; never substitute the later run-start Dossier. Final publication still requires the GitHub-confirmed run-start receipt.

## Mandatory publication gate

Before publishing the FIRST Deep result or terminal execution receipt from this invocation, obtain the GitHub-owned receipt at:

`data/cache/progressive_pass2_run_start_receipts/{run_start_anchor_commit}.json`

The receipt must:

- have `contract: "PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1"`;
- have `status: "confirmed"`;
- reference the exact `run_start_anchor_commit`;
- carry the exact marker path and `run_start_nonce` lineage;
- have `marker_contract: "PROGRESSIVE-PASS2-RUN-START-MARKER-V2"`;
- have `run_start_authority_commit == run_start_marker_parent_commit`, exactly equal to the actual parent of `run_start_anchor_commit`;
- echo the exact GitHub-computed `progressive_pass2_contract_blob_sha` and `progressive_pass2_work_blob_sha` from that parent, matching the files already frozen by the worker;
- supply `run_started_at_utc` from the marker commit's Git committer time.

Never substitute a time chosen by the semantic worker.

If the receipt is `rejected`, inconsistent, unsafe, confirms any authority other than the marker parent, reports different contract/work blob identities, or otherwise fails the exact lineage/authority checks:

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

After a confirmed receipt is obtained, validate each ordinary/recovery item's exact Dossier from `run_start_authority_commit` using the trusted `run_started_at_utc`: exact path, content SHA256, compatibility binding, app/work identity and expiry must be valid at that confirmed boundary. Recovery items must carry the exact GitHub-prepared recovery authorization fields. For `legacy_full_reanalysis`, validate the exact Dossier from `migration_provenance.migration_authority_commit`, prove that authority is an ancestor of the run-start authority, verify its exact SHA/binding/app identity, and evaluate its generated/expiry validity at `migration_frozen_at_utc`. A migration item must never use a newer Dossier even when one exists. An item invalid at its applicable trusted boundary produces no artifact; continue to later frozen items.

Once this one receipt is confirmed and bound to the exact marker-parent frozen authority, do not reread or revalidate mutable `main`, manifest order, Dossier content/binding/expiry, live profile, recovery authorization projection or GitHub progress between games. Any state that lands after the marker commit belongs to the next invocation and must never be substituted into this one.

## Asynchronous traversal and transport

Traverse only executable items from the frozen marker-parent/confirmed order while runtime/tool budget safely permits.

For each item:

- If its exact `result_submission_path` or exact `terminal_execution_submission_path` already exists, do not rerun it. This means only `already submitted; do not recreate`, never canonical acceptance or attempt consumption. Continue to the next frozen item.
- Otherwise execute semantic analysis using the frozen profile, semantic input and frozen Dossier evidence. The first item's analysis may already have been computed provisionally before confirmation.
- Publish at most one create-only artifact: a valid `PROGRESSIVE-PASS2-RESULT-V1`, or only after an authorized semantic attempt actually started but no accepted result can be produced, a `PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1`.
- Echo all immutable work/Dossier/recovery/migration fields exactly, including `migration_provenance` when present, and additionally include the invocation-wide `run_start_anchor_commit`, GitHub-confirmed `run_start_authority_commit`, and GitHub-confirmed `run_started_at_utc`.
- After submitting A, do not wait for GitHub ingest, attempt advancement, manifest rebuild or sibling removal before starting B.
- Never revisit an item in the same invocation. If GitHub later rejects and removes an invalid transport, that does not authorize a same-invocation retry.

Never overwrite, rename, delete, or invent an alternate transport filename. A stale/similarly named path is not a marker for the current item.

## Semantic outcomes

A trustworthy fit may return `analyzed_fit`; a trustworthy completed negative may return `analyzed_not_fit`; unresolved overall fit evidence returns `analysis_incomplete`. Insufficient overall fit evidence is never a completed negative. Do not use price, discount, sale urgency, wishlist, purchase value or other commercial signals for the semantic judgment.

### Mandatory balanced negative assessment for every completed Deep result

For every new `analyzed_fit` or `analyzed_not_fit` result, inspect the frozen accepted Dossier **both for favorable evidence and for every negative/mixed observation plus every conflict**. Return `negative_assessment` in the exact result schema.

The assessment is separate from the overall fit verdict:

- `negative_assessment.status = "completed"` only after every candidate negative/mixed observation and every conflict in the exact accepted Dossier has been evaluated. Echo all of those candidate references in `evaluated_candidate_refs`, using only the exact `{"kind":"observation","index":N}` / `{"kind":"conflict","index":N}` references from the frozen Dossier. A completed assessment may have zero surfaced findings, but only after this full explicit evaluation.
- `negative_assessment.status = "unresolved"` when material negative/mixed evidence exists but cannot be responsibly classified as a personalized risk, display-only caution, or not personally relevant. Echo the candidate references actually evaluated and emit no findings. Unresolved never means “no risk”.
- Never emit `legacy_not_evaluated`; that value is GitHub-owned compatibility projection for historical accepted Deep state that predates this contract.

Each surfaced finding must be exactly one of:

1. `confirmed_personal_risk`: the frozen Dossier evidence supports a candidate-specific personal risk under the bound profile. It MUST use one existing canonical `risk_code` allowed by the result schema. Do not invent a new risk code, weight, penalty or score. The existing GitHub risk policy alone decides any score effect.
2. `caution`: the frozen Dossier evidence supports a useful trade-off or friction worth showing, but it is not sufficiently established as a score-affecting personal risk. Its `risk_code` MUST be `null`. A caution is display-only unless a separate pre-existing practical/risk rule independently applies.

Every finding must carry non-empty Russian user-facing `text_ru` and at least one exact Dossier `evidence_refs` reference. Do not turn every public complaint into a personal risk. Do not infer a personal risk solely from recurrence, general review sentiment or a Dossier category. Do not create arbitrary free-form negative claims that are not anchored to the accepted Dossier references.

For `analyzed_not_fit` with `not_fit_basis = "confirmed_personal_negative"`, the balanced negative assessment must be `completed` and contain at least one `confirmed_personal_risk` finding. Other completed not-fit bases still require the same balanced assessment, but they do not automatically imply a score-affecting risk.

Historical accepted Deep results without `negative_assessment` remain historical authoritative fit/not-fit truth. Do not rerun, recreate, recover or invalidate them merely to backfill this field unless GitHub has explicitly emitted that exact identity in the one-off `legacy_full_reanalysis` work mode described below.



## One-off legacy full reanalysis mode

When and only when a frozen work item has `work_mode = "legacy_full_reanalysis"`, execute PPD-010 in the existing Deep worker. This is not recovery and not a second first pass.

- Treat the item's `migration_provenance` as immutable GitHub-owned identity. Echo it exactly in a result or terminal execution receipt.
- Use the frozen profile pin from the work manifest and the exact Dossier from `migration_provenance.migration_authority_commit`. Do not use a later Dossier even if the current repository contains one.
- If `prior_outcome = "analyzed_fit"`, `preserved_positive_evidence` is the complete already-accepted favorable evidence. Do **not** search the web or Dossier for additional positive evidence, do not rewrite it, and do not drop inconvenient rows. An `analyzed_fit` migration result must return `positive_evidence` exactly equal to that preserved list.
- If `prior_outcome = "analyzed_not_fit"`, `preserved_not_fit_evidence` is the accepted existing unfavorable/decision baseline. Do not invent positive evidence that the prior revision never contained. A new `analyzed_not_fit` result must retain every preserved baseline row; if the available frozen evidence cannot support a responsible completed conclusion, return `analysis_incomplete` instead of manufacturing a fit.
- Re-evaluate the whole personalized conclusion under the current Deep contract using the preserved favorable/baseline side plus **every** frozen Dossier negative/mixed observation and conflict. The new completed result may change overall outcome, fit level, confidence, taste factors, not-fit basis/evidence and grounded negative findings.
- Apply the mandatory balanced `negative_assessment` rules below exactly. Confirmed risks may use only existing canonical risk codes; cautions remain display-only.
- Do not preserve the old overall verdict merely because it was previously accepted. The old revision is immutable history, not a forced answer.
- `analysis_incomplete` is allowed when the frozen evidence does not support a trustworthy completed revision. GitHub will record that migration attempt without replacing the prior completed Deep revision.
- Never reinterpret this work mode as `recovery`, never create a recovery authorization, and never consume or alter normal-first-pass/recovery accounting.
- Never expand the migration scope. Once GitHub stops emitting a target for this migration ID, do not rediscover it from legacy state on your own.

## Ownership boundary

GitHub alone owns Deep scope/order, run-start confirmation truth, exact run-start acceptance proof, normal-first-pass accounting, recovery ownership/authorization, validation, canonical persistence, terminal receipts, future eligibility recomputation, completeness and producer projection. The worker never chooses retry eligibility or recovery scope.

The run-start confirmation is an anti-race publication guard for the exact GitHub-selected marker-parent Deep authority, not a repository-wide head-stability lock. Semantic computation before confirmation is speculative only; no semantic artifact may cross the GitHub boundary before the exact confirmation is durable.

Invalid technical transport consumes no semantic attempt. GitHub may persist its rejection receipt and remove the invalid active inbox candidate; only a later invocation's then-current GitHub run-start view can authorize another submission. The worker never turns a freed path into its own retry decision.

Do not modify Fast/PASS 1 state, Dossier state/workflows, Deep GitHub state/recovery authorization/accounting, visual projection, or Scheduled Task settings.
