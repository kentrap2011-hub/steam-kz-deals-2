# WORKER TASK — DEEP LEGACY FULL REANALYSIS WITH PRESERVED POSITIVES 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `deep-legacy-full-reanalysis-with-preserved-positives-01`
Mode: `ONE-OFF MIGRATION / CONTRACT-FIRST IMPLEMENT / ORCHESTRATE / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/deep-legacy-full-reanalysis-with-preserved-positives-01.md`

## Explicit user authorization

The user explicitly authorizes a one-off full reanalysis of CURRENT games that already have an authoritative completed Deep result produced under the old contract and therefore still project `negative_assessment_status = legacy_not_evaluated`.

The user explicitly clarified:

- do NOT preserve the old final Deep conclusion merely because it was previously accepted;
- each targeted game must be evaluated fully again;
- the existing positive evidence is already available and must be reused rather than researched again;
- the newly evaluated negative/mixed evidence may legitimately change:
  - fit/not-fit outcome;
  - fit level;
  - confidence;
  - taste factors;
  - risk/caution presentation;
  - final score/rank through already-existing canonical scoring policy;
- Dossier should remain able to run independently in parallel.

This is a finite, one-off historical reanalysis authorization. It is not permission to create a recurring second Deep stage or new scheduler.

## Canonical basis

