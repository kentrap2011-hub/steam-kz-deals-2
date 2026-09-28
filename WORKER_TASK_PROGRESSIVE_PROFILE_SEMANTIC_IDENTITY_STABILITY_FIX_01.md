# WORKER TASK — PROGRESSIVE PROFILE SEMANTIC IDENTITY STABILITY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `progressive-profile-semantic-identity-stability-fix-01`
Mode: `CONTRACT-FIRST IMPLEMENT / RECONCILE / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-profile-semantic-identity-stability-fix-01.md`

## Explicit user authorization

The user explicitly authorized this fix.

The user does NOT authorize:
- rerunning the already completed 30-game Deep migration merely because of the current identity bug;
- changing Scheduled Task configuration;
- manual Deep/Fast/Dossier backlog processing;
- weakening immutable provenance or exact-input execution binding.

## Accepted diagnosis

Use the accepted diagnostic as authoritative unless current `main` materially contradicts it:

`reviews/worker_reports/deep-migration-results-not-reflected-on-site-diagnostic-01.md`

Accepted facts:

1. PPD-010 migration completed successfully:
   - 30/30 accepted completed;
   - 26 analyzed_fit;
   - 4 analyzed_not_fit;
   - 0 incomplete;
   - 23 confirmed-risk;
   - 7 caution.
2. Those 30 results remain durably stored.
3. They disappeared from current Deep/card/ranking/statistics surfaces because the current Progressive semantic identity changed.
4. The actual Taste profile bytes did NOT change:
   - profile blob remained `9b9926031889dbd98ba6585c57836d52c739a0bb`;
   - profile content SHA-256 remained `e2d5f363778d83ec9fdd269f29744356c1b777201fb3dc0c56e898dbd99a44b4`.
5. Only the immutable profile provenance commit changed:
   - old resolved commit `feb5e74d5d3d95000612ee2888926618001e6424`;
   - later resolved commit `09f4901ff0eef5b6fda15f32ff43d53907df7072`.
6. That provenance-only commit change changed `profile_pin_sha256`, then the global `semantic_generation_id`, then every derived current Deep work identity.
7. As a consequence, all 30 valid completed migration results became non-current and were re-emitted as ordinary Deep work even though the semantic profile content was unchanged.
8. This affects cards, ranking, risk/caution projection and Deep statistics, not only the Statistics page.
9. The separate Dossier/Deep release-year compatibility issue was already fixed by PR #111 / PPD-011 and must remain intact.

Do not re-diagnose the accepted root cause from scratch unless current `main` contradicts these facts.

## Goal

Implement a stable Progressive semantic identity model in which:

- immutable profile provenance remains exact and auditable;
- execution still freezes an exact immutable profile source/ref/commit/blob;
- a provenance-only source commit change with byte-identical semantic profile content does NOT create a new global semantic generation;
- a real semantic profile content change DOES create a new semantic generation;
- model/semantic-contract/context-contract changes still create a new semantic generation according to existing rules;
- item-level fingerprint/context changes still create new item work identities according to existing rules;
- previously accepted Deep/Fast results remain current only when their semantic inputs are provably equivalent under the new contract;
- arbitrary historical results cannot be revived by weakening matching.

The already completed 30 PPD-010 migration results must become current again WITHOUT another semantic Deep run if the implementation proves their only relevant mismatch was provenance-only profile commit churn.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. accepted diagnostic report;
4. relevant Progressive routes in `PROJECT_ROUTES.md`;
5. PPD-004, PPD-006, PPD-007, PPD-008, PPD-009, PPD-010, PPD-011 and any profile-pin decisions;
6. current Progressive/Fast/Deep contracts;
7. current profile pin / semantic generation contract(s);
8. `config/execution_ownership_contract.json`;
9. current PASS 1/PASS 2 state and work projection;
10. only the smallest implementation/tests/workflows needed.

## Mandatory architecture preflight

Before writes, prove:

1. GitHub remains sole owner of:
   - profile resolution/pinning;
   - semantic generation;
   - work identities;
   - eligibility;
   - attempts/recovery;
   - result acceptance;
   - persistence;
   - current-result selection;
   - visual publication.
2. Scheduled ChatGPT remains bounded semantic execution only.
3. No new scheduler, recurring stage, retry loop, queue owner, backlog manager or checkpoint authority is created.
4. Exact execution provenance is NOT weakened:
   - a semantic invocation still binds to one exact immutable source commit/ref/blob/profile artifact selected by GitHub;
   - results still carry enough exact provenance to prove what bytes were actually used.
