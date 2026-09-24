# Progressive Runtime Rule Rationale Consistency Audit 01

**Task:** `progressive-runtime-rule-rationale-consistency-audit-01`  
**Mode:** READ-ONLY / RECON / ARCHITECTURE AUDIT  
**Repository / source of truth:** `kentrap2011-hub/steam-kz-deals-2` / `main`  
**Final status:** `complete_ready_for_director_review`

## 1. Executive summary

The confirmed PASS 1 seed is a real runtime-rule regression.

PPD-002 intentionally made Fast/PASS 1 item-level, coverage-first and sibling-independent: a worker may process multiple consecutive predeclared items in one invocation, each through its own immutable create-only artifact, and one item's failure must not block later items. The original PASS 1 prompt implemented that model. The later pinned-profile handoff fix correctly introduced an exact immutable live-profile pin and Git-history work authority, but commit `4e9b2f84c77a59df89afdef5d126362ce5f16c4e` also changed the stale-work rule to: before every new item reload current work and take the exact next item currently prepared. When the just-created artifact is not yet ingested, GitHub still projects that same item first, reintroducing a one-item-per-ingest round trip. That is stronger than the profile-pin invariant requires and contradicts PPD-002.

Current architecture already contains the protection the pin fix actually needed: every prepared Fast/Deep item binds an immutable profile pin; workers fetch and verify exact pinned profile bytes; later mutable profile changes do not invalidate started pinned work; ingest resolves exact historical pre-semantic work authority from Git history instead of requiring mutable latest `main`. Therefore canonical acceptance may remain asynchronous without forcing a Fast worker to wait before processing later already-predeclared independent items.

Dossier is materially different. Its normal same-invocation runtime already buffers groups without waiting for ingest. The remaining rule that stops on an exact existing-but-still-pending deterministic Dossier artifact is deliberate, not an accidentally retained old maximal-prefix rule: the g000012 incident and the later canonical-writer coalescing fix explicitly preserved “worker must not skip this unclassified group” while making GitHub state-based reconciliation coalescing-safe. Changing that would be a new ownership-policy decision, not a straightforward bug fix.

Deep is also different from Fast. It may process independent siblings without prior sibling acceptance, but every item still needs current exact Dossier liveness and, for recovery, current explicit GitHub authorization. The per-item manifest reload introduced by the same profile-pin fix should be a liveness/authorization check, not evidence that the previous item was ingested. A separate Deep defect/risk exists for malformed current transport: invalid Deep result/receipt is intentionally rejected with **no attempt consumed**, but current ingest leaves that immutable active path in place. The item can remain authorized while its only create-only path is occupied. That requires a Director decision on transport-recovery semantics; it must not be silently converted into either automatic retry or consumed attempt.

No current cross-stage semantic prerequisite was found contrary to PPD-004. Deep eligibility code does not require Fast completion; Fast only suppresses future work for the same identity after current authoritative Deep completion; Dossier remains neutral and independent. The shared GitHub canonical-writer concurrency boundary serializes canonical writes to avoid stale projection overwrite; it is persistence synchronization, not semantic-stage waiting.

## 2. Scope and source-of-truth refs

Fresh-main canonical blobs at the final audit read:

- `config/progressive_pass1_worker_prompt.md`: `5f52466ddb7a3e79bb26dc46ca33e9ed65117a76`
- `config/progressive_pass2_worker_prompt.md`: `56768ad846b532804ccad666f34ef8481c1f1c5d`
- `config/taste_steam_review_dossier_worker_prompt.md`: `b0febcfa6685744b8b21efe69647d6bbb8938718`
- `config/progressive_pass1_contract.json`: `8fd575aea7d3f1bf0a3f0608cfe8943c5b75a814`
- `config/progressive_pass2_contract.json`: `ff08eacbec400809e7d6f057cbce9992abb4f80b`
- `config/taste_steam_review_dossier_contract.json`: `c9765f9a3330f90aa00899309949e5348e6bcb21`
- current Fast work: blob `effd58c2524069b2c5d3b541fd40f9efd0ee64bb`, generation `b33cc4416860bd15a37f530c9daef8fb7755ae440929f93aa915d5363e31c490`, 529 prepared remaining items
- current Deep work: blob `86a611f375d46c3162aa90173cc3da24568c7cb5`, same generation, 29 currently prepared items
- current Dossier worker index: blob `d70004649c490d968cb8b252a94dbc480541ad10`, snapshot `4531598188b3d3173e38363c46f202f6eb02f78a4ec56e1775632cfde45fbbfd`, next pending sequence 5, 173 total groups

At that read Fast scope was 531 = 2 attempted + 529 remaining, with both current attempted results completed fit. Deep scope was 531, with 1 first-pass attempted/recovery-owned, 29 ready/pending and 501 waiting for Dossier. These counts are observations only; normal production may advance after this report.