Read and obey:
- `PROJECT_DECISIONS.md#PPD-004`
- `PROJECT_DECISIONS.md#PPD-006`
- `PROJECT_DECISIONS.md#PPD-007`
- `PROJECT_DECISIONS.md#PPD-008`
- `PROJECT_DECISIONS.md#PPD-009`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass2_worker_prompt.md`
- `config/progressive_pass2_result_schema.json`
- `config/progressive_personalization_contract.json`
- `config/execution_ownership_contract.json`
- accepted reports:
  - `reviews/worker_reports/jedi-deep-missing-negative-evidence-diagnostic-01.md`
  - `reviews/worker_reports/deep-balanced-negative-assessment-contract-fix-01.md`
  - `reviews/worker_reports/deep-positive-evidence-card-projection-fix-01.md`

PPD-009 intentionally did not automatically replay old completed Deep results. This task is the separately user-authorized reanalysis/migration that PPD-009 reserved for later explicit authorization.

## Goal

Create a finite GitHub-owned one-off reanalysis of every CURRENT authoritative Deep result that:

- belongs to the current semantic/work identity;
- was completed under the old contract;
- lacks the new balanced negative assessment and therefore projects `legacy_not_evaluated`.

For every target:

1. reuse the already accepted positive Deep evidence as the favorable side of the analysis;
2. do not perform fresh web research for positive evidence;
3. evaluate the negative and mixed evidence from the exact Dossier frozen for this migration invocation;
4. make a new full personalized Deep judgment using both sides;
5. allow the new authoritative result to differ from the old one when evidence supports that;
6. keep the old Deep result/history auditable rather than silently overwriting its provenance.

This is not merely a “fill the missing minus field” migration.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. relevant Fast/Dossier/Deep routes in `PROJECT_ROUTES.md`;
5. canonical decisions PPD-004 / 006 / 007 / 008 / 009;
6. current PASS 2 contracts/prompt/schema;
7. execution ownership;
8. current PASS 2 state/work;
9. current accepted Dossier projection/storage;
10. exact existing Deep run-start marker/receipt and transport path;
11. only the smallest scripts/workflows/tests necessary.

## Mandatory architecture preflight

Before writes, prove all of the following:

1. GitHub remains sole owner of:
   - migration scope;
   - ordering;
   - immutable evidence/profile binding;
   - authorization;
   - validation;
   - persistence;
   - current-result selection;
   - completeness accounting.
2. Existing `Progressive Deep Worker` remains the only semantic runtime used.
3. The interactive worker chat does not manually author per-game semantic conclusions.
4. No second scheduler, recurring stage, retry daemon, queue owner, quota, or backlog manager is created.
5. Existing Scheduled Task settings are not modified.
6. Dossier remains an independent neutral evidence stage and can continue normal production concurrently.
7. Historical old Deep result remains retained as history/audit after the new reanalysis becomes current.
8. This one-off migration cannot recur automatically after completion.
9. Normal current Deep first-pass and recovery semantics remain unchanged for non-migration work.

If current architecture cannot express the migration safely, add the smallest new canonical decision (for example PPD-010) BEFORE contract/runtime changes.

## Frozen migration scope

GitHub, not the chat, must derive a finite durable manifest.

Target only items satisfying ALL:

- current eligible game identity;
- current authoritative completed Deep result exists;
- result is old-contract / `legacy_not_evaluated`;
- result has trustworthy accepted positive evidence or an explicitly valid old not-fit evidence basis;
- exact current accepted Dossier exists at the migration freeze authority;
- item has not already received an accepted result from this migration.

Exclude:
- new-format Deep results that already include the PPD-009 negative assessment;
- incomplete/recovery-owned Deep;
- stale historical identities;
- items without a safe current migration evidence binding.

Record:
- migration ID;
- immutable authority commit;
- exact target count;
- ordered target IDs;
- exact result paths;
- migration status counts.

## Evidence model

### Positive side — reuse, do not research again

For old `analyzed_fit` targets:

- reuse the accepted old Deep `positive_evidence` as the positive semantic evidence;
- reuse its exact provenance/binding;
- do NOT perform fresh web searching or external research to find positive reasons;
- do not require Dossier to recollect favorable evidence merely for this migration.

The old taste factors and fit level are a baseline, not an immutable conclusion. The new full semantic judgment MAY revise taste factors, confidence, fit level or outcome after considering the negative side.

For old `analyzed_not_fit`:
- reuse the old accepted not-fit evidence as the existing unfavorable/decision baseline;
- apply the current balanced-negative contract coherently;
- do not invent positive evidence that was never present.

### Negative/mixed side — frozen current Dossier

At migration invocation start, use the exact accepted Dossier content/binding that is current at the GitHub-selected immutable migration authority.

Evaluate:
- all negative observations;
- all mixed observations;
- all conflicts;
- relevant friction/trade-off evidence required by PPD-009.

Do not substitute Dossier writes that arrive after the frozen migration authority into the current invocation.

## Full reanalysis semantics

The existing Deep worker must produce a NEW authoritative migration result that can legitimately become:

- `analyzed_fit`;
- `analyzed_not_fit`;
- `analysis_incomplete` if evidence cannot support a responsible full conclusion.

For a completed fit/not-fit result, produce the full current contract, including:
- fit/not-fit conclusion;
- fit level/confidence where applicable;
- current taste factors where applicable;
- positive evidence references reused from the old accepted Deep result, without new positive research;
- balanced `negative_assessment`;
- exact migration provenance.

The new result must be allowed to change the old conclusion if the negative assessment materially alters fit.

Do not artificially preserve:
- old fit outcome;
- old fit level;
- old confidence;
- old taste factors;
- old rank.

But do preserve the old result as historical state/audit.

## Result precedence and history

Design a migration-safe current-result model:

- original Deep completion remains immutable historical evidence;
- accepted migration reanalysis becomes the CURRENT authoritative Deep result for that same current game identity;
- effective result projection uses the newest canonically accepted migration revision;
- history retains both old and migrated revisions with explicit provenance;
- no ambiguity about which revision drives current card/ranking;
- failure/unresolved migration must follow an explicit safe rule and must not silently erase a previously trustworthy old result without contract basis.

Define the unresolved migration behavior explicitly before implementation. Prefer fail-safe continuity unless the canonical decision justifies otherwise.

## One-off migration work mode

Use the existing Deep control plane.

If needed, add a bounded work mode such as:
`legacy_full_reanalysis`.

Requirements:

- GitHub prepares the exact immutable migration manifest;
- existing Deep run-start V2 authority/receipt model is reused or coherently extended;
- the worker reads frozen migration inputs from GitHub-selected authority;
- migration result binds to:
  - migration ID;
  - prior accepted Deep revision identity;
  - current semantic/work identity;
  - exact profile pin;
  - frozen current Dossier SHA/binding;
  - old accepted positive evidence provenance;
  - GitHub authorization;
- accepted migration does NOT pretend to be another normal first-pass attempt;
- normal first-pass attempt count/history is preserved;
- migration has separate finite accounting;
- invalid transport is zero-effect and fail-closed;
- no ordinary recovery authorization is fabricated to force already completed items back into normal Deep work.

## Dossier parallelism — REQUIRED

Dossier may continue its normal work throughout this migration.

Prove:

- Dossier does not need to be paused;
- Dossier writes before the migration run-start authority are naturally included in that frozen view;
- Dossier writes after the migration authority belong to later work and do not alter the current frozen invocation;
- migration does not edit Dossier state, prompt, recovery, schedule or queue;
- existing shared-writer serialization protects Git persistence;
- no whole-`main` stability rule is reintroduced.

This should follow the accepted PPD-008 marker-parent authority model where practical.

## Semantic execution boundary

The worker chat may implement and validate the migration control path.

The worker chat MUST NOT manually write the per-game semantic reanalysis conclusions.

Actual per-game semantic reanalysis must be performed by the existing canonical `Progressive Deep Worker` against GitHub-prepared migration work.

Do not create/edit/enable/disable/reschedule that Scheduled Task.

If the external Deep worker has not naturally consumed the prepared migration by the time implementation is ready:
- leave the migration durably prepared;
- report exact pending count/state;
- do not impersonate it.

If it does consume migration work during this task:
- continue end-to-end validation through canonical persistence and site publication.

## Migration observability

Expose separately from normal first-pass metrics:

- migration ID;
- total scoped;
- pending;
- submitted;
- accepted;
- changed_fit_outcome count;
- unchanged_fit_outcome count;
- analysis_incomplete/unresolved count;
- completed_with_confirmed_risk count;
- completed_with_caution count;
- completed_no_relevant_negative count;
- last accepted migration write time;
- migration complete boolean.

Do not merge these into normal first-pass attempt counts.

## Validation

Required regressions:

1. scope contains only current authoritative old-contract / legacy-not-evaluated Deep results;
2. new-format Deep results excluded;
3. stale identities excluded;
4. old positive evidence is reused without fresh positive research;
5. frozen Dossier at migration authority is used;
6. later parallel Dossier writes do not substitute into an in-flight migration;
7. migration result may change fit -> not_fit when grounded evidence supports it;
8. migration result may keep fit while adding caution/risk;
9. taste factors/fit level may change when semantically justified;
10. old Deep result remains in history;
11. accepted migration becomes current authoritative result;
12. unresolved migration behavior follows explicit canonical rule;
13. confirmed risk uses existing risk policy only;
14. caution creates no new score penalty;
15. completed-no-relevant-negative requires complete negative candidate evaluation;
16. no new normal first-pass attempt is consumed;
17. invalid/mismatched migration transport is fail-closed;
18. normal Deep first pass/recovery unaffected;
19. Dossier path unaffected;
20. migration is finite and does not recur after completion.

## End-to-end validation

If migration semantic execution occurs during this task:

- verify canonical persistence for all accepted migration results;
- verify current Deep counts/revision counts;
- verify visual rebuild and Pages deploy;
- inspect bounded samples including `game:1172380` plus at least:
  - one result whose old fit conclusion stays unchanged;
  - one result whose risk/caution state changes;
  - if any exist, one result whose fit/not-fit outcome changes;
- confirm positive reasons remain grounded and are not re-researched;
- confirm current cards/ranking use migrated result;
- confirm old result remains auditable.

If execution has not yet run:
- report implementation prepared plus exact migration pending count;
- do not claim the games were re-evaluated.

## Hard prohibitions

Do not:
- manually author per-game reanalysis in this worker chat;
- perform new positive web research;
- replace old positives merely because reanalysis occurs;
- freeze the old fit conclusion;
- automatically convert every criticism into a risk;
- change Dossier semantics/execution/recovery;
- pause Dossier;
- process Dossier backlog manually;
- change Scheduled Task settings;
- add a second semantic scheduler;
- add new ranking weights or penalty codes;
- create blind retry loops.

## Report

Write:
`reviews/worker_reports/deep-legacy-full-reanalysis-with-preserved-positives-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Canonical migration decision`
4. `Frozen scope`
5. `Positive-evidence reuse`
6. `Frozen Dossier evidence`
7. `Changes`
8. `Dossier parallelism proof`
9. `Execution state`
10. `Validation`
11. `Published result`
12. `Changed outcomes`
13. `Remaining / unresolved`
14. `Status`
15. `Recommended next step` — exactly one bounded next step
16. exact PR/commit/run/artifact/migration refs
17. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.
