# WORKER TASK — RETRY EXISTING 10-RESULT TASTE BATCH

## Task ID
`taste-existing-batch-retry-01`

## Mode
`AUTHORIZED PRODUCTION RETRY / EXISTING RESULTS ONLY`

## Expected report
`reviews/worker_reports/taste-existing-batch-retry-01.md`

## Goal
Retry canonical ingest for the already-produced untouched 10-result inbox submission after the transactional-proof repair, without regenerating semantic results and without starting any new Taste batch.

## Exact existing submission
- inbox file: `data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json`
- expected current blob SHA from predecessor repair report: `54faa8bc16064b15df8dd781d1988986b05e0e1c`
- original submission commit: `f138d5216248c999fde588c47ca5088ff9c076ee`

## Required predecessor reports
Read once:
- `reviews/worker_reports/taste-manual-drain-ingest-failure-diagnose-01.md`
- `reviews/worker_reports/taste-transactional-proof-repair-01.md`

## Mandatory execution order

### Step 1 — create durable report first
The FIRST repository mutation after reading this task must be creation of the expected report with:
- lifecycle: `in_progress`;
- current UTC;
- retry_status: `not_started`;
- inbox_blob_sha_before_retry;
- queue_count_before_retry;
- next_action: verify unchanged submission and launch one canonical ingest retry.

Commit immediately. If report creation fails, STOP.

### Step 2 — pre-retry verification
Before retrying, verify:
- exact inbox file still exists;
- its blob SHA is unchanged from the expected value above;
- canonical queue count is still consistent with predecessor state unless a clearly authorized unrelated canonical change occurred;
- no receipt/accepted commit already exists for this exact batch;
- no later successful retry for this exact submission already occurred.

If a successful retry already exists, do not launch another. Consume and report that result instead.

If the inbox changed, disappeared, or bindings/state no longer match safely, STOP fail-closed and diagnose per `WORKER_REPORT_DURABILITY_PROTOCOL.md`.

Checkpoint report before launch.

### Step 3 — launch exactly one canonical ingest retry
Use the existing canonical ingest path/workflow for this exact inbox submission.

Do NOT regenerate or edit any semantic result.
Do NOT create a replacement inbox file.
Do NOT start batch 2.
Do NOT modify Scheduled Task.

Immediately after launch, checkpoint the exact workflow run/job id in the report before polling.

Follow `WORKER_ANTI_STALL_PROTOCOL.md` for bounded polling.

### Step 4 — consume retry result
If successful, verify canonically:
- exact 10-result batch accepted;
- ingest receipt/batch id exists and is complete;
- exact inbox submission consumed/removed as canonical workflow defines;
- queue decreases consistently with the canonical rebuilt state;
- exact accepted subjects are no longer pending where appropriate;
- no extra semantic result or unrelated batch was ingested;
- Scheduled Task remained untouched.

Record queue count before and after.

If failed, do not launch another retry. Perform bounded self-diagnosis from the exact failed run/job/logs as required by the worker durability protocol, record the root cause classification and smallest next action, then stop.

## Boundaries
Allowed:
- exactly one canonical retry for the existing untouched 10-result submission;
- canonical ingest/state changes resulting from successful acceptance of those exact 10 results;
- durable report checkpoints.

Not allowed:
- semantic regeneration;
- editing the 10 results;
- processing new games;
- batch 2;
- direct queue/cache edits;
- unrelated code/config changes;
- Scheduled Task mutation;
- creating another Scheduled Task;
- paid/external services.

## Finish
Use one final status:
- `complete_existing_batch_accepted`
- `failed_closed_root_cause_recorded`
- `blocked_state_changed`
- `waiting_external`

If complete, explicitly state:
- 10 existing results accepted without regeneration;
- queue count before/after and exact decrease;
- receipt/batch id;
- no next batch started;
- ready to resume the throughput experiment from the next canonical queue item.

Then STOP.
