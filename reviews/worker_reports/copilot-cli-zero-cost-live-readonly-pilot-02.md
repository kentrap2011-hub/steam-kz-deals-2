# Copilot CLI Zero-Cost Live Read-Only Pilot 02

## Status

`blocked`

## Final scope decision

Pilot 02 is durably closed. No next task was selected, no queue draining occurred, and no autonomous `IMPLEMENT` was dispatched.

The representative task remained exactly:

- task: `epic-ru-availability-source-probe-02`
- task file: `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md`
- mode: `READ_ONLY_RECON`
- revision: `1`
- attempt: `1`
- attempt ID: `epic-ru-availability-source-probe-02:r1:a1`
- lease ID: `slot_2:epic-ru-availability-source-probe-02:r1:a1`
- bound base SHA: `4027aea1103a1a872c27b24ebd4a9c3e1473d315`
- task-file blob SHA: `8270487fb3019135adc5662d0b67f0f37e189bed`
- exact semantic report path: `reviews/worker_reports/epic-ru-availability-source-probe-02.md`

## What happened before the real dispatch boundary

The first implementation did not actually complete a Pilot 02 semantic dispatch. The failures below all occurred before an exact Pilot 02 lease was committed and before the semantic worker ran:

1. Initial launch run `34017053600`, prepare job `101442565794` failed on the retained Phase 2B regression because the workflow used historical fixture `98f88a3813a7a882f452c816898a6d0f748ab85e`, which was already post-first-recovery. Worker job `101442579536` and publisher job `101442579523` were skipped. Semantic dispatches/model invocations at this point: `0`.
2. A recovery workflow was added, but its first marker push did not register a run because a static-check string contained a literal GitHub expression prefix and made the YAML invalid before execution. No lease or worker was created.
3. Registered pre-dispatch recovery run `34017309381`, prepare job `101443260176`, successfully ran the corrected Phase 2B fixture `69a3c929c9ab32416a54b513b4f8c662b8013c91` and all Pilot 02 adapter tests, then failed in an additional static job-boundary assertion that accidentally matched its own source text. Worker `101443279304` and publisher `101443279856` were skipped. Semantic dispatches/model invocations remained `0`.

These were infrastructure/pre-dispatch failures, not retries of the semantic task. They did not acquire a second semantic attempt and did not invoke Copilot inference.

## Actual bounded live run

The first and only run that crossed the Pilot 02 dispatch boundary was:

- GitHub Actions run ID: `34017359203`
- run attempt: `1`
- recovery/control-plane head: `e7a97b984f8b19eebdd67b17d9adc2ba34bc8961`
- prepared-state commit: `8c1c52fb29cfba8d9d8f3d8ea6f2163eea9f9c15`
- prepare job ID: `101443394553` — `success`
- worker job ID: `101443422968` — `success`
- trusted publisher/closeout job ID: `101443470139` — `success`
- publisher closeout commit: `abbda278104567d474ecec3e1e0f7fad605178fc`

Prepare proved the corrected Phase 2B regressions and Pilot 02 adapter regressions, acquired exactly `slot_2`, persisted only authoritative orchestration state, and emitted the exact bound request artifact.

Request artifact:

- artifact ID: `9984318905`
- name: `copilot-pilot02-request-recovery`
- digest: `sha256:02e33d16ec8cbdad5205f6ddccd777413caba23b2d515c5178d8ffdf79bda1f0`

The artifact confirms exact `r1:a1`, exact `slot_2` lease, base `4027aea1103a1a872c27b24ebd4a9c3e1473d315`, blob `8270487fb3019135adc5662d0b67f0f37e189bed`, `READ_ONLY_RECON`, and all worker mutation authorities set to false.

## Authentication and worker security boundary

The live worker received only the Actions built-in `GITHUB_TOKEN` with:

- `contents: read`
- `copilot-requests: write`
- metadata read implicitly supplied by GitHub Actions

Both the recovery control-plane checkout and exact worker-base checkout used `persist-credentials: false`.

