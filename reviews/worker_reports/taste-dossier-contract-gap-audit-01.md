# Taste Dossier Contract Gap Audit 01

Task ID: `taste-dossier-contract-gap-audit-01`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Mode: `READ / AUDIT / RECON`  
Status: `complete_new_gaps_found`

`audit_baseline_sha`: `c1e1e0961fa3fc7093efc5147affa886562326cc`

All substantive audit reads and conclusions are pinned to that SHA. `main` was still at the same SHA immediately before this report publication. No other repository was read or used.

## Task

Independently audit the active Taste Steam review dossier prompt/schema/web-evidence contract/strict validator/freshness/ingestion boundary for additional reachable contract gaps, while excluding the already-known live defects being handled in parallel. Do not implement fixes or run production.

## Architecture preflight

PASS.

- GitHub remains the control-plane owner for scope, order, snapshot/group identity, validation, persistence, recovery, progress and completeness.
- Scheduled ChatGPT remains the bounded semantic/data worker for web research and compact synthesis.
- This audit changes neither responsibility boundary and creates no queue, retry loop, scheduler, quota or production stage.
- `config/execution_ownership_contract.json`, TASTE-004 through TASTE-007 decisions, the active V2 dossier contract and the active worker prompt are consistent on that ownership boundary.
- This task is `READ / AUDIT / RECON`; under the Director read-only worker rule, the only repository write is this durable report. No `CURRENT_TASK.md` mutation was made.

## Enforcement matrix summary

| Requirement / state | Prompt / web contract | Schema | Strict validator | Buffered / ingestion | Freshness / snapshot | Result |
|---|---|---|---|---|---|---|
| Exact descriptor appid/title | required | structural | exact expected appid/title | exact ordered group + strict per dossier | current queue title checked when a new daily manifest is built | mechanically enforced |
| Release year / resolved identity | title+year research, reliable metadata | year/range/status/corroborators | range, resolved, identity source exists, exact appid corroborator | inherits strict | revalidated structurally | semantic provenance only partially enforced |
| Observation feedback IDs / `mention_count` / recurrence | distinct attributable records | explicit binding invariants | exact IDs/count thresholds | inherits strict | strict cache reuse | mechanically enforced for distinct IDs, not physical-item identity |
| Individual feedback locator | individual review/post/contribution; URL or stable public ref | URL/public-ref fields | HTTPS host match or arbitrary 3..500-char `public_ref` | inherits strict | none | physical attribution not mechanically enforced |
| Source diversity | prefer multiple independent player sources | source-mix states | counts distinct used source IDs | inherits strict | none | source-ID diversity enforced; physical-source aliasing is not |
| Current/historical/durable | explicit temporal rules | status/freshness/role enums | role/freshness label relationships | inherits strict | dossier TTL separately evaluated | publication date is not reconciled with `recent` |
| Russian attempt | exact three-state semantics | enum | `found_and_used` has a one-way positive check | inherits strict | none | inverse state consistency missing |
| Conflicts | neutral synthesis includes conflicts/evidence strength | only array shape | statement + recurrence enum + resolvable source IDs | inherits strict | none | no attributable feedback/count binding |
| Dossier expiration at ingest | only fresh evidence should be reusable | expiry formula + future-skew metadata | checks formula and future generated time | canonical ingress calls strict validator directly | `dossier_state_strict` checks stale only when freshness is explicitly evaluated | expired dossier can be canonically ingested |
| Evidence-contract compatibility | incompatible evidence binding must rebuild | explicit revisions exist | active schema/contract loaded | strict uses current files | snapshot binding uses only names/versions/prompt revision token; worker index omits binding | compatibility fingerprint is incomplete |
| Canonical persistence | GitHub-owned | n/a | strict dossier validation | buffered and legacy canonical ingress both use strict V2 before persistence | downstream semantic input revalidates strict + freshness | strict-pass gaps below silently persist |

The retained legacy current-checkpoint transport is not a V1 validation bypass: `scripts/ingest_taste_steam_review_dossiers.py` routes it through `persist_submission_and_advance_snapshot_strict()`. The stale V1 metadata still present in the parent contract is therefore classified below as hardening-only, not as a proven canonical ingress bypass.