The active inbox directories for Fast, Deep result/receipt and Dossier had no tracked files at the final audit read; GitHub returned no directory content for those empty paths. Therefore collision findings below are current **rule/code-path** findings, not claims that an unclassified artifact is presently stranded.

## 3. Audit method

1. Executed the current `CHAT_PROTOCOL.md` START gate and read the task before broad task-specific search.
2. Read current ownership/contracts/prompts/work manifests and the relevant route/decision entries.
3. For suspicious rules, traced the smallest relevant provenance: introducing decision/task/report and exact Git commit where needed.
4. Compared worker prompt semantics with actual ingest/persistence code rather than relying on prose.
5. Separated immutable-profile authority from mutable Dossier liveness and recovery authorization.
6. Treated transport existence, canonical acceptance, attempt consumption and recovery ownership as different states.
7. Made no code/contract/prompt/workflow/state/manifest/scheduler/production changes. The only repository write authorized by this task is this report.

## 4. Confirmed PASS 1 seed regression provenance

### Original rule and intent

PPD-002, recorded with the Phase B item-level implementation, says:
- PASS 1 is item-level and coverage-first;
- one insufficient/invalid/failing item cannot block later items;
- worker may process multiple consecutive items in one invocation;
- every item has its own immutable create-only artifact;
- batch atomicity and maximal contiguous-prefix progress are not authority.

The original worker prompt added in `4bb7e822f3275fc922d32105fc922f2966f14577` states the same behavior: submit A, then move on; B failure must not block C; there is no fixed batch quota. Its stale-work protection only required each submission to originate from the manifest read for that invocation and prohibited adapting an old result to a new binding.

### Change that introduced the regression

Pinned-profile handoff core commit `4e9b2f84c77a59df89afdef5d126362ce5f16c4e` correctly added:
- exact `PROGRESSIVE-PROFILE-PIN-V1`;
- exact commit/blob/byte/SHA verification of profile content;
- per-item `profile_pin_sha256`;
- Git-history pre-semantic work authority;
- acceptance of legitimate historically prepared in-flight work despite later profile/main drift.

The same commit changed Fast stale-work text to:
> before starting each new item, reload current GitHub work and take only the exact next item GitHub currently prepares.

That conflates two different concepts:
- **newly prepared work**, which should use then-current profile/identity; and
- the **next already-predeclared item in an existing immutable work manifest**, which PPD-002 already authorizes independently.

Observed KOF XV behavior is the direct consequence: after its exact pinned result was created but before GitHub ingest advanced canonical state, the reloaded manifest still exposed KOF XV first and the worker stopped instead of continuing.

PASS 1 ingest code further proves no canonical sibling dependency exists: `scripts/ingest_progressive_pass1.py` scans all inbox artifacts, resolves exact historical work authority for each, and ingests independent artifacts together. `scripts/progressive_pass1.py::process_submission_documents` explicitly processes siblings without rollback. The accepted coactive-ingest recovery also canonically ingested five already-existing Fast artifacts in one run without semantic re-execution.

**Finding:** this is `BUG_REGRESSION`, not a necessary consequence of profile pinning.

## 5. Rule Rationale Matrix

