# Steam KZ price-only 30-ID batch test — 2026-11-09

**Authorization:** explicit user request "Проверяй", after the [RECON report PR #422](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/422) proposed this exact bounded test.  
**Scope:** only repository kentrap2011-hub/steam-kz-deals-2; trial branch in [draft PR #423](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/423). GitHub main at branch creation e8bbae604c29c215e561d860a804bad623f860e3.  
**Execution:** [GitHub Actions run 42612198610](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42612198610), successful; executable commit 1afc9290b3a8a4b590237e77e8739320b40726a5.  
**Sample provenance:** 4 eligible base roots and 26 related child-candidate AppIDs observed in [completed collector run 42601207552](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42601207552), source SHA 9b4b0668438c20b39a48302acd27ddb3250ff41c. Related candidate is not proof of DLC app.type.

## Measured output

| Metric | Exact observed result |
| --- | --- |
| Individual KZ full-appdetails GETs | 30, HTTP 200 each |
| Batch KZ appdetails with filters=price_overview | 1, HTTP 200; 30 AppID keys returned |
| Total physical requests | 31 / maximum 31, no retries, no 429/502/5xx |
| Individual elapsed wall, with 0.9s pacing | 26.244 seconds |
| Batch GET service duration, separate from start pacing | 0.234 seconds |
| Entire bounded comparison | 27.238 seconds |
| Price-bearing single records | 27, all currency KZT |
| Exact price-field matches | **27/27 priced AppIDs**, identical initial/final integer minor units, discount percent, KZT |
| Other three IDs | 235960, 488140, 2819760 |
| Strict normalization mismatches | 3: full metadata single returned a data dictionary without price_overview (unpriced); filtered batch returned success=true but no data dictionary (no_data) |
| Script verdict | PRICE_OR_RESPONSE_MISMATCH; 27 of 30 strict normalized records matched |
| CI result | SUCCESS means test execution completed, NOT full strict comparison pass |

The three mismatches are **absent-price response-shape differences**, not an observed mismatch of two KZT prices. Neither record carried priced KZT fields in the compared response. This is not yet proven equivalent availability/identity semantics: fail closed rather than silently interpreting missing data as a definitive nonsale.

## Architecture and safety conclusion

**PRICE_PARITY_PRICED_27 / INCOMPLETE_SCHEMA_PARITY_3.** Batch price_overview is technically available for the exact KZ 30-ID sample and reproduces 27/27 complete priced records. It does **not** return all type, fullgame immediate parent, DLC lists, nested chain and identity metadata needed to preserve the current full-source discovery semantics. Thus it cannot replace all full child GETs without a separate, verified proof of terminality and source/expiry completeness. A 0.234s batch request compared with 26.244s of 30 paced full requests is **not** an observed ~112x end-to-end collector speedup, nor proof of any of the ~1,751 production appdetails calls being safely eliminable.

No modification was made to existing source/production workflows, appdetails pacing 180/300s, 429 policy, main, daily schedule, KZT/50%/4500 safeguards, root relation rules, data/cache, manifests, mailing, semantic work, site or output publication. The isolated trial uses GitHub-only read-only permission, a PR-open-only trigger, restricted exact branch, 31 physical GET hard cap, 0.9s minimum spacing, 12s per GET timeout, zero retries and a 5-minute job timeout. It should **not be merged** into main as a permanent recurring workflow.

**Further work requires a new user decision:** prove which exact terminal child IDs may avoid full metadata GETs, using a frozen source snapshot plus exact old-vs-new App_/Sub_/DLC coverage, parent chains and fail-closed null handling. No additional live traffic or production cutover was authorized or performed by this one-off trial.

## Evidence

- [Action run 42612198610](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/42612198610) contains every per-call status and complete structured price-canary-result log.
- [Trial script](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/trial/steam-kz-price-batch-30-20261109/scripts/steam_kz_price_batch_canary.py).
- [PR-only workflow](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/trial/steam-kz-price-batch-30-20261109/.github/workflows/steam-kz-price-batch-canary.yml).