## `proven_new_gap`

### GAP-01 — Canonical ingress accepts an already-expired dossier and advances progress

**Active rule.** The dossier contract says fresh dossiers are reusable only while fresh, stale in-scope dossiers require refresh, and downstream semantic input is fail-closed on stale dossiers. `dossier_state_strict()` implements that by returning `stale` when `now >= expires_at_utc`.

**Missing enforcement.** `validate_dossier_strict()` checks:
- `expires_at_utc == generated_at_utc + ttl_days`;
- generated time is not more than five minutes in the future.

It does **not** require `expires_at_utc > now`. Both active canonical ingress paths ultimately call `validate_dossiers_against_expected_items()` / `validate_dossier_strict()` rather than requiring `dossier_state_strict(...) == "fresh"`:
- buffered path: `scripts/taste_steam_review_dossier_buffered.py::validate_buffer_artifact()`;
- retained current-checkpoint path: `scripts/taste_steam_review_dossier_web.py::persist_submission_and_advance_snapshot_strict()`.

**Minimal reachable fixture.** Start from the repository `web_dossier()` test fixture, but generate it 21 days before ingest while retaining the canonical 20-day TTL:

```text
generated_at_utc = NOW - 21 days
expires_at_utc   = NOW - 1 day
ttl_days         = 20
all other V2 fields valid
```

The worker shape can emit those timestamps; no schema field requires generated time to be near invocation time.

**Current strict result:** `ACCEPT`. The expiry formula is correct and the generated timestamp is not future-dated.

**Canonical consequence.** The dossier can be persisted, the immutable group consumed, and canonical `completed_required_count` advanced even though the just-persisted dossier is already stale. `build_semantic_input_strict()` then rejects the same cache entry as stale. Worse, same-day `build_or_preserve_daily_work()` preserves a compatible fixed snapshot without rebuilding cache freshness, so a now-complete worker index can coexist with downstream stale failure until a later daily rebuild.

**Impact class:** stale compatibility/freshness risk; control-plane completeness false positive.

**Narrow future fix layer:** strict canonical ingress/freshness boundary. Require the exact dossier being persisted to be `fresh` at ingress time, with a deterministic regression proving expired-but-formula-valid V2 dossiers cannot advance progress.

---

### GAP-02 — One physical player-feedback item can be aliased under multiple locators/IDs and counted multiple times

**Active rule.** The prompt and evidence contract define `mention_count` as the number of **distinct attributable player-feedback records actually inspected** and explicitly forbid duplicating records merely to reach recurrence thresholds. Source diversity likewise intends distinct used player sources.

**Missing enforcement.** `_validate_feedback_record()` returns the literal URL/public-ref string. `validate_dossier_strict()` deduplicates only exact strings in `feedback_refs`. Source refs are also deduplicated only by exact literal ref. There is no canonicalization of query parameters, fragments, equivalent URL forms, or stable physical feedback-item identity.

**Minimal reachable fixture.** Three feedback records point to the same physical review but use different syntactically valid HTTPS aliases, for example:

```json
{"feedback_id":"pf1","source_id":"p1","url":"https://steamcommunity.com/profiles/42/recommended/123456/", ...}
{"feedback_id":"pf2","source_id":"p1","url":"https://steamcommunity.com/profiles/42/recommended/123456/?utm_source=x", ...}
{"feedback_id":"pf3","source_id":"p1","url":"https://steamcommunity.com/profiles/42/recommended/123456/#review", ...}
```

An observation binds `pf1,pf2,pf3`, sets `mention_count:3`, `recurrence:"moderate"`.

**Current strict result:** `ACCEPT`. The three ref strings are distinct, all hosts match the parent source domain, and the count/recurrence rules are therefore satisfied mechanically.

The same primitive can also manufacture `multi_source` by representing one physical discussion/review surface with multiple source IDs whose literal refs differ only by alias form.

**Impact class:** evidence double-counting; semantic false positive.

