# Taste Dossier Live Web Evidence Acceptance 01

- Date: `2026-09-16`
- Mode: `ACCEPTANCE`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base branch / source of truth: `main`
- Final status: `rejected_live_web_evidence_group1`

## Task

Perform one live acceptance invocation of the existing `Taste Steam Review Dossier` Scheduled Task against the active V2 ordinary-web player-feedback evidence contract. Do not press `Run now` from this worker, do not modify Scheduled Task UI, do not perform manual workflow dispatch, do not use MCP/appreviews transport, do not modify Taste Semantic Producer, and do not perform a second `Run now`.

## Architecture preflight

Preflight was repeated after an explicit repository-scope correction and was performed only against `kentrap2011-hub/steam-kz-deals-2` on `main`.

Verified:

- GitHub remains the control plane for scope, immutable group identity/order, validation, canonical progress, persistence, recovery and completeness.
- Scheduled ChatGPT remains a constrained semantic/external-research worker.
- `TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2` version `2` is active.
- `TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V1` version `1` is active.
- dossier schema is `TASTE-STEAM-REVIEW-DOSSIER-V2` version `2`.
- worker prompt revision is `web-evidence-v1`.
- raw review/post bodies, quotes/excerpts, usernames and per-review corpus persistence remain forbidden.
- recovery remains GitHub-owned and is valid only for the exact current invalid expected deterministic artifact after canonical validator failure; it cannot advance progress and cannot use alternate retry filenames.

No architecture responsibility was transferred to the interactive chat and no new recurring stage/queue/retry loop/backlog manager was introduced.

## Baseline immediately before live invocation

The current daily snapshot had legitimately advanced from the prior-day 594-item snapshot to the `2026-09-16` snapshot:

- snapshot ID: `b5d4cdf8aa2eacf81f2e4fe7e37d23d44305cc8f6952b71516ffbb435eeb5023`
- prepared required: `618`
- completed required: `0`
- remaining required: `618`
- canonical expected sequence: `1`
- group count: `62`
- full backlog complete: `false`

The current group-1 descriptor contained exactly 10 items and had:

- sequence: `1`
- group SHA-256: `658adb1723400bbc5349567ab1a95fcb86f0a80830edb72f093c95a0e4da038a`

The deterministic new g1 inbox path did not exist before invocation.

The prior legacy g2 from snapshot `c4b3c299...` no longer blocked this snapshot: normal GitHub-owned new-snapshot stale cleanup had moved it to the stale quarantine path.

## Live invocation

The user manually pressed `Run now` exactly once on the existing `Taste Steam Review Dossier` task.

No second invocation was requested or performed.

The Scheduled Task stopped fail-closed during identity validation of current group 1 and reported that no buffered artifact had been published.

The specific blocking descriptor item is the second item of g1:

- key: `Sub_87601`
- descriptor appid: `304240`
- descriptor title: `Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle`
- dossier path: `data/cache/taste_steam_review_dossiers/App_304240.json`

This identity shape conflicts with the active V2 identity requirements for the semantic worker: it must preserve the exact descriptor title/appid, resolve one concrete release identity using title + release year, and must not silently combine or reinterpret bundle/edition/version entities as another release. The worker therefore correctly failed closed instead of fabricating a resolved identity or publishing a dossier for an uncertain entity.

## Post-invocation verification

After the reported fail-closed stop, GitHub state remained:

- snapshot ID: `b5d4cdf8aa2eacf81f2e4fe7e37d23d44305cc8f6952b71516ffbb435eeb5023`
- canonical expected sequence: `1`
- completed required: `0`
- remaining required: `618`

The deterministic g1 buffered artifact is still absent:

`data/ai_inbox/taste_steam_review_dossiers/b5d4cdf8aa2eacf81f2e4fe7e37d23d44305cc8f6952b71516ffbb435eeb5023--g000001--658adb1723400bbc5349567ab1a95fcb86f0a80830edb72f093c95a0e4da038a.json`

Therefore:

- GitHub did not accept 10 dossiers;
- progress did not become `completed=10`;
- expected sequence did not become `2`;
- no V2 group-1 artifact exists to inspect for player-feedback sources, Russian search attempts, current technical evidence, or raw-body exclusion at the persisted-artifact level.

The acceptance PASS criteria were not met.

## Recovery decision

The conditional legacy-g2 recovery path is not applicable in this acceptance result.

That recovery was allowed only if g1 had first been accepted and the old legacy g2 then became the current invalid blocker. Here g1 was never published or accepted and canonical expected sequence remains `1`.

No recovery request was created, no file was manually deleted, canonical progress was not advanced, and no alternate retry filename was created.

## Taste Semantic Producer / prohibited actions

Confirmed for this acceptance task:

- no Taste Semantic Producer changes;
- no manual workflow dispatch;
- no MCP/appreviews transport;
- no Scheduled Task UI changes by this worker;
- no second `Run now`;
- no manual dossier authoring;
- no raw review corpus persistence.

## Acceptance conclusion

The live V2 evidence worker demonstrated the intended fail-closed identity behavior, but the requested live group-1 acceptance itself failed because the canonical prepared group contains an identity-incompatible bundle/app mapping before the worker can publish the complete 10-dossier V2 group.

The next work should be a bounded correction/review of dossier work-item identity generation for package/bundle-backed Taste rows, preserving the V2 fail-closed identity guarantees. This acceptance task does not implement that fix and does not rerun production.

## Final status

`rejected_live_web_evidence_group1`
