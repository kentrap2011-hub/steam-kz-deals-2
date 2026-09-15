# Taste dossier full defect sweep 01

Task ID: `taste-dossier-full-defect-sweep-01`  
Mode: `READ-ONLY / RECON`  
Status: `sweep_complete_repair_batch_ready`  
Sweep baseline: `main@8c4d28ccd1333c84fd1a97554d09145c88ebf181` (`director: add full dossier defect sweep task`)  
Canonical snapshot: `c4b3c29947e926fd2e8cfea0d3cc7a8c5f42baa7e2438d4d16b59857161d9bf3`  
Prepared date: `2026-09-15` (Europe/Samara contract date)  
Prepared/completed/remaining: `594 / 0 / 594`  
Canonical expected sequence: `1` of `60`  

## Executive conclusion

The compact N→N+1 transport itself passed the important live ordering property: group 2 was published immediately after group 1 without waiting for canonical acceptance of group 1. The current blocker is not compact traversal or workflow serialization.

The full sweep found two repair families that must be closed before another live `Run now`:

1. **Dossier schema/evidence contract closure.** The live worker prompt does not carry the exact canonical dossier JSON contract, the canonical validator contains hidden/loose rules, and evidence-unavailability semantics are undefined. This produced the live `content` enum rejection and also allowed 20 dossier objects with zero review bodies and weak provenance to look structurally valid.
2. **GitHub-owned buffered recovery/lifecycle.** An invalid deterministic create-only expected artifact has no same-snapshot repair path. The worker is correctly forbidden to overwrite/rename/skip it and the GitHub drain is correctly fail-closed, but there is no authorized quarantine/replacement/reconciliation path. The current snapshot is therefore deadlocked at group 1 until GitHub-owned recovery is implemented or the daily snapshot rolls over.

A new live `Run now` is **not safe now**. No production artifacts were deleted/replaced and no workflow was dispatched during this sweep.

## Current repository state

- Full canonical manifest remains `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2`, snapshot `c4b3...d9bf3`, with `594` required, `0` completed, `594` remaining.
- Compact worker index agrees with canonical state: `group_count=60`, `canonical_expected_sequence=1`, `ttl_days=20`.
- Descriptor `g000001` contains 10 exact items and group hash `74000acf375f0f0647b09d3726e6e5b37c1953f21543527027b9d61ccf7d7d06`.
- Descriptor `g000002` contains the next 10 exact items and group hash `f8646b55450b4b4fe988bdf1a8a3348be4f794461bdc30699be2393095ae5f8a`.
- Descriptor `g000003` exists and is readable; the worker stopped while researching it, before publication.
- Final descriptor `g000060` is a valid partial final group with 4 items, so the compact projection represents the `594 % 10 = 4` edge correctly.
- Inbox currently contains exactly two current-snapshot files: deterministic group 1 and deterministic group 2. There is no group 3 artifact.
- Both observed ingest attempts stopped at canonical expected group 1 with `invalid_expected_group`; canonical progress therefore did not advance and neither pending file was cleaned.

## Exhaustive audit of every published dossier in group 1 and group 2

Classification meanings:

- `INVALID` = rejected by the current canonical validator.
- `VALID-BUT-EVIDENCE-SUSPICIOUS` = passes current validator but violates or fails to prove the intended Steam-review evidence model discovered in this sweep.

| Group | AppID | Title | Current validator | Evidence audit |
|---|---:|---|---|---|
| 1 | 2378500 | Baldur's Gate 3 - Digital Deluxe Edition DLC | **INVALID**: observation category `content` is not allowed | zero sampled reviews; weak placeholder provenance |
| 1 | 1000360 | Hellish Quart | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1003590 | Tetris® Effect: Connected | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1003890 | Blacksad: Under the Skin | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1025440 | Fantasy General II | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1034860 | GRANDIA HD Remaster | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1047010 | Synergia | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1062040 | Dragon Star Varnir | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 1071870 | Biped | valid | zero sampled reviews; weak placeholder provenance |
| 1 | 107310 | Cthulhu Saves the World | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1077970 | Dry Drowning | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1079800 | Pistol Whip | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1082710 | Bug Fables: The Everlasting Sapling | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1083790 | Deathbulge: Battle of the Bands | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1104380 | The Room VR: A Dark Matter | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1143810 | Black Skylands | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1147560 | Skul: The Hero Slayer | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1152300 | Atelier Ayesha: The Alchemist of Dusk DX | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1152310 | Atelier Escha & Logy: Alchemists of the Dusk Sky DX | valid | zero sampled reviews; weak placeholder provenance |
| 2 | 1157390 | King Arthur: Knight's Tale | valid | zero sampled reviews; weak placeholder provenance |

