# Publication Freshness Recurrence Postmortem 01

## Task
Cross-incident READ-ONLY / RECON / POSTMORTEM for giveaway, paid-list, and automatic ChatGPT/Taste freshness recurrence.

## Status
`complete_reliability_action_required`

## Scope
Determine bounded local causes, common systemic failure modes, per-domain end-to-end freshness invariants, exact cadence/grace windows for `current` / `delayed` / `stale`, a durable first-missed-day signal without paid API or per-domain producer schedulers, user-visible partial-freshness semantics, and exactly one bounded next IMPLEMENT task.

No prevention mechanism was implemented in this task.

## Findings

### 1. Bounded local cause per incident

#### Ordinary prices and discounts / paid-list publication
The deterministic commercial source continued advancing while the canonical user-visible paid-list publication stopped advancing. The bounded failure was therefore not Steam collection/filtering; it was the missing/stalled publication handoff to the current public visual artifact. The accepted recovery established a `commercial_only` canonical refresh path and an exact scoped visual freshness receipt. That receipt intentionally does not claim unrelated giveaway or Taste freshness.

#### Giveaways
Fresh giveaway source/runtime state could exist while the canonical/public giveaway handoff was stale or absent. The bounded failure was publication handoff/provenance rather than source absence. The accepted recovery established a `giveaway_only` canonical refresh path plus scoped freshness evidence. A current scoped success receipt is necessary to distinguish a valid result of zero active giveaways from a stale/missing handoff that happens to render as zero.

#### Automatic ChatGPT / Taste analysis
The historical incident remains bounded to the point before staging/commit: the preceding daily Taste cycle had succeeded and candidates existed, but the next expected 01:00 Europe/Samara cycle had no stage/final lifecycle evidence. That is consistent with the external ChatGPT Scheduled Task not dispatching/starting, while the repository cannot prove the private platform-side reason. A success-side tracker cannot detect this class of failure by itself because a task that never starts writes no new success/failure receipt.

Separately, the current scheduler state must not be inferred from that historical contract. The user has directly verified in the ChatGPT interface that there are currently no active Scheduled Tasks. Therefore the automatic Taste analysis is **not currently scheduled at 01:00**. In the freshness contract below, `01:00` is the intended/contractual Taste cycle time, not evidence that an active ChatGPT scheduler presently exists.

### 2. Common systemic failure modes

The three incidents are not one shared producer bug. They expose one missing cross-domain property: there is no single cycle-keyed statement of whether each independently owned daily publication actually completed for the expected local day.

Common failure modes are:

1. Source-generation success and public-publication success are different facts.
2. A canonical current pointer or scoped publication receipt can stop advancing while upstream truth continues to advance.
3. Success-only receipts cannot detect complete producer non-dispatch.
4. Raw file age has no knowledge of expected local cadence, normal execution time, or a legitimate in-progress window; using only `now - mtime` creates false positives and late detection.
5. An empty result is ambiguous unless the current expected cycle has a success receipt. This is especially important for giveaways: valid zero and stale/missing publication must not be conflated.
6. One aggregate freshness flag destroys partial-freshness information. A stale Taste cycle must not make fresh prices/giveaways appear stale, and vice versa.
7. Production ownership is deliberately split: GitHub owns the deterministic commercial/giveaway cycle, while the external ChatGPT controller is the intended owner of Taste when its Scheduled Task exists. Freshness monitoring must not create a second producer or fallback owner.

### 3. End-to-end freshness invariant per domain

All deadlines below are evaluated in `Europe/Samara` and against the **expected daily cycle**, not against the age of whichever file happens to be present.

The state names are:

- `current` = «Данные актуальны»;
- `delayed` = «Обновление задерживается»;
- `stale` = «Данные не обновляются».

Before the current day's normal completion deadline, the last successfully completed previous cycle remains `current` while the new cycle is legitimately not due yet. If the current-cycle success evidence arrives earlier, the state is immediately `current` for that new cycle. A late coherent success for the same expected cycle clears `delayed`/`stale` back to `current`.

