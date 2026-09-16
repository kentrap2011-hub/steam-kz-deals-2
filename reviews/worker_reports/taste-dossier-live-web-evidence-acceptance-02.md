# Taste Dossier Live Web Evidence Acceptance 02

Task ID: `taste-dossier-live-web-evidence-acceptance-02`
Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`
Mode: `READ / VALIDATE / ACCEPTANCE`
Status: `rejected_live_web_evidence_group1`

## Task
Validate the manually published fresh-snapshot group-1 transport artifact from commit `15b386859c945ce159ebb7fd35cfed6d00c3fb72`, prove or disprove GitHub-owned canonical acceptance, audit live V2 evidence quality, and do not run the Scheduled Task again.

## Architecture preflight
- GitHub remains owner of canonical scope/order, exact group plan, strict validation, ingestion, cache persistence, progress and expected sequence.
- Scheduled ChatGPT remains bounded to semantic web research plus create-only transport publication.
- This worker performed repository/GitHub observation and acceptance only. It did not dispatch workflows, rewrite queue/progress/cache/receipts, edit Scheduled Tasks, or create any recurring control-plane mechanism.
- Task-specific restriction overrides the normal worker progress-update convention: the only repository write by this worker is this durable report.

## Verified facts

### Exact group-1 transport binding
Canonical snapshot: `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`.

Canonical group-1 descriptor:
- sequence: `1`
- range: `[0,10)`
- prepared-required SHA: `f070bdff0c3e850c5498dd7377c393afbc32acdf0fc6ace515142405c9adabc1`
- group-plan SHA: `1a11584b8c22535946887c9c58d8eda6a63669d29fc1fd1b62c24db91363957c`
- items SHA: `3cc83d780e8da0d8f0eb025395f386cc340732511426c1214e65a189cd97ecfb`
- group SHA: `14fe28456bf2c6b400559cc848ad698a736b14c9f78274239759efa317836728`

Published transport artifact:
`data/ai_inbox/taste_steam_review_dossiers/6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53--g000001--14fe28456bf2c6b400559cc848ad698a736b14c9f78274239759efa317836728.json`

Transport commit:
`15b386859c945ce159ebb7fd35cfed6d00c3fb72` — `Publish Taste Steam review dossier group 1`.

The transport artifact and immutable descriptor match on snapshot, sequence, range, ordered appids, item SHA and group SHA.

### All ten group-1 items
GitHub-owned strict buffered ingestion accepted exactly one group and exactly ten dossiers. The persisted list in run `35102962980` contains all ten expected appids, so strict V2/schema/identity binding passed for every planned item:

| # | AppID | Canonical subject | Strict canonical ingest |
|---|---:|---|---|
| 1 | 2378500 | Baldur's Gate 3 - Digital Deluxe Edition DLC | PASS |
| 2 | 1000360 | Hellish Quart | PASS |
| 3 | 1003590 | Tetris® Effect: Connected | PASS |
| 4 | 1003890 | Blacksad: Under the Skin | PASS |
| 5 | 10150 | Prototype™ | PASS |
| 6 | 1015940 | Welcome to Elk | PASS |
| 7 | 1018800 | DEEEER Simulator: Your Average Everyday Deer Game | PASS |
| 8 | 1025440 | Fantasy General II | PASS |
| 9 | 1029690 | Sniper Elite 5 | PASS |
| 10 | 1034860 | GRANDIA HD Remaster | PASS |

The buffered validator calls `validate_dossiers_against_expected_items(...)` before persistence, so acceptance also proves the repository-defined strict checks passed, including exact planned appid/order/identity binding and rejection of prohibited raw-review/body/quote/username fields.

`App_2378500` remained its exact DLC subject (`Baldur's Gate 3 - Digital Deluxe Edition DLC`, appid `2378500`); it was not remapped to base game `1086940` and was not rejected merely for being DLC.

The prior hybrid package failure is absent: the fresh manifest uses `package-member-dossier-aggregation-v1`, retains the package-member mapping for `Sub_87601`, while the semantic worker group contains game appids only rather than the old hybrid package title/appid combination.

### Canonical GitHub acceptance
Automatic workflow `Ingest Steam review dossier checkpoint` was triggered by transport commit `15b3868...`:
- run: `35102962980`
- job: `104816750008`
- conclusion: `success`
- drain result: `accepted_group_count=1`, `accepted_dossier_count=10`, `accepted_sequences=[1]`
- next stop: `blocked_reason=gap`, `stop_sequence=2`
- canonical ingestion commit: `f37ea0ff19f8dac2a881702bfb4f34d02a6a9c98` — `Drain Steam review dossier buffer`

The canonical state after ingestion is coherent:
- `completed_required_count = 10`
- `remaining_required_count = 608`
- `canonical_expected_sequence = 2`
- `full_backlog_complete = false`

The group-1 transport file was deleted by the GitHub-owned drain after persistence, as designed.

### Group 2
Canonical group 2 exists only as the predeclared descriptor `g000002.json`, sequence `2`, group SHA `2ab633d6e03181e0d3a2855333d01ba87e50e523d635dcb87ccefe05c5361847`.

The corresponding deterministic group-2 inbox artifact is absent from current `main`, and canonical progress is still sequence `2` with 608 remaining. Commit history for the dossier inbox after `15b3868...` shows only the automatic `f37ea0f...` drain for this fresh snapshot; no later group-2 publication from this invocation is present. Older group-2 history belongs to earlier snapshots/runs and is not credited here.

Therefore the authoritative UI statement is consistent with repository truth: group 2 was researched only, not published or accepted in this invocation.

## V2 evidence-quality assessment

