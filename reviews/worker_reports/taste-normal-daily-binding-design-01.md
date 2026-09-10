# TASTE Normal Daily Binding — Design Report

- task_id: `taste-normal-daily-binding-design-01`
- lifecycle: `completed`
- current_utc: `2026-09-10T07:44:49Z`
- decision: `recommend_max_10_prepared_taste_items_per_invocation`
- next_action: create a separate implementation task that codifies this binding in the canonical producer/contracts and the existing Scheduled Task, then verifies it with a bounded canary; do not implement from this design task

## Scope guard

Design only. This task did not change the Scheduled Task, producer code, configuration, queue, cache, production state, or production data, and it did not run semantic TASTE, ingest, downstream processing, or any operational workflow. The only repository mutation performed by this task is this worker report.

## Current state

The active architecture already has the required ownership and fail-closed foundations:

- one active ChatGPT Scheduled Task producer with execution identity `steam_kz_taste_producer_main`;
- deterministic producer ownership of source loading, classification, candidate selection, exact TASTE queue construction, validation, authoritative ingest, and downstream gating;
- semantic TASTE may consume only the exact producer-prepared GitHub queue and may not choose candidates, reorder them, inject/drop items, write production state, or run downstream work;
- GitHub is the authoritative operational state; no local/external fallback cache is allowed;
- single active execution, one semantic batch at a time, one ingest writer, durable GitHub lock/checkpoint state, current-live-profile pinning, bounded retry, strict validation, and fail-closed recovery are already canonical;
- daily deterministic completeness means the full eligible source set is loaded/classified. A fixed small semantic invocation cap must not be reinterpreted as the daily source/business scope.

The current checkpoint model is `incremental_by_chosen_feed_chunk`, but the canonical policy explicitly says that a committed chosen-feed chunk is a checkpoint unit, **not** a business quota and **not** daily completion. Current feed/shortlist storage chunk sizes therefore do not define a safe semantic invocation size.

## Blocking evidence

`reviews/worker_reports/taste-normal-daily-operation-enable-01.md` is correctly on HOLD because there is no canonical exact bounded amount of prepared semantic TASTE work that one Scheduled Task invocation may attempt.

The necessary contracts confirm the missing boundary:

- `config/execution_ownership_contract.json` fixes producer ownership, one active execution, one semantic batch at a time, GitHub-only state, and same-identity recovery, but does not give a numeric semantic item cap per Scheduled Task invocation.
- `config/daily_execution_contract.json` requires complete deterministic daily source loading/classification and explicitly rejects `first N` or a small fixed candidate quota as the meaning of daily scope.
- `config/mailing_policy.json` defines `chosen_feed_chunk` checkpointing and explicitly prevents treating that checkpoint unit as a business/daily quota.
- `config/taste_checkpoint_contract.json` defines immutable run/profile/input pinning, strict durable checkpoint commit, deterministic resume, one semantic batch at a time, and GitHub-only recovery, but does not define a numeric semantic item cap per Scheduled Task invocation.
- `config/taste_result_contract.json` and `config/taste_validation_contract.json` already bound retry to two attempts for the same checkpoint/work and require exact one-result-per-input, no missing/extra/duplicate/reordered output, and fail-closed termination on exhausted retry or mismatch.
- `reviews/worker_reports/taste-active-producer-restore-design-01.md` confirms the one-task/one-identity producer binding and that semantic TASTE must not decide the queue.

The current GitHub runtime payload shows a latest confirmed automatic queue delta of 11 items (`37 -> 26`). This is useful only as observed evidence that a small bounded semantic unit around this size has completed; it is **not** a canonical limit and must not itself become policy.

No inspected canonical contract contains an existing `max semantic items per invocation` value. Existing data chunk sizes (`50` for the producer shortlist and `150` for the feed) are deterministic storage/processing chunk sizes and provide no safety basis for allowing 50 or 150 semantic TASTE evaluations in one Scheduled Task invocation.

## Preserve

This design must preserve all of the following unchanged:

- full deterministic daily source loading and classification before semantic work;
- deterministic producer ownership of candidate selection and queue order;
- semantic TASTE truth and all semantic evaluation rules;
- exact GitHub-prepared queue identity; ChatGPT never chooses candidates;
- GitHub-only operational state and recovery;
- current-live-profile load/pin/freeze and digest/fingerprint checks;
- the existing maximum of two attempts for the same semantic work unit;
- strict validation, atomic authoritative ingest, exact post-ingest verification, and fail-closed behavior;
- one active task, one execution identity, one lock, one semantic batch at a time, one ingest writer;
- current daily cadence;
- the rule that a semantic safety cap is not a business quota and is not the definition of daily completeness.