| Domain | Expected / contractual start | Success evidence that must advance for the expected cycle | Normal completion deadline | Delayed window | Stale from |
|---|---:|---|---:|---:|---:|
| Ordinary prices and discounts | 00:10 GitHub Actions cron | Canonical paid-list/current publication plus exact `commercial_only` publication/freshness evidence for that local cycle | 01:30 | 01:30–02:30 | 02:30 |
| Giveaways | 00:10 GitHub Actions cron | Canonical giveaway publication plus exact `giveaway_only` publication/freshness evidence for that local cycle | 01:30 | 01:30–02:30 | 02:30 |
| ChatGPT / Taste analysis | 01:00 contractual target; currently no active ChatGPT Scheduled Task | Final lifecycle evidence for run key `taste-auto-YYYY-MM-DD` (`taste:auto-finalize`) and the corresponding finalized result/publication for that run | 02:00 | 02:00–03:00 | 03:00 |

#### Why the deterministic windows are now bounded this way

`.github/workflows/steam-test.yml` contains `cron: "10 20 * * *"`, which configures a nominal daily trigger at 00:10 Europe/Samara (20:10 UTC on the preceding UTC date). That YAML proves configuration only; it does not by itself prove execution.

The GitHub Actions run history does prove that recent scheduled executions actually occurred. The checked `event=schedule` runs for `Steam KZ production shortlist` were:

- run `34159138510`: started `2026-09-08 00:22:11` Europe/Samara, completed successfully;
- run `34057743377`: started `2026-09-07 00:21:38` Europe/Samara, completed successfully;
- run `33989834080`: started `2026-09-06 00:20:56` Europe/Samara, completed successfully;
- immediately preceding run `33915846239`: started `2026-09-05 00:21:50` Europe/Samara and did run, but completed with failure.

So recent real scheduled starts were roughly 11–12 minutes later than the nominal 00:10 cron time. Because the production job has `timeout-minutes: 60`, the previous 01:10 normal deadline was too strict: the timeout is relative to the actual job start, not the nominal cron minute.

A bounded corrected deterministic envelope is therefore:

- nominal cron: 00:10;
- reasonable scheduler-start allowance: through 00:30, covering the recent observed 00:21–00:22 starts with additional margin;
- hard job runtime envelope: up to 60 minutes after actual start;
- normal completion deadline: 01:30;
- additional delayed grace: 60 minutes;
- stale from: 02:30.

This avoids treating an ordinary GitHub scheduling delay as a publication delay while still making a missed deterministic cycle stale on the same local day.

For Taste, 01:00 remains the contractual target used to evaluate lifecycle evidence. A known historical successful cycle finalized close to 01:03, so 02:00 remains a deliberately generous completion deadline and 03:00 remains the stale cutoff. However, because the user has verified that no ChatGPT Scheduled Task is currently active, the present operational diagnosis is stronger than mere timing uncertainty: automatic Taste execution at 01:00 is currently **not scheduled**. A health observer must not pretend otherwise or attempt to start ChatGPT itself.

#### Per-domain criteria

**Ordinary prices and discounts**
- `current`: no newer cycle is due yet, or the expected local cycle has a coherent canonical paid publication and matching `commercial_only` success evidence.
- `delayed`: after 01:30, the expected local cycle has not produced matching commercial publication evidence, but the 60-minute delay grace has not expired.
- `stale`: from 02:30 until coherent success evidence for the expected local cycle appears.

**Giveaways**
- `current`: no newer cycle is due yet, or the expected local cycle has a coherent canonical giveaway publication and matching `giveaway_only` success evidence. A result of zero giveaways is valid only under this condition.
- `delayed`: after 01:30, current-cycle giveaway publication evidence is absent/incoherent, but the delay grace has not expired.
- `stale`: from 02:30 until coherent current-cycle giveaway publication evidence appears.

