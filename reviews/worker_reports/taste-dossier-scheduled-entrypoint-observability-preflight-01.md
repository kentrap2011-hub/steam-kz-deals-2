# Taste dossier scheduled entrypoint observability preflight 01

## 1. Task / repo / mode

- Task: taste-dossier-scheduled-entrypoint-observability-preflight-01.
- Worker task: WORKER_TASK_TASTE_DOSSIER_SCHEDULED_ENTRYPOINT_OBSERVABILITY_PREFLIGHT_01.md.
- Repository: kentrap2011-hub/steam-kz-deals-2.
- Base/source of truth: main.
- Mode: READ-ONLY / ARCHITECTURE PREFLIGHT.
- Other repositories were not read, searched, changed, or used.
- No Scheduled Task was run or edited.
- No production dossier candidate, runtime receipt, recovery artifact, quarantine action, canonical progress mutation, prompt/contract/schema/validator/runtime implementation, workflow change, or evidence retrieval was performed.
- The only permitted write is this durable architecture report.

## 2. Accepted problem

Two accepted facts are preserved:

1. The canonical worker prompt in main unambiguously requires FAIL_CLOSED_EXECUTION_LEDGER_V1 on every fail-closed stop before successful candidate publication.
2. A live Scheduled Task invocation stopped fail-closed on the current binding but omitted that mandatory ledger.

The accepted follow-up diagnostic could verify the repository-side rule but could not inspect the actual live Scheduled Task entrypoint/invocation prompt. Its final classification was insufficient_observability_to_classify.

The unresolved boundary is therefore:

Scheduled Task entrypoint/config -> canonical prompt/binding establishment -> early fail-closed or later runtime work -> output.

The goal here is not to strengthen wording inside the same prompt again. The goal is to define the smallest externally machine-verifiable observability mechanism that can distinguish:

- no machine-verifiable current-binding handshake;
- current-binding handshake established, but no valid terminal artifact;
- current-binding handshake established and a valid success or fail-closed terminal artifact produced.

The mechanism must not pretend that an LLM assertion, receipt, hash echo, or nonce proves semantic comprehension of every prompt clause.

## 3. Architecture ownership preflight

### 3.1 Current owner by responsibility

Canonical work binding:
- Owner: GitHub repository / GitHub Actions control plane.
- Basis: config/execution_ownership_contract.json and config/taste_steam_review_dossier_contract.json.
- GitHub selects exact scope/order, prepares immutable group plan and worker projection, binds snapshot/group/evidence/prompt identity, and owns canonical expected sequence.

Runtime external/semantic work:
- Owner: existing Scheduled ChatGPT dossier worker.
- It may read exact GitHub-prepared work, perform bounded public-web semantic/evidence work, and submit structured results only through the repository-defined runtime artifact interface.

Validation / persistence / progress:
- Owner: GitHub control plane.
- Candidate creation is transport only. GitHub validates against the full canonical manifest, persists accepted dossiers, advances canonical progress only through the maximal valid contiguous prefix, and owns cleanup.

Retry / recovery / completeness:
- Owner: GitHub control plane.
- Scheduled ChatGPT must not infer queue/retry/replay state, skip gaps, heal invalid candidates, or declare canonical completeness.

### 3.2 Which canonical contract permits observability

PRODUCTION-EXECUTION-OWNERSHIP-V1 permits Scheduled ChatGPT to persist or submit results only through a repository-defined runtime artifact interface while GitHub retains validation and interpretation.

TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2 already permits create-only worker transport and explicitly keeps transport non-authoritative for progress/retry/completeness.

However, the current TASTE-STEAM-REVIEW-DOSSIER-PERSISTENCE-BRIDGE-V1 defines only:
- legacy current-checkpoint submission; and
- active buffered dossier candidate transport.

It does not currently authorize a runtime-receipt artifact class.

Therefore a create-only observability receipt is ownership-compatible in principle, but it is NOT currently an authorized artifact class. IMPLEMENT must first amend the canonical dossier contract/persistence bridge before any runtime receipt is created.

### 3.3 Control-plane transfer check

The recommended design does not move control-plane responsibility into Scheduled ChatGPT or interactive chat if all of the following remain true:

- GitHub prepares all authoritative work/binding inputs.
- Scheduled ChatGPT only emits non-authoritative observable runtime receipts and dossier candidates.
- GitHub validates receipt identity/binding and interprets stale/duplicate/replay state.
- Receipts never advance canonical progress, choose retry, alter scope, or declare completeness.
- Director reads GitHub-validated state but does not become the runtime executor.