| ID | exact current rule/path | introduced/changed by | original problem/rationale | invariant that still matters | current architecture that now protects it | current runtime effect | classification | safe change boundary | risk if changed incorrectly | proposed minimal correction |
|---|---|---|---|---|---|---|---|---|---|---|
| RRC-01 | Fast prompt: before every new item reload current work and take exact next current item | original stale guard in `4bb7e822…`; strengthened by pinned fix `4e9b2f84…` | prevent adapting stale/mutable-profile work to a new binding | worker may execute only GitHub-prepared exact work with exact profile identity | immutable profile pin + exact profile-byte verification + per-item identity + Git-history work authority | after create-only A, unchanged manifest still exposes A, creating ingest round-trip/HOL before B | `BUG_REGRESSION` | keep exact initial/current manifest authority and pin; remove prior-item ingest advancement as next-item gate | allowing arbitrary non-manifest work would transfer scope/order to worker | traverse later already-predeclared items in order after successful create without waiting for A ingest; current reload may be liveness only |
| RRC-02 | Fast exact deterministic path may already exist while current manifest still lists item; prompt says never revisit but does not define later-invocation traversal | PPD-002 transport + current prompt; exposed by RRC-01 | preserve create-only immutability and prevent duplicate semantic attempt | no overwrite/rename/alternate path; canonical acceptance stays GitHub-owned | deterministic current item path, current manifest identity, Git-history authority, sibling-independent ingest | later invocation can otherwise collide with first submitted/unclassified item and stop | `KEEP_INVARIANT_CHANGE_MECHANISM` | exact path occupancy may mean only “submitted”; it must never mean accepted/attempted | treating any similarly named/stale file as progress could skip unauthorized work | for Fast only, if current manifest item’s exact `submission_path` exists on current repo state, mark it locally “already submitted, do not recreate” and continue to later manifest items; never project acceptance |
| RRC-03 | Fast exact current malformed/invalid semantic payload becomes `accepted_as_incomplete_invalid_result` and consumes that item’s one PASS 1 attempt | PPD-002 implementation `4bb7e822…` / current `process_submission_documents` | one-shot coverage-first progress; invalid item must not indefinitely retry/block siblings | no blind retry; exact item gets terminal honest incomplete state | item-level state/receipt + independent sibling processing | bad exact current item is consumed as incomplete; later siblings continue | `KEEP_AS_IS` | none | making malformed Fast transport “free” without retry ownership can create loops/locks | keep |
| RRC-04 | Fast/Deep must fetch exact pinned profile content and verify commit/blob/bytes/SHA; mutable profile `main` is not semantic input | pinned handoff fix `4e9b2f84…` | prevent mixed profile generations and remembered/mutable profile drift | semantic result must use exact canonical personalized profile | `PROGRESSIVE-PROFILE-PIN-V1` and exact byte verification | bounded verification cost; no ingest wait required | `KEEP_AS_IS` | none | removing it permits semantic identity mismatch | keep |
| RRC-05 | Deep prompt: before each new item reload current Deep manifest | pinned handoff fix `4e9b2f84…` | newly started Deep work must still have current GitHub authorization while started pinned work survives profile drift | current scope/order/authorization remain GitHub-owned; recovery auth and Dossier liveness must remain current | exact manifest item, profile pin, Dossier SHA/binding/expiry, recovery authorization ID; ingest revalidates Dossier | safe if used as liveness check; ambiguous if interpreted as “previous item must disappear before next” | `KEEP_INVARIANT_CHANGE_MECHANISM` | retain per-item current authorization/liveness; explicitly decouple traversal from prior sibling ingest | freezing arbitrary old Deep plan could execute revoked recovery/stale Dossier work | define reload as liveness/authorization guard only; choose next still-authorized ordered item whose exact result/receipt transport is not already submitted; no prior sibling acceptance wait |
| RRC-06 | Deep immediately revalidates exact canonical Dossier content/binding/expiry before semantic execution and ingest revalidates again | PPD-005 / Deep activation | wall-clock expiry or rebinding can occur after projection | Deep must never consume stale/unaccepted evidence | canonical Dossier store + exact SHA/binding/expiry + ingest `prepared_work_item_dossier_is_live` | may stop one stale item, but consumes no attempt and does not block siblings | `KEEP_AS_IS` | none | removing it permits stale evidence to become authoritative | keep |
| RRC-07 | Deep one normal first pass; unresolved consumed attempt becomes recovery-owned; recovery requires fresh explicit GitHub authorization | Deep core `670e2cf…`, runtime adaptation `e3b5cdc…` | prevent blind retry loops and worker-chosen recovery | attempt/recovery ownership must remain GitHub-only | canonical Deep state, authorization ID/reason/binding, result or terminal receipt consumption | one item can wait for recovery while unrelated normal work continues | `KEEP_AS_IS` | none | relaxing it lets semantic worker invent retry/recovery | keep |
| RRC-08 | Deep invalid current result/receipt => `rejected_invalid_*_no_attempt`; ingest does not remove that active file; prompt refuses rerun when exact path exists | Deep core `670e2cf…`; still current | invalid/stale transport must not falsely consume a semantic attempt | no false attempt consumption; create-only evidence must remain auditable | ingest receipt proves rejection, but no current canonical disposition frees/re-authorizes transport | affected item can remain unconsumed yet its deterministic path stays occupied; siblings remain independent | `NEEDS_DIRECTOR_DECISION` | any fix must be GitHub-owned and distinguish transport correction from semantic retry | auto-delete/retry can create hidden loop; consuming invalid transport changes attempt policy | choose an explicit policy: GitHub-owned invalid-transport quarantine/re-authorization, or deliberate Fast-like terminal consumption; do not silently auto-retry |
| RRC-09 | Dossier after successful create N rereads compact V2 index only for snapshot/plan/binding liveness and may continue to next >N pending group without ingest | TASTE-006 buffered design, TASTE-013 nonblocking progress, V2 alignment `17eba7f…` | remove per-group GitHub round trip without transferring queue ownership | snapshot/plan/binding must remain live; worker must not invent scope/order | immutable predeclared group plan + V2 index + per-group GitHub state | multiple groups can be buffered in one invocation; no normal ingest wait | `KEEP_AS_IS` | none | removing liveness permits publication into superseded snapshot | keep |
| RRC-10 | Dossier later invocation: if exact deterministic artifact exists while group is still canonical pending, do not overwrite/rename/skip; stop and let GitHub classify | g000012 diagnostic + coalescing-liveness task/merge `e69eb97…` explicitly preserved this rule | transport existence alone must not become ChatGPT-owned group progress after a lost wake-up | GitHub alone classifies accepted/failed/pending and recovery | every surviving shared canonical writer now state-reconciles Dossier inbox; PITFALL-007 | exceptional collision waits for GitHub classification; normal successful buffering still proceeds | `KEEP_AS_IS` | changing it is a new ownership-policy decision, not a bug cleanup | worker-side skip could turn transport observation into progress authority and mask canonical-liveness defects | keep current rule; rely on coalescing-safe GitHub reconciliation |
| RRC-11 | Dossier invalid group is quarantined/failed only for itself and removed from normal first-pass traversal | TASTE-013 / nonblocking implementation `79f1c38…` | old maximal-contiguous-prefix made one bad group block hundreds | strict validation must remain fail-closed for affected group without global HOL | per-group pending/accepted/failed state + separate recovery | invalid group no longer blocks later groups | `KEEP_AS_IS` | none | restoring prefix semantics reintroduces proven g000005 blocker | keep |
| RRC-12 | Fast/Dossier/Deep canonical writers share `taste-steam-review-dossier-canonical-writer` serialization | PPD-005 + Dossier coalescing fix | concurrent writers/rebases could overwrite Deep eligibility derived from stale Dossier/attempt truth | one canonical ordered persistence boundary | state-based Dossier reconcile + recompute hooks in all shared writers | GitHub writes serialize; semantic stages do not wait for each other as prerequisites | `KEEP_AS_IS` | none | splitting writers reopens stale-projection race | keep |
| RRC-13 | Deep eligibility reads Fast state only for observability; no Fast prerequisite. Fast suppresses future work only after same-identity authoritative Deep completion | PPD-004/runtime adaptation `e3b5cdc…` | remove old Fast-incomplete prerequisite while avoiding redundant Fast after final Deep | independent stages with authoritative precedence | `recompute_eligibility`, producer precedence, current-identity matching | Fast and Deep may progress in either order; only same-item final Deep suppresses future Fast | `KEEP_AS_IS` | none | removing same-item suppression wastes work; restoring Fast prerequisite blocks Deep | keep |
| RRC-14 | Ingest resolves exact historical pre-semantic manifest authority from Git history instead of rebuilding mutable-current profile work before acceptance | pinned handoff fix `4e9b2f84…` | profile may advance after valid started work is durably prepared/submitted | exact historical authorization must be provable; stale/unbound work still rejected | artifact introduction commit + ancestor manifest lookup + pin verification + superseded-state guard | legitimate in-flight pinned result survives later `main` drift | `KEEP_AS_IS` | none | reverting to mutable-latest invalidates valid in-flight work | keep |
| RRC-15 | Dossier currentness is not replaced by profile pinning; Deep must use current accepted Dossier, not buffered/failed/stale evidence | PPD-004/005 and Deep contract | neutral evidence has independent freshness/binding lifecycle | Deep authority must rest on current exact evidence | accepted Dossier cache, binding, content SHA, expiry, GitHub recomputation | some items wait/stop independently when evidence is not live | `KEEP_AS_IS` | none | treating profile pin as sufficient would authorize stale Dossier evidence | keep |

