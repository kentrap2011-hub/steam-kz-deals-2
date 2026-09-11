# QUEUED TASK — giveaway-decouple-from-steam-crawl-01

Status: `queued_later_do_not_start_now`
Mode when authorized later: `IMPLEMENT`

## Goal

Make canonical Epic/GOG/Steam giveaway refresh independent from the full Steam commercial catalog traversal, so a commercial Steam crawl failure cannot block current giveaway refresh and publication.

## Required behavior

- Keep the full Steam commercial collector fail-closed on real commercial crawl errors.
- Allow `scripts/giveaway_production.py` (or its canonical equivalent at implementation time) to refresh the strict giveaway artifact independently.
- Preserve all current giveaway validation, region/KZ eligibility, provenance, and contract checks.
- Do not hardcode giveaway titles.
- A Steam commercial crawl failure must not erase or block valid current Epic/GOG giveaway state.
- Downstream visual giveaway-only refresh and deploy should continue to use canonical giveaway state.

## Explicit priority

The user asked to add this to the queue but **not work on it now**. Do not dispatch or implement until the Director explicitly authorizes it later.
