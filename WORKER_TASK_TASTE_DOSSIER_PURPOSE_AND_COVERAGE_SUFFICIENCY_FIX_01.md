# WORKER TASK — TASTE DOSSIER PURPOSE + COVERAGE SUFFICIENCY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

Task ID: `taste-dossier-purpose-and-coverage-sufficiency-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/taste-dossier-purpose-and-coverage-sufficiency-fix-01.md`

## User-approved decision

The Dossier worker must understand the purpose of its output, not merely collect a few valid facts.

Canonical purpose to encode:

> The Dossier is a neutral evidence package for a downstream semantic worker that will later judge how well the game fits a specific user. The Dossier itself must not personalize, score fit, or use the user's taste profile to select evidence. Its responsibility is to give the downstream worker a sufficiently complete, balanced, evidence-grounded picture of the actual game experience so that a later personalized judgment is reasonably possible.

Priority rule:

> Completeness and downstream usefulness of the game picture are more important than speed of obtaining the Dossier. Throughput/latency must not justify stopping while material, reasonably discoverable aspects of the game experience remain uncovered.

This does NOT mean exhaustive or unbounded research. Boundedness remains semantic/adaptive and runtime-safe. The worker must stop when the picture is sufficiently complete for downstream analysis, when remaining materially distinct required/promising routes are exhausted, or when a directly observed runtime/tool/liveness blocker prevents safe continuation.

## Proven diagnostic basis

Accepted report:
`reviews/worker_reports/progressive-deep-insufficient-evidence-diagnostic-01.md`

Accepted dominant root cause:
`DOSSIER_TOO_THIN`

Proven sample findings:
- 8/8 sampled current Deep `analysis_incomplete / insufficient_evidence` outcomes were justified when reviewed only against their exact canonical Dossier inputs;
- all 8 sampled incomplete Dossiers were `overall_strength=limited`, had only 1–2 observations, and several covered only one narrow topic;
- additional exact-product, decision-relevant player evidence was readily discoverable for all 8 in bounded diagnostic checks;
- 4 successful Deep `not_fit` controls proved compact Dossiers can be sufficient when their evidence is genuinely decisive;
- therefore the fix must improve semantic coverage/sufficiency, NOT impose a dumb minimum review/source quota and NOT weaken Deep first.

Extreme regression example:
- appid `1244460` / Jurassic World Evolution 2 had an accepted Dossier whose useful observation was effectively localization/menu selection, yet it was marked `research_state:"sufficient"` + `stop_reason:"evidence_stable"`.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Read current, minimally:
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- current Dossier semantic schema / strict validator / focused tests
- `reviews/worker_reports/progressive-deep-insufficient-evidence-diagnostic-01.md`
- `reviews/worker_reports/taste-dossier-semantic-bounded-retrieval-01.md` as needed to preserve the no-fixed-numeric-limit design.

Do not perform broad repository archaeology.

## Architecture preflight — fixed decisions

Before editing verify:

1. GitHub remains owner of Dossier scope/order, binding, validation, persistence, first-pass/recovery state and completeness.
2. Scheduled ChatGPT remains bounded neutral evidence generation + create-only transport only.
3. The Dossier remains profile-agnostic and must not read/use the user's taste profile to decide which evidence is favorable or unfavorable.
4. Deep remains the personalized semantic stage.
5. No new scheduler, queue, retry daemon, backlog manager, quota or second Dossier producer is introduced.
6. No fixed minimum number of reviews, sources, searches or pages is introduced.
7. Existing exact-product identity, Russian-evidence, temporal/freshness, privacy/provenance and create-only rules remain strict.
8. Existing semantic/adaptive boundedness remains; the fix changes what qualifies as sufficiently complete/stable, not whether research is bounded.
9. No Scheduled Task create/update/enable/disable/pause/delete/reschedule/rename/recreate/run action is authorized.
10. No automatic recovery of existing Deep/Dossier failures is authorized by this task.

If any required implementation would violate these fixed decisions, stop and report instead of broadening scope.

## IMPLEMENT

### FIX-01 — encode the Dossier's downstream purpose

