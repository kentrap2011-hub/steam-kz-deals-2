# Taste dossier prepublication validation + recovery implement 01

Status: `complete_ready_for_live_acceptance`

Date: 2026-09-17

Task: `WORKER_TASK_TASTE_DOSSIER_PREPUBLICATION_RECOVERY_IMPLEMENT_01.md`
Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

## Executive result

The blocked Taste Steam review dossier snapshot was recovered without mutating any published immutable group and without manually editing queue/cache/progress/receipts.

The worker publication path is now fail-closed before GitHub create-only publication: the worker-side pre-publication entrypoint calls the same repository implementation, `taste_steam_review_dossier_buffered.validate_buffer_artifact`, that canonical GitHub ingestion uses. A group that canonical strict validation would reject therefore fails before publication when that repository validator is executable. If the Scheduled ChatGPT environment cannot execute the exact repository validator, the worker prompt requires publishing nothing and stopping rather than substituting a reduced handwritten check.

Compact provenance now has a machine-enforced privacy/content guard that rejects author/user identity, author/profile-scoped URLs, and review/post content-like locator metadata. The existing evidence guard remains active and the canonical group size remains `3`.

Implementation PR `#36` merged to `main` as `3940fcf9de12519316938dbc723141023781aa05`. The merge automatically activated the normal GitHub-owned pre-AI rebuild/recovery path. GitHub Actions run `35157755703`, job `105001126796`, succeeded and created fresh snapshot `adaccfbc4cd43faf4d7ea52e1a018adb66c785468959d5a6f8a64c1f8ade139d`. Canonical progress remains `0/591`; expected sequence is `1`; the first descriptor contains exactly three items. The three old immutable artifacts from snapshot `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973` were moved by the normal GitHub stale-snapshot quarantine path as `100%` renames, not rewritten in place.

Scheduled Task `Run now` was **not** launched.

## START / architecture gate

Read before implementation:

- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- current `WORKER_TASK_TASTE_DOSSIER_PREPUBLICATION_RECOVERY_IMPLEMENT_01.md` from `main`;
- `CURRENT_TASK.md`;
- relevant dossier contracts, validator, worker prompt, recovery implementation and ownership contract;
- relevant rationale/route material before changing runtime/workflow responsibility.

Architecture preflight result:

1. GitHub remains owner of canonical snapshot, immutable group plan, progress, strict acceptance, persistence and recovery.
2. Scheduled ChatGPT remains a bounded research/synthesis worker with create-only transport.
3. Pre-publication validation is a publication guard over the existing canonical validator implementation; it does not become a second control plane, second queue, second retry loop or second validation truth source.
4. Recovery remains GitHub-owned. No interactive-chat mutation of immutable artifacts or progress is introduced.

## Defects reproduced from the blocked snapshot

The old active snapshot was:

`d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`

It had canonical progress `0/591` and expected group `1`.

Three immutable artifacts already existed in the active inbox:

1. `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000001--83d91127ece346690fb62af453938d80be6707c19ae6019ab85de6404b11d021.json`
2. `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000002--4bf163f8c62c39a7d6fed6b18fa24b64511c36bf964def36583b561ba7db4283.json`
3. `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000003--22af57a771861638ed2d5d493f604ba95e4f883d67c31fe6cde06d59cfc57694.json`

Focused reproduction preserved the known strict-validator failures rather than weakening them:

- Hellish Quart live shape: a `current` observation without recent current-state evidence is rejected.
- DEEEER Simulator live shape: `single_source_only` with more than one used player-feedback source is rejected.
- Sniper Elite 5 live shape: Russian `found_and_used` without a Russian/mixed player-feedback record actually bound to an observation is rejected.

The old artifacts also demonstrated the compact-provenance privacy/content problem classes:

- author/display attribution in `public_ref`, e.g. `contribution by ...` / `user review by ...`;
- Steam profile-scoped review URLs under `/id/<name>/...` or `/profiles/<steamid>/...`;
- content-like locator metadata such as `review summarized as ...`.

