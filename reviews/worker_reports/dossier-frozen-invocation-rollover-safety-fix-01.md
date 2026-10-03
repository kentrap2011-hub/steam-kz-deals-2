# Dossier frozen invocation rollover safety fix 01

## 1. Task

Task: `WORKER_TASK_DOSSIER_FROZEN_INVOCATION_ROLLOVER_SAFETY_FIX_01.md`

Mode: `IMPLEMENT / VALIDATE`

Goal: preserve a legitimate already-started Dossier semantic group across unrelated later `main` movement or daily snapshot rollover without weakening GitHub-owned authority, stale-work protection, exact-product validation, or truthful current-snapshot progress.

Sequencing gate was satisfied before PR opening: PR-production trigger isolation was already merged on `main` via PR #141, merge `da71fb7578c5fe467da0ce8e3decfbc62a6465a4`, and the current execution-ownership regression proves PR-origin `workflow_run` cannot authorize production mutation.

## 2. Incident reproduction

The production incident began from exact prepared snapshot:

- snapshot: `448f12da0193d4b5d43b65042e6e6826f39f571d1ae260055913ef11a3125f18`;
- sequence: `1`;
- group SHA: `50ee28265629b1fd51275e9c27ddf34510a5443c65a875dd96b2b18a640e561e`.

The semantic invocation performed material exact-product/player-feedback research. Before publication, mutable current state had rolled to snapshot:

`a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`.

The old runtime treated that normal rollover as a publication-liveness failure, stopped with `snapshot_plan_or_binding_changed`, attempted no publication, and discarded otherwise valid semantic work.

The new regression reproduces the same A -> B timing: freeze A, create B before result publication, then submit the exact A transport. The result is accepted against A's frozen authority, persisted only as validated neutral Dossier content, and current B progress changes only through separate exact cache reconciliation.

## 3. Architecture preflight

The safe authority model is:

1. One Dossier group is legitimate only when GitHub prepared the exact canonical work manifest, immutable group plan, worker index, exact group descriptor, semantic/evidence binding, runtime binding, and pending group state.
2. Before material semantic work, the worker creates one nonce-only create-only run-start marker. The marker contains no snapshot, group, authority commit, or worker-selected historical identity.
3. GitHub's actual single parent of that marker commit is the frozen invocation authority. This makes the frozen authority Git-history-derived rather than worker-asserted.
4. The frozen authority binds:
   - snapshot and prepared-required identity;
   - exact group plan and sequence;
   - ordered exact items/appids;
   - group/items hashes;
   - evidence/schema/worker binding;
   - exact worker descriptor bytes;
   - exact runtime prompt bytes/revision/hash;
   - contract/persistence bytes;
   - exact Git ancestry/provenance.
5. Later unrelated `main` movement, daily snapshot replacement, queue ordering changes, or group repartitioning do not retroactively change that frozen authority.
6. Material incompatibility still fails closed: forged marker/history, mismatched descriptor/binding, wrong exact product identity, incompatible evidence binding/TTL, already-consumed authority, duplicate transport, or old-to-new group rebinding.
7. Old accepted semantics can populate neutral per-appid Dossier cache only. They never directly mark an unrelated new group accepted.
8. A current group advances from cache only if every exact current item independently has a strict fresh current-compatible dossier.
9. The design adds no second queue, retry owner, scheduler, checkpoint owner, or ChatGPT-owned scope authority.

## 4. Root cause

The previous Dossier architecture had already made per-group progress non-blocking, but runtime publication still used the latest mutable worker index/snapshot/plan as a liveness lock.

That conflated two different questions:

- whether the work was legitimately authorized when semantic execution began; and
- whether GitHub had since prepared newer legitimate work.

Normal daily rollover therefore invalidated old in-flight work even when its exact prepared authority and semantic/evidence binding remained valid.

During PR validation, two narrower implementation defects were also found and corrected:

