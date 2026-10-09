# WORKER TASK — Commercial refresh independent from Dossier failure 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Mode: `IMPLEMENT / PRODUCTION RESILIENCE`

## User-approved product requirement

Fresh Steam discounts/prices and the site's commercial/current-offer state must update independently of Dossier-specific failures.

A local Dossier test/validation/preparation defect must NOT keep the site pinned to an older commercial snapshot when the Steam collection and deterministic commercial preparation succeeded.

This does **not** authorize weakening, bypassing, or auto-accepting invalid Dossiers.

## Confirmed current defect

On 2026-10-08:
- `Steam KZ production shortlist` succeeded;
- `Build mailing-optimized feed` succeeded;
- `Build pre-AI deterministic payload` then failed in the Dossier regression suite;
- the failing test path was `scripts/test_taste_steam_review_dossier_prepublication.py`;
- failures were caused by test fixtures being considered expired by the strict Dossier validator;
- because the large pre-AI workflow commits atomically only after all later stages pass, the newly built commercial/pre-AI state was not persisted;
- the site therefore continued to show a commercial source from 2026-10-06 even though the 2026-10-08 Steam collection had succeeded.

This violates the project rule that local subsystem defects must not freeze unrelated current site data.

## Goal

Refactor the production refresh boundary so that a Dossier-local failure cannot block publication/persistence of already-successful current Steam/commercial data.

The solution must preserve strict fail-closed Dossier validation.

## Required investigation

Read current:
- `.github/workflows/build-pre-ai-store-snapshot.yml`
- `.github/workflows/build-mailing-feed.yml`
- commercial/pre-AI builders used before Dossier preparation
- Dossier preparation/validation/test steps
- site visual/publication builders and freshness contracts
- existing site publication resilience contract/tests

Identify the smallest safe boundary that separates:
1. current Steam/commercial deterministic artifacts required by the site;
2. Dossier-specific preparation, reconciliation, validation and tests.

Do not redesign unrelated pipelines.

## Required behavior

### A. Commercial/site freshness must persist independently

If these succeed:
- current Steam/shortlist input;
- mailing feed;
- deterministic current Store snapshot / offer-family / purchase/commercial state;
- any other deterministic artifacts required for the site to safely show current offers;

then those successful current artifacts must be persistable/publishable even when a later Dossier-specific stage fails.

The site must not keep an older commercial date solely because Dossier failed.

### B. Dossier remains fail-closed

If Dossier preparation/tests/validation fail:
- do not update canonical Dossier acceptance from invalid output;
- do not fabricate/recover/skip Dossier evidence;
- keep the previous valid Dossier state or explicit Dossier diagnostic state;
- expose the Dossier problem independently in observability/Statistics if already supported;
- Deep must not receive an unvalidated Dossier.

### C. No false freshness

Do not simply change the displayed date.

The site may show a new commercial refresh date only when the corresponding Steam/commercial artifacts were actually produced from that current cycle and persisted with intact source bindings.

If downstream semantic artifacts remain older, their own timestamps/bindings must remain honest.

### D. Failure isolation

A Dossier-local failure may degrade only Dossier-dependent outputs.

It must not invalidate:
- current prices;
- discount percentages;
- active/expired offer filtering;
- current commercial candidate universe;
- other deterministic commercial fields that were successfully rebuilt.

True global integrity failures may still fail closed.

### E. Current failing Dossier test

Also repair the current time-brittle Dossier regression fixture that caused the 2026-10-08 build to fail:
- valid fixture cases must remain valid over time;
- invalid fixture cases must still fail for their intended reason;
- do not weaken the production expiry validator;
- do not replace expiry checks with permissive behavior.

Prefer dynamically time-relative test fixtures or another deterministic non-expiring test construction.

## Acceptance tests

Prove at minimum:

1. Dossier test fixture no longer expires simply because wall-clock time advanced.
2. Strict production Dossier expiry validation still rejects already-expired real candidates.
3. Simulated Dossier-local failure after successful commercial preparation does not prevent current commercial artifacts from being persisted/published.
4. Site freshness date/source binding advances with successful commercial refresh even while Dossier remains on previous valid state.
5. Dossier observability clearly remains old/failed/pending as appropriate; no false claim that Dossier refreshed.
6. Deep does not consume unvalidated Dossier output.
7. Existing site publication resilience tests remain green.
8. Existing Dossier strict validation tests remain green.

## Real production proof

After the implementation is merged, the Director must be able to observe:
- a successful current-cycle commercial/pre-AI publication path;
- the site no longer pinned to the 2026-10-06 commercial source solely due to the Dossier test failure;
- current Dossier state remains truthful and independently validated.

Do not falsify this proof by manually editing timestamps or production JSON.

## Boundaries

- No weakening of Dossier evidence, provenance, expiry, Russian, temporal, identity or privacy validation.
- No changes to Dossier semantic scope/order/retry rules unless strictly required for isolation and explicitly justified.
- No Deep scoring/ranking changes.
- No Steam discovery policy changes (discount threshold, price cap, top-N policy, DLC policy).
- No translation changes.
- No Scheduled Task / automation changes.
- No synthetic production data.
- No manual timestamp bump.
- No broad architecture rewrite beyond the persistence/failure boundary required by this defect.

## Deliverable

Create:
`reviews/worker_reports/commercial-refresh-independent-from-dossier-failure-01.md`

Report must include:
1. exact root cause;
2. exact persistence/failure boundary before and after;
3. files changed;
4. proof strict Dossier validation is unchanged;
5. tests proving commercial refresh independence;
6. real or merge-ready production verification plan;
7. any remaining limitation.

Create a PR and stop.
