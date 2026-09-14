# Taste Dossier Buffered Submission RECON 01

Task ID: `taste-dossier-buffered-submission-recon-01`  
Mode: `READ-ONLY / RECON`  
Date: 2026-09-14  
Repository: `kentrap2011-hub/steam-kz-deals-2`

## Final status

`viable_but_contract_change_needed`

## Executive conclusion

The proposed buffered architecture is viable and is a good fit for the already-implemented fixed daily Steam-review-dossier snapshot, **provided the buffer is implemented as immutable create-only checkpoint files and GitHub continues to own every control-plane decision**.

The current architecture already contains the most important prerequisite: the daily work manifest fixes the complete ordered `prepared_required_items[]` for one immutable `snapshot_id`. Therefore groups 11–20, 21–30, 31–40, etc. are already mathematically determined by GitHub's fixed snapshot and `checkpoint_size=10`; ChatGPT does not need to select or reorder games.

However, the current canonical contracts do **not** authorize ChatGPT to process those future groups before canonical manifest advancement. The current worker contract says to process only `current_checkpoint_items[]`, and the current submission validator binds a submission to the **current mutable** `scope_sha256`, which is recomputed from the current remaining scope after every accepted checkpoint. Therefore the proposed behavior is not a prompt-only change and is not ready for implementation under the present contract.

The minimum safe design is:

1. GitHub prepares an immutable checkpoint/group plan for the full fixed daily snapshot.
2. ChatGPT processes those already-declared groups in sequence, ten at a time.
3. After each completed group ChatGPT creates one immutable create-only buffer file with a deterministic group identity.
4. ChatGPT may immediately start the next **predeclared** group without waiting for canonical ingest.
5. GitHub Actions owns a serialized drain that accepts only the maximal contiguous prefix beginning at the canonical expected group, validates every group, persists dossiers, advances canonical state, and consumes accepted buffer files.
6. Missing or invalid group N blocks N+1 and later; GitHub never skips a gap.
7. Buffer contents never become an independent ChatGPT queue/retry/completeness system.

This removes the Action/manifest round-trip wait between every ten dossiers while preserving GitHub as the control plane.

## Architecture preflight

### 1. Current owners of scope / order / retry / checkpoint / completeness / persistence

Current canonical ownership is unambiguous:

- **GitHub / GitHub Actions owns**
  - full dossier scope selection;
  - canonical order and appid deduplication;
  - fixed daily snapshot preparation;
  - checkpoint construction;
  - checkpoint advancement;
  - retry/unresolved state;
  - completeness accounting;
  - submission validation;
  - canonical dossier persistence;
  - canonical manifest persistence;
  - accepted inbox cleanup;
  - the decision that the production cycle is complete.
- **Scheduled ChatGPT dossier worker owns only**
  - external/semantic evidence collection for GitHub-prepared work;
  - neutral dossier synthesis;
  - structured submission through the repository-defined create-only handoff.