All 20 dossiers otherwise have the expected current appid order, non-empty titles, 20-day TTL, generated/expires timestamps separated by exactly 20 days, non-empty summaries/observations, allowed sentiment `neutral`, recurrence `anecdotal`, `mention_count=1`, `evidence_languages=["store"]`, empty conflict arrays, two recorded lane objects, and Steam-prefixed provenance URLs. Group-level immutable descriptor bindings and appid ordering are correct.

The validator would therefore reject only `App_2378500` today, but **all 20 are semantically suspect as Steam-review dossiers** because the same runtime-access failure pattern is encoded in every one.

## Defect register

### FDS-01 — Worker prompt does not expose the exact canonical dossier schema/enums

Severity: **HIGH / live blocker already reproduced**  
Affected surfaces: `config/taste_steam_review_dossier_worker_prompt.md`, `config/taste_steam_review_dossier_contract.json`, `scripts/taste_steam_review_dossier.py`, CI fixtures.

Evidence:

- Contract V2 declares exact allowed observation categories: `mechanics`, `structure`, `pacing`, `progression`, `repetition`, `difficulty`, `friction`, `multiplayer`, `coop`, `localization`, `translation`, `voice`, `font`, `encoding`, `regional`, `other`.
- Canonical validator enforces that enum exactly.
- Worker prompt only describes categories in prose (`mechanics`, `structure`, `pacing`, etc.) and says each output must contain a “valid `TASTE-STEAM-REVIEW-DOSSIER-V1`”; it does **not** give the exact dossier JSON schema or exact category enum.
- Live worker emitted `category:"content"` for `App_2378500`, a reasonable natural-language category for DLC content but not a canonical enum value.
- Prompt also does not specify serialized fields such as `evidence_languages`, `mention_count`, exact sentiments, exact recurrence values, all per-field type/length constraints, or exact provenance subfield requirements. Future failures analogous to `content` are therefore possible even after fixing that one word.
- Contract `required_dossier_fields` lists appid/title/timestamps/TTL/summary/observations/conflicts/review_sample/provenance, while the validator additionally requires top-level `schema` and `schema_version`. The schema name is declared elsewhere, but the required-field list itself is not a complete machine-consumable dossier schema.
- Validator has an `evidence_languages` enum (`russian`, `non_russian`, `mixed`, `store`, `store_and_reviews`) that is not surfaced in the active worker prompt and is not exposed as an equivalent exact enum in Contract V2.

Root cause: the live worker is asked to manufacture a structured object from a prose contract while the final gate is a stricter Python implementation. There is no single exact worker-readable dossier schema shared by prompt, contract and validator.

Recommended repair:

- Make one canonical machine-readable dossier schema/enum source authoritative.
- Render or copy its exact required fields/enums/type rules into the repository worker prompt, or explicitly require/read a compact schema file that is small enough for the scheduled worker.
- Make validator rules derive from or be regression-checked against that same source.
- Do not patch only `content`; close all hidden enum/type/required-field gaps in one batch.

Required tests:

- Golden valid dossier generated from the worker-facing schema.
- Negative matrix for every enum, including `content`.
- Static assertion that worker-facing allowed categories/evidence-language/sentiment/recurrence sets exactly equal canonical validator sets.
- Required-field and unknown-field policy tests.

### FDS-02 — Evidence stop semantics disagree across contract, prompt, validator and tests

Severity: **HIGH / systematic pipeline risk**  
Affected surfaces: sampling contract, worker prompt, `_validate_review_sample`, test fixtures.

Evidence:

Contract sampling exposes exactly three stop conditions:

1. `two_consecutive_batches_add_no_material_recurring_theme_or_conflict_change`
2. `source_exhausted_or_sparse`
3. `hard_ceiling_reached`

But canonical validator only requires `lane.stop_reason` to be a non-empty string; it does not enforce those values. The active worker prompt describes stop behavior in prose but does not instruct the worker to serialize one of the exact canonical values.

