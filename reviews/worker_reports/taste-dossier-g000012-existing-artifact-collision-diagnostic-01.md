# Taste Dossier g000012 Existing-Artifact Collision Diagnostic 01

**Task:** `taste-dossier-g000012-existing-artifact-collision-diagnostic-01`  
**Mode:** READ-ONLY / RECON  
**Repository / source of truth:** `kentrap2011-hub/steam-kz-deals-2` / `main`  
**Final status:** `complete_root_cause_proven`

## Executive finding

The g000012 HTTP 422 was a **same-snapshot exact-artifact collision caused by lost GitHub ingest/drain liveness inside the shared canonical-writer concurrency boundary**.

The deterministic path itself is correctly scoped by `snapshot_id + sequence + group_sha256`. The first g000012 publication created the exact immutable candidate once. Its push did wake `Ingest Steam review dossier checkpoint`, but that run was cancelled before any job started while another workflow using the same `taste-steam-review-dossier-canonical-writer` concurrency group was active and a newer Progressive PASS 1 run entered that same group. The surviving PASS 1 workflow did not reconcile the Dossier inbox. No later Dossier ingest run observed the candidate before the daily rollover.

Therefore GitHub canonical state still projected sequence 12 as `pending`; the Scheduled semantic worker correctly reloaded that GitHub projection, derived the same exact deterministic path, and correctly refused overwrite/rename/skip when create-only returned 422.

This is primarily a **GitHub canonical-writer liveness / ingest-drain wake-up loss defect**, not a worker create-only defect, not a deterministic-path identity defect, not cross-snapshot rebinding, and not failed-group recovery. The later daily rollover rendered the old artifact inert by replacing the active snapshot and removing the old active-inbox path.

## Exact incident identity

Historical canonical Dossier identity immediately after the first g000012 publication and still unchanged immediately before the later rollover:

- snapshot: `9cf59f4d94d1b4c7270bece5464666e3eb2359b87bd74cbefe3883b969f90689`
- prepared required SHA-256: `39867146352844fbbf1ff442b64adc63ca14ba1d0793570909486c3e602d033d`
- group-plan SHA-256: `b12e3a0c49ebc80e443f17240b738228f4035e6ebbbfef2d28901a1e134686a3`
- source-queue SHA-256: `97df681161ff572131c8c5a8f706d3ccdc8918a09b56d89f0397fb839fcf3124`
- worker-index blob: `2fcbc4d473f6691304b0f03e68ac8f554a42ada5`
- validation-status blob: `659df1bcce7113729084378cb93f95c0dcd17969`
- `next_pending_sequence=12`
- accepted groups: 8
- failed groups: 3
- pending groups: 173
- accepted dossiers: 24
- failed dossiers: 9
- pending dossiers: 517
- full backlog complete: false

The three historical failed groups were g000001, g000002, and g000011. They were already classified separately; none makes g000012 a recovery item.

The exact immutable g000012 descriptor was:

- descriptor blob: `10d926deca514fb3d101e71a7dd9531044751ddd`
- sequence: 12
- start/end: `33..36`
- appids: `1163590`, `1164940`, `1169040`
- titles: `Bullet Girls Phantasia`, `Trepang2`, `Necesse`
- items SHA-256: `1b6b78b0b5522715d9df846a7b880f1e28e5b0e51f535ac90f3b367d4d80981f`
- group SHA-256: `84b848d68245d5de3c44c105b76e25a2b0185555b920629379060430368b4617`
- evidence-contract SHA-256: `be470fbdb75b90fde5eb71da8d7a76ec9df77ac0ed171237aa4283df4a4deaac`
- worker-schema SHA-256: `d3d02d5060b5a978c827ebaddacac67b9cf4e1fa5369e5921a0762fce940da98`
- worker-prompt SHA-256: `6d5c3be5eb7043a9731054679bf05871a4c34284abec86b1177d547bd9fa5d65`

The exact deterministic publication path was:

