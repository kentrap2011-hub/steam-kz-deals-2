# Dossier two-stage Research + Assembly — architecture report 01

**Task:** WORKER_TASK_DOSSIER_TWO_STAGE_RESEARCH_ASSEMBLY_ARCHITECTURE_01.md  
**Repository / source:** kentrap2011-hub/steam-kz-deals-2 / main; inspected 2026-10-08.  
**Mode / result:** ARCHITECTURE / CONTRACT RECON; **proposal only, NOT activated**.  
**Status:** complete_ready_for_director_acceptance (architecture review required before implementation).  
**Delivery scope:** report-only PR. No production writes, semantic work, automation changes, or contract/source changes.

## Decision and architecture preflight

**Recommendation:** versioned per-game Research evidence packages with GitHub structural/privacy validation; per-game Assembly results sealed independently; GitHub reconstructs the *existing exact three-game group*, runs the **unchanged** strict buffered Dossier validator/ingest under its existing single canonical-writer domain, then alone marks group accepted/failed/pending and recomputes Deep eligibility. A dual-lane, bounded GitHub-assigned pipeline can overlap Research for N+1 with Assembly for N; **this is not two independent queues**. The current one-stage worker stays active until separate contracts, implementation, parity, shadow verification and Director cutover approval.

Architecture preflight (CHAT_CONTEXT.md):
1. **Owner now:** config/execution_ownership_contract.json + config/taste_steam_review_dossier_contract.json + config/taste_steam_review_dossier_persistence_bridge.json: GitHub owns immutable work scope/group plan, identity, retries/recovery, attempt accounting, acceptance, persistence and shared canonical writer. Scheduled ChatGPT is bounded semantic data plane.
2. **Permission:** the current contracts authorize only the existing one-stage buffered worker. This task authorizes **design only**; separate versioned contract amendments are prerequisites for Stage-A transport, Stage-B assignments, staged per-game output, any parallel lease or transport changes, and a pre-publication validator.
3. **Ownership:** proposed lanes never select/reorder work, infer canonical acceptance, author retries, write canonical caches/progress or control schedules. GitHub prepares every assignment and is the only reconciler.
4. **No unauthorized recurring stage:** independent scheduled Research/Assembly invocations and their cadence are **not authorized by this report**. Future implementation must prove that operator-approved orchestration can invoke both roles without creating a second independent queue owner or self-managed scheduler. Existing Scheduled Task unchanged here.

Canonical references actually examined: CHAT_PROTOCOL.md, CHAT_CONTEXT.md, PROJECT_ROUTES.md (Dossier route), PROJECT_DECISIONS.md (TASTE-007, 011, 014–017, PPD-011), config/execution_ownership_contract.json, config/taste_steam_review_dossier_runtime_prompt.md, config/taste_steam_review_dossier_worker_prompt.md, config/taste_steam_review_dossier_schema.json, config/taste_steam_review_dossier_web_evidence_contract.json, config/taste_steam_review_dossier_terminal_receipt_schema.json, config/taste_steam_review_dossier_contract.json, config/taste_steam_review_dossier_persistence_bridge.json; scripts/taste_steam_review_dossier_strict.py, scripts/taste_steam_review_dossier_buffered.py, scripts/taste_steam_review_dossier_group_progress.py, scripts/taste_steam_review_dossier_worker_projection.py, scripts/taste_steam_review_dossier_prepublication.py, scripts/ingest_taste_steam_review_dossier_inbox.py, scripts/ingest_taste_steam_review_dossiers.py, scripts/taste_steam_review_dossier_recovery.py, scripts/build_progressive_pass2_work.py and .github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml. Baseline: reviews/worker_reports/dossier-throughput-quality-preserving-diagnostic-01.md.

## 1. Current contract fit: move semantics, not authority

| Responsibility now inside one-stage worker | Target | Immutable boundary |
| --- | --- | --- |
| Resolve exact work/product identity: AppID, title, original/work release year, identity-role source; distinguish DLC/editions/remakes | **Research observes**, **Assembly verifies/copies** | GitHub defines descriptor AppID/title and checks binding. PPD-011 forbids comparing work-year to Steam storefront-year as equivalent kinds. |
| Find concrete player feedback across materially distinct physical surfaces, Russian/mixed evidence, positives, weaknesses, issues, chronology | **Research** | Neutral/profile-blind; no source/review/search count quotas; TASTE-014/015 completeness beats speed. |
| Record safe parent/child locator, actual visible item vs search-result representation, factual dates/languages and provenance | **Research observes facts**; **Assembly validates and may reopen exact source** | Never invent missing date/locator/identity or turn query/aggregate metadata into observed player feedback. |
| Decide evidence meaning, qualitative recurrence, supported conflicts, nuances, 12-dimension coverage closure | Research supplies attributable observations and coverage/gap attestation; **Assembly makes canonical classifications**, with Research re-open where substantive coverage is missing | Stage-B may not replace missing research with speculative labels; GitHub strict validation remains fail-closed. |
| Create source-NNN/feedback-NNN sequence ids, copy descriptor binding, join indices, derive bound language union, summary, normalized domain, TTL/date-derived freshness | **Deterministic GitHub helper for mechanical transforms**; Assembly handles semantic association decisions | GitHub derives recent/older/unknown from factual publication dates; strict.py::derive_temporal_state. No inferred support. |
| Build strict Dossier V2 and inspect source/feedback link graph | **Assembly** creates per-game V2 candidate | Current exact V2 observation/conflict/coverage schema, privacy and 365-day checks unchanged. |
| Prepare index, descriptors, frozen marker parent, group plan, create-only transport path; classify failures, reconcile cache/rollover, author retry/terminal acceptance | **GitHub only** | Existing group-progress, frozen-authority validation, retryable invalid quarantine, Deep eligibility and canonical-writer concurrency unchanged at the final boundary. |