Current live groups use a fourth value in every lane:

`steam_review_bodies_not_exposed_by_accessible_runtime_surface`

Current regression fixtures use another noncanonical value:

`stable_after_two_batches`

Both pass the canonical validator. CI therefore currently *teaches* and accepts behavior that contradicts the contract enum.

Root cause: stop condition semantics are descriptive in contract/prompt but are not canonicalized at the validation boundary.

Recommended repair:

- Define exact serialized stop reasons and validate them.
- Distinguish **source truly exhausted/sparse** from **source exists but the worker runtime cannot access review bodies**. These are operationally different and must not share one value.
- Decide contractually whether `source_access_unavailable` can yield a usable reduced-evidence dossier or must yield unresolved work. If unresolved, ownership/retry remains GitHub control plane.

Required tests: every allowed stop reason, every forbidden stop reason, zero-sample sparse source, zero-sample source-access failure, and mismatch between lane reason and observed counts.

### FDS-03 — Current group 1/2 dossiers do not prove Steam-review evidence and provenance validation is too weak

Severity: **HIGH data-quality defect**  
Affected surfaces: all 20 pending dossiers, provenance validator, downstream semantic trust.

Evidence across all 20 pending dossiers:

- `sampled_russian=0`
- `sampled_non_russian=0`
- `sampled_total=0`
- both lane `sampled=0`
- review provenance query explicitly says the accessible runtime exposed aggregate metadata but not review bodies
- all observations cite only `evidence_languages:["store"]`
- `sample_ids_sha256`, `store_description.content_sha256`, and `steam_reviews.source_refs_sha256` are all the same value `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`; that digest is SHA-256 of the canonical empty JSON list `[]`
- `steam_reviews.url` is a store-page `#app_reviews_hash` anchor, not evidence that any review body was actually captured

The current validator accepts this because it checks hash shape but not hash meaning, Steam URL prefix but not appid/source binding, two lane names but not actual review access, and nonnegative counts but not a minimum sample or evidence-state semantics.

This is not merely “some games have no reviews”. Public Steam pages for group 3 currently show abundant review populations while the accessible text surface still does not expose review bodies. Examples observed during this recon on 2026-09-15:

- White Shadows (`1158890`): ~1,871 total reviews.
- Trepang2 (`1164940`): ~12,141 English reviews.
- Necesse (`1169040`): ~12,471 English reviews.
- STAR WARS Jedi: Fallen Order (`1172380`): ~83,754 English reviews.

Therefore group 3’s halt is **systematic runtime evidence-access failure, not source sparsity** for at least several planned items. Groups 1/2 already encoded that same access failure as zero-review dossiers instead of stopping.

Root cause: the pipeline has no canonical evidence-availability state. The worker made two different choices under the same runtime limitation: publish store-only zero-review dossiers for groups 1/2, then fail closed during group 3.

Recommended repair:

- Canonically distinguish `reviews_sampled`, `source_sparse/exhausted`, and `review_source_access_unavailable`.
- Require provenance to bind to the dossier appid and to actual captured/source identifiers.
- Do not let a placeholder/empty digest masquerade as store content provenance.
- Define downstream semantics for a valid reduced-evidence/store-only dossier if that state is permitted; otherwise mark the item unresolved and let GitHub own retry/exception handling.
- Verify that the scheduled worker actually has a repeatable source surface capable of retrieving review bodies before requiring 594 dossiers under this contract.

Required tests: provenance URL/appid mismatch, placeholder hashes, captured timestamp requirements, zero review samples against abundant-source/unavailable state, and a real/synthetic worker-evidence fixture.

### FDS-04 — Canonical dossier validator is not type/identity/consistency strict enough

Severity: **MEDIUM-HIGH latent correctness defects**  
Affected surface: `scripts/taste_steam_review_dossier.py`, buffered validation.

Proven gaps:

