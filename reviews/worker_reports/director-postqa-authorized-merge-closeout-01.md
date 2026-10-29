# ЧАТ 1 — Director post-QA authorized MERGE closeout

**Task:** `director-postqa-authorized-merge-closeout-01`  
**Mode:** bounded L1 IMPLEMENT; source of truth `main`.  
**Scope:** only `DIRECTOR_PROTOCOL.md` and this report.  
**Verdict:** `READY_FOR_DIRECTOR_MERGE` **only after** existing site-task/backlog both succeed on the exact final PR HEAD, with no material source delta or new L3 risk. Live Actions, not this static declaration, are the authority for final gate.

## Verified facts
- Canonical `CHAT_PROTOCOL.md` START, `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md` §1, task and audit report from report-only PR #360 at `2255fb222ad827443200911e490d551fe9743a28` read. Audit is not in `main`, and #360 is still a separate DRAFT report PR; neither authorizes a source merge.
- GitHub ownership and existing Director §1/§10: Director, not semantic worker or Board, owns the human MERGE decision, while GitHub owns source state and control plane. This change only clarifies preexisting user authority and closeout, without granting new authority.
- Original source #346 was already merged as `3ea4749c2ce3880ed0034c8bded78334bed348f0`; earlier L3 QA `PASS_FOR_DIRECTOR_MERGE` on source `8619ad1dfcd88ea203f6d7e732f335e3597767db` is not proof of earlier user consent or live production acceptance. No duplicate source merge performed.

## Changes
- One replacement inside the existing §1 typed STATUS / DECIDE / MERGE decision path plus two bounded closeout paragraphs. Valid user-authored specific standing conditional grant + fulfilled conditions routes to a **real same-turn MERGE** after live source HEAD, required CI, L3 QA, delta, conflict, mergeability and permission checks. Missing/unknown grant blocks merge; no Board-as-user approval.
- Direct `Прими PR #X` is sufficient authority when safety gates pass; `Кто должен?` is an actor question; report-only QA and source PR are distinct; production is separate. Explicit `MERGED`/`ALREADY_MERGED` SHA or `BLOCKED_PERMISSION`/`BLOCKED_SAFETY` reason.

## Validation — targeted acceptance matrix

These are **decision walkthroughs, not claims of independent ChatGPT execution**. A live no-write probe follows separately.

| Case | Expected and inspected outcome |
| --- | --- |
| Pure `Проверь чат 1`, PASS, no user grant | STATUS read-only; source merge `BLOCKED_PERMISSION`; no new audit/REGISTER/write |
| Prior specific **user-authored** `после PASS прими source #X`, unchanged HEAD, mandatory CI green, independent L3 PASS, clean source PR, rights | Same-turn source MERGE with expected HEAD; `MERGED` SHA; no extra confirmation, not future-step advice |
| Current direct `Прими PR #X` with gates met | MERGE now, report SHA; no redundant second authorization |
| `Кто должен принять?` without earlier grant | DECIDE: Director is actor; merge needs a user's command; zero writes |
| QA `CHANGES_REQUIRED` | `BLOCKED_SAFETY` regardless of permission |
| Source L3 HEAD materially changed since PASS | Focused delta QA needed; `BLOCKED_SAFETY`, no full QA of unchanged inputs |
| Mandatory CI red/pending/skipped/absent | `BLOCKED_SAFETY` on exact source HEAD; optional deliberately skipped PR-isolated collector is distinguished |
| Exact-HEAD CI mismatch, merge conflict, unknown mergeability, or insufficient actor rights | `BLOCKED_SAFETY`, exact blocker |
| Unknown/unproven user grant despite green CI + PASS | `BLOCKED_PERMISSION`; Board/worker authored plans do not override it |
| DRAFT QA/report-only PR approved/merged | QA report acceptance is not source merge; inspect source separately and apply source authority |
| Claimed authorized closeout ended with only «следующее действие — merge» | FAIL route: require actual `MERGED` or new concrete `BLOCKED` reason on this turn |
| User grant only for deploy/Dossier/manual run | `BLOCKED_PERMISSION` for unrelated source PR merge |
| Source already merged, repeated STATUS or MERGE request | `ALREADY_MERGED` with original SHA; no second merge; production still unverified |

**Cold read-only negative probe:** queried live metadata of independent report-only DRAFT PR #360 twice with a fresh pure-STATUS/no-source-grant branch; HEAD `2255fb222ad827443200911e490d551fe9743a28`, `state=open`, `draft=true`, `merged=false` unchanged before/after. Zero write or merge tool called. This is a real live no-write check, **not** a fresh separately instantiated Director-chat behavioral test. The positive path cannot safely be action-tested without separately authorized harmless test PR; no real test merge performed.

## Validation gates and limitation
- Prewrite asserted exactly one matching STATUS/DECIDE/MERGE table, preserved L3 independent QA, authorization, risk levels and production split. GitHub diff must show only the two allowed files.
- Existing site-task and backlog workflows must succeed on **exact final PR HEAD**; `get_commit_combined_status` alone is insufficient evidence of GitHub Actions. Final live CI verdict belongs to the checked PR HEAD, not a promised future run.
- Procedural text has no mechanical ability to force a ChatGPT tool call. Separate future cold Director execution remains a residual behavioral risk, not a claimed tested guarantee.

## Risk and rollback
**Risk:** Director could mistakenly interpret a Board item/QA PASS as user grant, or fail to act on an actual grant; main branch enforcement may not technically prevent unsafe direct merges. Fail closed on missing provenance, exact HEAD/CI/QA/rights. **Rollback:** revert the one `DIRECTOR_PROTOCOL.md` delta if a pure STATUS starts auto-merging, Board is treated as consent, or required L3 checks are relaxed; a bad historical merge cannot be undone safely by reverting prose alone.

## Unresolved and closeout
- No independent live authorized harmless positive merge test (forbidden without fresh explicit permission).
- User approval provenance from the old #346 conversation remains unproven; #346 already merged, do not re-merge.
- Live Steam site / production acceptance is not verified or granted.
- **Status:** `complete` for bounded protocol implementation; **merge disposition:** `READY_FOR_DIRECTOR_MERGE` after exact-final-HEAD site-task/backlog `success`, otherwise `BLOCKED_CONCRETE` with the exact failed/incomplete run. Worker does not self-merge.
- **Recommended next step:** Director reviews this L1 PR and merges only after current final-HEAD existing CI GREEN and a valid user MERGE authorization; no new independent QA absent actual L3 risk.
- **Efficiency / reusable lesson:** route/pitfall candidate is contained in audit #360 and addressed within existing §1, without adding a separate register, workflow or global checklist.
