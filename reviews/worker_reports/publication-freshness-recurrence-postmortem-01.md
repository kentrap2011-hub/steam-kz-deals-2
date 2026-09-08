# Publication Freshness Recurrence Postmortem 01

## Task
Cross-incident READ-ONLY / RECON / POSTMORTEM for giveaway, paid-list, and automatic ChatGPT/Taste freshness recurrence.

## Status
`complete_reliability_action_required`

## Scope
Determine bounded local causes, common systemic failure modes, per-domain end-to-end freshness invariants, exact cadence/grace windows for `current` / `delayed` / `stale`, a durable first-missed-day signal without paid API or per-domain schedulers, user-visible partial-freshness semantics, and exactly one bounded next IMPLEMENT task.

No prevention mechanism was implemented in this task.

## Findings

### 1. Bounded local cause per incident

#### Ordinary prices and discounts / paid-list publication
The deterministic commercial source continued advancing while the canonical user-visible paid-list publication stopped advancing. The bounded failure was therefore not Steam collection/filtering; it was the missing/stalled publication handoff to the current public visual artifact. The accepted recovery established a `commercial_only` canonical refresh path and an exact scoped visual freshness receipt. That receipt intentionally does not claim unrelated giveaway or Taste freshness.

#### Giveaways
Fresh giveaway source/runtime state could exist while the canonical/public giveaway handoff was stale or absent. The bounded failure was publication handoff/provenance rather than source absence. The accepted recovery established a `giveaway_only` canonical refresh path plus scoped freshness evidence. A current scoped success receipt is necessary to distinguish a valid result of zero active giveaways from a stale/missing handoff that happens to render as zero.

#### Automatic ChatGPT / Taste analysis
The preceding daily Taste cycle had succeeded, candidates existed for the next expected cycle, but the expected 01:00 Europe/Samara cycle had no stage/final lifecycle evidence. The bounded failure was before staging/commit, consistent with the external ChatGPT Scheduled Task not dispatching/starting. The repository cannot prove the private platform-side reason. A success-side tracker cannot detect this class of failure by itself because a task that never starts writes no new success/failure receipt.

### 2. Common systemic failure modes

The three incidents are not one shared producer bug. They expose one missing cross-domain property: there is no single cycle-keyed statement of whether each independently owned daily publication actually completed for the expected local day.

Common failure modes are:

1. Source-generation success and public-publication success are different facts.
2. A canonical current pointer or scoped publication receipt can stop advancing while upstream truth continues to advance.
3. Success-only receipts cannot detect complete producer non-dispatch.
4. Raw file age has no knowledge of expected local cadence, normal execution time, or a legitimate in-progress window; using only `now - mtime` creates false positives and late detection.
5. An empty result is ambiguous unless the current expected cycle has a success receipt. This is especially important for giveaways: valid zero and stale/missing publication must not be conflated.
6. One aggregate freshness flag destroys partial-freshness information. A stale Taste cycle must not make fresh prices/giveaways appear stale, and vice versa.
7. Production ownership is deliberately split: GitHub owns the deterministic commercial/giveaway cycle, while the external ChatGPT controller owns Taste. Freshness monitoring must not create a second producer or fallback owner.

### 3. End-to-end freshness invariant per domain

All deadlines below are evaluated in `Europe/Samara` and against the **expected daily cycle**, not against the age of whichever file happens to be present.

The state names are:

- `current` = «Данные актуальны»;
- `delayed` = «Обновление задерживается»;
- `stale` = «Данные не обновляются».

Before the current day's normal completion deadline, the last successfully completed previous cycle remains `current` while the new cycle is legitimately not due yet. If the current-cycle success evidence arrives earlier, the state is immediately `current` for that new cycle. A late coherent success for the same expected cycle clears `delayed`/`stale` back to `current`.

| Domain | Expected start | Success evidence that must advance for the expected cycle | Normal completion deadline | Delayed window | Stale from |
|---|---:|---|---:|---:|---:|
| Ordinary prices and discounts | 00:10 | Canonical paid-list/current publication plus exact `commercial_only` publication/freshness evidence for that local cycle | 01:10 | 01:10–02:10 | 02:10 |
| Giveaways | 00:10 | Canonical giveaway publication plus exact `giveaway_only` publication/freshness evidence for that local cycle | 01:10 | 01:10–02:10 | 02:10 |
| ChatGPT / Taste analysis | 01:00 | Final lifecycle evidence for run key `taste-auto-YYYY-MM-DD` (`taste:auto-finalize`) and the corresponding finalized result/publication for that run | 02:00 | 02:00–03:00 | 03:00 |

#### Why these windows are bounded this way

- The deterministic `Steam KZ production shortlist` schedule starts at 00:10 and has a hard 60-minute job timeout. Therefore 01:10 is the real maximum normal execution envelope already encoded by the current workflow, not an arbitrary file-age threshold.
- An additional 60-minute delay grace, through 02:10, distinguishes a late/retried-but-still-plausible publication from a genuinely missed deterministic daily publication.
- The Taste schedule is expected at 01:00. A known normal successful cycle finalized at approximately 01:03, so the usual work is short. Because the external Scheduled Task has no repository-enforced job timeout visible here, 60 minutes to 02:00 is a deliberately generous normal completion envelope; another 60 minutes to 03:00 is the delay grace before declaring the cycle missed.
- These thresholds are intentionally generous enough to avoid calling a normally running cycle stale, while still making the missed cycle machine-detectable on the same local day.