- **Title identity is not bound.** Buffered validation binds dossier order/appids to descriptor appids, but never checks dossier `title` equals the descriptor item title. A worker can persist a wrong non-empty title for the right appid.
- **JSON booleans pass several integer checks.** Python `bool` is an `int`; `schema_version:true` compares equal to `1`, and boolean `mention_count`, sampled counts and batch counts can pass current `isinstance(value, int)` checks under some combinations.
- **Additional fields are accepted.** There is no strict additional-field policy except a blacklist for raw review/personal/commercial keys. Regression fixtures themselves include an extra top-level `key` not required by Contract V2, demonstrating permissive canonical acceptance.
- **Duplicate observations are accepted.** No duplicate statement/object check exists.
- **Observation/sample consistency is not checked.** Recurrence `mention_count` is not bounded by review sample counts or tied to `evidence_languages`.
- **Lane structure is set-based, not exact.** The validator checks the set of lane language scopes equals `{russian, non_russian}`, so duplicate lane objects can coexist and lane-level sampled counts are not reconciled to top-level Russian/non-Russian counts.
- **Provenance URLs are not appid-bound.** Any `https://store.steampowered.com/...` store/review URL can satisfy a dossier for a different appid.
- **Review provenance detail is mostly optional.** Review capture time/query/filter/source hash is not required by the validator even though the worker prompt relies on provenance to prove both lanes were attempted.
- **Store/review capture timestamps are not parsed or freshness-checked.** Only dossier generated/expires timestamps are parsed.
- **Ingest accepts future-generated dossiers.** `validate_dossier` verifies generated/expires arithmetic but does not apply `dossier_state`’s future-time guard during persistence; a future-dated dossier can be accepted and only be classified invalid later during a future daily preparation.

Current group 1/2 values do not exploit the boolean/title/duplicate defects, so these are latent validator gaps rather than extra current-file failures.

Recommended repair: define strict JSON types and identity bindings in the canonical schema, reject bool where integer is intended, bind title and provenance to descriptor/appid, reconcile lane counts, define duplicate/additional-field policy, and run future-time validation before canonical persistence.

Required tests: wrong title, numeric-vs-string appid policy, boolean schema/counters, duplicate lanes, lane/top-level count mismatch, duplicate observations, wrong provenance appid, missing capture metadata, future generated time, and unknown fields.

### FDS-05 — Current create-only state has no safe same-snapshot recovery path

Severity: **BLOCKER for next live invocation**  
Affected surfaces: worker prompt, inbox lifecycle, buffered drain, operator recovery contract.

Current deterministic group-1 file exists, canonical expected sequence is still 1, and that file is invalid. The active rules are individually correct but jointly deadlock:

- worker rule: if deterministic current-expected artifact exists and canonical progress has not advanced, stop; no overwrite, rename, alternate retry filename, skip or scan-ahead;
- drain rule: invalid current expected group blocks it and all later groups;
- accepted cleanup only deletes groups after successful validation/persistence;
- there is no GitHub-owned invalid-artifact quarantine/removal/replacement transition.

Therefore another scheduled invocation must stop at existing g1 before doing useful work. Group 2 is also stranded behind group 1. Under a stricter evidence repair, both current files should be treated as needing replacement, not only the single `content` field.

Architecture preflight for repair:

- Current control-plane owner is GitHub and must remain GitHub.
- Contract already assigns validation/persistence/cleanup/retry-unresolved authority to GitHub.
- The worker must not gain overwrite/retry/backlog authority.
- No new ChatGPT-owned queue/retry stage is required.

Recommended repair: add one explicit **GitHub-owned** recovery transition for a validator-proven invalid deterministic expected artifact, e.g. quarantine/remove under controlled policy and permit the same deterministic path to be created again after correction. Do not introduce alternate retry filenames. Repair both known pending groups in one controlled recovery batch after the schema/evidence rules are finalized.

Required tests: invalid expected artifact → authorized recovery → deterministic same-path republish → contiguous drain; later pending groups remain intact until revalidated; no alternate filenames; worker still stops on unhandled existing artifact.

### FDS-06 — Buffer lifecycle lacks implemented stale-snapshot cleanup and lost-wakeup reconciliation

Severity: **MEDIUM operational debt / can accumulate or strand work**  
Affected surfaces: daily rollover, inbox cleanup, workflow wake semantics.

Evidence:

- `plan_buffered_drain` correctly treats old-snapshot files as inert.
- Existing regression explicitly confirms an old snapshot artifact remains present after a new snapshot is considered.
- `write_worker_projection` removes old **descriptor directories**, but no equivalent implementation was found for old `data/ai_inbox/taste_steam_review_dossiers` files.
- Contract assigns stale-buffer cleanup to GitHub, but current daily builder stages manifest/index/descriptors and does not stage/delete the inbox.
- Thus daily rollover can escape an old deadlock by generating a new snapshot, but leaves stale production inbox artifacts behind.
- Ingest is triggered by inbox path pushes and then drains current main state. If a valid create-file commit lands but the corresponding ingest wake is lost/cancelled externally, a later worker invocation sees the existing deterministic expected artifact and must stop; it cannot recreate the file to generate a new push. There is no periodic/state-based GitHub reconciliation trigger dedicated to already-present pending artifacts.

