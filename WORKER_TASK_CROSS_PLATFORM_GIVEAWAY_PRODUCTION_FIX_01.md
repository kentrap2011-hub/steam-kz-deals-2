# WORKER TASK — CHAT 1

Task ID: `cross-platform-giveaway-production-fix-01`
Mode: `IMPLEMENT / FIX`
Report: `reviews/worker_reports/cross-platform-giveaway-production-fix-01.md`

## Goal

Finish the missing production integration from `cross-platform-giveaway-implement-01`.

Do NOT repeat source recon and do NOT rewrite the Steam/Epic/GOG adapters unless a concrete integration failure proves a bounded fix is necessary.

## Read first

- `reviews/worker_reports/cross-platform-giveaway-implement-01.md`
- `config/execution_ownership_contract.json`
- `config/daily_execution_contract.json`
- current canonical GitHub-owned daily production workflow
- the implemented giveaway contract/producer/tests from the prior task

## Required work

1. Wire `scripts/giveaway_production.py` into the existing canonical GitHub-owned daily production path at the correct stage.
2. Wire `scripts/test_giveaway_production.py` into the smallest appropriate existing validation/CI route; do not add a recurring schedule.
3. Preserve single-writer ownership:
   - existing Steam collector continues to own legacy `data/production/freebies.tsv` / `freebies_index.json`;
   - cross-platform producer alone owns `data/production/giveaways/**`.
4. Run the canonical production workflow once, or use the exact existing supported manual dispatch path if the canonical workflow already exposes one.
5. Verify the generated canonical artifacts:
   - `data/production/giveaways/index.json`
   - `data/production/giveaways/v1/current.json`
   - `data/production/giveaways/v1/audit.jsonl`
6. Record real current KZ source health for Steam / Epic / GOG and accepted current offer count.
7. If the correct accepted count is zero, treat that as valid only if all required Tier-1 sources refreshed successfully and the snapshot is complete.
8. If one required source fails, preserve fail-closed/incomplete semantics; do not fake completeness and do not manually seed rows.

## Validation

- deterministic giveaway suite passes in the canonical validation route;
- production workflow/run ref is recorded;
- generated artifact validates against `CROSS-PLATFORM-GIVEAWAY-V1`;
- source completeness/freshness is explicit;
- no second scheduler or writer is introduced.

## Hard boundaries

Do NOT:
- repeat broad recon;
- redesign adapters unless a concrete failing integration requires a bounded patch;
- change Taste/paid ranking/UI;
- add manual production rows;
- add a second recurring ChatGPT/GitHub schedule;
- weaken fail-closed rules merely to produce a non-empty result.

## Done when

- producer and tests are wired into the existing canonical GitHub production/validation paths;
- one real canonical production run has completed;
- the versioned giveaway artifacts exist on main or the exact canonical generated-artifact destination used by the project;
- real Steam/Epic/GOG health and accepted count are recorded;
- no scoped blocker remains.

## Report format

Save:
`reviews/worker_reports/cross-platform-giveaway-production-fix-01.md`

### Task
What was finished.

### Production wiring
Exact workflow/stage and writer ownership.

### Production result
Run ref, Tier-1 source health, completeness, accepted offer count.

### Changes
Exact files/commits.

### Validation
Tests and artifact validation.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only; `none` is valid if production data plane is complete.

Final response must include report path and exact refs.