No raw review-body persistence was added or required.

## IMPLEMENT

### 1. Shared canonical pre-publication validation

Added:

- `scripts/taste_steam_review_dossier_prepublication.py`

The entrypoint resolves the exact immutable group descriptor from the canonical manifest/group plan, checks snapshot binding, then directly calls:

`taste_steam_review_dossier_buffered.validate_buffer_artifact`

This is the same function used by canonical buffered ingestion. There is no independent copy of the cross-field validation rules.

The worker prompt now requires constructing the complete candidate group ephemerally and running:

`python scripts/taste_steam_review_dossier_prepublication.py --artifact <ephemeral-candidate-group.json>`

before **any** GitHub create-file action.

Publication is allowed only after `status:"valid"`. On a validation failure the group is not published and no later group is attempted. If the exact repository validator cannot be executed, the prompt requires `prepublication_validator_unavailable`, publishes nothing, and stops fail-closed. A shortened handwritten validator is explicitly forbidden as a replacement.

### 2. Machine compact-provenance privacy/content guard

Added:

- `scripts/taste_steam_review_dossier_compact_provenance.py`

Updated the active V2 evidence contract and worker schema with a machine-readable compact-provenance policy. The canonical buffered validator now runs this guard after the existing strict dossier/evidence checks.

The guard rejects:

- author/user identity attribution in compact refs;
- profile-scoped path forms such as `/id/<name>/...`, `/profiles/<steamid>/...`, and configured equivalent identity paths;
- configured identity query parameters such as `author`, `user`, `username`, `profile`, `steamid`;
- URL text disguised as `public_ref`;
- review/post content-like summary metadata such as `summarized as ...`.

The policy requires omission of author identity rather than hashing/pseudonymization.

Neutral non-identifying locators remain permitted.

### 3. Evidence guard preserved

The implementation does not relax the existing strict evidence model. The old evidence/recovery test suite remains in the canonical PR workflow and passed together with the new focused tests. The three known cross-field failures above are now explicit pre-publication regressions proving parity with canonical acceptance.

### 4. Group size preserved

`config/taste_steam_review_dossier_contract.json` continues to define `checkpoint_size: 3`.

The focused regression asserts size `3`, and the fresh production descriptor `g000001.json` has:

- `start_index: 0`;
- `end_index_exclusive: 3`;
- appids `2378500`, `1000360`, `1003590`;
- group SHA `c9ec4036a383e5b354b6ec0c2cd85faeb39d95861feeb97f7c0099f6986eab58`.

## Focused validation / PR CI

Implementation PR: `#36`
Validated head: `742bbb10166d869bc7179d1e2f96521b5a18e1bc`
Canonical PR workflow run: `35157709471`
Job: `105000977445`
Result: `success`

The final canonical dossier PR job ran:

- daily snapshot regressions: `9` passed;
- buffered submission regressions: `8` passed;
- same-day preservation regressions: `4` passed;
- existing strict evidence/recovery regressions: `16` passed;
- new pre-publication suite: `8` passed;
- package identity regressions: `6` passed.

The new suite proves:

1. a valid complete size-3 group passes both pre-publication and canonical paths;
2. Hellish Quart known invalid cross-field shape fails before publication;
3. DEEEER known invalid source-mix shape fails before publication;
4. Sniper Elite 5 known invalid Russian-binding shape fails before publication;
5. username/display-name compact refs fail;
6. custom-name and numeric profile URLs fail;
7. a neutral locator passes while review-content-like summary metadata fails;
8. old-snapshot artifacts are inert under a fresh snapshot and stale cleanup does not advance progress.

An initial temporary focused CI attempt failed because the newly written test fixture timestamp was slightly in the future relative to CI wall-clock time. This was a regression-fixture defect, not a validator bypass; the fixture was corrected and the final canonical PR workflow above is green.

