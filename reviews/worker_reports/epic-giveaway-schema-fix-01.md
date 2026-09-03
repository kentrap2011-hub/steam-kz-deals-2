# EPIC GIVEAWAY SCHEMA FIX 01

STATUS: complete

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

Implementation blob:
- `scripts/giveaway_epic.py` — `6fb410a27a0bc40c3fce2eecacc9d09da7aec88e`

## STRICTNESS PRESERVED

For every element that is actually an active current 100% giveaway candidate, the adapter remains fail-closed and explicitly requires:

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

Covered cases:

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

Test blob:
- `scripts/test_giveaway_production.py` — `0bf860f3e35e5dc367a82f531be7d55c3abba089`

Final GitHub-owned regression evidence:
- run `33790442843`;
- head SHA `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`;
- job `100774514557`;
- `Regression test cross-platform giveaways` -> `success`.

Therefore the required focused regression surface has executed successfully in GitHub Actions.

## PRODUCTION VERIFICATION

Canonical GitHub-owned run:
- run `33790442843`;
- workflow `Steam KZ production shortlist`;
- head SHA `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`.

Relevant final step results:

- `Regression test cross-platform giveaways` -> `success`;
- `Collect full Steam KZ catalog and build production shortlist` -> `success`;
- `Verify Steam collector touched only owned production paths` -> `success`;
- `Build canonical Steam Epic GOG KZ giveaways` -> `success`;
- `Validate canonical giveaway artifact contract` -> `success`;
- `Verify production writers touched only owned paths` -> `success`.

The fresh canonical giveaway result produced by this run was:

- snapshot: `complete`;
- Epic source `status = ok`;
- Epic source `complete = true`;
- Epic `accepted_count = 1`.

This proves the original parser-ordering failure no longer aborts Epic merely because irrelevant/non-current catalog elements have variant `price.totalPrice`, while a real active current giveaway still maps through the canonical schema under the preserved strict price contract.

## RUN-LEVEL FAILURE CLASSIFICATION

Run `33790442843` has overall conclusion `failure`, but the failure occurred only at the final post-verification step:

- `Commit production feed, giveaways and review cache` -> `failure`.

By that point all task-relevant regression, canonical giveaway build, source-health generation, writer-boundary verification and giveaway contract validation had already completed successfully.

The final commit step failed because `main` advanced while the long-running job was executing and the workflow hit a rebase conflict when attempting to publish generated production files. The run started from `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`; `main` later advanced beyond that head (observed closeout ref: `f9cdee6ae0776e683fdf1005cba3baf6061a7924`).

This publication/rebase conflict is not an Epic parser failure and does not invalidate the already-produced fresh canonical snapshot/source-health evidence required by this task. No follow-up parser fix is indicated by it, and this closeout does not broaden scope into workflow publication behavior.

## EPIC SOURCE COMPLETE?

Yes.

Fresh canonical evidence from run `33790442843`:

- `status = ok`;
- `complete = true`;
- `accepted_count = 1`.

## CURRENT ACTIVE ACCEPTED GIVEAWAY COUNT

Fresh canonical Epic accepted count: **1**.

## ORIGINAL INCIDENT CLOSED?

Yes.

The original `SOURCE_SCHEMA_FAILURE` incident caused by validating `price.totalPrice` before determining giveaway relevance is closed by:

1. the implemented ordering fix;
2. focused regression coverage proving irrelevant/upcoming variant-price elements are skipped without weakening active-giveaway strictness;
3. successful GitHub-owned canonical giveaway build;
4. successful canonical giveaway contract validation;
5. fresh complete snapshot with Epic `status=ok`, `complete=true`, `accepted_count=1`.

The separate final-step rebase conflict does not reopen the Epic schema incident.

## STATUS DECISION

`complete`.

Under the task contract, completion requires the narrow parser fix, preserved fail-closed behavior for actual current giveaways, focused regression proof, and fresh canonical production/source-health evidence. All of those conditions are now satisfied.

The workflow's final generated-file commit failure occurred after those acceptance conditions were met and was caused by concurrent `main` advancement/rebase conflict, not by the Epic implementation or its canonical output. Therefore `blocked` is no longer appropriate, and `needs_followup_fix` would incorrectly classify an unrelated publication race as an Epic parser defect.

## EXACT REFS

- task: `WORKER_TASK_EPIC_GIVEAWAY_SCHEMA_FIX_01.md`
- recon closeout: `reviews/worker_reports/epic-giveaway-schema-recon-01.md`
- implementation commit: `aa7cea8d06d4d71a5ff6fe4c23a71c2cbda28783`
- implementation blob: `scripts/giveaway_epic.py` @ `6fb410a27a0bc40c3fce2eecacc9d09da7aec88e`
- regression commit / canonical run head: `d59d31a311c54b1501b78f4ba8bfb456cebf5f3f`
- regression blob: `scripts/test_giveaway_production.py` @ `0bf860f3e35e5dc367a82f531be7d55c3abba089`
- canonical final run: `33790442843`
- canonical final job: `100774514557`
- run overall conclusion: `failure` only at final generated-file commit step
- task-relevant build/validation steps: `success`
- observed advanced `main` ref during final closeout: `f9cdee6ae0776e683fdf1005cba3baf6061a7924`

## SCOPE CHECK

- new implementation in this closeout: **none**;
- `scripts/giveaway_epic.py`: unchanged in this closeout;
- `scripts/test_giveaway_production.py`: unchanged in this closeout;
- only `reviews/worker_reports/epic-giveaway-schema-fix-01.md` updated;
- workflows: unchanged;
- Epic endpoint/KZ params: unchanged;
- active giveaway price strictness: preserved/fail-closed;
- Steam/GOG behavior: untouched;
- ITAD/IGDB: untouched;
- title/fuzzy/manual inference: not introduced;
- extra provider/fallback: not introduced.