5. Dossier remains independent.
6. PPD-010 migration history remains immutable/auditable.
7. PPD-011 release-year compatibility remains unchanged.
8. No whole-`main` stability rule is reintroduced.

If current canonical decisions do not distinguish **semantic profile identity** from **execution provenance identity**, add the smallest new canonical decision (for example PPD-012) BEFORE runtime changes.

## Required semantic/provenance split

The contract must explicitly distinguish:

### A. Semantic profile identity

This is the material that determines whether the user's Taste semantics changed.

It must be based on semantic content, such as:
- exact profile content/blob identity;
- canonical profile content SHA;
- relevant taste model version;
- taste semantics binding;
- candidate-context contract binding;
- other genuinely semantic inputs already required by the existing generation model.

A source commit/ref must NOT change this semantic identity by itself when the semantic profile bytes and all other semantic inputs are identical.

### B. Execution provenance identity

This records exactly where the bytes came from for a given prepared invocation:
- repository/source;
- resolved commit;
- blob;
- content SHA;
- path/ref as applicable;
- immutable preparation provenance.

This remains strict and exact for run-start/work/result validation and audit.

The semantic identity and provenance identity may both be stored/bound, but they must not be conflated.

## Required invalidation rules

Prove with tests:

### Must NOT invalidate current semantic results

- only `resolved_commit_sha` changes;
- profile blob/content SHA is identical;
- taste model version identical;
- taste semantics identical;
- candidate-context contract identical;
- item fingerprint/context identical.

### MUST invalidate / create new semantic identity

- profile content bytes change;
- profile content SHA changes;
- taste model version changes;
- taste semantics binding changes;
- candidate-context contract changes;
- relevant item fingerprint/context changes according to existing item-level rules.

### Fail closed

Do NOT treat semantic equivalence as proven when:
- profile content hash/blob is missing or inconsistent;
- provenance does not resolve to the claimed bytes;
- current contract version/binding is incompatible;
- result lacks enough historic semantic material to prove equivalence;
- product/work/item identity differs.

## Historical/current result reconciliation

This task must not merely prevent future churn. It must safely reconcile the already completed Deep results.

Required rule:

- keep every historical accepted result immutable;
- do not rewrite its original run-start/provenance fields;
- derive current-result equivalence through a GitHub-owned compatibility/reconciliation rule;
- promote/reuse an existing durable Deep result as current only when exact semantic equivalence is proven under the new contract;
- do not count this as a new semantic attempt;
- do not create a fake new worker result;
- preserve original acceptance time and result provenance;
- expose any compatibility/reconciliation provenance separately if needed.

For the 30 PPD-010 migration results, prove:
- same semantic profile bytes;
- same relevant taste model/semantics/context contract;
- same AppID/taste subject/fingerprint/context;
- only provenance commit/profile pin wrapper changed;
- therefore no semantic rerun is necessary.

If any of the 30 fails exact semantic-equivalence proof on fresh `main`, fail closed for that item and report it; do not force reuse.

Also inspect the two other durable non-migration Deep completions identified by the accepted diagnostic. Apply the same rule generically rather than hard-coding only the migration 30.

## Work projection after reconciliation

After implementation and normal deterministic recomputation:

- semantically equivalent completed Deep results must NOT be emitted again as `normal_first_pass`;
- PPD-010 30 completed migration targets should return to current authoritative Deep coverage if equivalence is proven;
- only genuinely not-yet-current Deep items remain ready/pending;
- no PASS 2 attempt is consumed merely by reconciliation;
- no recovery authorization is created;
- no old create-only result transport path is reused incorrectly.

Because PR #111 repaired 8 Dossier compatibility items, current ordinary Deep readiness may have changed. Do not hard-code an expected final queue count. Report exact fresh arithmetic after removing semantically already-completed items.

## Fast / shared generation implications

The Progressive global semantic generation is shared infrastructure.

Inspect whether Fast/PASS 1 uses the same profile semantic identity material.

Required:
- avoid fixing only PASS 2 if the same provenance-only churn can invalidate Fast current results;
- preserve existing Fast exact execution provenance;
- do not retroactively invent Fast completions;
- add regression that byte-identical profile provenance refresh does not invalidate otherwise-current Fast state when semantic inputs are unchanged.

Do not expand into unrelated Fast behavior.

## Interaction with PPD-010 migration