### What passed
- All ten persisted objects are `TASTE-STEAM-REVIEW-DOSSIER-V2` under the strict worker contract.
- Exact title/appid identity binding passed all ten.
- Compact provenance is used; raw review/post corpora, usernames and quotes were not persisted.
- Russian-attempt status fields are present and structurally valid.
- The set is not purely official/professional metadata: ordinary player-feedback source types are present.

### Substantive quality gap not caught by strict validation
The live group is **not acceptable as evidence quality**, despite canonical syntactic acceptance.

A representative audit of six canonical dossiers exposes a repeated semantic mismatch between the strength of prose and the recorded evidence:

1. `App_2378500` says Steam feedback is “overwhelmingly positive” and repeats that for Russian feedback, but both observations are `recurrence=anecdotal`, `mention_count=1`, from the same `steam_ru` source. The dossier is nevertheless marked `overall_strength=moderate` and `evidence_stable`.
2. `App_1000360` makes a generalized Russian-feedback claim from one anecdotal current source, and its stored Steam provenance path is semantically malformed: `https://store.steampowered.com/app/1000360Hellish?l=russian`.
3. `App_1003590` says players “repeatedly praise” core qualities while the supporting durable observation is explicitly one anecdotal mention (`mention_count=1`).
4. `App_1003890` says technical roughness “remains a recurring friction point”, but the declared supporting observation is `durable`, `anecdotal`, one older community source; there is no recent technical/current-state source bound to that claim. This violates the intended temporal discipline even though the schema cannot parse the prose-level word “remains”.
5. `App_1015940` records `russian_attempt=searched_not_found_or_insufficient`, yet the Russian Steam store page is still tagged `source_type=steam_reviews`, `player_feedback=true` and contributes to `source_mix_status=multi_source`. The representation therefore lets an insufficient RU attempt inflate the player-source mix mechanically.
6. `App_1025440` states that older community discussion records disagreement about translation quality, but the localization observation binds only `source_ids=["steam_ru"]`; the separate older `community` source is not bound to that localization observation. The persisted source/claim binding does not support the full sentence as written.

The same audit also shows a recurring provenance pattern where `?l=russian` Steam **store app pages** are classified as Russian `steam_reviews`/`player_feedback` current-state sources. A language/UI parameter alone is not compact review-level provenance proving that the cited player feedback itself is Russian. The current strict validator validates source flags, HTTPS/domain shape and source counts, but it does not validate this semantic correspondence or reconcile generalized prose with `anecdotal/1` recurrence.

This is precisely the task's fail condition: group 1 can be canonically ingested while a substantive evidence-contract gap remains outside strict validation. The result must therefore not be rubber-stamped as successful live V2 evidence acceptance.

## Changes
- Added only this report: `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-02.md`.
- No code, config, workflow, prompt, queue, production state, cache, progress, receipt or Scheduled Task changes were made by this worker.

## Production side effects
None caused by this acceptance worker. Observed pre-existing/automatic effects are limited to:
1. the user-confirmed external create-only group-1 transport publication (`15b3868...`), and
2. the repository-owned automatic canonical drain/persistence (`f37ea0f...`).

No Scheduled Task `Run now` was initiated here.

## Validation
- Exact immutable group-1 descriptor vs transport identity: PASS.
- Strict V2 validation and persistence of all 10 planned dossiers: PASS.
- Canonical progress advancement `0 -> 10`, remaining `618 -> 608`, expected sequence `1 -> 2`: PASS.
- Group-1 transport cleanup: PASS.
- Fresh package-member identity invariant / DLC exact identity: PASS.
- Group 2 publication/acceptance in this invocation: correctly absent.
- V2 semantic evidence quality: **FAIL** for the recurrence/claim-strength, temporal-source binding and RU provenance semantics described above.

## Unresolved
Strict validation currently accepts evidence whose source flags/counts are schema-valid but whose prose-level recurrence strength, current-vs-durable wording, RU-language provenance, or clause-to-source binding is materially weaker than the persisted claim.

## Status
`rejected_live_web_evidence_group1`

Canonical group-1 ingestion itself is proven successful; the overall live web-evidence acceptance is rejected because the persisted V2 evidence exposes a substantive contract/validator gap that the task explicitly requires acceptance to reject.

## Recommended next step
Create one bounded IMPLEMENT task to harden the V2 research/persistence guard so generalized or current-state claims cannot pass with contradictory `anecdotal/1` evidence and a Russian store-language page cannot mechanically count as Russian player-feedback evidence without an attributable player-feedback reference; then re-accept against a newly produced bounded group artifact under the existing GitHub-owned control plane.

## Exact refs
- Task: `WORKER_TASK_TASTE_DOSSIER_LIVE_WEB_EVIDENCE_ACCEPTANCE_02.md`
- Snapshot: `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`
- Group-1 descriptor: `data/production/pre_ai/taste_steam_review_dossier_worker_groups/6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53/g000001.json`
- Group-1 transport commit: `15b386859c945ce159ebb7fd35cfed6d00c3fb72`
- Automatic ingestion run/job: `35102962980` / `104816750008`
- Canonical ingestion commit: `f37ea0ff19f8dac2a881702bfb4f34d02a6a9c98`
- Worker index: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- Work manifest: `data/production/pre_ai/taste_steam_review_dossier_work.json`
- Web-evidence contract: `config/taste_steam_review_dossier_web_evidence_contract.json`
- Strict validator: `scripts/taste_steam_review_dossier_strict.py`
- Buffered validator/drain: `scripts/taste_steam_review_dossier_buffered.py`

Efficiency / reusable lesson: acceptance must audit semantic claim strength separately from strict schema success; canonical ingestion success alone is insufficient evidence-quality acceptance.