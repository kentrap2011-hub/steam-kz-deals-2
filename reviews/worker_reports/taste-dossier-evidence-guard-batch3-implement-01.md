# TASTE DOSSIER EVIDENCE GUARD + BATCH 3 IMPLEMENT 01

Final status: `complete_ready_for_live_acceptance`

Date: 2026-09-16
Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`
Task: `WORKER_TASK_TASTE_DOSSIER_EVIDENCE_GUARD_BATCH3_IMPLEMENT_01.md`

## Scope and architecture preflight

START gate was completed from `CHAT_PROTOCOL.md` before implementation. The task was executed only in `kentrap2011-hub/steam-kz-deals-2`; no other repository was used.

Architecture preflight result: PASS.

- Owner of scope/order/progress/persistence remains the GitHub control plane.
- The existing `TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2` authorizes the fixed daily snapshot, immutable group plan, create-only buffered transport, canonical drain, persistence and recovery model used here.
- No canonical control-plane responsibility was moved into ChatGPT.
- No new scheduler, queue, retry system, backlog manager, recurring stage or production quota was introduced.
- Group size `3` remains an internal durability/transport boundary, not a run quota or daily limit.
- `Scheduled Task Run now` was not invoked in this task.

## Root cause

The live V2 acceptance exposed a structural evidence gap rather than a transport failure. The previous dossier shape could persist source-level provenance but did not require an observation to bind its `mention_count` to the individual player-feedback records actually inspected. That allowed a worker to use aggregate storefront/review counts as if they were observation mentions, and recurrence could consequently be higher than the attributable evidence actually present.

The previous semantic rules also did not mechanically prevent a Steam Store app page rendered with `?l=russian` from being represented as Russian player-feedback evidence. This could incorrectly satisfy `found_and_used` and inflate `source_mix_status` despite no attributable Russian player review/discussion having been inspected.

The required correction therefore had to be structural and validator-enforced: observation -> compact attributable player-feedback records -> exact count -> recurrence.

## Landed contract revisions

Implementation PR: `#35` — `Harden Taste dossier evidence and use groups of three`.

PR head: `f963633e6da4d86a7844b071f6c831fb25d45e48`
Merge commit on `main`: `7c52df8faf4fd2745447eac95d3c06ddcfc50486`

Active revisions after merge:

- Control-plane contract: `TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2`, revision `evidence-guard-batch3-2026-09-16`.
- Web evidence contract: `TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2`, version `2`, revision `evidence-record-binding-2026-09-16`.
- Worker schema remains `TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2`, version `2`, with schema revision `auditable-feedback-record-binding-2026-09-16`.
- Dossier schema remains `TASTE-STEAM-REVIEW-DOSSIER-V2`, version `2`.
- Worker prompt revision: `web-evidence-v2`.

The payload schema version was deliberately not churned again; compatibility is controlled by the explicit web-evidence binding. Prior `WEB-EVIDENCE-CONTRACT-V1` evidence is not accepted as V2 evidence.

## Auditable mention semantics

The active dossier contract now requires compact attributable player-feedback records in:

`provenance.player_feedback_records`

Each observation must contain exact distinct `player_feedback_ids` referring to those records. For every observation:

`mention_count == number of distinct bound player_feedback_ids`

Each bound record must resolve to a source with `player_feedback:true`, and that source must also appear in the observation `source_ids`.

Persisted feedback records remain compact: stable `feedback_id`, parent `source_id`, URL or stable public reference, approximate publication date when available, and language. Raw review/post bodies, quotes/excerpts, usernames and author profiles remain forbidden.

Aggregate storefront statistics do not create player-feedback records and cannot contribute to `mention_count`. This includes overall review totals, positive counts, language-filtered totals, percentages, ratings and similar aggregate values. Therefore a displayed aggregate such as `523` cannot become `mention_count:523` unless 523 distinct attributable player-feedback records were actually inspected, represented and bound to that observation.

`source_mix_status` is also derived from player-feedback sources actually used by bound records, not merely from the number of source pages listed in provenance.

## Recurrence reconciliation

