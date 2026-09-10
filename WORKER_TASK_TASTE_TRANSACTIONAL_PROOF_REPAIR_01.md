# WORKER TASK — REPAIR TASTE TRANSACTIONAL PROOF EXPECTATION

## Task ID
`taste-transactional-proof-repair-01`

## Mode
`IMPLEMENT / NARROW NONSEMANTIC REPAIR`

## Expected report
`reviews/worker_reports/taste-transactional-proof-repair-01.md`

## User authorization
The user explicitly approved fixing the diagnosed nonsemantic transactional-proof defect.

## Goal
Repair only the transactional proof expected-retention logic so it matches the already-canonical post-ingest consumer behavior for the two diagnosed branches, and add regression coverage for both cases.

## Diagnosis source
Read once:
- `reviews/worker_reports/taste-manual-drain-ingest-failure-diagnose-01.md`

Known failing job/check-run id:
- `102798215077`

Known failure:
`Taste inbox transactional proof failed: ['ingested_key_retention_matches_negative_and_base_support_state', 'ai_queue_count_exact', 'queue_file_count_exact']`

Known diagnosed cases:
1. `App_2336880` — final Taste verdict is deterministic non-INCLUDE/EXCLUDE, so baseline `resolve_base_support_condition` must NOT be expected to remain queued when canonical consumer logic removes it.
2. `Sub_87601` — valid INCLUDE/moderate result, but selected post-fit deal scenario is deterministically EXCLUDE, so `resolve_grounded_negative_analysis` must NOT be expected to remain queued when canonical consumer logic removes it.

The 10 semantic results themselves are already diagnosed as valid and must not be regenerated or edited.

## Mandatory execution order

### Step 1 — create durable report first
The FIRST repository mutation after reading this task must be creation of the expected report with:
- lifecycle: `in_progress`;
- current UTC;
- implementation_status: `not_started`;
- next_action: inspect exact diagnosed functions/tests.

Commit immediately. If report creation fails, STOP.

### Step 2 — inspect only exact affected implementation/test paths
Start from the diagnosis and inspect only the exact current code needed for:
- `process_taste_inbox.py::expected_retained_work(...)` and directly related transactional-proof logic;
- `scripts/validate_taste_inbox_transactional_proof.py` and directly related fixtures/tests;
- canonical consumer gating logic only as needed to mirror the already-existing authoritative behavior.

Do not broaden into unrelated architecture changes.

### Step 3 — implement the smallest repair
Change the proof expectation model, not the canonical consumer behavior.

Required behavior:
- when a newly cached Taste result deterministically excludes the family before base-support work construction, proof must not expect stale baseline base-support work to remain;
- when a valid cached Taste fit selects a deterministic EXCLUDE deal scenario before grounded-negative work construction, proof must not expect grounded-negative work to remain;
- all other existing retention expectations and fail-closed checks remain unchanged unless directly necessary for correctness.

Do NOT weaken queue-count exactness. The goal is to make expected state correct so exact proof still passes/fails honestly.

### Step 4 — add regression coverage
Add focused regression cases reproducing both diagnosed branches:
1. baseline base-support work + newly cached final Taste EXCLUDE => no retained base-support queue row expected;
2. INCLUDE/moderate + incomplete negative analysis + deterministic post-fit deal EXCLUDE => no retained grounded-negative queue row expected.

Keep existing regression fixtures passing.

### Step 5 — validation
Run the narrowest relevant tests first, including the transactional-proof regression suite.

Then run any directly affected Taste inbox/ingest validation tests required to prove no guardrail regression.

Record exact commands and results in the report.

### Step 6 — do NOT retry the real inbox batch
This task is code/test repair only.

Do NOT:
- rerun canonical ingest for `manual-throughput-drain-01-batch-001.json`;
- edit/delete that inbox file;
- regenerate or edit its 10 semantic results;
- change queue/cache/production state;
- start batch 2;
- modify Scheduled Task;
- change producer generation, V5 contract semantics, profile binding, evidence/factor rules, price-blind rules, or retry policy.

## Acceptance criteria
PASS only if:
- both diagnosed cases are explicitly covered by regression tests;
- transactional proof now models canonical consumer exclusions correctly;
- queue/count exactness remains strict;
- existing relevant tests pass;
- no semantic result or production state is changed;
- the untouched 10-result inbox submission remains available for a later retry.

## Finish
Finalize report with one of:
- `complete_repair_ready_for_existing_batch_retry`
- `needs_followup`
- `blocked`

If complete, explicitly state:
- exact files changed;
- exact tests added;
- exact validation results;
- whether the existing 10-result submission can now be retried unchanged;
- confirmation that no retry was performed in this task.

Then STOP.