## 6. Fast asynchronous transport vs canonical acceptance state machine

1. **GitHub-prepared immutable item** — item exists in current PASS 1 manifest with exact generation, work ID, candidate binding, deterministic `submission_path`, and profile pin.
2. **No submission yet** — worker may execute it in GitHub order using exact pinned profile.
3. **Exact create-only submission exists** — this is transport state only. It means “do not recreate/overwrite this exact item”. It is not canonical acceptance and not yet an attempt in durable Fast state.
4. **GitHub has not yet ingested** — current manifest may still list the item. Under PPD-002 this must not block later already-predeclared siblings.
5. **Accepted** — GitHub ingest writes PASS 1 state/receipt, removes active transport and regenerates work. Valid fit/not-fit/incomplete consumes the one Fast attempt.
6. **Malformed/invalid exact current transport** — current Fast ingest deliberately converts only that item to `analysis_incomplete / invalid_semantic_result`, consumes its one Fast attempt and continues siblings.
7. **Stale/unbound transport** — rejected without mutating current item state; historical exact authority is resolved from Git history where applicable.
8. **Generation later advances** — worker must never adapt an old result to new identity. Already-authorized historical pinned submission can still be validated against its historical manifest; newly prepared work uses the new generation/pin.

### Exact conditions for a later-invocation Fast transport marker

