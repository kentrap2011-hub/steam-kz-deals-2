# WORKER TASK — PROGRESSIVE RUNTIME RULE RATIONALE CONSISTENCY AUDIT 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `progressive-runtime-rule-rationale-consistency-audit-01`
Mode: `READ-ONLY / RECON / ARCHITECTURE AUDIT`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-runtime-rule-rationale-consistency-audit-01.md`

## User intent

The user wants a broad audit BEFORE any further repair.

The goal is not to find rules that merely look inconvenient and delete them. For every suspicious runtime/control rule, first determine:

1. Why was this rule introduced?
2. Which concrete invariant/problem was it intended to protect?
3. Is that original reason still valid under the current architecture?
4. Has another accepted mechanism since replaced the original protection?
5. Does the current implementation enforce a stronger restriction than the underlying invariant actually requires?
6. If the rule is changed, can the original safety/property still be preserved?
7. Is the change straightforward, or does it require a Director/user decision because there are real trade-offs?

After this audit the Director/user will discuss disputed findings. Only AFTER that discussion will a separate IMPLEMENT task be authorized for the agreed fixes.

Do not implement fixes in this task.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Repository scope:
- work only in `kentrap2011-hub/steam-kz-deals-2`;
- for profile-binding rationale, read-only access to the already-canonical external profile authority `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json` is allowed only if actually needed;
- do not inspect unrelated repositories.

## Mandatory canonical reading

Read current:
- `DIRECTOR_TASK_BOARD.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- current PASS 1 / Dossier / PASS 2 work manifests and directly referenced persistence/validation logic as needed.

Historical rationale must be traced through the smallest relevant subset of:
- accepted `PROJECT_DECISIONS.md` entries;
- exact worker task/report pairs that introduced or later changed a suspicious rule;
- Git history / introducing commit when necessary to resolve why a rule exists.

Do not read large unrelated history merely for completeness.

## Confirmed seed example

Treat this as a confirmed example to explain and use as an audit pattern, NOT as proof that every similar-looking guard is wrong:

Current PASS 1 prompt now says, before every new item, to reload current GitHub work and take the exact next current item.

This was introduced by the pinned live-profile handoff fix. The immediately preceding PASS 1 behavior allowed multiple consecutive GitHub-prepared items in one invocation and required independent per-item create-only artifacts. Canonical PPD-002 says:
- PASS 1 is item-level and coverage-first;
- insufficient/invalid/failure of one item must not block later items;
- worker may process multiple consecutive items per invocation;
- batch atomicity/maximal contiguous prefix are not PASS 1 authority.

Observed production symptom:
- KOF XV produced a valid new pinned-generation `analyzed_fit` result;
- worker reread the still-not-yet-ingested manifest, saw the same first item and stopped;
- GitHub later ingested it successfully and advanced to 1 attempted / 530 remaining.

Audit whether this current reload rule accidentally reintroduced a GitHub round-trip dependency that PPD-002 intended to avoid.

Also audit the broader question:
- should semantic workers ever wait for canonical GitHub ingest before processing the next already-predeclared immutable work item/group?
- if not, what exact transport-level fact is sufficient to move on while GitHub canonical acceptance remains asynchronous?
- across a later Scheduled invocation, may an existing exact create-only submission artifact be treated only as “already submitted, do not recreate” while still NOT being treated as canonical acceptance?

Do not assume the answer. Prove it against current manifests, transport semantics, validators, ownership rules and historical rationale.

## Audit scope

Audit current production Fast / Dossier / Deep semantic runtime for analogous **rule-purpose drift**.

Search specifically for:

### A. Unnecessary GitHub round-trip waits
- worker waits/reloads/polls for ingest or manifest advancement after a create-only submission even though later work was already immutably predeclared;
- next work is blocked only because canonical state has not caught up with transport state;
- run/day throughput is unintentionally reduced to one item/group per GitHub round trip.

### B. Head-of-line / global barriers that conflict with independent progress
- one failed/incomplete/stale item blocks unrelated siblings/later work despite item/group independence;
- residual maximal-prefix/group-completion assumptions after architecture moved to non-blocking per-item/per-group progress;
- global PASS 1/PASS 2/Dossier completion waits that no longer match current independent-stage architecture.

