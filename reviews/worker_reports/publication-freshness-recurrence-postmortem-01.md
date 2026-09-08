# Publication Freshness Recurrence Postmortem 01

## Task
Cross-incident READ-ONLY / RECON / POSTMORTEM for giveaway, paid-list, and automatic ChatGPT/Taste freshness recurrence.

## Status
`in_progress`

## Scope
Determine bounded local causes, common systemic failure modes, per-domain end-to-end freshness invariants, exact cadence/grace windows for `current` / `delayed` / `stale`, a durable first-missed-day signal without paid API or per-domain schedulers, user-visible partial-freshness semantics, and exactly one bounded next IMPLEMENT task.

## Interim findings

### Local incident causes already bounded by predecessor work
- Giveaway recurrence: fresh giveaway source/runtime state could exist while the canonical/public visual handoff remained stale or absent. The failure boundary was publication handoff/provenance, not source absence. The accepted recovery now supports a bounded `giveaway_only` canonical visual refresh and an exact scoped freshness receipt; such a receipt explicitly does not claim unrelated full-visual/Taste freshness.
- Paid-list recurrence: deterministic commercial truth continued advancing while the canonical paid visual publication stopped advancing. The missing owner was the paid publication handoff, not Steam collection. The accepted recovery now supports `commercial_only` refresh through the existing canonical visual writer and exact scoped receipt, with `full_visual_freshness=false`.
- Automatic ChatGPT/Taste recurrence: after a prior successful daily cycle, the expected 01:00 Europe/Samara cycle had no stage/final lifecycle evidence even though candidates existed. The bounded cause was failure before staging/commit, consistent with the external Scheduled Task not dispatching/starting. A success-side tracker alone cannot detect its own total non-dispatch.

### Existing ownership and cadence facts
- `config/daily_execution_contract.json` and `config/execution_ownership_contract.json` make the external ChatGPT controller the sole production owner for Taste; expected run is 01:00 Europe/Samara. GitHub scheduling/fallback for Taste is forbidden.
- `.github/workflows/steam-test.yml` (`Steam KZ production shortlist`) is the existing daily GitHub production owner for the deterministic commercial/giveaway source cycle. Its schedule is 00:10 Europe/Samara and its job timeout is 60 minutes.
- `.github/workflows/build-mailing-feed.yml` is an already-existing independent daily GitHub schedule at 09:17 Europe/Samara. It runs after both expected overnight production cycles and is therefore a viable durable observation point for a first-missed-day freshness check without introducing another scheduler.

### Common systemic failure shape
The recurring defect is not one shared producer bug. It is the absence of one end-to-end, cycle-keyed freshness invariant that answers whether each independently owned daily domain actually completed publication for the expected local day. Source freshness, canonical publication freshness, and task dispatch evidence can diverge. Checking only file age or only success receipts is insufficient because a process that never starts cannot write its own failure receipt.

### Direction under investigation
Freshness must be evaluated against each domain's expected local daily cycle and its own success evidence, with independent states `current`, `delayed`, and `stale`. A durable cross-domain observer must not rerun producers; it should only persist the observed state. Public/health semantics should preserve the last known good readable payload while marking the affected domain stale instead of converting stale publication into an empty result or falsely declaring all domains stale.

## Changes
Report file only. No prevention mechanism has been implemented.
