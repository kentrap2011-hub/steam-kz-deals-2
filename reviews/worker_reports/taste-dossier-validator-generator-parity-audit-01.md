# Taste dossier validator ↔ generator parity audit 01

## 1. Task / repo / mode
- Task: `WORKER_TASK_TASTE_DOSSIER_VALIDATOR_GENERATOR_PARITY_AUDIT_01.md`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Audited main SHA: `247f2b15bafd495dc44be3aebf734bb22d5f613b`.
- Mode: READ-ONLY / RECON.

## 2. Scope and exclusions
Compared only current-main authoritative dossier acceptance against the active generator-facing schema, web-evidence contract and Scheduled-worker prompt, with dossier/execution ownership contracts used only to classify responsibility.

Excluded: retrieval-strategy invention, new sources, scheduler/platform reliability, retry/queue/checkpoint redesign, ranking/UI/purchase logic, performance/code-quality review, Git history, and speculative future cases.

No implementation, production candidate, inbox/quarantine, progress, workflow, Scheduled Task or runtime state was changed.

## 3. Sources of truth checked
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `CURRENT_TASK.md`
- Taste dossier route in `PROJECT_ROUTES.md`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `scripts/taste_steam_review_dossier_strict.py`
- directly called acceptance helpers:
  - `scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact`
  - `scripts/taste_steam_review_dossier_compact_provenance.py::validate_compact_provenance`
  - `scripts/taste_steam_review_dossier.py::_validate_no_raw_or_personal_payload`
- closed control example: `reviews/worker_reports/taste-dossier-identity-provenance-generation-fix-01.md`

## 4. Parity method
For each substantive strict-validator rule, checked:
1. whether the rule is applied to worker-generated dossier data;
2. whether it belongs to Scheduled-worker generation rather than GitHub-only control plane/transport defense;
3. whether schema/evidence contract/prompt state the same invariant strongly enough;
4. whether a compact, otherwise valid-looking worker output can satisfy the generator-facing text yet be rejected by the canonical validator.

Only rules satisfying all task finding criteria are reported as confirmed gaps.

## 5. Compact substantive parity matrix

| Rule class | Classification | Result |
|---|---|---|
| Game identity / exact product binding | aligned | Exact descriptor title/appid, release year, appid corroborator, identity source and exact-product Steam appid/container binding are generator-facing. |
| Identity-role provenance control case | aligned | Current schema + prompt explicitly require at least one `evidence_role:"identity"` source in `identity_source_ids`; ordinary feedback must not masquerade as identity provenance. |
| Source role / player-vs-context semantics | aligned | Player source types, context-only types, official/professional boundaries and `player_feedback` semantics are expressed. |
| Source locator serialization | confirmed_parity_gap | Strict requires exactly one source `url` or `public_ref`, and an URL must be HTTPS with `domain` equal to its normalized host; generator-facing contracts do not encode all of these source-level requirements. |
| Player-feedback record identity | aligned | Stable vs transient fallback modes, item-level locator requirements, local IDs and fallback privacy are explicit. |
| Parent/child physical binding and aliasing | aligned | Reddit containment, Steam review/discussion surface binding, exact appid/container matching and alias rules are generator-facing. |
| Source / feedback language containment | aligned | Russian/non-Russian child-parent containment is explicit. |
| Observation evidence-language derivation | aligned | Exact ordered projection from bound feedback records is explicit in schema/evidence contract/prompt. |
| mention_count and recurrence | aligned | Exact bound-record count and anecdotal/limited/moderate/strong thresholds are explicit. |
| Stable vs fallback recurrence strength | aligned | Moderate/strong require stable-locator thresholds; fallback support is capped at limited. |
| Russian attempt states | aligned | Only `found_and_used` and `searched_no_existence_signal` are complete-dossier terminal states; unresolved existence/access states fail closed. |
| Source mix / physical diversity | confirmed_parity_gap | Physical used-source counting is explicit, but strict additionally requires `single_source_reason:null` whenever `source_mix_status:"multi_source"`; generator-facing layers do not state that null invariant. |
| Current / historical / durable / uncertain support | aligned | Current requires recent current-state support; historical requires historical + recent current-state check; durable requires durable-trait support. |
| Freshness / dated recency coherence | aligned | <=365 recent / >365 older, old-child parent coherence and undated handling are explicit. Materially future publication-date rejection is treated as defensive chronology sanity, not a generator parity finding. |
| Privacy / forbidden author identity | aligned | Profile URLs, author identity, hashes/pseudonyms, content-like refs and raw bodies are explicitly forbidden. |
| Source type / player-feedback role restrictions | aligned except Store-parent subtype below | General player/context mapping is aligned. |
| Professional / official context boundaries | aligned | Context cannot become player-feedback mentions or recurrence support. |
| Steam Store exact-app fallback parent | confirmed_parity_gap | Strict permits the Store fallback parent only with `source_type:"steam_reviews"` or `"store_user_reviews"`; prompt says these are only “normally” used and machine contracts do not state the exclusive set. |
| Summary derivation | aligned | Canonical summary string is deterministic from observation count and is explicitly generator-facing. |
| Duplicate observations / conflicts / physical items | aligned | Exact duplicates and physical aliases are forbidden in generator-facing rules. |
| Contract/binding compatibility fields | aligned | Exact content-complete binding copy, descriptor/index liveness, title/appid/TTL and complete ordered group serialization are explicit. |
| Malformed/duplicate transport artifacts, canonical prefix/progress interpretation | validator_only_by_design | GitHub control-plane defense; Scheduled worker must not emulate or own these checks. |

## 6. Confirmed parity gaps

### PARITY-01 — source locator serialization is under-specified
**Exact validator behavior**
- every provenance source must contain exactly one of `url` or `public_ref`;
- if `url` is used, it must be a public HTTPS URL;
- source `domain` must equal the normalized URL hostname.

