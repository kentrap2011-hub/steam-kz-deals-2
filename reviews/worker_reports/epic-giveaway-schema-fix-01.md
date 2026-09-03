# EPIC GIVEAWAY SCHEMA FIX 01

STATUS: blocked

## IMPLEMENTATION

Implemented only the parser-ordering repair proven by `epic-giveaway-schema-recon-01`.

In `scripts/giveaway_epic.py`:

1. Element identity fields needed by the adapter are still validated first.
2. `promotions` is inspected before price data.
3. A candidate is selected only when an entry in the existing `promotionalOffers` / current state:
   - has parseable `startDate` and `endDate`;
   - is active at `observed` (`start <= observed < end`);
   - has object `discountSetting`;
   - has integer `discountSetting.discountPercentage`;
   - has `discountPercentage == 0`.
4. Elements that are not active current 100% giveaway candidates are skipped before reading `price.totalPrice`.
5. Only an active current 100% giveaway candidate is then required to satisfy the strict price contract.

No endpoint, KZ parameters, claim URL rules, canonical output schema, source-health ownership, Steam/GOG logic, ITAD/IGDB identity enrichment, paid-deal/ranking/Taste logic, workflow, scheduler, queue or writer ownership was changed.

Implementation commit:
- `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783` — `Fix Epic giveaway price validation ordering`

Current `main` implementation blob at verification time:
- `scripts/giveaway_epic.py` — `6fb410a27a0bc40c3fce2eecacc9d09da7aec88e`

## STRICTNESS PRESERVED

For every element that is actually an active current 100% giveaway candidate, the adapter remains fail-closed and now explicitly requires:

- `element.price` is an object;
- `price.totalPrice` is an object;
- `price.totalPrice.discountPrice` is an integer (bool rejected);
- `price.totalPrice.originalPrice` is an integer (bool rejected);
- `discountPrice == 0`;
- `originalPrice >= 0`.

Malformed current promotion discriminator data needed to decide whether an active entry is a 100% giveaway remains a `SourceSchemaError`; it is not inferred from title or price.

No fallback price, fuzzy/title inference, second source, or globally optional price contract was introduced.

## FOCUSED REGRESSION COVERAGE

Focused coverage was added to the existing `scripts/test_giveaway_production.py` surface rather than creating a new test subsystem.

Added/updated cases cover:

1. no-current-promo element + missing `price.totalPrice` -> skipped;
2. no-current-promo element + `price.totalPrice = null` -> skipped;
3. upcoming-only promo + variant/null `price.totalPrice` followed by a valid current giveaway -> upcoming element does not abort current extraction;
4. current active 100% promo + valid normal price -> existing mapping remains valid and accepted;
5. current active 100% promo + missing `price.totalPrice` -> `SourceSchemaError`;
6. current active 100% promo + non-object/null `price.totalPrice` -> `SourceSchemaError`;
7. current active 100% promo + non-integer price field -> `SourceSchemaError`;
8. current 100% promotion whose price says non-zero `discountPrice` -> fail closed;
9. malformed active `discountPercentage` discriminator -> fail closed.

Test commit:
- `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f` — `Add Epic giveaway schema ordering regressions`

Current `main` test blob at verification time:
- `scripts/test_giveaway_production.py` — `0bf860f3e35e5dc367a82f531be7d55c3abba089`

Worker-side focused logic checks for the ordering/fail-closed cases passed.

GitHub-owned workflow evidence currently available:
- run `33790369125`, head `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`;
- workflow `Steam KZ production shortlist`;
- `Regression test cross-platform giveaways` completed successfully;
- the run is still inside the preceding long `Collect full Steam KZ catalog and build production shortlist` step, so its canonical giveaway production step has not run yet.

The workflow run containing the newly committed focused regression cases is:
- run `33790442843`, head `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`;
- status at closeout: `pending`, queued behind run `33790369125` under the existing workflow concurrency.

Because the newly added focused cases have not yet executed in GitHub Actions, no GitHub-CI PASS is claimed for those new cases in this closeout.

## PRODUCTION VERIFICATION

The existing canonical path is already wired into `.github/workflows/steam-test.yml` and requires no workflow change. It runs:

- giveaway regression tests;
- the canonical `scripts/giveaway_production.py` path writing `data/production/giveaways/v1/current.json` and audit output;
- `scripts/validate_giveaway_contract.py`.

At closeout time the code-commit run `33790369125` had not yet reached `Build canonical Steam Epic GOG KZ giveaways`; it remained in the earlier full-Steam-catalog collection step. The test-commit run `33790442843` remained pending behind it.

The worker execution environment cannot independently reach GitHub/Epic over network/DNS for a fresh canonical live run, so the task explicitly permits using GitHub-owned production evidence. That evidence is not complete yet.

Therefore this report does **not** claim any of the following without evidence:

- that the fresh Epic source is `ok/complete`;
- a fresh active accepted Epic giveaway count;
- that the current canonical snapshot has been regenerated successfully;
- that the original production `SOURCE_SCHEMA_FAILURE` incident is closed.

## EPIC SOURCE COMPLETE?

Cannot yet be established from fresh canonical production evidence.

Status: **blocked on the already-running canonical GitHub workflow reaching and completing the giveaway production step.**

This is not a request to weaken the parser. If a real active current 100% giveaway later fails the strict price contract, the correct result remains fail-closed and would require explicit follow-up evidence rather than a permissive workaround.

## CURRENT ACTIVE ACCEPTED GIVEAWAY COUNT

Not claimed. Fresh canonical live production evidence was not yet available at closeout.

## ORIGINAL INCIDENT CLOSED?

Not yet proven closed in production.

The implementation directly removes the proven ordering defect and preserves strictness for actual current giveaways, but closure requires the fresh canonical source-health/snapshot evidence demanded by this task. The canonical GitHub-owned run is already in progress; no separate workflow or source was introduced.

## EXACT REFS

- recon closeout: `reviews/worker_reports/epic-giveaway-schema-recon-01.md`
- implementation commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`
- implementation blob: `scripts/giveaway_epic.py` @ `6fb410a27a0bc40c3fce2eecacc9d09da7aec88e`
- regression commit: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`
- regression blob: `scripts/test_giveaway_production.py` @ `0bf860f3e35e5dc367a82f531be7d55c3abba089`
- canonical code-run: `33790369125` (`aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`), in progress at closeout
- canonical test-run: `33790442843` (`d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`), pending at closeout

## SCOPE CHECK

- `scripts/giveaway_epic.py`: changed, ordering fix only.
- `scripts/test_giveaway_production.py`: changed, focused Epic regression coverage only.
- workflows: unchanged.
- Epic endpoint/KZ params: unchanged.
- active giveaway price strictness: preserved/fail-closed.
- Steam/GOG behavior: untouched.
- ITAD/IGDB: untouched.
- title/fuzzy/manual inference: not introduced.
- extra provider/fallback: not introduced.
