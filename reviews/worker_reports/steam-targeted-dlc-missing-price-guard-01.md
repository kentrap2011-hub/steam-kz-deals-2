# Worker report — steam-targeted-dlc-missing-price-guard-01

**Worker:** НОВЫЙ ЧАТ 1, bounded IMPLEMENT + developer self-review + existing GitHub checks; **no independent QA worker**.
**Source PR:** https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/401
**Base:** `main`, branch `fix/steam-targeted-dlc-missing-price-guard-01`.
**Implementation/test SHA before this report:** `4b15ef22486d03944f0a2ad776415dbb3ab5bd10`.
**Exact final PR HEAD:** use the authoritative PR head SHA and GitHub Actions checks at the linked PR; the report commit itself necessarily changes the head. Its exact final SHA and CI outcome will be attested in a PR conversation comment without another code/document commit.
**Status:** IMPLEMENTED; awaiting Director source acceptance and full live main acceptance. **Worker MUST NOT merge.**

## Changed files
1. `scripts/steam_targeted_paid_lanes.py` — exact targeted-DLC classification of absent/null/empty-object price data, integrity-before-skip, and strict nonempty price checks.
2. `scripts/test_steam_targeted_paid_lanes.py` — one new deterministic regression covering synthetic App_201877 no-price variants, a succeeding valid KZT DLC sibling and suppressed out-of-gate siblings, foreign/partial/malformed data, child identity and parent integrity.
3. `reviews/worker_reports/steam-targeted-dlc-missing-price-guard-01.md` — this evidence and handoff.

No production data, workflow, scheduler, retry, queue, rate limiter, Steam Search sort/cap, Dossier/Deep semantics, Board or director status changed.

## Factual cause, before and after
**Before:** `data.get('price_overview') or {}`, followed by `price.get('currency') != 'KZT'`, made an absent/null/empty price object raise `DLC App_201877 has non-KZT price` before verifying sale fields. A single unpriced child blocked the complete paid shortlist run.

**After:** after exact AppID/type and `fullgame` relationship integrity, only a missing `price_overview`, explicit null, or an empty dictionary skips that single DLC without emitting a paid card. The following unique children are still fetched and subjected to the same paid gates. For a nonempty price object, actual KZT currency and integer `final` / `discount_percent` are mandatory; foreign currency (RUB/USD/EUR), missing/partial fields, wrong-value types and malformed outer structures still fail closed. Correct KZT discounts are accepted only under unchanged `PAID_MAX_PRICE_KZT` (4500) and `PAID_MIN_DISCOUNT_PERCENT` (50).

**Integrity and source coverage:** exact `cc=kz` fetch, canonical positive parent/child identities, strict parent `type=game`, DLC `type=dlc` handling, no global DLC crawl, ordered dedupe, complete verified parent set and unchanged reporting. For a synthetic parent with 4 unique related children (including no-price App_201877), `dlc_price_lookups=4`, `dlc_accepted_after_paid_gate=1`, `dlc_rejected_after_paid_gate=3`, and `relation_complete=true`; the no-price child never becomes an invented zero-cost candidate. Incorrect fullgame relationship of an unpriced child fails closed before the skip.

## AppID 201877 historical evidence boundary
- **Confirmed:** live main run `41944401178`, source SHA `798566d5d6bc5c1ae1956b230b2844c751f35950`, failed with `DLC App_201877 has non-KZT price` after successful HTTP 200 appdetails calls. Earlier code is proven to have conflated absence with foreign currency.
- **Unverified / unknown:** the actual live Steam appdetails JSON field `price_overview` for `AppID 201877`, `cc=kz`, was not retained in that run. Attempts to obtain a narrow direct Steam storefront/API response through the available environment failed; no historical `null`, `{}`, KZT or foreign value is asserted.
- **Synthetic assumption tested, not historical evidence:** `App_201877` is modeled separately with missing, null and empty-object price fields and complete valid identity/parent relationship. These three paths skip; a populated real foreign-price response would still abort the run.
- **STOP guard:** if a later authenticated KZ response for this AppID shows a valid actual KZT price or non-KZT price, do not claim this patch resolves that live observation. Diagnose the exact conflicting response/region/source before any scope expansion.

## Self-review and tests
- Developer review of the actual PR patch confirms no global traversal, no change to shared Appdetails 180 requests/rolling 300-second cap, no change to KZ API params, no scheduler, retry or new semantic worker.
- The **actual GitHub** PR-only `steam-test.yml` regression run `42009071104` on implementation SHA `4b15ef22486d03944f0a2ad776415dbb3ab5bd10` passed: `regression=success`, `collect=skipped` by design. Log says `targeted Steam KZ DLC and independent package 16/16 PASS`; the whole regression suite includes `validate_mailing_policy.py`, `validate_backlog_dispositions.py`, `test_backlog_disposition_validator.py`, production output ownership and other existing scripts.
- Related site task registry workflow `42009071575` passed on the same implementation SHA.
- Final exact-HEAD PR checks must be re-read after this report commit; the final verified run IDs/results will be recorded as a no-code-change PR comment.
- Local full repository tests were unavailable because the local container could not resolve github.com; actual GitHub CI executed the tests instead.

## Residual risks / Director handoff
1. Only an actual current `cc=kz` appdetails response can settle what Steam returned for AppID 201877. Treat the no-price diagnosis as conditional, not observed JSON.
2. All real foreign, conflicting and malformed price structures intentionally continue to abort production; this is a data-integrity barrier, not a retryable error.
3. PR CI is deterministic and does not execute live `collect`. No real Steam → mailing → pre-AI / fresh Dossier binding is yet proven on `main`.
4. Director alone may accept/merge after reviewing exact-final-HEAD required checks and drift; then use the existing normal `Steam KZ production shortlist` run and downstream binding. A new explicit manual live run needs separate authorization if the regular trigger does not occur.

**Worker final:** `IMPLEMENTED_WAITING_DIRECTOR`; source PR remains open and unmerged.
