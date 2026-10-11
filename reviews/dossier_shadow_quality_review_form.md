# Offline Dossier shadow-quality review / adjudication form

**STATUS: PROPOSED / INACTIVE.** No game selection, real source reading, quality confirmation, semantic-worker launch, pilot authorization, production cutover or Deep readiness. The accepted one-stage Dossier remains authoritative.

## Pre-register and freeze BEFORE viewing outputs

A later user/Director approval must authorize a trial ID, sample owner, exact original indivisible three-game groups, candidate Git commit/group plan, prospective selection method/seed/strata, full-frame denominator and exclusions, reviewers, source/privacy protocol, stop criteria and sample authority. Six groups / eighteen games is a separate proposed calibration size, NOT yet approved or selected. Never resample favorable games after outcomes.

Freeze a safe Git JSON beneath reviews/dossier_shadow_offline/ with exactly:
- trial_id;
- candidate_manifest_sha256;
- ordered groups[]; each group contains sequence, group_sha256 and exactly three games[] of appid (string), title and original_work_year (integer).

Record freeze_commit plus its immutable commit/path/blob_sha256 locator. Match each group against the actual immutable original candidate group plan. A Steam storefront date is a *different fact kind* from the original work year and from player-feedback publication dates. Track source-language and external work-year truth separately. Unavailable and excluded games remain in the original denominator.

For each group, supply the unchanged historical writer preflight request including the real canonical writer commit/parent, appended writer audit receipt SHA, frozen marker-parent, original group descriptor and the three unchanged cache blobs. The **existing** verify_offline_preflight proves historical acceptance. The presence of an old cache JSON, fit score, worker-written boolean or passing V2 schema is never accepted as writer provenance; missing proof is baseline_writer_provenance_not_verified.

Supply only frozen GitHub-owned Research/Assembly item locators in exact original order. Existing inspect_original_groups plus existing shadow evaluate_offline_fixture check strict V2 and Research/Assembly Git chain, for a whole group of three. A worker claim of assembled_candidate_ready is not acceptance.

## Blind first round — two separate immutable Git documents per game

A and B review separately. They must not inspect one another's findings before BOTH first rounds are Git-frozen on divergent branches from the same initial cohort-freeze commit. Each reviewed Git JSON has its own immutable commit/path/blob_sha256, unchanged at fixture HEAD after merging. A third independent adjudicator acts only after both first-round commits and keeps all disagreements visible. Git ancestry enforces a mechanical separation, not proof of actual human blinding; that still needs procedural review.

Each A/B document has exactly five top-level keys:
- role: A or B;
- subject: exactly trial_id, group_sequence and appid, matching the frozen selected game (prevents cross-game source/review replay);
- dimensions: exactly 13 required named findings;
- negative_retention: one mapping for EVERY old negative/mixed observation;
- unknown_resolution: one mapping for EVERY Research unresolved gap.

Each dimension finding has exactly state, severity, reason_code and anchors. State is confirmed_no_issue, confirmed_issue, needs_review or unknown. Severity is none, minor, material or critical. Valid reason codes are enumerated in scripts/dossier_shadow_quality_review_gate.py as REASONS, e.g. evidence_supported, source_not_verifiable, negative_dropped, unknown_overstated, wrong_product, personal_data_leak, confidence_overstated. Confirmed judgments need an exact safe bound anchor. No freeform personal/raw review text.