Any design in which the model decides receipt scope, marks a receipt accepted, chooses retry sequence, or mutates progress is rejected.

### 3.4 New recurring architecture check

The recommended design creates no new scheduler, recurring stage, queue, retry loop, backlog manager, checkpoint owner, or completeness owner.

Validation is attached to the existing repository push -> dossier ingest/validation boundary. It may add a receipt-validation branch/helper inside that existing event-driven workflow, but not a second recurring automation.

PREFLIGHT ownership result: PASS.

## 4. Current binding / persistence surfaces

Current active production binding confirmed by accepted report and current canonical work:

- snapshot_id: ad93a4484f1c6ceba4ba3d4ef0de681f65fe670ec1ee600e2abc0822b0eec54a
- canonical expected sequence: g000001 / sequence 1
- current group: Crown Trick / Hellish Quart / Tetris® Effect: Connected
- g000001 group_sha256: dd3e9ad4d9cd1fe34420ba8cc8b40a569002ff3896b36251247c81082868e695
- active worker prompt revision: web-evidence-v2-fail-closed-execution-ledger-v1
- active worker prompt content SHA-256: 6d5c3be5eb7043a9731054679bf05871a4c34284abec86b1177d547bd9fa5d65
- active evidence-contract content SHA-256: be470fbdb75b90fde5eb71da8d7a76ec9df77ac0ed171237aa4283df4a4deaac

Existing success-path transport:
data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json

Existing properties:
- immutable create-only;
- one deterministic candidate per predeclared group;
- buffer is transport only;
- GitHub owns validation/progress/replay/gap/stale interpretation;
- create success means candidate buffered, not canonical acceptance.

Existing workflow:
.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml

It is push-triggered for dossier inbox artifacts, uses the existing canonical-writer serialization boundary, drains current repository state, writes observational validation status, and commits canonical progress only after GitHub-side validation.

Current worker prompt already contains a user-visible ephemeral fail-closed ledger, but that ledger is neither durable nor machine-verifiable by GitHub.

The available GitHub read surface can expose the current main branch head commit SHA. This matters because a GitHub-owned branch-head SHA can be used as a deterministic per-invocation freshness anchor without inventing model-chosen scope or a secret nonce.

## 5. OPTION A — final-response attestation only

Shape:
- final response echoes snapshot id, sequence/group hash, prompt revision/hash and states that the canonical prompt was loaded.

What it proves:
- only that the model emitted those values in its final response.

What it does not prove:
- that the current canonical prompt file was read fully;
- that the values came from the current invocation rather than a previously known binding;
- that the fail-closed ledger section was reached/applied;
- that output was preserved durably;
- that GitHub can machine-validate the claim;
- that the worker did not stop before required retrieval/action work.

Material strength versus the failed ledger requirement:
- insufficient.
- It remains pure prompt compliance and is vulnerable to exactly the class of omission already observed.

Decision:
REJECT as a sufficient architecture.

It may remain a human-readable convenience, but it cannot be the acceptance signal.

## 6. OPTION B — candidate-only binding proof

Current state:
- This substantially already exists.
- The buffered candidate is bound to the exact immutable group descriptor.
- Each dossier copies the exact web_evidence_contract_binding.
- GitHub strict/buffered validation checks the candidate against the full canonical manifest and descriptor identity.
- The binding already carries content-complete schema/evidence/prompt hashes and revisions.

What it proves when GitHub accepts the candidate binding:
- the published candidate is for the exact current snapshot/group and exact bound evidence/prompt/schema content identity;
- success-path artifact identity was not silently rebound to another snapshot or contract.

What it does not prove:
- that a no-candidate invocation established a current prompt/binding handshake;
- where a fail-closed invocation stopped;
- whether required fail-closed output was produced;
- whether a worker that stopped before publication read/applied the current prompt.

Decision:
KEEP as the success-path foundation, but insufficient alone.

OPTION B should be linked to an invocation entry receipt in the recommended design rather than replaced.

## 7. OPTION C — GitHub-validated create-only invocation receipt

### Feasibility under ownership

Ownership-compatible only after explicit canonical contract authorization.

Scheduled ChatGPT already has one permitted persistence mechanism: connected GitHub create-file into a repository-defined runtime artifact interface. A small non-authoritative receipt can reuse that mechanism.

The current persistence bridge does not define such an artifact, so implementation today without contract change would be out of contract.