Current runtime already freezes a nonce-only marker's **actual Git parent** as GitHub-selected authority, permits cached exact per-item Dossier reuse, traverses frozen groups without waiting for ingest, and accepts present groups independently (missing/invalid older sequence does not block later valid groups). Do not claim these as new accelerations. Current prepublication.py is **CI/developer parity only**; active web-evidence contract explicitly disallows mandatory Scheduled-worker local Python/manual prechecks. Two-stage pre-acceptance requires a **new, approved GitHub** contract, not a hidden second check in chat.

## 2. Versioned Stage-A evidence package: proposed exact wire shape

New *inactive proposal*, schema **DOSSIER-RESEARCH-PACKAGE-V1**, schema_version 1, strict unknown-field rejection. **One game per package**, nested under its existing immutable three-game descriptor; no synthetic source data. The following object is a **field/type specification, not a synthetic production example** (field values represent types).

~~~text
{
  schema: const "DOSSIER-RESEARCH-PACKAGE-V1",
  schema_version: const 1,
  assignment: {
    assignment_id: string (GitHub-issued opaque immutable id),
    snapshot_id: sha256hex, group_sequence: positive_int,
    group_sha256: sha256hex, prepared_required_sha256: sha256hex,
    group_plan_sha256: sha256hex, items_sha256: sha256hex,
    item_index: nonnegative_int, appid: numeric_string,
    title: exact_descriptor_string,
    source_queue_sha256: sha256hex, scope_source: descriptor_string,
    research_contract_sha256: sha256hex,
    dossier_web_evidence_contract_binding: exact_GitHub_binding,
    research_marker_anchor_commit: GitHub_create_commit_sha,
    research_marker_nonce: 32_hex
  },
  identity: {
    resolved_title: string_or_null, original_work_release_year: int_or_null,
    resolution: "resolved" | "unresolved",
    corroborators: [{kind: allowed_current_identity_kind, value: safe_value}],
    identity_source_refs: [local_source_ref],
    ambiguity_notes: safe_neutral_synthesis_or_null
  },
  sources: [{
    ref: "rsource-NNN" (package-local only),
    locator: {url: safe_public_https_url} | {public_ref: safe_neutral_locator},
    normalized_locator: safe_GitHub_verified_identity_or_null,
    domain: normalized_public_domain_or_null,
    source_type: current_V2_source_type_enum,
    evidence_role_hint: current_V2_evidence_role_enum,
    player_feedback: bool,
    language: "russian"|"non_russian"|"mixed"|"unknown",
    publication_date: "YYYY-MM-DD"|null,
    temporal_kind_hint: "current_sensitive"|"historical"|"durable"|"uncertain"|"identity",
    feedback_surface_mode: "concrete_item_collection"|"search_result_representation"|null,
    exact_product_binding: {basis: current_V2_allowed_basis, appid: string_or_null,
                            title: string_or_null, release_year: int_or_null}|null,
    observed_mode: "opened_source"|"inspected_collection"|"search_representation",
    availability_on_revisit: "not_checked"|"accessible"|"unavailable",
    physical_dedupe_ref: safe_neutral_locator_or_null
  }],
  observed_feedback: [{
    ref: "rfeedback-NNN" (package-local only),
    parent_source_ref: local_source_ref,
    acquisition_mode: "stable_item"|"inspected_collection_item"|"search_result_observation",
    item_locator: safe_public_item_url_or_safe_public_ref_or_null,
    publication_date: "YYYY-MM-DD"|null,
    language: "russian"|"non_russian"|"mixed"|"unknown",
    exact_product_binding_ref: local_source_ref,
    observed: true,
    independent_evidence_note: safe_neutral_note_or_null
  }],
  findings: [{
    ref: "rfinding-NNN", kind: "observation"|"conflict",
    safe_neutral_synthesis: nonempty_nonquoting_string,
    polarity_hint: "positive"|"negative"|"mixed"|"neutral",
    recurrence_basis: safe_neutral_basis_or_null,
    dimension_hints: [one_or_more_of_12_canonical_dimensions],
    support_feedback_refs: [local_feedback_ref],
    contextual_source_refs: [local_source_ref],
    temporal_relevance_hint: "current_sensitive"|"historical"|"durable"|"uncertain",
    uncertainty_note: safe_neutral_note_or_null
  }],
  research_audit: {
    russian_attempt_observed: one_of_current_four_russian_states,
    russian_existence_signal: "confirmed"|"not_observed"|"unresolved",
    dimension_survey: [{dimension: one_of_12_exact_dimensions,
                        finding_refs: [local_finding_ref],
                        investigation_state: "supported"|"not_material"|
                           "routes_exhausted_no_usable_support"|"material_gap"}],
    strengths_investigated: bool, weaknesses_tradeoffs_investigated: bool,
    used_distinct_route_classes: [safe_class_only],
    required_route_state: {identity: state, russian: state,
                           source_diversification: state, temporal: state},
    unresolved_gaps: [{gap_id: local_gap_id,
      field_or_dimension: exact_field_or_dimension,
      reason: "not_observed"|"ambiguous"|"source_unavailable"|"contradictory",
      source_refs: [local_source_ref], material: bool,
      next_materially_distinct_route: safe_class_or_null}],
    completeness: "assembly_ready"|"research_incomplete"|"semantic_exhausted",
    completion_basis: "broad_neutral_picture"|"compact_central_experience"|
                      "sufficient_after_route_exhaustion"|null
  }
}
~~~

