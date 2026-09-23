# WORKER TASK — PROGRESSIVE FAST + DEEP ZERO COMPLETION DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository. If GitHub/tool opens another repository by default or the repository target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `progressive-fast-deep-zero-completion-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

## User authorization and problem

The user explicitly assigned a second independent worker chat to analyze why the current Statistics page shows useful Dossier progress but effectively zero completed Fast and Deep personalized results.

Observed trigger from the deployed Statistics view at assignment time:
- Fast current scope: 511;
- Fast processed/attempted: 86;
- Fast completed fit: 0;
- Fast completed not-fit: 0;
- Fast incomplete/no-conclusion: 82;
- Fast errors: 4;
- Dossier accepted: 12 / 511;
- Deep first-pass attempted: 2;
- Deep authoritative/final completed: 0.

These are diagnostic trigger values only. Re-read fresh `main` and prove the current values before drawing conclusions.

The user wants the real reason, not a UI explanation.

## START

First open the current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Before diagnosis, read the minimum canonical files needed to establish ownership and semantics:
- `DIRECTOR_TASK_BOARD.md`
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/execution_ownership_contract.json`
- current Fast and Deep worker prompts referenced by those contracts
- current Dossier contract / evidence binding only where needed to explain Deep evidence sufficiency

Use `PROJECT_ROUTES.md` before broad repository search.

## Architecture preflight

Record before diagnosis:

1. GitHub owns Fast/Deep scope, exact current identity, attempt accounting, persistence, recovery authorization and statistics projection.
2. Scheduled ChatGPT workers are bounded semantic data-plane only.
3. This task is diagnostic only. It must not change contracts, prompts, code, state, work manifests, results, recovery authorization, workflows or scheduler configuration.
4. Do not run Fast, Deep or Dossier semantic production.
5. Do not create recovery authorizations or replay attempts.
6. The only permitted write is the durable diagnostic report at the exact path below.

## Goal

Determine why current Fast and Deep statistics show zero completed personalized results despite many consumed Fast attempts and successful Dossier production.

The diagnosis must distinguish at least these possibilities rather than assuming one:

- current attempts genuinely produce almost only `analysis_incomplete / insufficient_evidence`;
- successful historical Fast results exist but are not current because generation/work identity changed;
- current-scope/statistics projection is excluding otherwise valid results;
- worker prompt/contract completion thresholds are too strict for the evidence actually supplied;
- Fast semantic input is systematically insufficient for a lightweight fit/not-fit conclusion;
- Deep Dossier evidence is present but not usable under the current Deep completion contract;
- Deep worker is failing to use evidence that is actually sufficient;
- transport/validation/runtime errors consume attempts without semantic completion;
- another exact current-identity or producer projection defect is causing completed results not to count.

## Required investigation

### A. Prove current statistics from canonical truth

From fresh `main`, establish the exact current:
- Fast total scope;
- Fast attempted;
- Fast completed fit;
- Fast completed not-fit;
- Fast incomplete;
- Fast error;
- Fast skipped due to completed Deep;
- Fast remaining;
- Dossier accepted/pending/recovery;
- Deep total target;
- Deep first-pass attempted;
- Deep final/authoritative completed fit/not-fit;
- Deep incomplete/recovery;
- Deep waiting for Dossier;
- Deep ready/pending.

Explain the arithmetic and identify the exact producer path that derives these counts.

### B. Fast: explain zero current completed

Inspect the current exact Fast state/work relationship, not just aggregate counters.

Required:
1. Count current exact Fast outcomes by:
   - analyzed_fit;
   - analyzed_not_fit;
   - analysis_incomplete grouped by issue code;
   - error projection class.
2. Separately count historical/non-current Fast state entries by outcome.
3. If historical `analyzed_fit` or `analyzed_not_fit` entries exist, prove exactly why they do not count as current:
   - generation mismatch;
   - work_id/fingerprint/context mismatch;
   - no longer current candidate;
   - business exclusion;
   - another exact reason.
4. Do not say “stale” without proving the binding that changed.
5. Inspect a bounded stratified sample:
   - at least 3 current `insufficient_evidence` Fast attempts;
   - every distinct current Fast error class, with at least one exact example per class;
   - at least 2 historical completed Fast results if such results exist.
6. For each sample, trace:
   - GitHub-prepared semantic input;
   - worker result/result receipt if available;
   - canonical ingest outcome;
   - current identity/binding;
   - why it becomes completed, incomplete, error, or non-current.
7. Determine whether the dominant Fast incompletes are expected under the current lightweight contract or indicate a systemic evidence/prompt mismatch.

### C. Fast errors: identify the four-error class precisely

Do not leave “4 errors” unexplained.

Prove the exact current issue-code distribution. For each error category such as `worker_failure` or `invalid_semantic_result`:
- count it;
- identify exact representative work IDs/appids;
- explain the immediate cause from the existing artifact/receipt/log evidence;
- classify as semantic insufficiency, runtime/tool failure, invalid worker output, validator mismatch, or other;
- state whether the defect is still live or historical.

### D. Deep: explain zero final completions

Inspect every current Deep first-pass attempt, because the count is small.

For each attempted current Deep item:
- exact appid/work_id;
- exact accepted Dossier binding/revision used;
- Deep result outcome and issue code;
- whether Dossier contained evidence relevant to making fit/not-fit;
- what evidence the Deep worker actually used or reported;
- why the result was accepted only as incomplete/recovery rather than final fit/not-fit.

Then determine whether zero final Deep results are caused by:
- genuinely insufficient Dossier evidence;
- Dossier contents being structurally valid but semantically too weak;
- Deep completion criteria being too strict;
- Deep prompt failing to use available Dossier evidence;
- mismatch between Dossier purpose and Deep evidence expectations;
- exact-binding/freshness issue;
- runtime/tool failure;
- another proven reason.

### E. Compare Fast vs Dossier vs Deep evidence design

Explain the intended evidence path in plain terms:

- What evidence does Fast receive?
- What evidence does Dossier add?
- What must Deep have to finalize fit/not-fit?
- Is the current system actually supplying that evidence?

Explicitly test whether the current architecture has a systemic gap where:
- Fast is intentionally too lightweight to decide most games, while
- Dossier gathers reviews/evidence, but
- Deep still cannot convert that evidence into a final personalized result.

If that is not the problem, prove the actual problem instead.

### F. Statistics vs actual system state

Determine whether the Statistics page is correctly exposing a real production problem or whether any count itself is wrong.

The report must give one of:
- `statistics_correct_system_semantics_broken_or_too_strict`
- `statistics_projection_bug`
- `mixed_root_causes`
- another precise classification.

### G. Recommended repair, but do not implement

If a defect is proven, propose the smallest correct implementation boundary.

Examples only:
- Fast worker prompt/evidence contract adjustment;
- Fast semantic-input enrichment from already GitHub-owned data;
- Deep prompt/evidence-use correction;
- Dossier-to-Deep evidence contract alignment;
- current-identity preservation/reuse fix;
- error-path validation/runtime correction;
- statistics projection correction.

For every proposed repair:
- identify the owning component;
- name the canonical contract that would authorize the change;
- state whether it changes business semantics or only fixes implementation drift;
- state whether existing incomplete attempts need explicit GitHub-owned recovery afterward;
- do not invent or execute the recovery.

Prefer one primary root cause and one bounded fix task if evidence supports that. If Fast and Deep have genuinely different root causes, say so and recommend separate tasks.

## Explicit prohibitions

Do not:
- modify source/config/contracts/prompts/workflows/state/work/results;
- run or edit any Scheduled Task;
- manually run Fast/PASS 1, Dossier or Deep/PASS 2 semantic work;
- authorize recovery;
- overwrite/delete/rebind immutable result artifacts;
- convert incomplete into completed manually;
- loosen validators merely to make counts nonzero;
- treat historical results as current without exact compatible binding proof;
- inspect another repository.

## Validation / acceptance

Prove at minimum:

- DIAG-01: current Fast/Dossier/Deep counts are independently reproduced from canonical state/projection.
- DIAG-02: Fast current exact outcome distribution is proven.
- DIAG-03: historical completed Fast results, if any, are reconciled against current identity and zero current-completed count.
- DIAG-04: all current Fast error classes are explained with exact evidence.
- DIAG-05: bounded representative Fast incomplete samples are traced end-to-end.
- DIAG-06: every current Deep attempted item is traced end-to-end.
- DIAG-07: Deep zero-final-completion cause is classified with evidence.
- DIAG-08: Dossier evidence availability vs Fast/Deep completion requirements is compared.
- DIAG-09: Statistics correctness vs system defect is explicitly classified.
- DIAG-10: no unsupported assumption that “workers do not run”; distinguish execution from useful completion.
- DIAG-11: no source/runtime/scheduler/recovery mutation occurred.
- DIAG-12: recommended repair respects GitHub control-plane ownership and names the canonical owner/contract.
- DIAG-13: durable report committed and reread from fresh `main`.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-fast-deep-zero-completion-diagnostic-01.md`

Keep it compact but evidence-complete. Include:
1. Task.
2. Architecture preflight.
3. Fresh current counts.
4. Fast findings.
5. Fast error breakdown.
6. Historical-vs-current Fast reconciliation.
7. Deep findings for every attempted item.
8. Dossier -> Deep evidence assessment.
9. Root-cause classification.
10. Whether Statistics is correct.
11. Recommended bounded repair task(s), without implementation.
12. DIAG-01..13.
13. Exact file/run/work/appid/commit refs.
14. Final status.
15. Exactly one recommended next Director step.

Allowed final statuses:
- `complete_root_cause_proven`
- `complete_multiple_root_causes_proven`
- `needs_deeper_recon`
- `needs_user_decision`
- `blocked`

Before completion, reread the committed report from fresh `main`.