PPD-010 remains a finite completed migration.

Do not:
- reopen migration pending state;
- rebuild its frozen target manifest;
- rerun any migration item;
- change original migration result payloads;
- erase revision history;
- reinterpret migration attempts as normal first-pass attempts.

The completed migration observability must remain complete 30/30.

After reconciliation, migrated results may become current authority again through semantic-equivalence selection, not by mutating PPD-010 history.

## Interaction with Dossier

Dossier may continue independently.

Do not:
- pause Dossier;
- alter Dossier scheduler;
- manually process backlog;
- rebuild dossiers as part of this fix.

A later Dossier change can still affect Deep eligibility/evidence under existing current compatibility rules. This task changes profile semantic identity stability, not Dossier freshness semantics.

## Production concurrency / fresh-main reconciliation

Immediately before merge:

- reread fresh `main`;
- preserve concurrent Dossier progress;
- preserve current Deep/FAST accepted results;
- preserve any new PASS 2 ordinary results that may have appeared;
- do not overwrite worker receipts/state using stale branch copies.

If ordinary Deep was manually or naturally run during this task and duplicated any of the 30 due to the known bug:
- do not delete data blindly;
- reconcile by canonical current-authority rules and report the exact situation;
- do not fabricate history.

## Required regressions

At minimum:

1. same profile bytes + new provenance commit => same semantic profile identity;
2. same profile bytes + new provenance commit => existing current Deep remains current;
3. same profile bytes + new provenance commit => existing current Fast remains current where applicable;
4. profile content byte change => new semantic identity;
5. taste model change => new semantic identity;
6. taste semantics binding change => new semantic identity;
7. candidate-context contract change => new semantic identity;
8. item fingerprint/context change => correct item-level invalidation;
9. missing/inconsistent content identity => fail closed;
10. arbitrary old result with different semantic content cannot be revived;
11. PPD-010 30 migration results reconcile without new semantic attempts when equivalence is proven;
12. those 30 are not re-emitted as ordinary Deep work after reconciliation;
13. migration remains complete 30/30;
14. PPD-011 eight repaired Dossier identities remain eligible as applicable;
15. run-start exact provenance remains strict;
16. result transport/authorization remains strict;
17. no Scheduled Task behavior changes.

## End-to-end validation

After merge, via normal GitHub-owned deterministic rebuild/publication paths, verify:

### Deep state
- exact authoritative completed count;
- fit/not-fit/incomplete;
- current Deep last-write timestamp;
- ready/pending;
- waiting for Dossier;
- remaining until authoritative completion;
- migration observability still complete.

### User-facing state
Verify a bounded sample including:
- STAR WARS Jedi: Fallen Order (1172380) if still in the 30;
- at least one migration confirmed-risk result;
- at least one migration caution result;
- at least one of the four migration not-fit results.

Prove:
- card uses current Deep result;
- positive reasons preserved;
- negative risk/caution preserved;
- not-fit result is represented according to normal current Deep rules;
- ranking/personalized score uses current Deep where it should;
- Statistics no longer shows zero merely because of provenance-only pin churn.

### Publication
Verify normal visual build and Pages deploy if they are triggered by the canonical path.

Do not manually clear service-worker/browser caches as a substitute for correct artifact publication.

## Hard prohibitions

Do not:
- rerun the 30 migration targets semantically;
- manually run Deep/Fast/Dossier;
- manually rewrite accepted Deep result payloads;
- replace immutable original provenance;
- make `resolved_commit_sha` disappear from audit/provenance;
- accept profile equivalence on title/path alone;
- weaken result/work/run-start exact binding;
- change ranking weights/risk policy;
- change PPD-011 release-year fix;
- create new scheduler/queue/retry logic;
- change Scheduled Tasks.

## Report

Write:
`reviews/worker_reports/progressive-profile-semantic-identity-stability-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Canonical semantic/provenance decision`
4. `Accepted root cause`
5. `Changes`
6. `Semantic identity regressions`
7. `Provenance / fail-closed regressions`
8. `Deep historical reconciliation`
9. `Fast compatibility`
10. `PPD-010 migration preservation`
11. `PPD-011 preservation`
12. `Production concurrency reconciliation`
13. `Validation`
14. `Current Deep counters`
15. `Published card/statistics result`
16. `Unresolved`
17. `Status`
18. `Recommended next step` — exactly one bounded next step
19. exact PR/commit/run/artifact refs
20. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.