**Mandatory semantics:** every observed-feedback record is **directly observed concrete player evidence**, and every finding requiring feedback points to real local records. Search results without concrete player-authored content, query-only hits, Russian UI language and aggregate review counts **cannot** become feedback. Identity-only official/professional sources cannot count as feedback; professional sources cannot substitute for player experience. Original/work release year remains distinct from storefront release year. Stage A must preserve observed facts and explicit unknowns without precomputing canonical freshness. Store **actual factual** date/null per source and per individual observed feedback; unknown date does not make recent support. A source may be a safe parent for a locatorless collection/search item when current strict exact-product rules are met; do not fabricate stable item URLs to ease Stage B. Stage-A source/ref IDs and dedupe refs are author-independent package-local joins, not claim of permanent feedback identity. A safe normalized locator must preserve physical identity and parent/child surface; never normalize two distinct sources into one or count aliases twice.

**Privacy:** persisted package must contain no review/post/search-result raw text, quote, excerpt, copied snippet, username/display name, author/profile URL, Steam/account identity, direct hash of an author id, predictable pseudonym, profile-derived locator, or secret. The only free-text fields are compact neutral observation, source-independent uncertainty and material route descriptions, subject to the *same* forbidden-body/profile checks as the canonical V2. No source raw HTML or original search result cache. Never embed text in public_ref. Acquisition/identity facts are retained without their raw author text.

**Four kinds of data, separated:** (i) Research-reported observation: visited surface, visible exact-product concrete content, safe observed finding, date/language if actually exposed, source/child relationship, actual ambiguities; (ii) GitHub deterministic derivation: exact descriptor fields, hash/sequence, normalized hostname and safe locator checks, physical alias equality where provable, final local ids, bound-language union, summary formula, age classification from recorded dates, timestamps/TTL and content hashes; (iii) Stage-B semantic interpretation: categorical observation type and sentiment, temporal materiality, qualitative recurrence, conflict interpretation, coverage closure, source-role decisions backed by evidence; (iv) **never inferred**: missing publication/release date, missing source/child item identity or appid, unseen feedback, Russian content from locale, independent mentions from duplicates, contradictory-fact resolution without evidence, author identity.

**Package identity:** Research can create exactly one immutable create-only candidate for its GitHub-assigned game/attempt, path proposed:
data/ai_inbox/dossier_research/{snapshot_id}/g{sequence:06d}/{appid}--{assignment_id}.json.
Assignment IDs are predeclared by GitHub (not a worker-chosen alternate retry filename); same path collision => stop. GitHub validates the exact marker-parent lineage and frozen group/index/binding plus package structure, joins, safe locators, identity, privacy, factual date formats and completeness attestation. It records a content-addressed **accepted Stage-A package**: sha256 of canonical JSON (UTF-8, sorted keys, no whitespace) over the whole validated payload; its actual Git blob SHA/path and original assignment/marker are retained. GitHub—not the semantic worker—computes/verifies this hash; never treat a user-supplied claimed hash as authority. Retain an immutable accepted package receipt with original schema/binding, content hash, original parent commit, validation revision, source package path and explicit acceptance kind. Stage-A acceptance means **safe structural evidence transport**, **not Dossier sufficiency or Deep acceptance**. Package status research_incomplete/semantic_exhausted is auditable but not silently promoted to Assembly-ready. Missing mandatory critical coverage remains unfinished even when a JSON object is well formed.

