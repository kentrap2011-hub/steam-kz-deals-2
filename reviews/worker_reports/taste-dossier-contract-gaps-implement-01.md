# Taste Dossier Contract Gaps Implement 01

Status: `complete_ready_for_live_acceptance`

Date: 2026-09-17

Task: `WORKER_TASK_TASTE_DOSSIER_CONTRACT_GAPS_IMPLEMENT_01.md`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## Executive result

The seven proven contract gaps from `reviews/worker_reports/taste-dossier-contract-gap-audit-01.md` were re-evaluated against the post-PR-#36 implementation baseline and closed without changing the GitHub/Scheduled-ChatGPT ownership boundary, without weakening the existing evidence/privacy guards, and without changing canonical group size `3`.

Implementation PR `#38` (`Close Taste dossier contract gaps 01`) was merged to `main` as `72193e9b221ee68c7673d8c8901aa1734f29bafc`. Its final head was `7dfc852ad45a299e5a9d5fd95676cf5f983d84fb`. The canonical PR validation workflow `Validate buffered Steam review dossier runtime`, run `35175218825`, completed successfully.

The merge automatically triggered the normal GitHub-owned `Build pre-AI deterministic payload` workflow. No manual workflow dispatch and no Scheduled Task `Run now` were used. Activation run `35175306164`, job `105055599145`, completed with `success` and published fresh canonical state in commit `f44896de65e7809339716fc1cb964be0e8e70fba` (`Refresh atomic pre-AI payload`).

The fresh canonical dossier snapshot is:

`057b53265eb1238ec4543a355ba22ef769b5ea2638e9e1c5276a9c01d972605f`

Its truthful starting state is:

- prepared: `634`;
- completed: `0`;
- remaining: `634`;
- canonical expected sequence: `1`;
- group count: `212`;
- current checkpoint/group size: `3`;
- full backlog complete: `false`.

The new canonical manifest, worker index, and immutable group descriptors carry the same content-complete compatibility binding, including schema/contract revisions and canonical content hashes plus the worker-prompt SHA. The old pre-activation snapshot `adaccfbc4cd43faf4d7ea52e1a018adb66c785468959d5a6f8a64c1f8ade139d` has the prior coarse binding only and cannot be rebound to or accepted by the new plan.

## START / architecture gate

The repository START gate and architecture preflight were completed before implementation. Work was confined to `kentrap2011-hub/steam-kz-deals-2`; no other repository was used.

Architecture result: PASS.

The implementation preserves these boundaries:

1. GitHub remains the owner of canonical scope, order, snapshot identity, immutable group plan, progress, strict validation, persistence, recovery and completeness.
2. Scheduled ChatGPT remains a bounded research/synthesis worker with create-only transport.
3. Worker pre-publication validation remains a publication guard over the exact canonical buffered validator implementation, not a second validation truth source or control plane.
4. No new queue, scheduler, retry manager, backlog manager or recurring production stage was introduced.
5. Immutable transport artifacts remain immutable.
6. Canonical group size remains `3`.
7. Package-member and DLC identity behavior was not intentionally changed.
8. Downstream Taste-fit/ranking/pricing/commercial logic was not changed by this task.
9. Existing evidence and compact-provenance guards were retained.

## GAP-01..07 reconciliation

