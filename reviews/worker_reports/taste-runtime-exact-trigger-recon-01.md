# Taste runtime exact trigger recon 01

## Scope

Read-only operational recon for the existing semantic Taste runtime. This report does not repeat the Trine 4 missing-game diagnosis, does not make a manual Taste decision for Trine 4, and does not create or modify any scheduler/automation.

Target Taste subject: `App_690640` (`Trine 4: The Nightmare Prince`).

## Conclusions

### Existing automatic Taste check

The project already has an existing scheduled ChatGPT semantic Taste runtime. It is the semantic worker; GitHub owns queue preparation, validation/ingest, persistence/completeness, and downstream rebuild.

The recon did not produce a trustworthy captured live value for the automation's `enabled` flag, exact schedule/RRULE, or `next_run`. Therefore those fields must not be invented or inferred from documentation or from the mere presence of `App_690640` in the queue.

Accordingly, the safe operational conclusion is:

- presence of `App_690640` in the Taste queue proves that Trine 4 is waiting for semantic work;
- it does **not** by itself prove that a semantic invocation is currently running;
- no exact current `enabled`, schedule, or next-run timestamp was captured strongly enough in this recon to report as fact.

### Standard manual trigger

On the available automation execution surface used for this recon, there is no separate `Run now` operation. No existing repository/runtime bridge was confirmed that would safely invoke the semantic Taste worker immediately.

Therefore a standard immediate manual launch cannot be claimed as available from the current execution surface. No replacement automation, duplicate scheduler, or ad-hoc semantic path should be created to simulate one.

### How to know that Trine 4 itself has been processed

Completion must be checked per Taste key, not by the completion of a whole scheduled run and not merely by whether the game appears in the final visual list.

For Trine 4, the completion signal is that the current semantic result for canonical key `App_690640` has been accepted and persisted by the GitHub-owned ingest/completeness path, and that `App_690640` is no longer unresolved for the current Taste input/fingerprint.

A completed semantic check does **not** necessarily imply that Trine 4 must appear in the final list: a valid semantic verdict may legitimately exclude it. Appearance in the final list is a downstream result, not the proof that semantic processing itself finished.

### Downstream rebuild

After an accepted semantic result is persisted, downstream rebuild remains GitHub-owned. The visual producer path includes `scripts/build_visual_feed_v2.py` and consumes only resolved/acceptable Taste state according to the existing production contract.

The correct verification sequence is therefore:

1. confirm an accepted current semantic result exists for `App_690640`;
2. confirm `App_690640` is no longer unresolved in the Taste queue/completeness state;
3. confirm the GitHub-owned downstream rebuild has consumed that persisted state;
4. inspect the rebuilt final output, interpreting presence or absence according to the accepted semantic verdict rather than treating presence as the semantic-completion criterion.

## Refs

- Worker task: `WORKER_TASK_TASTE_RUNTIME_EXACT_TRIGGER_RECON_01.md`
- Taste subject: `App_690640`
- Ownership contract: `config/execution_ownership_contract.json`
- Taste queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- Visual producer: `scripts/build_visual_feed_v2.py`
- Report: `reviews/worker_reports/taste-runtime-exact-trigger-recon-01.md`

## Changes performed

Only this recon report was added. No Taste verdict, production rule, queue content, scheduler, automation, ranking rule, budget rule, or downstream production state was changed.
