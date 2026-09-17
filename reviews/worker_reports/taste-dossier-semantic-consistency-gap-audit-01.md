# Taste Dossier Semantic Consistency Gap Audit 01

Status: `complete_new_gaps_found`

Task: `taste-dossier-semantic-consistency-gap-audit-01`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Mode: `READ / VALIDATE`

Pinned audit baseline: `01a5984eb8322b45b6f269f02fbf5c497e62278b`

`main` was still exactly at the pinned baseline immediately before this report publication. No other repository was searched, read, modified, or used. Scheduled Task `Run now` was not invoked.

## Result

The audit found **6 proven new semantic-consistency gaps** beyond the already-known `g000002` Blacksad language mismatch:

- **4 `acceptance_gap`** findings where semantically contradictory or unsupported data can pass the current canonical GitHub strict validator;
- **2 `generation_contract_gap`** findings where the strict validator rejects a shape but the active worker prompt/schema/evidence contract do not clearly state the rule needed to avoid generating it;
- additional `hardening_only` observations are recorded separately and are not counted as proven gaps.

The known Blacksad defect is explicitly excluded from this count and remains owned by the separate implementation chat.

## Architecture preflight

PASS.

1. **Current owner:** GitHub remains the control-plane owner of dossier scope/order, immutable group plan, canonical validation, persistence, progress, recovery and completeness under `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json`.
2. **Canonical authorization:** the active dossier contract, V2 web-evidence contract, worker schema and worker prompt authorize Scheduled ChatGPT only for bounded semantic web research, compact synthesis and immutable create-only candidate publication.
3. **Control-plane transfer:** none. This audit does not move validation, queue, retry, persistence, acceptance or completeness authority into Scheduled ChatGPT or this interactive chat.
4. **New recurring mechanism check:** none. No scheduler, queue, retry loop, quota, backlog manager, alternate persistence path or repair mechanism is created.

This task is read-only except for this durable report. No production/runtime/configuration implementation was made.

## Audit method and bounded scope

The audit reconciled the current active:

- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `scripts/taste_steam_review_dossier_strict.py`;
- `scripts/taste_steam_review_dossier_buffered.py`;
- `scripts/taste_steam_review_dossier_compact_provenance.py`;
- `scripts/taste_steam_review_dossier_parallel_validation.py` and its contract/status surface;
- downstream `build_semantic_input_strict()` handoff;
- required prior contract-gap / implementation / parallel-buffer / live-acceptance reports.

Bounded live supporting evidence was limited to the current-snapshot `g000002` and `g000003` candidates. No broad artifact mining was performed.

The proof standard for `acceptance_gap` is either a live strict-valid example or a deterministic code-path counterexample in which every existing strict predicate is satisfied while the contradictory state remains unchecked. The proof standard for `generation_contract_gap` is a validator predicate that rejects the shape plus absence of the corresponding generation rule from the active worker-facing prompt/schema/evidence contract.

## Known Blacksad defect — excluded from new finding count

`g000002` remains invalid because the Blacksad current observation declares Russian evidence while all feedback records bound to that observation are `non_russian`. GitHub correctly records:

`observation 1 claims Russian evidence without Russian player-feedback record`

This is the already-known defect assigned to the separate implementation worker. This report does **not** count that instance, nor the direct `evidence_languages` root rule being handled there, as a new finding.

No other independent `g000002` issue is used as a new finding below.

## Proven new gaps

