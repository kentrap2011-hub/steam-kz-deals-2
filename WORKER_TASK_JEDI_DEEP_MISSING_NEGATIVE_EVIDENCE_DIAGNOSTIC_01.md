# WORKER TASK — JEDI DEEP MISSING NEGATIVE EVIDENCE DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `jedi-deep-missing-negative-evidence-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/jedi-deep-missing-negative-evidence-diagnostic-01.md`

## User question

For `game:1172380` / `STAR WARS Jedi: Fallen Order™`, the current authoritative Deep result says the game fits strongly, but the published card says:

- `Подтверждённых персональных рисков не найдено`;
- `Риск пока не подготовлен`.

The user wants a separate investigation of **why Deep produced no negative/risk findings at all**, not an immediate fix.

## Goal

Determine whether the absence of negatives is:
1. correct because the accepted evidence genuinely contains no relevant negative signal for the user's profile;
2. caused by the Deep semantic contract/prompt not requiring balanced positive + negative evaluation;
3. caused by relevant negative evidence existing in the accepted Dossier but being ignored by Deep;
4. caused by Deep producing negative evidence that ingest/state persistence drops;
5. caused by canonical Deep state containing negative evidence that the visual/risk mapper drops;
6. caused by another exact proven boundary.

Do not change anything except the required report.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. relevant Fast/Dossier/Deep and grounded-risk routes in `PROJECT_ROUTES.md`;
5. current Deep contract and worker prompt;
6. current accepted Deep state plus exact accepted result/transport record for `game:1172380`;
7. exact accepted Dossier content and provenance bound to that Deep result;
8. current visual item/risk fields for `game:1172380`;
9. exact ingest/state projection and risk-mapping contracts only as needed to locate the boundary.

Use current repository truth. Do not rely on remembered conclusions.

## Required evidence comparison

For `game:1172380`, build a factual chain:

`accepted Dossier evidence`
→ `Deep worker input requirements`
→ `exact Deep result submitted`
→ `accepted PASS 2 state`
→ `visual/risk projection`
→ `published card`.

At every boundary state explicitly whether negative/risk information exists and in what form.

Inspect the accepted Dossier for concrete negative player-feedback observations relevant to likely personal risks such as repetition, backtracking, combat friction, pacing, exploration friction, difficulty, technical problems, or other contract-defined categories. Do not invent a risk merely because a game is known to have criticism.

If the Dossier contains relevant negative observations, determine whether the Deep prompt/result considered them.

If it contains none, determine whether that is because the Dossier evidence itself did not surface any, without re-running or changing Dossier.

## Bounded control sample

Use at most 2–3 additional current authoritative Deep `analyzed_fit` games as controls if necessary to determine whether:
- Deep fit results normally include negative/risk findings;
- `game:1172380` is an isolated evidence case;
- the entire current Deep path systematically omits negatives.

Do not perform repository-wide manual semantic analysis.

## Important distinction

Do not treat “no risk penalty in ranking” and “no textual negative evidence” as automatically equivalent.

Determine separately:
- whether Deep semantic output contains negative/risk evidence;
- whether risk mapper considers it rank-affecting;
- whether UI is allowed to show neutral/non-scoring cautions.

## Hard prohibitions

Do not:
- implement a fix;
- edit contracts/prompts/runtime;
- change Dossier or Deep state;
- rerun Deep/Dossier/Fast;
- manually process backlog;
- change Scheduled Tasks;
- use general web research as a substitute for inspecting the exact accepted Dossier/result chain;
- declare that the game has no drawbacks merely because current UI shows none.

Only the report may be written.

## Report

Write:
`reviews/worker_reports/jedi-deep-missing-negative-evidence-diagnostic-01.md`

Required sections:
1. `Task`
2. `Verified chain`
3. `Dossier negative evidence`
4. `Deep prompt/result behavior`
5. `State persistence`
6. `Visual/risk projection`
7. `Control sample`
8. `Root cause`
9. `User-visible interpretation`
10. `Changes` — report only
11. `Unresolved`
12. `Status`
13. `Recommended next step` — exactly one bounded next step
14. exact file/result/commit refs
15. `Efficiency / reusable lesson`

Allowed conclusion labels:
- `NO_RELEVANT_NEGATIVE_EVIDENCE_IN_ACCEPTED_DOSSIER`
- `DEEP_PROMPT_OR_CONTRACT_OMISSION`
- `DEEP_SEMANTIC_OMISSION_DESPITE_EVIDENCE`
- `INGEST_OR_STATE_DROPS_NEGATIVE_EVIDENCE`
- `VISUAL_RISK_PROJECTION_DROPS_NEGATIVE_EVIDENCE`
- `MULTIPLE_BOUNDARIES`
- `UNDETERMINED`

Allowed final statuses:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.