## Recommended bounded work-unit

**Canonical recommendation: `MAX_TASTE_ITEMS_PER_INVOCATION = 10` and `MAX_TASTE_WORK_UNITS_PER_INVOCATION = 1`.**

A normal Scheduled Task invocation may semantically evaluate at most **10 prepared GitHub-hosted TASTE items**.

The bounded work-unit is the producer-owned deterministic contiguous head window of the first `min(10, remaining_prepared_queue_count)` **uncommitted** items from the canonical ordered GitHub TASTE queue for the pinned producer state. The producer, not ChatGPT, determines this exact window and pins its ordered item identities/hash together with the existing repository revision, current profile SHA, prompt/config/context/input digests, and other canonical invariants before the semantic call.

Rules by remaining count:

- `0`: valid no-op; no semantic TASTE call;
- `1..9`: process exactly all remaining uncommitted items;
- `>=10`: process exactly the first 10 uncommitted items and no others.

This cap is an **execution-safety boundary only**. It does not redefine TASTE truth, source eligibility, candidate selection, the daily source scope, or business completeness. Full deterministic source loading/classification still follows the existing daily contract even when semantic backlog requires multiple Scheduled Task invocations to drain.

Why 10: there is no existing canonical numeric semantic cap to reuse, and the available storage/checkpoint chunk sizes are explicitly unsuitable as a semantic quota. The only observed current automatic progress evidence is an 11-item queue reduction. A cap of 10 is a conservative round value below that observed completed amount, leaves headroom rather than adopting 11 as a policy, and is small enough to prevent a whole-backlog attempt. It is a design safety limit, not a claim that 10 is a formally benchmarked throughput maximum.

## Exact stop condition

A Scheduled Task invocation must never begin a second semantic work-unit after selecting its one exact `<=10`-item work-unit.

For a successful work-unit, the producer may finish only the already-canonical close-out sequence for that exact work-unit:

1. receive exactly one valid semantic result per exact input item;
2. pass strict identity/profile/context/count/order/result validation;
3. perform atomic authoritative ingest for that exact work-unit;
4. pass exact post-ingest verification;
5. commit the durable GitHub checkpoint/receipt for exactly those accepted item identities.

**Immediately after the durable commit of that exact work-unit, the semantic-work budget for the invocation is exhausted. No item 11 and no second semantic work-unit may start in the same Scheduled Task invocation.** Success-dependent close-out/downstream behavior already required by the canonical contracts may run only to the extent it belongs to the committed work-unit; it must not be used to open another TASTE work-unit.

If the invocation reaches the 10-item cap while more prepared items exist, that is a normal bounded stop, not an error and not daily/business completion.

## Backlog persistence and next invocation

The untouched suffix of the canonical prepared queue remains GitHub-authoritative, ordered, and semantically unevaluated. Hitting the cap must not drop, reorder, mark complete, synthetically reject, or otherwise mutate any suffix item merely because it was not processed in this invocation.

A successful commit advances durable progress only across the exact accepted prefix/work-unit. The next invocation, under the same task identity and GitHub lock/recovery rules, resumes from the first still-uncommitted canonical item and forms the next contiguous head window of at most 10 items.

No second queue, local cache, external cursor, or ChatGPT-maintained backlog is introduced. Durable GitHub queue identity plus durable committed work-unit/checkpoint position is the authority for what remains.

Because the existing `chosen_feed_chunk` can be larger than 10 items, future implementation must distinguish **source/checkpoint provenance** from the new **semantic invocation work-unit**. A source chunk may therefore span multiple Scheduled Task invocations. Committing one `<=10` semantic work-unit must never falsely mark the entire larger source chunk complete. The durable state must identify the exact ordered item IDs/hash of each accepted semantic work-unit so the remaining suffix of that source chunk is resumed without duplicate, skip, reorder, or reassessment.

Fresh daily producer inputs must continue to obey existing deterministic identity/digest rules. The implementation task must reconcile newly prepared GitHub input with durable already-committed work without weakening identity checks; this design does not authorize append/merge heuristics or candidate selection by ChatGPT.

## Producer ownership

The deterministic producer owns every boundary decision:

- determine the first uncommitted canonical queue position;
- take the exact contiguous `<=10` head window;
- pin ordered identities/hash and existing run/profile/context invariants in GitHub state;
- invoke semantic TASTE only on that exact window;
- validate, ingest, verify, and durably commit only that exact window;
- stop semantic work for the invocation after that work-unit.