| ID | Classification | Exact reachable shape | Why current controls do / do not catch it | Impact | Smallest recommended response |
|---|---|---|---|---|---|
| `SCG-01` | `acceptance_gap` | A feedback record is assigned to a parent `source_id` whose physical locator / surface type does not actually contain or represent that item, while staying on the same host. Live `g000003` does this: `s-reddit` is `https://www.reddit.com/r/sniperelite/`, but `s-f4` points to `/r/XboxSeriesX/comments/...` and `s-f5` to `/r/patientgamers/comments/...`; DEEEER also binds a `steam-discussion:*` item under a `steam_reviews` `/reviews/` parent source. | Strict only requires the record's `source_id` to resolve to a player-feedback source, the record source to appear in the claim `source_ids`, and URL host to equal parent-source domain. `public_ref` type is not reconciled with parent `source_type`; same-domain URL paths are not reconciled with parent physical locator. `g000003` is durably marked `valid`, proving live acceptance. | Parent provenance can be false; `source_mix_status`, source type, source language/freshness/role and physical-source diversity can be derived from the wrong parent surface. | Define and enforce one canonical parent-item relationship rule for item URL/public-ref ↔ source locator/type, preserving same-thread distinct-item support. |
| `SCG-02` | `acceptance_gap` | The same physical player item can be represented as a parent source with `publication_date:null`, `freshness:"recent"`, `evidence_role:"current_state"`, while its bound feedback record for the same item has `publication_date:"2020-01-01"`; a `current` observation binds that old record. | Dated freshness is checked only inside `provenance.sources[]`. Feedback-record dates are validated for syntax/future date but never reconciled with the parent source's freshness/role/date. A null-dated source may be worker-labeled `recent`; `current` only asks for a referenced `current_state + recent` source. No source↔child temporal coherence predicate rejects the contradiction. | An old attributable item can satisfy a mechanically `current` player-feedback claim through contradictory source-level metadata, despite the 365-day source freshness guard. | Add source↔feedback temporal coherence for the physical item / current-state support path; keep the existing explicit undated-source behavior where no child date resolves it. |
| `SCG-03` | `acceptance_gap` | Start from any strict-valid dossier and change only `summary` to a direct contradiction, e.g. state that no attributable Russian feedback was found while `russian_attempt:"found_and_used"` and Russian records are bound, or assert a recurring localization defect with no matching observation/conflict. Keep the text within 20..1200 characters. | Strict validates only summary type/length plus generic raw/personal-field guards. It does not bind summary claims to observations, conflicts, Russian attempt, statuses, recurrence or evidence strength. Downstream `build_semantic_input_strict()` copies the full validated dossier unchanged. | Unsupported or contradictory free-form claims can become canonical and reach the Taste semantic producer despite all structured evidence fields being correct. | Make dossier-level summary mechanically derived from validated structured findings or add an explicit structured summary binding so free-form prose cannot introduce new factual claims. |
| `SCG-04` | `acceptance_gap` | Take any conflict object that individually passes strict validation and append a byte-identical second copy to `conflicts[]`. | The prompt explicitly says not to duplicate conflicts, but `_validate_conflicts()` has no cross-entry duplicate set/hash. Observation validation rejects exact duplicate observations; conflict validation does not. Both copies pass mention-count, recurrence and source/feedback binding checks independently. | Canonical dossier content can double-present the same conflict and downstream semantic analysis can overweight duplicated evidence despite no new player feedback. | Add deterministic exact-conflict duplicate rejection, aligned with the existing observation duplicate guard; separately define semantic-near-duplicate policy only if needed. |
| `SCG-05` | `generation_contract_gap` | Valid observations have maximum recurrence `moderate`; a valid conflict has `strong` recurrence with 5 bound records; worker emits `evidence.overall_strength:"strong"` because the dossier contains strong conflict evidence. | Active schema only enumerates `overall_strength`; prompt says to preserve evidence strength but gives no derivation; web-evidence contract gives no rule saying `strong`/`moderate` strength is based only on observations. Strict, however, computes `max_recurrence_rank` from **observations only** and rejects `strong` unless at least one observation is `strong` (and similarly `moderate`). | A plausible contract-compliant synthesis can create an immutable candidate that GitHub rejects, causing avoidable production stalls even though all underlying evidence bindings are valid. | Put the canonical `overall_strength` derivation in the worker-facing machine contract/prompt and align validator semantics, explicitly deciding how conflicts participate. |
| `SCG-06` | `generation_contract_gap` | Parent player source is recorded as `language:"non_russian"`; one attributable child record under that source is `language:"russian"`, is correctly bound, and `russian_attempt:"found_and_used"`. Symmetric Russian-parent/non-Russian-child shape also applies. | Worker prompt/schema/evidence contract require both source-level and item-level language fields but do not state the parent-language containment rule. Strict has a hidden rule: Russian child requires parent `russian|mixed`, non-Russian child requires parent `non_russian|mixed`, and rejects otherwise. | Worker can correctly find/use Russian evidence yet publish an immutable group that stalls only because parent language was not widened to `mixed`; this is separate from Blacksad's observation-language mismatch. | Document the exact parent-source ↔ feedback-record language rule in the active machine contract/prompt, preferably as a schema invariant matching the existing strict validator. |

## Detailed proof notes

### SCG-01 — live strict-valid parent-source mismatch

`g000003` is independently recorded by GitHub as `validation:"valid"` / `canonical_position:"later_buffered"`.

Inside Sniper Elite 5:

- parent source `s-reddit` locator is the `r/sniperelite` community root;
- feedback records `s-f4` and `s-f5` are item URLs in `r/XboxSeriesX` and `r/patientgamers` respectively;
- all three are accepted under the same `source_id` because their host is `reddit.com`.

Inside DEEEER Simulator:

- parent `d-steam` is typed `steam_reviews` and locates the Steam reviews collection;
- `d-f3` is persisted as a `steam-discussion:*` public reference under that source.

