# WORKER TASK — Dossier retryable transport reject fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `DOSSIER_RETRYABLE_TRANSPORT_REJECT_FIX_01`
Worker slot: `ЧАТ 2`
Mode: `DIAGNOSE / IMPLEMENT / VALIDATE`

## Purpose

Restore forward progress of the existing Taste Steam Review Dossier pipeline, which is currently blocked at sequence 20 by repeated `retryable_transport_rejected` results.

This is a technical control-plane/transport repair task.

It is **not** a Dossier semantic-worker invocation. Do not generate new semantic Dossier content yourself.

## Current canonical evidence

At task creation:

- current snapshot:
  `a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`
- `next_pending_sequence = 20`
- `accepted_group_count = 19`
- `accepted_dossier_count = 57`
- `failed_group_count = 0`
- `pending_group_count = 112`
- `pending_dossier_count = 334`

Two later semantic candidates were produced:

### Sequence 20
Submission commit:
`d0a6ccd1d13179f52c77ae6071e2aa29184cc892`

Ingest run:
`37345670048`

Observed ingest result:
- workflow conclusion: `success`;
- `accepted_group_count_this_run = 0`;
- `retryable_transport_rejection_count_this_run = 1`;
- `rejected_sequences = [20]`;
- overall internal status: `retryable_transport_rejected`.

The candidate was moved to quarantine under:
`quarantine/taste_steam_review_dossier_inbox/retryable_transport/.../g000020/...`

### Sequence 21
Submission commit:
`170c80e805769849a08eda1dc932a68a5bb38b5c`

Ingest run:
`37346094306`

Observed ingest result:
- workflow conclusion: `success`;
- `accepted_group_count_this_run = 0`;
- `retryable_transport_rejection_count_this_run = 1`;
- `rejected_sequences = [21]`;
- overall internal status: `retryable_transport_rejected`.

The candidate was moved to quarantine under the corresponding `g000021` retryable-transport path.

The canonical index remained at sequence 20.

## START

1. Read current `CHAT_PROTOCOL.md` and perform the required START gate.
2. Read the current canonical Dossier runtime prompt, worker prompt, contract, persistence bridge, execution ownership contract, worker index, and exact ingest/recovery implementation relevant to this failure.
3. Inspect only the exact commits/runs/artifacts for sequences 20 and 21 needed to determine the rejection reason.
4. Do not do a broad Dossier redesign.

## Required diagnosis

Find the **exact deterministic reason** each artifact was classified as `retryable_transport_rejected`.

Do not stop at the generic status.

Determine whether the cause is one or more of:

- missing / mismatched frozen invocation authority;
- stale or invalid run-start reference;
- wrong parent/authority commit;
- submission-path/binding mismatch;
- snapshot/group descriptor mismatch;
- race with concurrent main movement;
- ordering/sequence issue;
- transport replay/deduplication issue;
- a defect in retryable-transport classification/recovery;
- another concrete cause proven from code and artifacts.

Do not infer the cause from names alone.

## Correctness requirements

Preserve all accepted architecture:

- GitHub owns scope/order/validation/persistence/recovery;
- semantic worker remains bounded data plane only;
- frozen invocation authority must remain fail-closed against forged/stale authority;
- later unrelated `main` movement must not invalidate a legitimately frozen invocation by itself;
- no sibling group may block unrelated valid groups except where exact canonical ordering requires it;
- no duplicate acceptance;
- no semantic result fabrication;
- no weakening of exact snapshot/group/binding checks merely to make groups 20/21 pass.

## Implementation

If this is an implementation defect, make the smallest fix in the existing canonical Dossier transport/ingest/recovery path.

Add regression coverage that reproduces the exact failure mode seen for sequences 20/21.

The regression must distinguish:
- a legitimately frozen candidate that should remain acceptable/recoverable;
- a genuinely stale/forged/wrong-binding candidate that must still fail closed;
- duplicate/replay safety.

If the rejection is correct and the semantic submissions themselves were invalid, do **not** weaken validation. Instead make the exact blocked state visible and prepare only the canonical safe recovery path required for a new valid semantic submission.

## Recovery of sequences 20/21

After fixing the transport defect, inspect the quarantined artifacts.

If and only if the existing exact semantic artifacts for 20/21 are still:
- authentic;
- exact-bound;
- generated under valid frozen authority;
- semantically/currently compatible;
- safe to replay under the canonical recovery model,

then recover them through the GitHub-owned canonical path without regenerating semantic content.

If they cannot be safely recovered, leave them quarantined and prepare the exact canonical authorization/state needed for the semantic worker to resume from sequence 20.

Do not manually edit a rejected JSON file to force acceptance.

## Workflow status correctness

The current GitHub Action can conclude `success` while all submitted groups were transport-rejected.

Assess whether this masks a production-stopping condition.

If appropriate within this task boundary, make the workflow/status surface distinguish:
- successful ingest with accepted/reconciled progress;
- nonfatal isolated retryable rejection where other progress exists;
- zero-progress transport rejection that leaves the head sequence blocked.

Do not turn expected isolated nonblocking quarantine into a global fatal failure if that would violate the current nonblocking architecture.

## Acceptance

Before closeout:

1. deterministic Dossier tests pass;
2. execution ownership tests pass;
3. backlog dispositions / relevant Dossier guards pass;
4. current canonical state is reconciled from fresh `main`;
5. sequence 20 is either:
   - canonically accepted/recovered and the index advances, or
   - explicitly prepared for one clean new semantic retry with exact reason and authorization;
6. sequence 21 is handled safely according to ordering/current authority;
7. no Scheduled Task is created, changed, paused, resumed, or run;
8. no Dossier or Deep semantic worker is invoked by this developer task;
9. Deep, Fast, ranking, translation, Steam discovery, and site publication are not changed.

## Report

Create:
`reviews/worker_reports/dossier-retryable-transport-reject-fix-01.md`

Include:

- exact root cause;
- exact evidence for sequence 20 and 21;
- why the existing runs appeared green despite no progress;
- files changed;
- regression coverage;
- PR and checks;
- final canonical Dossier counts;
- whether 20/21 were recovered or require a new semantic invocation;
- exact next user/Director action, if any.

Allowed final statuses:

- `complete_progress_restored`
- `complete_fix_ready_semantic_retry_required`
- `diagnosed_correct_rejection_semantic_retry_required`
- `blocked_needs_director_decision`