`data/ai_inbox/taste_steam_review_dossiers/9cf59f4d94d1b4c7270bece5464666e3eb2359b87bd74cbefe3883b969f90689--g000012--84b848d68245d5de3c44c105b76e25a2b0185555b920629379060430368b4617.json`

## Exact existing artifact and creation history

The exact path first appeared in commit:

- `674a68aa377db2e324486e5714c1ce31bf722d44`
- message: `buffer taste steam review dossiers g000012`
- committed at: `2026-09-22T21:02:37Z`
- Git blob: `394ac414faa85643f631d90aa841299d9c03804f`

Its embedded descriptor identity exactly matches the immutable g000012 descriptor above: same snapshot, prepared SHA, plan SHA, sequence/range, exact appids/items, items SHA, source queue SHA, group SHA, and evidence/worker binding. This was not an artifact from another descriptor or an old snapshot accidentally occupying a new snapshot path.

The candidate contains three dossiers in descriptor order for the exact three planned appids. Whether those dossier semantics would have passed strict canonical validation was never established by canonical ingest, because the wake-up run never executed a job.

## Ingest/drain/recovery timeline

1. g000011 publication had already triggered Dossier ingest run `35784083220` (#71), which completed successfully.
2. Progressive PASS 1 ingest run `35784137789` (#93) entered the shared canonical writer at `2026-09-22T21:02:32Z` and completed at `21:02:47Z`.
3. g000012 commit `674a68aa...` landed at `21:02:37Z`.
4. Its push created Dossier ingest run `35784149716` (#72) at `21:02:39Z`.
5. Run #72 was cancelled at `21:02:41Z` and has **zero jobs**. Therefore it never checked out main, never ran recovery, never ran `ingest_taste_steam_review_dossier_inbox.py --reconcile-nonfatal`, never ran parallel validation, and never wrote canonical Dossier state.
6. Progressive PASS 1 run `35784151641` (#94) entered at `21:02:40Z`. Its workflow uses the exact same concurrency group:
   `taste-steam-review-dossier-canonical-writer`, `cancel-in-progress: false`.
7. The PASS 1 workflow does not run Dossier inbox reconcile/drain or Dossier validation. It only ingests PASS 1, rebuilds PASS 2 eligibility, revalidates PASS 1, and commits PASS 1 state/work.
8. No `Ingest Steam review dossier checkpoint` run occurred after cancelled #72 and before the rollover build.
9. Immediately before rollover, the repository still had:
   - the g000012 artifact blob `394ac414...` at the deterministic inbox path;
   - worker-index blob `2fcbc4d...` with `next_pending_sequence=12`;
   - validation-status blob `659df1bc...` with `candidate_count=0`, no candidate groups, and no malformed-current-snapshot records.
10. Thus canonical GitHub ingest/validation never observed or classified g000012 during that snapshot. It remained an unclassified transport artifact while canonical state remained pending.
11. Daily/pre-AI run `35796234158` (#176) started at `2026-09-22T23:11:52Z`. It built fresh snapshot `c4eb260d...`; step output reported `stale_inbox_quarantined_count=1`, then current-snapshot reconcile found nothing to persist.
12. Atomic pre-AI commit, ultimately `58f6441834e4c0303fc282cf3862629e38bb5986`, removed the old active-inbox g000012 path and installed the new projection. No `data/cache/taste_steam_review_dossiers/**` file changed in that commit.

### Stale-cleanup observability note

The rollover log says one stale inbox artifact was quarantined, and the recovery implementation moves recognized old-snapshot files to `data/quarantine/taste_steam_review_dossier_inbox/stale/<snapshot>/...`. The durable commit/current tree proves that the old g000012 active-inbox file was removed, but no durable `stale/9cf59f4d.../g000012...` target is present. This is a secondary persistence/observability discrepancy in stale cleanup, not the cause of the 422 incident. The old candidate is nevertheless no longer active and cannot authorize or collide with the current snapshot.

## Same-snapshot vs cross-snapshot determination

**Same-snapshot exact-group collision: proven.**

At the time of the failing retry, the canonical projection still had the same historical snapshot `9cf59f4d...`, the same g000012 descriptor, the same group hash `84b848d6...`, and sequence 12 pending. The pre-existing file embeds exactly that identity.

The pathname is not under-scoped:

`{snapshot_id}--g{sequence:06d}--{group_sha256}.json`

The group SHA itself binds snapshot, prepared scope, sequence/range, ordered appids/items hash, scope source, and source queue. A legitimate new snapshot/group receives a different path.

Current fresh g000012 proves this concretely:

- current snapshot: `c4eb260d36f55f5205cb8128886a49d79fe824ab456305d80905970d38fc5e42`
- current appids: `1222140`, `1222680`, `1225560`
- current items SHA-256: `776c23c72d93c527ad4251a45b60d8294d49e8d8ed5e6945bdf396e600cf4f66`
- current group SHA-256: `32266babd871b87db7bf6dda65ef8e8e9e38f1c1c641cdf2ce01a4ce945244d4`
- current deterministic path:
  `data/ai_inbox/taste_steam_review_dossiers/c4eb260d36f55f5205cb8128886a49d79fe824ab456305d80905970d38fc5e42--g000012--32266babd871b87db7bf6dda65ef8e8e9e38f1c1c641cdf2ce01a4ce945244d4.json`

Therefore the old g000012 path cannot collide with the fresh g000012 path.

## Why the worker was still authorized to create g000012

The worker does not own buffer interpretation. Its start authority is GitHub's compact canonical worker projection.

Because the only g000012 ingest wake-up was cancelled before execution:

- GitHub never transitioned g000012 to accepted;
- GitHub never classified it failed;
- GitHub never removed it from normal pending traversal;
- the worker index correctly remained `next_pending_sequence=12`.

The contract explicitly forbids the Scheduled semantic worker from scanning the inbox and converting artifact existence into progress/recovery truth. Therefore the later worker did exactly what the authority model required: read g000012 as pending, derive its deterministic create-only path, then fail closed when GitHub Contents reported that exact path already existed.

## Defect classification

### Primary owner: GitHub ingest/drain liveness within shared canonical-writer concurrency

The contracts intentionally serialize Dossier drain, daily pre-AI work, PASS 1 derived PASS 2 recomputation, and PASS 2-related canonical writes in `taste-steam-review-dossier-canonical-writer`.

The observed failure is that a Dossier push is documented as only a wake-up signal, but a pending Dossier wake-up can be cancelled/coalesced by a newer run in the same shared concurrency group, while the surviving non-Dossier workflow does not necessarily perform Dossier state reconciliation. This leaves durable transport without canonical classification.

The exact observed chain is run #93 occupying the writer, g000012 Dossier run #72 becoming pending, then newer PASS 1 run #94 entering the same group and #72 being cancelled before any job. PASS 1 #94 did not drain Dossier inbox.

### Not primary defects

- **Deterministic path identity:** correct and sufficiently snapshot/group scoped.
- **Snapshot regeneration/rebinding:** correct isolation; the later snapshot has a different path.
- **Worker behavior:** create-only refusal was correct.
- **Failed-group recovery:** not applicable before validation because g000012 was never classified failed.
- **Stale-work/liveness in worker:** the worker consumed the current GitHub projection correctly; the stale fact was inside GitHub's unclassified transport state.
- **Scheduler behavior:** separate issue only if an actual task mutation occurred; repository evidence cannot establish that mutation.

## Scheduler ownership finding

Canonical contracts forbid the Scheduled Dossier worker from enabling, disabling, pausing, deleting, rescheduling, or editing its own Scheduled Task.

The incident wording said the recurring task was stopped/disabled. Repository evidence does not expose the external scheduler state or prove an actual scheduler mutation. Therefore this diagnostic does **not** assert that the task was actually disabled. If only the invocation stopped, that is correct; if the recurring task was actually mutated by the semantic worker, that would be contract-incompatible.

No Scheduled Task setting was read or changed by this diagnostic.

## Current canonical Dossier state

Evidence head immediately before this report write: `3fea32d854e6feb1572fe58bfdf084c087986a08`.

Current worker index:
- blob: `70c05ec940a1193e7eb9a85ffeaffc2a55e82045`
- snapshot: `c4eb260d36f55f5205cb8128886a49d79fe824ab456305d80905970d38fc5e42`
- prepared date: `2026-09-23`
- prepared required SHA-256: `8bcd232d2c63fe5228c30a69db738d1eb22306e04f0eecea77c570dbd6356ddb`
- group-plan SHA-256: `e546324e415c50e17686d6117dcb89e91b32e96caaad8391e2e3892f885911e8`
- source-queue SHA-256: `db3f6e3c2b92e2bf47f293585c405d2d19fa276c6911c7fcdd124db18f3eda1d`
- accepted groups: 0
- failed groups: 0
- pending groups: 178
- accepted dossiers in this fresh work projection: 0
- failed dossiers: 0
- pending dossiers: 533
- next pending: `g000001`
- normal first pass complete: false
- all groups accepted: false
- full backlog complete: false

Current validation status:
- blob: `d42c5008327977d749b3b023e68957174df5e921`
- candidate count: 0
- valid candidates: 0
- invalid candidates: 0

Current g000012:
- descriptor blob: `081f6e7930916e09a673c29c84c6e036a722deab`
- state: `pending`
- appids: `1222140`, `1222680`, `1225560`
- group SHA-256: `32266babd871b87db7bf6dda65ef8e8e9e38f1c1c641cdf2ce01a4ce945244d4`
- its fresh deterministic path differs from the historical occupied path.

## Recovery and durable fix

### Smallest safe one-off recovery

For the **historical incident at the time the 9cf59... artifact was still current**, the minimal owning recovery was not worker-side delete/recreate and not failed-group recovery. It was a GitHub-owned state-based Dossier reconcile/drain of the already-present exact current-snapshot candidate, allowing canonical validation to classify it from repository truth.

That historical artifact is now superseded and removed from the active inbox by normal snapshot rollover. Therefore **no one-off recovery of historical g000012 should be executed now**; restoring or rebinding it would be wrong.

For the fresh c4eb... g000012, no old-artifact recovery is needed. It is a new immutable group/path.

### Smallest durable recurrence fix

Preserve the existing shared serialized GitHub canonical-writer boundary; do not split writers into independent concurrency domains and do not add a scheduler/retry daemon.

Make Dossier reconciliation **state-based and coalescing-safe inside that same boundary**: every surviving workflow run capable of superseding a pending Dossier wake-up must reconcile already-present Dossier inbox state (and update its canonical validation/projection consistently), or those shared triggers must be funneled through one common canonical-writer entrypoint that always performs that reconciliation before committing derived state.

A regression must reproduce the observed ordering — another canonical writer running, Dossier candidate wake-up pending, newer shared-writer event arriving — and prove that the candidate is still classified exactly once even if its original wake-up run is cancelled before job start.

This keeps GitHub as control plane, keeps create-only transport immutable, preserves one serialized writer domain, and introduces no new retry owner or recurring stage.

## Traversal safety

The fresh snapshot may traverse pending groups normally before g000012; the historical 9cf59... path cannot collide with fresh work.

Before any publication of the **fresh** g000012, the exact required conditions remain:

1. current GitHub index still binds snapshot `c4eb260d...`, its current plan/binding, and g000012 as pending;
2. the exact fresh descriptor remains the authority;
3. the fresh deterministic path is absent at create time;
4. the worker uses create-only and never overwrites/renames/skips.

If a deterministic current path already exists again while the group is still pending, the worker must stop that invocation exactly as it did here; GitHub must classify the existing transport state.

## Impact on accepted Dossiers and Deep

The incident did not roll back or mutate already-canonically-accepted Dossiers.

The historical g000012 candidate was never accepted, so it never became Deep evidence. The rollover commit that rendered it stale changed **zero** `data/cache/taste_steam_review_dossiers/**` files. Canonical Deep rules consume only accepted exact-compatible Dossiers; buffered/unclassified/failed candidates do not count.

Therefore the incident affected **forward Dossier progress/liveness only**, not already accepted Dossier evidence used by Deep. This diagnostic did not alter Fast, Dossier production state, Deep state, the active Deep activation task/PR, or any scheduler.

## Exact refs

- START protocol: `CHAT_PROTOCOL.md` blob `38e4891059d71fd16da39bae8e7bbeec684fc56a`
- task: `WORKER_TASK_TASTE_DOSSIER_G000012_EXISTING_ARTIFACT_COLLISION_DIAGNOSTIC_01.md` blob `e3be50c34d38e5db39136970bcc2781d2a8dad0a`
- Dossier contract: `c9765f9a3330f90aa00899309949e5348e6bcb21`
- persistence bridge: `4d53faade7de382d63539bdb5e4ed2797c601400`
- recovery contract: `aa87774d4f6eb98cf76947df25ffb31a198ac927`
- execution ownership: `76f1132bf8dceda9792e303d70e64cabd49b1a0e`
- worker prompt: `1ba4a390923e6bfbc655c7f0094db70ba395b9a6`
- historical worker index: `2fcbc4d473f6691304b0f03e68ac8f554a42ada5`
- historical validation status: `659df1bcce7113729084378cb93f95c0dcd17969`
- historical g000012 descriptor: `10d926deca514fb3d101e71a7dd9531044751ddd`
- historical candidate creation commit: `674a68aa377db2e324486e5714c1ce31bf722d44`
- historical candidate blob: `394ac414faa85643f631d90aa841299d9c03804f`
- g000012 Dossier wake-up: run `35784149716` (#72), cancelled, zero jobs
- overlapping PASS 1 run: `35784137789` (#93), success
- newer same-concurrency PASS 1 run: `35784151641` (#94), success
- PASS 1 workflow at incident: `.github/workflows/ingest-progressive-pass1.yml` blob `268e0b6199331578fc76dd68bda09520dc0bcca4`
- Dossier ingest workflow at incident: `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml` blob `5899e489738a4c8ffb10a65f963f07cd4334ec05`
- rollover build: run `35796234158` (#176), success
- rollover atomic main commit: `58f6441834e4c0303fc282cf3862629e38bb5986`
- current index blob: `70c05ec940a1193e7eb9a85ffeaffc2a55e82045`
- current validation-status blob: `d42c5008327977d749b3b023e68957174df5e921`
- current g000012 descriptor blob: `081f6e7930916e09a673c29c84c6e036a722deab`

## Process / routing note

The longest part of this diagnostic was historical Actions reconstruction rather than repository-state inspection: the decisive evidence lived across one candidate commit, a cancelled zero-job Dossier run, two overlapping PASS 1 runs sharing the same concurrency domain, and the later rollover build log. For future incidents of “immutable candidate exists but canonical state still says pending”, `PROJECT_ROUTES.md` / `KNOWN_WORKER_PITFALLS.md` should eventually point investigators directly to shared-concurrency run history and zero-job cancelled wake-ups. This task is READ-ONLY, so those routing files were not changed here.

## Recommended next step

Authorize **one bounded IMPLEMENT task** to make the existing shared `taste-steam-review-dossier-canonical-writer` boundary coalescing-safe by guaranteeing state-based Dossier inbox reconciliation in every surviving writer path that can supersede a Dossier wake-up (or one common equivalent entrypoint), with a regression reproducing runs #93 → Dossier #72 → PASS 1 #94. Do not recover the superseded historical g000012 artifact, do not change the Scheduled Task, and do not touch Fast/Deep activation.
