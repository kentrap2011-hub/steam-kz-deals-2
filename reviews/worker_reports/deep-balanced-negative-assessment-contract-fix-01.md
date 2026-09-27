# Deep balanced negative assessment contract fix 01

## 1. Task

- Task: `WORKER_TASK_DEEP_BALANCED_NEGATIVE_ASSESSMENT_CONTRACT_FIX_01.md`.
- Mode: contract-first implement / validate.
- Worker slot: ЧАТ 2.
- Repository: `kentrap2011-hub/steam-kz-deals-2`, source of truth `main`.
- Goal completed: new completed Deep results now carry an explicit grounded negative assessment; scoring risks and display-only cautions are separated; historical old-contract Deep results no longer imply that negatives were checked.
- No production Deep/Dossier/Fast semantic rerun, manual backlog processing, Scheduled Task mutation, new scheduler, retry loop, or ranking-weight change was used.

## 2. Architecture preflight

Preflight passed before implementation and remained true after merge:

- GitHub remains owner of Deep scope, order, eligibility, exact Dossier binding, validation, persistence, projection, attempt accounting, completeness, publication and recovery authorization.
- Scheduled ChatGPT remains the bounded semantic data plane and may only return schema-defined fields for already-authorized work.
- Dossier remains neutral evidence preparation; it does not decide personalized risk.
- Existing canonical risk codes and `config/final_ranking_policy.json` remain the only score-penalty authority.
- A `caution` is display-only and has `risk_code: null`; it does not enter score by itself.
- Historical Deep completions are not invalidated, requeued or automatically replayed to backfill the new field.
- `config/execution_ownership_contract.json` was not changed.
- The bounded regression `scripts/test_deep_balanced_negative_assessment.py` explicitly asserts GitHub control-plane ownership, external scheduler ownership and the existing no-blind-retry prohibition.

## 3. Accepted root cause

Accepted diagnosis: `DEEP_PROMPT_OR_CONTRACT_OMISSION`.

The accepted Jedi diagnostic proved that the accepted Dossier for `game:1172380` contained concrete mixed/negative material, including backtracking/no-fast-travel friction, EA application launch/access friction and a divisive backtracking conflict. The old Deep `analyzed_fit` result had no general structured negative-assessment field, so no such assessment could survive ingest. Downstream projection therefore created empty negative arrays and the old card wording incorrectly implied that no personal risks had been found.

No persistence-loss defect was found: the old result simply could not represent the assessment.

## 4. Canonical decision / contract model

Added canonical decision `PROJECT_DECISIONS.md#PPD-009`.

For every new completed `analyzed_fit` or `analyzed_not_fit` result:

- Deep must evaluate every negative/mixed Dossier observation plus every Dossier conflict from the exact accepted immutable Dossier.
- `negative_assessment.status = completed` is allowed only after that exact candidate set is explicitly covered.
- A `confirmed_personal_risk` must be grounded in exact Dossier refs and use an already-existing canonical risk code; only the existing risk policy can turn it into a score penalty.
- A `caution` is grounded user-visible friction/trade-off, uses `risk_code: null`, and creates no new score penalty.
- Completed evaluation may have zero surfaced findings only after the whole candidate set was actually evaluated.
- `unresolved` means material negative/mixed evidence could not be responsibly classified; it is never interpreted as “no risk”.
- The worker cannot emit the compatibility state `legacy_not_evaluated`; that projection belongs to GitHub.

The structured schema is fail-closed for finding shape, disposition, existing risk code and exact observation/conflict references.

## 5. Migration model

Historical authoritative Deep completions produced before PPD-009 remain valid for their historical fit/not-fit decision.

If such an accepted Deep entry lacks `negative_assessment`:

- GitHub projects `negative_assessment_status = legacy_not_evaluated`;
- the visible status says `В старом Deep-разборе минусы отдельно не оценивались`;
- it is not converted to evaluated-no-risk;
- no attempt is consumed;
- no automatic replay, requeue, invalidation or recovery authorization is created.

Only future naturally and canonically authorized Deep executions can produce the new assessment unless a separate future migration/reanalysis task is explicitly authorized.