### Minimal entry receipt

Recommended artifact family:
TASTE-STEAM-REVIEW-DOSSIER-RUNTIME-RECEIPT-V1

Recommended location under the existing dossier runtime inbox boundary:
data/ai_inbox/taste_steam_review_dossiers/runtime_receipts/

Entry path design:
{snapshot_id}--g{sequence:06d}--{group_sha256}--entry-{entry_base_commit_sha}.json

The entry_base_commit_sha is the exact GitHub main HEAD SHA pinned immediately before reading the canonical prompt/contracts/index/descriptor for the handshake.

The worker must read the canonical files at that pinned ref, not as a set of drifting main reads.

Minimum entry fields:
- schema / schema_version;
- phase = entry;
- repository and branch;
- entry_base_commit_sha;
- snapshot_id;
- prepared_required_sha256;
- group_plan_sha256 when present in the current projection;
- canonical_expected_sequence observed at entry;
- sequence;
- group_sha256;
- worker_prompt_revision;
- worker_prompt_content_sha256;
- worker schema revision/content SHA-256;
- web evidence contract revision/content SHA-256;
- dossier contract identity/hash or Git blob identity;
- persistence bridge identity/hash or Git blob identity;
- receipt path identity;
- canonical_progress_claim = non-authoritative / no progress.

The create-file operation itself returns a GitHub commit SHA. That resulting entry_receipt_commit_sha becomes the per-invocation durable linkage key for the later terminal artifact.

### Exact required event

Create the entry receipt only after:
1. main HEAD is pinned;
2. the current canonical prompt/contracts and exact worker index/group descriptor are read at that pinned ref;
3. exact snapshot/group/binding equality checks have passed.

Create it before:
- the first external web retrieval; OR
- any terminal fail-closed return after the binding can be formed.

No external evidence work may begin until the entry receipt create succeeds and the returned GitHub commit is verified to descend directly from the pinned entry_base_commit_sha. If a concurrent GitHub write races the handshake so the parent relation is not exact, the receipt is invalid/stale for acceptance and the worker must stop before evidence work.

### What this proves

After GitHub machine validation, the receipt proves:
- a GitHub create happened through the repository-defined transport;
- the receipt is tied to an exact GitHub-owned main commit;
- its current snapshot/group/prompt/schema/contract identities match the canonical contents at that pinned commit;
- an externally durable handshake artifact existed before later runtime work.

It does NOT prove:
- that the LLM semantically comprehended every prompt clause;
- that it read every prompt line rather than obtaining enough canonical data to construct the receipt;
- that later tool work followed every instruction.

### Create-only / non-authoritative semantics

Yes:
- worker may create only;
- worker may never update/delete/rename a receipt;
- receipt is not canonical progress;
- receipt is not queue state;
- receipt is not retry state;
- receipt is not completeness state;
- GitHub alone validates/labels current/stale/duplicate relationships.

### Duplicate/replay handling

- Same deterministic entry path may be created only once.
- A second concurrent invocation starting from the same entry_base_commit_sha collides on the same create-only path; it must stop rather than choose an alternate name.
- A later non-concurrent invocation naturally observes a newer main HEAD because the prior receipt create itself advanced main, so its deterministic path differs.
- Replayed receipt content for an old snapshot/binding is stale/inert.
- Same-path duplicate/replay never authorizes progress.

Decision:
ACCEPT as the entry half of the recommended architecture, with explicit contract change required before implementation.

## 8. OPTION D — fail-closed durable execution receipt

### Same artifact family versus separate subsystem

Use the same TASTE-STEAM-REVIEW-DOSSIER-RUNTIME-RECEIPT-V1 family, not a second subsystem.

Phase:
fail_closed

Recommended fail path:
{snapshot_id}--g{sequence:06d}--{group_sha256}--fail-{entry_receipt_commit_sha}.json

The fail receipt must reference:
- entry_base_commit_sha;
- entry_receipt_path;
- entry_receipt_commit_sha;
- exact current snapshot/group/binding;
- exact terminal publication state.

It carries the durable analogue of the current fail-closed execution ledger:
- exact stop gate;
- last completed material stage;
- safe material route classes attempted;
- factual observable results;
- applicable search/page budget used;
- required-route states;
- next required step;
- next required step status;
- factual blocker or explicit unknown;
- no canonical progress claim.

### GitHub validation / no-progress semantics

