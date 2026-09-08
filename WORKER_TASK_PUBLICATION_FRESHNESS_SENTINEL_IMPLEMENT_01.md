# WORKER TASK — PUBLICATION FRESHNESS SENTINEL IMPLEMENT 01

## Mode
IMPLEMENT / ACCEPTANCE

## Priority
VERY_HIGH_RELIABILITY

## Preconditions
Read first:
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`

The corrected postmortem is the authoritative predecessor for this task.

## Goal
Implement exactly one independent, health-only daily observer that tells us whether the expected overnight publication cycles actually completed for:
1. ordinary prices/discounts;
2. giveaways;
3. ChatGPT/Taste.

The observer must detect a missed cycle even when the producer never started, while never becoming a producer or recovery path itself.

## Accepted timing contract — Europe/Samara
### Commercial / paid
- nominal GitHub producer cron: 00:10;
- normal completion through 01:30;
- delayed: 01:30–02:30;
- stale from 02:30.

### Giveaways
- nominal GitHub producer cron: 00:10;
- normal completion through 01:30;
- delayed: 01:30–02:30;
- stale from 02:30.

### ChatGPT / Taste
- contractual target: 01:00;
- normal completion through 02:00;
- delayed: 02:00–03:00;
- stale from 03:00.

Current operational fact: there is no active recurring ChatGPT Scheduled Taste task. The observer must therefore surface an explicit diagnostic such as `scheduler_not_configured` rather than pretending an active 01:00 scheduler exists.

## Required implementation
1. Add one independent daily health-only execution after the latest stale cutoff, target approximately 03:15 Europe/Samara.
2. It must not be attached only to the 00:10 producer because that producer cannot detect its own complete non-dispatch and runs before Taste.
3. The observer may inspect only already-existing cycle-keyed success/publication/lifecycle evidence.
4. Compute independent per-domain state: `current`, `delayed`, or `stale`, plus a bounded diagnostic reason.
5. Persist one machine-readable health snapshot, preferably `site/publication_freshness.json` unless an existing canonical health artifact is clearly safer.
6. Expose the same per-domain truth through the existing health/status surface and, where already architecturally appropriate, the public UI. Do not create competing truth sources.
7. Preserve last-known-good readable data. Stale health must not erase or synthesize publication data.
8. A current giveaway result of zero is valid only when current-cycle success evidence proves it; missing evidence must not be rendered as a valid zero.
9. Late coherent success for the same expected cycle must clear delayed/stale back to current.
10. Keep commercial, giveaway, and Taste freshness independent; one stale domain must not falsely mark the others stale.

## Hard boundaries
- Do NOT collect Steam data.
- Do NOT collect giveaway data.
- Do NOT rebuild or publish replacement commercial/giveaway/Taste payloads.
- Do NOT invoke ChatGPT.
- Do NOT create, enable, disable, delete, clone, or modify any ChatGPT Scheduled Task.
- Do NOT create a GitHub Taste fallback or second Taste producer.
- Do NOT rerun/retry/repair any producer.
- Do NOT use OpenAI API, Copilot, or any separately paid API/service.
- Do NOT change producer ownership.
- Do NOT use raw file age as the sole freshness criterion.
- Do NOT collapse all domains into one boolean freshness flag.
- Do NOT touch unrelated backlog.

## Required tests / acceptance
Cover at minimum:
- real-world GitHub scheduler start delay relative to nominal 00:10;
- `current`, `delayed`, `stale` boundaries;
- same-day missed-cycle detection;
- complete producer non-dispatch;
- commercial evidence mismatch/missing evidence;
- giveaway valid-zero vs stale/missing cycle;
- late coherent recovery;
- Taste stage-without-final vs no-stage/no-final;
- current `scheduler_not_configured` Taste diagnostic;
- independence of three domain states;
- explicit proof that observer never invokes or reruns producers;
- snapshot/status consumers agree on the same health truth.

If the existing architecture cannot expose public/UI freshness without unsafe broader changes, keep the implementation bounded to the canonical health snapshot/status surface and report the UI follow-up explicitly rather than widening scope.

## Durability / report
Before expensive work, create exact report:
`reviews/worker_reports/publication-freshness-sentinel-implement-01.md`
with status `in_progress` and persist it to `main`.

Update the same report at major milestones and before long final verification.

Before final response, persist final report to `main` and re-read it from `main`.

## Final status — exactly one
- `complete_ready_for_system_audit`
- `needs_followup_fix`
- `blocked`

## After completion
This is a material runtime/health change. Do not widen or start another implementation. Director must schedule an independent System Audit before calling the reliability change accepted.
