# Taste Dossier Contract Contradiction Audit 01

## 1. Task / repo / mode

- Task: `taste-dossier-contract-contradiction-audit-01`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base / source of truth: `main`
- Mode: `READ-ONLY DIAGNOSTIC`
- Audit baseline: current `main` read during this task on 2026-09-18.
- Repository writes performed by this task: this durable report only.
- No config/schema/prompt/script/workflow/test was edited; no PR was created; no Scheduled Task was run.

Canonical baseline at the final pre-report recheck:
- evidence contract revision: `transient-author-dedupe-fallback-2026-09-18`;
- worker schema revision: `transient-author-dedupe-fallback-2026-09-18`;
- worker prompt revision: `web-evidence-v2-transient-author-fallback-v1`;
- active work snapshot: `99c3601ff39f62af05be2b529854516dcd7e9ba3570948aa6e8c257d62bba8b8`;
- prepared/completed/remaining: `730 / 0 / 730`;
- group size: `3`;
- current first group `g000001`: Crown Trick (`1000010`), Hellish Quart (`1000360`), Tetris® Effect: Connected (`1003590`).

## 2. Audit boundaries

The audit was limited to the active Taste Steam Review Dossier evidence pipeline and the interaction between worker-facing evidence semantics, V2 schema, web-evidence contract, strict validator, compact provenance, content-complete compatibility binding and buffered candidate validation.

Reviewed canonical/active paths included:
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `scripts/taste_steam_review_dossier_strict.py`;
- `scripts/taste_steam_review_dossier_compact_provenance.py`;
- `scripts/taste_steam_review_dossier_buffered.py`;
- `scripts/taste_steam_review_dossier_prepublication.py`;
- `scripts/build_taste_steam_review_dossier_work.py`;
- relevant TASTE decisions and the recent implementation reports required by the task.

Ranking, pricing, package economics, giveaway, UI, production scheduling/retry architecture and unrelated Taste Semantic Producer logic were not audited. Story-DLC policy was read only far enough to confirm the current dossier identity/scope and the current `g000001`.

## 3. Current canonical evidence modes reviewed

The audit traced the required active evidence modes through schema/contract/prompt/strict validation/provenance/binding:

1. normal stable-locator player feedback;
2. transient-author fallback on a non-Steam collection parent;
3. transient-author fallback on an exact-product Steam Store parent as intended by Chat 1;
4. direct profile-scoped feedback inspected transiently with profile identity omitted from persistence;
5. mixed stable + fallback evidence;
6. Russian `found_and_used` via fallback;
7. old/recent feedback split;
8. exact product identity where a Steam URL exposes appid;
9. one parent source containing multiple concrete child items;
10. duplicate/alias physical feedback seen through multiple surfaces.

## 4. Known Chat 1 contradiction excluded

The known Crown Trick contradiction is deliberately not counted below.

That already-assigned issue is the mismatch where concrete individual review cards are visible on the exact-product Steam Store app page, while the older broad Store-page source restriction prevents that page from serving the narrowly intended parent collection surface for a `transient_author_deduped` child record. The intended rule remains that the Store page itself, aggregate counts, ratings and language totals are not feedback records or mentions.

At the final pre-report recheck, `reviews/worker_reports/taste-dossier-steam-store-review-card-parent-fix-01.md` was not yet present on `main`. This audit therefore treats the Chat 1 fix as concurrent work and does not duplicate it.

## 5. Rule-interaction matrix summary

| Evidence mode | Schema / contract / prompt | Strict / provenance behavior | Audit result |
|---|---|---|---|
| Stable locator | Stable item identity, physical parent, exact-product identity required | Item locator and surface class enforced; Steam child exact appid/container is not fully bound | **CONTRA-01** |
| Non-Steam transient fallback | Concrete collection parent + local opaque child + no profile persistence | Matches intended fallback rules | No contradiction |
| Steam Store transient fallback | Narrow parent-only exception is intended | Known concurrent Chat 1 issue | Excluded |
| Profile item inspected transiently | Identity may be read only in memory; profile URL must not persist | Profile URLs are rejected; safe fallback parent is allowed | No contradiction |
| Mixed stable + fallback | Total mentions count both; moderate/strong use stable-only thresholds | Stable thresholds and total mention count match | No strength contradiction; **CONTRA-02** can affect internal IDs |
| Russian fallback | Valid Russian/mixed fallback may satisfy `found_and_used` | Bidirectional Russian gate uses bound record languages | No contradiction |
| Old/recent split | Known old child cannot inherit recent parent; historical needs current check | Mechanical 365-day and old-child guards match | No contradiction |
| Exact product/appid | Exposed Steam appid must bind to exact dossier product | Parent source appid checked; stable child URL appid is not | **CONTRA-01** |
| Multiple children under parent | Distinct children allowed only when physically contained; host alone is insufficient | Reddit thread containment is enforced; Steam containment stops at surface class | **CONTRA-01** |
| Duplicate/alias surfaces | Canonical physical item/source aliases must not inflate support | URL/ref normalization and duplicate identity rejection match | No additional contradiction |
| Bound-record language projection | `evidence_languages` must equal exact ordered projection of bound record languages | Only partial positive-support checks are enforced | **CONTRA-03** |
| Compact privacy | Persisted provenance must contain no author/profile identity | URL/public_ref privacy enforced, but stable internal IDs are unrestricted strings | **CONTRA-02** |
| Compatibility / buffer | Content-complete hashes require fresh compatible snapshot; buffered validator is canonical | Binding hashes + same-day compatibility + shared buffered validator align | No contradiction |