Recurrence is mechanically constrained by the bound attributable evidence:

- `anecdotal`: exactly 1 bound player-feedback record;
- `limited`: at least 2;
- `moderate`: at least 3;
- `strong`: at least 5.

One attributable player-feedback item therefore cannot support `moderate` or `strong` recurrence. The validator also prevents `overall_strength:"moderate"` or `"strong"` unless at least one observation has mechanically supported recurrence at that level.

The existing temporal rules remain active: current-state claims require recent current-state support; historical/fixed claims require both historical evidence and a recent current-state check; durable design traits require durable-trait evidence.

## Russian player-feedback guard

Russian feedback remains a mandatory research attempt, but the acceptance rule is now explicit and structural.

`found_and_used` requires at least one attributable Russian- or mixed-language player-feedback record that is actually bound to an observation through `player_feedback_ids`.

A Steam Store app page rendered in Russian, including `?l=russian`, is context/metadata only. It cannot be marked as attributable player feedback solely because of the language parameter, cannot satisfy `found_and_used`, and cannot by itself create `multi_source` status. Language-filtered aggregate review counts are also insufficient.

If only Russian Store UI or aggregate counts are found, the canonical state is `searched_not_found_or_insufficient`. Russian-specific localization/translation/voice/font/encoding/regional findings cannot be inferred from non-Russian feedback.

## Canonical group boundary: 3

`config/taste_steam_review_dossier_contract.json` now has:

`checkpoint_size: 3`

The existing invariants remain unchanged:

- GitHub owns canonical scope/order/progress/persistence;
- group plan is derived from the fixed `prepared_required_items` order;
- groups are contiguous and non-overlapping;
- group identity/hash semantics remain deterministic;
- ChatGPT transport remains immutable create-only;
- GitHub drain accepts only the maximal valid contiguous prefix;
- gaps, invalid expected groups, stale snapshots, duplicates and replay remain GitHub-owned interpretations;
- same-snapshot canonical progress advances only after successful persistence.

Regression coverage proves group-of-three plus smaller-tail behavior. The currently activated snapshot contains 591 required items, so it partitions exactly into 197 groups of 3 and has no tail because 591 is divisible by 3. Separate deterministic regressions cover non-divisible scopes and preserve the smaller final tail semantics.

## Migration and snapshot rebuild

Same-day preservation was tightened. A same-day manifest is preserved only when all of the following remain compatible:

- package identity policy revision;
- exact active web-evidence contract binding;
- canonical group/checkpoint size.

If the evidence binding or group size is incompatible, the normal GitHub-owned pre-AI builder constructs a new snapshot and new immutable group plan. Old progress/cache is not manually rewritten or rebound. Snapshot identity now incorporates the active web-evidence binding and canonical group size.

Old snapshot/group-plan buffer artifacts can never be rebound to the new snapshot. The normal rollover cleanup/reconciliation path remains GitHub-owned.

## Deterministic validation

PR CI workflow: `Validate buffered Steam review dossier runtime`
Run: `35131461365` / run #34
Result: SUCCESS
Job: `104913226280`

The CI job executed the fixed-snapshot, buffered transport, same-day preservation, strict evidence/recovery and package-member aggregation suites. Totals from the five suites were 9 + 8 + 4 + 16 + 6 = 43 tests, all passing.

Required evidence-guard regressions include:

- aggregate `523` cannot become `523` observation mentions;
- one player-feedback record cannot support moderate/strong recurrence;
- Russian Steam Store `?l=russian` cannot be player feedback or satisfy `found_and_used`;
- a real bound Russian player-feedback record can satisfy `found_and_used`;
- historical launch issue requires historical evidence plus recent current-state check;
- repeated current complaint requires distinct bound records;
- Markdown-wrapped/non-plain provenance URLs remain rejected;
- raw body-like fields and duplicate provenance/feedback records remain rejected;
- group-of-three planning, contiguous drain, gap blocking, replay/idempotency and durable progress remain green;
- package-member aggregation and exact title/appid identity behavior remain green.

