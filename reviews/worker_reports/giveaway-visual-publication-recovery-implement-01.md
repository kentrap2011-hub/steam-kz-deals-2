# Giveaway visual publication recovery — IMPLEMENT 01

Status: `complete_ready_for_user_verification`

Date: 2026-09-06

Task: `WORKER_TASK_GIVEAWAY_VISUAL_PUBLICATION_RECOVERY_IMPLEMENT_01.md`

Mode: `IMPLEMENT / ACCEPTANCE`

## Outcome

The production giveaway publication path is recovered without weakening fail-closed behavior and without creating a second scheduler, a second giveaway writer, or a manual patch path.

The existing canonical visual writer now publishes the fresh canonical giveaway snapshot into `data/production/visual/current.json` through a bounded section-level refresh when the full paid/Taste visual build is independently blocked.

Final production identities:

- canonical giveaway snapshot blob: `04a913e4be29689d7ded6c8cf0f3f81f2030d23f`;
- canonical visual blob: `61b20125acdcddd722df8efa0f67ed0dc23341af`;
- canonical visual commit: `1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab`;
- visual `production_contract.source_giveaway_snapshot_blob_sha`: `04a913e4be29689d7ded6c8cf0f3f81f2030d23f`;
- giveaway visual state: `active`;
- active offer count: `1`;
- giveaway snapshot / visual freshness deadline: `2026-09-07T02:45:35.089580Z`.

The independent full visual/Taste freshness state was **not** fabricated: the scoped receipt explicitly records `full_visual_freshness=false`.

## Exact root cause

The previous failing boundary was correctly identified as:

`Build daily visual payload` -> `Build and refresh canonical visual payload once` -> `scripts/build_final_visual_payload.py`.

The historical failed run `34037436064` / job `101497984247` failed inside that boundary with:

`ChatGPT production payload is not complete`

The underlying guard is the existing completeness check in `scripts/build_daily_visual_payload.py`. The full visual build therefore remained correctly fail-closed because the current semantic/Taste production payload was incomplete. The giveaway source itself was not the failing subsystem.

A bounded giveaway-only path already existed on `main`, using the same canonical `scripts/build_final_visual_payload.py` writer under `GIVEAWAY_VISUAL_REFRESH_ONLY=1`, but it had two defects that prevented acceptance:

1. its `scope` classifier required the triggering push to be a narrowly pure giveaway-only commit; the canonical giveaway snapshot is normally refreshed inside mixed production commits, so the fresh source snapshot could remain newer than the visual provenance without activating the section-level route;
2. its freshness receipt was deliberately emitted as `degraded/no_fresh_build` even after the section was actually produced and persisted, so publication could not prove a real fresh scoped build.

At recovery start the provenance mismatch was concrete:

- current giveaway blob: `04a913e4be29689d7ded6c8cf0f3f81f2030d23f`;
- visual-recorded giveaway source blob: `33c1318a4950450aadb41b98a9552223b5cf43b8`.

## Architecture / ownership preflight

The fix stays inside existing ownership boundaries:

- GitHub Actions remains the orchestration and persistence owner;
- `data/production/visual/current.json` remains the single canonical visual artifact;
- `scripts/build_final_visual_payload.py` remains the single canonical visual writer;
- no second scheduler, producer, queue, retry loop, giveaway cache writer, or UI-side data reconstruction was added;
- the full build's semantic/Taste completeness gate was not modified or bypassed;
- no Taste recommendation logic was changed;
- no manual patch was made to `visual/current.json`, the giveaway snapshot, or giveaway handoff/cache.

## Implementation

Implementation commit:

`62ea2734146edceed111b4758baac3f3f23637ab` — `Recover giveaway visual publication from mixed source commits`

It was based on the then-current `main` commit `392903cf720dde1de4936436f235e9489d659ddd`, preserving the parallel Taste canary work.

Changed files:

- `.github/workflows/build-daily-visual-payload.yml`;
- `scripts/visual_freshness_receipt.py`;
- `scripts/test_visual_freshness_receipt.py`.

### 1. Scope classification fix

The existing visual workflow now checks canonical provenance before falling back to trigger-diff classification:

- compute current `HEAD:data/production/giveaways/v1/current.json` blob;
- read `production_contract.source_giveaway_snapshot_blob_sha` from canonical visual;
- when they differ, route to the existing bounded `giveaway_refresh` job.

This means mixed production commits can no longer hide a stale giveaway section.

The old pure giveaway-only diff route remains as a fallback.

### 2. Scoped freshness receipt

The existing receipt contract now supports two explicit scopes:

- `full_visual` — existing history-bound semantics;
- `giveaway_only` — canonical giveaway-source-bound semantics.

For a successful giveaway-only refresh the receipt may be `fresh_build=true` only when:

- the intended giveaway blob exists;
- the canonical visual was persisted;
- the produced visual records exactly that giveaway blob as its source provenance.

It simultaneously records:

`full_visual_freshness=false`

so a fresh giveaway section cannot be mistaken for a fully fresh paid/Taste visual build.

Verification remains fail-closed on source mismatch, produced provenance mismatch, canonical visual blob/commit mismatch, or staged publication mismatch.

### 3. Regression coverage

