# Worker report: steam-postmerge-actions-failures-fix-01

Repository: kentrap2011-hub/steam-kz-deals-2; base main fcbbec1eacdc81cca88193283e97d49e294d1091; ЧАТ 6.

## Root causes
- Actions [policy #40523125907](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125907): validator expected 1.21 while canonical policy is 1.22; profile check matched an obsolete local-variable spelling, although projection compares each cached profile SHA exactly to the current profile SHA.
- Actions [family #40523125705](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125705): previously complete eligibility included App_1492680/The Pathless against an older mailing tree. Current mailing tree and the old eligibility source binding differ. Historical taste cache has 101 INCLUDE verdicts, but 67 keys are outside the current 703-row mailing feed; no current KZ offer/price for them. Metadata collector previously failed on missing historical rows; family dereferenced them unchecked.

## Implementation
- Actual version 1.22 and actual exact profile-SHA expression validated, without disabling the cache binding check.
- GitHub-owned legacy metadata/eligibility stages now classify only current mailing feed members, with full explicit historical out-of-feed key list and counts. Historical taste cache entries remain unchanged.
- Shared fail-closed offer/key/AppID validation rejects duplicates or mismatches. Family stage verifies source Git SHAs, current-scope coverage, receipt and identity before price access; no fake price or silent eligible omissions.
- Targeted regression `scripts/test_legacy_offer_scope.py` in existing PR-only `steam-test.yml`, which also executes the canonical policy validator.
- No new workflow, scheduled job, retry, Deep, Dossier, ITAD or production state writes. No manual dispatch.

## Verification
PR #346 code HEAD `cb8cf8bf268f13938ecce223c61db4d7e75232e7`: existing `Steam KZ production shortlist` PR regression run [#40748993196](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40748993196) **success**, including `Validate post-merge policy and historical/current offer scope` and full `Run fresh discovery regressions`; `collect` intentionally skipped for PR. Existing `Validate backlog dispositions` [#40748993171](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40748993171) **success**; site task registry/page [#40748993346](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40748993346) **success**. This report-only update requires final-HEAD checks to be re-confirmed. Deterministic PR tests are not a live successful main production, metadata rebuild or Pages deploy. Those require the existing GitHub-owned chain after Director review/merge.

## Bounded downstream Actions disposition (merge commit 59b5aec)
- [Content eligibility #40523125741](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125741) failed due to stale metadata-vs-current-mailing-tree binding; directly related to the stale historical/current scope mismatch and addressed by producer scope reconciliation + future exact source binding validation.
- [Build site current status #40523125745](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125745) built and validated status but could not push after three competing main updates. Separate Git write race, not an eligibility/family price lookup error; no unsupported retry/ownership change added here.
- [Steam shortlist #40523125746](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125746) failed in live collect, a separate collector runtime failure, not caused by the family KeyError in this workflow; this task does not alter the collector.
- [Daily visual #40523126047](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523126047) and [deploy #40523125681](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125681) were cancelled, not confirmed downstream validation errors. Re-activation or live publication has not been demonstrated.
