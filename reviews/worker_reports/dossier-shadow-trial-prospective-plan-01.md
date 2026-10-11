# Worker report A — prospective two-stage Dossier shadow trial (NOT EXECUTED)

**Worker:** НОВЫЙ ЧАТ — ЧАТ 2  
**Task:** `WORKER_TASK_DOSSIER_SHADOW_TRIAL_PLAN_AND_SITE_DEEP_COUNT_QA_01.md`  
**Base:** `main` at branch creation `6bdd2a26f408d52eb533e1ef2135347f11956f57`  
**Disposition:** `prospective_plan_complete_inactive_no_authorization`  
**Existing implementation:** accepted PR #191, `scripts/dossier_two_stage_shadow_quality.py`, `reviews/dossier_two_stage_shadow_trial_protocol.md`. No new validator, scheduler or workflow is proposed.

## Preregistration card — to be completed and approved BEFORE real selection

| Required field | Pending frozen value |
| --- | --- |
| Trial ID; planned start/end; Director/user approval/commit | `NOT_APPROVED` |
| Objective | Side-by-side Research→Assembly→strict V2 against independently writer-accepted one-stage Dossier for the *same exact game/work identity* |
| Eligible GitHub snapshot commit + manifest/tree hashes | `NOT_FROZEN` |
| Legacy accepted writer commit, per-group receipt/state, cache SHA | `NOT_VERIFIED` |
| Research/Assembly binding, immutable markers, V2 result SHA | `NOT_FROZEN` |
| Sampling method/seed/strata, units, planned exclusions | `PROPOSED_ONLY` |
| Auditor A/B and disinterested adjudicator; source access protocol | `UNASSIGNED` |
| Preapproved failure-rate thresholds and decision owner | `NOT_APPROVED` |
| Final authorization for read-only real-source trial | `NOT_APPROVED` |

These are placeholders, **not** authority to select actual games, start workers or read live review sources. A trial lacking the frozen writer receipt is uncomparable, even if an on-disk legacy JSON exists and passes schema validation.

## Proposed selection policy (recommendation only)

- Sampling unit = **original immutable three-game Dossier group**, never hand-picked independent games. Freeze a pre-output eligible-group frame from current GitHub authority. Require matching exact accepted one-stage writer receipts for all proposed comparators, but record every excluded/missing group against the frozen frame rather than silently substituting an easy group.
- Suggested scale for separate approval: **30 original groups / up to 90 games** in two preregistered batches (**6 groups / 18-game calibration pilot**, **24 groups / 72-game holdout**). This is a planning estimate, **NOT approved sample size or throughput quota**; a different approved size may be chosen before sampling. The pilot calibrates *reviewer agreement and rubric*, not favorable semantic outcomes. Do not resample the holdout based on pilot performance.
- Enumerate each eligible group's **pre-output** characteristics from GitHub-frozen metadata and source-provenance descriptors only: original-vs-storefront release-year ambiguity, original/remaster/DLC identity, Russian/multilingual evidence, recent/older/unknown publication dates, independent player-source breadth, local/technical risks, meaningful negative/mixed evidence, and source-route exhaustion/unknown gaps.
- Proposed group-level stratification: deterministic rare-category coverage first (where available), then fill remaining groups by publicly reproducible SHA-256 sort on `trial_id|frozen_manifest_sha|group_id`. Freeze the category membership rule, seed, all group IDs/order and exact Git tree prior to observing Research→Assembly results. Multi-label groups count once; no cherry-picked replacements after unblinding. Any infeasible category is reported `not_measured` with denominator.
- Maintain an immutable **CONSORT-like accounting**: frozen frame N → predeclared selected groups N → groups with independently verified legacy acceptance N → valid complete three-game strict V2 chain N → auditable games N → independently reviewed N → adjudicated N. Count failed/unavailable/mismatched games as failures or `not_measured` with reason, never as silently excluded winners.

## Evidence freeze and eligibility gate

For **each original group**, record GitHub authority SHA + `work_id`/appid/work year/release identity, manifest and source blob SHAs, frozen Research request SHA, marker parent, Research commit/source refs, Assembly candidate/transport SHA, final V2 strict acceptance inspection and exact one-stage **historically writer-accepted** counterpart with writer commit/group receipt/cache blob. Pair by product identity, not by title alone. Date/year comparison must compare *original work release year with original work release year*; storefront date is independently labeled and not substituted. Research→Assembly→strict V2 validation uses existing PR #191 harness `evaluate_offline_fixture` inside disposable local Git. Its `baseline_acceptance=not_verified_separate_writer_receipt_required` is deliberately **not** evidence of an accepted baseline.

The known conflicting original-year Research case previously XFAIL must be jointly rechecked after accepted PR #187/#188 integration; require evidence of a positive strict conflict rejection regression. No quality success can repair a failed identity/year chain.

