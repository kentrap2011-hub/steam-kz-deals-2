# WORKER TASK — DEEP BALANCED NEGATIVE ASSESSMENT CONTRACT FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `deep-balanced-negative-assessment-contract-fix-01`
Mode: `CONTRACT-FIRST IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/deep-balanced-negative-assessment-contract-fix-01.md`

## Accepted diagnosis

Read and rely on:
`reviews/worker_reports/jedi-deep-missing-negative-evidence-diagnostic-01.md`

Accepted root cause:
`DEEP_PROMPT_OR_CONTRACT_OMISSION`.

The accepted diagnosis proved:

- `game:1172380` / `STAR WARS Jedi: Fallen Order™` has concrete mixed/negative evidence in its accepted Dossier;
- the current Deep `analyzed_fit` result contract has fields for positive evidence and taste factors but no general structured negative/risk assessment;
- the exact accepted Jedi Deep result therefore had no negative/risk field;
- ingest/state persistence did not lose negative data because none was representable in the result;
- downstream PASS 2 projection then generated empty negative arrays;
- the same pattern exists for other authoritative Deep fit games;
- therefore current UI wording can falsely imply that negatives were checked and none existed.

## User-approved product semantics

For a completed Deep analysis, positive fit and negative assessment are separate dimensions.

A completed `analyzed_fit` MUST explicitly evaluate relevant negative/mixed Dossier observations rather than silently omit them.

The Deep negative assessment must distinguish at least these semantic outcomes:

1. **confirmed personal risk**
   - grounded in accepted Dossier evidence;
   - judged personally relevant by Deep;
   - may affect scoring/ranking only through already-existing canonical risk rules/codes;
   - this task must not invent new ranking weights.

2. **grounded caution / trade-off**
   - grounded in accepted Dossier evidence;
   - useful for the user to know;
   - not strong enough or not of a type that should create a ranking penalty under current policy;
   - display-only unless an existing canonical rule already says otherwise.

3. **evaluated: no relevant negative**
   - Deep actually evaluated the relevant negative/mixed candidates and concluded none is personally relevant enough to surface;
   - this is materially different from “negative analysis was never performed”.

4. **negative assessment unresolved / not evaluable**
   - evidence exists but cannot be responsibly classified;
   - must not be presented as “no risks found”.

Historical authoritative Deep results produced under the old contract did NOT perform this balanced negative assessment. They must remain valid for their historical fit decision unless current canonical architecture requires otherwise, but the presentation must not falsely claim that their negatives were evaluated.

## Goal

Extend the canonical Deep contract, worker prompt, result schema, validation, persistence, semantic projection, risk/caution projection and user-visible presentation so:

- future completed Deep results carry a structured grounded negative assessment;
- `analyzed_fit` may contain both positive reasons and negative cautions/risks;
- score-affecting risk remains governed by existing canonical risk policy;
- non-scoring cautions can be displayed without silently becoming penalties;
- an explicit “no relevant negative” state is possible only after negative evaluation;
- old Deep results without the new assessment are presented truthfully as legacy/not-evaluated rather than “confirmed no risks”.

Do not hard-code Jedi-specific findings.

## Parallel-work constraint

НОВЫЙ ЧАТ 1 is concurrently implementing:
`WORKER_TASK_DEEP_POSITIVE_EVIDENCE_CARD_PROJECTION_FIX_01.md`.

Before merge:
- reread fresh `main`;
- preserve all ЧАТ 1 changes;
- reconcile overlapping explanation/risk/card files carefully;
- rerun the relevant shared validation after reconciliation;
- if ЧАТ 1 introduces a semantically conflicting explanation contract, stop with `blocked` and report the exact contradiction rather than overwriting it.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. relevant routes in `PROJECT_ROUTES.md`;
5. accepted diagnostic report above;
6. `PROJECT_DECISIONS.md` relevant Progressive decisions;
7. `config/progressive_pass2_contract.json`;
8. `config/progressive_pass2_worker_prompt.md`;
9. `config/progressive_pass2_result_schema.json`;
10. `config/progressive_personalization_contract.json`;
11. existing grounded-negative / risk contracts;
12. `config/execution_ownership_contract.json`;
13. only the smallest implementation/test/UI files needed.

## Mandatory architecture preflight

Before implementation, prove:

1. GitHub remains owner of Deep scope/order/eligibility/validation/persistence/projection/completeness.
2. Scheduled ChatGPT remains only the bounded semantic data plane returning schema-defined fields.
3. No new scheduler, recurring stage, queue, retry daemon, backlog manager, quota or Scheduled Task change is introduced.
4. Dossier remains neutral evidence and does not decide personalized risk.
5. The existing risk-scoring policy remains the only authority for score penalties.
6. Display-only cautions do not silently become score-affecting risks.
7. Historical completed Deep results are not automatically re-run or invalidated unless a canonical contract rule explicitly requires it.
8. The transition does not cause a global automatic replay of already completed Deep backlog.

If the current canonical decisions are insufficient or encode semantics inconsistent with the user-approved model above, update `PROJECT_DECISIONS.md` FIRST, then contracts, then implementation.

## Contract requirements

Design a structured negative-assessment result for completed Deep outcomes.

Exact field names may follow repository conventions, but the schema must represent:

- overall negative-assessment status:
  - completed;
  - unresolved;
  - legacy/not-evaluated only as a projected compatibility state, not something a new worker should emit as completed work;