GitHub validates:
- entry receipt exists and is valid;
- fail receipt references that exact entry_receipt_commit_sha;
- binding fields match the pinned entry receipt/canonical commit;
- receipt path is deterministic;
- privacy/field restrictions hold;
- phase is fail_closed.

A valid fail receipt never calls dossier persistence and never advances canonical expected sequence.

### Privacy

Durable fail receipts must be stricter than ordinary diagnostic prose.

Forbidden:
- chain-of-thought or hidden reasoning;
- raw review/post bodies;
- quotes/excerpts;
- usernames/display names;
- Steam/account identifiers;
- profile URLs;
- author-derived hashes/pseudonyms;
- secrets/tokens;
- raw query strings containing identity;
- unsupported root-cause guesses.

Safe persisted route names are surface classes only.

A raw visible tool error may be persisted only if it contains no secret/profile/author-sensitive material. Otherwise persist a safe error class plus an explicit redaction flag, not the sensitive raw payload.

### Stale / replay

- Old-snapshot fail receipts are inert.
- GitHub may mark them stale in the existing observational validation surface.
- Any later cleanup/quarantine remains GitHub-owned and should be attached to the existing daily/recovery boundary, not a new scheduler.
- Worker never deletes or repairs receipts.

### Relationship to final-response ledger

The durable fail receipt should become the machine-verifiable source for the final user-visible failure summary.

The user-visible marker may remain, but the final response no longer needs to be the sole carrier of the only diagnostic facts. A later implementation may keep FAIL_CLOSED_EXECUTION_LEDGER_V1 and summarize or mirror the receipt, but GitHub acceptance must depend on the durable receipt, not on the final prose.

Decision:
ACCEPT as the terminal-failure half of the same recommended architecture.

## 9. OPTION E — GitHub-issued challenge / nonce / manifest token

What it could prove:
- echo of a token present in a current GitHub-prepared work input;
- potentially stronger freshness than a static revision name.

What it still would not prove:
- full prompt reading;
- semantic comprehension;
- execution of required routes;
- compliance after token echo.

Why it is not recommended now:
- current work already has content-complete snapshot/group identity plus worker prompt/schema/evidence content hashes;
- a per-work-unit nonce would be static across repeated invocations of the same group unless GitHub mutates work state for every invocation;
- making GitHub issue a new per-invocation nonce would introduce a new handshake/orchestration state machine and coupling to the scheduler;
- a secret token is unnecessary and creates secret-handling risk;
- a public deterministic token adds little beyond existing hashes.

The recommended design obtains invocation freshness from a GitHub-owned main HEAD commit SHA plus the GitHub commit SHA created by the entry receipt. That is simpler and externally verifiable.

Decision:
DO NOT ADD nonce/challenge in V1.

## 10. Adversarial scenarios 1-10

### Scenario 1 — worker knows new binding revision but did not read/apply full canonical prompt

Expected observation:
- It may still be able to construct a syntactically valid receipt if it can obtain enough canonical binding data.
- Therefore a valid receipt does not prove full prompt reading or semantic application.

Classification:
- machine-verifiable binding handshake can be present;
- full prompt comprehension remains unproven.

This is an explicit non-guarantee, not a hidden assumption.

### Scenario 2 — worker read current work manifest but not full worker prompt

Expected observation:
- Because the current work binding contains prompt identity/hash, manifest knowledge alone may be enough to echo the prompt hash.
- Even adding the prompt Git blob identity does not prove semantic reading.

Classification:
- receipt can prove possession/echo of current canonical identities;
- it cannot prove full prompt content consumption.

No nonce solves semantic comprehension by itself.

### Scenario 3 — worker read both, starts correctly, then stops before retrieval

If the worker reaches the defined handshake point:
- valid entry receipt exists;
- no evidence retrieval attempt exists;
- if it can terminate cleanly, it must create fail_closed receipt before final response.

If runtime disappears immediately after entry receipt:
- valid entry exists;
- no terminal artifact.

Director classification:
B — handshake established, terminal artifact absent.

### Scenario 4 — worker performs retrieval and fail-closes without candidate

Required:
- valid entry receipt;
- fail_closed terminal receipt linked by entry_receipt_commit_sha;
- durable observable attempt/budget/gate facts;
- no candidate and no progress.

Director classification:
C-failure-artifact-correct.

If final prose omits the old ledger but the valid durable fail receipt exists, machine observability is preserved; final-response formatting can be diagnosed separately.

### Scenario 5 — worker publishes a candidate