An existing artifact may be used **only** as “already submitted, do not recreate” when all are true:
- fresh current PASS 1 manifest is read;
- the item is explicitly present in that manifest;
- the observed path equals that exact item’s canonical deterministic `submission_path`;
- item generation/work/profile-pin identity is the current manifest identity;
- the file is durably present in current repository state.

The worker must not:
- infer accepted/attempted/completed from that file;
- parse a different path as equivalent;
- use an old-generation artifact to skip current work;
- overwrite/delete/rename it;
- choose retry/recovery.

For Fast, semantic validity of the existing bytes is **not** required merely to skip recreating the transport slot: GitHub owns validation, and current ingest intentionally terminalizes malformed exact current transport as that item’s incomplete attempt. This preserves sibling progress without turning the worker into acceptance authority.

## 7. Dossier state machine and current conformity

1. GitHub fixes a daily snapshot and immutable ordered group plan.
2. V2 index exposes GitHub-owned pending/accepted/failed state and exact next pending group.
3. Worker executes a pending descriptor and create-only writes its exact deterministic candidate.
4. Candidate is **buffered transport, not accepted evidence**.
5. In the same invocation, worker may reread compact index for snapshot/plan/binding liveness and continue to a later still-pending predeclared group **without waiting for group N ingest**.
6. GitHub canonical writer strict-validates every present pending candidate independently:
   - valid -> accepted/persisted;
   - invalid -> failed/quarantined/recovery-owned for that exact group;
   - missing -> remains pending but does not block classification of another present pending group.
7. Accepted/failed groups leave normal first-pass traversal.
8. If a later invocation sees the exact deterministic artifact still present while canonical state remains pending, the current worker stops rather than interpreting that artifact as progress. This is an intentional exceptional ownership guard.
9. The g000012 lost-wakeup defect was fixed on the GitHub side: every surviving writer in the shared canonical-writer domain reconciles repository inbox state, so durable current transport should be classified even if the original wake-up is cancelled.

**AUD conclusion:** no current normal Dossier “wait for manifest advancement after every successful group” remains. The collision-stop rule is not a remnant of old maximal-prefix progression; it was explicitly preserved by the later coalescing-liveness fix.

## 8. Deep state machine and necessary differences from Fast

1. GitHub prepares an exact Deep item only when current Progressive identity and exact accepted Dossier/recovery conditions authorize it.
2. Worker verifies exact profile pin.
3. Immediately before semantic execution, worker must revalidate current canonical Dossier path/content/binding/expiry. Recovery work must also remain exact to its explicit authorization.
4. A valid exact result or valid terminal execution receipt is create-only transport. The worker must never execute the same exact item again merely because canonical ingest has not completed.
5. GitHub ingest resolves historical work authority, revalidates Dossier liveness, then:
   - exact valid result -> consumes attempt;
   - exact valid terminal execution receipt -> consumes unresolved attempt and moves item to recovery-owned;
   - stale/mismatched -> no attempt, removable transport;
   - malformed/invalid current result/receipt -> no attempt.
6. Unresolved consumed first pass never re-enters normal work. A later recovery attempt requires a fresh exact GitHub authorization.
7. Siblings are item-independent; one unresolved/recovery-owned item does not block other normal Deep work.

### Difference from Fast

Fast’s candidate semantic work is fully bound by current item identity + immutable profile pin; once the exact current transport slot is occupied, current Fast ingest has a terminal policy for even malformed exact transport.

Deep has two additional live dimensions:
- Dossier content/binding/expiry can become invalid with wall-clock/current canonical change;
- recovery authorization can change and is item-specific.

Therefore a Deep manifest reread may remain useful before each new item, but it must be treated as a **current liveness/authorization guard**, not as proof that the previous sibling was ingested.

### Deep invalid-no-attempt transport gap

Current `scripts/ingest_progressive_pass2.py::removable_names` removes accepted, accepted-terminal, replay and stale/mismatched artifacts, but not `rejected_invalid_result_no_attempt` or `rejected_invalid_execution_receipt_no_attempt`. Current worker prompt says an existing exact result/receipt path must not be run again.

Thus:
- attempt remains unconsumed;
- work can remain eligible;
- create-only path remains occupied;
- automatic semantic rerun is forbidden;
- no current transport-recovery disposition is defined.

This does not create a global sibling barrier, but can strand the exact Deep identity. Resolving it requires an explicit policy decision.

## 9. Cross-stage independence audit

Actual runtime code matches current PPD-004 stage independence:

