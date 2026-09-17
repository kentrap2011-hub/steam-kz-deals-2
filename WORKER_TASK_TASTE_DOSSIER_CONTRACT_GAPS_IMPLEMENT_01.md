# WORKER TASK — Taste Dossier Contract Gaps Implement 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-contract-gaps-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## Goal
Implement the seven **new proven gap classes** from:

`reviews/worker_reports/taste-dossier-contract-gap-audit-01.md`

against the **current `main` after PR #36**, without regressing the evidence guard, pre-publication validator parity, immutable recovery semantics, or group size `3`.

This task is the follow-up to the independent gap audit. Do not run another broad audit here.

Do **not** run Scheduled Task `Run now`.

## Important baseline reconciliation

The audit was pinned to an older baseline. Since then PR #36 landed and changed compact-provenance validation and pre-publication validation.

Therefore, before changing code:

1. read the audit report;
2. reproduce/re-evaluate each of GAP-01 through GAP-07 against the **current `main`**;
3. for any gap that PR #36 already incidentally closes, do **not** add redundant machinery — instead add/retain a focused regression proving the gap is now closed;
4. implement only the parts that remain reachable on current `main`.

The final report must say for each GAP-01..07 whether it was:
- `implemented_now`, or
- `already_closed_on_current_main` with proof.

Do not silently drop a finding.

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully, then read at minimum:

- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- relevant `CURRENT_TASK.md` state;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md` for active Taste dossier/web-evidence ownership and compatibility decisions;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-dossier-contract-gap-audit-01.md`;
- `reviews/worker_reports/taste-dossier-prepublication-recovery-implement-01.md`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-03.md`;
- active dossier contract, web-evidence contract, schema, worker prompt;
- active strict validator;
- buffered/pre-publication validation path;
- snapshot/freshness/compatibility binding and pre-AI workflow triggers only as needed for these seven findings.

Run architecture preflight before implementation.

## Architecture invariants

Must remain true:

1. GitHub owns canonical scope/order/snapshot identity/group plan/progress/persistence/recovery/completeness.
2. Scheduled ChatGPT remains bounded research/synthesis + create-only transport.
3. The pre-publication validator remains a publication guard using the same canonical validation implementation, not a second control plane.
4. Do not add another queue, scheduler, retry manager, backlog manager or recurring production stage.
5. Immutable transport artifacts remain immutable.
6. Group size remains `3`.
7. Existing package-member and DLC dossier identity behavior remains unchanged.
8. Do not change downstream Taste-fit/ranking/pricing/commercial logic.
9. Do not weaken any existing evidence guard to make new fixtures pass.

If one of the seven findings would require violating these invariants, STOP and report `blocked` rather than inventing a new architecture.

# Required gap closures

## GAP-01 — Expired dossier must not advance canonical progress

Audit finding: a dossier can have internally consistent `generated_at_utc + ttl_days == expires_at_utc` but already be expired at ingest time; strict canonical ingress can currently accept it and advance progress.

Required semantics:

- canonical ingestion must require the submitted dossier to be fresh **at ingest/acceptance time**, not merely internally date-consistent;
- an already-expired dossier must not be persisted as accepted work and must not advance `completed_required_count`;
- pre-publication validation must enforce the same rule under its canonical validation path;
- preserve bounded future-clock tolerance only where already intentionally defined; do not convert this into arbitrary wall-clock looseness;
- same-day snapshot preservation must not leave canonical progress claiming completion for a dossier that was already stale when accepted.

Add deterministic regression for an expired-but-formula-valid V2 dossier.

## GAP-02 — One physical feedback item must not count multiple times via URL aliases

Audit finding: literal-string dedupe can treat one physical review/post as multiple distinct feedback records when URL aliases differ only by query parameters, fragments, harmless formatting, or equivalent source locator forms.

Required semantics:

- recurrence/`mention_count` must count distinct attributable physical feedback items, not distinct URL strings;
- normalize or derive a deterministic compact `feedback_item_identity` sufficient to reject obvious aliases of the same item;
- remove fragments and non-identity tracking/query noise where safe;
- do not collapse genuinely distinct items on the same discussion/review surface;
- source diversity must not be inflated by aliasing one physical source/item under multiple source IDs;
- preserve the no-username/profile/excerpt policy from PR #36.

Because PR #36 now rejects profile-scoped locators, do not rely only on the audit's old profile-URL example. Prove current-main behavior with a still-permitted non-identifying item-level locator alias if one remains reachable. If PR #36 already makes the entire gap unreachable, document and regression-test that instead.

## GAP-03 — Counted feedback records must identify an individual feedback item

Audit finding: a reviews index/search/listing/aggregate page or vague human-readable label can masquerade as one attributable feedback record.

Required semantics:

- every `player_feedback_record` counted toward an observation must have an auditable item-level stable locator/identity;
- known collection/list/index/search/aggregate surfaces may remain valid as parent/context sources but cannot themselves count as one feedback item;
- vague labels such as `Steam review found on <date>` without a stable item identity are insufficient;
- do not require or store username/profile identity to make a locator auditable;
- do not store raw review text.

Implement the narrowest source-type/domain-aware item-locator rule needed to make the current worker's allowed evidence auditable. Fail closed where an item cannot be uniquely located.

Add positive fixtures for valid non-identifying item locators and negative fixtures for collection/search/index/vague refs.

## GAP-04 — `recent` / `older` must be coherent with publication date

Audit finding: a source dated years earlier can be labeled `freshness:"recent"` and satisfy a current-state claim.

Required semantics:

- when `publication_date` is present, its age must be mechanically coherent with the `freshness` classification relative to dossier generation/research time;
- use one canonical threshold consistent with the active evidence contract's meaning of recent research (roughly the last 12 months when available), made explicit in config/contract rather than hidden magic where practical;
- a dated older source cannot satisfy `recent/current_state` merely because the worker labels it recent;
- preserve a clearly defined path for genuinely unknown/undated sources; do not fabricate dates;
- current-state observations must still require recent current-state support.

Add boundary regressions around the threshold and a clear old-date/`recent` rejection fixture.

## GAP-05 — Russian attempt status must be mutually coherent both directions

Audit finding: current validation checks `found_and_used -> bound Russian/mixed feedback`, but allows the inverse contradiction: used Russian feedback with `searched_not_found_or_insufficient` or `source_access_unavailable`.

Required semantics:

- if any Russian/mixed player-feedback record is actually bound to an observation in a way that qualifies as Russian evidence under the active contract, `russian_attempt` must be `found_and_used`;
- `searched_not_found_or_insufficient` and `source_access_unavailable` must reject dossiers that actually use qualifying Russian evidence;
- preserve any intentional distinction between `russian` and `mixed` only if explicitly supported by the active contract; do not create a new ambiguity;
- retain the already-fixed forward implication.

Add exact inverse-direction regressions.

## GAP-06 — `conflicts[]` strength must be attributable to player feedback or be unquantified

Audit finding: `conflicts[]` can claim strong recurrence using only official/non-player sources and has no feedback-record/count binding.

Implement one coherent model, preferring the smallest extension consistent with the active dossier purpose:

### Preferred model
Bind conflicts to attributable `player_feedback_ids` with count/recurrence semantics analogous to observations where conflict recurrence is asserted.

Requirements if using this model:
- `mention_count`/distinct record semantics must apply;
- official/professional/context-only sources cannot create player recurrence;
- alias/dedupe and Russian/temporal rules apply where relevant;
- no raw bodies/usernames/profiles/excerpts.

### Alternative model
If architecture/product semantics show `conflicts` are only a qualitative synthesis note, remove recurrence strength from conflict objects and validate them as unquantified contradiction summaries backed by resolvable sources.

Do not leave the current hybrid state where `strong` has no auditable meaning.

Whichever model is chosen, add regressions showing official metadata alone cannot manufacture a `strong` player-feedback conflict.

## GAP-07 — Evidence compatibility binding must be content-complete and propagate changes

Audit finding: snapshot compatibility/binding omits meaningful revision/content identity and the pre-AI workflow does not trigger on all active semantic contract files.

Required semantics:

- semantics-changing changes to the active dossier schema, web-evidence contract, or worker prompt must change the compatibility binding/snapshot identity even if top-level schema/version numbers are unchanged;
- include the relevant explicit revisions and/or deterministic content hashes in one canonical binding rather than relying only on coarse name/version tuples;
- the canonical worker projection/group plan must expose enough binding to prove the Scheduled worker is operating against the intended contract;
- pre-AI build workflow must trigger when any active semantic contract/prompt file that affects dossier validity/worker behavior changes;
- same-day preservation must rebuild when this binding changes;
- old cached dossiers and old immutable artifacts must not silently satisfy a changed binding;
- do not require manual version bumps as the only safety mechanism.

Add regressions for:
1. schema/contract revision/content change with unchanged top-level version;
2. prompt body change with unchanged coarse version token;
3. same-day rebuild on binding change;
4. stale old artifact/dossier cannot be rebound to the new compatibility identity.

# Shared validation requirement

Any new strict rule added for GAP-01..06 must automatically apply to pre-publication validation through the shared canonical implementation introduced by PR #36.

Add a focused regression proving at least one newly-added rule fails both:
- pre-publication validation; and
- canonical buffered ingestion validation
for the same candidate group.

Do not create a second handwritten pre-publication rule set.

# Migration / activation

If these changes alter semantic validity or compatibility, bump the minimal appropriate revision/binding and let the normal GitHub-owned snapshot rebuild/recovery path activate it.

Requirements:

- no manual queue/cache/progress/receipt edits;
- no manual dossier artifact creation;
- no Scheduled Task run;
- old incompatible snapshot/artifacts must become stale/inert through normal binding/rebuild/quarantine semantics;
- fresh canonical snapshot should start with truthful progress and group size 3;
- no accepted work may be silently rebound across an incompatible evidence binding.

# Deterministic validation

Run the repository-defined canonical tests/CI plus focused fixtures for every GAP-01..07 that remains reachable on current main.

At minimum prove:

- expired dossier cannot advance canonical progress;
- aliasing cannot inflate `mention_count` or source diversity;
- collection/index/search/vague locator cannot count as an individual feedback record;
- old dated source cannot masquerade as `recent`;
- Russian attempt inverse contradictions fail;
- conflict strength cannot be manufactured from non-player metadata;
- semantic contract/prompt changes invalidate same-day compatibility and trigger rebuild;
- new rules are enforced before immutable publication through the shared pre-publication validator;
- previous aggregate-count, recurrence, Russian Store, privacy/content, temporal, package-member and buffered recovery regressions remain green;
- group size remains 3.

# PR / merge / activation

Use normal worker branch -> PR -> canonical CI -> merge path.

If green and ordinary repository-owned activation is safe under the task, merge and let the normal pre-AI workflow rebuild the canonical snapshot.

Do not press Scheduled Task `Run now`.

If another unrelated change lands on `main` while working, reconcile narrowly; do not absorb unrelated work into this task.

# Prohibitions

Do not:
- run a new broad audit;
- process live dossier games manually;
- run Scheduled Task `Run now`;
- change group size away from 3;
- weaken strict validation;
- reintroduce usernames/profiles/excerpts;
- store raw review bodies;
- change downstream Taste/ranking/pricing/commercial logic;
- implement package edition-quality scoring;
- create another control plane or external service;
- use any other repository.

# Definition of Done

Complete only when:

- all GAP-01..07 are reconciled against current main;
- every still-reachable proven gap is mechanically closed;
- any gap already closed by PR #36 is regression-proven and explicitly documented;
- shared pre-publication/canonical validation parity remains intact;
- compatibility binding is content-complete enough to force correct same-day rebuilds;
- relevant tests/CI pass;
- fresh canonical state is activated through GitHub-owned mechanisms if binding changed;
- group size remains 3;
- no Scheduled Task run occurred;
- durable report is in `main`.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `blocked`

# Durable report

Publish to `main`:

`reviews/worker_reports/taste-dossier-contract-gaps-implement-01.md`

Report must include:

- architecture preflight;
- exact current-main reconciliation for GAP-01..07 (`implemented_now` vs `already_closed_on_current_main`);
- exact rule/representation chosen for each implemented gap;
- alias/item-identity strategy;
- freshness threshold semantics;
- Russian inverse-state rule;
- conflict model chosen and why;
- compatibility binding contents and workflow-trigger changes;
- proof shared pre-publication/canonical validation parity remains intact;
- PR/merge/CI refs;
- fresh snapshot id, progress, expected sequence and first group descriptor after activation if binding changed;
- proof group size remains 3;
- confirmation no Scheduled Task `Run now` occurred;
- remaining risks;
- exactly one next step.

On success, the one next step should be: run the existing Scheduled Task exactly once, then perform a separate READ/VALIDATE live acceptance against the fresh snapshot.

Ensure the durable report is in `main` before completion. Stop after report publication.