# Card explanation fix 01 — worker report

Date: 2026-09-01

### Task

Task ID: `card-explanation-fix-01`

Source task: `WORKER_TASK_CARD_EXPLANATION_FIX_01.md`

Scope was limited to the one remaining acceptance defect from `card-explanation-implement-01`:

`Middle-earth™: Shadow of Mordor™: positive lacks explicit personal-taste link`

No broad audit/recon or explanation-system redesign was repeated.

### Root cause

The remaining failure was a small policy/validator wording mismatch, not missing provenance and not a producer-ownership problem.

The canonical generated-output validator requires every visible positive to contain an explicit personal-link marker matching `теб` (`scripts/validate_card_explanations.py`). Two otherwise grounded positive templates in `scripts/card_explanation_policy.py` used wording of the form `...совпадает с твоей любовью...`. That is a personal link semantically, but it does not contain the validator's explicit `теб` marker, so a real generated positive could pass policy/provenance generation and still fail the final bounded acceptance gate.

The fix was systemic rather than game-specific: the affected positive templates were rewritten to use explicit `тебе ...` wording. No title/app-ID special case was added and the validator was not weakened.

### Changes

1. `scripts/card_explanation_policy.py`
   - aligned the affected `multiple_solutions` and `ability_progression` positive wording with the existing explicit personal-link contract;
   - preserved concrete game-specific evidence requirements;
   - preserved fail-closed behavior for weak/generic positives;
   - did not introduce price, discount, rank, score, or eligibility language as Taste rationale;
   - did not change grounded-risk visibility rules or ranking/scoring behavior.

2. `scripts/test_card_explanation_policy.py`
   - added focused regression cases for both affected positive-template variants;
   - verifies each produced positive contains the explicit personal-link marker;
   - existing generic-positive, heuristic-risk, grounded-risk, determinism, and unrelated-field checks remain in place.

Exact fix refs:
- `77a53d6585e58d84d84b20648571196f4788c5d5` — `fix: align positive explanations with personal-link contract`.
- `d2aa975ed71d2f1ec17626266f025b4268c1b1b5` — `test: cover personal-link positive variants`.

Relevant existing implementation/gate refs retained unchanged:
- `353bc86d0814c0a1921689f9ab3f23c55d565fce` — shared grounded card-explanation policy.
- `df67452288a1c37ab56e74bdff797c9760bdfd2b` — canonical final-producer explanation enforcement.
- `7652eae02db7c48bffce4b9cf31e49429af57e8e` — generated-card explanation validator.
- `d40db7ee637e29b40a3c35fb3a343a378d8b1fd8` — canonical workflow explanation gates.

### Validation / workflow run refs

Canonical workflow after the fix:
- workflow: `Build daily visual payload`
- run: `33547075019`
- job: `99987114449`
- head SHA: `d2aa975ed71d2f1ec17626266f025b4268c1b1b5`
- event: `push`
- overall workflow conclusion: `failure` only because the later independent Russian-description gate failed; the scoped card-explanation gates both passed before that failure.

Focused behavioral test result:

`CARD_EXPLANATION_POLICY_TESTS=PASS count=7`

The same canonical run then rebuilt/refreshed the real visual payload in the runner workspace:

`VISUAL_FINAL_BUILD=BUILT mode=deterministic_refresh items_refreshed=442 media_keys=438 package_qualifying=8 package_strict=8 package_equivalence=1 package_touched=19 ai_queue=3`

Real generated top-30 explanation sample:
- command: `python scripts/validate_card_explanations.py data/production/visual/current.json 30`
- path: `data/production/visual/current.json`
- sample size: `30`
- visible positive cards: `3`
- omitted positive cards: `27`
- visible risk cards: `2`
- no visible risk cards: `28`
- violation count: `0`
- validator result: `CARD_EXPLANATION_VALIDATION=PASS`

First five sample titles reported by the validator:
1. `Decarnation`
2. `The Last Soldier of the Ming Dynasty`
3. `Plague Inc: Evolved`
4. `The Black Grimoire: Cursebreaker`
5. `Orbo's Odyssey`

This closes the exact previous real-sample defect: the bounded generated explanation gate now passes with zero violations. No scoped explanation blocker remains.

After the explanation PASS, the workflow continued to the pre-existing Russian-description gate and failed there with `129/433` visible cards not yet having meaningful Russian descriptions (`304` good RU, `129` missing/needs translation). That gate is outside this fix task and is intentionally unchanged; because it occurs after the explanation validator, it does not invalidate the successful real generated explanation sample.

### Status

`complete`

Acceptance for `card-explanation-fix-01` is satisfied:
- `CARD_EXPLANATION_POLICY_TESTS=PASS`;
- real canonical generated top-30 explanation sample: `violation_count=0`;
- `CARD_EXPLANATION_VALIDATION=PASS`;
- no validator weakening or per-game exception;
- no generic fallback praise reintroduced;
- no price/discount/rank-only Taste rationale introduced;
- no unrelated ranking, giveaway, package, duration, translation, or UI behavior intentionally changed.

### Recommended next step

Close `card-explanation-fix-01` as accepted. Continue the separate existing Russian-description/translation track independently; no further card-explanation work is required by this task.

Efficiency / reusable lesson: when producer policy and output validator both encode a semantic invariant, keep their explicit surface marker convention aligned and add regression fixtures for every policy template family that can reach the visible output.