Required:
- valid entry receipt;
- successful candidate remains the existing deterministic buffered dossier artifact;
- candidate must carry a small runtime-entry reference containing at least entry_receipt_commit_sha and deterministic entry receipt path/identity;
- GitHub validates both current candidate binding and entry linkage before canonical candidate acceptance.

Director classification:
C-success-artifact-correct.

Candidate creation still does not equal canonical progress until the existing strict GitHub validation passes.

### Scenario 6 — snapshot/binding changes between invocations

A new invocation pins the new main HEAD and reads the new current snapshot/binding.
Old entry/fail receipts are stale/inert.
No old receipt may authorize a new candidate.

If binding changes during one invocation:
- the existing liveness rule still applies;
- terminal fail receipt records binding_changed/stale transition against its original entry receipt;
- no candidate is published for the superseded projection.

### Scenario 7 — duplicate/replayed receipt appears

Same path:
- create-only prevents overwrite;
- second write fails;
- no alternate filename allowed.

Old or copied content under a different path:
- deterministic path validation fails.

Already validated receipt replay:
- idempotent observationally;
- never re-advances progress.

### Scenario 8 — receipt is missing

If there is no valid entry receipt:
- current-binding handshake is not machine-proven.

If a user-visible failure exists but no entry receipt exists:
- Director can classify entrypoint/handshake as unproven, but cannot distinguish non-execution from abrupt runtime loss before receipt creation without an external platform invocation record.

If valid entry exists but terminal candidate/fail receipt is missing:
- Director has positive evidence that the handshake artifact was established and negative evidence that no required terminal durable artifact was produced.

### Scenario 9 — receipt has stale/mismatched hashes

GitHub rejects it observationally:
- wrong snapshot/group;
- prompt/schema/evidence mismatch;
- wrong entry path;
- wrong main-base relation;
- wrong entry receipt linkage;
- wrong phase/path.

It never mutates progress and never authorizes retry.

### Scenario 10 — runtime ends abruptly before terminal receipt can be written

If it ended after valid entry receipt:
- GitHub can prove entry handshake artifact creation;
- it cannot prove why the runtime disappeared or which unpersisted steps occurred;
- no terminal artifact means B.

If it ended before the entry receipt:
- there is no repository artifact from the invocation;
- GitHub cannot prove whether the task never started, used a stale entrypoint, crashed before receipt creation, or was terminated externally.

This residual ambiguity is fundamental unless the Scheduled Task platform itself exposes an invocation-start record outside the model-controlled artifact path.

The recommended design does not claim otherwise.

## 11. Recommended architecture — exactly one

Recommendation:

PINNED-MAIN-HEAD CREATE-ONLY RUNTIME RECEIPT, one artifact family with:
- entry phase;
- fail_closed terminal phase;
- existing buffered candidate as the success terminal artifact, linked to the entry receipt.

This is one architecture combining the useful parts of OPTIONS B + C + D.
OPTION A is informational only.
OPTION E is intentionally omitted.

### 11.1 Minimal interface

New non-authoritative receipt family under the existing dossier inbox boundary:

data/ai_inbox/taste_steam_review_dossiers/runtime_receipts/

Entry:
{snapshot_id}--g{sequence:06d}--{group_sha256}--entry-{entry_base_commit_sha}.json

Fail terminal:
{snapshot_id}--g{sequence:06d}--{group_sha256}--fail-{entry_receipt_commit_sha}.json

Existing success candidate path remains unchanged:
data/ai_inbox/taste_steam_review_dossiers/{snapshot_id}--g{sequence:06d}--{group_sha256}.json

The buffered candidate gains only a top-level runtime entry-receipt reference; dossier evidence semantics remain unchanged.

### 11.2 Writer

Exact writer:
existing Scheduled ChatGPT dossier worker through connected GitHub contents create-file.

It may:
- create entry receipt;
- create fail_closed terminal receipt;
- create existing candidate.

It may not:
- update/delete/rename any receipt or candidate;
- validate its own receipt authoritatively;
- advance progress;
- choose retry;
- create alternate paths.

### 11.3 Validator

Exact authority:
GitHub Actions control plane.

Validation should run inside the existing .github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml event-driven boundary, not a new scheduler.

Receipt validation should be observational and may extend the existing data/production/pre_ai/taste_steam_review_dossier_validation_status.json rather than creating a second status/logging service.

Candidate canonical acceptance remains in the existing strict/buffered GitHub validation path.

### 11.4 Authoritative for progress

No.