### C. Mutable-currentness checks applied where immutable pin authority should suffice
- rules that force a worker/result to match mutable latest `main` after exact work was already durably pinned;
- rebuild/reload before ingest that accidentally invalidates legitimate in-flight pinned work;
- profile/Dossier/work currentness checks whose original reason has already been replaced by exact immutable pin/liveness proof.

Important: distinguish profile pinning from Dossier liveness. Current Deep Dossier expiry/current-compatibility checks may remain necessary even when profile currentness does not.

### D. Create-only collision semantics
- exact submission already exists but worker treats that as a fatal stop rather than “already submitted” when later immutable work is independent;
- determine separately for:
  - valid-looking exact transport awaiting ingest;
  - already canonically accepted transport;
  - malformed/invalid exact transport;
  - stale/wrong-generation/wrong-snapshot transport.
- Never recommend silently overwriting or renaming immutable artifacts.

### E. Worker/control-plane ownership overreach
- ChatGPT is forced to wait for GitHub to decide something already deterministically encoded in an immutable plan;
- OR the opposite: removing a wait would accidentally make ChatGPT own queue state, retry eligibility, recovery, canonical acceptance, completeness or scope.

A proposed relaxation is acceptable only if GitHub still owns canonical truth and ChatGPT merely traverses an already-authorized immutable plan.

### F. Redundant revalidation/rebuild rules
- repeated expensive or blocking checks whose protected invariant is already guaranteed by an immutable identity;
- duplicate current-manifest rebuilds before accepting an exact historical prepared work item;
- liveness checks that are correctly necessary and therefore should be explicitly classified KEEP, not “optimized away”.

### G. Attempt/recovery rules
- one-attempt or recovery guards whose original rationale remains safety-critical;
- rules that accidentally convert “submitted but not yet ingested” into a consumed attempt or permanent blocker;
- rules that prevent unrelated work while one item is recovery-owned.

### H. Cross-stage coupling
- Fast waiting on Deep or Deep waiting on Fast contrary to PPD-004;
- Dossier progress unnecessarily waiting on personalized semantic stages;
- downstream stage projection incorrectly requiring synchronous acceptance of an unrelated stage.

## Required reasoning discipline

For every finding, do NOT write only “this is inefficient”.

Create a **Rule Rationale Matrix** with these columns:

`ID | exact current rule/path | introduced/changed by | original problem/rationale | invariant that still matters | current architecture that now protects it | current runtime effect | classification | safe change boundary | risk if changed incorrectly | proposed minimal correction`

Allowed classifications:

- `KEEP_AS_IS` — restriction is still necessary and proportionate.
- `KEEP_INVARIANT_CHANGE_MECHANISM` — safety goal remains, but current mechanism is stronger/blocking and can be replaced.
- `REMOVE_SUPERSEDED_RULE` — original rationale is fully covered by newer canonical machinery.
- `BUG_REGRESSION` — current behavior directly contradicts an accepted current decision/contract.
- `NEEDS_DIRECTOR_DECISION` — more than one legitimate policy choice remains.
- `UNKNOWN_INSUFFICIENT_EVIDENCE` — provenance/rationale cannot be proven.

Do not classify based only on age. A historical rule can remain correct.

## Required special analysis: asynchronous transport vs canonical acceptance

Produce a dedicated section explaining the exact state machine for each stage:

### Fast
Distinguish:
- GitHub-prepared immutable item;
- no submission yet;
- exact create-only submission exists;
- GitHub has not yet ingested it;
- accepted;
- rejected/invalid;
- current work generation later advances.

Determine whether the worker can continue to later predeclared items without waiting and how a later invocation safely avoids resubmitting the same exact path.

### Dossier
Compare current implementation to the accepted buffered/non-blocking rationale already in `PROJECT_DECISIONS.md`. Determine whether any old “wait for manifest advancement” behavior remains.

### Deep
Determine whether current exact work/authorization/profile pin permits buffered multi-item semantic transport without waiting for prior Deep ingest, and identify any Dossier-expiry/current-authorization constraints that make Deep materially different from Fast.

Do not assume Fast rules can be copied mechanically to Deep.

## Historical rationale / supersession proof

For every recommended change, identify at least one of:
- current canonical decision that the rule conflicts with;
- exact later mechanism that superseded its original protection;
- introducing task/commit and later architecture change that made the implementation stronger than necessary.

For every `KEEP_AS_IS`, state the concrete failure it still prevents.