## 6. Changes

Canonical/contracts:
- `PROJECT_DECISIONS.md` — PPD-009.
- `PROJECT_ROUTES.md` — rediscovery route for the balanced negative path.
- `config/progressive_pass2_contract.json` — completed Deep negative-assessment contract and legacy projection.
- `config/progressive_pass2_result_schema.json` — strict negative assessment/ref/finding schema.
- `config/progressive_pass2_worker_prompt.md` — mandatory balanced negative evaluation rules.
- `config/progressive_personalization_contract.json` — producer-owned presentation states.

Runtime/persistence:
- `scripts/ingest_progressive_pass2.py` binds validation to the exact frozen Dossier bytes/SHA.
- `scripts/progressive_pass2.py` validates candidate refs, persists the assessment for normal/recovery accepted results and projects confirmed risk/caution/no-relevant-negative/unresolved/legacy states.
- `scripts/refine_visual_ranking.py` permits only explicit confirmed Deep personal risks into the existing risk-code path.
- `scripts/card_explanation_policy.py` projects display-only Deep cautions separately and preserves exact provenance.
- `scripts/build_final_visual_payload.py` publishes cautions and producer-owned negative status.
- `scripts/priority_ranking.py` renders truthful non-scoring caution/evaluated/unresolved/legacy statuses while preserving existing risk scoring.
- `scripts/validate_card_explanations.py` fail-closes malformed/unbound Deep risk/caution presentation.
- `.github/workflows/deploy-visual.yml` protects the new producer-owned semantic fields during bounded commercial refresh.

UI:
- `web/index.html` / `web/app.js` render producer-owned cautions; the browser does not classify negative-assessment states or infer scoring.

Regression:
- added `scripts/test_deep_balanced_negative_assessment.py`;
- adapted existing synthetic PASS 2 fixtures to exact bound-Dossier validation;
- wired the new regression into `Validate Progressive PASS 2 core`.

## 7. Parallel reconciliation

Before implementation and immediately before merge, fresh `main` was reread. The final pre-merge base was `2c8d78b2d9ff948682986fb3f2f983e850b6ddd0` (`Accept Deep positive evidence card projection fix`), and the implementation branch was `behind_by=0`.

Overlapping ЧАТ 1 files were explicitly reread, including `scripts/card_explanation_policy.py` and `scripts/build_final_visual_payload.py`. The already-merged positive-evidence policy/binding was preserved.

Post-deploy verification proves the preservation: the Jedi card still contains the two grounded Russian `Почему может зайти` reasons and exact Deep semantic provenance while also using the new truthful legacy negative status.

## 8. Validation

PR #107 validation, head `6cd462f499f2e8b64df796daa9c2b51ea48d9b35`:
- `Validate Progressive PASS 2 core` run `36345232462` / #254 — success.
  - Python compilation — success.
  - async traversal + invalid transport — success.
  - frozen-start regression — success.
  - PASS 2 core — success.
  - PASS 2 Dossier integration — success.
  - **Deep balanced negative assessment regression** — success.
  - PASS 1 and Progressive personalization regressions — success.
  - UI provenance — success.
  - recomputation without consuming attempts — success.
- `Validate backlog dispositions` run `36345232394` / #1324 — success.
- `Validate package purchase value` run `36345232475` / #24 — success, including full priority ranking and browser JavaScript syntax.

The bounded Jedi regression proves:
- exact accepted Dossier candidate refs enter the negative path;
- caution-only fit survives result -> validation -> state -> semantic projection -> visual with zero new penalty;
- confirmed risk uses an existing risk code/policy only;
- evaluated-no-relevant-negative is accepted only after full candidate evaluation;
- unresolved never becomes no-risk;
- old analyzed_fit without the field becomes `legacy_not_evaluated`;
- malformed or unbound evidence is rejected with zero attempt;
- `analyzed_not_fit` confirmed-personal-negative requires a confirmed risk;
- non-Deep legacy/Fast mapping remains intact;
- frontend remains presentation-only;
- GitHub/external-scheduler ownership boundary remains intact.

