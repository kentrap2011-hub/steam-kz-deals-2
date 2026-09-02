# WORKER TASK — CHAT 2

Task ID: `giveaway-igdb-implement-prep-01`
Mode: `IMPLEMENT / PREP UNTIL USER SECRET PREREQUISITE`
Report: `reviews/worker_reports/giveaway-igdb-implement-prep-01.md`

## Context

Direct continuation of:
`reviews/worker_reports/giveaway-analysis-identity-recon-01.md`.

Known and already approved:
- giveaway UI/navigation is accepted and must not be redesigned;
- title/fuzzy matching is forbidden as semantic identity proof;
- smallest safe route is exact Epic/GOG provider identity -> IGDB External Game -> IGDB game id -> exact Steam appid -> existing canonical description/Taste path;
- current blocker is the already-known missing GitHub Actions secrets `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`;
- same credentials also unblock the existing duration/IGDB track.

Do not repeat identity recon.

## Goal

Own all repo-side preparation for this continuation and reduce the remaining user action to the smallest explicit secret-provisioning step.

## Required work

1. Inspect the existing implemented IGDB provider route and the exact GitHub workflow/config points that expect the two secrets.
2. Prepare/implement any safe repository-side wiring that does NOT require live secret values and does not depend on unverified Epic/GOG External Game semantics.
3. Do not guess provider source IDs/uid semantics. Any production binding that requires live IGDB acceptance must remain disabled/fail-closed until credentials are provisioned and verified.
4. Produce a compact user handoff containing exactly:
   - where the user must create/get the IGDB credentials;
   - exact GitHub repository Settings path where each secret must be added;
   - exact secret names: `IGDB_CLIENT_ID`, `IGDB_CLIENT_SECRET`;
   - explicit instruction never to paste the values into ChatGPT or commit them.
5. After documenting the user action, define the exact continuation to run immediately after the user says the secrets are added:
   - verify normal IGDB connectivity through the existing route;
   - acceptance-test exact Epic/GOG External Game identity semantics on a bounded sample;
   - persist canonical cross-store identity only when exact and unambiguous;
   - attach existing canonical description/pros/grounded cons to giveaway detail;
   - run canonical build/deploy if implementation succeeds;
   - leave UI acceptance semantics unchanged.

## Hard boundaries

Do NOT:
- ask the user to send secret values in chat;
- commit or log secret values;
- create another external provider, queue, scheduler, or browser fetch;
- manually map current giveaway titles;
- enable title/fuzzy fallback;
- redesign giveaway UI;
- repeat the completed recon.

## Stop condition

If live provider verification is impossible solely because the two GitHub secrets are absent, stop with status `blocked_on_user_secrets` after completing all safe repo-side preparation and exact user handoff.

Do not spend time repeatedly proving that the same secrets are absent.

## Report format

Save:
`reviews/worker_reports/giveaway-igdb-implement-prep-01.md`

### Repo-side preparation
What was safely completed before secrets.

### Exact user action
Minimal numbered secret-provisioning steps; no secret values.

### Post-secret continuation
Exact next implementation/acceptance route.

### Status
Exactly one:
- `blocked_on_user_secrets`
- `complete`
- `needs_fix`
- `needs_user_decision`

Efficiency / reusable lesson: `none | <short candidate/ref>`

Final response must include the report path and exact refs.