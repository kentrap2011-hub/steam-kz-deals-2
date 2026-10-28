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
PR checks and exact final PR HEAD: pending. Deterministic PR tests are not a live successful main production, metadata rebuild or Pages deploy. Those require the existing GitHub-owned chain after Director review/merge.
