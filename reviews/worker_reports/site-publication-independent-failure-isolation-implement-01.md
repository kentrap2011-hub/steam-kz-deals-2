# Site publication independent failure isolation — implementation report

**Task ID:** `site-publication-independent-failure-isolation-implement-01`  
**Mode:** IMPLEMENT / independent draft PR only  
**Base:** `main` at `a2f734d15dddfe870927c7bd484050b73594ec10`  
**PR:** [#238](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/238), DRAFT, NOT MERGED  
**Verified code HEAD before this report-only commit:** `4aee40f307ef1cefa3e07aef583c53b478d8cb27`  
**Outcome:** `IMPLEMENTED_DRAFT_AWAITING_INDEPENDENT_QA`. Published Pages bytes and real runtime Deploy are **UNVERIFIED**.

## Architecture authorization and boundary

- START gate: current `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task file, `DIRECTOR_TASK_BOARD.md` and `config/director_task_plan.json` agree that this task is `authorized_ready_for_worker`, owned by new Chat 1. PR #236 report HEAD `9b815b8ec1055a80e5096a35de71f0338edb5f0c` reviewed.
- Preflight: `config/execution_ownership_contract.json` gives publication/control-plane/validator ownership to GitHub; `config/site_publication_resilience_contract.json` authorizes isolatable presentation defects but requires fail-closed global material/source integrity. No new queue, scheduler, retry loop, semantic worker, browser source calculation or production mutation.
- No real Research, Assembly, data/production rewrite, live Deploy, merge or Scheduled Tasks were performed.

## Implementation: changed runtime behavior

1. `.github/workflows/deploy-visual.yml`: synthetic receipts/material regression tests and UI regression suite no longer execute in the actual Deploy job. Existing *actual* `visual_freshness_receipt.py verify-receipt --expected-run-id ... --staged-path web/data/current.json` is retained for exact triggering build artifact. Scope classification and required source integrity checks remain.
2. `scripts/stage_site_optional_sections.py`: mandatory stage core verifies parseable visual JSON, schema, read-only producer contract, unique paid IDs, nonnegative numeric prices, discount percent in [0,100], **identical canonical/staged bytes** and **exact Git blob SHA**. Any mismatch aborts the Pages job. Receipt verifier then independently checks upstream run ID, material hash/source, produced commit/blob and staged bytes for workflow-triggered build.
3. Director tasks are generated and strictly validated in an isolated bounded subprocess. If either step fails, task page/assets/data are omitted and the index task link is removed. No invalid tasks are published or unverified last-good task data reused.
4. Current status is independently validated against exact source bindings. In a general/commercial/giveaway publication failure omits only `web/data/status.json`; in a **status-only** publication failure blocks the operation.
5. Giveaway presentation is separately validated: on a general/commercial paid publication, an invalid optional section hides the giveaway tab and renders unavailable presentation; the canonical visual JSON is **never edited** and must still pass global source/receipt integrity. On a **giveaway-only** event the same validation failure blocks the operation.
6. `web/app.js`: only honors a stage-authored optional omission flag; does not recompute ranking/price/scope or mutate canonical payload.
7. `web/data/publication-disposition.json` staged artifact records scope, exact source Git blob, source/staged SHA256, per-section `fresh/omitted/unchanged` and diagnostic reason. `published_visual_sha256=null` until independent live readback. Last successful live deploy time is not guessed.
8. `scripts/test_visual_freshness_receipt.py`: test fixture explicitly disables `gc.auto` and `maintenance.auto` before Git fixture commits to prevent background Git maintenance vs `TemporaryDirectory` cleanup race. No production receipt validator was weakened.
9. New PR-only `.github/workflows/validate-site-deploy-isolation.yml` executes the synthetic receipt/material tests, all former UI regressions, and new isolation fault-injection suite. Independent Director task registry validation is preserved as an isolated diagnostic CI job, not a deploy acceptance gate. `PROJECT_ROUTES.md` records navigation.

## Confirmed GitHub PR-only CI for code HEAD `4aee40f...`

| Workflow | Run | Result |
|---|---:|---|
| Validate site deploy isolation (PR only) | [39644705975](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644705975) | **SUCCESS** (core job SUCCESS, isolated Director-registry diagnostic job fails under allowed continue-on-error) |
| Validate site publication resilience | [39644706049](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644706049) | SUCCESS |
| Validate package purchase value | [39644706074](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644706074) | SUCCESS |
| Validate site Deep count queue diagnosis (PR only) | [39644705988](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644705988) | SUCCESS |
| Validate browser Deep feed refresh (PR only) | [39644705994](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644705994) | SUCCESS |
| Validate Deep site mirror UI | [39644706168](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644706168) | SUCCESS |
| Validate Progressive PASS 2 core | [39644706176](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644706176) | SUCCESS |
| Validate site task registry and page | [39644705978](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39644705978) | **FAILURE, unrelated pre-existing invalid Director registry** |

**Fault injections:** `python scripts/test_site_deploy_isolation.py` passed 14 cases: good paid stage; missing `recent_completion`; invalid Director task payload; generator exception; optional status failure vs strict status-only; optional giveaway failure vs strict giveaway-only; paid price tampering; missing canonical source; working file Git blob drift; invalid scope/browser safety; broken task navigation fail-closed; negative price/discount and duplicate paid IDs. Existing `python scripts/test_visual_freshness_receipt.py` passed genuine material/giveaway/commercial/visual mismatch cases and upstream wrong run ID. `python scripts/test_visual_material_freshness_guard.py` passed after changing PR checkout to full Git history. All original browser UI regressions are PR-only.

**Known red CI:** `config/director_task_plan.json` contains new `authorized_ready_for_worker` entries without the exact legacy `recent_completion` field; `scripts/build_site_tasks.py` still permits only old statuses and exact legacy field set. `scripts/test_site_tasks.py` currently fails with `Unexpected/omitted task registry fields` and `KeyError: recent_completion` (and dependent test assertions). This task intentionally does **not** rewrite Director governance data or weaken strict task registry validation; the site task page is omitted until the registry/contract is independently reconciled. This red check still needs its own owner and cannot be interpreted as green QA of task page.

## Independent QA handoff (new read-only reviewer, exact HEAD)

1. Read `CHAT_PROTOCOL.md`, START gate, this report, task file, PR #236 findings and current site resilience/ownership policies. Confirm PR #238 targets `main`, is DRAFT and exactly matches the reviewed head; if head moves re-run review.
2. Review *every changed file*, especially `deploy-visual.yml` removed tests vs retained runtime receipt/sha checks; verify this is a production **acceptance split**, not blanket disabling. Check malicious paid prices, duplicate scope, source SHA drift, wrong build run ID/receipt, missing canonical visual, malformed core contract, status-only and giveaway-only failure rejection.
3. Run `python scripts/test_site_deploy_isolation.py`, `python scripts/test_visual_freshness_receipt.py`, `python scripts/test_visual_material_freshness_guard.py`, plus all former browser UI regression commands from PR-only workflow. Check PR-only CI run IDs on the exact code HEAD (or successor).
4. Fault-inject bad task registry, missing `recent_completion`, crashed task generator and invalid current site status; assert otherwise valid paid stage continues, `tasks.html` navigation is removed, and status-only fails closed. Fault-inject invalid giveaway; assert general paid stage uses safe presentation omission but giveaway-only fails closed.
5. Independently audit that *actual* full/commercial/giveaway receipt checks prove source bindings and exact upstream `workflow_run.id`; `unbound/non_workflow_run` publication must never be claimed as fresh. Confirm no mixing incompatible commercial/giveaway/Deep snapshots and no browser-side data recalculation.
6. Inspect staging/manifest for `source_visual_git_blob_sha`, `source_visual_sha256`, `staged_visual_sha256`, section dispositions/reasons and correct `published_visual_sha256=null` pre-deploy. Independently verify no broken tasks link if task section omitted. Check how existing service-worker/cache behavior presents omitted sections.
7. Do **NOT** perform actual Pages Deploy/merge as QA. After a separate Director decision and authorization, compare live `https://kentrap2011-hub.github.io/steam-kz-deals-2/data/current.json`, `data/status.json`, `data/publication-disposition.json` against deployed Pages artifact and canonical Git commit. Compare SHA256, Git source binding, prices/offer expiry, ID/order, current Deep/Fast statistics, and published run IDs/time; distinguish source freshness, visual build freshness and Pages deploy time.

**Evidence gap:** actual successful live Pages readback, published byte hashes, precise last successful deploy time and full comparison with current canonical visual are not proven in this PR. The PR-only execution proves code/tests, not deployed freshness. Prior PR #236 identified two real failed Deploy runs but those do not prove live site freshness. No unauthorized Deploy was launched.

## PRE-SEND and context budget

The work took sustained GitHub file/contract reading, PR #236 review, isolated code writes, CI iteration and job log diagnosis. A PR-only initial failure was caused by shallow checkout hiding the pinned historical material commit; the CI workflow now uses `fetch-depth: 0`. The task route and in-PR report avoid repeating repository-wide archaeology. Temporary `CURRENT_TASK.md` was not overwritten because it carries concurrently active independent work and this completed worker's durable report is task-specific.