## RECOVER / ACTIVATE

No manual workflow dispatch and no Scheduled Task `Run now` were used.

Merging PR `#36` changed the active worker/evidence contract binding. That binding participates in dossier snapshot identity, so the existing normal GitHub-owned pre-AI workflow rebuilt the snapshot rather than rebinding old immutable group files.

Auto-triggered canonical workflow:

- workflow: `Build pre-AI deterministic payload`;
- run: `35157755703`;
- job: `105001126796`;
- triggering head: implementation merge `3940fcf9de12519316938dbc723141023781aa05`;
- result: `success`;
- generated state commit: `79741bb5c719d0ae8393649e8b291226a5fbd1d1` (`Refresh atomic pre-AI payload`).

The build produced:

- old snapshot: `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`;
- fresh snapshot: `adaccfbc4cd43faf4d7ea52e1a018adb66c785468959d5a6f8a64c1f8ade139d`;
- prepared count: `591`;
- completed count: `0`;
- remaining count: `591`;
- group count: `197`;
- canonical expected sequence: `1`;
- `full_backlog_complete: false`.

Therefore recovery did **not** create artificial progress.

The workflow reported `quarantined_stale_submission_count: 3` and committed each old artifact as a `R100` rename into:

`data/quarantine/taste_steam_review_dossier_inbox/stale/d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973/`

All three expected old filenames are present in that quarantine directory on `main`. This is the normal GitHub-owned stale-snapshot recovery route. No old artifact was overwritten with corrected content, no alternate immutable filename was published, and no manual queue/cache/progress/receipt repair was performed.

The same auto-run also executed the repository dossier regressions after rebuilding/reconciling state; the run completed successfully.

## Acceptance checklist

- [x] Worker has a mandatory pre-publication guard before create-only publication.
- [x] The guard executes the same canonical `validate_buffer_artifact` implementation used by GitHub ingestion.
- [x] Known Hellish Quart invalid shape fails before publication.
- [x] Known DEEEER invalid shape fails before publication.
- [x] Known Sniper Elite 5 invalid shape fails before publication.
- [x] Usernames/display names/author attribution are mechanically forbidden in compact provenance.
- [x] Author/profile-scoped URLs are mechanically forbidden.
- [x] Review/post content-like compact locator metadata is mechanically forbidden.
- [x] Existing evidence guard remains green.
- [x] Canonical group size remains `3`.
- [x] Old blocked snapshot recovered through GitHub-owned fresh-snapshot/stale-quarantine path only.
- [x] Three immutable old group artifacts were quarantined, not edited in place.
- [x] Progress remained `0/591`; no synthetic completion or manual advancement.
- [x] No manual queue/cache/progress/receipt repair.
- [x] No Scheduled Task `Run now`.
- [x] Implementation PR CI passed.
- [x] Post-merge GitHub activation/recovery workflow passed.

## Remaining live boundary

This task intentionally did not run the existing Scheduled ChatGPT task. Therefore one property cannot be truthfully claimed as live-accepted yet: whether the actual Scheduled ChatGPT runtime can execute the repository Python pre-publication entrypoint in its production environment.

The implemented contract handles that uncertainty fail-closed: if execution is unavailable, the worker must publish nothing rather than publish an unchecked immutable group.

Accordingly the final status is `complete_ready_for_live_acceptance`, not a claim of completed Scheduled Task runtime acceptance.

## Recommended next step

In a separate live-acceptance task, manually run the existing `Taste Steam Review Dossier` Scheduled Task **once** and verify one of the two allowed outcomes against canonical GitHub state:

- a group is published only after the repository pre-publication validator succeeds and is then accepted canonically; or
- the runtime cannot execute the validator and therefore publishes nothing with the fail-closed `prepublication_validator_unavailable` outcome.

Do not create a second scheduler/producer and do not change group size, queue, progress or evidence policy for that acceptance.
