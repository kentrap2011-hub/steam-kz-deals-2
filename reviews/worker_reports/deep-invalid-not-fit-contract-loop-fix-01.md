# Deep invalid not-fit contract loop fix 01

## Task

Task ID: `deep-invalid-not-fit-contract-loop-fix-01`.

Repository: `kentrap2011-hub/steam-kz-deals-2`.

Branch: `fix/deep-invalid-not-fit-contract-loop-fix-01`.

Pull request: #129, `Fix Deep invalid not-fit contract retry loop`.

Scope completed: align the canonical Deep result schema, worker prompt, PASS 2 contract and GitHub ingest so a proven exact-bound semantic contract failure cannot loop as fresh normal first-pass work, while preserving the existing Progressive Deep worker, recovery architecture, nonblocking frozen sibling traversal, RANK-013 and DEEP-SCORE-EVIDENCE-V1.

No semantic Deep execution and no Scheduled Task/scheduler change were performed in this developer chat.

## Dependency reconciliation with PR #128

PR #128 `Align Deep score evidence with card explanations` was already merged before implementation.

Canonical merge: `d6221868a5e78b9852a0720319de036f76e6ec68`.

Its DEEP-SCORE-EVIDENCE-V1 work-item binding and score-explainability migration were preserved. The branch was repeatedly reconciled with advancing `main` rather than overwriting new production Deep state. In particular, production score-migration state advanced from 0 accepted on the original branch snapshot to 42/43 accepted at fresh-main base `43a95562cca0431eb25d785e91e1c1068356bb7c`.

The score-evidence regression was also made state-aware so it validates both the immutable frozen 43-target migration snapshot and the current advancing production state instead of assuming forever that all 43 targets remain pending.

## Root cause

The four canonical layers disagreed:

- the worker prompt required completed negative assessment and a confirmed personal risk but did not explicitly require high confidence;
- the JSON result schema allowed both `medium` and `high`;
- the PASS 2 contract did not encode the special invariant;
- GitHub semantic validation rejected `confirmed_personal_negative + medium` with `confirmed personal negative requires high confidence`.

GitHub then recorded those parseable exact-bound results as `rejected_invalid_result_no_attempt`. Because no normal first-pass attempt was consumed, the exact same `work_id` remained eligible for ordinary Deep work and could be processed again.

Latest proven repeated execution used run-start anchor `4d1a1c573289358713897559e79b754907ff91c8` and frozen authority `ab9f5f1c841b9c6d40ace1932c7d32437763eb8a`. The three submitted result commits were `6919dcb927526f716e4448d3013eb2c74736e3bb`, `57a31a9789673b6e10464c02938b76c4991a6e40` and `911e1b1e00fdc5dbed1bff3d9e3f0148a18c58ac`. GitHub rejection evidence is in reconciliation commit `5651782bb91a18aaaedc1b26b5973159e3e021d0`.

## Canonical confidence invariant

The canonical invariant is now:

`outcome=analyzed_not_fit AND not_fit_basis=confirmed_personal_negative => confidence=high`.

This is an evidence requirement, not a formatting repair.

Deterministic `medium -> high` rewriting is explicitly forbidden. If evidence does not honestly support high confidence, `confirmed_personal_negative` is unavailable. The worker may use another completed not-fit basis only when that different basis is genuinely supported; otherwise it must choose truthful `analysis_incomplete` with an allowed issue code.

## Schema / prompt / contract / ingest alignment

`config/progressive_pass2_result_schema.json` now has a real JSON Schema conditional requiring `confidence: high` for the confirmed-personal-negative not-fit combination.

`config/progressive_pass2_worker_prompt.md` now states the same evidence rule, forbids mechanical confidence promotion, requires a final pre-publication contract self-check, and keeps GitHub ingest authoritative.

`config/progressive_pass2_contract.json` now encodes the same invariant and explicitly distinguishes exact-bound semantic-contract failures from malformed/stale/unbound transport.

