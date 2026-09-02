# WORKER TASK — SEMANTIC RUNTIME COMPLETION ACCEPTANCE 01

Task ID: `semantic-runtime-completion-acceptance-01`
Mode: `ACCEPTANCE`
Report: `reviews/worker_reports/semantic-runtime-completion-acceptance-01.md`

## Why this task exists

System Audit `reviews/system_audits/baseline-01.md` proved two linked user-impact problems:

1. semantic Taste work can be correctly queued while the existing scheduled semantic worker remains operationally unobserved;
2. unresolved semantic readiness is fail-closed and can silently remove valid live-sale candidates from the user-visible choice set, making an incomplete feed look authoritative.

Trine 4 / `App_690640` is the concrete incident. Do not re-diagnose that game.

## Read first

- `reviews/system_audits/baseline-01.md`
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`
- `reviews/worker_reports/trine4-missing-diagnosis-01.md`
- `data/production/pre_ai/chatgpt_payload.json`
- `config/execution_ownership_contract.json`
- `scripts/build_visual_feed_v2.py`
- the smallest exact runtime/automation evidence needed to perform this acceptance

Do not perform broad Git-history archaeology.

## Goal

Determine whether the existing production system provides enough durable evidence to answer both questions:

### A. Is the semantic worker operationally observable?
A production operator must be able to establish, for the existing scheduled semantic runtime, an equivalent of:
- enabled/disabled or otherwise definitely active/inactive;
- expected cadence or next execution expectation;
- last successful execution/progress signal;
- whether the current GitHub-prepared semantic queue is actually progressing.

Do not create a second scheduler, semantic worker, manual Taste path, or duplicate queue.

If the underlying platform cannot expose one of those exact fields, determine whether the current architecture already exposes an equivalent trustworthy heartbeat/progress proof. Queue presence alone is not sufficient.

### B. Can the published feed truthfully communicate semantic incompleteness?
Determine whether current canonical publication/acceptance distinguishes:
- `scope partitioning completed`, from
- `user-visible recommendation result is sufficiently complete/current`.

A large unresolved required semantic scope must not be able to look indistinguishable from a fully current recommendation feed.

Acceptance should establish what exact current signal exists for:
- unresolved semantic count;
- unresolved age/staleness where available;
- whether the user-visible/current-payload layer has an explicit degraded/incomplete state;
- whether a published feed can silently omit materially many candidates while still looking fully healthy.

## Boundaries

Do NOT:
- change Taste policy, weights, scores or exclusion semantics;
- make a manual verdict for Trine 4 or any other game;
- create a second scheduler/runtime/queue;
- process production items manually;
- weaken fail-closed semantic safety merely to make more games appear;
- redesign the UI;
- implement a fix in this task unless an existing acceptance mechanism only needs a trivial configuration/metadata activation explicitly already supported by canonical contracts. Otherwise stop at exact missing mechanism.

## Required result

Report exactly:

1. `Semantic runtime observability`: `pass | fail | partial`
2. `Feed semantic completeness visibility`: `pass | fail | partial`
3. Current concrete evidence for each result.
4. If failed/partial, the smallest missing mechanism(s), no more than 2.
5. Whether the defect requires an `IMPLEMENT` task.
6. One recommended next step only.

If implementation is required, specify a bounded implementation contract with exact files/ownership boundaries, but do not perform the implementation here.

## Completion

Save:
`reviews/worker_reports/semantic-runtime-completion-acceptance-01.md`

Status exactly one:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Final answer must state the exact report path and exact refs used.