Proof:
- receipt contains no dossier persistence authority;
- receipt phase never mutates remaining_required_items, completed_required_count, canonical_expected_sequence, dossier cache, or completeness;
- only an existing valid candidate can enter canonical dossier persistence;
- canonical progress remains maximal-valid-contiguous-prefix GitHub logic.

### 11.5 Deterministic invocation identity

Invocation freshness anchor:
entry_base_commit_sha = exact GitHub main HEAD pinned immediately before canonical handshake reads.

Per-invocation durable linkage:
entry_receipt_commit_sha = GitHub commit SHA returned by the create-only entry receipt action.

Why this is better than a model-generated UUID:
- both anchors are GitHub-issued;
- the worker does not choose scope or random identity;
- receipt creation advances main, so a later sequential invocation naturally gets a different base head;
- concurrent same-head invocations collide deterministically instead of inventing multiple identities.

### 11.6 Lifecycle

prepared canonical work
->
pin main HEAD
->
read prompt/contracts/index/descriptor at pinned commit
->
validate exact binding/group
->
create entry receipt
->
verify entry receipt commit parent/base relation
->
external semantic/evidence runtime work
->
either:
  a) create existing candidate carrying entry receipt linkage; or
  b) create fail_closed receipt carrying durable ledger facts and entry linkage
->
GitHub machine validation
->
candidate path only: existing strict persistence/progress logic
->
fail receipt path: no progress, observational status only.

### 11.7 Stale / duplicate behavior

- Old snapshot/binding receipts are inert.
- Exact duplicate paths cannot be overwritten.
- Alternate receipt filenames are invalid.
- GitHub owns replay interpretation and any later stale quarantine/cleanup.
- Cleanup, if implemented, must piggyback the existing GitHub daily/recovery boundary and must not create a new scheduled service.
- Candidate or receipt replay never repeats canonical advancement.

### 11.8 Success versus fail-closed

Success:
- entry receipt exists and validates;
- buffered candidate exists, copies current binding, and references entry receipt;
- existing strict validation decides candidate acceptance.

Fail-closed:
- entry receipt exists and validates when the handshake point was reached;
- no candidate;
- fail_closed receipt exists and validates;
- receipt carries only observable execution facts/gates/budget/next-step state;
- no progress.

Abrupt:
- valid entry only, no terminal artifact => B;
- no entry => handshake not machine-proven, with residual ambiguity about pre-receipt runtime loss.

### 11.9 Director diagnosis A/B/C from durable state

A — handshake not machine-proven:
- no valid entry receipt tied to the current invocation/current binding.
- Strong claim allowed: GitHub has no machine-verifiable current-binding entry handshake.
- Strong claim NOT allowed: the model definitely never read the prompt.

B — handshake established, later terminal artifact absent:
- valid entry receipt;
- no valid linked candidate;
- no valid linked fail_closed receipt.
- This localizes the failure after the machine-verifiable entry handshake and before durable terminal completion.

C — terminal artifact correct:
- valid entry receipt; and
- either valid linked fail_closed receipt, or valid linked candidate.
- For candidate, canonical acceptance still additionally requires the existing strict dossier validator.

### 11.10 Why this is the smallest sufficient design

It reuses:
- existing GitHub control plane;
- existing create-file runtime transport;
- existing dossier inbox namespace;
- existing push-triggered ingest workflow;
- existing strict candidate validation;
- existing observational validation-status surface;
- existing content-complete binding hashes.

It adds no nonce, scheduler, queue, retry owner, progress owner, external logging service, or second production worker.

## 12. Strongest guarantee / explicit non-guarantees

### Strongest honest guarantee

A GitHub-validated entry receipt can prove that, before later runtime work, the Scheduled worker successfully created a durable artifact whose exact snapshot/group/prompt/schema/contract identity matches canonical GitHub contents at a pinned GitHub main commit, and that later terminal artifacts are linked to that same entry receipt.

A GitHub-validated fail_closed receipt can additionally prove which observable stop gate, material route classes, budget counters and factual blocker/unknown state the worker durably reported before its final fail-closed response.

A linked candidate can prove success-path artifact binding for the same receipt-linked invocation before existing strict dossier acceptance.

### Explicit non-guarantees

The mechanism cannot prove:
- that the model read every line of the prompt;
- semantic comprehension of every prompt clause;
- hidden reasoning;
- that unpersisted material attempts occurred exactly as mentally represented;
- the root cause of an abrupt runtime disappearance;
- that an invocation existed at all when no platform record and no receipt were produced;
- that a missing receipt means stale entrypoint rather than pre-receipt crash/cancellation.