No PAT, `OPENAI_API_KEY`, provider secret, Steam secret, alternate provider, billing-setting mutation, paid fallback, or paid-overage enablement was supplied or used.

The worker had no repository-write, state-write, product-write, or next-task authority.

## Copilot CLI and zero-cost quota gate

The official CLI installed and executed successfully for version discovery:

`GitHub Copilot CLI 1.0.83`

Install method:

`npm install -g @github/copilot@latest`

The worker then attempted the required no-inference quota preflight through `@github/copilot-sdk@latest` / `account.getQuota` before allowing any `copilot -p` semantic call.

The preflight returned:

`quota_auth_or_entitlement_error:Client is not connected. Call start() first.`

Therefore:

- usable quota snapshot: none
- zero-additional-payment proof: `false`
- Copilot semantic CLI invocations: `0`
- semantic result: none
- postflight quota snapshot: not applicable

Evidence artifact:

- artifact ID: `9984324571`
- name: `copilot-pilot02-evidence-recovery`
- digest: `sha256:2e6f2d2568cbfd34f46c85de11738cb4c99c52a9dddf853e1159328763681a6a`
- `provider_outcome`: `provider_unavailable_zero_cost_gate`
- `copilot_invocation_count`: `0`

### Root cause of the quota failure

This diagnostic was not evidence that the account lacks Copilot entitlement. It exposed a Pilot 02 adapter defect: the SDK client was constructed but `client.start()` was not called before the quota RPC.

Official SDK usage requires starting the client before RPC/session operations. The adapter was corrected after closeout in commit:

`d5f9eeb04672fcf7b499c42df8557aae266c58ee`

The corrected helper now executes `await client.start()` before `account.getQuota`.

The pilot was **not rerun** after this correction. Reopening or redispatching `r1:a1` after its deterministic closeout would violate the explicit one-dispatch/no-second-dispatch boundary. Consequently the current account's actual included Copilot quota and overage setting remain undetermined by Pilot 02.

## Trusted publisher conclusion

The trusted publisher received no semantic worker result because the zero-cost gate stopped before inference.

Publication result:

- semantic publication accepted: `false`
- `reviews/worker_reports/epic-ru-availability-source-probe-02.md`: **not published**
- reason: there was no real semantic worker result to validate

This is intentional. Creating a semantic report without a real accepted worker result would violate the task contract.

The mandatory pilot report itself was published and the authoritative controller closed the attempt as `blocked`.

## Final orchestration state

After closeout:

- `dispatch_enabled`: `false`
- orchestration phase: `copilot_cli_zero_cost_live_readonly_pilot_02_closed`
- Pilot 02 state: `blocked`
- Pilot 02 attempt number: `1`
- Pilot 02 attempt ID: `epic-ru-availability-source-probe-02:r1:a1`
- Pilot 02 assigned slot: none
- both logical slots: free
- automatic next dispatch: `false`
- paid fallback used: `false`
- Copilot semantic invocation count: `0`
- semantic report path in closeout: `null`

The unrelated queued `IMPLEMENT` task `top-summary-filter-buttons-01` remained at attempt `0` with `attempt_id: null`; it was not dispatched.

## Cost conclusion

No Copilot inference request was sent, so Pilot 02 did not consume a semantic model request. The only Copilot operations were installation/version discovery and the failed pre-inference SDK quota call.

No additional payment path was enabled. No paid overage was authorized. No PAT or `OPENAI_API_KEY` was used. No alternate provider was tried.

Exact AI-credit usage is not guessed when GitHub did not provide a valid quota snapshot.

## Final decision

`blocked`

Pilot 02 is fully closed as a fail-closed zero-cost pilot. The current run could not safely prove entitlement/quota because of a pre-inference SDK startup defect. That defect has been corrected in the adapter code, but no second dispatch or rerun was performed. The semantic Epic RU report is correctly absent because no accepted semantic worker result existed. General dispatch remains disabled and no next task has been started.
