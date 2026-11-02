# Independent L3 QA — PR #372 director consent gate

**Task:** `director-pr372-consent-gate-independent-l3-qa-01` (NEW physical Chat 1).  
**Mode:** independent read-only governance/authorization QA; only this report is written in a separate DRAFT PR.  
**Source:** [PR #372](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/372); **source HEAD verified twice:** `5d1126192f5a61f1a5143849a63330570d3359f3`; source OPEN / DRAFT / `merged=false` / `mergeable=true` / `mergeable_state=clean`.  
**Reference main at report preparation:** `42fac171a0d3d2684b684b9702c8c472e3e0aa5c`.  
**Outcome: `BLOCKED_EVIDENCE` for authorization of *merging PR #372 itself*.** The substantive proposed L3 rules pass this narrow independent static review (no critical text defect found), but **this report does not authorize source merge**: the currently effective `main` MERGE gate requires a verifiable *PR-specific* user grant, and the evidence recovered here proves only the user's general desire to eliminate the repeated approval, not an explicit instruction to merge source PR **#372** after PASS. Do not let PR #372 authorize its *own* adoption before its rules become effective. Also source is still DRAFT.

## Verified facts and scope

1. Fully read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md` and exact named task from main. Read addressed source `DIRECTOR_PROTOCOL.md` §1/§8/§10 and `CHAT_PROTOCOL.md` PRE-SEND, `PROJECT_ROUTES.md` director task route, `config/execution_ownership_contract.json`, both source implementation reports and exact four-file source PR diff. Checked applicable main-vs-proposed MERGE wording, actor/authorization boundary, and reports from [PR #380](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/380) and [PR #382](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/382). No other repository was read.
2. Exact source changed files: `DIRECTOR_PROTOCOL.md`, `CHAT_PROTOCOL.md`, `reviews/worker_reports/director-postdiagnosis-consent-handoff-continuity-implement-01.md`, `reviews/worker_reports/director-pr372-no-repeat-approval-implement-01.md`; no source changes to production, permissions, scripts, ownership contract, workflow, registry or Board. Earlier original report's L1/ready advice explicitly superseded by L3 amendment.
3. New rule's conditional grant is tightly scoped: verifiable, unrevoked user approval of one concrete IMPLEMENT scope, the same task/source PR, unchanged authority and material behavior, exact-source-HEAD checks and risk-specific independent QA, mergeability and actor rights. Generic Board, task, worker report, QA PASS and green CI are expressly *not* grants. New goal/scope/permissions and real semantic, recovery/retry, production/deploy or Scheduled Tasks require separate express authorization.
4. The result→single useful DECIDE+ASK→one specific user yes→REGISTER prewrite→CI/main→launcher continuity remains; no repeat question for the same decision. STATUS does not autonomously create registration; `нет`, duplicate or ambiguous `да` fail closed. §8, §10 and `CHAT_PROTOCOL.md` PRE-SEND point to the same canonical gate without a second approval ledger.
5. **Important bootstrap distinction:** `DIRECTOR_PROTOCOL.md` on **current main** still admits source MERGE only after user command `Прими PR #X` or a verified specific conditional `после PASS принимай именно source PR #X`; it explicitly rejects an assistant promise, task, report, Board, or green CI as a grant. The **proposed, not yet effective** PR #372 broadens this to approval of the matching bounded IMPLEMENT. We recovered a user statement on 2026-11-02 accepting the no-repeat principle for completed agreed work, but did **not** verify a direct user grant mentioning source PR #372 or its acceptance after L3 QA. This is an authorization-evidence blocker for *this adoption*, not a defect in the future conditional merge policy. Do not infer the missing initial PR-specific grant from the assignment to run this independent QA, the PR description, or prior assistant statements.
6. Ownership preflight: Director may coordinate approved interactive governance transitions; canonical GitHub PR/CI/registry retains source state; semantic execution and production control-plane remain governed by `config/execution_ownership_contract.json`. No new recurring stage, queue, retry-loop, scheduler, secret, grant store or autonomous semantic operation introduced.

## Exact-HEAD GitHub checks (actually fetched, not simulated)

| Evidence | Actual observation |
| --- | --- |
| source HEAD | `5d1126192f5a61f1a5143849a63330570d3359f3` (source PR metadata and REST pull both matched) |
| [Validate backlog dispositions, run 41495996682](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41495996682) | `completed/success`, check `backlog-disposition`, exact source HEAD |
| [Validate site task registry and page, run 41495996673](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41495996673) | `completed/success`, check `validate`, exact source HEAD |
| Check Runs API | `total_count=2`; two completed successes above, no red/pending/skipped in returned check runs |
| Legacy combined status | `pending` with **zero** legacy statuses; this is **not** a failed/pending named required GitHub Actions check |
| main branch protection / repository rulesets | `protected=false`, reported required-status-check enforcement `off`, zero contexts/checks; repository ruleset list `[]`. Protection detail endpoint returned 403 to integration; do not claim GitHub mechanically enforces project's procedural merge safety |
| Source merge state | `mergeable=true`, `mergeable_state=clean`; source `draft=true` and cannot be accepted as-is until taken out of Draft following valid authorization |
| Actor permissions | Connected repo metadata reports `permissions.admin=true` / `push=true`; actual Director actor and HEAD-bound merge remain unexercised, must be checked live |

These two workflows are the checks observable on the exact source HEAD and both succeeded. The project still requires manual enforcement of exact-HEAD required checks because main is not protected. **No** GitHub-run L3 semantic governance regression suite was observed; source implementer's 20 scenarios and this worker's 24/24 exact-text anchor assertions are static, not real Director tool calls or end-to-end behavior tests.

## Independent static/regression scenarios

Mapped against actual **source PR HEAD** `DIRECTOR_PROTOCOL.md` §§1,8,10 and `CHAT_PROTOCOL.md` PRE-SEND, not merely inherited from implementer's report. All expected behaviors are supported textually; no live registration/merge/semantic/deploy/failure injection was performed.

| # | Input / security edge | Expected / review |
| --- | --- | --- |
| 01 | One concrete user-approved bounded IMPLEMENT, same source PR and scope, all gates PASS | Conditional HEAD-bound source merge **without another approval question** — static PASS, *after rule effective* |
| 02 | Newly finished diagnosis with one useful but unapproved repair | One bounded next step + one consent question; no REGISTER/MERGE — PASS |
| 03 | User says no | No write — PASS |
| 04 | Ambiguous `да` applying to two proposed tasks | One clarification, no write — PASS |
| 05 | Same task already registered | Existing registration reused; no duplicate — PASS |
| 06 | Only RECON/diagnosis user consent | No inferred IMPLEMENT or source merge — PASS |
| 07 | Only independent QA consent | No inferred source-IMPLEMENT merge — PASS |
| 08 | Missing, ambiguous or revoked original user grant | `BLOCKED_PERMISSION`, no guess from CI/Board/report — PASS |
| 09 | A source implementation expands its user-approved scope or changes owner/permissions | Require separate express grant; stop — PASS |
| 10 | Mandatory CI failure/red | `BLOCKED_SAFETY` — PASS |
| 11 | Mandatory CI pending, skipped or absent at *source* HEAD | `BLOCKED_SAFETY` — PASS |
| 12 | Report-only commit changes HEAD without material code delta | Check actual delta; no automatic full substantive QA redo — PASS |
| 13 | Material code/governance HEAD delta after prior QA | Delta-specific risk QA required before merge — PASS |
| 14 | Material L3 change with no independent substantive QA or QA failure | `BLOCKED_SAFETY` — PASS |
| 15 | Conflict, unknown mergeability, or actor lacks authority | `BLOCKED_SAFETY` — PASS |
| 16 | GitHub unavailable so exact live HEAD/CI/rights cannot be checked | Fail closed via absent safety evidence; **no offline authorization** — PASS (inference from required gates, not outage test) |
| 17 | Source already merged, later repeated status | `ALREADY_MERGED`, no repeated merge — PASS |
| 18 | A QA report-only PR is green/merged but source PR is not | QA/report does not substitute for source acceptance — PASS |
| 19 | New semantic one-shot, real recovery or retry | Requires separate explicit authority — PASS |
| 20 | Production, deploy, scheduled-task or independent high-risk action | Separate approval; source merge grants none — PASS |
| 21 | Post-QA closeout of already scoped approved implementation | Director evaluates existing grant and merges if gates hold, no second `принимаем?` — PASS |
| 22 | Repeated STATUS of identical result with no new decision | No duplicate question, task or write — PASS |
| 23 | Original source #372 itself before new rule is in main | **Existing main grant applies**; absent PR-specific provenance → `BLOCKED_EVIDENCE` for merge, not implicit authorization |
| 24 | Source #372 still Draft | Cannot immediately merge Draft; Director must handle ready-for-review under valid same-source authorization — operational blocker, not a content safety failure |

**Static anchor verification:** 24/24 targeted text-presence/consistency assertions passed against source `5d112619...`; a passing anchor does not prove runtime Director compliance. Scenarios 23–24 deliberately identify adoption prerequisites not resolved by text assertions.

## Durable closeout/recovery separation

[PR #380](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/380) is **MERGED, report-only** and explicitly states `BLOCKED_OVERLAP_FOR_IMPLEMENT`: its suggested durable closeout/recovery mechanism was **not** implemented because source #372 owns the overlapping `DIRECTOR_PROTOCOL.md`/`CHAT_PROTOCOL.md`. [PR #382](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/382) is **MERGED, report-only independent QA** with `PARTIAL_BACKUP_ONLY`: a readable Library fallback exists but snapshot is stale/incomplete and tested automatic recovery/replay does not exist. A PASS or merge for #372 would **not** mark closeout/recovery fixed. That is a distinct later bounded implementation with L3 checks and no unsanctioned automatic recovery.

## Changes / status / next actor

- **Changes:** only this report, in a new separate report-only DRAFT PR. **Source PR #372 untouched**; no changes to Board, registry, contracts, source scripts/workflows, other PRs or production.
- **Validation:** live GitHub source state and exact-HEAD two successful Actions checks; 24/24 static anchors; 24 substantive negative/positive scenario reasoning only. No real runtime/Director actions tested.
- **Unresolved:** documentary source-PR-specific **initial user MERGE grant for #372 under current main** not established here; current source Draft; live HEAD/CI/mergeability must be rechecked on any Director action. Current main branch CI policy is procedural rather than branch-enforced.
- **Status:** `blocked` for source merge authorization evidence, **substantive L3 static review completed without source-rule defect**. **Verdict:** `BLOCKED_EVIDENCE` (not `CHANGES_REQUIRED`: no critical bug in the intended new source rule was found; not `PASS_FOR_DIRECTOR_MERGE_REVIEW`: this task explicitly includes provenance and current main requires source-specific grant for this first adoption).
- **Recommended next step / single actor — DIRECTOR:** bounded verification of an *existing*, unrevoked **user PR #372-specific MERGE-after-L3-PASS grant** from the original user conversation; if evidence remains absent, obtain that one-time grant before source acceptance. Only then recheck the exact source HEAD, mandatory CI, draft/ready state, mergeability and actor rights and execute a HEAD-bound source merge. After #372 is accepted, separately assign implementation of the **not yet delivered** durable closeout/recovery from reports #380/#382; do not combine that work with the source merge.
- **Efficiency / reusable lesson:** the active main-vs-unmerged-source consent boundary should be examined at future L3 governance QA entry; conditional grants in a proposed PR do not retroactively govern acceptance of that same PR. Keep this as a narrowly scoped governance QA note; no extra route/pitfall file write authorized.

**Time note:** most work was spent on exact source/main director consent comparison, retrieval of both historical reports and #380/#382, and exact-HEAD CI/branch safety evidence. Next independent QA of a consent-boundary change can start from the active `DIRECTOR_PROTOCOL.md` MERGE gate and source diff rather than rebuilding wider project history.