No architecture based only on model-written repository artifacts can eliminate the last case. A platform-owned invocation-start record would be required for that stronger guarantee.

## 13. Required canonical changes if later implemented

No implementation is performed here.

A later IMPLEMENT should be bounded to these exact surfaces:

1. config/taste_steam_review_dossier_contract.json
   - authorize runtime receipt artifact class;
   - define non-authoritative ownership;
   - define stale/replay/no-progress rules.

2. config/taste_steam_review_dossier_persistence_bridge.json
   - define runtime_receipts subdirectory;
   - define create-only entry/fail path templates;
   - required fields/linkage;
   - worker forbidden update/delete/alternate names;
   - GitHub validation ownership.

3. config/taste_steam_review_dossier_worker_prompt.md
   - pin main head;
   - read canonical handshake files at pinned ref;
   - exact entry receipt timing;
   - capture entry_receipt_commit_sha;
   - link candidate/fail receipt;
   - durable fail receipt before final fail-closed output.

4. config/taste_steam_review_dossier_web_evidence_contract.json
   - advance worker_prompt_revision/content binding for the prompt change only;
   - evidence semantics should remain unchanged.

5. .github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml
   - add receipt-path push trigger;
   - invoke receipt validation inside the existing serialized writer/validation boundary;
   - no new recurring workflow.

6. scripts/taste_steam_review_dossier_buffered.py
   - require/validate candidate linkage to a valid entry receipt before candidate acceptance.

7. scripts/taste_steam_review_dossier_parallel_validation.py
   - expose observational receipt/candidate linkage validity in the existing validation-status surface.

8. One bounded non-scheduled helper is acceptable if needed:
   scripts/taste_steam_review_dossier_runtime_receipts.py
   - deterministic path/field validation only;
   - no queue/progress/retry state.

9. Focused dossier regression tests
   - entry valid/invalid/stale;
   - fail receipt valid;
   - success candidate linkage;
   - duplicate/replay;
   - concurrent same-head collision;
   - snapshot rollover;
   - no-progress invariant.

No new dossier evidence schema semantics are required. The worker-facing dossier evidence schema remains V2; receipt fields belong to the transport/observability layer, not observations/provenance.

No nonce/work-manifest field is required for V1, so scripts/build_taste_steam_review_dossier_work.py need not gain a new challenge state machine.

Normal GitHub-owned activation would still be required after any prompt/contract revision change so the content-complete binding produces a fresh compatible snapshot.

## 14. PREFLIGHT-01..12

PREFLIGHT-01 — PASS.
Four ownership questions answered explicitly: GitHub owns binding/control/validation/persistence/progress/retry/completeness; Scheduled ChatGPT owns bounded runtime external/semantic work and non-authoritative create-only output.

PREFLIGHT-02 — PASS.
OPTIONS A-E compared with explicit proof/non-proof boundaries.

PREFLIGHT-03 — PASS.
Current contracts checked. Execution ownership permits repository-defined worker artifacts in principle, but current persistence bridge does not authorize receipts; explicit contract/bridge change is required before implementation.

PREFLIGHT-04 — PASS.
No recommended guarantee depends on final-response self-attestation alone.

PREFLIGHT-05 — PASS.
Success candidate and fail-closed/no-candidate paths are both covered.

PREFLIGHT-06 — PASS.
Stale binding, rollover, duplicate, replay and same-path collision behavior are defined.

PREFLIGHT-07 — PASS.
Abrupt runtime loss before/after entry receipt is explicitly bounded; pre-entry disappearance remains fundamentally ambiguous without platform-owned invocation telemetry.

PREFLIGHT-08 — PASS.
No GitHub control-plane ownership moves to Scheduled ChatGPT or interactive chat.

PREFLIGHT-09 — PASS.
No new recurring stage, queue, retry loop, backlog manager, checkpoint owner or scheduler is introduced.

PREFLIGHT-10 — PASS.
Exactly one architecture selected: pinned-main-head create-only runtime receipt family with entry + fail phase and linked existing success candidate.

PREFLIGHT-11 — PASS.
Implementation impact is bounded to exact canonical/runtime surfaces above; no implementation performed.

PREFLIGHT-12 — PASS.
No production run; report only.

## 15. Changes

Report only:
reviews/worker_reports/taste-dossier-scheduled-entrypoint-observability-preflight-01.md

No other repository/runtime/task/business state is intentionally changed by this worker.

