# Task

Final ACCEPTANCE check for `Steam fixed-package purchase options — verified complete-content valuation` on current `main` (inspected head before report write: `791ed410c6b422d6c4de158981e07f3791131669`). Checked implementation/regression, production pre-AI, downstream comparison/ranking semantics, production visual, Pages deploy, and the deployed package card path for the BioShock control case.

# Verified facts

- Feature implementation is present in commit `80789541b1d3384324beb64ba1fa067f08149eab` (`Value verified DLC and complete content in fixed packages`). Canonical contract: `config/fixed_package_purchase_option_contract.json` v2 stores verified top-level package content across app types, requires exact single-app acquisition evidence for addon value, leaves unknown/unpriced content at zero, and forbids recursive Season Pass/edition expansion.
- Production pre-AI `data/production/pre_ai/fixed_package_options.json` contains `Sub_127633` = `BioShock: The Collection` with the complete verified six-app top-level membership: `8870`, `214933`, `409710`, `409720`, `525720`, `2028850`; no unresolved membership and completeness is true.
- Content typing/evidence for the control case is preserved: `214933` BioShock Infinite - Season Pass = `dlc`, parent `8870`, verified exact single-app route, `662 KZT`; `525720` Minerva's Den Remastered = `dlc`, parent `409720`, no verified standalone route and no invented price; `2028850` Columbia's Finest = `dlc`, parent `8870`, verified exact single-app route, `262 KZT`. `409710` BioShock Remastered is present but nonpersonalized downstream.
- Executed regression confirms verified DLC is not zeroed merely because `type != game`, unpriced verified content remains monetary zero, excluded/noncovered content does not gain personalized value, and addon price is accepted only from an exact single-app purchase Sub.
- The deployed production payload uses the split comparison values for `Sub_127633`: visible covered base-game value `256 RUB`, verified incremental content value `173 RUB`, total comparable value `429 RUB`, package price `265 RUB`, savings `164 RUB` (`38.2%`), `strict_current_price_savings=true`, `comparison_source_aligned=true`.
- Deployed payload keeps all six verified included items. `214933` and `2028850` are counted incremental content; `525720` is explicitly `verified_incremental_content_unpriced` with zero value; `409710` is `verified_included_not_personalized` with zero personalized value.
- Pages deploy artifact `9788326291` contains both `data/current.json` and `package-deal-ui.js`. Rendering the BioShock record with that deployed renderer shows all six Steam items, separately labels Season Pass + Columbia's Finest as counted addon content, Minerva's Den as present but unpriced, BioShock Remastered as included but nonpersonalized, and displays the `256 + 173 = 429 RUB` economics against the `265 RUB` package without misleading value.

# Changes

Feature logic: none.

Acceptance artifact only: created `reviews/worker_reports/package-acceptance-01.md`. `CURRENT_TASK.md` was intentionally left open because the full Definition of Done is not proven.

# Validation

- Pre-AI build run `33476402196`, job `99756472327`, exact feature SHA `80789541b1d3384324beb64ba1fa067f08149eab`: `scripts/test_fixed_package_purchase_options.py` -> `19 passed`; `scripts/test_package_complete_content_value.py` -> `5 passed`; production pre-AI rebuilt successfully and committed as `036eadb261577eae2c6885d5029cd631bd85ad42`.
- Relevant regression files inspected: `scripts/test_package_complete_content_value.py`, `scripts/test_fixed_package_purchase_options.py`.
- Production pre-AI artifact inspected: `data/production/pre_ai/fixed_package_options.json`, package key `Sub_127633`, app keys `8870`, `214933`, `409710`, `409720`, `525720`, `2028850`.
- Visual build run `33476430746`, job `99756553979`, on exact pre-AI SHA `036eadb261577eae2c6885d5029cd631bd85ad42`: package/ranking validation succeeded, production `data/production/visual/current.json` was built, and final visual commit `9aa0aef011bc2e4701f263846faadc5d6f934789` was created.
- Deploy run `33476449000`, job `99756607117`: checked out exact SHA `9aa0aef011bc2e4701f263846faadc5d6f934789`, copied `data/production/visual/current.json` to `web/data/current.json`, uploaded Pages artifact `9788326291`, and Pages reported deployment success for build version `9aa0aef011bc2e4701f263846faadc5d6f934789`.
- Deployed Pages artifact `9788326291` inspected directly; deployed `data/current.json` SHA-256: `a477d7d43e598e9af6a38a2840adf95e5305dbd90a11061fc39635548f2ef5a1`. The BioShock `Sub_127633` rows and deployed `package-deal-ui.js` were exercised locally from this exact artifact.
- Compact current ranking lookup also contains BioShock Infinite and BioShock 2 entries: `data/production/visual/ranking_lookup/b.json`.

# Unresolved

Regression layer: the current Definition of Done explicitly requires a regression proving one entitlement is not double-counted when a Season Pass/edition and recursive constituent DLC overlap. The executed `19 + 5` tests cover DLC valuation, fail-closed unpriced behavior, exact single-app evidence, and nonpersonalized content, but no existing regression inspected constructs the required Season Pass/recursive constituent overlap and asserts single counting. Contract text alone is not an executed regression, so acceptance cannot close.

# Status

needs_fix

# Recommended next step

Issue one IMPLEMENT task limited to adding the missing Season Pass/recursive-constituent double-count regression (without changing product semantics), run the package/pre-AI validation path, then return this same fixed-package task to ACCEPTANCE.
