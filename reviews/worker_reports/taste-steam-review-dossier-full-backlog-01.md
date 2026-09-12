# Taste Steam Review Dossier — Full Backlog

**Task:** `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_01.md` + continuation `WORKER_TASK_TASTE_STEAM_REVIEW_DOSSIER_FULL_BACKLOG_CONTINUE_01.md`

**Branch:** `worker/taste-dossier-full-backlog-01`

**Status:** in progress — rationale preserved before checkpoint-progression changes

## Architecture rationale recovered from the focused pathology

The dossier preparation scope is the **full current canonical Taste queue** at `data/production/pre_ai/chatgpt_taste_queue.jsonl`, deduplicated by `appid` while preserving first-occurrence canonical queue order.

The active Taste pin (`data/production/pre_ai/taste_active_work_unit.json`) is deliberately **not** the dossier-preparation scope. It is a downstream semantic-input binding. Using it as preparation scope caused the observed pathology where the first `Run now` exposed only the active-pin-sized subset and made a technical batch look like the whole dossier backlog.

This choice is necessary because dossier preparation is neutral reusable Steam evidence, not a personalized Taste decision. A dossier can be prepared/reused independently of whether that app happens to be in the current active semantic pin. Fresh dossiers therefore remain reusable; missing or stale in-scope dossiers remain required; stale dossiers outside the current canonical Taste queue can be cleaned by GitHub-owned policy.

## Ownership invariant

GitHub remains the control plane. It owns:

- the canonical full dossier scope and its deterministic order;
- deduplication by `appid`;
- fresh/stale classification and cleanup policy;
- the bounded checkpoint presented to the external semantic worker;
- checkpoint progression, completeness, retry/resume state and persistence;
- validation that a submission exactly matches the currently prepared checkpoint.

The scheduled ChatGPT worker remains a constrained semantic data-plane producer. It may only process the explicit GitHub-prepared manifest, inspect Steam evidence, synthesize neutral compact dossiers and submit them through the repository interface. It does not invent scope, queue ordering, retry policy, backlog management or completion rules.

## Checkpoint semantics

A checkpoint size of `10` is an internal durability/runtime boundary, **not** a production quota, daily cap or completion threshold. Full-backlog completeness is evaluated against the entire canonical required scope. After one accepted checkpoint, GitHub must rebuild the manifest and expose the next deterministic checkpoint; the same scheduled-task invocation may continue through successive checkpoints until the backlog is exhausted or a real platform/runtime limit stops it. A later invocation must resume from the remaining GitHub-owned required scope rather than restarting or treating the previous checkpoint as completion.

No second dossier scheduler, no replacement scheduler, no new Taste producer, no new daily production limit and no age-priority policy are introduced by this work.

## Existing branch chain confirmed before continuation

The required six commits were found on the branch before new work began:

- `66c8901745c7b953d88c20b8de69f1bf8f6549cd` — Reconcile dossier backlog ownership contract
- `28a6cdae17518fb6324332517f139497b2ced450` — Build dossier work from full canonical Taste backlog
- `f01845137023189da20abadcec1f8e9ee4bab647` — Cleanup dossiers against full Taste scope
- `131c4629c54af07a9955478af872587e87a6dcc9` — Project full Taste backlog into dossier work manifest
- `9f50843adae9692bf2c0386bf79ef5d88b9856c8` — Cover full dossier backlog reconciliation
- `83aa9abc2c5d9c96d979f29dee92b8bf1b2e1f5d` — Use full queue fixture in dossier test

The branch HEAD at continuation start was `83aa9abc2c5d9c96d979f29dee92b8bf1b2e1f5d`.