#### Per-domain criteria

**Ordinary prices and discounts**
- `current`: no newer cycle is due yet, or the expected local cycle has a coherent canonical paid publication and matching `commercial_only` success evidence.
- `delayed`: after 01:10, the expected local cycle has not produced matching commercial publication evidence, but the 60-minute delay grace has not expired.
- `stale`: from 02:10 until coherent success evidence for the expected local cycle appears.

**Giveaways**
- `current`: no newer cycle is due yet, or the expected local cycle has a coherent canonical giveaway publication and matching `giveaway_only` success evidence. A result of zero giveaways is valid only under this condition.
- `delayed`: after 01:10, current-cycle giveaway publication evidence is absent/incoherent, but the delay grace has not expired.
- `stale`: from 02:10 until coherent current-cycle giveaway publication evidence appears.

**ChatGPT / Taste**
- `current`: no newer cycle is due yet, or the expected run key has final lifecycle/result evidence.
- `delayed`: after 02:00, expected-run final evidence is absent, but the delay grace has not expired.
- `stale`: from 03:00 until the expected run is finalized coherently.
- Diagnostic refinement: stage evidence without final evidence means “started but not completed”; absence of both stage and final evidence means “no repository evidence that the run started”. Both still map to the same time-based freshness state above; the diagnostic reason should be preserved separately.

### 4. Durable first-missed-day signal without a new scheduler

A checker placed only inside each producer is insufficient because complete non-dispatch is exactly the failure that must be detected.

The repository already has an independent daily GitHub schedule: `.github/workflows/build-mailing-feed.yml` runs `Build mailing feed` at 09:17 Europe/Samara. This is after all three stale cutoffs (02:10, 02:10, and 03:00). Therefore the best bounded prevention design is to use that **existing** daily execution as a read-only observation point.

The future observer should:

1. evaluate the expected local cycle for each of the three domains;
2. inspect each domain's own cycle-keyed success evidence;
3. calculate `current` / `delayed` / `stale` independently;
4. persist one machine-readable snapshot, proposed as `site/publication_freshness.json`;
5. never rerun, retry, repair, or take ownership of a producer.

At the ordinary 09:17 run, a missed overnight publication is already past its stale threshold, so the repository itself records the failure **on the first missed local day** even when the affected producer never started. This adds no new cron, does not modify the ChatGPT Scheduled Task, does not require a paid API, and does not create fallback production ownership.

The proposed `site/publication_freshness.json` should contain at least:

- observation timestamp and local date;
- one independent record for `commercial`, `giveaways`, and `taste`;
- state (`current` / `delayed` / `stale`);
- expected cycle/run key;
- expected start, normal deadline, and stale cutoff;
- last successful cycle;
- success-evidence/provenance reference;
- diagnostic reason when evidence is missing/incoherent;
- aggregate health such as `ok` / `degraded`, derived without erasing per-domain state.

This proposed file is a next-task design, not an artifact created by this postmortem.

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

Bounded implementation scope:

- implement one unified, read-only publication-freshness evaluator for the three domains using the cadence/deadline/evidence contract above;
- invoke it from the already-existing 09:17 `Build mailing feed` schedule rather than adding a scheduler;
- persist `site/publication_freshness.json` atomically/durably;
- expose the independent per-domain state through the existing health/status/publication surface, preserving last-known-good readable data;
- add tests for `current`, `delayed`, `stale`, same-day missed-cycle detection, valid-zero giveaway versus stale giveaway, late recovery, and the rule that the sentinel never reruns producers;
- do not modify the ChatGPT Scheduled Task, do not add a GitHub Taste fallback/secondary scheduler, and do not use a paid API.

No other implementation task is proposed by this postmortem.

## Changes

Changed only:

- `reviews/worker_reports/publication-freshness-recurrence-postmortem-01.md`

No application code, workflow, scheduler, Scheduled Task, API mechanism, publication artifact, or recovery logic was changed.

## Validation

Validated against:

- `CHAT_PROTOCOL.md`;
- `CHAT_CONTEXT.md`;
- `DIRECTOR_PROTOCOL.md`;
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`;
- `WORKER_TASK_PUBLICATION_FRESHNESS_RECURRENCE_POSTMORTEM_01.md`;
- predecessor giveaway, paid-list, and Taste recon/implementation reports named by the task;
- `config/daily_execution_contract.json`;
- `config/execution_ownership_contract.json`;
- `PROJECT_ROUTES.md`;
- current workflow definitions including `.github/workflows/steam-test.yml`, `.github/workflows/build-daily-visual-payload.yml`, and `.github/workflows/build-mailing-feed.yml`.

Consistency checks:

- deterministic commercial/giveaway expected start is 00:10 Europe/Samara;
- deterministic production job timeout is 60 minutes;
- Taste expected start is 01:00 Europe/Samara and external ChatGPT remains sole owner;
- no GitHub Taste fallback is proposed;
- existing independent `Build mailing feed` run at 09:17 occurs after all chosen stale cutoffs and can therefore persist first-missed-day state without a new scheduler;
- exactly one next implementation task is named and it has not been started.

## Rollback / changed paths

This task changed only the report path above. Rollback is limited to reverting the report commits; there is no runtime behavior to roll back.
