# Research Stage 1 technical boundary audit — CHAT 4

Status: **ARCHITECTURE_RECON_COMPLETE (design only; detailed implementation preflight required)**. Source: current main; immutable original marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`. No Research, Assembly, production, scheduler, or source edits.

## Evidence and diagnosis
- Canonical original prompt `config/dossier_shadow_research_trial_semantic_prompt.md` requires the semantic worker to author a full `DOSSIER-RESEARCH-PACKAGE-V1` JSON, populate technical assignment/source fields, invoke `validate_research` and `validate_physical_sources`, calculate byte/canonical hashes, and perform create-only Git transport. These are technical duties mixed into evidence investigation.
- Strict guard `scripts/dossier_two_stage_contract_guard.py` rejects SULFUR 2124120: `identity.identity_source_refs` includes `rsource-002` whose `evidence_role_hint` is `current_state`, not `identity`. This is a substantive role/reference consistency defect; an adapter must NOT silently change the role to identity.
- Physical guard `scripts/dossier_two_stage_staging.py` rejects Sifu 2138710: locator `https://www.sifugame.com/news` has declared domain `www.sifugame.com` whereas verified canonical hostname is `sifugame.com`. Mechanical hostname normalization is suitable for deterministic code. Separately preserve 2022 original-work vs 2023 old-baseline claim for adjudication.
- Four absent exact original paths: 1508750, 1607130, 1849000, 1857090. Proven absent Git transport; whether researched, interrupted, skipped or tool-failed is **unknown**. No item-level attempt receipts in original frozen transport. See independent [PR #233](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/233), head `d068f57fb983809906da7e7ac1dd805f32042b98`, for immutable blobs, commits and [real Python inspect](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596): 12 ready, 2 invalid, 4 missing. Ready is transport readiness, not semantic adequacy.

## Field responsibility matrix (prospective; exact schema-key mapping is an IMPLEMENT preflight acceptance gate)

| Field class | Semantic worker | GitHub deterministic adapter / guard |
| --- | --- | --- |
| Game identity, original work, edition, port, original-work year, uncertainty | Investigate and provide cited assertions, unknowns, conflicts | Bind AppID/assignment from frozen manifest; never infer semantic identity/year from AppID |
| Twelve research dimensions, positive/negative gameplay findings, source-supported judgments, Russian feedback | Supply typed observations and explicit unknowns; distinguish firsthand vs secondary evidence | Serialize schema shape, preserve null/unknown; reject unsupported fabricated claims |
| Source URL, physical parent, acquisition mode, date, role, independence, privacy-sensitive locator | Provide actually inspected URL, role claim, acquisition evidence, factual dates or null | Parse URL, normalize hostname (including www), canonicalize safe URL, validate HTTPS, identity/privacy, physical parent, provenance and role/reference consistency; never invent role or inspected status |
| Source IDs, evidence references, cross-reference links | Associate assertions with semantic source records | Assign stable IDs, map references, reject dangling/wrong-role references; do not launder source roles |
| Assignment ID, group sequence, AppID binding, trial/marker/nonce, candidate path | None; consume pinned assignment only | Generate entirely from GitHub-owned immutable manifest/marker |
| JSON schema/version, field ordering, safe empty collections, optional nulls | Provide typed content; never manually compose canonical JSON | Generate full schema-valid object, safe structural defaults only; missing substantive evidence remains unknown |
| Raw SHA-256, canonical SHA-256, blob identity, commit ancestry, transport status | None | Calculate/verify exact bytes, single create-only Git commit, ancestry and path collision checks |
| Outcome/attempt/disposition | Explain semantic evidence insufficiency or inability when observed | GitHub-owned immutable per-item accepted/invalid/blocked/unknown-attempt receipt; no unapproved retry |

## Proposed end-to-end boundary
Frozen GitHub assignment/one-shot authorization -> semantic typed findings with source-level observations and uncertainties -> deterministic adapter builds canonical Research V2 package with pinned keys, source IDs, URL/domain normalization and schema-safe structural fields -> unchanged or stronger strict schema, physical, privacy, source-role, evidence and assignment validators -> GitHub-owned create-only transport and per-item immutable receipts -> Stage B inspect only after independent QA and explicit authorization.

**Important:** normalize a source hostname, not the evidentiary meaning of that source. For SULFUR, do not automatically promote `current_state` to `identity`; require independent identity evidence or remove the unsupported identity assertion, preserving explicit incompleteness. Reject unsafe URLs and author identifiers rather than scrubbing evidence silently. Source acquisition/role must remain traceable to what was genuinely inspected. Preserve strict privacy and original-work-year comparison.

## Receipt and failure handling
GitHub owns an append-only, immutable per-item disposition tied to exact trial/assignment/marker and adapter version: submitted-valid, submitted-invalid (specific validator code), evidence-incomplete, explicit semantic failure, transport failure, or unconfirmed/no receipt. Receipt records cannot claim an attempt occurred unless supported by an authorized execution receipt. Keep transport errors separate from semantic failures. Do not create ChatGPT-owned queues, retry loops or automatic retry authority. GitHub should generate structured validation codes rather than Stage B's collapsed `invalid_origin_or_binding` alone.

## Exact same-18 rerun
Historical original order and triples, frozen buffer blob `c8a6b6f515162f431c0e3d86175376114c0acf7e`:
- g3: 1508750, 1517180, 1533420
- g8: 1590230, 1599600, 1607130
- g13: 1849000, 1857090, 1868140
- g15: 1999170, 1999360, 2009010
- g18: 206420, 2067050, 2076140
- g20: 2124120, 213610, 2138710

Preserve original source baseline `95a4bf4990a60082ecb3302da5bc7f23b618d93e`, historical Research marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, one-use feasibility authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`, original sandbox and all old candidate bytes. **Do not reuse original one-use marker or overwrite candidate paths.** Define a new versioned isolated trial namespace and separate GitHub-issued immutable marker/authorization, with exact original baseline and 18 frozen assignments linked by hash to old trial. Execute only after contract + adapter implementation, tests, independent QA and explicit user launch. Every one of 18 must have an individually verified valid Research outcome OR explicit auditable failure/unresolved disposition; never assert all are valid regardless of evidence. No Assembly until separately authorized and readiness proven.

## PR #232 and next work
[PR #232](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232) is Assembly preflight, not permission to run Assembly. Hold its merge/activation decision pending independent QA and Stage 1 architecture changes; determine whether Stage B inspect must be version-aware and report granular validation failures. Do not edit #232 in this task.

**One bounded next IMPLEMENT task:** first amend the sandbox Research ownership/schema/typed-input/receipt contracts and adapter versioning, then implement deterministic Research serializer/URL normalization, strict reference/physical/privacy checks and granular receipts, with fixtures for SULFUR and Sifu, missing outcomes, hostile URLs, mismatched identity roles, all twelve dimensions, historical immutability, and 18 exact order. Independent QA must verify no semantic laundering, exact original lineage, no production writes or scheduler changes, and fail-closed Stage B behavior. Only then authorize a fresh one-shot all-18 Research.

## Boundaries and remaining unknowns
No item-specific explanation for the four missing results can be established from immutable GitHub transport. No assertion that all 12 ready packets are semantically adequate. The proposed typed input/schema migration needs exhaustive field-by-field reconciliation with `config/dossier_research_package_v1.schema.json` before implementation; this report specifies ownership by field class, not a verified exhaustive leaf-key inventory. No permission to rerun or merge is inferred from this report.

Sources: [original trial contract](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_shadow_research_trial_contract_v1.json), [original prompt](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_shadow_research_trial_semantic_prompt.md), [strict guard](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/bb63cc291eba5aa8fc56e2920ef84d131ac28a4f/scripts/dossier_two_stage_contract_guard.py), [physical guard](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/bb63cc291eba5aa8fc56e2920ef84d131ac28a4f/scripts/dossier_two_stage_staging.py), [PR #233 evidence](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/233).