| Exact dimension key | Independent quality test |
| --- | --- |
| supported_claims | Are claims supported by exact item/player feedback rather than metadata/search hit/aggregate or invented recurrence? |
| source_authenticity | Does real external player-authored evidence exist and support claims? Offline anchor existence is NOT independent authenticity. |
| source_independence | Are sources different physical parents, not duplicated wrappers, quotes, aliases or metadata? |
| negative_mixed_retention | Does every substantive old negative/mixed finding survive or have an independently supported correction? |
| material_omissions | Are important strengths, caveats, unknowns, risks and contradictions preserved? |
| unknown_gap_fidelity | Are unresolved Research gaps still unknown unless exact-source evidence resolves them; was revisit/gap lookup disciplined? |
| original_work_year | Is original/work-year matched to original/work-year, with external truth independently checked later? |
| storefront_date_distinction | Has Steam storefront date been confused with work year or player-feedback dates? |
| russian_language_quality | Were Russian-language evidence, search outcomes, translation and limitations represented accurately? |
| identity_version | Are AppID, title and original/DLC/remaster/version/source identity correct? |
| privacy_safety | Are player handles, profiles, raw quotes, personal records and identifiers excluded? |
| technical_localization_risk | Have technical, compatibility, localization and region risks survived with their proper time scope? |
| confidence_calibration | Is certainty consistent with sample breadth, dates, contradictions and support strength? |

Allowed anchor shapes are old:obs:<index>, new:obs:<index>, old:source:<id>, new:source:<id>, old:feedback:<id>, new:feedback:<id>, research:finding:<ref>, research:source:<ref>, and research:gap:<id>, all scoped to the same already Git-validated game. Duplicate/unknown anchors are rejected. Source URL presence does not prove the source is genuine.

negative_retention mapping keys use old:obs:<index> for EVERY old negative/mixed item. Mapping values contain disposition (preserved, supported_correction, missing, unknown) and anchors. Preserved requires a bound new *negative/mixed* observation; supported corrections require explicit material evidence and a separately coded judgment. Unknown/missing cannot be called parity.

unknown_resolution mapping keys use research:gap:<id> for EVERY Research gap. Mapping values contain disposition (still_unknown, confirmed_with_source, omitted) and anchors. A confirmed claim requires bound source evidence, not just a conclusion; a real-world source check remains mandatory.

Never include a player name, handle, source author ID, email, profile, URL, pasted raw review, private data, personal hash or reviewer freeform note in Git reports. Machine documents accept only safe exact source identifiers and enumerated reason codes.

## Separate adjudication

Third-person adjudication JSON has exactly role (adjudicator), subject (same exact trial_id, group_sequence and appid), resolved and justifications. resolved keys match ALL A/B differences: dimension keys, negative:old:obs:<index> or gap:research:gap:<id>; values are A, B or unresolved. justifications has identical keys, each with a defined reason_code and >=1 existing bound anchor. Adjudicator commit must descend from BOTH independent first-round commits and must remain immutable. Preserve both original reviewer records; do not erase minority dissent or count unresolved as agreement.

## Denominator and decision card

Always report frozen groups/games, historical writer-proven games, strict candidate-ready groups, comparable games, offline-gate-ready, rejected, not-measured, reviewer disagreements, adjudicated games and unadjudicated disagreements, with per-game codes. Never hide a failed/missing group, pretend it is a pass, or cherry-pick a replacement. Record unrepresented categories as not_measured, not absent.

**Conditional numeric STOP proposals — NOT APPROVED:** One or more critical wrong work-year/product identity, fabricated/unverifiable player source, personal data exposure, high-impact unsupported claim or suppressed material negative should stop the affected original group and demand Director review. If a *later separately authorized* 18-game pilot is chosen, the operational coverage proposal is 18/18 independently frozen A/B decisions and adjudication of every first-round material disagreement. These are NOT an approved semantic pass percentage or failure-rate waiver. There is **no approved numerical parity pass-rate threshold**; any noncritical defect tolerance, impact scale and stop-vs-quarantine scope must be frozen separately BEFORE real outputs are seen.

Even fully valid synthetic files result in offline_gate_ready only, with quality_verified=false, pilot_authorized=false, canonical_readiness=false, deep_readiness=false and real_source_authenticity_verified=false.

Before treating actual evidence as parity: explicit user/Director approval of prospective group freeze (CHАТ 1 independently proposes it), historical writer and GitHub Actions corroboration, Research original-year positive regression and strict group-chain test, real independent source and game/work-year authenticity, genuinely blind human A/B, reasoned adjudication, source privacy review, preapproved numeric decisions, and a separate later authorization for any production integration under the existing canonical writer lock.
