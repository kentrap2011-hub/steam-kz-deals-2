# Future Research → Assembly versus one-stage V2 shadow-quality trial

**Status:** DRAFT / INACTIVE. No real evidence run, semantic-worker invocation, sample selection, production cutover, automatic activation or failure-rate approval is authorized by this document or by the readiness PR.

## Scope and authority

- Director/user must separately approve a bounded trial ID, exact games, review operators, accepted baseline commit and independent source-verification process *before* real semantic evidence is requested or used.
- GitHub remains the sole owner of source scope, game order, original three-game groups, immutable Research/Assembly work manifest, Git markers, downstream strict V2 validation, retries, recovery and eventual Dossier acceptance. No interactive chat picks additional games or retry scope.
- Use the GitHub-frozen candidate manifest, original prepared assignments, marker-parent identities, Research package Git commits/blobs/raw SHA and exact Assembly submissions. The new offline quality harness calls `inspect_original_groups` from the existing final-acceptance bridge, which calls the existing Research validator, Assembly chain validator and strict V2 group validator. It must never treat a worker's `assembled_candidate_ready` string as acceptance.
- The trial operator builds a **disposable, isolated local Git replica** from the exact frozen Git evidence and a timestamped frozen copy of the original one-stage accepted cache. The replica is not the live working repo; use the existing `.dossier-final-offline-fixture` guard and verify lineage/byte hashes. There is no automated inbox, website access or writing to production. The current bridge permits only such isolated fixtures.
- At trial time independently cross-check that each `data/cache/taste_steam_review_dossiers/App_<appid>.json` baseline was accepted by the **existing GitHub writer** for the exact appid/identity (original writer commit, group acceptance state and hash). A file's existence, passing strict V2 validation and an operator's claim are each insufficient to establish historical acceptance. This separate writer-receipt verification is intentionally **not automated** in the inactive harness. Without it, diagnostic output must retain `baseline_acceptance=not_verified_separate_writer_receipt_required`.

## Freeze and sample selection before unblinding

1. Director/user approves the objective, period, sample owner and independent reviewers. GitHub owner freezes the exact selected candidate identities, group plan, submitted timestamps/commits and immutable legacy counterpart. Sampling is prospective; never cherry-pick only improved examples after seeing results.
2. The proposed sample must cover, as available, original-game versus Steam storefront year discrepancies; original/remaster/DLC identity; multilingual and Russian-signal cases; recent/older/unknown publication dates; strong and weak player-source diversity; technical/localization risk; meaningful negative/mixed findings; and gaps requiring revisits or explicitly unknown conclusions. These are categories, **not quotas or claimed numerical thresholds**. Record unrepresented categories as `not_measured`.
3. The Director must approve a *prospective sample selection method* and review rubric (including any numerical acceptable failure rates) in a separate decision before evaluating real candidates. This PR sets **no** threshold or failure-rate waiver.
4. Candidate Research and Assembly packages must already be authorized and GitHub-validated against the exact frozen state. If not, no side-by-side judgment is performed for that game. A missing/invalid game cannot be silently dropped from cohort accounting.

## Independent side-by-side human evidence audit

For each game, inspect, record explicit citations to immutable *safe* Research finding/source refs and V2 observation/source IDs, and compare these dimensions **separately**, without combining into a fabricated numeric quality score:

- **Product identity:** AppID, title, original/work year, release/remaster/version/platform. Compare original release year only with original release year; a different Steam storefront date is a different kind of fact, not an automatic conflict.
- **Research completeness:** twelve required dimensions, documented investigation states, Russian-language search outcome, genuine unknowns, material gaps, source and temporal route coverage, central strengths and recurring weaknesses.
- **Source quality:** real presence of each exact product's player-authored evidence; working public-source citation and support strength; physical independent-source diversity rather than two aliases or two records of one parent; metadata/search-hit/aggregate cannot pose as player feedback. A synthetic URL/fixture is not evidence that a real source exists.
- **Claims and conclusions:** each candidate V2 observation supported by safe exact-item evidence, whether the original one-stage substantive fact survives, whether reasoning overstates recurrence or chronology, and whether comparable negative/mixed trade-offs remain visible.
- **Gaps and supplemental follow-up:** every operation references its frozen Research gap/source, genuine exact-source-first revisit, narrow one-field lookup only after an explicit genuinely-absent result; verify no unrelated general re-research or conversion of unknowns into assertions.
- **Temporal and privacy fidelity:** dated feedback versus unknown date; GitHub-owned deterministic recent/older/unknown classification; source/child citation consistency; source snapshots and safe locators. No names, profiles, handles, hashes, author aliases, raw review/post excerpts or private source data appear in outputs.
- **Conflicts:** year mismatch, contradictory support, old/new disagreement, unresolved source conflicts and accidentally merged cross-release evidence. Mark supported corrections distinctly from unexplained removals.
- **Independent semantic judgment:** clarity, balancedness, usefulness of conclusions and whether the two-stage output improves/equates/degrades versus the accepted one-stage dossier. Strict schema compliance alone cannot answer this.

Use review states `unknown`, `needs_review`, `confirmed_issue`, `confirmed_no_issue`; confirmed judgments must cite exact source/reference identifiers and an explanation. Different reviewers should independently examine material omissions and source authenticity before adjudication. Preserve disagreements rather than deciding from superficial wording similarity.

## Stop conditions and rollback

Immediately stop the affected game or the whole trial (as scoped by an explicit Director review) if frozen binding, baseline acceptance, original-work identity, or strict V2 validation is ambiguous; if evidence sources are invented, unverifiable or wrongly attributed; if a material risk is suppressed or an unsupported finding is asserted; if identity/temporal/private data leaks are found; or if an active production writer/Deep/cache change is detected. Record exact Git references and safe diagnostics. Do not retry/rebind/edit a semantic result in place. Existing one-stage Dossier remains authoritative throughout the trial; there is no active two-stage state to "rollback" in this readiness phase. If a later cutover is separately approved, require an explicit canonical-writer-level rollback/recovery plan preserving accepted one-stage records and avoiding mixed Deep references.

## Decision / handoff gates

The quality trial report must include frozen cohort denominators; exact number compared and excluded/not-measured with reason; complete per-game immutable source and V2 hashes; review evidence and reviewer disagreements; categorical material omissions, unsupported claims, privacy/source/year contradictions; a comparison of negative and mixed findings; real-source audit outcome; and explicitly Director-approved acceptable failure rates versus observed outcomes (or `not_approved` if not yet approved).

A quality readiness result can be proposed **only after** all separately required conditions are demonstrated: fixed and jointly retested Research year consistency, immutable Research→Assembly→strict three-game Git chain, accepted original one-stage benchmark confirmation, independent real-evidence checks, adjudicated semantic parity, approved failure-rate criteria, safety/contradiction resolution and explicit user/Director sign-off. The present helper intentionally returns `canonical_readiness=false` and `deep_readiness=false` for every input; it cannot become an activation gate by toggling a flag.

A later dedicated authorization and separate PR must handle any production integration under the existing shared GitHub writer lock. Do not create a second final validator, scheduler, retry manager or Scheduled Task and do not remove Fast or migrate Deep as part of shadow-quality verification.

## How to run *only synthetic* isolated proof in this PR

```sh
python -m pip install 'jsonschema>=4.21,<5'
python -m unittest discover -s scripts -p 'test_dossier_two_stage_shadow_quality.py' -v
```

This is a synthetic logic/guard test, not a real-source semantic comparison or a production run. The low-level `compare_records` function is a deliberately non-authoritative pure projection for validated/synthetic objects; only `evaluate_offline_fixture` invokes the existing strict Git-bound inspector, and even it does not independently prove the historical baseline acceptance receipt.
