# WORKER TASK — DIRECTOR ORCHESTRATION PHASE 2A SYSTEM AUDIT 01

Task ID: `director-orchestration-phase2a-system-audit-01`
Mode: `READ-ONLY / AUDIT`
Report: `reviews/system_audits/director-orchestration-phase2a-audit-01.md`

## Context

Independent audit of the Phase 2A security/state/cloud-worker boundary.

Implementation report:
`reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`

Validated implementation head:
`bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`

Validation evidence:
- workflow run `33964008655`
- job `101300745779`
- artifact `9968832310`
- artifact name `director-orchestration-phase2a-staging-request`

Phase 1 has already been independently accepted. This audit is only for the newly added Phase 2A boundary.

## Goal

Determine whether Phase 2A is safe enough to permit a separately enabled Phase 2B live READ-ONLY RECON/AUDIT cloud-worker pilot after direct GitHub secret provisioning.

Do not implement fixes and do not enable live dispatch in this audit.

## Required audit questions

1. Is there exactly one authoritative future writer for `orchestration/state.json`?
2. Is state persistence still disabled in Phase 2A and impossible through ordinary worker paths?
3. Are immutable intake event IDs/digests, task revision, attempt identity, exact task-file blob SHA, base SHA, report path and lease binding sufficient to reject stale/ambiguous work?
4. Are maximum two logical slots and external/manual occupancy still enforced?
5. Can Phase 2 cloud workers accept only `READ_ONLY_RECON` / `AUDIT`, with `IMPLEMENT` rejected before lease/dispatch?
6. Is the future worker request/result contract fail-closed and exact-revision bound?
7. Is the trusted publisher truly separate from the future LLM worker and confined to exactly the expected report path?
8. Can an LLM worker request state/product/repository mutation or next-task selection? It must not be able to.
9. Does the future Codex worker job have only repository read access, checkout with `persist-credentials: false`, no GitHub write credential, and only future `OPENAI_API_KEY` exposure?
10. Is `openai/codex-action` pinned to the exact immutable verified commit recorded in the implementation, with provenance checked against authoritative sources?
11. Is the future worker definition structurally non-executable in Phase 2A?
12. Does the validation workflow avoid OpenAI/Codex, secrets, worker dispatch, state mutation, product mutation and write permissions?
13. Do run/job/artifact refs validate the same implementation revision being audited?
14. Are secret-detection and publisher checks adequate for the bounded Phase 2B READ-ONLY pilot, recognizing deterministic limits explicitly?
15. Is it safe to ask the user to create `OPENAI_API_KEY` in GitHub Actions Secrets only after this audit accepts?
16. Is Phase 2B ready to enable exactly one bounded READ-ONLY pilot task, without enabling autonomous IMPLEMENT?

## Critical invariants

Reject Phase 2A systemic closure if any of these are false:
- one state writer only;
- no LLM GitHub write credential;
- no worker ability to write state/product files;
- stale result rejection;
- max two slots;
- real dispatch remains disabled today;
- IMPLEMENT cannot enter Phase 2 cloud-worker path;
- trusted publisher writes only expected report path;
- exact task/revision/attempt/base/blob/report binding;
- no secret value committed/logged.

## Boundaries

READ-ONLY / AUDIT only.

Do NOT:
- modify code/config/state/workflows;
- enable Phase 2B;
- add or inspect `OPENAI_API_KEY`;
- invoke OpenAI/Codex;
- dispatch a worker;
- change product/Taste/ranking logic;
- broaden into general Actions hardening outside this boundary.

## Output

Save exactly:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`

Maximum 5 findings.

Include:
1. Scope
2. Verified security/state invariants
3. Findings (max 5)
4. Phase 2B readiness
5. Whether user secret provisioning may proceed
6. One next step max
7. Exact refs

End exactly with:
`Director orchestration Phase 2A systemic closure: accepted | needs_followup`
