# WORKER TASK — Copilot CLI Zero-Cost Live Read-Only Pilot 02

## Task ID
`copilot-cli-zero-cost-live-readonly-pilot-02`

## Mode
`IMPLEMENT`

## Priority
`VERY_HIGH_INFRASTRUCTURE_PRIORITY`

## Expected report
`reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md`

## User cost policy — hard gate
The user will not pay any additional money for inference/automation.
- Do not use `OPENAI_API_KEY`.
- Do not buy or enable paid Copilot overage.
- Do not create a PAT or new provider secret.
- If built-in `GITHUB_TOKEN` plus included Copilot entitlement/credits cannot execute the pilot, fail closed as `blocked`.

## Why revision 02 exists

Pilot 01 correctly stopped because `reviews/worker_reports/epic-ru-availability-source-probe-01.md` already existed as historical Phase 2B blocked-closeout evidence. Do not overwrite or repurpose that file.

Revision 02 uses a new representative task identity and exact report path:

`WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md`

Expected semantic worker report:

`reviews/worker_reports/epic-ru-availability-source-probe-02.md`

If this new exact path already exists at pre-dispatch time, stop and report the conflict rather than overwrite it.

## Authoritative sources
Read:
- `reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`
- `reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-01.md`
- Phase 2A/2B reports/contracts
- current orchestration state and controller/publisher boundaries.

## Goal
Validate exactly one real headless semantic worker using direct GitHub Copilot CLI inside GitHub Actions, authenticated only through the repository's built-in `GITHUB_TOKEN` / documented Copilot request permission, while preserving the accepted Phase 2A/2B control/security boundary.

This is a bounded provider-adapter pilot, not queue draining and not general automation enablement.

## Exact representative task
Use exactly:
`WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md`

Worker mode:
`READ_ONLY_RECON`

Expected semantic worker report:
`reviews/worker_reports/epic-ru-availability-source-probe-02.md`

## Required architecture
- Keep `scripts/director_orchestration_controller.py` as sole state writer.
- Preserve exactly two logical slots and current manual/external occupancy truth.
- Exact task revision / attempt / lease / task-file blob / base SHA / report path binding.
- Preserve current-state/CAS/stale/lease barriers.
- One logical pilot task only; no second task and no automatic queue draining.
- `IMPLEMENT` remains excluded from autonomous semantic dispatch.

### Copilot worker job
- GitHub-hosted standard runner.
- Use current official GitHub Copilot CLI mechanism documented for Actions.
- Authentication: built-in `GITHUB_TOKEN` only.
- Minimum permissions: repository `contents: read`; add only the documented Copilot inference permission necessary.
- Checkout exact bound base with `persist-credentials: false`.
- Model/LLM process must not possess repository write authority.
- No PAT, no `OPENAI_API_KEY`, no Steam/provider secrets.
- Non-interactive/no-user-prompt mode.
- Restrict tools to bounded repository read/search, safe read-only shell inspection, and web access needed for the Epic source probe; deny repository mutation, git push, issue/PR mutation, arbitrary credential access, and blanket permissive/yolo mode.
- Structured/machine-readable output suitable for deterministic validation.
- If included Copilot entitlement or AI credits are unavailable/exhausted, classify fail closed; never enable paid overage.

### Trusted publisher
- Separate deterministic job/process owns narrow `contents: write` authority.
- Validate exact task/revision/attempt/lease/base/blob/report binding and fresh current state immediately before publication.
- Publish only exact expected worker report path.
- Reject extra mutations, wrong path, stale state, expired lease, malformed output, secret-looking output, or worker-requested state/product changes.

## Required live evidence
Report:
- exact implementation commit(s);
- exact pilot workflow run/job IDs;
- current official Copilot CLI version/action/install method used;
- effective GitHub permissions for worker and publisher;
- proof built-in token path was used and no new secret/PAT/OpenAI key was supplied;
- Copilot entitlement/quota result without exposing private tokens;
- task/attempt/lease/base/blob/report bindings;
- worker conclusion;
- publisher conclusion;
- automatic worker report commit/path if published;
- proof no second dispatch and no autonomous IMPLEMENT;
- any measured/observable AI-credit consumption if GitHub exposes it safely; otherwise say unobservable rather than guess.

## Required tests
At minimum retain/re-run relevant Phase 1/2A/2B security tests and add bounded provider-adapter regressions for:
- worker has no repo write authority;
- no PAT/API/provider secret requirement;
- wrong report path rejected;
- stale/current-state rejected;
- expired lease rejected;
- concurrent/CAS conflict fail closed;
- exact one logical pilot only;
- second auto-dispatch disabled;
- IMPLEMENT excluded;
- quota/auth failure does not fall back to a paid/second provider.

## Success criteria
`complete` only if:
1. a real Copilot CLI semantic worker executes the exact Epic revision-02 READ_ONLY_RECON task using zero-additional-payment entitlement;
2. trusted publisher durably creates `reviews/worker_reports/epic-ru-availability-source-probe-02.md`;
3. security/current-state invariants hold;
4. no second task or paid fallback occurs.

Otherwise report `blocked` or `needs_followup` with exact non-secret evidence.

## After pilot
Do not enable general dispatch. A successful new provider boundary must go to independent System Audit before material acceptance/general use.