Package semantics were not changed. The existing `Sub_87601` mapping still resolves to per-game dossier nodes `App_304240` (`Resident Evil`) and `App_339340` (`Resident Evil 0`) with package-level aggregation remaining downstream/commercial mapping rather than a second semantic game dossier subject.

## Activation

After PR #35 merged, the normal push-triggered GitHub workflow `Build pre-AI deterministic payload` ran automatically. This was not a manual Scheduled Task Run now.

Activation workflow run: `35131508119` / run #124
Job: `104913384010`
Result: SUCCESS

Relevant successful activation steps included:

- `Prepare fixed daily full Steam review dossier backlog`;
- `Reconcile already-present dossier inbox state`;
- `Regression test fixed daily dossier snapshot control plane`;
- `Commit atomic pre-AI payload`.

The workflow committed the refreshed canonical pre-AI payload to `main` as:

`16bb018b387eefae5150e52403da76322400add4` — `Refresh atomic pre-AI payload`

## Fresh canonical snapshot proof

Fresh snapshot:

`d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`

Canonical worker index after activation:

- `prepared_for_date`: `2026-09-16`
- `prepared_required_count`: `591`
- `completed_required_count`: `0`
- `remaining_required_count`: `591`
- `group_count`: `197`
- `canonical_expected_sequence`: `1`
- `prepared_required_sha256`: `0e4444fe7fe2e34df70bb98362f785207af43e1ac8c047732640f6b188fbb641`
- `group_plan_sha256`: `64bcf06228f279f0db5cf9ea4406e48484cf9b95b801f4b11d03fd7770138ae2`
- `source_queue_sha256`: `f69df37779c9b4c2c6eae5e075054098789c514e7d2cc5127d85620060ca7c50`

The canonical work manifest binds this snapshot to:

- `TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2`
- evidence contract version `2`
- worker schema version `2`
- dossier schema version `2`
- worker prompt revision `web-evidence-v2`

Exact first canonical descriptor:

`data/production/pre_ai/taste_steam_review_dossier_worker_groups/d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973/g000001.json`

Sequence `1`, indices `[0,3)`, group SHA-256:

`83d91127ece346690fb62af453938d80be6707c19ae6019ab85de6404b11d021`

Exact first three pending items in canonical order:

1. `App_2378500` / `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC` — `refresh_required`
2. `App_1000360` / `1000360` — `Hellish Quart` — `refresh_required`
3. `App_1003590` / `1003590` — `Tetris® Effect: Connected` — `refresh_required`

This provides two important activation proofs. First, group size is actually 3 in the fresh canonical projection, not only in configuration. Second, the incompatible prior evidence for these entries is not treated as fresh: each is explicitly scheduled for refresh under the new binding.

The previous rejected live snapshot was `6e4f851cd4c9e6d6f5a6c265ba30b80ee0d338b6477401453111be06109c8f53`. The new snapshot has a different identity and starts from canonical progress 0. Activation reconciliation completed successfully without advancing the new snapshot, so no stale old-snapshot buffered artifact was accepted as progress for the new plan. The old snapshot identity is not present in the active main projection, and the current dossier inbox path contains no pending old transport artifact after activation.

## Scheduled Task Run now

No Scheduled Task Run now was started during IMPLEMENT, ACTIVATE or VALIDATE. The only activation execution was the ordinary GitHub `push`-triggered pre-AI build described above.

## Residual risks / follow-up boundary

- The validator can prove mechanical evidence binding and count consistency; live acceptance is still required to verify that the scheduled semantic worker actually selects relevant, attributable player feedback in practice.
- Existing incompatible dossier files may remain physically present until rebuilt, but strict freshness validation marks them incompatible/refresh-required and prevents them from satisfying the new evidence contract.
- The smaller group boundary increases the number of transport artifacts for a full backlog, but does not create a new quota or transfer progress ownership away from GitHub.
- The current snapshot is intentionally not advanced in this task; live scheduled-worker behavior under the new contract has not yet been accepted.

## Next step

1. Run exactly one manual Scheduled Task Run now for the dossier worker against snapshot `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`, then perform a separate READ/VALIDATE live acceptance of the resulting group before any additional scheduled run.