## 3. Stage-B exact authority, gap handling and forbidden detours

**Input**: only GitHub-prepared Assembly assignment bound to an accepted Stage-A content hash and exact frozen source work identity, plus current canonical evidence schema, and prior current-schema compatible per-item Dossier cache for reuse. One game at a time, no global search. Stage B may return a complete V2 Dossier candidate *or* a bound gap/terminal proposal; it never writes directly to canonical Dossier cache/manifest or a final three-game transport path.

**Algorithm / priority order**:
1. Load exact Stage-A package by GitHub-provided immutable hash; validate source/feedback/finding graph, exact identity and semantic contract. Do not re-research by default; do not reinterpret source as new work.
2. Map observed facts into canonical observations/conflicts, record-level language, 12-dimension coverage, strength, recurrence and Russian-attempt state. A GitHub deterministic assembly utility can produce sequence ids, referential joins, language projection, summary, TTL and publication age *from supplied facts only*, then strict-check structure. Stage B may judge semantic categorical choices but cannot invent evidence.
3. For a **specific** missing/invalid field, first reopen **the exact Stage-A safe URL/public_ref, exact product and surface** when available. Preserve the same source-child relationship; reopening parent does not count as rereading a disappeared child. If the original evidence came from a search-result representation, its original visible content remains a truthful Stage-A observation despite subsequent target-page access failure; do not falsely claim it was reopened.
4. If that same source **actually lacks** the required fact, permit a narrowly scoped, materially distinct query solely for an explicit gap_id and exact AppID/title/work-year, e.g. an independently dated exact-app discussion for a material current-state issue. Every new observed source/record follows the *same* schema and privacy rules, with new Stage-B provenance addendum linked to that gap. A query for 'everything about this game', broad reviews, general recrawling, adding unrelated themes or refinding already-supported sources is prohibited.
5. If a missing fact remains unknown, contradictory or materially incomplete, return a **typed unresolved-gap disposition to GitHub**. Never switch null to a guessed date, widen a source language to hide mismatch, mark sparse evidence sufficient, re-label an acquisition mode to evade the parent rule, erase a duplicate while keeping inflated recurrence, or invent an identity corroborator. GitHub decides whether to reopen Research via explicit new assignment/recovery. A structured schema preview can reject before *final* publication only after contract authorization; the existing strict GitHub validator alone remains final acceptance.

**Bounded supplemental rule:** one exact missing field/dimension, source, finding and identity context per explicit gap operation; Stage B must record why the original source was revisited and what concrete fact it lacked. No independent source-budget quota, no fabricated numeric research stop. A need for material multi-dimensional expansion, Russian existence established but no content, substantive conflicting claims or multiple unknown identity/support facts **returns to GitHub-owned Research**, rather than silently making Assembly a second full researcher. Stage B can perform multiple small operations only when each is explicitly bound to a real gap in the frozen package; audit safe gap refs and elapsed phase cost so repeated gap operations do not become hidden broad research.

**Failure matrix:**

| Condition | Safe treatment |
| --- | --- |
| Source later 404/blocked | Keep previously truthfully observed Stage-A safe synthesis if its provenance was valid; do not pretend it is newly re-observed. Missing essential fact => unknown + GitHub research-gap disposition. Runtime access failure is never semantic exhaustion. |
| Date or language cannot be recovered | null/unknown as observed. No recent qualification for unknown child date; no Russian finding from unbound language; if a current-state material gap persists, return to Research / fail closed. |
| Product identity ambiguous/wrong title, year, AppID or DLC | Reject that support. If cannot resolve correct exact work, no complete Dossier and no consuming terminal receipt without the contract's resolved-identity precondition. |
| Stage-A facts contradict | Preserve independently bound conflict with attribution if real; otherwise expose contradiction as unresolved, do not cherry-pick or mechanically relabel. |
| Missing required neutral coverage | If truly nonmaterial classify per existing 12-dimension semantics; otherwise research-gap handoff, not optimistic sufficient/closed. |
| Duplicate or invalid physical source | Canonical alias check; remove duplicate **as evidence**, re-evaluate mention_count, qualitative recurrence, source diversity, Russian and coverage. If this loses material proof, reopen Research. Do not keep fake independent support. |
| Evidence research genuinely exhausted | Emit bounded exact semantic-exhaustion proposal carrying current approved stop class, blocked exact game and route states; GitHub alone validates/consumes a corresponding exact group terminal. A tool stop or malformed transport consumes zero attempts. |

## 4. One GitHub-owned queue, leases, frozen authority, receipts and migration