Semantic ChatGPT is not allowed to choose the 10 items, skip difficult items, reorder items, fill unused capacity from elsewhere, continue into the suffix, or adaptively expand the limit.

## Fail-closed behavior

The existing bounded retry remains unchanged: at most two attempts for the **same exact work-unit** under the same pinned profile/context/input identity.

On profile/revision/input/digest mismatch, malformed output, missing/extra/duplicate/reordered result, exhausted second attempt, ingest failure, or post-ingest mismatch:

- fail closed;
- do not commit or advance the failed work-unit;
- do not dequeue or alter its untouched queue identity;
- do not start another semantic work-unit in the same invocation;
- do not run success-dependent downstream behavior for the failed work-unit;
- leave the exact work resumable through GitHub durable state under the same producer identity, subject to existing canonical invalidation/recovery rules.

There is no adaptive fallback that increases the cap above 10, creates a second producer, or moves state outside GitHub.

## Future files/actions affected — do not modify in this task

A separate implementation task should bind this design into the existing architecture. Expected touch points are:

- the existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` prompt/binding: enforce max 10 items, exactly one semantic work-unit per invocation, and the stop rule;
- `config/execution_ownership_contract.json`: canonical producer ownership of the bounded semantic work-unit and per-invocation cap;
- `config/taste_checkpoint_contract.json`: exact semantic work-unit identity, partial larger-chunk progress, prefix-only commit, and deterministic suffix resume;
- `config/mailing_policy.json`: explicit separation between source/chosen-feed chunk sizes and the semantic invocation safety cap;
- `config/taste_result_contract.json` and `config/taste_validation_contract.json`: reference the exact bounded work-unit count/identity where needed while preserving current strict validation and two-attempt retry semantics;
- the active deterministic producer entrypoint that materializes the canonical pre-AI/TASTE queue/payload: enforce producer-side slicing/pinning and stop-after-one-work-unit behavior;
- `config/daily_execution_contract.json` only if a cross-reference is needed to make explicit that the new cap does not weaken complete daily deterministic source loading/classification; its business/source-scope meaning must not change.

No file in this section is modified by this design task.

## Risks

1. **Throughput/backlog growth.** A 10-item daily semantic cap can drain an existing backlog slowly and may fall behind if more than 10 new semantic items are continuously prepared per cadence. That is an operational capacity issue, not grounds for silently expanding this safety cap. Any throughput change requires a separate measured design/implementation decision.
2. **False whole-chunk completion.** Existing chosen-feed/source chunks can exceed 10. Without exact semantic sub-unit identity, accepting 10 items could incorrectly advance an entire larger chunk. Implementation must commit exact ordered item IDs/hash only.
3. **Quota confusion.** Treating 10 as `first N` daily eligibility or daily completion would violate the daily execution contract. The full deterministic source set still has to be loaded/classified; 10 limits only semantic work attempted by one invocation.
4. **Queue regeneration/reconciliation.** Fresh daily prepared input must not cause already-committed work to be repeated or untouched backlog to be skipped. Existing identity/digest/fail-closed rules must remain authoritative when implementation defines resume across invocations.
5. **Evidence strength.** Ten is deliberately conservative and below the observed 11-item successful progress, but it is not a formally benchmarked timeout ceiling. The implementation/canary task should verify the bound without auto-tuning it during production execution.

## Decision

**APPROVE FOR IMPLEMENTATION AS A SEPARATE TASK:** one Scheduled Task invocation may process **at most 10 exact producer-prepared GitHub TASTE items**, in **one and only one semantic work-unit**. Stop semantic work after that exact work-unit is either durably accepted or fails closed. Preserve every uncommitted suffix item in GitHub-authoritative state for the next invocation, with deterministic producer-owned prefix selection and exact work-unit identity.

This is the single recommended design. No alternative quota or chunk-size option is proposed.

## Next action

Create a separate implementation task that:

1. codifies `MAX_TASTE_ITEMS_PER_INVOCATION = 10` and `MAX_TASTE_WORK_UNITS_PER_INVOCATION = 1` in the canonical producer/contracts;
2. adds exact semantic work-unit identity/progress so a larger chosen-feed chunk can resume across invocations without duplicate/skip/false whole-chunk commit;
3. updates the existing Scheduled Task binding without creating a second producer or changing cadence;
4. verifies with a bounded canary that one invocation never starts item 11 or a second semantic work-unit and that untouched suffix work remains durably resumable in GitHub;
5. preserves all current profile pinning, strict verification, two-attempt retry, atomic ingest, fail-closed, lock, ownership, and GitHub-only state rules.

STOP after this report. No implementation is authorized by `taste-normal-daily-binding-design-01`.