- current-snapshot marker-authorized transports initially compared a full frozen worker descriptor with a raw group-plan entry; the comparison now reconstructs the exact current worker descriptor before equality validation;
- rollover cache compatibility initially compared current queue `key` as though it were product identity. The old work binding is already strictly proven by frozen authority; neutral Dossier reuse is therefore gated by exact appid/title plus current semantic/evidence/TTL compatibility, while current group progress remains separately bound to the new exact current items.

## 5. Frozen authority model

Runtime now creates:

`data/ai_inbox/taste_steam_review_dossiers/run_starts/{run_start_nonce}.json`

with only:

- schema;
- schema_version;
- fresh 32-hex nonce.

The durable marker commit is the worker-visible `run_start_anchor_commit`. The worker does not choose or serialize the authority commit. GitHub derives the marker's actual single parent and validates that the marker commit added only that marker path.

Late candidate/terminal transports carry only a `run_start_authority` reference containing:

- reference schema/version;
- marker commit SHA;
- nonce.

GitHub reconstructs the marker parent, loads the exact historical index/manifest/descriptor/runtime bytes from Git, validates the exact frozen descriptor and pending state, and validates that the result transport was introduced after the marker on the correct first-parent history.

This proves the authority was genuinely GitHub-prepared and prevents arbitrary historical snapshot selection.

## 6. Rollover-safe persistence semantics

A valid late result remains bound to its old frozen snapshot/group.

For a late Dossier candidate:

- validate the transport against the exact frozen historical authority;
- require current semantic/evidence/TTL compatibility;
- reject exact current product-title conflicts for any overlapping appid;
- preserve an already-present strict current-compatible dossier rather than overwrite it;
- otherwise persist validated per-appid neutral dossier content;
- append a frozen-authority consumption audit;
- never directly mutate a new snapshot's group state.

For a late semantic-exhaustion terminal receipt:

- validate it against the old frozen authority;
- archive/audit it against that old authority only;
- never fail or accept a new snapshot group because of the old receipt.

Consumed frozen authorities are replay-cleanup-only and cannot repeat cache mutation or progress advancement.

## 7. Current-snapshot reuse semantics

Before material web research for each frozen item, runtime requires checking the exact cache view frozen at invocation start and reusing an already strict compatible fresh dossier verbatim.

After GitHub persists a valid late dossier, current work may reuse that neutral cache through deterministic reconciliation:

- compatibility is evaluated per exact current item;
- appid/title, strict dossier schema, web-evidence binding, TTL and provenance validation remain mandatory;
- partial overlap never marks a whole group complete;
- a current group is accepted from cache only when every current item is independently satisfied.

Thus a daily rollover does not force duplicate web research when the resulting dossier remains semantically reusable, but it also cannot fabricate current progress.

## 8. Changes

Implemented on branch `fix/dossier-frozen-invocation-rollover-safety-01`:

- added `scripts/taste_steam_review_dossier_authority.py` for Git-history-derived marker-parent authority;
- extended buffered ingest/drain for current marker-authorized transports, late frozen transports, neutral cache persistence, consumption audit, replay deduplication and current cache reconciliation;
- updated Dossier runtime prompt with nonce-only frozen invocation start, frozen traversal, per-item cache reuse and rollover-safe publication;
- updated Dossier contract, persistence bridge and terminal receipt schema for authority references and rollover semantics;
- updated worker projection/runtime binding;
- updated canonical ingest entrypoint plumbing;
- added `scripts/test_taste_dossier_frozen_invocation_rollover.py`;
- wired frozen rollover regressions into `Validate buffered Steam review dossier runtime`;
- preserved the stable existing runtime revision identity and existing ownership inventory so the change extends behavior without creating a new semantic owner.

Current canonical Dossier snapshot/progress was never replaced by stale branch state during synchronization. The branch was repeatedly rebased-by-merge onto current `main`, taking current production cache/work/index state and changing only the intended runtime binding in the active worker index.

## 9. Regression coverage

The final Dossier validation proves:

1. exact A -> B incident reproduction remains publishable/ingestible under frozen A authority;
2. unrelated `main` movement after marker does not invalidate a current frozen group;
3. a changed B partition/order does not rebind A group identity;
4. materially changed evidence binding fails closed without cache/progress mutation;
5. a forged historical commit/group cannot masquerade as a run-start authority;
6. consumed/duplicate frozen transport is create-only/idempotent and replay-cleanup-only;
7. accepting frozen A cannot falsely advance unrelated B progress;
8. compatible current work can consume the newly persisted cache without another semantic research run;
9. existing nonblocking traversal, retryable invalid transport handling and failed-group recovery regressions remain green;
10. Progressive Deep/Fast ownership and execution remain independent and unchanged.

The same Dossier workflow also runs all prior daily snapshot, buffered submission, same-day preservation, strict recovery, prepublication, contract-gap, language, semantic consistency, bounded retrieval, provenance, package identity, story DLC, parallel validation, temporal classification, atomic staging and terminal-receipt regressions.

## 10. Validation

Final implementation head validated before report-only commit:

`39b62238d53a2eead29775931ceb1f8eddb471c9`

Synchronized base:

`main@4c5c851bcf712c351a67afb670dc8116290cf894`

Compare immediately before report: `behind_by=0`.

Green runs:

- `Validate buffered Steam review dossier runtime` — run `37130680399`, job `111224993354`, success; step `Frozen invocation rollover regression` succeeded.
- `Validate execution ownership` — run `37130680398`, job `111224993500`, success; both `Validate component ownership boundaries` and `Validate workflow-run production authority` succeeded.
- `Validate Progressive PASS 2 core` — run `37130680429`, job `111224993560`, success; core, Dossier integration and canonical-writer staging regressions succeeded.

The durable-report commit is intentionally documentation-only and separately triggers `Validate backlog dispositions`.

## 11. Production safety

No real Dossier backlog was run as implementation validation.

No ChatGPT Scheduled Task was created, edited, enabled, disabled, paused, resumed, renamed or deleted.

No Fast or Deep semantic worker was run or changed.

The branch was not opened as a PR until the separate PR-production trigger-isolation fix was confirmed merged. Current execution-ownership validation proves successful feature/PR `workflow_run` is rejected as production authority and only successful upstream `main` authority is accepted for guarded mutating paths.

Current canonical production progress was preserved during every synchronization; fresh `main` work/index/cache state was used as the base rather than restoring older branch data.

## 12. Exact PR/commit/run refs

Task branch:

`fix/dossier-frozen-invocation-rollover-safety-01`

Implementation PR:

`#143` — `Fix Dossier frozen invocation rollover safety`

Final tested implementation head before report:

`39b62238d53a2eead29775931ceb1f8eddb471c9`

Current synchronized base before report:

`4c5c851bcf712c351a67afb670dc8116290cf894`

Final green validation refs:

- Dossier runtime: run `37130680399`, job `111224993354`;
- execution ownership: run `37130680398`, job `111224993500`;
- Progressive PASS 2 core: run `37130680429`, job `111224993560`.

Sequencing-gate implementation:

- PR #141;
- merge `da71fb7578c5fe467da0ce8e3decfbc62a6465a4`;
- post-merge execution-ownership run `37122344406`.

The exact implementation merge commit will be appended in the post-merge closeout update to this durable report.

## 13. Unresolved

No unresolved architecture or correctness blocker is known within this task.

The implementation intentionally does not alter semantic evidence rules, exact-product validation, Dossier scheduler cadence, failed-group recovery ownership, Fast/Deep semantics, Taste profile/scoring, or production backlog processing.

A live production semantic invocation is outside implementation validation and is not required to establish the deterministic rollover-safety contract.

## 14. Status

`implementation_complete_ready_for_director_acceptance`

## 15. Recommended next step

Director reviews the merged Dossier rollover-safety implementation and records acceptance.