**ChatGPT / Taste**
- `current`: no newer cycle is due yet, or the expected run key has final lifecycle/result evidence.
- `delayed`: after 02:00, expected-run final evidence is absent, but the delay grace has not expired.
- `stale`: from 03:00 until the expected run is finalized coherently.
- Diagnostic refinement: stage evidence without final evidence means “started but not completed”; absence of both stage and final evidence means “no repository evidence that the run started”. The currently verified absence of any active ChatGPT Scheduled Task should be preserved as the stronger operational diagnostic `scheduler_not_configured` (or equivalent) rather than being misreported as an unexplained producer delay.

### 4. Corrected first-missed-day observer boundary

A checker placed only inside each producer is insufficient because complete non-dispatch is exactly the failure that must be detected.

The previous report contained a factual error here. `.github/workflows/build-mailing-feed.yml` does **not** have a `schedule:` trigger and does **not** run independently at 09:17 Europe/Samara. Its current triggers are `workflow_dispatch`, `workflow_run` after `Steam KZ production shortlist`, and selected `push` events. Therefore it cannot be used as an independent daily observer. In particular, if `Steam KZ production shortlist` never starts, its downstream `workflow_run` trigger cannot provide the missing independent observation.

The actual configured daily GitHub trigger is the `cron: "10 20 * * *"` entry in `.github/workflows/steam-test.yml`, nominally 00:10 Europe/Samara. The Actions history above proves recent `event=schedule` executions of that workflow. But that does **not** solve the monitoring problem:

1. the 00:10 producer cannot reliably detect its own complete non-dispatch, because when it never starts it executes no checker;
2. 00:10 is before the contractual ChatGPT/Taste start at 01:00 and therefore cannot evaluate whether that later cycle completed;
3. the previous supposed 09:17 independent observation point does not exist;
4. no **verified existing independent scheduled execution after the latest 03:00 stale cutoff** is available for this report to rely on.

The available GitHub Actions history is sufficient to verify the recent 00:10-class scheduled producer runs above. It is not evidence of an independent post-deadline health observer. Repository-wide code search for additional cron entries returned an incomplete result, so this postmortem does not make an unsupported exhaustive claim that no other YAML can possibly contain a schedule. The reliability conclusion is narrower and sufficient: **there is no verified existing independent post-deadline execution that can safely be treated as the observer.** Until such an execution is explicitly proven or implemented, the architecture must treat that observer as absent.

#### Narrowest safe future observer

The narrowest safe remedy is one independent **health-only** daily observer scheduled after the latest stale cutoff, for example at approximately `03:15 Europe/Samara` (23:15 UTC on the preceding UTC date). This timing is after commercial/giveaway stale at 02:30 and Taste stale at 03:00, while still recording a missed overnight cycle on the same local day.

That observer must be strictly read-only with respect to producer behavior. It may only:

1. determine the expected local cycle/run key for `commercial`, `giveaways`, and `taste`;
2. inspect the already-existing cycle-keyed success/publication/lifecycle evidence;
3. calculate the independent freshness state and diagnostic reason for each domain;
4. persist or expose only a health-status receipt/snapshot if durable health evidence is required.

It must **not**:

- collect Steam data;
- collect giveaway data;
- build or publish replacement commercial/giveaway/Taste payloads;
- invoke ChatGPT;
- create or repair a Taste run;
- rerun or retry any producer;
- become a fallback production owner;
- interpret a missing giveaway cycle as a valid zero;
- use a paid API merely to perform freshness checking.

A machine-readable health snapshot may still be named `site/publication_freshness.json` if the implementation chooses to reuse that proposed path, but its contract must be health-only: it records whether expected cycles occurred and must not become a replacement publication artifact.

At the proposed post-03:00 observation time, a missed producer cycle is detectable on the first missed local day even if that producer never started. The observer itself still cannot prove its own complete non-dispatch from inside the same scheduler; that is a separate meta-monitoring boundary and must not be disguised as producer recovery.

Because there is currently no active ChatGPT Scheduled Task, such an observer would correctly report the expected Taste lifecycle as missing/stale until a real Taste scheduler is separately restored. It must not restore or launch that scheduler itself.

### 5. User-visible partial-freshness semantics

Freshness and readability must be separate concerns. A missed refresh should not destroy the last known good data.