**Generator-facing omission/ambiguity**
- schema lists `url` and `public_ref` as allowed source fields but has no source-level exact-one locator invariant;
- schema/evidence contract do not state the general HTTPS + domain/URL-host equality invariant;
- prompt says “URL or stable public reference” but does not make the full strict serialization rule mechanical.

**Minimal valid-looking rejected shapes**
- source carries both a safe URL and a neutral `public_ref`;
- or source uses `domain:"steampowered.com"` with `url:"https://store.steampowered.com/app/1000010/"`;
- or a public source URL is serialized as `http://...`.

All can otherwise satisfy source role/language/freshness semantics but strict acceptance rejects them.

**Production consequence:** `conditional_blocker`.

**Smallest likely repo-owned fix surface:** schema only (make source locator cardinality, HTTPS and normalized host equality explicit machine invariants); tests/fixtures should cover the strict shapes during implementation.

### PARITY-02 — multi-source reason nullability is missing from generator contract
**Exact validator behavior**
When `evidence.source_mix_status == "multi_source"`, strict requires at least two distinct physical used player-feedback sources **and** `evidence.single_source_reason is null`.

**Generator-facing omission/ambiguity**
Schema/evidence contract state that `single_source_only` requires a compact reason and that `multi_source` requires >=2 physical used sources, but do not state the converse null requirement. The prompt likewise explains when to provide a single-source reason but never explicitly says to serialize `null` for multi-source dossiers.

**Minimal valid-looking rejected shape**
```json
{
  "source_mix_status": "multi_source",
  "single_source_reason": "Two independent player-feedback sources were used."
}
```
with two valid physical used sources.

**Production consequence:** `conditional_blocker`.

**Smallest likely repo-owned fix surface:** schema only (explicit `multi_source_requires_single_source_reason_null:true`); add a regression fixture during implementation.

### PARITY-03 — Steam Store fallback-parent source type is weaker generator-side
**Exact validator behavior**
An exact Steam Store `/app/{appid}/` source used as `feedback_surface_mode:"concrete_item_collection"` with `player_feedback:true` is accepted only when `source_type` is `steam_reviews` or `store_user_reviews`.

**Generator-facing omission/ambiguity**
The prompt says the Store fallback parent uses the normal player-feedback surface classification and **normally** `steam_reviews` or `store_user_reviews`, which leaves other player-feedback enum values semantically possible. Schema/evidence contract describe the Store-parent exception but do not encode the exclusive source-type set.

**Minimal valid-looking rejected shape**
A correct exact-app Store parent with:
```json
{
  "source_type": "other_player_feedback",
  "player_feedback": true,
  "feedback_surface_mode": "concrete_item_collection"
}
```
plus otherwise valid transient fallback child records.

**Production consequence:** `conditional_blocker`.

**Smallest likely repo-owned fix surface:** evidence contract clarification (make the exclusive Store-parent source-type set canonical); a focused regression should accompany implementation.

## 7. Validator-only-by-design items worth noting
Not findings:
- malformed/alternate/duplicate buffered artifact filenames and maximal-contiguous-prefix/progress handling are GitHub-owned transport/control-plane checks;
- basic malformed JSON/type/range defenses and compact-string length guards do not need a second handwritten Scheduled-worker validator;
- source/feedback publication dates materially after dossier generation are rejected as defensive chronology sanity; generator is already instructed to serialize actual publication dates and no reasonable positive-evidence semantics depend on future-dated player feedback;
- acceptance-time expiry/future-generation checks are canonical ingest safety; the worker-facing timestamp contract already states expiry derivation and future skew.

## 8. Identity-provenance control case status
`aligned`.

The previously closed defect is not reopened. Current main explicitly requires:
- at least one exact-product provenance source with `evidence_role:"identity"`;
- at least one such source referenced by `game_identity.identity_source_ids`;
- exact descriptor appid corroboration;
- separation of identity-only metadata from player-feedback mention, Russian-use, recurrence and source-diversity support.

The current strict reject condition and generator-facing instructions now match.

## 9. Unclear items
None. No rule class requires additional history, production examples or web retrieval to classify this current-main parity pass.

## 10. Changes
`none` except this report.

No prompt, schema, evidence contract, validator, runtime script, workflow, Scheduled Task, production candidate, inbox/quarantine, canonical progress or recovery state was changed. `CURRENT_TASK.md` was intentionally not rewritten because the task explicitly permits read-only bookkeeping to remain inside the report when another active handoff exists.

## 11. Validation of findings
- Every confirmed gap is tied to a concrete current-main validator requirement.
- Each gap shows the exact generator-facing omission/ambiguity and a compact valid-looking rejected shape.
- GitHub-only transport/recovery/progress checks were excluded.
- Identity provenance is confirmed aligned and not reported as a new gap.
- No retrieval/source/game hypothesis is promoted to a finding.
- No speculative “might fail someday” items are included.

## 12. Unresolved
No audit uncertainty remains. The three confirmed parity gaps are implementation work, not unresolved recon.

## 13. Status
`complete_confirmed_parity_gaps`

## 14. Exactly one recommended next step
Create one bounded IMPLEMENT task covering only PARITY-01..PARITY-03: align generator-facing contracts to the existing strict validator and add focused regression fixtures, without changing validator semantics, ownership, queue/retry/checkpoint architecture or production state.

## 15. Efficiency / reusable lesson
The fast reusable parity route is: enumerate substantive strict reject conditions by worker-owned data class, then require a matching machine invariant in schema/evidence contract or an unambiguous prompt instruction. Low-level transport defenses stay validator-only; worker-generated serialization rules that can plausibly produce a valid-looking rejected dossier must be mirrored generator-side.