The compact-provenance validator checks profile/privacy/content safety only; it does not repair this parent/source semantic relationship. This is therefore a live acceptance gap, not merely a hypothetical hardening idea.

### SCG-02 — cross-level freshness contradiction survives the 365-day guard

The previous 365-day gap is closed for a **dated source**. This new gap is different: the source can have `publication_date:null`, so source freshness remains worker-classified by contract. If the bound feedback item itself has a known old date, strict does not reconcile that child date back to the source-level `recent/current_state` label.

A minimal valid path is:

```json
{
  "source": {
    "source_type": "reddit",
    "domain": "reddit.com",
    "url": "https://www.reddit.com/r/example/comments/abc123/",
    "publication_date": null,
    "language": "non_russian",
    "freshness": "recent",
    "evidence_role": "current_state",
    "player_feedback": true
  },
  "feedback_record": {
    "source_id": "same-source",
    "url": "https://www.reddit.com/r/example/comments/abc123/",
    "publication_date": "2020-01-01",
    "language": "non_russian"
  },
  "observation": {
    "evidence_status": "current",
    "recurrence": "anecdotal",
    "mention_count": 1
  }
}
```

With ordinary required IDs/fields filled consistently, current strict has no rejecting predicate for the source-vs-child date contradiction.

### SCG-03 — summary is not evidence-bound

`validate_dossier_strict()` checks only:

- `summary` is a string;
- trimmed length is 20..1200.

It never derives or cross-validates summary assertions. Because the downstream semantic input embeds the complete dossier, the summary is not harmless display-only text.

### SCG-04 — conflicts lack the duplicate guard observations already have

Observation validation calculates a canonical digest and rejects an exact duplicate object. Conflict validation has no equivalent `seen` set. Duplicating an otherwise-valid conflict changes neither any individual count nor any item identity, so both entries pass.

### SCG-05 — `overall_strength` validator semantics are hidden from the producer

Strict uses:

- `strong` => at least one `strong` **observation**;
- `moderate` => at least one `moderate` or `strong` **observation**.

It does not include conflict recurrence in that maximum. Neither the active schema invariants nor the evidence contract nor worker prompt defines that observation-only derivation. This is exactly the class requested for `generation_contract_gap`: validation is correct according to its own rule, but worker instructions do not provide the rule needed to generate reliably acceptable data.

### SCG-06 — parent language containment is validator-only

Strict enforces:

- child `russian` => parent source language must be `russian` or `mixed`;
- child `non_russian` => parent source language must be `non_russian` or `mixed`.

The worker-facing contracts enumerate both language fields and define Russian-attempt semantics, but do not state this source-child containment invariant. The rule should not remain discoverable only through GitHub's post-publication rejection.

## Audited consistency-family matrix

| Consistency family | Result | Notes |
|---|---|---|
| Observation `evidence_languages` vs bound records | `not provable` as a **distinct new** finding | The live Blacksad mismatch is known and excluded. The broader exact-language derivation surface belongs to that same parallel fix and is not double-counted here. |
| Conflict feedback/count recurrence | `protected` | Required `mention_count` / `player_feedback_ids`, recurrence thresholds and player-source binding are enforced. |
| `russian_attempt` vs used Russian/mixed records | `protected` | Bidirectional strict rule is active. |
| `source_mix_status` vs used physical player sources | `gap found` | Core distinct-source count exists, but SCG-01 proves the physical parent source can be semantically wrong, undermining the derived mix. |
| Observation `mention_count` / recurrence vs distinct physical feedback records | `protected` | Exact ID count, physical item de-aliasing and recurrence minimums are enforced. |
| Observation/conflict `source_ids` vs feedback parent relationship | `gap found` | SCG-01. Source ID membership is checked, actual parent surface/type relationship is not. |
| Dated source freshness (`<=365` recent, `>365` older) | `protected` | Existing source-level guard is active. |
| Source freshness/role vs child feedback date | `gap found` | SCG-02. Cross-level temporal contradiction remains possible. |
| `current` / `historical` / `durable` source-role prerequisites | `protected` with SCG-02 caveat | Required source-role/freshness labels are checked; the caveat is that child dates are not reconciled to those labels. |
| Player-feedback vs official/professional source types | `protected` at declared source-object level | Type→`player_feedback` boolean rules are enforced. Actual item-to-parent surface/type consistency is SCG-01. |
| Item-level public refs vs list/search/index/aggregate surfaces | `protected` | Existing item-level stable-locator guard is active. |
| Physical feedback/source aliasing | `protected` | Canonical URL/source normalization rejects the known alias class. |
| Compact-provenance privacy/content rules | `protected` | Profile URLs, identity attribution and content-like refs remain mechanically guarded. |
| Conflicts vs observations duplicate semantics | `gap found` | SCG-04: exact conflict duplicates pass while exact observation duplicates are rejected. |
| Dossier-level `summary` vs structured evidence | `gap found` | SCG-03. |
| `overall_strength` vs observation/conflict evidence | `gap found` | SCG-05 generation drift for `strong/moderate`; exact inverse semantics for `limited/conflicted` remain under-specified and are not promoted beyond hardening-only. |
| Parent source language vs child feedback language | `gap found` | SCG-06 generation-contract drift. |
| Release identity / exact appid-title binding | `protected` structurally | Exact appid/title and identity-source/appid corroborator checks remain active; external truth of free-form corroborator values is outside deterministic proof here. |

