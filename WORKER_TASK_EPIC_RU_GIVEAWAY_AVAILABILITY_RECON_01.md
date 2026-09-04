# WORKER TASK — EPIC RU GIVEAWAY AVAILABILITY RECON 01

Task ID: `epic-ru-giveaway-availability-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/epic-ru-giveaway-availability-recon-01.md`

## User request

Future behavior change, Epic Games only:

- include Epic Games free giveaways only when the giveaway is currently available/redeemable for the **Russian region (RU)**;
- Steam giveaway behavior must remain unchanged;
- GOG giveaway behavior must remain unchanged.

Interpretation: "available for the Russian region" means the giveaway must be claimable in RU. It does **not** mean the giveaway has to be exclusive to Russia.

## Why recon first

Current Epic collection historically uses KZ-oriented request semantics. Before implementation, establish the smallest authoritative RU-availability check using the current Epic source contract without weakening fail-closed behavior or changing Steam/GOG semantics.

## Goal

Determine the exact bounded implementation needed so Epic accepted giveaways satisfy current free-promotion rules **and** are available for RU, while Steam/GOG remain exactly as today.

## Required checks

1. Read current `scripts/giveaway_epic.py`, `scripts/giveaway_production.py`, giveaway contract/tests, and only the exact source/region docs or response fields needed.
2. Identify the current Epic region inputs and whether RU availability can be established by:
   - querying Epic with `country=RU` / equivalent current endpoint semantics;
   - an authoritative allowed-country / offer-availability field;
   - or another existing source-owned signal.
3. Determine whether switching only the Epic adapter from KZ to RU is sufficient and safe, or whether a separate RU-availability verification is required.
4. Preserve current active/current/100%-free validation and fail-closed schema behavior.
5. Specify how canonical source metadata should represent the Epic region after the change without changing Steam/GOG region semantics.
6. Identify focused regression cases at minimum:
   - active Epic giveaway available in RU -> accepted;
   - active Epic giveaway unavailable in RU -> rejected/skipped according to the existing source contract;
   - malformed/unknown RU availability -> fail closed, not guessed;
   - Steam behavior unchanged;
   - GOG behavior unchanged.
7. Identify any user-visible/canonical migration or audit checkpoint triggered by changing Epic provider region semantics.
8. Produce one bounded IMPLEMENT plan only.

## Boundaries

Do NOT change code or production data in this recon.
Do NOT change Steam collector behavior.
Do NOT change GOG collector behavior.
Do NOT change giveaway UI, cache, publication chain, ITAD/IGDB, Taste/ranking, or semantic runtime.
Do NOT broaden this into a general project-region migration.

## Done when

Save:
`reviews/worker_reports/epic-ru-giveaway-availability-recon-01.md`

Include:
1. Task
2. Current Epic region semantics
3. Authoritative RU-availability signal
4. Exact behavior change
5. Steam/GOG non-impact proof
6. Regression plan
7. Review/audit implications
8. One bounded IMPLEMENT plan
9. Status
10. Exact refs

Status exactly one:
- `complete`
- `blocked`
- `needs_user_decision`
