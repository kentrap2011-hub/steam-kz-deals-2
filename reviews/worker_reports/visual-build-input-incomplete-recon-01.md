# Visual Build Input Incomplete Recon 01

## Final status

`needs_user_evidence`

## Scope and constraints

This was a read-only recon of the current ChatGPT/semantic production input and the visual-build readiness path. No production data, completeness thresholds, code, workflows, schedulers, queues, or unrelated product areas were changed. The only repository change made by this task is this report.

No broad Git history or GitHub Actions history search was used.

## Executive finding

The visual-build blocker is **mixed**, with one primary data-state blocker and one secondary visual-readiness control-flow defect:

1. **Primary / real publication blocker — same known semantic incompleteness.** The current canonical ChatGPT production manifest truthfully reports a complete family partition but **701 unresolved semantic rows**, so it is not sufficiently complete for publication and its top-level status is `degraded`.
2. **Secondary / separate production defect — unreachable degraded/queued branch in visual readiness.** `current_production_readiness()` rejects any ChatGPT payload whose top-level status is not `complete` before it reaches its later `ai_queue_count != 0` handling. Therefore the truthful `degraded` state raises `RuntimeError("ChatGPT production payload is not complete")` instead of reaching the builder's existing degraded/queued path.

The second issue explains the exact exception/control-flow behavior, but fixing or bypassing it would **not** make the current semantic data safe to publish as a normal fresh/complete visual build. The primary blocker remains the 701 unresolved semantic rows.

## Exact blocker

Current canonical input:

`data/production/pre_ai/chatgpt_payload.json`

Observed state:

- `status = "degraded"`
- `ai_queue_count = 701`
- `ready_without_ai_count = 0`
- `complete_family_partition = true`
- semantic unresolved count = `701`
- `sufficiently_complete_for_publication = false`
- source mailing timestamp is current-scope data from `2026-09-03T18:53:27.390807+00:00`

This is internally consistent rather than a malformed/corrupt payload. `scripts/semantic_runtime_completion.py` intentionally derives publication completeness from the semantic partition and unresolved count: unresolved semantic work greater than zero keeps publication sufficiency false and therefore keeps the manifest `degraded`.

The exact visual exception is then introduced in `scripts/build_daily_visual_payload.py` inside `current_production_readiness()`:

- it loads the canonical ChatGPT production payload;
- it checks `payload.get("status") != "complete"` and raises `RuntimeError("ChatGPT production payload is not complete")`;
- only later in the same readiness logic is there handling for a nonzero AI queue (`ai_queue_count != 0`) that can return a non-ready/degraded result instead of treating it as a normal complete source.

Because the current truthful semantic status is `degraded`, execution never reaches that later queued branch.

`scripts/build_final_visual_payload.py` already contains a deterministic refresh-existing-media path for the `source_key is None` / semantic-work-still-queued situation when the forced refresh mode is used, and propagates degraded semantic state rather than pretending it is complete. The early status gate above prevents the current truthful payload from reaching that path.

## Root-cause classification

`mixed`

### `same_known_semantic_incompleteness`

This is the **primary blocker for a normal fresh publishable build**. The semantic runtime/control-state work previously accepted in `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md` made the incomplete state explicit; it did not redefine the publication threshold. The current manifest therefore correctly says that the family partition is complete while semantic work remains unresolved.

The broader audit/release material is consistent with this: visual freshness cannot be closed as a normal fresh complete publication while the canonical semantic production input remains incomplete.

### `separate_production_defect`

There is also a **secondary visual-readiness control-flow mismatch**: the coarse top-level `status == complete` check occurs before the more specific queued/degraded handling, making the latter unreachable for a truthful semantic `degraded` manifest.

This is a real defect in degraded-path reachability, but it is **not the smallest safe thing to repair first for the user's stated goal**. Removing/reordering that check now would only permit a degraded refresh path; it would not satisfy the semantic publication contract or produce a normal fresh complete visual build.

## Producer that owns making the condition complete

The owner of resolving the 701 semantic rows is the **existing scheduled ChatGPT semantic production runtime for the current canonical scope**.

The GitHub-side semantic completion helper is not the producer of semantic verdicts; it derives/persists truthful canonical completeness state from the queue/results. The visual builder is also not the owner of semantic completion and must not manufacture readiness.

`config/execution_ownership_contract.json` is consistent with this division: deterministic repository/control-plane logic owns canonical state/completeness derivation, while the ChatGPT semantic runtime owns completing the semantic work needed for the unresolved scope.

## Current producer state

`cannot_determine`

Repository evidence shows accepted semantic progress for an older scope, while the current canonical production scope is newer and still contains 701 unresolved rows. The inspected repository state does **not** prove whether the existing scheduled ChatGPT task is currently enabled, has a valid next run, or has successfully accepted a batch for this current scope.

There is therefore insufficient evidence to classify the producer as `working_but_incomplete`, `stalled`, or `failing`. Calling it stalled/failing from queue age alone would be an unsupported inference.

## Is the current payload safe to publish?

**No, not as a normal fresh/complete production payload.**

Under the current contract, the normal publication path must remain fail-closed until semantic completeness reaches the accepted threshold. In the current state:

- `sufficiently_complete_for_publication = false`;
- unresolved semantic work is nonzero;
- top-level semantic state is truthfully `degraded`.

A deterministic degraded refresh path may preserve truthful degraded state, but it must not be treated as proof of a normal fresh complete visual publication or as closure of visual freshness/deploy acceptance. No completeness check should be weakened to turn the current 701-row unresolved scope into a nominally complete build.

## One minimal next action

**Verify the existing scheduled ChatGPT semantic production task against the current 701-row scope and, if it is not active/healthy, restore that same existing task; the recovery acceptance signal is one new accepted current-scope semantic batch/receipt.**

Do not manually process the queue, create a new scheduler/process, or change completeness thresholds.

Why this is the smallest safe next step:

- it addresses the actual owner of the primary blocker;
- it distinguishes a merely incomplete working producer from a stopped/broken producer without speculative code changes;
- it preserves the existing semantic publication contract;
- once current-scope progress is re-established, the existing producer can continue draining unresolved work naturally.

The secondary visual-readiness ordering defect should not be used as a shortcut around semantic completeness. It can be handled separately only if degraded-refresh behavior itself later needs repair.

## Can visual freshness/deploy then be re-verified?

**Yes, but only after the current semantic scope is fully resolved.**

A single accepted current-scope batch is the recovery proof for the producer, not the publication-completeness proof. After the existing producer drains the current unresolved semantic count to zero and the canonical manifest naturally becomes publication-sufficient / `complete`, rerun the existing canonical visual build and then re-verify visual freshness/deploy using the normal workflow.

Until that happens, normal fresh visual publication remains correctly blocked.

## Evidence inspected

The recon was bounded to the task and directly relevant canonical/control files, including:

- `WORKER_TASK_VISUAL_BUILD_INPUT_INCOMPLETE_RECON_01.md`
- `data/production/pre_ai/chatgpt_payload.json`
- `scripts/semantic_runtime_completion.py`
- `scripts/build_daily_visual_payload.py`
- `scripts/build_final_visual_payload.py`
- `.github/workflows/build-daily-visual-payload.yml`
- `reviews/worker_reports/semantic-runtime-completion-acceptance-02.md`
- `reviews/worker_reports/visual-freshness-release-01.md`
- `reviews/system_audits/system-audit-02.md`
- `DIRECTOR_TASK_BOARD.md`
- `config/execution_ownership_contract.json`

No code or production input was modified.