Evidence:
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`

This ownership must remain unchanged.

### 2. Do current contracts allow future tens before canonical manifest advancement?

**No.**

The current worker contract explicitly says to process only the exact `current_checkpoint_items[]`. It permits the next checkpoint only after the prior submission has been canonically ingested and the advanced same-snapshot manifest is visible.

The current validator also requires:
- exact current `snapshot_id`;
- exact current `scope_sha256`;
- exact current `scope_source`;
- exact current `source_queue_sha256`;
- dossiers exactly equal to the current checkpoint appids, in order.

Current `scope_sha256` is derived from:
- `snapshot_id`;
- hash of the current `remaining_required_items`;
- current checkpoint items.

Because `remaining_required_items` changes after each ingest, `scope_sha256` for a future group is intentionally not the same immutable identity as that future group.

Therefore the current fixed snapshot contains enough information to know future groups, but the **authorization and submission identity contract is still current-checkpoint-only**.

### 3. Would the proposed architecture move control-plane responsibility from GitHub to ChatGPT?

It would **not**, if GitHub predeclares the complete group plan and ChatGPT may only process those exact group descriptors in sequence.

It **would** move control-plane responsibility if ChatGPT were allowed to:
- choose arbitrary offsets from the snapshot;
- skip a missing group;
- decide which buffered group needs retry;
- reinterpret a duplicate;
- decide canonical completeness;
- construct a new queue from repository contents.

The recommended design does none of those things.

### 4. Would it create a new ChatGPT-side queue / retry / backlog manager?

Not in the recommended design.

The buffer is only a durable transport handoff. GitHub remains the queue/retry/completeness owner. ChatGPT's loop is limited to:

`read immutable GitHub checkpoint plan -> process next declared group -> create deterministic file -> process next declared group`

A later Scheduled Task invocation must not scan the buffer and invent a recovery policy. It starts from current GitHub canonical state. If the canonical expected group's deterministic buffer path already exists and has not yet been canonically advanced, the worker must not overwrite, rename, skip, or create an alternate retry artifact.

## Current-state evidence

The accepted production run in `reviews/worker_reports/taste-dossier-live-prompt-acceptance-01.md` proves the current bottleneck:

- same snapshot remained active;
- completed count advanced `30 -> 40`;
- remaining count advanced `554 -> 544`;
- exactly one next ten-item checkpoint was successfully processed and submitted;
- the worker stopped because GitHub ingest was still queued and the canonical manifest had not advanced yet;
- the ingest later succeeded and atomically persisted the ten dossiers, removed the submission artifact, and advanced the same snapshot.

This is exactly the latency the buffered design is intended to remove.

The current fixed snapshot decision is already durable in `PROJECT_DECISIONS.md` as `TASTE-005`: one full daily snapshot is fixed by GitHub; checkpoint size 10 is only a durability boundary.

## A. Future checkpoints

### Does the fixed snapshot already contain the full immutable list?

**Yes.**

`data/production/pre_ai/taste_steam_review_dossier_work.json` is `TASTE-STEAM-REVIEW-DOSSIER-WORK-V2` and contains the complete fixed `prepared_required_items[]`.

`scripts/taste_steam_review_dossier_daily.py` constructs that list once, stores `prepared_required_sha256`, and then derives the current checkpoint as the first `checkpoint_size` items from `remaining_required_items`.

Therefore the full future order is already present and deterministic.

### What is missing?

What is missing is an immutable **future-group authorization identity**.

Today:
- the fixed snapshot is immutable;
- the current checkpoint is authorized;
- a submission is bound to mutable `scope_sha256`.

For buffered future groups, GitHub should expose an immutable `checkpoint_plan[]` or equivalent deterministic descriptors during daily preparation.

### Recommended deterministic checkpoint identity

For every group, GitHub should precompute or canonically derive:

- `snapshot_id`;
- `prepared_required_sha256`;
- `sequence` — 1-based group number;
- `start_index`;
- `end_index_exclusive`;
- exact ordered `appids`;
- `items_sha256` over the exact group items;
- `group_sha256` over the complete identity above.

Recommended identity formula conceptually:

`group_sha256 = canonical_sha256(snapshot_id + prepared_required_sha256 + sequence + range + exact ordered group items)`

The submission should also preserve existing global provenance such as `scope_source` and `source_queue_sha256`.

A deterministic create-only path can then be:

`data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json`

The important property is not this exact spelling; it is that the identity is immutable and independent of current canonical `remaining_required_items`.

The current mutable `scope_sha256` should remain useful for current progress validation if desired, but it should **not** be the identity of future buffered groups.

## B. Buffer design comparison

| Design | Write conflicts | Partial failure / recovery | Replay / idempotency | Ordering / validation | GitHub write & trigger behavior | Assessment |
|---|---|---|---|---|---|---|
| One mutable shared `buffer.json` | High: ChatGPT and GitHub would repeatedly update the same file | A bad update can affect the whole buffer; harder to isolate a completed ten | Requires merge/update semantics and conflict handling | Ordering is embedded in mutable shared state | Requires update-file rather than current create-only pattern; poor fit for safety-block/write boundary | **Not recommended** |
| One immutable create-only file per ten dossiers | No shared-file mutation between worker submissions | Failure loses at most the not-yet-created group; previously created groups stay durable | Deterministic path + group hash gives natural create-only idempotency | Exact group identity and gap detection are straightforward | Same basic write frequency as current architecture: one create-file per checkpoint; rapid pushes can be drained/coalesced | **Recommended** |
| One file per dossier | Low per-file conflict, but many independent artifacts | Very fine-grained durability, but GitHub must reassemble ten-item groups | More duplicate/partial-set states | Harder to prove group completeness/order before advancement | Roughly 10x the current handoff writes and much more trigger churn | **Not recommended unless dossier-level durability later becomes a separate requirement** |
| Immutable multi-group bundle per worker segment/invocation | Low write conflict | Groups are not durable until the larger bundle is created; a worker interruption can lose more completed semantic work | Bundle identity can be deterministic but retry semantics are coarser | Validator must unpack another aggregation layer | Fewer writes, but less aligned with the existing 10-item durability boundary | **Viable but inferior to per-checkpoint files** |

### Why create-only checkpoint files fit the existing architecture best

They preserve the already-approved checkpoint boundary and the existing principle that ChatGPT may only create a new transport artifact, never mutate canonical state.

They also minimize TPI/safety exposure relative to alternatives:
- no update/overwrite operation;
- no shared mutable file;
- no alternate retry filename;
- no direct manifest or dossier-store write.

A safety block on a create-file remains a real stop condition. The buffered architecture does not remove safety controls and should not compensate by accumulating unpublished semantic work in memory.

## Recommended scheme in plain language

GitHub already knows the whole list for the day. It should divide that already-fixed list into numbered immutable tens in advance.

ChatGPT then works through those numbered tens:
- finishes group 5;
- creates the file for group 5;
- immediately works on group 6;
- creates group 6;
- immediately works on group 7;
- and so on.

It does **not** wait for GitHub to update the canonical manifest between those writes.

GitHub independently looks at the buffer and says: “My canonical next group is 5. Do I have 5? Yes. Then 6? Yes. Then 7? Yes.” It validates and accepts them in that exact order. If 6 is absent, GitHub stops after 5 and leaves 7 alone.

Thus ChatGPT performs semantic work continuously, while GitHub remains the sole authority that decides what has actually been accepted.

## Technical scheme

### Fixed daily preparation

GitHub daily preparation continues to:
- select the full eligible dossier scope;
- deduplicate by appid;
- preserve canonical queue order;
- build `prepared_required_items[]`;
- produce the same fixed `snapshot_id`.

Additionally it produces an immutable group plan over `prepared_required_items[]`.

No current queue reread is needed between groups.

### Worker processing

The scheduled dossier worker:
- reads the current fixed snapshot and immutable group plan;
- begins at the GitHub-authorized next group;
- processes exact group items in order;
- creates the deterministic create-only group artifact;
- on successful create, advances only its **local traversal of the already-predeclared plan**, not canonical GitHub progress;
- may continue immediately to the next declared group without waiting for ingest.

The worker may optionally re-read the manifest before beginning a later group only to detect that a **different daily `snapshot_id`** has replaced the one it is processing. It must not use that read to choose a new order or to reinterpret canonical progress.

### Buffer semantics

The buffer is:
- durable transport state;
- append/create-only from ChatGPT's perspective;
- not canonical dossier state;
- not canonical checkpoint progress;
- not a retry queue owned by ChatGPT.

Only GitHub may consume/delete/mark those files.

## Ownership after the change

### GitHub remains owner of

- snapshot creation;
- full scope;
- canonical order;
- immutable group plan;
- deterministic group identity;
- canonical expected sequence;
- gap detection;
- retry/unresolved interpretation;
- duplicate/replay interpretation;
- stale snapshot handling;
- validation;
- canonical dossier persistence;
- canonical manifest advancement;
- completeness;
- buffer consumption/cleanup;
- workflow orchestration.

### Scheduled ChatGPT remains owner of

- Steam store/review inspection;
- neutral dossier synthesis;
- processing exact GitHub-declared group items;
- create-only publication of each completed group;
- continuing to the next already-declared group without waiting for canonical ingest.

It does not become a queue manager.

## C. GitHub drain algorithm

The drain should treat a buffer push as a **wake-up signal**, not as “the one file this run must ingest”.

At workflow start:

1. Obtain the latest canonical manifest and immutable group plan.
2. Determine `expected_sequence` from GitHub-owned canonical progress.
3. Enumerate buffer artifacts for the current `snapshot_id`.
4. Ignore artifacts belonging to other snapshot ids for purposes of the current drain; handle their cleanup under explicit stale-buffer policy.
5. Starting at `expected_sequence`, attempt to consume the maximal consecutive valid prefix.

For every expected group:

- **Missing group:** stop the drain successfully at the gap. Never inspect group N+1 as a candidate for advancement.
- **Valid group:** validate schema, snapshot, sequence/range, immutable group hash, exact ordered appids/items, source binding and every dossier. Add it to the accepted prefix.
- **Malformed expected group:** fail closed for that group and every later group. If earlier groups in the same drain were already proven valid, they may still be committed as the valid contiguous prefix; the malformed group remains unaccepted and becomes the explicit blocker.
- **Wrong snapshot:** never apply it to current canonical state.
- **Duplicate pending create:** deterministic create-only naming should prevent a second copy of the same group at the same path.
- **Already canonically accepted replay:** do not persist or advance again. Treat it as idempotent stale replay and consume/reject it under GitHub policy.
- **Alternate-filename duplicate:** reject; the worker is never authorized to choose alternate names.
- **Stale submission:** never mutate the current snapshot from it.
- **Later group behind a gap:** leave untouched.

### Example

If canonical `expected_sequence = 4` and buffer contains `4, 5, 6, 7`:

`4 -> 5 -> 6 -> 7` are all validated and accepted in order.

If buffer contains `4, 5, 7`:

GitHub accepts `4 -> 5`, stops because `6` is absent, and leaves `7` pending.

If buffer contains `4, 5, malformed 6, 7`:

GitHub may persist the already-valid prefix `4 -> 5`, but must not accept 6 or 7. The result must explicitly report `blocked_at_sequence=6`.

### Atomic canonical advancement

The preferred drain transaction is:

- validate and build the maximal valid contiguous prefix;
- write all dossiers from that prefix in the working tree;
- compute one final canonical manifest state after that prefix;
- remove or mark consumed exactly those accepted buffer artifacts;
- create one canonical Git commit containing all of those changes.

A failed push/rebase does not create partial remote canonical state. A rerun must derive truth again from GitHub, not from the previous runner's memory.

### One multi-group drain vs one canonical ingest per group

**Recommend one multi-group drain per workflow run.**

Each buffered group remains individually validated, but the workflow should advance through as many currently available consecutive groups as possible before one canonical commit.

Reasons:
- avoids recreating the current per-ten manifest wait;
- reduces repeated writes to the same canonical manifest;
- reduces rebase/push contention;
- naturally coalesces a burst of buffer files;
- preserves exact per-group identity and gap semantics.

Running a separate canonical ingest workflow for every single group is safe if serialized, but it unnecessarily preserves much of the current Action/manifest latency and creates more contention.

## D. Concurrency

### Current state

Current dossier ingest workflow already has:

`concurrency: ingest-taste-steam-review-dossier-${{ github.ref }}`  
`cancel-in-progress: false`

So dossier ingest runs do not execute concurrently with one another.

However, the daily pre-AI workflow also writes `data/production/pre_ai/taste_steam_review_dossier_work.json` and uses a different concurrency group:

`pre-ai-deterministic-payload`

Therefore the repository does **not currently have one shared serialization boundary across all proven writers of the dossier manifest**.

This is acceptable today because conflicts fail closed through rebase/push behavior, but it is not the strongest basis for a high-throughput asynchronous buffer.

### Required minimal safety rule

Every workflow that can write the dossier canonical manifest must participate in one shared serialization boundary for that manifest.

At minimum that includes:
- dossier buffer drain;
- daily pre-AI snapshot preparation.

Because GitHub Actions' default concurrency behavior can replace an already-pending run with a newer pending run, a shared group must preserve queued canonical-state runs rather than allow a burst of buffer pushes to cancel a pending daily snapshot preparation.

Current GitHub Actions supports queued concurrency; the implementation task should choose a queued shared canonical-writer group rather than relying on default pending-run replacement.

### Coalescing

A burst of five or ten create-only buffer pushes must not produce five or ten **concurrent canonical writers**.

The first drain run that obtains the writer slot scans current repository buffer state and drains the whole contiguous prefix. Any later queued drain wake-ups can then become cheap no-ops if the first run already consumed their work.

This is state coalescing even if multiple event records were generated.

An additional custom coalescer is optional optimization, not required for correctness.

### Current workflow trigger logic that must change

The current workflow assumes the triggering commit contains exactly one inbox change and resolves exactly that one file.

That is incompatible with buffered drain semantics.

The future workflow must:
- inspect current buffer state, not rely on one trigger commit as queue state;
- tolerate a canonical drain commit deleting multiple accepted buffer files;
- avoid treating its own multi-delete cleanup commit as a new submission failure.

## E. Recovery behavior

### ChatGPT produced 30 dossiers / three groups, GitHub accepted only 10

The other two create-only group files remain durable in the buffer.

The next GitHub drain begins from canonical expected sequence and consumes them in order. ChatGPT does not need to resubmit or maintain retry state.

### GitHub fails after only part of a drain

If failure occurs before the canonical commit/push:
- no remote canonical advancement happened;
- the buffer remains the durable source of unconsumed submissions;
- the next run starts again from GitHub truth.

If a canonical commit was successfully pushed:
- the accepted prefix and consumed artifacts are durable;
- the next run begins from the advanced manifest.

No runner-local checkpoint is authoritative.

### Next Scheduled Task starts while old buffer files still exist

It reads current canonical state.

If the deterministic artifact for the current canonical expected group already exists but is not yet canonically advanced, the worker must not overwrite it, choose an alternate name, skip it, or invent a retry policy. It stops and leaves GitHub to drain.

If canonical state has advanced beyond those buffered groups, it resumes from the new canonical expected point.

This keeps restart/retry ownership on GitHub.

### New daily snapshot appears while old snapshot still has buffered submissions

Old-snapshot submissions must never be applied to the new snapshot.

Safe behavior:
- canonical drain filters by current `snapshot_id`;
- old buffered files become stale transport artifacts;
- GitHub may later delete/mark them stale under an explicit cleanup rule;
- the new daily preparation independently evaluates current dossier freshness/missing state.

Work performed for the superseded snapshot may be wasted, but canonical correctness is preserved.

Shared serialization between daily snapshot replacement and buffer drain reduces race exposure, but stale-snapshot validation is still mandatory.

### One group is never created

If group 6 is missing and group 7 is present:
- canonical progress stops at 6;
- group 7 remains pending;
- GitHub never skips the missing group.

A future worker invocation sees the GitHub-authorized expected group 6 and processes it. Once 6 exists, drain can accept 6 and then 7.

### ChatGPT interruption

Every successfully created group remains durable.

At most the group being semantically processed but not yet successfully created must be redone. This preserves the current ten-item durability property.

## F. Throughput impact

### Latency removed

Today the effective loop is:

`semantic processing of 10 -> create submission -> wait for GitHub Action/ingest/commit -> reload advanced manifest -> semantic processing of next 10`

The proposed architecture changes it to:

`semantic 10 -> create immutable group -> semantic next 10 -> create immutable group -> ...`

while GitHub independently runs:

`scan buffer -> validate contiguous prefix -> canonical persist/advance -> consume`

The removed delay is specifically the **canonical ingest round-trip between every ten dossiers**.

### Limits that remain

The architecture does not remove:
- Steam/store/review semantic processing time;
- Steam/source availability;
- GitHub create-file latency;
- GitHub Actions execution and Git commit/push time;
- GitHub API/connector behavior;
- safety blocks on GitHub writes;
- ChatGPT tool/runtime/context/platform limits;
- source/network failures;
- canonical drain throughput.

No exact platform/runtime quota is assumed by this recon.

## G. Minimal implementation surface

### Required contract / representation changes

**`config/taste_steam_review_dossier_contract.json`**
- authorize immutable full-snapshot group planning;
- distinguish worker traversal of predeclared groups from canonical checkpoint advancement;
- explicitly permit future predeclared group processing before prior group canonical ingest;
- retain GitHub ownership of retry/gaps/completeness.

**Work manifest / `scripts/taste_steam_review_dossier_daily.py`**
- expose an immutable checkpoint/group plan or equivalent canonical descriptors;
- define `group_sha256`;
- preserve current fixed snapshot identity and order;
- add canonical expected sequence/progress representation if needed.

**`config/taste_steam_review_dossier_persistence_bridge.json`**
- replace current `{snapshot_id}--{scope_sha256}.json` current-checkpoint-only identity with immutable per-group create-only identity;
- allow multiple pending files for one snapshot;
- define replay/stale/gap/consumption semantics;
- retain no direct ChatGPT canonical write.

**Ingest/drain scripts**
- `scripts/ingest_taste_steam_review_dossier_inbox.py`;
- `scripts/ingest_taste_steam_review_dossiers.py` or a bounded drain adapter;
- validate and consume maximal consecutive prefix;
- guarantee idempotent replay handling and one final manifest state.

**`.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`**
- change from “exactly one file from trigger commit” to state-based drain;
- serialize canonical writers;
- support multi-file accepted cleanup;
- no-op safely on already-drained wakeups.

**`.github/workflows/build-pre-ai-store-snapshot.yml`**
- participate in the same canonical dossier-manifest writer serialization boundary;
- continue preparing the fixed daily snapshot.

**`config/taste_steam_review_dossier_worker_prompt.md`**
- permit immediate continuation to the next immutable GitHub-declared group after successful create-only publication;
- remove the mandatory “wait for prior canonical ingest before next semantic group” rule;
- preserve all scope/order/retry/completeness prohibitions.

**Tests**
- extend current fixed-snapshot tests and add drain tests covering the acceptance plan below.

### Optional optimizations

- consumed/rejected receipt metadata instead of immediate deletion;
- stale-buffer cleanup metrics;
- explicit diagnostics showing `expected_sequence`, buffered contiguous count and blocked gap;
- a later trigger coalescer if redundant queued no-op drain runs become materially expensive;
- lightweight snapshot-liveness check by the worker before starting each later group.

### What should not change

- Taste Semantic Producer;
- Taste active pin authority;
- Taste Semantic Producer schedule or limits;
- dossier checkpoint size `10`;
- daily fixed-snapshot scope semantics;
- canonical queue order/deduplication policy;
- dossier neutrality/sampling rules;
- dossier TTL solely for this change;
- downstream semantic input authority;
- Scheduled Task schedule/cadence;
- any production limit.

## Migration of the current unfinished snapshot

The current accepted state is:

- `snapshot_id = d75f0b64dc983883a3d97a29c1ba1e0f25c679060ffdb5de269c10fadf05a180`;
- `prepared_required_count = 584`;
- `completed_required_count = 40`;
- `remaining_required_count = 544`;
- next checkpoint begins with appids `1158890, 1159290, 1161580, 1164940, 1167450, 1169040, ...`.

A safe migration must **not** rebuild scope and must **not** change that snapshot merely to adopt buffering.

Recommended migration procedure for a future authorized implementation:

1. Read and validate the existing V2 manifest.
2. Derive the immutable group plan directly from existing `prepared_required_items[]`, its existing hash, existing `snapshot_id`, and checkpoint size 10.
3. Prove that current `remaining_required_items[]` is exactly the suffix of `prepared_required_items[]` after the already-completed prefix.
4. Mark the first four ten-item groups as canonically accepted by inference from the already-validated 40-item completed prefix; do not recreate or re-ingest them.
5. Set the next canonical expected group to sequence 5.
6. Preserve the existing `snapshot_id`, source queue binding, prepared scope and remaining 544 items.
7. From group 5 onward, use the new immutable group identities.
8. Reject any attempted migration if the completed/remaining prefix relationship cannot be proven exactly.

This is a schema/contract migration of the same fixed snapshot, not a new scope refresh.

## Risks

1. **Contract drift risk.** A prompt-only change would be unsafe because current validator and persistence bridge remain current-checkpoint-only.
2. **Mutable shared-buffer risk.** A single `buffer.json` would introduce write conflicts and a new shared state machine.
3. **Cross-workflow manifest race.** Current dossier ingest and daily pre-AI writer use different concurrency groups while both can write the dossier manifest.
4. **Trigger storm / redundant runs.** Rapid create-only group files can produce many workflow wake-ups. Correctness requires serialization and state-based drain; optimization can coalesce work.
5. **Malformed-gap blocking.** An invalid expected group must block later groups. Operator visibility must make the exact blocked sequence obvious.
6. **Stale-snapshot accumulation.** A daily replacement can strand old buffer artifacts; cleanup policy is needed, but stale files must never mutate the new snapshot.
7. **Replay after consumed-file deletion.** Deleting accepted files permits the same deterministic path to be recreated later. Drain must treat sequence `< expected` as replay/no-op, never as new canonical work.
8. **Safety-block persistence.** The proposed design cannot guarantee GitHub create-file actions will never be safety-blocked. It should stop safely rather than bypass.
9. **Semantic work can outrun canonical drain.** Buffer accumulation is safe only because the fixed snapshot bounds it and GitHub owns acceptance; it is not permission for ChatGPT to invent a second queue or unbounded retry loop.
10. **Daily rollover while worker still processing old snapshot.** Correctness is preserved by snapshot binding; optional liveness checks can reduce wasted work.

## Acceptance test plan

A future implementation should not be accepted until all of the following are demonstrated with synthetic fixtures/non-production execution first, then one bounded production acceptance authorized separately:

1. **Immutable plan determinism**
   - same fixed snapshot yields identical group sequences/hashes;
   - 25 items produce exact `10/10/5`;
   - group identities do not change when canonical progress advances.

2. **No scope transfer**
   - worker cannot submit an appid outside a predeclared group;
   - reordered, skipped or extra appids fail closed;
   - changing current live queue after snapshot creation cannot mutate the group plan.

3. **Future buffering**
   - group N+1 submission validates as a buffer artifact even while canonical expected group remains N;
   - it is not canonically persisted until all preceding groups are accepted.

4. **Contiguous drain**
   - buffer `4,5,6,7` with expected 4 advances through 7 in one drain;
   - buffer `4,5,7` advances only through 5;
   - after 6 is later created, the next drain accepts 6 then 7.

5. **Malformed group**
   - malformed expected group never advances canonical state for that group or later;
   - a valid earlier contiguous prefix can remain durable;
   - blocker sequence is reported.

6. **Wrong snapshot / stale buffer**
   - old snapshot files cannot mutate a new snapshot;
   - stale artifacts do not block valid current-snapshot drain.

7. **Replay / idempotency**
   - exact duplicate create is prevented by create-only path;
   - recreated already-accepted artifact produces no canonical re-advance;
   - alternate-filename duplicate fails validation.

8. **Atomicity**
   - simulated failure before commit leaves remote canonical state unchanged;
   - simulated push/rebase failure does not create partial remote state;
   - successful multi-group drain produces one internally consistent final manifest and dossier set.

9. **Concurrency**
   - five or more rapid buffer file creates never result in concurrent dossier canonical-state writers;
   - daily snapshot writer and drain cannot concurrently mutate the dossier manifest;
   - pending daily preparation is not silently canceled by buffer-trigger pressure.

10. **Worker interruption/restart**
    - after worker creates groups 5 and 6 then stops, those files remain durable;
    - later canonical drain and worker resume do not duplicate them or skip a gap.

11. **Current-snapshot migration**
    - the existing snapshot keeps the same `snapshot_id`;
    - accepted 40 remain accepted;
    - remaining 544 remain the exact remaining scope;
    - next group begins at the already-known next checkpoint;
    - no old canonical dossier is rewritten solely by migration.

12. **Downstream invariants**
    - Taste Semantic Producer/pin tests remain unchanged and pass;
    - semantic input still fail-closes on missing/stale dossier requirements;
    - checkpoint size remains 10 and is never interpreted as a production quota.

13. **Throughput acceptance**
    - one controlled worker invocation demonstrates at least two successive group files created without waiting for the first group's canonical manifest advancement;
    - GitHub subsequently drains them in order;
    - no scope/order/completeness decision is made by ChatGPT.

## Changes

No production/config/workflow/code changes were made.

No Scheduled Task was read or changed through automation surfaces.

No production run was started.

The only permitted write for this task is this worker report.

## Validation / evidence refs

Primary canonical evidence inspected:

- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `KNOWN_WORKER_PITFALLS.md` (`PITFALL-003`, `PITFALL-004`)
- `PROJECT_DECISIONS.md` (`TASTE-004`, `TASTE-005`)
- `reviews/worker_reports/taste-dossier-live-prompt-acceptance-01.md`
- `reviews/worker_reports/taste-dossier-run-stop-recon-01.md`
- `reviews/worker_reports/taste-dossier-live-prompt-alignment-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/execution_ownership_contract.json`
- `data/production/pre_ai/taste_steam_review_dossier_work.json`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/taste_steam_review_dossier_daily.py`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/ingest_taste_steam_review_dossiers.py`
- `scripts/test_taste_steam_review_dossier_daily_snapshot.py`
- `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- GitHub Actions concurrency documentation current as of 2026-09-14.