## 6. Confirmed findings, ordered by production impact

### CONTRA-01 — Stable Steam child evidence is not fully bound to the exact product/parent surface

**Plain-language description.**  
The active contract says a stable player-feedback child must belong to the exact product and physical parent surface, and host match alone is insufficient. The strict validator checks exposed Steam appid only on the parent source URL. A stable child Steam URL is checked for host, item-level shape and broad review-vs-discussion surface class, but its exposed appid and resolvable Steam container/thread are not compared to the dossier/parent.

**Exact intended valid/invalid case.**  
Valid: dossier `appid=1000360`, exact-product Steam parent for `1000360`, and a stable child item belonging to that same product/parent surface.  
Invalid but currently structurally passable: the parent source exposes the correct `/app/1000360/`, while a stable child URL on the same Steam host and same broad surface class exposes another `/app/{different_appid}/...`. Likewise, a thread-specific Steam parent and a child from a different resolvable thread can evade containment if both resolve to the same broad `steam_discussion` class.

**Rule/component A.**
- `config/taste_steam_review_dossier_web_evidence_contract.json -> identity.steam_player_feedback_url_appid_must_match_exact_dossier_appid_when_exposed = true`;
- `parent_item_binding.rule`: every feedback record must resolve to the physical surface represented by its parent and host match alone is insufficient;
- worker prompt stable path: existing parent/child and exact-product rules remain unchanged.

**Rule/component B.**
- `scripts/taste_steam_review_dossier_strict.py::_validate_source` applies `_steam_appid_from_url` to the parent source;
- `_validate_feedback_record` does not apply the same exact-appid guard to a stable child URL;
- `_validate_parent_item_relationship` reconciles Steam review/discussion surface class but does not compare child appid or a resolvable Steam parent/thread container.

**Why they conflict.**  
The worker-facing canonical contract defines exact product + physical parent containment for the feedback item, while canonical strict acceptance can accept a child whose own locator proves a different product/container.

**Production consequence.**  
Wrong-product or wrong-parent Steam feedback can be canonically accepted and then counted as a real mention. That can contaminate observation/conflict support and recurrence strength while appearing structurally valid.

**Severity:** `silent_semantic_error`

**Can current `g000001` hit it?**  
Yes. Any of the three current games can use stable Steam Community/review/discussion evidence. The issue is structurally reachable for the active group; this audit does not claim that the current live worker has already emitted such a mismatched child.

**Minimal fix direction — design only.**  
For stable Steam child locators, derive the exposed appid/container identity when deterministically available and require it to match the exact dossier appid and the resolvable parent surface/container, analogous to the existing Reddit containment rule. Keep unknown/unresolvable generic surfaces on the existing fail-closed/known behavior rather than inventing fuzzy identity.

**Would this weaken an intentional guard?**  
No. It strengthens the already-declared exact-product and physical-provenance guards.

---

### CONTRA-02 — Author identity can leak through stable `source_id` / `feedback_id` despite the compact privacy contract

**Plain-language description.**  
The active compact-provenance contract says persisted author/profile identity is forbidden, and the prompt says usernames/account/profile identity must never be persisted. The strict/compact validators enforce that for URLs, public refs and transient fallback IDs, but ordinary stable-record `source_id` and `feedback_id` values remain arbitrary 1–80 character strings. A worker-created stable ID can therefore contain a username, SteamID/account id or other author-derived token and still pass canonical validation.

**Exact intended valid/invalid case.**  
Valid: opaque dossier-local join IDs such as neutral local tokens, while the stable physical item identity lives in the safe item URL/`public_ref`.  
Invalid but currently structurally passable: a stable record with an otherwise valid neutral item locator but `feedback_id:"steamid:76561198442230810"`, or a stable player source with an author-derived `source_id`, with all references updated consistently.

