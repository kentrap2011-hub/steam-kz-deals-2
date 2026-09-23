# Progressive PASS 1 coactive ingest recovery fix 01

Date: 2026-09-23  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Branch/source of truth: `main`  
Task: `WORKER_TASK_PROGRESSIVE_PASS1_COACTIVE_INGEST_RECOVERY_FIX_01.md`  
Final status: `complete_ready_for_director_acceptance`

## Result

The Progressive PASS 1 coactive-ingest recovery is complete on canonical `main`.

The original stale activation guard, the missing focused regression/validation coverage, and the later optional-Dossier-path commit/staging defect are fixed. The second operator `workflow_dispatch` completed the canonical ingest without semantic re-execution.

No workflow or Scheduled Task run was launched by the final verification chat.

## Implementation already landed

Coactivation/documentation:
- `c64a3a5706b2a3c2d8416c003a4d64f48b18bd93` — PASS 1 ingest accepts canonical `pass1_active=true / pass2_active=true` and remains fail-closed for incompatible flags.
- `0b97cb01109f906f4da6f2538f87cdcf61e1666a` — focused activation regression.
- `13d3a84a5f33df3beced90d2aa5dcc2f453624cc` + `aa78ca856aa416b821623d854e0c346a742f2415` — Progressive validation coverage.
- `08c16eecc1f9ac38ef797c4ed812a6792aef8976` + `fb50a59bfa73b88f7ad16f60977779c317c85948` — route/decision documentation reconciled with production-active `FAST-DOSSIER-DEEP-V1`.

Commit-stage robustness:
- `66d33ee5a2b99b9044f6205e85b81752ab1c32ab` — canonical-writer staging helper.
- `d4f6819b6b11532a326f93db162f769bb1794531` — focused absent/present/tracked optional-path staging regression.
- `d3405f7390777297280bd7d9094e47e51584d799` — live PASS 1 workflow uses the staging helper.
- `5ab6f94a1318d7689429932cc9a3d8af4988dea1` — validation surface covers the helper/regression.
- `264a851dd146155fcec664034d23b73101f43d16` — tracked optional-path detection hardened.
- `5a113f32eafdcdc233d2dd0dce5a531bf625730e` — Deep integration regression follows the production staging helper.
- validation run `35868415779`, job `107205837580`: success.

## Recovery execution

First operator dispatch `35863646555` proved ingest/recompute/revalidation but failed at commit because absent optional path `data/ai_inbox/taste_steam_review_dossiers` was staged unconditionally. That defect is the staging fix above.

Second operator dispatch:
- run `35870243352`;
- job `107212138816`;
- source head `42ea0568cee5f56316d105b1db0613bbefa06677`;
- conclusion: `success`.

All relevant steps succeeded:
- Dossier reconcile;
- Dossier validation/recovery projection;
- PASS 1 pre-ingest regression;
- PASS 1 ingest;
- PASS 2 recompute;
- PASS 1 post-ingest revalidation;
- canonical commit/push.

Canonical ingest commit:
`9c51743030d9f6cba62648a27b3a8f3d1af937f8`.

Run summary:
- `processed_artifact_count=5`;
- `accepted_count=5`;
- PASS 1 `560 total / 105 attempted / 455 remaining`;
- PASS 2 recompute: target `560`, first-pass attempted `1`, waiting Dossier `532`, ready/pending `27`, recovery pending `0`.

The global delta is +5 attempted / -5 remaining because five already-existing PASS 1 artifacts were pending when the second dispatch started. This is normal production ingest behavior; the recovery was not forced into an artificial Friends-only commit.

## FIX-04 — Friends artifact canonically ingested without re-analysis

PASS.

Friends vs Friends identity:
- appid `1785150`;
- family `game:1785150`;
- work_id `4a85ac1f78ca5a8812a59631c715058f36032959b997b8be2504018c1100eed0`.

The artifact immediately before the successful dispatch had blob SHA:
`5643b0ad29ffae4514350d93f99b748d1f487974`.

The artifact in its original creation commit `63ceb92cc4a3628b987a5ee537cb22ca30c35be8` has the same blob SHA:
`5643b0ad29ffae4514350d93f99b748d1f487974`.

Therefore the successful recovery consumed the original byte-identical artifact; no semantic regeneration or edit occurred.