| Gap | Reconciliation | Closure / proof |
|---|---|---|
| GAP-01 — already-expired dossier could advance progress | `implemented_now` | Canonical strict acceptance now rejects a dossier when `now >= expires_at_utc` while preserving the existing bounded future-skew rule. The same rule is reached by pre-publication because it calls the canonical buffered validator. Regression proves an expired-but-formula-valid dossier fails both pre-publication and canonical buffered validation and does not advance progress. |
| GAP-02 — one physical feedback item/source could be double-counted through URL aliases | `implemented_now` | Strict validation now derives canonical physical locator identities, normalizing host/path, dropping fragments and known tracking query noise, and rejecting duplicate/aliased feedback items and aliased physical sources. Regression proves tracking/fragment aliases cannot manufacture recurrence or multi-source diversity while genuinely distinct item locators on the same discussion surface remain distinct. |
| GAP-03 — review-list/search/index/vague refs could count as an attributable feedback item | `implemented_now` | Counted feedback records now require an item-level stable locator. Known collection/search/index shapes and vague human-readable refs are rejected, while non-identifying stable item locators remain allowed. No username/profile identity or raw review text is required. |
| GAP-04 — old dated source could be labeled `recent` | `implemented_now` | The active evidence contract now defines `recent_max_age_days: 365`. For a non-null publication date, `<=365` days must be `recent` and `>365` days must be `older`, relative to dossier generation date. Boundary and old-date/false-recent regressions are present. The explicit undated path remains available without inventing dates. |
| GAP-05 — Russian attempt state was only checked in the forward direction | `implemented_now` | Validation is now bidirectional: `found_and_used` still requires bound Russian/mixed feedback, and any actually bound Russian/mixed feedback requires `russian_attempt=found_and_used`. Both contradictory non-found/unavailable states are regression-tested. |
| GAP-06 — conflict strength could be asserted without attributable feedback | `implemented_now` | The preferred player-feedback-bound model was adopted. Every conflict now carries `mention_count`, `source_ids`, and `player_feedback_ids`; count and recurrence thresholds match observation semantics. Official/professional/context-only evidence cannot manufacture player recurrence. |
| GAP-07 — compatibility binding was incomplete and semantic changes could survive same-day preservation | `implemented_now` | Binding now includes schema/contract revisions, canonical schema/contract content hashes, and worker-prompt content SHA; dossiers must copy the exact active binding; worker index and every immutable descriptor expose it; same-day binding change rebuilds snapshot identity; old dossiers/artifacts cannot be rebound. The workflow push-path trigger subpart had already been incidentally closed on the current-main baseline after PR #36 for the active schema/web-contract/prompt files, so no redundant trigger mechanism was added; a focused regression preserves that fact. |

No audit gap was silently dropped.

## Shared canonical validation path

The implementation retains the single-source validation rule introduced by PR #36:

`scripts/taste_steam_review_dossier_prepublication.py`

resolves the exact canonical descriptor for the candidate group and calls:

`taste_steam_review_dossier_buffered.validate_buffer_artifact`

That is the same buffered acceptance implementation used by canonical GitHub ingestion. New GAP-01..06 rules therefore reach worker pre-publication and canonical ingestion through the same strict path rather than through a duplicated handwritten pre-publication checklist.

The focused GAP-01 regression explicitly proves parity: the same expired complete-group candidate fails both pre-publication validation and direct canonical buffered validation, and buffered drain reports no accepted progress.

## Implementation summary

### Freshness at acceptance

Strict validation now distinguishes structural expiry consistency from actual acceptability. A dossier still must satisfy:

`expires_at_utc == generated_at_utc + ttl_days`

and the existing maximum future skew, but canonical acceptance additionally requires the dossier to still be fresh at the time of acceptance. The stale-state helper can still classify an already-persisted dossier without pretending that stale data is a valid new ingest.

### Physical feedback/source identity

Feedback-record identity is no longer equivalent to a literal locator string. URL identity normalization removes obvious non-identity variance such as fragments, tracking parameters, redundant path slashes, trailing-slash noise, and normalized host form. Duplicate physical item identities are rejected before recurrence counting. Parent source locators receive corresponding alias protection so `source_id` duplication cannot create false multi-source evidence.

### Item-level locator enforcement

Player-feedback records counted toward observations/conflicts must locate a concrete attributable item, not merely a collection or search surface. Source/domain-aware checks reject known Steam/Reddit collection shapes and generic search/index/list locators. Stable non-identifying machine-like `public_ref` values remain supported.

### Mechanical recency

The active evidence contract now makes the temporal boundary explicit at `365` days. Dated provenance cannot satisfy a current-state claim by self-labeling an old source as recent. Unknown publication dates remain representable as `null`; the worker is not forced to fabricate a date.

### Russian attempt coherence

The three-state Russian attempt model is now mutually coherent with actual bound evidence. The validator checks both implications, including Russian/mixed evidence used by conflicts as well as observations.

### Conflict evidence strength

Conflicts now use the same auditable player-feedback count/recurrence model as observations. `mention_count` must equal distinct bound feedback records, recurrence thresholds are enforced, record sources must also appear in conflict `source_ids`, and context-only sources cannot substitute for player recurrence.

### Content-complete compatibility binding

`current_worker_contract_binding()` now contains:

- evidence contract schema/version;
- evidence contract revision;
- evidence contract canonical SHA-256;
- worker schema name/version;
- worker schema revision;
- worker schema canonical SHA-256;
- dossier schema/version;
- worker prompt revision;
- worker prompt content SHA-256.

A dossier whose binding differs from the active binding is rejected as missing/stale. The canonical daily manifest owns the binding, while the compact worker index and each immutable group descriptor expose the exact same binding so the worker can prove liveness against the intended semantic contract.

