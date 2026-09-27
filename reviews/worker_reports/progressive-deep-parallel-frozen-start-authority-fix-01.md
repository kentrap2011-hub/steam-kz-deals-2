# Progressive Deep parallel frozen start authority fix 01

## Task

Task: `WORKER_TASK_PROGRESSIVE_DEEP_PARALLEL_FROZEN_START_AUTHORITY_FIX_01.md`

Repository: `kentrap2011-hub/steam-kz-deals-2`

Implementation PR: #101 — `Fix Deep frozen start authority under parallel Dossier writes`

PR head: `0368ffc06cf1121476b9dd2b4f3b0124c628c03b`

Merge commit: `544c0400b3290f945d1de5464d8dfa9f4faf2aa0`

## Architecture preflight

- Deep start authority remains owned by the GitHub control plane.
- The semantic worker does not choose scope, order, eligibility, freshness, recovery, attempts, completeness, or canonical acceptance.
- The exact invocation authority is now selected by GitHub from the actual parent of the create-only V2 run-start marker commit.
- The exact PASS 2 contract/work Git blobs are computed and confirmed from that GitHub-selected authority.
- The worker freezes ordered work, immutable profile pin, exact accepted Dossier content/binding/expiry, recovery authorization, and exact transport paths only from that immutable authority.
- Whole-`main` equality was stronger than the business requirement because Dossier and Deep are independent stages and unrelated/later canonical writes may legitimately advance `main` concurrently.
- The replacement does not allow arbitrary historical work: the worker cannot provide a V2 authority commit or contract/work blob identity; GitHub derives them from the actual marker-parent commit, then existing exact work/Dossier/profile/recovery validation and consumed/retired-work guards remain in force.
- No control-plane responsibility moved to ChatGPT. No scheduler, queue, retry daemon, backlog manager, or per-item mutable reread was added.

## Verified root cause

The legacy V1 run-start rule required the marker commit's parent to equal an earlier worker-observed whole-`main` commit. If Dossier or another canonical writer advanced `main` between the worker's observation and durable marker creation, GitHub rejected the marker as superseded even when the exact Deep work itself was still legitimate.

That repository-wide head-stability requirement serialized otherwise independent stages and caused zero-work Deep invocations during legitimate parallel Dossier progress.

## Corrected authority model

New Deep invocations use `PROGRESSIVE-PASS2-RUN-START-MARKER-V2`.

The V2 marker contains only its schema/contract plus a fresh nonce. It intentionally contains no worker-selected authority commit, PASS 2 blob identity, or timestamp.

When GitHub persists the marker:
1. the marker commit's actual single parent becomes `run_start_authority_commit`;
2. GitHub computes the exact PASS 2 contract/work blob identities from that parent;
3. the worker reads and freezes all semantic inputs only from that exact parent;
4. semantic computation may proceed provisionally against that immutable view;
5. no result or terminal receipt is publishable until the GitHub-owned confirmation receipt durably confirms the same marker-parent authority, exact contract/work blobs, nonce/marker lineage, and trusted marker commit time.

Therefore Dossier and Deep can operate independently in parallel:
- a Dossier/canonical write that lands before the marker is naturally included in the marker parent and this Deep invocation;
- a Dossier/profile/work/recovery write that lands after the marker/freeze belongs to the next Deep invocation;
- later `main` movement alone no longer invalidates the current frozen Deep invocation.

## Changes

The accepted implementation updated the canonical decision/route/contracts, worker prompt, GitHub run-start/ingest authority logic, and focused regressions.

Key behavior:
- V2 marker authority is GitHub-selected from the actual marker parent;
- GitHub computes the exact PASS 2 contract/work blobs;
- the worker cannot inject an old authority into V2;
- later repository movement alone is non-invalidating;
- existing exact Dossier/profile/recovery/work bindings remain immutable within one invocation;
- missing/rejected/mismatched confirmation still publishes nothing and consumes no attempt;
- legacy V1 compatibility remains fail-closed under its existing rules;
- Fast semantics, Dossier evidence semantics/recovery, and Scheduled Task configuration were not changed.