Recommended repair: implement bounded GitHub-owned stale inbox cleanup at daily rollover and define a GitHub-owned reconciliation path for valid pending current-snapshot artifacts whose wake was missed. Prefer integrating this into existing writer workflows rather than creating a new ChatGPT retry loop.

Required tests: next-day rollover deletes/quarantines old-snapshot inbox files while preserving current-snapshot files; lost-wakeup valid artifact can be drained by GitHub state reconciliation; cleanup cannot mutate canonical progress by itself.

### FDS-07 — CI/regression coverage did not exercise the actual worker/validator contract boundary

Severity: **HIGH process defect; direct reason `content` reached live acceptance**  
Affected surfaces: `validate-taste-dossier-buffered.yml`, daily/buffered test modules, worker prompt validation.

What existing tests do cover well:

- 10/10/partial group partitioning;
- compact descriptor/index exactness and same-snapshot descriptor immutability;
- pointer advancement;
- missing/mismatched descriptor fail-closed behavior;
- future buffered groups waiting behind gaps;
- maximal contiguous prefix drain;
- invalid group blocking later groups;
- replay idempotence;
- same-day snapshot preservation;
- workflow staging and shared serialization wiring.

What they do **not** cover:

- exact worker prompt ↔ validator enum parity;
- a realistic worker-produced dossier fixture;
- unsupported `content` category negative case;
- evidence-language enum parity;
- exact stop-condition parity (fixtures themselves use noncanonical `stable_after_two_batches`);
- zero-review source-access-unavailable semantics;
- provenance semantic validation;
- title binding;
- bool-as-int and strict JSON types;
- unknown/duplicate field policy;
- invalid-artifact recovery lifecycle;
- stale inbox cleanup;
- lost wake-up reconciliation.

Root cause: CI is strong on control-plane transport invariants but uses hand-built always-valid dossier fixtures and does not test the semantic serialization boundary used by the scheduled worker.

Recommended repair: add a contract-conformance test suite that validates worker-facing schema/prompt against the exact canonical validator and includes golden/negative dossier fixtures. Keep existing transport tests; add semantic-contract tests rather than replacing transport coverage.

## Prompt ↔ contract ↔ validator matrix

| Surface | Contract V2 | Worker prompt | Canonical validator | Result |
|---|---|---|---|---|
| dossier schema id/version | schema declared; required-field list omits schema/version | says produce valid V1 but no field layout | exact V1 + version 1 required | underspecified worker/contract list |
| required top-level data | list present | not enumerated | individually checked | worker underspecified |
| observation category | exact contract enum | prose categories only | exact hardcoded enum | **live mismatch** |
| sentiment | exact enum | neutral prose, no serialization enum | exact hardcoded enum | underspecified worker |
| recurrence | exact enum/guidance | only `anecdotal` explicitly serialized | exact hardcoded enum | underspecified worker |
| evidence_languages | no equivalent exact V2 enum found | not specified | hidden hardcoded enum | validator-only contract |
| mention_count | recurrence guidance implies counts | field not specified | integer threshold rules | worker underspecified |
| sampling ceilings | exact | copied/described | enforced | aligned |
| stop reasons | exact 3 contract conditions | behavior prose only | any non-empty string | **mismatch** |
| two lane names | exact | exact Russian/non-Russian | set equality | mostly aligned; duplicates/count reconciliation missing |
| minimum usable review evidence | not explicit | says inspect reviews | zero is accepted | ambiguous |
| evidence access failure | no canonical state | no deterministic rule | arbitrary stop string accepted | **missing semantic state** |
| store provenance | intended provenance | general guidance | URL prefix + 64-hex hash | too weak |
| review provenance | intended both-lane proof | general guidance | Steam URL only + lane records elsewhere | too weak |
| title identity | descriptor contains title | worker sees title | no expected-title check | validator gap |
| generated/expires/TTL | 20-day current snapshot TTL | preserve index TTL | arithmetic + expected TTL | aligned for current files |
| future generated time at ingest | freshness model rejects future later | not explicit | not rejected during ingest | validator gap |
| additional fields | no strict policy | not explicit | mostly accepted | ambiguous/permissive |
| duplicate observations | no explicit policy | not explicit | accepted | ambiguous/permissive |

