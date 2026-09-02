# Semantic Runtime Completion Acceptance 01

Task ID: `semantic-runtime-completion-acceptance-01`
Status: `needs_fix`

## Required result

1. `Semantic runtime observability`: `fail`

   Current concrete evidence:
   - The existing semantic queue contains **644 of 743 families** still requiring semantic work.
   - Queue presence is not a trustworthy runtime heartbeat and does not prove that the existing scheduled Taste worker is active, progressing, or successfully applying semantic results.
   - The acceptance evidence does not provide a durable last-success/progress signal sufficient to establish operational observability of the existing scheduled semantic runtime.

2. `Feed semantic completeness visibility`: `fail`

   Current concrete evidence:
   - `data/production/pre_ai/chatgpt_payload.json` reports `status="complete"` and `complete_family_partition=true` while **644 of 743 families** remain in the semantic queue.
   - Therefore the current `complete` signal demonstrates completion of family partition/accounting, not that the user-visible recommendation result is sufficiently semantically complete/current.
   - The accepted evidence does not establish an explicit user-visible degraded/incomplete semantic state or a trustworthy unresolved-age/staleness signal that prevents a materially incomplete feed from looking fully healthy.

3. Smallest missing mechanisms:
   1. A durable heartbeat/progress proof for the **existing canonical Taste scheduled runtime** that exposes an equivalent of active/enabled state, expected cadence/next-run expectation, and last successful semantic execution/progress. Queue existence alone must not satisfy this mechanism.
   2. An explicit canonical semantic completeness state in publication that distinguishes `scope partitioning completed` from `user-visible recommendation result sufficiently complete/current`, including unresolved semantic count and unresolved age/staleness where available.

4. Defect requires an `IMPLEMENT` task: `yes`

5. Bounded implementation contract:
   - Runtime ownership boundary: preserve the single existing Taste scheduler/runtime and queue defined by `config/execution_ownership_contract.json`; do not create a second scheduler, manual Taste path, or duplicate queue. Add only durable observability/heartbeat evidence for that existing owner.
   - Publication boundary: limit feed-completeness implementation to `scripts/build_visual_feed_v2.py` and its canonical generated payload `data/production/pre_ai/chatgpt_payload.json`; do not change Taste policy, weights, scores, exclusion semantics, or fail-closed safety. The published state must explicitly distinguish partition completion from semantic-result completeness/currentness and expose unresolved semantic count plus age/staleness where available.

6. Recommended next step:

   Create one bounded `IMPLEMENT` task covering exactly the two mechanisms above: durable observability for the existing canonical Taste runtime and truthful degraded/incomplete semantic publication state.

## Exact refs used

- `WORKER_TASK_SEMANTIC_RUNTIME_COMPLETION_ACCEPTANCE_01.md`
- `reviews/system_audits/baseline-01.md`
- `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`
- `reviews/worker_reports/trine4-missing-diagnosis-01.md`
- `data/production/pre_ai/chatgpt_payload.json`
- `config/execution_ownership_contract.json`
- `scripts/build_visual_feed_v2.py`
- `reviews/worker_reports/semantic-runtime-completion-acceptance-01.md`
