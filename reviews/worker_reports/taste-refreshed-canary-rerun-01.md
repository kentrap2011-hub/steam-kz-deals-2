# taste-refreshed-canary-rerun-01

## Status
`needs_followup`

## Task
Refresh the exact Chernobylite Complete Edition (`App_1016800`) canary binding against the current canonical Taste profile, use the same existing generation-2 `Taste Semantic Producer` Scheduled Task, run only that one canary, restore its permanent DAILY 01:00 Europe/Samara schedule, and verify canonical acceptance without weakening safety or widening production.

## Final outcome
The task is stopped fail-closed with `needs_followup` because the canonical pre-AI payload and the live Taste profile are no longer bound to the same profile blob. A new Chernobylite result cannot be safely accepted until the canonical pre-AI state is regenerated against the then-current live profile.

No replacement game was selected and no unsafe/manual binding substitution was performed.

## Durable lifecycle and prior actions
The report was created in `main` before any Scheduled Task mutation or active Taste inbox mutation and checkpointed during execution.

The previously stale generation-2 Chernobylite result was preserved exactly at:
`data/ai_archive/taste/generation-2/stale-profile/canary-app-1016800-gen2-profile-c42a6a5d.json`

That archived result is producer generation 2 and is bound to the obsolete profile SHA:
`c42a6a5dcf608e04bf86d24be9e1542f1b934456`.

Its former active copy:
`data/ai_inbox/taste/canary-app-1016800-gen2.json`
was removed from the active inbox and is currently absent there.

Archive commit: `6c7dede402af5f4c30ef4bf79201439f227fd21b`.
Active-copy removal commit: `bac200cc1d55cd0afe945a366562d0005c263fec`.

## Architecture and containment
- GitHub/GitHub Actions remains owner of queue scope, current-input construction, producer fencing, validation, persistence, receipt state and completeness.
- The existing Scheduled ChatGPT task remains only the constrained semantic producer.
- No new queue, quota, retry loop, scheduler, backlog manager, producer generation or recurring stage was introduced.
- No producer fence, binding guard or V5 validation was weakened.
- No manual profile SHA substitution was used to force acceptance.

## Same Scheduled Task
The only Scheduled Task touched is the existing task:
- title: `Taste Semantic Producer`
- task id: `6aa032f37e688191a5c9a1a83f91c5d9`
- producer id: `chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9`
- producer generation: `2`

Its canary prompt was previously refreshed to the then-current frozen Chernobylite tuple and is fail-closed: it must write nothing if any source/profile/fingerprint/context/eligibility/producer binding differs and it may not select a fallback game.

At final verification, the same task is enabled and its permanent schedule is restored to:

```text
DTSTART;TZID=Europe/Samara:20260910T010000
RRULE:FREQ=DAILY;BYHOUR=1;BYMINUTE=0;BYSECOND=0
```

Timing mode: `exact_schedule`.
Enabled: `true`.
Task id remains unchanged.

The task's recorded `last_run_time` is still `2026-09-08T17:57:42.661880+00:00`; therefore no new bounded Chernobylite execution occurred after the passed 01:00 window. The permanent schedule was nevertheless explicitly restored and re-verified rather than leaving the task disabled or on a temporary trigger.

No new Scheduled Task was created.

## Current canonical state after 01:00
The nightly commercial/pre-AI chain did refresh the current source snapshot. The current canonical pre-AI payload reports:
- `source_mailing_updated_at_utc`: `2026-09-08T20:46:16.637935+00:00`
- `canonical_profile_blob_sha`: `191b6d6c5dec2f9ef2976517f301528740f9bec2`
- `taste_model_version`: `taste-v3`

The atomic pre-AI refresh commit observed for that chain is:
`4662895180d40ac8c503dc94d816fb62425c1d97` (`Refresh atomic pre-AI payload and queues [skip ci]`).

However, the current live canonical Taste profile has subsequently advanced again to blob SHA:
`705e1f852d91a8a63d8686b37c51ace41c02f4ac`.

Therefore:

```text
prepared pre-AI profile binding = 191b6d6c5dec2f9ef2976517f301528740f9bec2
current live profile blob        = 705e1f852d91a8a63d8686b37c51ace41c02f4ac
```

These values are not equal. A result evaluated against the current live profile would not have the canonical pre-AI profile binding, while a result bound to the prepared payload would not use the current live profile. Either path would violate the exact binding requirement. The correct action is therefore to stop rather than bypass the guard.

## Chernobylite queue state
Chernobylite remains the exact selected row and still requires fresh full Taste work:
- title: `Chernobylite Complete Edition`
- `taste_subject_key`: `App_1016800`
- `appid`: `1016800`
- `taste_fingerprint`: `b8f101a75b7f50b2139e18349a0f31ea791fb4601b463f00a99d48834e5e4129`
- `candidate_context_sha256`: `2fb17ed4b0732e67bee6e9e05668c31fbeac2bd60c4858801a9282bbf319480e`
- `ai_required_reason`: `taste_cache_key_missing`
- required work: `evaluate_taste_fit`, `evaluate_normalized_taste_factors`, `resolve_grounded_negative_analysis`

No successor or alternate game was chosen.

## Canonical acceptance check
A new active result for Chernobylite is not present at:
`data/ai_inbox/taste/canary-app-1016800-gen2.json`.

Chernobylite remains in the canonical Taste queue, so its queue state did not advance to accepted/consumed.

The latest runtime receipt still records its last successful semantic execution/accepted progress at `2026-09-01T21:03:08+00:00`, with source snapshot `2026-09-01T20:47:04.563817+00:00`; it does not show a new Chernobylite acceptance from this rerun attempt.

Consequently this task cannot claim:
- a new generation-2 Chernobylite result;
- canonical ingest acceptance;
- receipt/cache advancement for this canary;
- removal of `App_1016800` from the Taste queue.

## Why execution stopped
The exact canary is still eligible, but the canonical input state is internally time-skewed because the live Taste profile advanced after the atomic pre-AI payload was prepared. Running the semantic producer against either side of that mismatch would defeat the binding protection that this task is explicitly required to preserve.

The bounded follow-up required before retrying this same canary is:
1. canonically regenerate the atomic pre-AI payload/queue against the then-current stable live Taste profile;
2. re-freeze the exact `App_1016800` tuple from that regenerated state;
3. update the same Scheduled Task id `6aa032f37e688191a5c9a1a83f91c5d9` to that exact tuple;
4. run only Chernobylite and verify normal producer-fence/binding/V5 ingest, receipt/cache advancement, active-inbox consumption and queue removal;
5. keep/restore the same permanent DAILY 01:00 Europe/Samara schedule.

This report does not authorize a fallback game, a new Scheduled Task, mass/backlog analysis, weakened checks or a System Audit.

## Containment verification
- New Scheduled Task created: **NO**.
- Existing Scheduled Task id changed: **NO**.
- Permanent DAILY 01:00 Europe/Samara schedule restored: **YES**.
- Existing task enabled at final verification: **YES**.
- Other game selected: **NO**.
- Mass/backlog semantic analysis started: **NO**.
- Paid OpenAI API/Copilot/external paid service used: **NO**.
- Producer fence/binding/V5 safety weakened: **NO**.
- System Audit started: **NO**.

## System Audit readiness
Not ready for System Audit from this task because the Chernobylite canary has not been canonically accepted under the current profile binding. The task terminates with `needs_followup` and does not start System Audit.