**No second queue owner.** New GitHub projectors would maintain one extended Dossier progress state derived from the **same immutable canonical current snapshot and predeclared ordered groups**. Stage state per game: research_pending -> research_assigned -> research_package_structurally_accepted -> assembly_pending -> assembly_assigned -> assembly_result_structurally_ready -> final_group_pending -> final_group_accepted (or GitHub-owned failure/recovery). 'Structurally accepted' does not mean semantically sufficient or canonically accepted. Stage markers are internal metadata on GitHub's existing ownership, **not independent production progress**. The existing normal-first-pass and all-accepted counters advance only from current canonical group acceptance/terminal as before.

**GitHub-prepared assignments:**
- Research assignment: exact descriptor + item position + exact frozen relevant contract hashes + single predeclared create-only path + stage attempt/assignment identity + nonce-only marker authority rules. At most one outstanding active Research assignment per exact game binding.
- GitHub validates Stage-A candidate in a serialized control-plane reconcile and stores a content-hash-identified safe immutable package. Only then it projects the exact Assembly assignment bound to *that* hash and its semantic/contract identity. Stage B cannot choose a package from inbox or pick newer mutable main state.
- Assembly assignment: exact Stage-A accepted content hash + source package location/blob + same group/item bindings + stage contract revision + predeclared path for one V2 dossier or typed gap disposition; marker-parent freeze verified exactly. No worker-selected historical authority commit or mutable 'latest' rebind.
- A **single GitHub-owned exclusive claim** per stage/game assignment and generation, acquired atomically under GitHub writer; no two workers get the same active assignment. Stage identity is deterministic based on current valid phase and explicit GitHub authorization. Use one nonce-only run-start marker per invocation with its actual parent as authority. For genuine parallel workers, preallocated non-overlapping work/claim projection must be committed **before** markers; a marker's parent freezes only already-assigned work. Existing marker may not be reused across workers or cross-wired as the other's authority. Do not rely on 'first chat to open index' as a lock.
- Crash, abandoned claim, unusable package, rejected submission and stage recovery are classified **only by GitHub** with explicit outcome and generation-aware reauthorization; never let an expired wall-clock lease alone negate valid frozen work. Late proven-old artifacts may be audited/reused only when validated against their original authority/binding; never mutate a new snapshot group directly or overwrite fresher cache.
- GitHub canonical serialization: each Stage-B V2 dossier is first strict-validated independently in staging. When all exact descriptor items are ready, GitHub constructs the exact unmodified buffered 3-game candidate from the frozen descriptor (items and hashes byte-for-byte) and calls **existing** scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact and strict.py::validate_dossier_strict + compact provenance validation; the existing serialized ingest then publishes canonical cache/group state and Deep recomputation. Staging is not a shortcut to canonical acceptance. Existing current-snapshot validator is the final gate. Group terminal/no-dossier state retains existing exact blocked_game, resolved identity, genuinely exhausted route proof, run-start authority and GitHub attempt-consumption semantics.
- The new Research/Assembly envelope/receipt need separate namespaces and deterministic paths so they never collide with currently active data/ai_inbox/taste_steam_review_dossiers paths. Stage receipts: created/accepted/rejected-invalid/research-incomplete/assembly-gap/runtime-blocked, carrying assignment, source-hash, contract revisions and no raw data. None counts as a normal-first-pass semantic exhaustion attempt or current Dossier accepted group. Only existing GitHub-validated exact group semantic terminal consumes the single no-dossier first-pass attempt. Invalid transport has zero consumption. No automatic retry loop.
- Any write touching Dossier manifest/projection, pending/claim/staged/accepted package state, final group outcome and Deep eligibility must participate in the existing **taste-steam-review-dossier-canonical-writer / cancel-in-progress:false** serialization and clean atomic staging. Upstream candidate push = advisory wake-up; durable GitHub state, not an event order, is authoritative. Idempotent reconcile on rerun.

**Snapshot/TTL/rollover:** bind packages to original marker-parent group and semantic revision; new daily snapshot re-prepares scope through GitHub. A compatible old Stage-A package may be *considered* as evidence reuse for exactly the same AppID/work-year/title and still-safe source material only after explicit GitHub binding/freshness and semantic coverage check. Current-state-sensitive items need refreshed dated evidence. Neither stage can transplant old group sequence/hash into new. Current group accepted only by exact current candidate or all-item current-compatible strictly validated canonical cache reconciliation. Respect existing cache precedence and no stale overwrite. Frozen old Stage-B result can populate neutral cache only via the same verified-compatibility rule as existing old Dossier candidates; stage A alone never populates canonical Dossier cache.

**Compatibility:** pre-cutover existing strict accepted V2 Dossiers and existing Deep references remain unchanged. Stage A is not a replacement for accepted Dossier evidence, and Deep sees nothing from staging. Worker prompt hash participates in V2 evidence binding: new Stage B prompt **cannot silently impersonate** the old worker-prompt hash or migrate old candidates. Design an explicit GitHub contract-version transition with validated equivalence/TTL reuse when provable, otherwise normal targeted refresh/rebuild. Keep old one-stage producer and old cache valid under old production authority until opt-in cutover; don't rewrite accepted historical records or bypass Deep's exact accepted-Dossier eligibility. An unproven semantic binding migration must fail closed.