## Focused implementation validation

Implementation PR: `#38`  
Base implementation SHA: `51f59dc9436bdc980832f45311fb582ebe45d268`  
Final PR head: `7dfc852ad45a299e5a9d5fd95676cf5f983d84fb`  
Merge commit: `72193e9b221ee68c7673d8c8901aa1734f29bafc`  
PR validation run: `35175218825`  
Result: `success`

The focused contract-gap suite covers GAP-01..07 and runs alongside the existing dossier suites. During implementation, stricter fail-closed production guards exposed legacy test fixtures that omitted the new compatibility binding or expected a later validation error than the new item/temporal guards. Those fixtures/expectations were aligned to the active contract; production validation was not weakened to make tests pass.

## Post-merge ACTIVATE / VALIDATE

Merging PR #38 automatically triggered the normal GitHub-owned pre-AI workflow because active semantic contract/runtime paths changed.

Activation workflow:

- workflow: `Build pre-AI deterministic payload`;
- run: `35175306164`;
- job: `105055599145`;
- triggering head: `72193e9b221ee68c7673d8c8901aa1734f29bafc`;
- status: `completed`;
- conclusion: `success`;
- atomic state commit: `f44896de65e7809339716fc1cb964be0e8e70fba` (`Refresh atomic pre-AI payload`).

The activation job completed all dossier-relevant steps successfully, including:

- `Prepare fixed daily full Steam review dossier backlog`;
- `Reconcile already-present dossier inbox state`;
- `Regression test fixed daily dossier snapshot control plane`;
- `Commit atomic pre-AI payload`.

The post-build dossier regression stage completed successfully with:

- daily snapshot suite: `9` tests OK;
- buffered submission suite: `8` tests OK;
- strict recovery suite: `16` tests OK;
- pre-publication suite: `8` tests OK;
- contract-gap suite: `10` tests OK.

The activation build itself reported:

- `mode: built_new_daily_snapshot`;
- `group_plan_added: true`;
- `web_evidence_binding_added: true`;
- `stale_inbox_quarantined_count: 0`;
- reconciliation status `no_contiguous_work_available`, with zero persisted groups and truthful progress still at zero.

## Fresh canonical snapshot and progress

Canonical manifest:

`data/production/pre_ai/taste_steam_review_dossier_work.json`

Activation snapshot:

`057b53265eb1238ec4543a355ba22ef769b5ea2638e9e1c5276a9c01d972605f`

State immediately after activation:

- prepared date: `2026-09-17`;
- prepared required: `634`;
- completed required: `0`;
- remaining required: `634`;
- current checkpoint count: `3`;
- group count: `212`;
- canonical expected sequence: `1`;
- `full_backlog_complete: false`;
- status: `work_required`.

The worker index at:

`data/production/pre_ai/taste_steam_review_dossier_worker_index.json`

matches the manifest on snapshot id, prepared-required hash, group-plan hash, counts, expected sequence, source queue, TTL and compatibility binding.

Current `main` subsequently advanced through unrelated automated commercial-state commits, but the dossier worker index and first descriptor were re-read from current `main` during this closeout and still expose the same activation snapshot and binding.

## Active compatibility binding

The canonical manifest, worker index and first descriptor all expose exactly:

- `evidence_contract_schema`: `TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2`;
- `evidence_contract_version`: `2`;
- `evidence_contract_revision`: `contract-gaps-2026-09-17`;
- `evidence_contract_sha256`: `005ee310dc9cdf944fa77b3722864cce9f61274553c5f3736f3f9b32458d7dad`;
- `worker_schema`: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2`;
- `worker_schema_version`: `2`;
- `worker_schema_revision`: `contract-gaps-2026-09-17`;
- `worker_schema_sha256`: `683c310bf9ea7364485f5e39456bcde0f5fb4a8cdf0106bb96d6aa9ea25b73be`;
- `dossier_schema`: `TASTE-STEAM-REVIEW-DOSSIER-V2`;
- `dossier_schema_version`: `2`;
- `worker_prompt_revision`: `web-evidence-v2-prepublication-v1`;
- `worker_prompt_sha256`: `2f0542940200b6b3b775ff04bbca0f25c71d6717f755c6feba73a61d81165aaa`.

This proves compatibility is tied to semantic file content, not only to coarse V2 names/version numbers.

## First immutable group descriptor

Canonical first descriptor:

`data/production/pre_ai/taste_steam_review_dossier_worker_groups/057b53265eb1238ec4543a355ba22ef769b5ea2638e9e1c5276a9c01d972605f/g000001.json`

Verified fields:

- schema: `TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1`;
- sequence: `1`;
- start index: `0`;
- end index exclusive: `3`;
- group item count: `3`;
- appids, in exact order:
  1. `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC`;
  2. `1000360` — `Hellish Quart`;
  3. `1003590` — `Tetris® Effect: Connected`;
- items SHA-256: `48256e357c57025236475a74cadcc1c2c64b72cbd199287869abe454712ab6bf`;
- group SHA-256: `5b584c0e789371414b3abe6cbc1abaa106609fe76b11635f6833d74aa33a7835`;
- group-plan SHA-256: `61cc08c4eee1672dc46baf8a7d5748a4b0e5adaded439f9141eac7df07fa2fb6`;
- compatibility binding: exactly equal to manifest/index binding.

This directly confirms canonical group size remains `3`.

## Old incompatible snapshot/artifact rejection

Immediately before activation, the canonical snapshot was:

`adaccfbc4cd43faf4d7ea52e1a018adb66c785468959d5a6f8a64c1f8ade139d`

That snapshot carried the old coarse compatibility object containing schema/version names and `worker_prompt_revision`, but not the new schema revision/hash, evidence-contract revision/hash, or worker-prompt content hash.

After activation:

1. the canonical manifest snapshot id is `057b53265eb1238ec4543a355ba22ef769b5ea2638e9e1c5276a9c01d972605f`;
2. worker projection was regenerated only under the new snapshot directory;
3. old `adaccfbc...` worker descriptors were removed by the normal GitHub-owned projection synchronization; the old `g000001.json` path is absent in the activation commit;
4. pre-publication resolves the current immutable plan and explicitly rejects an artifact whose `snapshot_id` differs from the canonical manifest with `prepublication group snapshot_id does not match the current canonical manifest`;
5. strict dossier validation recomputes the current content-complete binding and rejects any dossier whose `web_evidence_contract_binding` is not exactly equal with `dossier web-evidence compatibility binding is missing or stale`;
6. focused GAP-07 regression proves same-day binding change creates a fresh snapshot identity and an artifact from the old snapshot cannot be accepted against the new manifest.

Therefore an old incompatible snapshot, descriptor, buffered artifact or dossier cannot silently satisfy or be rebound to the new compatibility identity. No accepted work was migrated across the incompatible binding and canonical progress started at `0/634`.

`stale_inbox_quarantined_count: 0` in this activation is not a bypass: there were no stale inbox files requiring movement. Snapshot/plan and compatibility checks make an old-bound artifact inert regardless, and the old worker projection was removed during the GitHub-owned rebuild.

## Scheduled Task boundary

Scheduled Task `Run now` was **not** launched during IMPLEMENT, activation or this post-merge validation.

This report therefore does not claim a successful live Scheduled ChatGPT production execution. The system is instead in the required state for that separate live acceptance boundary: if the Scheduled worker cannot execute the exact repository pre-publication validator, the already-active prompt remains fail-closed and must publish nothing.

## Acceptance checklist

- [x] GAP-01..07 reconciled against current main after PR #36.
- [x] GAP-01 already-expired ingress is rejected before progress advancement.
- [x] GAP-02 obvious physical feedback/source aliases cannot inflate recurrence/source diversity.
- [x] GAP-03 counted feedback requires an auditable item-level non-identifying locator.
- [x] GAP-04 dated `recent`/`older` classification is mechanically coherent at a 365-day boundary.
- [x] GAP-05 Russian attempt state is coherent in both directions.
- [x] GAP-06 conflict recurrence is bound to attributable player feedback/count semantics.
- [x] GAP-07 compatibility binding is content-complete across schema, evidence contract and worker prompt.
- [x] Worker index and immutable descriptors expose the exact active compatibility binding.
- [x] Same-day incompatible binding change causes a GitHub-owned fresh snapshot.
- [x] Old incompatible snapshot/artifacts cannot be rebound to the new plan.
- [x] Shared pre-publication/canonical validation parity is preserved.
- [x] Existing evidence/privacy guards remain active.
- [x] Canonical group size remains `3`.
- [x] Implementation PR CI passed.
- [x] Automatic GitHub-owned post-merge activation run passed.
- [x] Fresh canonical state is truthful at `0/634`, expected sequence `1`.
- [x] No manual queue/cache/progress/receipt edits were used.
- [x] No manual dossier artifact creation was used.
- [x] No Scheduled Task `Run now` was used.

## Final status

`complete_ready_for_live_acceptance`