**Rule/component A.**
- `compact_provenance.author_identity_allowed = false`;
- `compact_provenance.rule`: persist only non-identifying locator/provenance metadata;
- worker prompt: never persist usernames/display names/author attribution/author profiles and do not place transient author identity in `source_id` or `feedback_id`;
- fallback rules already prove the intended privacy model by forcing local `source-NNN` / `fallback-NNN` tokens.

**Rule/component B.**
- `scripts/taste_steam_review_dossier_strict.py::_validate_source` validates stable `source_id` only by type/length/uniqueness;
- `_validate_feedback_record` validates ordinary stable `feedback_id` only by type/length/uniqueness;
- `scripts/taste_steam_review_dossier_compact_provenance.py` inspects `url` and `public_ref`, not the internal ID values;
- the fallback-wide author scan checks forbidden field names/profile URLs, not arbitrary author identity embedded as a string value in a stable ID.

**Why they conflict.**  
The canonical privacy rule applies to persisted provenance, but the canonical acceptance path leaves two persisted provenance fields capable of carrying the very identity the contract prohibits.

**Production consequence.**  
A candidate can pass canonical buffered validation while durably persisting reviewer identity in GitHub metadata. This defeats the privacy purpose of transient-author fallback and can create cross-run reviewer linkage if the worker derives IDs from a visible public identity.

**Severity:** `privacy_risk`

**Can current `g000001` hit it?**  
Yes. Fallback records themselves have safe enforced local patterns, but the current group may contain ordinary stable records or mixed stable+fallback evidence. Those stable internal IDs remain unrestricted. This audit found no evidence that such a leak has already been persisted for the current group.

**Minimal fix direction — design only.**  
Make all persisted `source_id` / `feedback_id` join keys explicitly dossier-local and author-independent, with a neutral machine pattern or deterministic local sequence that cannot encode reviewer identity. Keep the reopenable stable physical identity exclusively in the already-validated neutral item URL/`public_ref`.

**Would this weaken an intentional guard?**  
No. It closes a privacy enforcement hole and preserves the stronger stable-locator path.

---

### CONTRA-03 — Strict validation does not enforce the exact bound-record language projection

**Plain-language description.**  
The active language contract says observation `evidence_languages` is not free-form: it must equal the ordered distinct union derived from the exact bound feedback records, and `mixed` is an input record language that must expand to `russian + non_russian`, never an output token. The strict validator only checks that an explicitly claimed `russian` or `non_russian` token has some supporting record. It does not compare the observation field to the exact expected projection.

**Exact intended valid/invalid case.**  
Valid: a bound `mixed` record produces exactly `["russian","non_russian"]`; a bound `unknown` record contributes `"unknown"` in canonical order.  
Invalid but currently structurally passable examples include:
- bound `mixed` feedback serialized as `evidence_languages:["russian"]`, silently omitting non-Russian support;
- bound Russian feedback serialized as `evidence_languages:["mixed"]`, even though the active contract forbids `mixed` as an observation-summary token;
- a mixed known+unknown bound set that omits the required `unknown` token.

**Rule/component A.**
- `language_binding.observation_summary_rule`: exact ordered distinct union from the bound records;
- `language_binding.mixed_summary_token_policy`: do not emit `mixed`;
- `language_binding.canonical_output_order`: `russian, non_russian, unknown`;
- worker prompt requires the derivation to be repeated from final `player_feedback_ids` immediately before serialization.

**Rule/component B.**
- `scripts/taste_steam_review_dossier_strict.py::_validate_observations` accepts any non-empty list of schema enum tokens, then only verifies positive support for explicit `russian` and `non_russian` claims;
- the schema enum still contains `mixed`, and strict validation has no exact projection/equality check and no rejection of `mixed` as an observation-summary output.

**Why they conflict.**  
The canonical generation contract defines a deterministic derived field, but canonical acceptance validates only a weaker subset of that derivation.

**Production consequence.**  
A semantically stale or malformed language summary can be accepted after the bound record set changes. Downstream consumers can receive understated, overstated or non-canonical language support even though the exact record languages are available in the same dossier.

**Severity:** `silent_semantic_error`

**Can current `g000001` hit it?**  
Yes. The current group can normally combine Russian, non-Russian, mixed or unknown player feedback. The issue is especially reachable when a final bound set changes during research or includes `mixed`/`unknown` items. No current malformed candidate is asserted.

**Minimal fix direction — design only.**  
In the canonical strict validator, deterministically derive the expected ordered language token list from each observation's final `player_feedback_ids` using the contract projection and require exact list equality. Treat `mixed` only as a feedback-record input value, never a valid observation-summary output.