## 5. Pipeline and concurrency model

**Choice: preserve group-of-3 atomic canonical acceptance, add per-game A/B staging.** Changing the accepted group plan now would invalidate immutable group hashes, rollover logic and recovery semantics and has not been proven beneficial. Per-game packages avoid repeatedly researching unrelated good siblings after one game's missing field. The final group cannot be accepted or exposed to Deep until all its ordered members pass identical validation. If a true semantic exhaustion is reached for one game, GitHub's currently authorized group terminal semantics remain group-bound; do not silently advance a partial accepted group or spend a per-game attempt that current contracts do not define. Other staged per-game evidence may remain reusable under exact compatibility/retention checks; a failure in group N must not block processing of independently assigned N+1.

**Launch shape after future authorization (not now):** one Research lane and one Assembly lane, each consuming only disjoint GitHub-frozen exact work. Research can work on group N+1 when Assembly has an accepted Stage-A package for N. The next assembled result may not be visible to Assembly in its current frozen invocation until a new GitHub assignment/marker; never spin/poll inside the worker. GitHub can predeclare multiple ready independent assignments in each frozen projection and workers traverse them in that order without waiting for sibling ingest, analogous to existing Dossier. Assembly follows GitHub's ordered *eligible* assembly assignments, not worker-chosen numerical offsets. Research can finish groups out of order; Stage-A packages become available independently after validation. Final accepted Dossier groups need not wait for earlier missing groups: current non-blocking per-group acceptance already permits this; within a group, exact dossier order is immutable.

**In-flight safety envelope for initial activation:** one active Research group claim and one active Assembly group claim, each containing at most three games; thus at most six separately staged game identities across two overlapping lanes (some can be shared across phase boundary without duplicating active ownership). Pending accepted packages beyond this envelope are durable GitHub state, not worker-owned leases. Start with this deliberately small limit; measure claim contention, arrival rate, stale time and storage before raising it. A frozen invocation can traverse its own predeclared groups in order; do not assign the same item to a second concurrent worker or allow accidental duplication from stale index. Failures are scoped per game during staging and per exact group at final classification, not a global crawl stop. No new throughput quota, daily cap or per-game search/page cap.

**Deadlock control:** Research never waits for Assembly to ingest; Assembly never waits on missing earlier Research group when another fully prepared exact assignment exists; both stop cleanly at no-authorized-ready-work and rely on future GitHub projection. Claim expiry/cancellation alone is not authority to publish a competing result. Terminal/gap state is durable and requires GitHub-controlled explicit classification.

## 6. Validators and quality proof

Keep **the original strict V2 validator unweakened and final**:
- New Stage-A deterministic safe-package validator: exact frozen assignment/marker-parent lineage, content hash, whitelist fields, privacy, actual date formats, allowed acquisition modes and parent/source relationships, local refs, same-source dedupe, observed-content flag, identity evidence, exact Russian gates and 12-dimension audit *presence*. It is **not** an oracle that evidence is truly sufficient.
- New Stage-B deterministic preflight inside GitHub (rather than a prohibited Scheduled-worker Python command): from accepted Stage-A facts derive exact local ids, canonical ordered language union (russian, non_russian, unknown), source domain, summary and TTL; dry-run the same strict Dossier validation and privacy check. No forgiving repair, field invention, hidden auto-retry, acceptance or direct cache write. This is an explicitly proposed future contract amendment; current prepublication policy still says not required for scheduled worker.
- GitHub final validator: unchanged validate_buffer_artifact -> validate_dossiers_against_expected_items -> validate_dossier_strict + compact provenance, then existing canonical writer ingest/reconcile. Different validation stages reject early, but **only the final one accepts**.