After ingest:
- one new PASS 1 state entry exists for `game:1785150`;
- its work_id is the exact expected work_id;
- `pass1_attempted=true`;
- outcome remains `analysis_incomplete / insufficient_evidence`;
- accepted_at_utc `2026-09-23T13:53:40+00:00`;
- exactly one accepted receipt exists: `data/cache/progressive_pass1_receipts/e3b608a9c92f9580790188f44d179593db75b42f8e0a47905cafa04d4749810c.json`;
- the Friends inbox artifact was removed by the canonical ingest commit;
- Friends no longer appears in remaining PASS 1 work.

## FIX-05 — PASS 1 state/work advances exactly once

PASS.

Before successful dispatch:
- state entries: `119`;
- attempted: `100`;
- remaining: `460`;
- first item: Friends vs Friends.

After canonical ingest:
- state entries: `124`;
- attempted: `105`;
- remaining: `455`;
- first item: The Age of Decadence, appid `230070`.

Exactly five new state entries were added, matching the five already-pending inbox artifacts:
- `game:225160`;
- `game:635320`;
- `game:1785150`;
- `game:212680`;
- `game:1300`.

Friends itself advanced exactly once: one new state entry, one receipt, and zero remaining-work copies of its work_id.

No pre-existing PASS 1 state entry was changed.

## FIX-06 — PASS 2 recompute succeeds after ingest

PASS.

The same canonical-writer job successfully ran `build_progressive_pass2_work.py` after PASS 1 ingest and before persistence.

PASS 2 scope before vs after:
- total current coverage target: `560 → 560`;
- first-pass attempted: `1 → 1`;
- authoritative completed: `0 → 0`;
- waiting Dossier: `532 → 532`;
- ready/pending: `27 → 27`;
- recovery pending: `0 → 0`;
- current Fast analysis-incomplete projection: `100 → 105`.

Only the derived Fast projection changed as expected from the five newly accepted PASS 1 incompletes. Deep attempt/state accounting did not advance.

## FIX-07 — unrelated Fast/Dossier/Deep histories unchanged

PASS.

Exact diff `42ea0568... → 9c517430...` contains only:
- removal of the five consumed PASS 1 inbox artifacts;
- five new PASS 1 receipts;
- additions to `data/cache/progressive_pass1_state.json`;
- regenerated `data/production/pre_ai/progressive_pass1_work.json`;
- a two-line derived projection change in `data/production/pre_ai/progressive_pass2_work.json`.

Additional proof:
- all `119` pre-existing Fast state entries are byte-equivalent at the JSON-entry level before/after ingest;
- Deep state blob SHA is unchanged at `7efdc20ade2ed66ae2770c0bf1184e925b9eea3e`;
- no Dossier semantic-history/cache file appears in the ingest commit diff;
- no Deep semantic-history/state file appears in the ingest commit diff.

The four non-Friends Fast entries added by the same run were also already-existing inbox results; they were canonically accepted, not regenerated or used to rewrite prior Fast history.

## Downstream fresh-main verification

The canonical ingest commit triggered the existing downstream route:
- visual build run `35870282561`: success;
- visual deploy run `35870360504`: success;
- resulting visual commit `c44825bf11c875f30cb534239170a627adc1ecd9`.

Fresh main retained PASS 1 at `105 attempted / 455 remaining` with Friends absent from remaining work.

## Acceptance matrix

- FIX-01 coactive production ingest guard: PASS.
- FIX-02 focused activation regression: PASS.
- FIX-03 validation coverage: PASS.
- FIX-04 existing Friends result canonically ingested without re-analysis: PASS.
- FIX-05 PASS 1 state/work projection advances exactly once for Friends and canonically consumes all five pending artifacts: PASS.
- FIX-06 Deep/PASS 2 recompute after ingest: PASS.
- FIX-07 unrelated Fast/Dossier/Deep histories unchanged: PASS.
- FIX-08 documentation reconciliation: PASS.
- FIX-09 no Scheduled Task mutation / Scheduled `Run now` by this worker task; final verification launched nothing: PASS.
- commit/staging optional-path defect and regression coverage: PASS.
- FIX-10 durable report committed and reread from `main`: PASS. Final report commit `450602fd7c23b83aa5ce7bb1b4325148a4b90a98` was reread from `main` as blob `58f0c2977e730c7ecbb57a434f5fe037e0bff65f`; this closeout update is reread again before the final response.

No remaining recovery action is required for this task.