`test_visual_freshness_receipt.py` now covers:

- fresh full visual receipt;
- fresh giveaway-only receipt with `full_visual_freshness=false`;
- degraded/no-build behavior;
- stale visual mismatch fail-closed;
- giveaway-source provenance mismatch fail-closed.

Deploy acceptance ran this suite successfully:

`VISUAL_FRESHNESS_RECEIPT_TESTS=PASS cases=fresh_full,fresh_giveaway,degraded,stale_mismatch,giveaway_mismatch`

## Production acceptance

### Canonical visual build

Workflow:

`Build daily visual payload`

Run: `34047960720`

Result: `success`

Relevant jobs:

- `scope` / job `101526312687`: success;
- `giveaway_refresh` / job `101526331353`: success;
- full `build`: skipped by the bounded route, preserving the independent semantic/Taste fail-closed condition.

Classifier evidence:

`VISUAL_SCOPE=giveaway_only reason=source_provenance_mismatch source_blob=04a913e4be29689d7ded6c8cf0f3f81f2030d23f visual_source_blob=33c1318a4950450aadb41b98a9552223b5cf43b8`

Existing canonical writer evidence:

`VISUAL_GIVEAWAY_REFRESH=BUILT changed=true state=active offers=1`

Handoff/visual validator evidence:

`GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=1 fresh_until=2026-09-07T02:45:35.089580Z`

Non-giveaway preservation proof:

- paid-items SHA before: `d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`;
- paid-items SHA after: `d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`;
- `GIVEAWAY_AUXILIARY_DIFF=PASS non_giveaway_state_unchanged=true`.

The workflow persisted the visual through its normal canonical commit path:

`1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab` — `Refresh giveaway visual payload`

Only `data/production/visual/current.json` was changed by that producer commit.

### Freshness receipt

The same build run produced and uploaded artifact:

- name: `visual-freshness-receipt`;
- artifact ID: `9993674061`;
- artifact ZIP SHA-256: `818700c68ecf74fa4e2ef8ca0a9c978d59e996aec5305c3bbcc6d382875f3345`.

Creator result:

`FRESHNESS_RECEIPT fresh_build=true scope=giveaway_only outcome=fresh_build reason=None`

The deploy workflow then verified the exact staged payload against that exact triggering receipt:

`VISUAL_FRESHNESS=fresh scope=giveaway_only run_id=34047960720 giveaway_blob=04a913e4be29689d7ded6c8cf0f3f81f2030d23f visual_blob=61b20125acdcddd722df8efa0f67ed0dc23341af visual_commit=1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab full_visual_freshness=false`

This proves the receipt describes the actually produced, persisted, and staged canonical visual rather than an intended or stale artifact.

## Normal deploy/publication acceptance

Workflow:

`Deploy visual mailing`

Run: `34047980496`

Result: `success`

The deploy was triggered through the normal `workflow_run` route from the successful visual build.

Key deploy evidence:

- `VISUAL_DEPLOY_SCOPE=giveaway_only visual_commit=1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab non_giveaway_state_unchanged=true`;
- `PAID_VISUAL_ACCEPTANCE=reused_existing_canonical_payload structural_diff_proof=pass`;
- giveaway validator: `PASS state=active offers=1`;
- UI regressions: image swipe PASS, compact purchase options PASS, detailed score mobile PASS, `GIVEAWAY_UI_TESTS=PASS`, giveaway cache identity PASS;
- staged publication receipt binding: `VISUAL_FRESHNESS=fresh scope=giveaway_only ... full_visual_freshness=false`;
- `VISUAL_PUBLICATION_OUTCOME=fresh`;
- GitHub Pages deployment reported success for build version `1d7fb4d172d6d36dec4e78a5db2cdf51fa26b6ab`.

Pages environment:

`https://kentrap2011-hub.github.io/steam-kz-deals-2/`

## Acceptance checklist

- [x] Exact failing cause localized inside the prior boundary.
- [x] Existing visual workflow now succeeds through the safe bounded giveaway section route.
- [x] Existing canonical visual writer only; no duplicate writer.
- [x] Canonical current giveaway blob is present as visual source provenance.
- [x] `source_giveaway_snapshot_blob_sha` equals the actual current giveaway blob `04a913e4be29689d7ded6c8cf0f3f81f2030d23f`.
- [x] Giveaway handoff/visual state is active, validated, and non-expired at build/deploy time.
- [x] Paid/Taste payload remained byte-semantically unchanged by section refresh.
- [x] Independent full visual/Taste freshness was not fabricated (`full_visual_freshness=false`).
- [x] Freshness receipt proves exact produced/persisted/staged visual identity.
- [x] Normal deploy/publication route completed successfully.
- [x] No fail-closed gate was weakened.
- [x] No next task was started.

## Runtime cost note

This task required more than a commit-only change because acceptance explicitly depended on a real GitHub Actions build, canonical persistence, exact receipt artifact binding, and the separate Pages deploy completing. The reusable speed-up is now in the workflow itself: publication scope is decided from canonical provenance mismatch rather than relying on a fragile pure-commit heuristic, so future mixed source refreshes should self-route without another manual recovery investigation.

## Final status

`complete_ready_for_user_verification`
