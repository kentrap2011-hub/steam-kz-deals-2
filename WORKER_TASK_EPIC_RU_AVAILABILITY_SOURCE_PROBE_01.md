# WORKER TASK — EPIC RU AVAILABILITY SOURCE PROBE 01

Task ID: `epic-ru-availability-source-probe-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/epic-ru-availability-source-probe-01.md`

## Context

Follow-up to:
`reviews/worker_reports/epic-ru-giveaway-availability-recon-01.md`

That recon is complete but implementation is blocked because it did not prove an automation-ready Epic-owned machine-readable signal whose semantics guarantee that a free offer is acquirable for an Epic account in Russia.

## Goal

Resolve exactly that blocker, and nothing broader.

Find and validate one authoritative Epic-owned machine-readable acquisition-availability signal for RU, or prove that no safe unattended signal is currently available.

## Required proof

1. Exact Epic-owned endpoint/request/field/status.
2. Exact RU account/country semantics.
3. At least one known RU-available offer case.
4. At least one known RU-unavailable offer case.
5. Demonstrate that the signal differentiates acquisition availability, not merely catalog visibility/promotion activity.
6. Failure/malformed behavior must be understood well enough to fail closed.
7. If using whitelist/blacklist fields, prove them from Epic-owned responses and prove their acquisition semantics; third-party field-name references are insufficient.
8. Do not change Steam/GOG or global KZ semantics.

## Stop conditions

If the only evidence remains undocumented discovery-row presence, catalog `ACTIVE`, or unverified third-party schema names, status must remain `blocked`.

## Boundaries

READ-ONLY only. No production code/data/UI/cache/Taste/ranking changes.

## Done when

Save:
`reviews/worker_reports/epic-ru-availability-source-probe-01.md`

Status exactly one:
- `complete`
- `blocked`
- `needs_user_evidence`

`complete` means an exact implementation-ready Epic-owned RU acquisition signal is proven.