**Narrow future fix layer:** compact feedback/source identity validation. Introduce canonical physical-item/source identity or deterministic locator normalization sufficient to reject obvious aliases before distinct-ID counting. Keep this separate from the already-fixed aggregate-count and recurrence-threshold guards.

---

### GAP-03 — A feedback record need not locate an individual feedback item at all

**Active rule.** The prompt requires every `provenance.player_feedback_records[]` entry to represent one individual review, post, discussion contribution or other attributable player-feedback item, using a URL or **stable public reference**. Aggregate/index/search surfaces are context/source containers, not one attributable mention.

**Missing enforcement.** `_validate_feedback_record()` only requires either:
- an HTTPS URL whose host matches the parent player-feedback source domain; or
- any string `public_ref` of length 3..500.

It does not distinguish a direct item locator from a reviews index, search-result page, aggregate/listing page or non-unique descriptive label.

**Minimal reachable fixtures.** Either of these can be used as the sole record behind an anecdotal observation:

```json
{"feedback_id":"pf1","source_id":"p1","url":"https://steamcommunity.com/app/123456/reviews/", ...}
```

or

```json
{"feedback_id":"pf1","source_id":"p1","public_ref":"Steam review found on 2026-09-16", ...}
```

The current live group-1 artifact also demonstrates the reachable shape: several Steam review records use human-readable date/playtime descriptors rather than an item identifier. This observation is independent of the already-known username/profile/excerpt defects in that artifact.

**Current strict result:** `ACCEPT` when the rest of the dossier is valid.

**Impact class:** semantic false positive; non-auditable provenance.

**Narrow future fix layer:** player-feedback-record locator contract/strict validator. Require an item-level stable locator for each counted record; explicitly reject known collection/search/aggregate locator shapes as feedback records while still allowing them as parent sources.

---

### GAP-04 — `freshness:"recent"` is not reconciled with the stored publication date

**Active rule.** The worker contract says current bugs/performance/compatibility/localization/regional claims require recent current-state support and describes recent research as roughly the last 12 months when available. The strict rule is intended to require a `recent` + `current_state` source for `evidence_status:"current"`.

**Missing enforcement.** `_validate_source()` enforces only the declared labels: if `evidence_role == "current_state"`, then `freshness` must equal `recent`. `_validate_publication_date()` merely rejects materially future-dated dates. No rule checks that a non-null publication date is temporally compatible with `freshness:"recent"`. `_validate_feedback_record()` likewise does not require a current observation's bound player records to be recent.

**Minimal reachable fixture.** In a structurally valid V2 dossier generated in September 2026:

```json
{
  "source_id":"p2",
  "source_type":"reddit",
  "publication_date":"2020-01-01",
  "freshness":"recent",
  "evidence_role":"current_state",
  "player_feedback":true,
  ...
}
```

Bind a player-feedback record also dated `2020-01-01` from `p2` to an observation with `evidence_status:"current"`.

**Current strict result:** `ACCEPT`. The declared `current_state/recent` pair satisfies the current predicate even though the persisted date makes that classification internally incoherent.

**Impact class:** temporal misclassification; semantic false positive for current state.

**Narrow future fix layer:** strict temporal coherence. When a publication date is present, validate `recent/older` against a canonical age rule relative to `generated_at_utc`; retain explicit behavior for genuinely unknown dates rather than trusting a contradictory label.

---

### GAP-05 — Russian attempt status is enforced only in the positive direction

**Active rule.** The prompt defines exactly three mutually meaningful states:
- `found_and_used`: at least one attributable Russian/mixed player-feedback record was actually bound to an observation;
- `searched_not_found_or_insufficient`: useful attributable Russian feedback was absent/too weak;
- `source_access_unavailable`: relevant Russian source access was unavailable.

**Missing enforcement.** `validate_dossier_strict()` checks only one implication:

`russian_attempt == found_and_used -> at least one used Russian/mixed record`.

It does not enforce the converse or exclusivity. A dossier can contain and use Russian feedback while claiming it was not found or access was unavailable.

