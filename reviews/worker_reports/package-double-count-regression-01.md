### Task
Implemented `package-double-count-regression-01`: added an executable Season Pass / constituent-content double-count regression through the real package builder -> comparison path. No product semantics were changed.

### Verified facts
- `build_content_catalog` accepts a monetary standalone acquisition price only when the verified fixed Sub acquires exactly that appid.
- The new fixture gives an Example Season Pass its own exact 500 KZT acquisition route, while a constituent DLC has an apparent 500 KZT route that also grants the Season Pass. The constituent therefore remains fail-closed/unpriced instead of receiving a second independent 500 KZT value.
- The downstream comparison verifies the actual final economics: visible base-game value `1000 KZT` + verified incremental content value `500 KZT` = total comparable value `1500 KZT`; against a `1200 KZT` package the calculated savings are `300 KZT`. A naive double count would have produced `2000 KZT` comparable value.
- The existing production implementation already satisfies this regression, so no production-code fix was required.

### Changes
- `scripts/test_package_complete_content_value.py`: added `test_season_pass_constituent_route_is_counted_once_in_comparable_value`; complete-content regression count increased from 5 to 6.
- Production code: none.
- `CURRENT_TASK.md`: recorded this completed worker subtask while intentionally keeping the main fixed-package task open for repeat acceptance.
- The canonical push-trigger workflow performed its normal generated pre-AI refresh; this was not a manual feature-logic change.

### Validation
- Regression commit SHA: `b2680f5740d2a45ea23287c33b2263aafded9b9f`.
- GitHub Actions run `33486496289`, job `99787681615`, exact head SHA `b2680f5740d2a45ea23287c33b2263aafded9b9f`, conclusion `success`.
- `scripts/test_fixed_package_purchase_options.py`: `19 passed`.
- `scripts/test_package_complete_content_value.py`: `6 passed`.
- Canonical workflow-generated pre-AI refresh commit: `e6ba0081d74970338aefa82a25fb68b3b5a09b63`.
- `CURRENT_TASK.md` progress commit: `005646b36c08f3936ad206dc75426fe8444c5b95`.

### Unresolved
No implementation defect remains in this worker scope. The main fixed-package task intentionally remains open because `WORKER_TASK.md` requires a separate repeat acceptance before it can be closed.

### Status
complete

### Recommended next step
repeat fixed-package acceptance