**Offline real-artifact parity (no synthetic production data):**
1. Replay actual previously accepted V2 Dossiers/candidates and rejected transports in isolated fixtures; include audited current first-10 groups and rejection types: 11 mode/parent, 5 schema/locator, 5 joins/languages, 3 duplicates, 5 temporal/coverage, 1 privacy, 1 product binding (31 current rejection events). Include 45 historical differently-classified failures without combining denominators.
2. Diverse exact real games: sparse and rich player sources, Russian present/missing/existence-only, title/year ambiguity, DLC vs base, duplicate alias/thread, searched result visible but target later blocked, mixed child dates/languages, technical current-state vs durable mechanics, strong contradictions and negative feedback. Check both source coverage and downstream meaningfulness by human/manual semantic review; neither a syntax pass nor a larger accepted count proves quality.
3. Compare A->B final canonical output vs accepted old-path V2 under identical exact work and unchanged strict validator: all 12 dimensions classified correctly, positive/negative coverage neither lost nor manufactured, same or stronger independent physical feedback support, no duplicate inflation, no fabricated new date/source/identity, Russian attempt correct and attributable, exact parent-child relationship, validated language union, temporal recent/older/unknown from actual child dates, complete provenance and no privacy regression.
4. Preserve **negative controls**: previously rejected invalid source/mode/identity/privacy/dated-current cases remain rejected unless *new actually observed* evidence repairs the missing fact. Never make them pass merely by relabeling. Per-group atomicity, rollover isolation, zero-attempt invalid transport, frozen marker-parent authority, nonblocking unrelated accepted groups and idempotent replay must all pass.
5. Check Deep through exact accepted Dossier handoff (scripts/build_progressive_pass2_work.py): unchanged V2 schema, same/better usable neutral evidence and conflicts, no new Fast prerequisite, no new personal profiling during Research/Assembly, no Deep score/rank/UI changes.
6. Shadow on real *read-only / non-active* source work with separated artifact namespaces, fail closed and no publication, then small controlled operator-authorized canary; measure accepted output **and independent coverage quality** by cohort. Compare a full representative scheduling window, not isolated successful marker windows.

**Never relax** existing strict provenance, TASTE-014 distinct-route semantics, TASTE-015 sufficiency, TASTE-016 actually observed feedback, TASTE-017 dates, source/child identity, Russian language gates or privacy. Assembly gap research must not become a second search sweep.

## 7. Throughput model (conditional, not a production promise)

Accepted prior diagnostic (measured 2026-10-08, mutable state observation): 2,134 dossiers / 712 groups of three prepared; 10 accepted groups, 702 pending; 27 retryable rejected transports before those ten accepted (27/37 = 73% outcome-event rejections, **not** 73% of games); 16–19 of 31 all-current retry events are plausible mechanical prevention candidates, *not* safely repairable facts. Marker-to-result span for those ten accepted groups 5.7–18.3 min, mean ~12.4 min, includes multi-group cumulative windows, research/reuse/transport and cannot be interpreted as isolated per-game effort. Accepted candidate commit-to-audit 13–52 seconds (~21 sec mean), and calendar 0.66 accepted dossiers/hour includes idle/manual episodes: no valid sustainable baseline. Prior report's conditional quality-preserving target was ~1.4–1.8x active effort (optimistic up to 2.4x) with **zero guaranteed** gain absent measurement.

Let R = safe research active time per comparable group, A = correct assembly active time, G = current GitHub final transport/validation, H = *new* Stage-A ingest/handoff/claim/Stage-B preflight overhead, E = avoidable historical reject/rework effort under old path, E2 = residual rejection/rework under new path. For warmed, steady-state dual-lane pipeline:

- Old per-group active cost approximately R + A + G + E.
- New *first-item/group latency* R + A + G + H + E2; **may be slower** even if throughput increases.
- New steady-state bottleneck cost approximately max(R, A, G) + H + E2 when lanes truly overlap and are fed by ready assignments.
- Modeled throughput gain approximately (R + A + G + E) / (max(R,A,G) + H + E2). No claim of perfect overlap during gaps, cadence idle, or stage imbalance. New H must be instrumented, not assumed negligible.

**Illustration only:** with hypothetical R=8 min, A=4 min, G=0.35 min, H=0.5 min, and no retries, overlap is 12.35 / 8.5 = **1.45x** throughput while latency rises from 12.35 to 12.85 min. The source diagnostic cannot measure R/A split or actual H. When R dominates, adding Assembly lane gives little gain; when Assembly is costly but mostly deterministic, overlap and early rejection prevention matter. When overhead plus repeated Stage-B search exceeds removed serialization/rework, it becomes slower; an example R=10, A=1, G=0.35, H=2.5 with no reject saving yields 11.35/12.85 = **0.88x**.

**Evaluation bands for this proposed architecture, not measured forecasts:**
- **Conservative:** 0.9–1.2x (no useful overlap, handoff cost offsets fewer rejects; genuine downside possible).
- **Realistic design target, conditional on full quality and sustained overlapping work:** **1.25–1.65x** accepted, equivalent-quality dossiers per active worker opportunity.
- **Optimistic:** 1.7–2.1x if the two phases balance and a large fraction of mechanical rejections disappears without repeated research; above ~2.1x remains speculative and the prior report's 2.4x optimistic ceiling is not a commitment.
- **Worst-case** at materially high Stage-A/Stage-B transfer overhead, access-lost sources or research twice: **<1x**, potentially around 0.6–0.9x on a bad workload; not an observed measurement.