Post-merge validation:
- PASS 2 run `36345297259` / #255 — success.
- backlog dispositions run `36345297060` / #1325 — success.
- no semantic worker was manually triggered.

## 9. Published result

Implementation PR `#107` merged as `54591936f1c31c9cf974a222296913def746e6d5`.

Normal full visual publication:
- `Build daily visual payload` run `36345297171` / #819 — success.
- full Progressive build selected; bounded commercial/giveaway refresh paths in that run were skipped.
- generated visual commit: `d33c74f5d7df21ec6dd38d8a3f896c0d91704a75`.
- all card-explanation and generated-card validators passed.
- following Pages deploy run `36345333429` / #860 — success.
- directly inspected Pages artifact: `10939999664`.

A later normal bounded commercial refresh produced `f37f06ce6218e35084bf56c4e6e9748123c11366` and preserved the semantic fields. Latest following deploy:
- `Deploy visual mailing` run `36345366969` / #861 — success.
- directly inspected Pages artifact: `10939738733`.

## 10. Historical-result behavior

Direct inspection of the latest deployed Pages artifact `10939738733` for `game:1172380` / `STAR WARS Jedi: Fallen Order™` shows:

- effective analysis source: `deep`;
- fit: `strong`;
- `negative_assessment_status: legacy_not_evaluated`;
- `risk_status.code: legacy_negative_not_evaluated`;
- label: `В старом Deep-разборе минусы отдельно не оценивались`;
- `cautions: []`;
- no risk score penalty was invented;
- rank remains `1`;
- total score remains `68.6`;
- personal score remains `43.6`;
- purchase score remains `25.0`;
- both ЧАТ 1 grounded positive reasons remain present.

Therefore the historical old-contract Deep card is truthful: it says negatives were not separately assessed instead of claiming that a completed negative check found nothing.

## 11. Unresolved

No blocker remains within this task.

Historical old-contract Deep results intentionally remain `legacy_not_evaluated` until a future naturally authorized Deep execution or a separately authorized future migration/reanalysis task. This is the migration design, not an unresolved defect.

## 12. Status

`complete_ready_for_director_acceptance`

## 13. Recommended next step

Director: accept this task as complete; do not create or trigger a historical Deep backfill from this closeout.

## 14. Exact PR/commit/run/artifact refs

- Implementation PR: `#107` — `Add balanced Deep negative assessment contract`.
- PR head validated: `6cd462f499f2e8b64df796daa9c2b51ea48d9b35`.
- Fresh pre-merge main / preserved ЧАТ 1 base: `2c8d78b2d9ff948682986fb3f2f983e850b6ddd0`.
- Implementation merge: `54591936f1c31c9cf974a222296913def746e6d5`.
- Visual commit: `d33c74f5d7df21ec6dd38d8a3f896c0d91704a75`.
- Later preserved commercial visual commit: `f37f06ce6218e35084bf56c4e6e9748123c11366`.
- PR PASS 2: run `36345232462` / #254.
- PR backlog: run `36345232394` / #1324.
- PR ranking/package/UI: run `36345232475` / #24.
- Post-merge PASS 2: run `36345297259` / #255.
- Post-merge backlog: run `36345297060` / #1325.
- Normal visual: run `36345297171` / #819.
- Following deploy: run `36345333429` / #860, artifact `10939999664`.
- Latest preserved deploy: run `36345366969` / #861, artifact `10939738733`.
- Canonical decision: `PROJECT_DECISIONS.md#PPD-009`.
- Main bounded regression: `scripts/test_deep_balanced_negative_assessment.py`.

## 15. Efficiency / reusable lesson

The reusable improvement is the dedicated contract-level regression that starts from a real accepted Jedi Dossier but treats its findings only as transport/projection fixtures. It now proves exact Dossier candidate coverage, risk-vs-caution separation, historical compatibility, fail-closed grounding, ownership and frontend passivity in one bounded test. Future Deep negative-path changes can validate this contract directly instead of rediscovering the full Dossier -> result -> state -> card chain manually.