## Independent review rubric and recording form (one row per game)

Two independent auditors initially see the same frozen, safe citations but record judgments separately; avoid revealing the other auditor's decision until both commit review files. Third independent adjudicator resolves differences with cited reasoning; keep *all* opinions and final decision. Reviewer identifiers should be role labels, not player/source-identifying handles.

| Dimension | Minimum recorded evidence | Outcome |
| --- | --- | --- |
| Exact identity and year | Work release year vs storefront release year, AppID/version/remaster/DLC, original chain SHA | `confirmed_no_issue / confirmed_issue / needs_review / unknown` |
| Research coverage | 12 required dimensions, per-dimension state, gaps/unknowns, Russian outcome | same |
| Authenticity/independence | Working exact-item player-authored source, independent parent/source counts, direct evidence vs search hit/aggregate | same |
| Finding preservation | Baseline material strengths, negative/mixed risks, omissions, supported corrections and new contradictions | same |
| Conclusion utility | Balanced trade-offs, certainty language, material impact on player's decision, semantic improves/equal/degrades | same plus `improves/equal/degrades/unknown` |
| Gap/follow-up discipline | Frozen source-first revisits, specific field-only fallback, unavailable outcomes remain unknown | same |
| Temporal/privacy hygiene | Evidence publication dates/unknown, deterministic classification, no player identifiers or raw private data | same |

Every confirmed verdict cites safe source/observation ID and immutable blob/commit; bare URL, alias, search snippet or aggregate is not a substantive citation. Check that two sources are independent *parents*, not duplicate wrappers. A schema-valid output is **not** semantic equivalence. Verify original negative or mixed findings even if both new dossiers look fluent.

Suggested per-game record fields: `trial_id`, `group_id`, `appid`, `original_work_year`, `frozen_binding_shas`, `historical_writer_receipt`, `baseline_blob_sha`, `research_sha`, `assembly_sha`, `v2_sha`, `twelve_dimension_checks`, `source_parent_audit`, `material_omissions[]`, `unsupported_claims[]`, `contradictions[]`, `privacy_failures[]`, `negative_mixed_retention`, `auditor_A`, `auditor_B`, `adjudicator`, `status`, `exclusion_or_unknown_reason`. Never include player names, profiles, handles, quotes or private identifiers in reports.

## Suggested stop/decision/rollback gates — none approved

**Immediate item/group halt:** wrong work/app/year/binding, invalid three-game Git chain, missing accepted one-stage writer receipt, untraceable source, unsupported material assertion or omitted material risk, privacy leak, falsified date/source parent, active writer/cache/Deep change. Preserve immutable evidence/receipts; no in-place edit, implicit retry, resampling, widening, or production fallback.

**Proposed numerical criteria for later stakeholder consideration only:** 0 privacy/identity/year/source-fabrication failures; 0 unsupported *material* risk-suppressing assertions; material omission and material degradation at most **2/90 games**, independent auditor coverage **90/90** where evidence is available, 100% explicitly counted unresolved cases, and 100% adjudication of material disagreements. These are *hypothetical conservative acceptance candidates*, `approval=NOT_APPROVED`; no statistically guaranteed quality follows from such a small sample. Any fatal safety finding causes stop even if a proposed aggregate threshold would pass. If approvals specify other limits, freeze them **before** the actual trial.

**Pre-run gate:** accepted #187/#188 year fix and joint integration QA; frozen frame/group baseline acceptance; independent real-source availability; reviewer conflict-of-interest declarations; Director-approved trial-ID/sample/limits.  
**Review gate:** no fatal cases, report complete denominator flow and per-item citations, independent A/B reports/adjudications; disclose uncertainty rather than pass unknown data.  
**Decision gate:** Director/user explicit signed acceptance required; no hidden automatic `canonical_readiness` or `deep_readiness`; existing helper remains false.  
**Rollback/cutover:** this trial is inactive so old one-stage authority remains unchanged and rollback is no-op. Any later migration requires *another* contract/PR approved under current shared GitHub canonical writer lock, pinned old cache+Deep references, fail-closed rollback and prevention of mixed authority. No Fast removal, Deep migration, live semantic execution or scheduled task action here.

## Execution and evidence status

Read #191 as merged (`42919b50af4df6212a9d2ab7233635c438571a7f`), its inactive protocol and prior report (8 synthetic tests passed on PR CI `38121638162`). This task **did not** run a trial, freeze any live group, inspect real player-authored source or verify one-stage writer receipts. It prepares only the preregistration proposal. Site-count QA is in the separate report `site-deep-count-14-vs-ui-8-plus-9-diagnostic-01.md`.

**Next authorized decision:** approve/revise prospective scale and selection method, reviewer assignments, acceptable failures and trial boundary *in a new separate task*; otherwise stay inactive.