## Group 3 evidence-access diagnosis

Group 3 planned appids are `1158890, 1159290, 1161590, 1164690, 1164940, 1169040, 1172380, 1178830, 1179080, 1179210`.

The worker reached this descriptor in the same invocation after publishing groups 1 and 2, so descriptor traversal/read size was no longer the blocker. It stopped before creating g3 because it could not obtain enough Steam/web evidence for every item.

Public Steam store pages prove that at least several of these are not sparse sources; they have thousands to tens of thousands of reviews. The accessible page text provides aggregate review counts/ratings but not individual review bodies. This matches the live worker’s group1/2 provenance text and demonstrates a **surface-capability mismatch** with a contract that expects adaptive review-body sampling.

Assessment: expected to be **systematic**, not rare, unless a different reliable review-body source surface is made available to the scheduled worker or the contract explicitly supports a reduced-evidence state.

## Compact traversal / workflow / rollover edge-case sweep

No defect found in these already-implemented invariants:

- N→N+1 local traversal uses exact descriptor reads and sequence+1 only.
- Group 2 can be published before canonical group-1 acceptance; live run proved it.
- A future group can wait behind a gap without advancing canonical progress.
- Drain accepts only maximal valid contiguous prefix and stops at first gap/invalid group.
- Current workflow checks out `main`, so the triggering commit is a wake signal rather than stale authority.
- Pre-AI builder and ingest workflow share concurrency group `taste-steam-review-dossier-canonical-writer` with `cancel-in-progress:false`.
- Same-day daily snapshot is preserved instead of rebuilt/reset.
- Compact same-snapshot descriptors are immutable; only the index progress pointer changes.
- Old descriptor trees are removed when a new snapshot projection is written.
- Partial final group is represented correctly.
- Accepted group replay does not advance canonical progress twice.

Remaining lifecycle defects are FDS-05/FDS-06: invalid-existing recovery, stale **inbox** cleanup, and missed-wake reconciliation.

## Minimal repair batches

### Repair batch A — `dossier-schema-evidence-contract-closure`

One coherent batch, not per-field fixes:

- establish one exact worker-readable dossier schema;
- align contract, prompt and validator enums/required fields/types;
- formalize evidence availability and exact stop reasons;
- strengthen provenance/title/count/timestamp consistency;
- reject placeholder/semantically invalid evidence where required;
- add full semantic contract regression matrix and realistic worker-produced golden fixtures.

Likely surfaces: contract, worker prompt, dossier validator, buffered validator where descriptor-title binding belongs, dossier-specific tests, PR validation workflow. No Taste Semantic Producer changes.

### Repair batch B — `dossier-buffer-recovery-lifecycle`

One GitHub-control-plane batch:

- add authorized recovery for validator-proven invalid deterministic expected artifacts without alternate filenames;
- reconcile current g1/g2 under the repaired schema/evidence rules in one controlled operation;
- add stale old-snapshot inbox cleanup at rollover;
- add GitHub-owned reconciliation for already-present valid pending artifacts after missed wake;
- add recovery/rollover/reconciliation regression tests.

Do not transfer retry/backlog ownership to scheduled ChatGPT and do not add a ChatGPT-managed recurring queue.

## Preconditions before the next live `Run now`

1. Repair batch A merged and CI green.
2. Repair batch B merged and current invalid/superseded pending g1/g2 resolved by the authorized GitHub-owned path.
3. Canonical expected sequence and compact index agree.
4. No existing deterministic invalid artifact remains at the current expected sequence.
5. A concrete evidence policy/source has been verified for review bodies, or the reduced-evidence/unavailable state has been explicitly authorized and validated.
6. Only then perform one fresh live acceptance invocation.

## Final status

`sweep_complete_repair_batch_ready`

The sweep is complete. The repo is not ready for another live scheduled invocation yet. No runtime/config/code, production artifacts, Scheduled Task UI, manual workflow dispatch, or Taste Semantic Producer state was changed by this task. The only write is this durable report.