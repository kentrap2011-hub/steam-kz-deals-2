# Worker report — dossier-v2-research-qa-evidence-gate-protocol-01

- **Status:** IMPLEMENT_DONE_IN_DRAFT_SOURCE_PR; awaiting exact-final-HEAD CI / Director review; **NOT MERGED / NOT semantic QA**.
- **Repository/base:** `kentrap2011-hub/steam-kz-deals-2`, `main@cc85a48433916255296be9e9ecaece9c9771df75`.
- **Source PR:** [#458](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/458), branch `implement/dossier-v2-research-qa-evidence-gate-protocol-01`.
- **Exact implemented source-rules HEAD (before this report commit):** `49610c255a68b328eb9b5f6dc40d19110d5399ce`. The report itself is a subsequent commit; the **final PR HEAD** and CI must be independently re-read from the live PR and attached to Director handoff rather than self-referentially guessed in the report.
- **Original correction:** final corrected report of report-only PR #456, [«Director handoff — исправление процедуры аудита»](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/audit/dossier-v2-fresh6-rerun1-research-quality-independent-20261115-01/reviews/worker_reports/dossier-v2-fresh6-rerun1-research-quality-independent-audit-01.md). Prior `4 QUALITY_GOOD / 2 QUALITY_WEAK` no longer provides legitimate evidence; no web pages were genuinely opened/read by that auditor.

## Changed files (strictly operational Markdown)

1. `config/dossier_research_independent_quality_audit_protocol.md` — short canonical independent QA operating protocol, status thresholds and Evidence Gate.
2. `CHAT_PROTOCOL.md` — one mandatory START entry for independent Research QA.
3. `PROJECT_ROUTES.md` — bounded audit route and incident pointer, verified against frozen `main`.
4. `WORKER_TASK_DOSSIER_V2_FRESH6_RERUN1_RESEARCH_QUALITY_INDEPENDENT_AUDIT_01.md` — one postmortem addition for future re-audit only; original authorization/scope/results not rewritten.
5. `KNOWN_WORKER_PITFALLS.md` — PITFALL-009 on false `opened`/`CONFIRMED`.
6. `reviews/worker_reports/dossier-v2-research-qa-evidence-gate-protocol-01.md` — this report.

## Acceptance — five rules, 5/5

| Rule | Exact permanent location | Result |
| --- | --- | --- |
| 1. Independently establish exact manifest identity and research external sources **before** reading Research claims | `config/dossier_research_independent_quality_audit_protocol.md` §1; `PROJECT_ROUTES.md` audit route | PASS |
| 2. `opened/read` only after actually opening and reading a relevant external passage in the current session; snippets/unavailable tagged honestly | canonical protocol §2, entry in `CHAT_PROTOCOL.md` | PASS |
| 3. Per-game full coverage: mechanics, solo/coop, exact edition/remaster/DLC, positives/negatives, dates/platforms and important omissions; do not invent frequency | canonical protocol §3 | PASS |
| 4. Per-claim evidence chain: Research claim → URL/source type → actually observed fragment/context → `CONFIRMED/UNCERTAIN/UNKNOWN` → quality impact | canonical protocol §4 | PASS |
| 5. Per-game **Evidence Gate before reporting**, with `BLOCKED_EVIDENCE` if not independently verifiable; no automatic `QUALITY_GOOD` from technical receipts | canonical protocol §5 and final paragraphs | PASS |

**Correct examples (conditional, not claims about a particular game):** an auditor opened the independently found exact-edition developer page and read its actual section listing a co-op mode; the report records exact URL, passage context, identity, and `CONFIRMED` for *that scoped capability only*. `QUALITY_GOOD` is acceptable only after independently accessed evidence supports the material claims, all coverage categories are checked, and no material unsupported omissions remain. If relevant external pages cannot be accessed/read, the only valid result is `BLOCKED_EVIDENCE`, with unknown assertions left `UNKNOWN`.

**Incorrect examples:** treating a Research `source_log` URL, search snippet or `notes_recorded` GitHub receipt as an auditor-opened source; calling a single complaint "widespread" without rate evidence; labelling such claims `CONFIRMED`, or publishing `QUALITY_GOOD` because six candidate JSON and receipts exist. `UNCERTAIN` is for partially supported/conflicted claims, not a substitute for invented facts.

**No hard quotas:** no source count, URL count, reading-time requirement or mandatory `source_log`. GitHub CI cannot prove an external page was actually opened. A genuine in-session access trace and a readable claim-to-evidence explanation are required.

## Verification and isolation

- Target repository/main/provenance checked; source branch created from `cc85a48433916255296be9e9ecaece9c9771df75`.
- Source-rule tree commit: `49610c255a68b328eb9b5f6dc40d19110d5399ce`; PR #458 changed-file listing verified before report: exactly five allowed Markdown rule/routing files.
- Initial PR CI for this rules HEAD: `Validate site task registry and page` run `43838115715`, `Validate inactive Dossier GitHub eventual chain acceptance QA` run `43838115436`, `Validate backlog dispositions` run `43838115433`. At the first inspection these were `in_progress`, **not** PASS. Exact-final-HEAD CI must be re-read after report commit.
- Scope intentionally excludes Research JSON, frozen manifests, receipts, sandbox, prior report-only PR #456, production, code, schemas, workflow, writer, owner/retry/queue, automation, Dossier V1/Deep and semantic workers. No real game/web audit was performed.
- No self-merge. This source PR is procedure-only and **does not** approve semantic assessment results.

## Director handoff

After reviewing the exact final PR HEAD and required CI, evaluate/accept this source PR under existing Director approval gates. Then register **separate independent READ-ONLY QA** for the same exact six manifest items, requiring actual web access and applying the new protocol. Keep PR #456 as a disavowed historical report; do not assume `4 GOOD / 2 WEAK`, do not silently repeat Research/Assembly, and do not imply a new user approval is needed for the already approved re-audit.
