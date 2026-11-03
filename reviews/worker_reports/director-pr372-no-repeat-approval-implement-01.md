# PR #372 — no repeat approval for already-consented scoped implementation

Task: `director-pr372-no-repeat-approval-implement-01`
Source: `kentrap2011-hub/steam-kz-deals-2`, main → existing draft [PR #372](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/372), branch `implement/director-postdiagnosis-consent-handoff-continuity-01`.
Mode: bounded textual governance implementation + static regression review. **No real REGISTER, MERGE, semantic/retry/production/deploy or Scheduled Task run.**

## Verified facts / authority
- Read `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md` from `main`, completed relevant START steps; inspected exact PR #372, original report, relevant `DIRECTOR_PROTOCOL.md` sections, `PROJECT_ROUTES.md` and execution ownership contract. Task-specific writes restricted to the existing PR branch.
- Canonical consent/STATUS/DECIDE/REGISTER/MERGE owner: `DIRECTOR_PROTOCOL.md` §1; concise enforcement: `CHAT_PROTOCOL.md` PRE-SEND. Existing `config/director_task_plan.json` and `DIRECTOR_TASK_BOARD.md` remain the one existing registry/assignment authority; they do **not** by themselves prove user approval.
- Architecture preflight: GitHub retains source scope/registration/CI/control plane; Director is authorized to take already approved bounded task through normal acceptance; worker performs only allocated task. No GitHub→ChatGPT control-plane transfer, recurring stage, new approval ledger, queue, retry or quota.
- Existing defect in PR #372: result→consent→REGISTER was explicit, but typed MERGE and post-QA closeout still required an independently expressed source-PR-specific merge grant after a user had already said yes to scoped IMPLEMENT.

## Changes
1. `DIRECTOR_PROTOCOL.md` §1 STATUS/DECIDE/REGISTER/MERGE and post-QA closeout: proven initial yes to one bounded IMPLEMENT task conditionally authorizes **ordinary source PR acceptance within that same task and scope**; after green mandatory exact-HEAD CI, risk-appropriate independent QA and live merge safety, Director executes HEAD-bound merge without asking "принимаем?" again. Refuse to infer consent from Board/task/PASS alone.
2. Preserved one initial user question for **new** diagnosis / unapproved implementation, no-write for "нет", disambiguation for unclear "да", deduped registration, and new separate explicit permission for scope drift/new goal, semantic/recovery/retry, production/deploy, Scheduled Tasks, expanded permissions, or high-risk action.
3. Explicit STOP at missing/revoked provenance, red/pending/skipped/missing required exact-HEAD CI, failed/missing L3 QA, stale materially changed HEAD lacking QA, merge conflict, unknown mergeability or insufficient actor rights.
4. `DIRECTOR_PROTOCOL.md` §8/§10 and `CHAT_PROTOCOL.md` Director PRE-SEND aligned to the same single decision gate; no parallel approval store.
5. Prior worker report `director-postdiagnosis-consent-handoff-continuity-implement-01.md` annotated: initial L1 rating only applies to its *former* result→REGISTER scope, not this amendment.

## Risk classification
**L3 (authority/consent gate changed).** The fact that this is text-only does **not** make it L1. Independent **narrow substantive QA on exact current source PR HEAD**, focused on grant provenance, safe conditional merge, scope boundaries, negative paths and contradictory directions, is mandatory before Director can merge. Original report's earlier L1/ready recommendation is superseded for the amended PR.

## Static regression walkthrough (expectations, not real GitHub merges)
| # | Input / condition | Required output |
| --- | --- | --- |
| 01 | User approved concrete bounded IMPLEMENT, exact source match, CI green, risk-appropriate QA PASS, rights and mergeability proved | Director performs guarded HEAD-bound MERGE **without second approval** |
| 02 | New DIAGNOSIS_COMPLETE with one useful unapproved repair | STATUS/DECIDE reports finding and asks once **before REGISTER**, no writes |
| 03 | User refuses proposed repair | No REGISTER, no PR merge or other writes |
| 04 | Ambiguous "да" between two proposals | One clarification; no writes |
| 05 | Exact task already REGISTERed/assigned | Reuse existing state; no duplicate |
| 06 | QA fails required substantive test | `BLOCKED_SAFETY`, no merge |
| 07 | Mandatory CI red | `BLOCKED_SAFETY`, no merge |
| 08 | Mandatory CI pending or skipped | `BLOCKED_SAFETY`, no merge |
| 09 | Mandatory CI absent on exact source HEAD | `BLOCKED_SAFETY`, no merge |
| 10 | Material new source HEAD after QA, delta unverified | `BLOCKED_SAFETY`; assess new delta |
| 11 | PR has merge conflict / unknown mergeability | `BLOCKED_SAFETY`, no merge |
| 12 | Director lacks actor permission | `BLOCKED_SAFETY`, no merge |
| 13 | Implement diff adds forbidden scope / new goal / new authorization | `BLOCKED_PERMISSION` for new scope, no merge |
| 14 | Unsafe production/deploy or semantic/retry / Scheduled Task action requested after bounded implementation | Separate explicit grant; no implicit action |
| 15 | L3 QA absent though CI green | `BLOCKED_SAFETY`, no merge |
| 16 | Only RECON or independent QA was approved, not IMPLEMENT | `BLOCKED_PERMISSION`, no inferred source merge |
| 17 | Original yes revoked or provenance unknown | `BLOCKED_PERMISSION`, no guessed consent |
| 18 | Exact source PR already merged | `ALREADY_MERGED` with SHA, no duplicate merge |
| 19 | Optional PR-only collector intentionally skipped, required checks green | Optional skip does not itself block normal MERGE |
| 20 | User directly says "Прими source PR #X" within valid safety boundaries | No repeat confirmation; apply same CI/QA/HEAD safety gates |

Walkthrough 01–20 mapped statically to amended typed §1 MERGE, result→REGISTER, post-QA paragraph, §8/§10 and PRE-SEND; **not an executable runtime acceptance or simulation of actual GitHub actions**. Additional 26/26 targeted in-memory anchor/guard checks passed on branch at snapshot `65f659a80733fb85ca70dfe6f5b9ac2643289e71`; they test presence/consistency of expected rules, not Director behavior in an autonomous later conversation.

## Validation / evidence / exact source
- Prior source change commits: `7455ef0a31d1c4d55eecb46892ae43a3c1c5dfc2` (`DIRECTOR_PROTOCOL.md`), `53e6d443b2909ebe9b2437c69ca3db183bca5cfd` (`CHAT_PROTOCOL.md`), `65f659a80733fb85ca70dfe6f5b9ac2643289e71` (old report amendment).
- **Pre-report source HEAD snapshot:** `65f659a80733fb85ca70dfe6f5b9ac2643289e71`. Creating this report moves the source HEAD: **independent QA and Director must read the live final PR #372 `head_sha` and verify exact-HEAD mandatory CI after report creation**. Never use this pre-report SHA as proof that the later final HEAD passed checks.
- At pre-report source snapshot, `Validate backlog dispositions` [run 41495756932](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41495756932) was `in_progress`; `Validate site task registry and page` [run 41495757128](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41495757128) was `success`. **No exact-final-report-HEAD CI success claimed.**
- No independent L3 QA performed by another actor. Source PR remains DRAFT and unmerged. No direct merge test, registration, runtime or production invocation performed.

## Unresolved / status / handoff
- `Status:` **complete** for scoped edits; **unmerged / pending independent substantive L3 QA and final-HEAD CI**.
- `Verdict:` **READY_FOR_NARROW_INDEPENDENT_QA**, **not READY_FOR_DIRECTOR_MERGE_REVIEW**.
- `Recommended next step:` **Director** registers/assigns an independent narrow L3 QA worker for the current exact source PR #372 HEAD, waits for required exact-HEAD CI and QA PASS, then applies source MERGE gate with separate approval only when a new authority boundary truly exists. The implementing worker does **not** self-merge.
- `Efficiency / reusable lesson:` existing PR and exact protocol anchors sufficed; no new `PROJECT_ROUTES.md`/pitfall update warranted under this task's narrow write-set.
