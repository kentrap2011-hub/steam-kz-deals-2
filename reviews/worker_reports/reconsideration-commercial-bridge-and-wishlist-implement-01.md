# Reconsideration commercial bridge and wishlist implementation 01

## 1. Status

`complete`

Taste Step 3 is repository-side technically complete after an independent owner self-recheck of the task, current `main`, implementation commits, downstream production wiring, regressions, current-data regeneration, Actions history, and temporary one-shot machinery.

This status is **technical implementation completion only**. It does not claim final material Taste acceptance. One fresh independent current Taste Review over the combined Steps 1–3 remains mandatory before the new Taste/wishlist semantics can be accepted as final product behavior.

## 2. Task / bounded scope

Task: `WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md`.

The implemented bridge is strictly post-Taste and commercial. It consumes the already-explicit V5 evidence state and does not mutate Taste fit/evidence state, play role, relative start priority, risk provenance, or final ranking weights.

Exactly two bounded paid eligibility routes are implemented:

### 2.1 `wishlist_good_deal`

Required conditions:

- exact ready V5 `fit_evidence_state=insufficient`;
- Steam wishlist is true;
- the existing moderate commercial scenario is `INCLUDE`;
- the existing purchase decision is exactly `БРАТЬ СЕЙЧАС`;
- all ordinary upstream content/store/sale/symbolic/budget gates still apply.

Effect:

- bypasses only the ordinary weak/insufficient paid eligibility rejection;
- preserves the original `EXCLUDE / below_moderate / insufficient` Taste state;
- does not create `moderate` or `strong` fit;
- does not change play role/start priority;
- does not add a new ranking bonus beyond existing wishlist ranking semantics;
- does not hide warnings/risks.

### 2.2 `reconsiderable_fixed_package_value`

Required conditions:

- exact ready V5 `fit_evidence_state=reconsiderable`;
- the standalone moderate commercial scenario remains `INCLUDE`;
- an existing fixed Steam `Sub_` package is found by the existing package economics;
- current package comparison is source-aligned;
- `strict_current_price_savings=true` under the existing exact/verified purchase-equivalence rules.

Effect:

- may make the purchase commercially reasonable as `МОЖНО БРАТЬ` using the canonical policy bucket for that advice;
- preserves the original `EXCLUDE / below_moderate / reconsiderable` Taste state;
- package value does not create `reconsiderable`, does not create positive Taste fit, and does not alter play role/start priority.

## 3. Canonical good-deal signal

Reused unchanged from the existing deal-quality semantics:

```text
decision_if_moderate disposition == INCLUDE
AND
purchase_decision == "БРАТЬ СЕЙЧАС"
```

No new raw-discount cutoff, percentage threshold, or hidden rescue constant was introduced.

The package bridge purchase decision/bucket is read from canonical `config/mailing_policy.json`; Step 3 no longer duplicates a hidden `PACKAGE_PRIORITY_BUCKET` constant in implementation code.

## 4. Confirmed-negative / direct-conflict protection

Exact V5 `fit_evidence_state=confirmed_negative` is a hard non-overridable block for wishlist, discount, package savings, and all other paid commercial signals. `HighFleet` remains the calibrated non-rescue control.

Step 1 deliberately made the V5 evidence state authoritative. Therefore a legacy `reason_code=exclude_direct_conflict` by itself is **not** proof of a current confirmed conflict:

- an ambiguous legacy row without a ready V5 binding remains fail-closed and cannot use the bridge;
- if exact V5 evidence has classified the row as `reconsiderable` (the BioShock control pattern), the legacy reason does not incorrectly veto the bounded package route;
- an exact V5 `confirmed_negative` / direct confirmed conflict remains non-rescuable.

This distinction is now aligned across implementation code, `PROJECT_RULES.md`, `PROJECT_DECISIONS.md`, and the deal/payload contracts.

## 5. Package / reconsideration behavior