- `scripts/progressive_pass2.py::recompute_eligibility` does **not** use Fast completion as a Deep eligibility predicate. It reads Fast only for an observability counter.
- A normal Deep item is emitted from current identity + live accepted Dossier + no current authoritative Deep completion + unconsumed normal first pass.
- Fast builder suppresses only a same-current-identity item whose Deep state is already authoritative complete. Deep waiting/incomplete/recovery does not suppress independent Fast.
- Dossier worker/progress does not wait on Fast or Deep semantic state.
- Dossier persistence triggers Deep work recomputation because accepted Dossier is a legitimate evidence dependency, not because Dossier waits for Deep.
- PASS 1 persistence also triggers Deep recomputation, but current Deep eligibility remains independent of Fast outcome.
- Shared writer serialization prevents stale canonical projection overwrite; it does not require semantic completion of one stage before another stage executes.

No current hidden Fast->Deep or Deep->Fast global completion gate was found.

## 10. SAFE_BOUNDED_FIXES

### SBF-01 — restore Fast asynchronous item traversal

**Findings:** RRC-01 + RRC-02.  
**Likely files:** `config/progressive_pass1_worker_prompt.md`, focused PASS 1 regression(s); contract text only if needed to make transport-marker semantics explicit.  
**Schema change:** no.  
**Semantic identity change:** no.  
**Existing submitted artifacts:** remain valid byte-for-byte.  
**Attempt/recovery state:** unchanged.  
**Scheduler change:** no scheduler setting change; external bootstrap only needs verification that it delegates to current canonical prompt and does not duplicate the stale reload-as-progress rule.

Minimal behavior:
- read exact current manifest/pin at invocation start;
- preserve GitHub order;
- after a successful create-only item A, continue to B from the same already-predeclared immutable plan without waiting for A ingest;
- before any new semantic item, current work may be reread for safety, but prior sibling disappearance/attempt advancement is not a prerequisite;
- on later invocation, if an exact current-manifest `submission_path` already exists, treat it solely as submitted transport and continue to later manifest items;
- never infer canonical acceptance/attempt from path existence.

Required tests:
- A created, manifest unchanged, B still executes;
- B failure/incomplete does not block C;
- later invocation with exact A transport present skips recreating A and can execute B;
- malformed exact A transport does not let worker retry/overwrite A and does not block B;
- old-generation/wrong-path artifact never marks current item submitted;
- mutable profile `main` advancing after pin does not invalidate already-authorized historical submission;
- GitHub ingest remains sole attempt/acceptance owner.

### SBF-02 — make Deep manifest reload explicitly liveness-only, not sibling-ingest progression

**Finding:** RRC-05.  
**Likely files:** `config/progressive_pass2_worker_prompt.md`, focused PASS 2 traversal regression; contract clarification only if necessary.  
**Schema change:** no for this bounded correction.  
**Semantic identity change:** no.  
**Existing submitted artifacts:** remain valid.  
**Attempt/recovery state:** unchanged.  
**Scheduler change:** no scheduler setting change; same bootstrap caveat as Fast.

Minimal behavior:
- retain current manifest membership/order check before a new item;
- retain exact profile pin, Dossier SHA/binding/expiry and recovery-authorization checks;
- explicitly state that prior sibling canonical ingest/attempt advancement is not required;
- if an exact current result/terminal path already exists, do not rerun that item; later current authorized siblings may still proceed;
- do **not** solve RRC-08 implicitly.

Required tests:
- valid exact A transport awaiting ingest does not block B;
- A accepted/incomplete/recovery state still behaves canonically after ingest;
- Dossier expiration/rebinding blocks only affected item before execution;
- stale/revoked recovery authorization cannot be bypassed by an older local plan;
- no Fast prerequisite appears.

SBF-01 and SBF-02 can be bundled safely in one coordinated implementation because both correct traversal semantics around the same pinned-handoff change without changing schemas, identity, attempts, recovery ownership or canonical acceptance.

## 11. DISCUSSION_REQUIRED

### DR-01 — Deep invalid current transport with no consumed attempt

**Finding:** RRC-08.

Two legitimate policy families remain; this audit does not select one:

**A. Preserve “invalid transport consumes no attempt”.**  
GitHub would need an explicit invalid-transport disposition, such as quarantine plus a bounded GitHub-owned re-authorization/republication rule. It must distinguish transport correction from semantic recovery, avoid a blind auto-retry loop, preserve audit history and define whether the same deterministic path may legally be recreated after GitHub removes/quarantines the invalid bytes.

**B. Terminalize malformed exact current transport.**  
Deep could adopt a Fast-like rule in which a malformed exact current submission becomes a consumed incomplete attempt. This removes the occupied-path/no-attempt contradiction but changes the current Deep safety policy that invalid transport must not consume an attempt.

