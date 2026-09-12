# Taste Steam Review Dossier Preparer 01 — durable report

- Task: `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_PREPARER_01.md`
- Mode: `IMPLEMENT_AND_VALIDATE`
- Date: 2026-09-12
- Final status: `complete_ready_for_separate_scheduler_and_clean_throughput_measurement`

## Result

Implemented a separate pre-Taste Steam review dossier mechanism without creating a Scheduled Task and without changing the existing Taste Semantic Producer. GitHub remains the control plane: it owns the exact pinned game scope, freshness decision, work manifest, validation, compact persistence and fail-closed downstream handoff. A future separately authorized ChatGPT preparer is constrained to evidence collection/synthesis for the exact GitHub-prepared scope.

The downstream handoff is deliberately separate from the existing active producer: `build_taste_semantic_dossier_input.py` joins the unchanged canonical Taste pin with fresh dossier objects and refuses to produce Taste semantic input when any dossier is missing, stale or invalid. This task therefore prepares the mechanism for a separate scheduler and later clean throughput measurement without silently changing the current scheduler.

## Files changed

Created:

- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier.py`
- `scripts/build_taste_steam_review_dossier_work.py`
- `scripts/ingest_taste_steam_review_dossiers.py`
- `scripts/build_taste_semantic_dossier_input.py`
- `scripts/test_taste_steam_review_dossier.py`
- `reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`

Updated only for task bookkeeping:

- `CURRENT_TASK.md`

Explicitly unchanged:

- existing Taste Semantic Producer Scheduled Task;
- `scripts/taste_pinned_work_unit.py`;
- current `data/production/pre_ai/taste_active_work_unit.json`;
- canonical Taste result ingest path/contracts;
- old Taste throughput measurement state.

## Canonical ownership and integration

Architecture preflight result:

1. GitHub owns exact scope, TTL/freshness, work preparation, submission validation, persistence and downstream gating.
2. The new canonical dossier contract explicitly defines the preparer boundary before implementation source was added.
3. No control-plane responsibility was transferred to ChatGPT or the interactive chat.
4. No recurring stage, retry manager, backlog manager, queue owner or scheduler was created by this task.

Current path:

`canonical Taste active pin -> Steam dossier work manifest -> future bounded semantic preparer -> validated compact dossier store -> fail-closed Taste semantic dossier input`

The semantic input keeps the canonical pin binding (`ordered_work_unit_sha256`, producer identity/generation, profile identity and Taste bindings) and preserves row order/key/appid/taste fingerprint/candidate-context/work-required fields. Dossier storage is keyed by Steam `appid`, so an `App_`/`Sub_` Taste subject can reuse the same Steam game dossier without changing pin authority.

## Dossier schema / persisted information

Each `TASTE-STEAM-REVIEW-DOSSIER-V1` contains at minimum:

- `appid` and canonical Steam title;
- `generated_at_utc`, `expires_at_utc`, `ttl_days`;
- compact neutral game/how-it-plays summary;
- structured observations with category, neutral statement, sentiment, recurrence strength, independent mention count and evidence-language lane;
- material review conflicts;
- actual reviewed counts for Russian and non-Russian lanes;
- adaptive-sampling metadata and stop reasons;
- Steam store/review provenance, capture metadata and compact hashes/fingerprints.

The validator rejects raw-review archive fields, long raw-like payloads, personal fit conclusions, include/exclude decisions and commercial fields such as price/discount/purchase urgency.

## Review acquisition and sampling strategy

The future semantic preparer prompt uses only Steam store material and Steam user reviews.

Adaptive policy:

- two lanes: `russian` and `non_russian`;
- initial target: up to 20 useful reviews per lane;
- continue in batches of up to 20 while a batch materially changes recurring themes, conflicts or support strength;
- a lane is stable after two consecutive batches add no material recurring theme/conflict change;
- stop earlier if the source is exhausted/sparse;
- hard ceilings: 80 Russian, 80 non-Russian, 160 total reviews per game;
- recurrence guidance: strong >=5 independent mentions, moderate 3–4, limited 2, anecdotal exactly 1.

The persisted dossier records the actual counts/batches/stop reason. The mechanism does not reduce evidence to Steam sentiment percentages.

## Russian-review handling

The Russian lane is mandatory to attempt even when sparse. It can create neutral observations in dedicated categories:

- localization;
- translation;
- voice;
- font;
- encoding;
- regional issues.

Regression coverage proves that a recurring Russian-review localization complaint is accepted as a neutral negative observation with `evidence_languages=["russian"]`, without turning it into a Dmitry-specific negative.

## TTL / freshness / reuse

Canonical default TTL: **20 days**.

Configurable bounds: 1–60 days.

Rules:

- fresh dossier is reused and no dossier work is emitted for that game;
- stale/invalid dossier is marked `refresh_required`;
- missing dossier is marked `missing_dossier`;
- persisted refresh replaces the current compact dossier instead of appending unbounded raw/history data;
- downstream Taste semantic input is fail-closed until every exact pinned game has a fresh valid dossier.

## Validation performed

Committed-equivalent Git blobs were validated locally. Confirmed blob identity for contract/core/test files against `main`, then ran the regression suite:

`PYTHONPATH=scripts python -m unittest -v scripts.test_taste_steam_review_dossier`

Result: **11/11 passed**.

Required task controls:

1. Fresh dossier reuse without reanalysis — PASS.
2. Stale dossier rejected/refresh-required before Taste — PASS.
3. Default TTL 20 days and configurable TTL — PASS.
4. Russian review evidence can create localization finding — PASS.
5. Recurring negative can be represented neutrally without personal negative inference — PASS.
6. Downstream Taste input contains prepared dossier and exact pin binding — PASS.
7. Missing/stale dossier cannot silently fall back to store-description-only — PASS.
8. Persisted form is compact synthesis/provenance; raw-review archive is rejected — PASS.
9. Canonical pin authority remains read-only/preserved — PASS.

Additional controls:

10. Reusable dossier is appid-bound rather than tied to an `App_`/`Sub_` Taste subject key — PASS.
11. Submission must exactly cover GitHub-prepared appid scope and cannot exceed adaptive review ceilings — PASS.

End-to-end CLI smoke also passed:

- first work build: `work_required`, one missing dossier;
- validated ingest: `persisted`, one compact dossier;
- second work build: `ready_from_fresh_cache`, zero required items;
- semantic input build: `ready_for_taste_semantic_producer`, exact pin SHA retained;
- final marker: `CLI_SMOKE_OK`.

Production invariance checks:

- current active pin blob SHA before/after implementation: `7060a24f23937442253ecba25502796e317476a6` (unchanged);
- `scripts/taste_pinned_work_unit.py` blob SHA: `b4902dcf5c90003b6a4b9fc033bab57d91281d5a` (unchanged);
- existing Scheduled Task was not created, edited, duplicated or run by this task;
- old Taste throughput measurement was not continued or finalized.

## Remaining limitations / next authorized step

No live production dossier batch was generated in this task. That is intentional: the user explicitly prohibited creating the separate Scheduled Task now and prohibited continuing the old throughput measurement. Validation used deterministic Steam-shaped fixtures and the exact committed lifecycle code.

Next step, under a separate authorization/task, is to create the separate Steam dossier Scheduled Task using the committed worker prompt, let it populate the exact GitHub-prepared work manifest, then run a **new clean** Taste throughput measurement against `taste_semantic_dossier_input.json`. The existing Taste Semantic Producer should remain unchanged until that separate integration/measurement task explicitly authorizes the scheduler/handoff change.

## Timing / protocol note

This worker took longer than a simple patch because the START gate required architecture/ownership/pin checks, the current active Taste authority had to be proven unchanged, and the implementation was exercised through 11 regressions plus an end-to-end CLI smoke. Future workers can enter directly through the new contract + three scripts instead of rediscovering the dossier lifecycle.

## Final status

`complete_ready_for_separate_scheduler_and_clean_throughput_measurement`