Step 3 reuses the existing fixed-package implementation in `scripts/apply_fixed_package_purchase_options.py`; Step 3 did not alter its purchase-equivalence or value-calculation semantics.

Still preserved:

- fixed Steam `Sub_` route only;
- exact appid coverage or explicit verified purchase-equivalence only;
- no fuzzy/franchise equivalence guessing;
- no fabricated personalized Complete-the-Set price;
- no unauthoritative bundle arithmetic;
- unknown/unpriced extras do not get invented positive value;
- package value cannot create Taste evidence or turn `confirmed_negative` into eligible.

A standalone moderate commercial exclusion remains authoritative even when package evidence exists; the bridge does not bypass ordinary content/store/symbolic/budget commercial exclusions.

## 6. Self-recheck findings and corrections

The owner self-recheck found and fixed two real Step-3 closeout defects that were not visible in the first production probe because current production had zero activatable bridge rows.

### 6.1 Final-refinement wiring gap

`build_visual_feed_v2.py` already preserved the real `below_moderate` fit and explicit bridge provenance. However the canonical final producer later calls `refine_visual_ranking.py`.

Before the closeout fix, that downstream recheck could theoretically:

- promote a bridge row away from its original `below_moderate` fit through fit adjustment;
- overwrite the package bridge's `МОЖНО БРАТЬ` commercial advice with the standalone moderate scenario's `ЛУЧШЕ ЖДАТЬ` advice.

Fixed in commit `69baa039c30c7cbc1f266f2a4395656a2b71fad8`:

- `refine_visual_ranking.py` now revalidates the commercial bridge against the current Taste entry;
- bridge rows preserve original `below_moderate` fit through final refinement;
- bridge-aware commercial recheck uses `commercial_reconsideration_bridge.effective_purchase_fields(...)`;
- `build_final_visual_payload.py` passes the validated bridge through both final fit and commercial rechecks;
- package route warning/risk provenance is preserved.

### 6.2 Legacy reason-code documentation/contract mismatch

Early Step-3 documentation described raw `exclude_direct_conflict` as universally non-rescuable. That contradicted Step-1 V5 semantics for exact `reconsiderable` controls such as BioShock.

The closeout fix makes exact V5 state authoritative and explicitly distinguishes a direct **confirmed** conflict from an ambiguous legacy reason code.

## 7. Files changed for the durable Step-3 implementation

Primary implementation / contract surface:

- `config/mailing_policy.json`;
- `config/deal_quality_contract.json`;
- `scripts/commercial_reconsideration_bridge.py`;
- `scripts/build_pre_ai_chatgpt_payload.py`;
- `scripts/build_visual_feed_v2.py`;
- `scripts/refine_visual_ranking.py`;
- `scripts/build_final_visual_payload.py`;
- `scripts/test_reconsideration_commercial_bridge.py`;
- `scripts/test_fixed_package_purchase_options.py` — the current-production BioShock Collection assertion is availability-aware while deterministic package controls remain strict;
- `scripts/validate_mailing_policy.py`;
- `PROJECT_RULES.md`;
- `PROJECT_DECISIONS.md`;
- `PROJECT_ROUTES.md`.

Explicitly protected / unchanged semantically by the final diff guard:

- `scripts/priority_ranking.py`;
- `config/final_ranking_policy.json`;
- Step-1 V5 result/cache/evidence/ingest contracts and `scripts/taste_evidence_contract.py`;
- Step-2 `scripts/play_priority_context.py` and its contract;
- `scripts/apply_fixed_package_purchase_options.py` package economics;
- `config/purchase_equivalence_overrides.json`;
- giveaway handoff;
- `web/app.js`;
- recurring `.github/workflows/build-daily-visual-payload.yml`.

No second ranker, sorter, semantic scheduler, or recurring Step-3 runtime was added.

## 8. Regression / control results

Final successful closeout run:

- run: `33979912267`;
- job: `101343174589`;
- result: `success`.

Focused Step-3 regression returned `PASS` for all of the following:

- wishlist + canonical good deal + `insufficient` -> bounded eligibility pass;
- wishlist + ordinary deal + `insufficient` -> blocked/no guaranteed override;
- `confirmed_negative` + huge commercial signal -> blocked;
- non-wishlist weak Taste -> unchanged;
- `reconsiderable` + strict fixed-package savings -> purchase-worthy;
- package without strict savings -> blocked;
- package route with standalone commercial exclusion -> blocked;
- BioShock-style exact V5 `reconsiderable` can pass despite ambiguous legacy `exclude_direct_conflict` reason;
- HighFleet remains non-rescuable;
- strong positive control unchanged;
- Step-2 role/start priority invariant to wishlist/discount/bridge;
- wishlist risk warning preserved;
- package risk provenance preserved;
- final refinement preserves `below_moderate` fit and package bridge purchase value.

Additional regressions in the same successful run:

- fixed package purchase-option tests: `19 passed`;
- package complete-content tests: `6 passed`;
- V5 evidence-state tests: `PASS`;
- play-role/start-priority tests: `PASS`;
- Taste V5 contract validation: `PASS`;
- grounded-negative contract: `PASS`;
- card explanation policy: `PASS`, 7 tests;
- priority ranking validation: `PASS`;
- mailing policy: `100` invariants validated;
- Taste semantic digest remained `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`;
- protected-path diff guard: `PASS`;
- `git diff --check`: `PASS`.

## 9. Current production regeneration / comparison

The final successful closeout run regenerated the current production path as far as current semantic dependencies permit.

Current fixed-package producer:

```text
status: complete
apps: 819
packageids_discovered: 970
eligible_fixed_packages: 14
included_content_apps: 71
requests: 21
```

Current pre-AI consumer state:

```text
status: degraded
source_family_count: 803
ai_queue_count: 710
ready_without_ai_count: 0
deterministically_excluded_without_ai_count: 93
complete_family_partition: true
sale_end_coverage: 1.0
sale_end_missing_count: 0
wishlist_entry_count: 90
negative_backfill_queue_count: 531
negative_full_evaluation_queue_count: 179
evidence_backfill_queue_count: 379
commercial_eligibility_bridge_counts: {}
```

Current package-bridge evidence:

```text
status: complete
source_aligned: true
stable_positive_family_count: 516
reconsiderable_candidate_count: 0
strict_savings_candidate_count: 0
bridge_family_ids: []
```

Current intermediate visual producer:

```text
status: degraded
item_count: 523
visible_bridge_counts: {}
```

Canonical final producer:

```text
exit_code: 1
result: EXPECTED_FAIL_CLOSED_DEGRADED_PAYLOAD
message: ChatGPT production payload is not complete
```

This is the correct current production result. The exact current semantic payload still has `379` unresolved V5 evidence-backfill items, and there are `0` exact ready `reconsiderable` package candidates. Therefore the current bridge count `{}` is a legitimate current-data absence, not a wiring failure. The task explicitly forbids manually processing semantic queues or fabricating missing V5 backfill.

Bridge activation through the final production refinement boundary is instead proven deterministically by `scripts/test_reconsideration_commercial_bridge.py`.

Generated runtime files from the closeout probe were not committed.

## 10. Proof Taste / role / risks were not rewritten

- `resolve_bridge(...)` requires an already-ready V5 state and emits an explicit commercial eligibility marker rather than a new Taste verdict.
- bridge metadata declares and tests `taste_state_preserved`, original `below_moderate` fit, role/start preservation, risk/warning preservation, and unchanged ranking weights.
- visual output keeps real `fit=below_moderate` and an explicit `eligibility_override` instead of faking `moderate`.
- final refinement now revalidates the bridge and explicitly preserves the original fit.
- Step-2 role/start tests prove wishlist/sale/commercial invariance.
- package and wishlist warning/provenance preservation are directly covered by focused regression.

## 11. Exact commits / runs

Foundation:

- Step 1: `2a1708ad598ea9baf7095478b646da689eb8f890`, run `33962387867`;
- Step 2: `19ff08128b09b9acb6cbe81f1789e0a5bba294ec`, run `33964033846`.

Step 3:

- primary implementation: `0fddfd3fc58373645bb648348dd5dc013b347eea`;
- primary implementation validation: run `33973214082`, job `101325287657`, `success`;
- first current production probe: commit `685972c2c8a4399a76ac56d7f1ab67f92bd9f3a2`, run `33973331054`, job `101325600995`, `success`;
- final downstream/contract correction: `69baa039c30c7cbc1f266f2a4395656a2b71fad8`;
- final full owner self-check/current production regen: run `33979912267`, job `101343174589`, `success`.

Self-check harness history is retained in Actions for transparency. Earlier runs `33979651202` and `33979849702` stopped on acceptance-harness issues after deterministic/product checks (first: degraded final producer was initially treated too strictly; second: cleanup attempted `git restore` on untracked `web/data/current.json`). Neither failed run pushed the downstream owner fix. The corrected run `33979912267` completed, revalidated after rebase, and pushed `69baa039...`.

Temporary one-shot cleanup commits:

- `7034735bae13b08dc97a7a8f09d71054dd02e5cc` — remove initial patch helper;
- `eb1eb66825310a77d149839ab1290d1042b80cff` — remove implementation one-shot workflow;
- `d878f1bfcf4a9348133163a9fb4fbb70eb00022e` — remove production-probe workflow;
- `79793fcadd470569ea17b572d769fb323fb726b3` — remove invalid self-check workflow;
- `4134e8e33382b99117f2d49b8879644a2c801851` — remove final patch helper;
- `043dff33cd61049b24bc46f88e9cb28ff16d171b` — remove final closeout workflow.

Useful Actions URLs:

- `https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33973214082`
- `https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33973331054`
- `https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/33979912267`

Useful commit URLs:

- `https://github.com/kentrap2011-hub/steam-kz-deals-2/commit/0fddfd3fc58373645bb648348dd5dc013b347eea`
- `https://github.com/kentrap2011-hub/steam-kz-deals-2/commit/69baa039c30c7cbc1f266f2a4395656a2b71fad8`
- `https://github.com/kentrap2011-hub/steam-kz-deals-2/commit/043dff33cd61049b24bc46f88e9cb28ff16d171b`

No persistent Actions artifact is required for acceptance; durable evidence is the committed owner code/tests/contracts, this report, and the cited Actions logs.

## 12. Temporary one-shot cleanup / final repository state

All Step-3 temporary execution machinery has been removed from current `main`:

- `scripts/_taste_step3_once.py` — removed;
- `.github/workflows/taste-step3-implement-once.yml` — removed;
- `.github/workflows/taste-step3-production-probe-once.yml` — removed;
- `.github/workflows/taste-step3-final-selfcheck-once.yml` — removed;
- `scripts/_taste_step3_final_fix_once.py` — removed;
- `.github/workflows/taste-step3-final-fix-valid-once.yml` — removed.

Post-cleanup verification:

- current workflow directory contains no `taste-step3` workflow;
- default-branch code search contains no `_taste_step3` helper;
- durable `scripts/test_reconsideration_commercial_bridge.py` remains;
- no recurring Step-3 scheduler/runtime was introduced.

Current `main` immediately before this durable report commit was `043dff33cd61049b24bc46f88e9cb28ff16d171b`.

## 13. Independent Taste Review requirement

**Mandatory next gate:** one fresh independent current Taste Review must evaluate the combined Steps 1–3 and regenerated controls before Director accepts the new Taste/wishlist semantics as final material product behavior.

Reviewer advice remains advisory and must not auto-write policy.

Repository-side technical Step-3 implementation has no remaining known fix or cleanup tail.

## 14. One bounded next step only

Director should start the single independent current Taste Review over Steps 1–3.

Do not start another Step-3 implementation task unless that independent review identifies a concrete defect.