`scripts/progressive_pass2.py` now checks exact immutable identity before semantic normalization. A parseable exact-bound result that then fails semantic result validation is recorded as an `analysis_incomplete` consumed attempt with `attempt_consumption_source=github_derived_semantic_contract_failure` and existing recovery ownership. Wrong identity or other unproven transport remains zero-attempt.

`scripts/ingest_progressive_pass2.py` persists the new `rejected_semantic_contract_result_attempt_consumed` disposition, and `scripts/progressive_work_authority.py` recognizes explicit `attempt_consumed=true` receipts.

## Invalid semantic execution disposition

The system now distinguishes two cases.

Unproven transport/authority failures remain non-attempting: malformed JSON, wrong work identity, wrong path/stale work and unconfirmed/wrong run-start authority do not consume semantic attempt budget.

A parseable result with exact authorized identity that reaches semantic result validation and violates the result contract proves that semantic execution occurred. GitHub records it as terminal incomplete through the existing attempt model, consumes the authorized attempt and prevents that exact identity from immediately returning as fresh normal first-pass work.

No invalid result is accepted as successful Deep truth.

## Attempt / recovery semantics

Normal first-pass remains one attempt per exact Deep identity.

A consumed exact-bound semantic contract failure becomes unresolved `analysis_incomplete`, `authoritative_completed=false`, `recovery_owned=true`.

A later attempt requires the existing fresh GitHub-owned recovery authorization. The recovery reason used for this defect is exactly:

`corrected_runtime_or_validation_defect_material_to_the_prior_failure`.

No new queue, retry daemon, scheduler, semantic worker or attempt owner was introduced.

## Pinned repeated games reconciliation

All three pinned exact identities had sufficient durable proof: exact run-start/work bindings, parseable submitted result commits, the same invariant failure at GitHub ingest, unchanged current semantic generation, unchanged current queue identity, and byte-identical current Dossiers versus frozen authority.

They were reconciled without fabricating accepted Deep results:

- Five Dates / AppID 1353270 / work_id `1379906886119f0bcd8b2d764fa7ce663140ada66a7da03ec1dd08176679773b` -> recovery authorization `78a3660c5930d60c03f6b71d97bea1b9575aac496c684ebccd69143b97a18814`.
- Her New Memory - Hentai Simulator / AppID 1296770 / work_id `a349c27f3663446a76886e22218455525bc43a2428278ca450257ad916f6239a` -> recovery authorization `d330d77dcc3803008332a0291baafdf7f842ee878c5e377bf3527f4e77df00f4`.
- Blazing Sails / AppID 1158940 / work_id `ddb33cb3665250557120ce1deaa1af3f23fe213fd96119e7335f5d17a9c01fe9` -> recovery authorization `c2ef1322b725a4551341e7e013f2949ecba572bc636b313a1e64e64c3950cc19`.

Canonical state reconciliation commit: `9131071437f98f64c911f1700bbdea373fa6ce6f`.

Each identity now has a consumed normal first pass recorded as `analysis_incomplete / terminal_execution_failure`, is recovery-owned, and has one bounded recovery authorization tied to the validated generic fix commit `b21bdfd773162e9856c1b12015b1b497b4999363` plus the historical run/result/rejection proof.

The regression recomputes each recovery authorization with canonical `authorize_recovery` and verifies current eligibility is `work_mode=recovery`, never `normal_first_pass`.

No semantic recovery was executed.

## Worker final-report semantics

The canonical worker prompt now separates create-only submission from canonical GitHub acceptance.

It must report artifacts as submitted when it only created them. It may say accepted or rejected only when that GitHub disposition is actually known. If asynchronous ingest is not awaited, canonical acceptance must be described as pending/unverified.

This reporting rule does not add polling and does not control sibling traversal.

## Validation

Primary final reconciliation tree: `3a41184d7293b23f1f9c9fe184f31222ed91b8f4`.