**Likely files if changed:** `config/progressive_pass2_contract.json`, `config/progressive_pass2_worker_prompt.md`, `scripts/progressive_pass2.py`, `scripts/ingest_progressive_pass2.py`, focused schemas/recovery or quarantine surfaces depending on chosen policy.  
**Schema/identity:** may remain unchanged under a quarantine/re-authorization design, but any new authorization object must be exact-bound; terminal-consumption policy changes attempt semantics rather than identity.  
**Existing invalid artifacts:** must be handled only by GitHub-owned migration/disposition if any exist; none was observed in active inbox at final audit read.  
**Scheduler:** no scheduler-setting change should be required, but worker prompt semantics would change.  
**Tests:** malformed result, malformed receipt, exact identity-invalid payload, sibling independence, no hidden retry, no false attempt consumption (option A) or exact deliberate terminal consumption (option B), create-only history preservation, current Dossier liveness, recovery interaction.

### Dossier occupied-pending artifact policy is not a current defect

The user’s broader question—whether *every* exact existing create-only artifact may be used as a local transport marker—has a stage-specific answer. For Dossier, current accepted architecture says **no** across later invocations: the worker must stop on an unclassified exact pending collision and GitHub must reconcile it. That policy was deliberately preserved by the g000012 coalescing-liveness fix. Revisiting it would be a new Director/user ownership decision, not part of SAFE_BOUNDED_FIXES.

## 12. KEEP_NO_CHANGE

Keep the following current mechanisms:

- exact immutable profile pin and byte verification for Fast/Deep;
- Git-history pre-semantic work authority and acceptance of legitimate historical pinned submissions;
- Fast one-shot attempt semantics, including exact malformed current Fast transport becoming terminal incomplete;
- Deep current Dossier content/binding/expiry revalidation before execution and again at ingest;
- Deep one normal first pass plus separate explicit GitHub recovery authorization;
- Dossier V2 liveness reread after successful create and same-invocation buffered continuation;
- Dossier exact pending collision stop across later invocations under current ownership model;
- Dossier independent per-group failed/quarantine/recovery state;
- shared serialized GitHub canonical-writer boundary and state-based Dossier reconciliation;
- Fast/Dossier/Deep stage independence and authoritative Deep precedence;
- no worker-owned queue, acceptance, completeness, retry or recovery state.

## 13. AUD-01..15

- **AUD-01 PASS — yes.** Current Fast per-item reload/take-exact-next is a regression relative to PPD-002. PPD-002/original Phase B prompt in `4bb7e822…` authorize multiple consecutive independent items. Pinned fix `4e9b2f84…` introduced the stronger per-item reload/take-next rule.
- **AUD-02 PASS — yes.** PASS 1 can safely continue through later already-predeclared items without waiting for GitHub ingest. Exact manifest order, deterministic create-only path, immutable profile pin and Git-history authority preserve safety; GitHub remains sole acceptance/attempt owner.
- **AUD-03 PASS — stage-specific.** Fast: yes, exact current-manifest path existence may be used solely as “already submitted” under the conditions in section 6. Deep: valid exact pending result/receipt may prevent rerun while siblings continue, but malformed no-attempt transport requires DR-01. Dossier: no cross-invocation local skip under current accepted ownership; GitHub must classify.
- **AUD-04 PASS — yes.** Fast current reload/take-first behavior creates head-of-line blocking until prior transport is ingested; this is the confirmed seed regression.
- **AUD-05 PASS — no contradictory normal wait remains.** Dossier same-invocation buffered progression does not wait for ingest. The exceptional existing-artifact stop is intentional and backed by the coalescing-safe canonical-writer fix.
- **AUD-06 PASS.** Deep has no contractually required sibling-ingest wait, but its pinned-fix per-item reload is ambiguous and should be clarified as liveness/authorization only. Dossier freshness/current binding and recovery authorization must remain.
- **AUD-07 PASS.** Fast’s reload/take-current-next over-applies mutable currentness after immutable pin and historical work authority. Deep ingest correctly does not use profile/main drift as liveness for started work. Dossier currentness is separate and remains required.
- **AUD-08 PASS.** Actual code preserves Fast/Dossier/Deep independence. Deep recomputation has no Fast eligibility prerequisite; Dossier is independent; only legitimate evidence/recompute dependencies and same-item Deep precedence remain.
- **AUD-09 PASS with one discussion item.** Fast current exact transport can be a submitted marker; Dossier pending collision stop is proportionate under current ownership; Deep stale/mismatched transport is removable, but invalid current no-attempt transport has an unresolved occupied-path contradiction.
- **AUD-10 PARTIAL / discussion required.** Fast submitted-but-not-ingested is not canonically consumed, though current prompt blocks traversal until fixed. Deep valid submitted transport is not consumed before acceptance. Deep malformed current transport is neither consumed nor legally rerunnable because the active path remains occupied; DR-01 must resolve that policy.
- **AUD-11 PASS.** Current remaining superseded/over-strong implementation is principally Fast’s per-item mutable-current/take-next progression gate after immutable pin + historical authority. Old Dossier maximal-prefix and old Deep Fast-incomplete eligibility have already been removed and are not current findings.
- **AUD-12 PASS.** RRC-03/04/06/07/09/10/11/12/13/14/15 are restrictive for concrete live reasons and must not be optimized away.
- **AUD-13 PASS.** Complete sets are sections 10–12.
- **AUD-14 PASS.** No code, contract, prompt, workflow, state, manifest, transport, recovery, scheduler or semantic-production mutation occurred. Only this required durable report is written.
- **AUD-15 PASS once closeout completes.** This report is committed to `main` and the exact committed bytes are reread from fresh `main` immediately before final response.