Do not multiply 'pipeline parallelism' by prior 'rejection prevention' as independent gains: they address overlapping assembly/rework. Measure R, A, staged idle, supplemental opens/searches, invalid transport reason, GH handoff latency, end-to-end age, final validator acceptance and a blinded coverage/Deep-usability quality score by comparable exact real cohorts before stating a production benefit. A second semantic worker can increase total compute/tool resource consumption even if wall-clock throughput improves. No new hourly schedule or cost assumption is authorized.

## 8. Bounded migration / Director implementation split

**P1 — contract/schema-only PR:** amend ownership/runtime/evidence/persistence bridge deliberately; add Research V1 schema, Stage-B assignment/receipt schema, status/claim/frozen-identity/rollover contracts, exact allowed web-gap rules. Define inactive feature gate and old prompt/hash compatibility. No activation.
**P2 — GitHub deterministic helpers/validators PR:** Stage-A whitelist/privacy/reference/hash validator, GitHub assignment projection and exclusive claims, safe mechanical assembly, Stage-B preflight and staged per-game validation, exact terminal bridge and atomic writer/coalescing safety. Real corpus unit tests, fail closed. No semantic worker yet.
**P3 — Research semantic prompt/transport PR:** exact observed-evidence package, 12-dimension audit, Russian, temporal, neutral synthesis, create-only output, run-start authority and privacy; inactive.
**P4 — Assembly semantic prompt/transport PR:** accepted immutable package only, exact-source-first/narrow-gap, typed return and V2 output; inactive. Keep the old one-stage prompt live.
**P5 — real-artifact offline parity PR:** accepted/rejected corpus, stage A/B correctness, no silent repair, group-of-three and rollover tests; measured failure taxonomy/phase timing.
**P6 — inactive dual-stage shadow PR:** separately stored no-publish observational run; compare quality, throughput and completion receipts without touching canonical cache or Deep.
**P7 — explicitly authorized controlled cutover PR:** only after Director quality/measurement acceptance and independent orchestration permission, activate single GitHub control-plane projections, update external operator-owned task configuration only in a separately authorized operation, verify writer/ingest/Deep end-to-end; rollback gate to old one-stage if parity fails.
**P8 — retirement:** remove old one-stage transport only after stable live canary, accepted-cache compatibility proof, no pending frozen old transport and complete recovery/rollback plan.

**Dependencies:** P1 -> P2 -> (P3 and P4 may work independently once wire contracts freeze) -> P5 -> P6 -> P7 -> P8. P2 touches shared GitHub owner/writer and must be serialized with any concurrent Dossier/Deep structural work. P3/P4 must not alter the current production one-stage semantic contract until cutover. No manual backlog repair or Synthetic production data.

## 9. Final exact deliverables and recommendation for Director

1. **Exact Stage-A package:** section 2, DOSSIER-RESEARCH-PACKAGE-V1; per-game, fully frozen descriptor/marker binding, observed safe source/feedback/neutral findings/12-dimension survey, explicit unknowns and route gaps, privacy-safe refs; GitHub accepted immutable hash/receipt before Assembly.
2. **Exact Stage-B rules:** section 3: accepted hash only -> canonical association/derivation -> re-open exact source on one named gap -> narrow exact-product lookup only if actually missing -> unresolved typed GitHub handoff, no broad rerun or invented facts; unchanged V2 Dossier shape.
3. **GitHub queue/ownership:** section 4: one frozen per-snapshot ordered control plane, GitHub-issued stage assignments/claims, versioned create-only paths, exclusive retry/recovery, GitHub-only acceptance, original marker-parent authority, immutable packages, cached-compatibility/rollover and canonical writer.
4. **Pipeline/concurrency:** section 5: retain group-of-three atomic final validation, independent per-game staging, one Research and one Assembly group active at a time initially, disjoint GitHub assignments, nonblocking unrelated groups, final accepted order within group preserved.
5. **Expected speedup:** section 7: no measured gain; conditional conservative 0.9–1.2x, realistic 1.25–1.65x, optimistic 1.7–2.1x, possible regression below 1x, one-lane latency can rise.
6. **Quality-preservation proof:** section 6: unchanged validator + real accepted/rejected corpus, 12 neutral dimensions, exact Russian/product/dated/physical-source privacy and provenance, per-group recovery/rollover and Deep-usefulness parity before activation.
7. **Recommended Director tasks:** P1 contract, P2 GitHub validators/writer, P3 Research, P4 Assembly, P5 real parity, P6 inactive shadow, P7 explicit controlled cutover, P8 retirement; no implementation nor scheduler action in this PR.

**Closeout:** START and architecture preflight completed; deliverable is a report-only PR; no tests or runtime proof asserted for a design-only change. This proposal requires explicit Director contract approval, subsequent implementations and real-evidence quality proof. Other active CURRENT_TASK.md work is not modified to avoid concurrent-worker lost updates; this report is the bounded durable handoff. No Scheduled Tasks, Deep/Fast/ranking/Steam/UI, production data or canonical Dossier contract altered.