## Validation

### Before merge

PR #101 head `0368ffc06cf1121476b9dd2b4f3b0124c628c03b` was open, non-draft, `mergeable=true`, and `mergeable_state=clean` immediately before merge.

Required PR-head checks passed:
- `Validate Progressive PASS 2 core` — run `36323011599` — success.
- `Validate backlog dispositions` — run `36323011605` — success.

### After merge on main

Merge commit: `544c0400b3290f945d1de5464d8dfa9f4faf2aa0`.

Main validation:
- `Validate Progressive PASS 2 core` — run `36334678553` — success.
  - Progressive async traversal + invalid transport regression — success.
  - Deep parallel frozen-start regression — success.
  - PASS 2 core regression — success.
  - PASS 2 Dossier integration regression — success.
  - PASS 2 canonical-writer staging regression — success.
  - PASS 1 regression and PASS 1 ingest/staging regressions — success.
  - Progressive personalization, unresolved-row preservation, visual routing and UI provenance regressions — success.
  - Active production eligibility recomputation completed without consuming attempts.
- `Validate backlog dispositions` — run `36334678558` — success.
- `Validate execution ownership` — run `36334678675` — success.

The focused regression suite proves:
- concurrent Dossier/work movement does not invalidate a legitimate frozen Deep invocation;
- an unrelated GitHub write does not invalidate it merely because the repository head moved;
- forged/material binding mismatch is rejected;
- arbitrary historical/non-authoritative work cannot be revived;
- newer Dossier/work state is not substituted into an already-frozen invocation;
- missing/rejected confirmation still produces no semantic publication and zero attempt;
- asynchronous sibling traversal remains non-blocking;
- Fast/Dossier/Deep independence and ownership boundaries remain intact.

## Production observations

No production Deep backlog was manually processed for validation.

No production Dossier or Fast semantic worker was manually triggered for this task.

No ChatGPT Scheduled Task was created, changed, paused, enabled, disabled, or manually triggered.

Post-merge acceptance relied on the existing GitHub validation workflows and the canonical V2 state now present on `main`.

The corrected production rule is now explicit: once one Deep invocation has frozen the GitHub-selected marker-parent authority, later Dossier data does not retroactively replace or cancel that invocation; it becomes input to a subsequent Deep invocation.

## Unresolved

No blocking unresolved issue remains for this task.

A manual production Deep run was intentionally not used as an acceptance test. The task explicitly forbids manual backlog processing and Scheduled Task changes; focused regressions plus successful post-merge GitHub validation provide the required acceptance proof.

## Status

`complete_ready_for_director_acceptance`

## Recommended next step

Director performs one bounded acceptance review of PR #101, merge `544c0400b3290f945d1de5464d8dfa9f4faf2aa0`, this report, and the successful post-merge validation runs; no manual production rerun is required for this task.

## Exact PR / commit / run refs

- Task: `WORKER_TASK_PROGRESSIVE_DEEP_PARALLEL_FROZEN_START_AUTHORITY_FIX_01.md`
- PR: `#101`
- PR title: `Fix Deep frozen start authority under parallel Dossier writes`
- Branch: `fix/progressive-deep-frozen-start-authority-01`
- Final PR head: `0368ffc06cf1121476b9dd2b4f3b0124c628c03b`
- Merge commit: `544c0400b3290f945d1de5464d8dfa9f4faf2aa0`
- PR PASS 2 validation: `36323011599`
- PR backlog validation: `36323011605`
- Main PASS 2 validation: `36334678553`
- Main backlog validation: `36334678558`
- Main execution ownership validation: `36334678675`

## Efficiency / reusable lesson

For independent semantic stages, repository-wide head equality is an unnecessarily broad anti-race lock. The reusable pattern is to let the control plane select and durably confirm a minimal immutable invocation authority, then bind all semantic inputs/results to that authority while allowing unrelated repository progress to continue. This preserves fail-closed stale-work protection without serializing otherwise independent pipelines.