CURRENT_TASK.md was read only for conflict detection and was not modified because this task explicitly permits only the durable architecture report write.

## 16. Unresolved

No architecture-blocking canonical fact remains.

One fundamental external observability limit remains:

If the Scheduled Task platform terminates or never launches an invocation before the worker creates the entry receipt, repository state alone cannot distinguish:
- task never started;
- stale/different live entrypoint;
- crash/cancellation before receipt;
- runtime/tool failure before receipt capability became available.

The proposed receipt architecture narrows the observable boundary after a valid entry receipt, but it cannot create evidence for an execution that disappears before creating any evidence.

No timeout, context limit, renderer loss, model defect, or platform cause is inferred.

## 17. Status

complete_architecture_recommendation

Reason:
- one minimal GitHub-verifiable design selected;
- ownership remains valid;
- candidate and fail-closed paths covered;
- residual unobservable cases explicit;
- exact implementation surfaces bounded;
- no implementation or production run performed.

## 18. Exactly one recommended next step

Return to Director for architecture acceptance and explicit user approval before one bounded IMPLEMENT task changes the canonical contract/persistence/prompt/validator surfaces described in section 13.

## 19. Exact refs

Read/authority refs:

- CHAT_PROTOCOL.md blob: fe9fb2e415ee696aa6618d915266eefe47449ff0
- WORKER_TASK_TASTE_DOSSIER_SCHEDULED_ENTRYPOINT_OBSERVABILITY_PREFLIGHT_01.md blob: 6148d2ee3c4af44f405471003914a705644e96fd
- PROJECT_ROUTES.md blob: 289cbeba41cd58c336dbf405498d45673c34dec7
- config/execution_ownership_contract.json blob: 96a02f5c51e09c60cde31aacd19323ead8d985e0
- config/taste_steam_review_dossier_contract.json blob: 1b3a9a4abe2151195d8cd9ed8dd6c12f5705d5a3
- config/taste_steam_review_dossier_persistence_bridge.json blob: db9bd5e13d7b36b0e7458c76da4c97416402ad80
- config/taste_steam_review_dossier_worker_prompt.md blob: 1ba4a390923e6bfbc655c7f0094db70ba395b9a6
- config/taste_steam_review_dossier_web_evidence_contract.json blob: 53b5f10d5a59f602e0a0c74bb538975c163eed87
- config/taste_steam_review_dossier_schema.json bounded read blob: 2d35cac69ea1864127df86f7fec90cc0818fab3f
- data/production/pre_ai/taste_steam_review_dossier_work.json blob: dffccb845b37f4f7b404498676fff111143882ae
- reviews/worker_reports/taste-dossier-fail-closed-execution-ledger-implement-01.md blob: 702cc4f5d6c4396fb8ffb53755ad45f6eb625a22
- reviews/worker_reports/taste-dossier-scheduled-entrypoint-ledger-diagnostic-01.md blob: fed61455447147cbabcadd32389e275080635d3a
- .github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml blob: ef20673f77293ce6a0f26991eade96abb64a5a32
- scripts/ingest_taste_steam_review_dossier_inbox.py blob: 083f77639eda84e9940501a03f7545b50160d160
- pre-report main HEAD observed through GitHub branch read: 12c4adba929d3e68a00fdd92c41e35caed64f138

Accepted implementation/diagnostic refs:
- fail-closed ledger implementation PR #73 merged as a5d53a58d92de9066890755b2bb6ae6c19409e80
- activation commit: 924673f2a788b52ccd61dbac4b2a844118a6bdf8
- active snapshot: ad93a4484f1c6ceba4ba3d4ef0de681f65fe670ec1ee600e2abc0822b0eec54a
- active g000001 group hash: dd3e9ad4d9cd1fe34420ba8cc8b40a569002ff3896b36251247c81082868e695
- prior diagnostic classification: insufficient_observability_to_classify

## 20. Efficiency / reusable lesson

The reusable pattern is to separate three propositions that were previously conflated:

1. canonical binding identity exists;
2. a runtime invocation durably established that binding;
3. the runtime later produced a valid terminal artifact.

A final response can assert all three but proves none by itself.

A create-only entry receipt anchored to a GitHub-owned main commit makes proposition 2 externally machine-verifiable without transferring progress/retry ownership. Linking either the existing candidate or a fail-closed receipt to the entry receipt makes proposition 3 machine-verifiable. The remaining semantic question — whether an LLM fully understood and obeyed every prompt clause — must remain outside the claimed guarantee.