- zero or more grounded findings;
- each finding must bind to accepted Dossier evidence/provenance;
- each finding must state whether it is:
  - score-affecting confirmed personal risk under existing policy; or
  - display-only caution/trade-off;
- when completed with no surfaced findings, explicit evidence that negative candidates were evaluated is required;
- unresolved assessment must never normalize to “no confirmed risk”.

Do not permit arbitrary free-form ungrounded negative claims.

The result schema remains fail-closed (`additionalProperties: false` or equivalent strictness).

## Worker prompt requirements

The Deep worker must:

- inspect both favorable and unfavorable/mixed accepted Dossier evidence;
- evaluate negative candidates even when the final fit outcome is `analyzed_fit`;
- not convert every criticism into a personal risk;
- distinguish personal scoring risk from non-scoring caution;
- explicitly return completed-no-relevant-negative only after evaluation;
- return unresolved negative assessment when evidence is insufficient to classify;
- stay bound to the exact frozen Dossier/profile/work authority.

Do not change Deep eligibility or order.

## Persistence / projection requirements

GitHub ingest/state must persist the new structured negative assessment exactly when valid.

PASS 2 semantic projection must no longer manufacture empty negatives for every `analyzed_fit`.

Projection must distinguish:
- new completed negative assessment with confirmed risk(s);
- new completed negative assessment with caution(s) only;
- new completed assessment with no relevant negatives;
- unresolved negative assessment;
- historical old-contract result with no negative assessment.

Historical old-contract `analyzed_fit` must NOT be labeled as proof that no risks exist.

## Visual/UI requirements

The card must present truthful states.

Required behavior:
- confirmed personal risks: visible under risk/minus area; score effects only per existing policy;
- display-only cautions: visible to the user but carry no penalty unless existing policy says otherwise;
- completed no relevant negatives: wording may state that Deep evaluated negatives and found no personally relevant issue;
- unresolved: wording must say the negative assessment is unresolved/not completed;
- legacy old Deep result: wording must say the old Deep result did not evaluate/store negatives under the current contract, rather than “Подтверждённых персональных рисков не найдено”.

Do not make the browser infer these semantics.

## Jedi bounded fixture

Add a bounded fixture/regression based on the already accepted Jedi Dossier characteristics.

It must prove:
- accepted Dossier negative candidates such as divisive backtracking/no-fast-travel friction and EA-app launch/access friction are actually presented to the Deep negative-assessment path;
- a completed Deep fit result can return one or more grounded cautions/risks without changing the positive fit outcome;
- those findings survive schema validation -> ingest/state -> PASS 2 projection -> visual risk/caution preparation;
- whether a particular Jedi observation is scoring or display-only is determined by the explicit Deep result + existing risk policy, not guessed by frontend code.

Do NOT claim a specific Jedi risk as production truth merely from the fixture. The fixture proves the transport/projection contract.

## Historical compatibility regressions

At minimum prove:

1. old authoritative `analyzed_fit` without the new negative-assessment fields remains readable/valid under the migration plan but projects as legacy/not-evaluated, not “no risks found”;
2. new `analyzed_fit` with confirmed scoring risk projects that risk and existing scoring code only;
3. new `analyzed_fit` with display-only caution shows it with zero new penalty;
4. new `analyzed_fit` with completed/no-relevant-negative shows an explicit evaluated-no-risk state;
5. unresolved negative assessment does not become no-risk;
6. malformed/unbound negative finding is rejected fail-closed;
7. `analyzed_not_fit` existing evidence semantics remain valid or are migrated coherently;
8. Fast/cache behavior remains unchanged;
9. positive evidence / fit scores / ranking weights are unchanged except for pre-existing risk policy reacting to genuinely confirmed risk codes;
10. no automatic replay of historical completed Deep work is introduced.

## Production migration rule

This task MUST NOT manually rerun production Deep/Dossier/Fast backlog.

After deployment:
- historical results should immediately stop making the false “risks were checked and none found” claim if they lack the new assessment;
- only future canonically authorized Deep executions may naturally produce the new negative assessment, unless a later separately authorized migration/reanalysis task is created.

Do not create such a migration/reanalysis task yourself.

## Validation

Run relevant:
- schema/contract validation;
- PASS 2 core regressions;
- personalization/risk/card explanation regressions;
- visual/UI regressions;
- execution ownership validation;
- backlog/attempt-accounting validation proving no replay/requeue side effect.

Before merge, refresh against fresh `main` because ЧАТ 1 is active in parallel.

After merge:
- verify normal visual build and Pages deploy if available;
- inspect at least one historical old-contract Deep-fit card and prove its risk wording is truthful legacy/not-evaluated;
- do not manually trigger semantic workers.

## Hard prohibitions

Do not:
- rerun Deep/Dossier/Fast production;
- manually process backlog;
- change Scheduled Task settings;
- add a retry loop or recovery shortcut;
- automatically mark all Dossier negatives as personal risks;
- create new ranking penalties/weights;
- infer semantic negatives in frontend;
- invalidate all historical Deep completions solely to populate the new fields;
- overwrite parallel ЧАТ 1 work.

## Report

Write:
`reviews/worker_reports/deep-balanced-negative-assessment-contract-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Accepted root cause`
4. `Canonical decision / contract model`
5. `Migration model`
6. `Changes`
7. `Parallel reconciliation`
8. `Validation`
9. `Published result`
10. `Historical-result behavior`
11. `Unresolved`
12. `Status`
13. `Recommended next step` — exactly one bounded next step
14. exact PR/commit/run/artifact refs
15. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.
