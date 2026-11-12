# Visual → Pages depth-safe direct-dispatch implementation

## Scope and authorization

User approved option 1 (2026-11-11): retain two GitHub Actions workflows, replace the unsupported fourth workflow_run hop in nightly publication with explicit producer-originated workflow_dispatch. Repository: only kentrap2011-hub/steam-kz-deals-2. Source: main. This is a draft implementation PR, not authority to merge, dispatch live production, create a scheduler, or start a semantic worker.

Source RECON: reviews/worker_reports/site-nov11-83-vs-100-pages-deploy-recon-01.md (draft PR #433). Nightly schedule → feed → pre-AI → visual succeeds, but subsequent workflow_run deploy is not created because GitHub permits only three chained workflow_run levels. Push from default GITHUB_TOKEN does not trigger Pages. Successful push-triggered deploys are not proof of nightly handoff.

## Changes

1. .github/workflows/build-daily-visual-payload.yml gains final dispatch_deploy requiring successful scope and one successful build, giveaway_refresh or commercial_refresh job. It runs on main only, with job-local actions:write and explicit workflow_dispatch sending exact original run ID and attempt. Skipped/failed producers cannot dispatch.
2. .github/workflows/deploy-visual.yml removes only Build daily visual payload from workflow_run subscriptions (prevents duplicate workflow_run + direct dispatch), preserving Build site current status, manual dispatch and existing push paths. Direct dispatch requires paired run ID/attempt, downloads original receipt and checks live GitHub run metadata, exact completed successful producer job matching receipt scope and attempt. Unchanged receipt verifier then binds staged bytes to original producer run and current canonical visual. Legacy manual/no-input and push remain explicitly unbound.
3. scripts/visual_deploy_dispatch.py isolates strict run/attempt/repository/workflow/main/event/receipt/job validation. scripts/test_visual_deploy_dispatch.py tests negatives and wiring. Checks job success rather than whole run conclusion because visual dispatch job is still running when Pages starts.
4. The only degraded receipt permitted for direct deployment is existing deterministic refresh with proven observed_visual. Existing canonical receipt verifier checks exact material and staged bytes. Other no-build/drift outcomes fail direct dispatch.
5. .github/workflows/validate-execution-ownership.yml runs offline tests for these paths.

## Architecture preflight

Owner of scope/orchestration/validation/publication remains GitHub Actions (config/execution_ownership_contract.json). One nightly cycle and read-only Pages are preserved (config/daily_execution_contract.json). Source-integrity and local quarantine remain unchanged (config/site_publication_resilience_contract.json). No new schedule, retry loop, queue, ChatGPT responsibility, Steam collector rerun or UI price refresh. Job-local actions:write is limited to dispatch job. Existing status and independent push paths remain. Concurrent unrelated push may still initiate its own Pages deployment; existing Pages concurrency unchanged.

## Acceptance and remaining checks

Implementation proposed only, awaiting exact-final-HEAD PR CI and independent QA. Check failed/skipped producer, foreign/main and attempt mismatch, missing artifact, changed current visual SHA, deterministic degraded-but-persisted path, manual no-input behavior, concurrency and absence of duplicate visual workflow_run deploy. Unchanged scripts/visual_freshness_receipt.py verify-receipt remains staged-blob verifier.

No production dispatch, merge, site-data mutation or external live HTTP read-back done. End-to-end is not proven until an unattended scheduled visual producer triggers Pages successfully and an independent live URL read-back matches the expected version and 100 active items.