Update the smallest canonical generator-facing contract/prompt surfaces so the worker explicitly understands:

- it is preparing evidence for a later personalized analysis by another worker;
- it must remain neutral and profile-agnostic;
- its output must describe the game experience broadly enough that the downstream worker can later evaluate fit;
- collecting one valid fact is not equivalent to completing the Dossier;
- a narrow observation may be useful evidence but cannot by itself justify `research_state:"sufficient"` unless it is genuinely decisive about the overall game experience or remaining material dimensions are reasonably unavailable/exhausted.

The wording must not encourage profile-targeted evidence cherry-picking.

### FIX-02 — completeness over speed

Make explicit in the active Dossier worker rules:

- semantic completeness / downstream usefulness has priority over throughput, speed, or minimizing tool calls;
- the worker must not stop merely because it already has a valid observation, a valid Russian item, or one usable source;
- ordinary latency or desire to process more games in the invocation is not a semantic reason to declare `evidence_stable`;
- while the binding remains live and runtime/tooling safely permits, continue through materially useful distinct player-feedback routes when material game-experience dimensions are still sparse.

Do NOT make this unbounded. Preserve safe runtime stopping and exact fail-closed behavior.

### FIX-03 — mandatory neutral coverage check before `sufficient/evidence_stable`

Before the worker may emit:
- `research_state:"sufficient"`
- and/or `stop_reason:"evidence_stable"`

require an explicit structured neutral coverage check over the observations intended for serialization.

The check should ask whether the Dossier gives a sufficiently complete and balanced picture of the actual player experience.

Material dimensions should include, when relevant and reasonably discoverable:
- core play loop / mechanics;
- controls / game feel where player feedback makes this material;
- progression / development / unlock structure;
- variety versus repetition over time;
- difficulty / mastery / learning / friction;
- pacing / structure / direction;
- exploration / mission/activity structure where relevant;
- multiplayer/co-op dependence where relevant;
- story/characters/identity hooks where materially part of the experience;
- recurring strengths;
- recurring complaints/downsides;
- current technical/performance/localization/regional issues when material.

These are coverage dimensions, NOT a checklist requiring one observation in every category for every game.

A Dossier may still be compact when:
- one or two observations directly and credibly characterize the central/core experience strongly enough that more research is unlikely to materially change the neutral picture; or
- remaining applicable dimensions are genuinely not reasonably discoverable after required materially distinct routes are exhausted.

### FIX-04 — narrow-topic anti-stop rule

Do not allow `evidence_stable` when the current evidence is only a narrow/nonrepresentative slice such as:
- localization/menu language only;
- generic social enjoyment only;
- one descriptive mechanic with no sustained-experience context;
- one isolated complaint with no corroboration when broader exact-product evidence is readily discoverable;
- aggregate sentiment without concrete player-experience content.

When that happens and materially distinct player-feedback routes remain reasonably discoverable, continue research.

### FIX-05 — balanced picture, not only negatives

Ensure the worker seeks a neutral picture containing both:
- meaningful strengths / positive characteristics when reasonably evidenced;
- meaningful weaknesses / recurring complaints / trade-offs when reasonably evidenced.

Do not require artificial “one pro + one con” symmetry when the evidence genuinely leans one way. The requirement is balanced investigation, not fabricated balance.

### FIX-06 — stop semantics

Preserve:
- `evidence_stable` for genuinely sufficient neutral coverage;
- exhausted/unresolved/fail-closed behavior when critical material coverage remains missing after all required materially distinct routes are exhausted;
- directly observed runtime/tool/liveness blockers as safe stop reasons where current contracts already allow them.

Do not call sparse evidence “stable” merely because no contradiction has yet been found.

### FIX-07 — machine-readable / validator alignment where appropriate

Inspect whether the current schema/strict validator can distinguish:
- genuine sufficient coverage,
- narrow sparse evidence incorrectly marked stable.

If generator-facing prompt/contract changes alone cannot prevent the proven defect, add the smallest machine-readable coverage attestation needed so strict validation can reject a plainly narrow `sufficient/evidence_stable` dossier.

Do not add a profile-scoped score or arbitrary numeric completeness score.