- If commercial data is delayed/stale, continue to show the last known good paid list, but expose that **prices/discounts are not updating** and show the last successful cycle/date.
- If giveaway data is delayed/stale, continue to retain the last known good giveaway payload where readable, but mark it delayed/stale. Do not present “0 active giveaways” unless a current-cycle success receipt proves that zero is the valid result.
- If Taste is delayed/stale, retain the last readable Taste/ChatGPT analysis but mark only the Taste domain delayed/stale. Commercial and giveaway freshness remain independent.
- A health/status surface should expose the three domain states independently. Overall status can become `degraded` when any domain is delayed/stale while service/process health remains otherwise healthy.
- If `/health` is the surface wired by the implementation, it should return this publication-freshness snapshot rather than collapse it to a single boolean. Public UI/status consumers should use the same snapshot so they cannot disagree about freshness.
- Staleness must never be converted into an empty dataset merely to make the UI look clean.

### 6. Exactly one next IMPLEMENT task

**Next task (not started): `WORKER_TASK_PUBLICATION_FRESHNESS_SENTINEL_IMPLEMENT_01`**

Corrected bounded implementation scope:

- implement one unified, independent, health-only publication-freshness observer for the three domains using the corrected cadence/deadline/evidence contract above;
- give that observer one independent daily execution after the latest stale cutoff (target approximately 03:15 Europe/Samara), because the previously assumed 09:17 `Build mailing feed` schedule does not exist;
- do not attach the observer only to the 00:10 producer, because that cannot detect the producer's own complete non-dispatch and runs before the Taste cycle;
- inspect only existing cycle-keyed success/publication/lifecycle evidence and emit only health state/diagnostics;
- if a durable snapshot is used, keep it health-only and atomic; do not overwrite or synthesize producer publications;
- expose independent per-domain freshness through the existing health/status surface while preserving last-known-good readable data;
- add tests for observed GitHub scheduler-start delay, `current`, `delayed`, `stale`, same-day missed-cycle detection, complete producer non-dispatch, valid-zero giveaway versus stale giveaway, late recovery, currently absent Taste scheduler diagnostics, and the rule that the observer never reruns producers;
- do not modify or invoke the ChatGPT Scheduled Task from the observer, do not add a GitHub Taste fallback/secondary producer, and do not use a paid API.

No other implementation task is proposed by this postmortem, and this implementation task has **not** been started.

## Changes

Changed only:

- `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`

No application code, workflow, scheduler, Scheduled Task, API mechanism, publication artifact, or recovery logic was changed.

## Validation

Validated against the previously named protocol/task/predecessor sources plus the current workflow definitions and GitHub Actions scheduled-run history needed for this correction.

Correction-specific consistency checks:

- `.github/workflows/build-mailing-feed.yml` has no `schedule:` trigger; the previous 09:17 daily-run claim was false and is removed;
- `.github/workflows/steam-test.yml` contains `cron: "10 20 * * *"`, configuring the GitHub Actions producer nominally for 00:10 Europe/Samara;
- the cron entry is treated as configuration, not execution proof;
- GitHub Actions history separately proves recent `event=schedule` producer runs at approximately 00:21–00:22 Europe/Samara, including three latest successful runs and the immediately preceding failed run;
- because real starts have recently lagged the cron minute by about 11–12 minutes, the deterministic normal deadline is corrected from 01:10 to 01:30 and stale cutoff from 02:10 to 02:30;
- 00:10 is GitHub Actions producer scheduling, not ChatGPT scheduling;
- 01:00 is the contractual Taste target, but the user has verified that there are currently no active ChatGPT Scheduled Tasks, so automatic Taste execution is presently not scheduled;
- no verified existing independent scheduled execution after the latest 03:00 stale cutoff is available to serve as the health observer;
- the corrected recommendation is one future independent health-only observer after all stale cutoffs, with no producer/recovery behavior;
- exactly one next implementation task remains named and it has not been started;
- final status remains `complete_reliability_action_required`.

## Rollback / changed paths

This correction changed only the report path above. Rollback is limited to reverting the report commit; there is no runtime behavior to roll back.