## Fix planning — design only

For each finding not classified KEEP, propose a smallest safe fix design. Do not modify files.

Each fix design must state:
- files/contracts likely affected;
- whether work/result schema must change;
- whether semantic identity must change;
- whether existing submitted artifacts remain valid;
- whether attempt/recovery state changes;
- whether Scheduled Task prompt/config must eventually be changed by the user/operator;
- exact regression/live acceptance tests needed;
- whether it can be bundled with other findings safely.

Group proposed fixes into:
1. `SAFE_BOUNDED_FIXES` — no unresolved product/policy choice.
2. `DISCUSSION_REQUIRED` — Director/user should decide before implementation.
3. `KEEP_NO_CHANGE`.

Do NOT produce a ranked “best choice”; describe the trade-offs on discussion items.

## Specific acceptance questions

Answer explicitly:

- AUD-01: Is the current PASS 1 per-item manifest reload a regression relative to PPD-002? Prove exact provenance.
- AUD-02: Can PASS 1 safely continue through already-predeclared items without waiting for GitHub ingest?
- AUD-03: On a later invocation, can exact existing create-only artifacts be used solely as transport-progress markers without treating them as canonical acceptance? Under what exact validation conditions?
- AUD-04: Does any current PASS 1 rule still create head-of-line blocking after PPD-002?
- AUD-05: Does Dossier still contain any round-trip wait that contradicts its accepted buffered/non-blocking architecture?
- AUD-06: Does Deep contain analogous unnecessary ingest waits, and which current liveness/authorization checks must remain?
- AUD-07: Are there any mutable-latest checks that conflict with the newly accepted immutable profile pin model?
- AUD-08: Are Fast/Dossier/Deep still independent in actual current runtime behavior, not only contract prose?
- AUD-09: Are create-only collision behaviors proportionate for valid-awaiting-ingest vs invalid/stale artifacts?
- AUD-10: Are attempt/recovery semantics free of “submitted but not yet ingested = blocked/consumed” errors?
- AUD-11: Identify all current rules whose original rationale has been superseded but implementation remains.
- AUD-12: Identify all suspicious restrictive rules that must NOT be removed because their rationale remains live.
- AUD-13: Produce complete `SAFE_BOUNDED_FIXES / DISCUSSION_REQUIRED / KEEP_NO_CHANGE` sets.
- AUD-14: No repository/runtime/scheduler/production mutation occurred.
- AUD-15: durable report committed and reread from fresh `main`.

## Explicit prohibitions

This task is READ-ONLY.

Do not:
- change code, contracts, prompts, workflow files, schemas, state, manifests or site files;
- create/delete/update/enable/disable/pause/reschedule/rename/recreate any Scheduled Task;
- run Fast, Dossier or Deep semantic production;
- dispatch ingest/recovery/production workflows;
- edit or remove existing transport artifacts;
- authorize Deep recovery;
- reset attempt state;
- “fix” a rule merely because it slows throughput;
- weaken exact identity, profile pin, Dossier identity/freshness, one-attempt, recovery authorization, privacy/evidence or canonical acceptance rules without proving how their original invariant is preserved.

Normal external production may continue independently. Record observations only if materially relevant.

## Durable report

Create and commit only:
`reviews/worker_reports/progressive-runtime-rule-rationale-consistency-audit-01.md`

Required sections:
1. Executive summary.
2. Scope and source-of-truth refs.
3. Audit method.
4. Confirmed PASS 1 seed regression provenance.
5. Rule Rationale Matrix.
6. Fast asynchronous transport vs canonical acceptance state machine.
7. Dossier state machine and current conformity.
8. Deep state machine and necessary differences from Fast.
9. Cross-stage independence audit.
10. `SAFE_BOUNDED_FIXES`.
11. `DISCUSSION_REQUIRED`.
12. `KEEP_NO_CHANGE`.
13. AUD-01..15.
14. Exact files/commits/tasks/reports used as rationale evidence.
15. Uncertainties / evidence limits.
16. Final status.
17. Exactly one recommended Director next step: discuss disputed items and then issue one coordinated IMPLEMENT task only for the approved findings.

Allowed final statuses:
- `complete_ready_for_director_review`
- `needs_more_recon`
- `needs_user_decision`
- `blocked`

Before completion, commit the report and reread that exact committed report from fresh `main`.