Prefer a compact structured coverage summary using neutral dimensions / covered vs materially-unresolved state only if necessary.

Do not weaken strict validation.

## VALIDATION

Add focused regression coverage proving at least:

### Proven failure cases

- COV-01 — Jurassic World Evolution 2 / appid 1244460:
  localization/menu-only evidence cannot be accepted as `sufficient/evidence_stable` while ordinary exact-product player-experience evidence remains reasonably discoverable.

- COV-02 — Rubber Bandits / appid 1206610:
  generic “fun with friends” evidence alone cannot close research while sustained variety/repetition remains materially unknown and discoverable.

- COV-03 — Retrowave / appid 1239690:
  one anecdotal repetition complaint cannot be called stable while readily discoverable corroborating variation/driving evidence remains.

- COV-04 — Terraformers / appid 1244800:
  one descriptive core-loop anecdote cannot close research before available long-horizon progression/variety evidence is considered or routes are exhausted.

- COV-05 — FINAL FANTASY VI / appid 1173820:
  Dossier must capture or explicitly exhaust reasonably discoverable evidence on combat/progression/variety/pacing rather than stopping on story/party/slow-opening alone.

- COV-06 — Severed Steel / appid 1227690, Need for Speed Heat / 1222680, Scars Above / 1196090:
  preserve exact-product identity while broadening material game-experience coverage beyond the narrow initial slice.

### Compact-success controls

- COV-07 — Lake / appid 1118240:
  compact evidence may still be sufficient when it directly characterizes the central core loop and the resulting neutral picture is genuinely decision-ready.

- COV-08 — Potion Craft / appid 1210320:
  compact evidence may still be sufficient when it directly captures a recurrent long-horizon progression/repetition property.

These controls must prove the fix is semantic, not a minimum-count quota.

### Architecture / invariants

- COV-09 — no minimum number of sources/reviews/searches/pages is introduced.
- COV-10 — Dossier remains profile-agnostic and contains no personalized fit judgment.
- COV-11 — Russian retrieval/provenance/privacy/exact-product rules remain strict.
- COV-12 — temporal completeness behavior remains intact.
- COV-13 — no new scheduler/queue/retry/backlog owner.
- COV-14 — existing normal buffered traversal and GitHub-owned persistence/recovery remain unchanged.
- COV-15 — completeness-over-speed wording cannot be interpreted as unbounded crawling; semantic/adaptive boundedness remains explicit.

Run all relevant current Dossier focused regressions/workflows. Do not weaken tests merely to make them green.

## Production boundary

Do NOT:
- manually rerun real failed Dossiers;
- authorize Dossier recovery;
- authorize Deep recovery;
- manually process Deep backlog;
- change/run the Scheduled Task.

Normal external production may continue independently unless the existing canonical task explicitly requires otherwise. Natural concurrent activity may be observed but is not required for implementation acceptance.

## Durable rationale

If this changes a non-obvious semantic rule, add/update the appropriate `PROJECT_DECISIONS.md` entry explaining:

- Dossier exists to support a later personalized decision while remaining itself neutral;
- semantic coverage/completeness is more important than throughput;
- compact decisive Dossiers remain valid;
- no fixed numeric quota is introduced;
- `evidence_stable` means “sufficiently complete neutral picture,” not “we found at least one valid fact.”

Update `PROJECT_ROUTES.md` only if the operational route would otherwise be stale.

## Durable report

Commit:
`reviews/worker_reports/taste-dossier-purpose-and-coverage-sufficiency-fix-01.md`

Required sections:
1. Final status
2. Architecture preflight
3. Proven defect
4. Purpose wording added
5. Completeness-over-speed rule
6. Coverage-check design
7. Narrow-topic anti-stop behavior
8. Validator/schema changes, if any
9. Files changed
10. Tests/workflows with exact refs
11. COV-01..COV-15 results
12. Natural production observations, if any
13. Unresolved
14. Director recommendation

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_user_decision`

Before completion:
- commit the final durable report to `main`;
- reread that exact committed report from fresh `main`;
- do not modify it after the reread unless repeating final commit+reread closeout.