No-op validation head with the identical tree: `c53d7907d1b37316411ad7e96acd2264e760dc65`.

GitHub Actions:

- Validate Progressive PASS 2 core: run `36680396786` — success.
- Validate backlog dispositions: run `36680396724` — success.
- Prior substantive reconciliation run `36680330138` — success.
- Prior backlog run `36680330244` — success.

Important regression outputs from run `36680330138`:

- `progressive async traversal + Deep invalid transport regression: ok`;
- `progressive Deep parallel frozen start authority regression: ok`;
- `DEEP_LEGACY_FULL_REANALYSIS_TESTS=PASS`;
- `DEEP_SCORE_EVIDENCE_EXPLAINABILITY=PASS`;
- `DEEP_INVALID_NOT_FIT_CONTRACT_LOOP=PASS`;
- active projection accounting: `target=266 waiting=206 ready=8 attempts=55`.

The increase to 55 first-pass attempts includes the three proven pinned semantic executions; they are no longer unattempted ordinary work.

## Production acceptance

Pre-merge acceptance is satisfied:

- schema, prompt, contract and ingest agree on the confidence invariant;
- exact invalid-result loop regression is green;
- existing PASS 2, frozen-start, async traversal, legacy migration, score-evidence, backlog and ownership-related validation remains green;
- pinned identities have deterministic consumed-attempt/recovery dispositions;
- no accepted Deep result was fabricated;
- no recovery semantic execution was performed;
- PR #128 architecture and concurrent production Deep state were preserved by fresh-main reconciliation.

At the latest pre-report main base `43a95562cca0431eb25d785e91e1c1068356bb7c`, score-explainability migration still had 42 accepted / 1 pending target, so ordinary normal work was temporarily paused by that existing migration. Independent canonical eligibility recomputation already proves all three pinned identities are recovery work rather than normal first-pass work.

Post-merge, this chat must verify the merged `main` work/state before handing semantic execution back to the existing Deep worker.

## Unresolved

The only intentionally unresolved work is semantic recovery for the three pinned games. It is prepared and authorized but must not be executed from this developer chat.

No implementation defect is currently known from validation.

## Status

`recovery_prepared_needs_semantic_execution`.

## Exact PR/commit/run references

- dependency PR #128 merge: `d6221868a5e78b9852a0720319de036f76e6ec68`;
- implementation PR: #129;
- generic validated fix commit: `b21bdfd773162e9856c1b12015b1b497b4999363`;
- fresh-main reconciliation merge: `ded2de1c711be2b2c51026b6612b5cd837cfb9e7`;
- pinned state reconciliation: `9131071437f98f64c911f1700bbdea373fa6ce6f`;
- pinned regression commit: `d0a1ca467a9d627a1285d856dd27712eda1c4f33`;
- recovery-ID verification commit: `3a41184d7293b23f1f9c9fe184f31222ed91b8f4`;
- validation head: `c53d7907d1b37316411ad7e96acd2264e760dc65`;
- final pre-report main base: `43a95562cca0431eb25d785e91e1c1068356bb7c`;
- PASS 2 core run: `36680396786`;
- backlog run: `36680396724`;
- historical rejected-results reconciliation: `5651782bb91a18aaaedc1b26b5973159e3e021d0`.

## Recommended next step

After PR #129 is merged and this chat confirms the merged recovery work on `main`, run the existing Progressive Deep semantic worker once normally.

## Efficiency / reusable lesson

Do not classify all invalid result documents by parse success alone. First prove exact authority/identity, then separate transport invalidity from post-execution semantic-contract invalidity. The latter already spent semantic work and must be accounted through the existing attempt/recovery owner; otherwise a zero-attempt rejection silently becomes an infinite semantic retry loop.

For long-lived migration regressions, test semantic behavior against the frozen migration authority snapshot and test production accounting dynamically. Hard-coding `pending=total` makes otherwise-correct validation fail as production legitimately advances.