## `g000003` additional issue

**Yes.** `g000003` exposes an additional issue beyond Blacksad: SCG-01 is present in a candidate GitHub independently marked strict-valid.

The Sniper Elite 5 and DEEEER examples above prove that a strict-valid dossier can carry parent-source locator/type metadata that does not correspond to the actual bound feedback item surface. This finding does not depend on `g000002`, does not reuse the known language mismatch, and is therefore counted as a new acceptance gap.

No new `g000003` issue is inferred merely from subjective content quality; only the deterministic parent/source inconsistency is used as live proof.

## Prompt/schema wording materially out of sync with strict validator

**Yes.** Two proven generation-contract gaps remain:

1. `overall_strength` has strict observation-only thresholds for `strong/moderate` that are absent from the worker-facing schema/evidence contract/prompt (`SCG-05`).
2. parent-source language containment for child feedback records is enforced by strict Python but not stated by the worker-facing contracts (`SCG-06`).

The known Blacksad `evidence_languages` defect is a third observed generation failure, but it is explicitly excluded from this audit's new-gap count because it is already assigned to the parallel implementation worker.

## Hardening-only / not promoted to proven new gaps

These are not counted as new proven gaps:

- `overall_strength:"limited"` and `overall_strength:"conflicted"` still lack an exact inverse derivation. The prior contract-gap audit already identified this as under-specified, and no new canonical semantic rule is invented here.
- Observation validation rejects only exact duplicate objects. A useful future semantic-near-duplicate identity may be possible, but the active contract does not define a deterministic equivalence relation precise enough to classify every near-duplicate as invalid. SCG-04 is limited to the proven exact-conflict duplicate hole.
- A source could be semantically mislabeled as a player-feedback source type despite being editorial/context content. This remains externally semantic and was already noted in the prior audit; this report does not invent a brittle domain classifier. SCG-01 is narrower and proven because the persisted child locator visibly belongs to a different physical surface than its parent locator/type.

## Existing protections revalidated, not re-reported

This audit does not re-count the already-implemented protections for:

- expired dossier rejection;
- physical feedback/source alias normalization;
- list/search/index/vague feedback-ref rejection;
- 365-day dated-source freshness coherence;
- bidirectional Russian-attempt consistency;
- feedback-bound conflict recurrence;
- content-complete compatibility binding;
- compact-provenance privacy/content guard;
- aggregate Steam counts not creating mention counts;
- Russian-rendered store page not counting as player feedback;
- contiguous-prefix canonical acceptance;
- parallel buffering behind an invalid group.

## Changes / execution

- Added only `reviews/worker_reports/taste-dossier-semantic-consistency-gap-audit-01.md`.
- No prompt, schema, contract, validator, workflow, runtime, route, candidate, cache, worker index/descriptor, validation status, canonical progress, recovery state or Scheduled Task configuration was changed.
- No Scheduled Task `Run now` was invoked.
- No production candidate/test artifact was created.

## Validation summary

- START gate and repo-scope guard: PASS.
- Pinned baseline before substantive audit: PASS — `01a5984eb8322b45b6f269f02fbf5c497e62278b`.
- `main` unchanged from pinned baseline immediately before report publication: PASS.
- Architecture preflight: PASS.
- Mandatory active contracts/prompt/schema/strict/buffered/parallel-status paths read: PASS.
- Required prior worker reports read: PASS.
- Bounded live candidate review limited to `g000002` / `g000003`: PASS.
- Known Blacksad defect excluded from new count: PASS.
- Proven new gaps: **6** (`4 acceptance_gap`, `2 generation_contract_gap`).
- Implementation changes: none.
- Scheduled Task runs: none.

## Exactly one next step

After Director review, create **one bounded IMPLEMENT task** for `SCG-01..SCG-06`, with one deterministic regression per counterexample and coordination with the separate Blacksad fix so the same language-related surface is not implemented twice; do not auto-fix or auto-run the Scheduled Task from this audit chat.