# WORKER TASK — CHAT 2

Task ID: `card-explanation-implement-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/card-explanation-implement-01.md`

## Goal

Fix the explanation-quality defects proven by `card-explanation-audit-01` without re-running the audit.

The current audit found:
- 0/30 sampled positive rationales were fully game-specific (`game fact/system/situation -> personal taste link`);
- 11/30 used the generic positive fallback `Игра прошла строгий вкусовой отбор...`;
- 13/30 showed a negative `risks[]` bullet despite `risk_codes=[]` and `risk_status.has_described_risk=false`;
- price/discount/rank must not be used as positive Taste rationale;
- heuristic risk codes alone are not enough for player-facing risk without grounded provenance.

## Read first

- `reviews/worker_reports/card-explanation-audit-01.md`
- `CHAT_PROTOCOL.md`
- relevant `KNOWN_WORKER_PITFALLS.md` entries only if trigger matches
- `config/execution_ownership_contract.json`
- current canonical visual/feed producer paths named by the audit
- the exact current producer/artifact binding used by production before editing

Do not perform broad history/code archaeology.

## Architecture preflight

Before editing, confirm the exact current canonical producer ownership for:
- visible positive `games[].why_fit[]`;
- visible negative `games[].risks[]` plus `risk_codes` / `risk_status`.

The prior audit identified:
- positive producer route around `scripts/build_visual_feed_v2.py::reason_ru()`;
- final negative producer route around `scripts/build_final_visual_payload.py::refine_games_from_signals()` and `scripts/refine_visual_ranking.py`.

Treat those as audit evidence, not as permission to edit stale paths blindly. Bind to the current canonical producer version first.

## Required behavior

### 1. Positive explanation quality

Replace broad fixed-template/fallback output with a deterministic explanation route that produces player-facing reasons grounded in **specific facts about the game** and explicitly links those facts to the user's established taste/profile evidence.

A valid reason must have both:
1. concrete game-specific fact/system/situation/content evidence;
2. explicit personal-taste connection explaining why that fact matters for this user.

Examples of structure only, not text to copy:
- specific mechanic/system -> matches known preference for X;
- specific pacing/structure -> fits known preference/avoidance;
- specific genre/subgenre feature -> linked to profile evidence.

Do not use:
- generic "passed taste filter" filler;
- score/rank alone;
- price/discount as Taste evidence;
- store popularity alone.

If there is not enough grounded evidence to make a game-specific positive reason, fail closed to a compact neutral/no-explanation state rather than emit generic praise.

### 2. Negative explanation consistency

When:
- `risk_codes=[]`, and
- `risk_status.has_described_risk=false`,

then visible player-facing `risks[]` must be empty / absent. Do not emit filler such as "явных рисков не найдено" inside the negative-risk block.

A visible risk must have:
- a meaningful risk code/status;
- grounded player-facing description;
- provenance/evidence sufficient under current contract.

Heuristic-only suspicion without required grounding must not become a definitive negative bullet.

### 3. Preserve separation of concerns

- Taste explanation must not be improved by zero price, discount size, rank, or deal score.
- Deal quality may remain visible in its own price/deal context.
- Ranking score may corroborate selection but cannot substitute for explanation.
- Do not change paid ranking weights, wishlist rules, giveaway logic, duration, translation or package behavior.

### 4. Contract / payload consistency

If the current payload contract cannot represent the needed grounded explanation cleanly, make the smallest versioned contract change owned by the canonical producer.

Do not create a second explanation writer.
Do not hand-edit production payloads.

## Validation

Use behavioral/output checks, not source-shape proxies.

Add or update deterministic tests covering at least:
- a game with strong specific positive evidence -> one or more game-specific reasons;
- a game with only generic eligibility/score -> no generic praise fallback;
- price/discount/rank alone cannot generate a positive Taste reason;
- `risk_codes=[]` + `has_described_risk=false` -> no visible negative block;
- grounded real risk -> visible risk preserved;
- heuristic/ungrounded risk -> not promoted to definitive player-facing bullet;
- existing unrelated card fields remain intact.

Then rebuild the smallest canonical visual production path needed to inspect a bounded real sample.

Acceptance gate for the bounded sample:
- no exact generic fallback `Игра прошла строгий вкусовой отбор...`;
- every visible positive reason is game-specific and linked to personal taste evidence;
- no negative bullet exists where the risk status says no described risk;
- no price/discount/rank-only positive rationale.

Do not claim full production acceptance from source code alone; validate generated output.

## Hard boundaries

Do NOT:
- repeat `card-explanation-audit-01`;
- redesign the whole Taste model;
- change ranking weights or eligibility;
- add external semantic/runtime queues unless existing canonical architecture explicitly authorizes them;
- manually write per-game explanations item-by-item;
- use price/discount/free status as Taste fit;
- weaken risk provenance requirements;
- change giveaway/UI/package/duration/translation tracks outside the smallest necessary explanation producer contract.

## Done when

- generic positive fallback is removed from generated player-facing explanations;
- visible positive reasons are grounded and game-specific or omitted fail-closed;
- no-risk entries produce no negative-risk bullet;
- grounded risks still render correctly;
- deterministic behavioral tests pass;
- a bounded real generated sample passes the explanation quality gate;
- no unrelated ranking/product behavior changed.

## Report format

Save:
`reviews/worker_reports/card-explanation-implement-01.md`

### Task
What changed.

### Producer / ownership
Exact canonical producer paths and any contract version change.

### Changes
Exact files/commits.

### Validation
Tests plus bounded generated-output sample results.

### Remaining limitations
Only real unresolved evidence/architecture limits.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only; `none` is valid if complete.

Final response must include report path and exact commit refs.