Production evidence refs:
- worker submission commit `f56786cebf346b23b85f0fdb97501bd74f3c79af`;
- ingest run `34839554711`;
- ingest job `103961103392`;
- canonical ingest commit `aa14b6444110f40f0d46eb8fb19ab90c4d5ff51a`.

## Unresolved / implementation gate

The architecture itself is sufficiently understood to recommend it as viable, but current canonical contracts expressly authorize only current-checkpoint processing after canonical advancement.

Therefore the next authorized project step should be a **CONTRACT change**, not direct implementation under the present contract. That contract task should approve:
- immutable predeclared group identities;
- create-only multi-pending buffer semantics;
- GitHub-owned contiguous drain;
- shared canonical-writer serialization;
- worker continuation across predeclared groups without waiting for ingest.

Only after that contract is accepted should an implementation task modify the manifest, bridge, drain workflow/scripts and worker prompt.

No Taste Semantic Producer change is needed.

## Recommended next step

Director should create a bounded contract-change task for the dossier buffered-submission architecture described above. Do not start implementation until the amended canonical contract is accepted.

## Efficiency / reusable lesson

Candidate route update for a later authorized documentation task: `PROJECT_ROUTES.md` currently has no dedicated Steam-review-dossier route despite the subsystem now having a stable manifest -> create-only inbox -> canonical ingest path. A compact route entry would reduce future recon navigation. This RECON did not modify it because the task permits only the report write.