**Minimal reachable fixture.** Start from the passing repository fixture with a bound Russian `pf4` and Russian-language current observation, then change only:

```json
"russian_attempt":"searched_not_found_or_insufficient"
```

or:

```json
"russian_attempt":"source_access_unavailable"
```

**Current strict result:** `ACCEPT` for both contradictory states. This is separate from the known Sniper Elite 5 defect, which is the opposite direction (`found_and_used` without a bound Russian record) and is explicitly excluded from the new-finding count.

**Impact class:** semantic false negative; internally contradictory evidence-state metadata.

**Narrow future fix layer:** strict evidence-state derivation/inverse constraints. If any Russian/mixed record is actually used, non-found/unavailable states must be rejected; define any intentional edge case explicitly rather than leaving the status worker-asserted.

---

### GAP-06 — `conflicts[]` recurrence can be asserted without any attributable player feedback

**Active rule.** The active production evidence model is player-feedback research; official/professional context cannot substitute for player feedback. Neutral synthesis explicitly includes conflicts and evidence strength, and recurrence is a player-feedback strength concept elsewhere in the V2 dossier.

**Missing enforcement.** `_validate_conflicts()` requires only:
- string `statement`;
- a recurrence enum;
- non-empty unique `source_ids` that resolve.

It does not require `player_feedback_ids`, `mention_count`, a player-feedback source, language/temporal binding, or any relationship between conflict recurrence and attributable records. The JSON schema itself defines `conflicts` only as an array.

**Minimal reachable fixture.** Add to any otherwise-valid V2 dossier:

```json
"conflicts":[{
  "statement":"Evidence is described as strongly conflicting.",
  "recurrence":"strong",
  "source_ids":["m1"]
}]
```

where `m1` is the existing `official_metadata` identity source with `player_feedback:false`.

**Current strict result:** `ACCEPT`. The source exists, so the conflict passes despite having zero attributable player-feedback records.

The current group-1 live artifact also proves the worker actively emits the loose `statement/recurrence/source_ids` conflict shape; this finding does **not** rely on or re-count Hellish Quart's already-known current-state validation defect.

**Impact class:** semantic false positive; unauditable evidence strength.

**Narrow future fix layer:** conflict schema/strict validation. Either bind conflicts to attributable feedback records with count/recurrence rules analogous to observations, or remove recurrence semantics from conflicts if they are intended only as unquantified synthesis.

---

### GAP-07 — Evidence compatibility is not content-complete and changes are not fully propagated to the daily snapshot

**Active rule.** The control-plane contract says:
- incompatible evidence binding requires a normal GitHub-owned snapshot rebuild even on the same day;
- fresh dossiers are reusable only when the active strict web-evidence binding remains compatible;
- worker liveness requires the same snapshot/plan bindings to remain current.

The active schema and web-evidence contract deliberately expose `schema_revision` and `contract_revision` fields.

**Missing enforcement, part A — incomplete fingerprint.** `current_worker_contract_binding()` contains only:

```text
evidence contract schema + version
worker schema name + version
dossier schema name + version
worker_prompt_revision token
```

It omits `schema_revision`, `contract_revision`, and any content hash of the schema, evidence contract or worker prompt. `_snapshot_identity()` and same-day `compatible_same_day` logic rely on that incomplete binding. Therefore a semantics-changing revision that stays within V2 can leave the binding and snapshot identity unchanged.

**Missing enforcement, part B — propagation.** `.github/workflows/build-pre-ai-store-snapshot.yml` triggers on `config/taste_steam_review_dossier_schema.json` and the parent dossier contract/scripts, but its `push.paths` does **not** include:

- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`.

A direct change to either active semantic contract file therefore does not itself rebuild the daily snapshot/projection.

**Missing enforcement, part C — worker projection.** The current `taste_steam_review_dossier_worker_index.json` contains snapshot/group/progress/TTL/sampling/scope bindings, but no explicit `web_evidence_contract_binding`; per-group descriptors also omit it. The worker can re-read the tiny index exactly as instructed and still cannot compare an active semantic revision/hash to the projection.

**Minimal reachable counterexamples.** Two bounded transition fixtures are enough:

1. Same day, change `schema_revision` or `contract_revision` and a V2 rule without changing the schema/version tuple. The pre-AI builder still sees the old snapshot as `compatible_same_day` and preserves its scope/progress because `current_worker_contract_binding()` is unchanged.
2. Change only the active worker prompt body or active web-evidence contract while leaving `worker_prompt_revision`/version unchanged. The canonical pre-AI workflow is not push-triggered by those files, the worker index remains unchanged, and an already-prepared snapshot remains live.

**Current strict result:** this gap occurs **before** a single-dossier strict decision. If the revision changes only semantic requirements not represented in strict structure, old dossiers/artifacts remain strict-valid and can silently continue. If the revision tightens strict validation, an immutable artifact prepared under the preserved old plan can newly fail as `invalid_expected_group`, while same-day compatibility still says the snapshot is current.

A second freshness consequence exists for cache reuse: same-day preservation does not rebuild required scope by re-running `dossier_state_strict()` over the store. A revision-only strict change can therefore make a cached dossier invalid for downstream semantic input without placing it into dossier work until a later true rebuild.

**Impact class:** stale compatibility/freshness risk; control-plane/recovery risk.

**Narrow future fix layer:** evidence-binding/versioning and pre-AI orchestration. Make the binding content-complete (revision fields and/or canonical hashes, including prompt semantics), bind/expose it in the worker projection, and trigger canonical snapshot reconciliation when either active semantic contract file changes.

## `already_known_or_parallel_fix`

The following are real but explicitly excluded from the new-finding count and were not reclassified as new gaps:

1. worker pre-publication validation not equivalent to canonical strict validation;
2. username/display-name/author-profile/review-excerpt leakage through compact provenance;
3. recovery of the currently blocked immutable invalid artifacts;
4. aggregate Steam review totals used as `mention_count`;
5. `?l=russian` / Russian Store UI used as Russian player feedback;
6. recurrence inconsistent with bound player-feedback evidence;
7. the observed Hellish Quart current-state mismatch, DEEEER source-mix mismatch, and Sniper Elite 5 unbound-Russian `found_and_used` mismatch.

The parallel implementation may change `main` after this audit baseline. This report intentionally does not chase or merge those changes into its findings.

## `hardening_only`

These observations are worth cleanup or future consideration but are **not** counted as proven reachable new defects in this report:

- `config/taste_steam_review_dossier_contract.json` still advertises `schemas.dossier = TASTE-STEAM-REVIEW-DOSSIER-V1` and legacy `required_dossier_fields` including `review_sample`, while active ingress is V2 and rejects `review_sample`. Active canonical ingestion does not consult those stale metadata fields, so no V1 bypass was proven.
- Release-year/corroborator semantics are only structurally checked. The validator proves exact appid/title and a resolved/ranged year, but cannot prove from compact metadata that the year was actually obtained from reliable public metadata. A deterministic wrong-release production case was not established without external semantic verification.
- A professional/editorial page can in principle be mislabeled as an allowed player-feedback source type because the validator trusts `source_type`; however a general domain-based classifier would be brittle and no independent live misclassification was proven on this baseline.
- `overall_strength:"conflicted"`, `conflicts[]`, and `stop_reason:"bounded_limit_reached"` lack some potentially useful inverse/count relationships, but the active contract does not define enough exact machine semantics to classify those combinations beyond GAP-06 without inventing policy.

## Canonical-ingestion and immutable-publication answers

**Can a proven new gap silently pass canonical ingestion? Yes.** GAP-01 through GAP-06 are accepted by the current strict predicates when embedded in otherwise-valid V2 dossiers. Both buffered ingestion and retained current-checkpoint ingestion call that strict V2 path before persistence, so those states can become canonical cache content and advance progress. GAP-07 can also silently preserve/reuse old-policy evidence when a semantic revision is not represented by the compatibility fingerprint.

**Can a proven new gap block immutable recovery/publication? Yes, but only GAP-07 directly creates that class.** A strict-tightening revision that is invisible to same-day compatibility can leave an old immutable expected artifact/snapshot active and then reject the artifact under the new validator, producing an `invalid_expected_group`-style stop. That root cause is distinct from the already-known recovery procedure for the currently blocked artifacts. GAP-01 through GAP-06 generally do the opposite: because strict accepts them, they do not trigger recovery and instead risk silent canonical persistence.

## Changes

- Added only `reviews/worker_reports/taste-dossier-contract-gap-audit-01.md`.
- No prompt, schema, contract, validator, workflow, queue, cache, worker index/group, canonical progress, receipt, recovery request, dossier artifact or Scheduled Task state was changed.
- Scheduled Task `Run now` was not invoked.

## Validation

- START gate and repository scope guard: PASS.
- Architecture/ownership preflight: PASS.
- Audit baseline pinned before substantive reads: PASS (`c1e1e0961fa3fc7093efc5147affa886562326cc`).
- Mandatory acceptance-02 / evidence-guard implementation / acceptance-03 history read: PASS.
- Active prompt/schema/web-evidence/strict/buffered/freshness/ingestion paths reconciled: PASS.
- Current canonical ingress legacy-transition check: PASS; retained current-checkpoint path is strict V2, not V1.
- Known/parallel defects excluded from new count: PASS.
- Proven new gap count: **7**.
- New production execution: none.

The fixture outcomes above are deterministic code-path audits against the pinned validator and repository test-fixture shape; this READ-only task did not add or execute new regression code.

## Unresolved

No implementation was attempted. The seven proven gaps remain open on the pinned baseline. A parallel worker may land fixes for the explicitly excluded known defects after this report; those changes were intentionally outside this baseline audit.

## Status

`complete_new_gaps_found`

## Recommended next step

Create **one bounded IMPLEMENT task** covering only the seven proven gap classes in this report: reject expired dossiers at canonical ingress; canonicalize/validate physical feedback identities and require item-level locators; enforce date/freshness coherence; make Russian-attempt states bidirectionally consistent; bind conflict strength to attributable evidence; and make evidence compatibility content-complete and rebuild-triggered. Add one deterministic regression per counterexample, keep group size `3`, preserve GitHub control-plane ownership, and do not mix the already-known current immutable-artifact recovery into this implementation task.

## Exact refs

- Audit task: `WORKER_TASK_TASTE_DOSSIER_CONTRACT_GAP_AUDIT_01.md`
- Baseline: `c1e1e0961fa3fc7093efc5147affa886562326cc`
- Active prompt: `config/taste_steam_review_dossier_worker_prompt.md`
- Active worker schema: `config/taste_steam_review_dossier_schema.json`
- Active evidence contract: `config/taste_steam_review_dossier_web_evidence_contract.json`
- Parent control-plane contract: `config/taste_steam_review_dossier_contract.json`
- Strict validator: `scripts/taste_steam_review_dossier_strict.py`
- Buffered validator/drain: `scripts/taste_steam_review_dossier_buffered.py`
- Strict canonical submission path: `scripts/taste_steam_review_dossier_web.py`
- Inbox state drain: `scripts/ingest_taste_steam_review_dossier_inbox.py`
- Daily/freshness builder: `scripts/build_taste_steam_review_dossier_work.py`
- Worker projection: `scripts/taste_steam_review_dossier_worker_projection.py`
- Pre-AI workflow: `.github/workflows/build-pre-ai-store-snapshot.yml`
- Shared V2 test fixture: `scripts/taste_steam_review_dossier_test_fixture.py`
- Current worker index on baseline: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- Existing live artifact shape used only for reachability examples: `data/ai_inbox/taste_steam_review_dossiers/d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000001--83d91127ece346690fb62af453938d80be6707c19ae6019ab85de6404b11d021.json`

Efficiency / reusable lesson: `candidate — compatibility/freshness audits should bind semantic contract content/revisions, not only schema/version names; otherwise same-day preservation can hide contract changes from both scope rebuilding and worker liveness checks.`