## 14. Exact rationale evidence

Primary canonical:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md` — especially PPD-002, PPD-004, PPD-005, TASTE-006, TASTE-013
- `config/execution_ownership_contract.json`
- current Fast/Dossier/Deep contracts, prompts and manifests
- `scripts/progressive_work_authority.py`
- `scripts/progressive_pass1.py`
- `scripts/ingest_progressive_pass1.py`
- `scripts/build_progressive_pass1_work.py`
- `scripts/progressive_pass2.py`
- `scripts/ingest_progressive_pass2.py`
- `scripts/taste_steam_review_dossier_group_progress.py`
- `scripts/taste_steam_review_dossier_buffered.py`
- `scripts/taste_steam_review_dossier_worker_projection.py`
- current shared-writer workflows.

Provenance / accepted rationale:
- Phase B PASS 1 implementation: `4bb7e822f3275fc922d32105fc922f2966f14577`
- item-level PASS 1 decision commit: `f81134ddf4b10312e6c8c021b5526f02dd89d52c`
- pinned-profile handoff core: `4e9b2f84c77a59df89afdef5d126362ce5f16c4e`
- `WORKER_TASK_PROGRESSIVE_PINNED_LIVE_PROFILE_HANDOFF_FIX_01.md`
- `reviews/worker_reports/progressive-pinned-live-profile-handoff-fix-01.md`
- PASS 1 coactive ingest report: `reviews/worker_reports/progressive-pass1-coactive-ingest-recovery-fix-01.md`
- Deep core: `670e2cfb6991d955a9503637d72345a523ebca7a`
- Deep runtime adaptation: `e3b5cdc362dbe4ba902f389d1099fcebf90065b3`
- Fast/Dossier/Deep architecture decision implementation: `a432b20f4ea6fbadeba072fa721343f5855386df`
- Dossier nonblocking implementation: `79f1c38c218d0d2ea89d7722e4ff5b1c9840d508`
- Dossier V2 runtime activation: `f0ffb166f37b0ba2da363f8908359373d8b17939`
- Dossier worker-prompt V2 alignment: `17eba7f5ba616e53d45ef63ec835d35a4eb60913`
- `reviews/worker_reports/taste-dossier-g000012-existing-artifact-collision-diagnostic-01.md`
- Dossier canonical-writer coalescing fix merge: `e69eb97a678636ea78b2aaac52ff07785c119f0d`
- `reviews/worker_reports/taste-dossier-canonical-writer-coalescing-liveness-fix-01.md`
- `KNOWN_WORKER_PITFALLS.md#PITFALL-007`.

## 15. Uncertainties / evidence limits

- This audit proves rule semantics and code paths, not every possible external Scheduled Task bootstrap string. Repository canonical prompts are the runtime authority inspected here; any external bootstrap that duplicates traversal logic should be checked during implementation acceptance.
- No active inbox artifact was present at final read, so RRC-08 is a proven current code-path contradiction, not a claim of a currently stranded production Deep artifact.
- Normal external production can change counts/manifests after this report; classifications rely on contracts/provenance rather than one transient count snapshot.
- No external profile repository read was needed: the current Progressive manifest already exposes the exact immutable profile-pin identity, and the audit question was runtime ownership/traversal rather than profile-content semantics.

## 16. Final status

`complete_ready_for_director_review`

Confirmed safe corrections are limited to Fast asynchronous traversal/transport-marker semantics and a Deep traversal clarification that preserves current per-item authorization/Dossier liveness. Deep invalid-no-attempt transport disposition remains a real policy/design question. Dossier collision handling remains intentionally GitHub-classified under the current accepted architecture.

## 17. Recommended Director next step

Discuss **DR-01 (Deep invalid-no-attempt transport disposition)** and then issue **one coordinated IMPLEMENT task only for the approved findings**, bundling SBF-01/SBF-02 and any Director-approved DR-01 policy while preserving every KEEP invariant.