**Would this weaken an intentional guard?**  
No. It mechanically enforces the already-approved language-binding rule.

## 7. Exact conflicting components and consequence

| Finding | Permit/require side | Reject/accept side | Concrete consequence |
|---|---|---|---|
| CONTRA-01 | Exact-product identity + physical parent-child binding contract/prompt | Strict child validation only checks host/item shape/surface class; exact appid is parent-only | Wrong-product/parent Steam item can become a counted mention |
| CONTRA-02 | Compact privacy contract + prompt forbid persisted author identity | Stable internal IDs are arbitrary strings and compact provenance does not inspect them | Reviewer identity can be durably serialized despite privacy contract |
| CONTRA-03 | Language contract/prompt require exact deterministic projection | Strict validator performs only partial support checks | Non-canonical/stale language summary can be accepted |

## 8. Current `g000001` exposure

Current group:
- Crown Trick — `1000010`;
- Hellish Quart — `1000360`;
- Tetris® Effect: Connected — `1003590`.

All three findings are structurally reachable by the current group without changing scope:
- CONTRA-01 if stable Steam child evidence is used;
- CONTRA-02 if any stable provenance join ID is derived from visible author/account identity;
- CONTRA-03 if bound record languages are mixed/unknown or the final record set changes without exact re-derivation.

The audit does **not** claim that any of these malformed shapes has already been published for `g000001`. Canonical progress was still `0/730` at the audit baseline.

The known Crown Trick Steam Store parent blocker remains excluded because Chat 1 owns that fix.

## 9. False positives considered and rejected

- **Language-specific wording inside `conflicts[].statement` is not mechanically parsed.** Rejected as a finding because the accepted language-binding report explicitly records this as an intentional design choice to avoid brittle natural-language parsing; the prompt/contract own that semantic generation rule.
- **Transient same-author dedupe cannot be reconstructed after privacy-safe serialization.** Rejected because TASTE-010 intentionally makes author identity run-local and non-persistent and compensates with reduced recurrence strength.
- **Fallback preferred only after stable locator retrieval fails.** Rejected as a validator contradiction because availability of an unpersisted alternative locator is a research-time semantic fact, not deterministically reconstructible from the candidate artifact.
- **Russian existence proof is not itself a feedback record.** Rejected because the contract and strict validator consistently treat it as discovery state only.
- **Old and recent child items under one collection parent can be conservative to serialize.** Rejected because the active recency contract deliberately fails closed against laundering old evidence through a recent parent; no contrary active rule guarantees one parent record can represent every temporal role.
- **Known Steam Store review-card parent issue for Crown Trick.** Excluded by task contract and assigned to Chat 1.

## 10. Areas checked with no contradiction

No additional material contradiction was found in:
- fallback-only and mixed stable+fallback recurrence thresholds;
- exact `mention_count` = distinct bound feedback records;
- Russian `found_and_used` via valid stable/fallback Russian or mixed feedback;
- Russian unresolved existence/access states remaining non-complete;
- aggregate storefront counts/ratings/language totals remaining non-mentions;
- non-Steam transient fallback collection-parent semantics;
- profile-scoped transient inspection with profile identity omitted before persistence;
- Reddit subreddit/thread parent containment;
- known-child-date vs parent freshness coherence;
- source/child Russian vs non-Russian language containment;
- obvious source/item alias normalization and duplicate rejection;
- source-mix counting by physical used source identity;
- summary derivation and observation-based overall strength;
- content-complete schema/contract/prompt binding;
- same-day compatibility rebuild behavior;
- buffered create-only validation and optional prepublication parity using the same canonical validator;
- immutable/maximal-contiguous-prefix buffered acceptance architecture.

## 11. Status

`complete_findings`

Confirmed additional material contradictions: **3**.

No fixes were implemented.

## 12. Exactly one recommended next step

Director should compare this report with Chat 1's completed Steam Store review-card parent fix before opening any new implementation task, so any follow-up can reconcile the post-Chat-1 canonical binding once rather than creating overlapping fixes against the pre-fix binding.

## 13. Efficiency / reusable lesson

The existing dossier route in `PROJECT_ROUTES.md` was accurate enough to avoid a repository-wide bug hunt. The most efficient diagnostic pattern was to compare each newly declared semantic invariant against the narrow canonical acceptance functions that can actually accept/reject it: source validation, child-record validation, observation derivation, compact provenance and content-complete binding. That surfaced the three material gaps without expanding into unrelated Taste or production areas.

A reusable lesson for future contract migrations is that worker-facing deterministic derivations and privacy restrictions should each have one explicit positive and one exact counterexample regression at the canonical validator boundary. The current route already identifies that validator boundary, so no route update is required by this read-only task.
