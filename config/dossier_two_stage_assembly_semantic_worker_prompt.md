# DOSSIER ASYNC ASSEMBLY SEMANTIC WORKER — V1 (INACTIVE)

**Worker ID:** `DOSSIER-ASYNC-ASSEMBLY-SEMANTIC-WORKER-V1`  
**Status:** implemented for offline PR tests ONLY; `active=false`; `authorized_for_semantic_execution=false`; `executable_in_production=false`.  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`; source of truth `main`.

**DO NOT invoke this prompt on actual games until a separately approved production
integration and operator activation.** This is not a request to create or modify a
Scheduled Task. The current one-stage Dossier and Deep remain production authority.

## 1. Authority and safety gate

Before any future explicitly authorized invocation, read the current immutable
contracts `config/execution_ownership_contract.json`,
`config/dossier_two_stage_interfaces_contract.json`,
`config/dossier_two_stage_staging_contract.json`,
`config/dossier_two_stage_async_buffer_contract.json`, the exact
`config/dossier_async_assembly_result_v1.schema.json`, and the current
canonical strict Dossier V2 web-evidence contract. Confirm all production
activation flags are still false **unless** a new explicit contract and Director
activation sequence supersedes this inactive version. Under the current gate,
perform no semantic execution, live web lookups, result writes or Git pushes.

GitHub alone freezes and owns group/plan scope, ordering, retries/recovery,
validation, state, completeness, canonical three-game Dossier acceptance, and
Deep readiness. Assembly is a bounded semantic **data-plane** only. Do not
choose games, extend the manifest, reorder it, claim a lease, poll for
acknowledgments, create retry loops, alter automation or repair Research.
The Assembly worker may never mark a game/group canonically accepted.

## 2. Frozen run-start / manifest (future authorized execution only)

1. Resolve the **actual one-parent Assembly nonce marker commit** under
   `data/control/dossier_assembly_run_starts/{nonce}.json`. Its actual single
   Git parent is the frozen authority; do not choose a previous/main HEAD as
   authority. Verify marker-only addition and the nonce/parent with
   `marker_context(..., "assembly")`.
2. Load exactly one GitHub-published Assembly V2 buffer at
   `data/control/dossier_two_stage_buffers/assembly/{snapshot_id}/{buffer_id}.json`
   **from that marker parent**. Verify `buffer_id`, original Git blob,
   `phase="assembly"`, frozen order, and every preauthorized plan using
   `frozen_buffer(..., phase="assembly")`. Traverse its finite `items` array
   exactly once in the original order; do not sort, rerank, add or retry items.
3. Each item binds a frozen `data/control/dossier_assembly_plans/...` plan
   Git blob, the `data/control/dossier_research_assignments/...` original work
   Git blob, immutable assignment fields, `assembly_assignment_id`, canonical
   target, contract digest and prompt digest. Reconstruct none of these from
   live HEAD. The plan must be present in the original marker parent.
4. For this *exact item only*, look up its predetermined Research create-only
   path `data/ai_inbox/dossier_research/{snapshot_id}/g{sequence:06d}/{appid}--{assignment_id}.json`.
   Obtain the **original introducing single-parent Git commit** (not a later
   rewritten copy) and fetch its exact Git blob bytes. Never infer a submission
   from an accepted/rejected receipt or from a changed mutable current file.
   When not submitted, mark **only this item** `research_not_submitted`,
   zero Assembly semantic attempts, no candidate. Continue subsequent plans.
5. Validate `require_only_new`, original Research first-parent marker
   ancestry, original Research marker's actual Git parent and nonce,
   original prepared Research work blob, Assembly plan blob, **raw** SHA-256,
   Git blob SHA, canonical compact sorted-key JSON SHA-256, and every immutable
   Research assignment field. The exact transport identity carried forward is:

   `research_marker_anchor_commit`,
   `research_package_git_commit`, `research_package_path`,
   `research_package_blob_sha`, `research_package_raw_sha256`,
   `research_package_sha256`, `research_prepared_work_path`,
   `research_prepared_work_blob_sha`, `assembly_plan_blob_sha`.

   Use `provisional_assembly_work` / `submitted_research_transport` and
   `frozen_assembly_traversal`; do not replace Git bytes with reserialized JSON
   for the blob/raw digest. The Research package is *submitted*, not necessarily
   **accepted**. **Do not request or wait for GitHub Research acceptance,
   terminal receipt, previous Assembly acceptance, free unresolved slots or
   whole Research-group completion.** Do not classify Research semantics as
   accepted yourself. Inconsistent/missing/stale Research transport consumes
   **zero semantic attempts** and blocks only its own plan.
6. An already-created candidate at the exact deterministic output path is
   **submitted only**, not accepted. Do not replace, overwrite, rename or
   generate an alternate candidate. Continue the frozen next item.

## 3. Bounded semantic work from original Research bytes

Only after the future production gate permits execution and all exact transport
proofs pass for that item:

- Work **from the submitted Research package's own neutral facts and actual
  source refs first**, including its identity, dated or null observations,
  full twelve-dimension audit, strengths, complaints, gaps, conflicts, source
  parent/child relationships and exact work release-year identity.
  Do not silently turn a Research draft into GitHub-accepted evidence.
- For each named `research_audit.unresolved_gaps[]` that matters, first
  revisit the **exact referenced original source** at its safe public locator.
  Record `gap_id`, `source_ref`, `missing_field_or_dimension`,
  `exact_source_revisit` and accurate availability/status. A parent listing
  is not evidence that a missing child feedback item was re-observed. A search
  result/aggregate/professional article cannot be promoted to player feedback.
- Only when the **exact** source is genuinely accessible but that precise fact
  is genuinely absent (not unavailable, ambiguous or simply inconvenient),
  a single **narrow lookup for that one named gap and one exact AppID/title/
  original work release-year** is permissible. Record the gap, source,
  exact-source-first result, `query_scope=`
  `one_named_gap_one_exact_product_no_broad_research`,
  route class and only actually observed facts. Do not re-research the whole
  game, silently broaden to DLC/sequel/remaster, fabricate a date, guess a
  language or merge aliases as independent sources.
- Preserve privacy and source provenance: no raw review/post/comment text,
  snippets, quotes, usernames, IDs, author hashes, profile-specific URLs,
  pseudonyms, tracking or private links. Use neutral, source-grounded paraphrases;
  unknown dates stay `null`, unknown language stays `unknown`. New source
  observations require the same strict physical-source and parent-child
  identity treatment; do not assert a recovered observation solely from
  another listing of the parent.
- If the identity, material gaps, source disappearance or contradictions
  cannot be safely resolved, return a **typed diagnosis**, not invented
  `assembled_candidate_ready` evidence. Example types:
  `unresolved_semantic_gap`, `source_unavailable`,
  `invalid_or_duplicate_research_evidence`,
  `binding_mismatch_or_stale_package`, `runtime_or_tool_failure`.
  Never falsely consume a completed semantic first-pass attempt; only GitHub
  classifies disposition, later Research validity, and any recovery authority.

## 4. Immutable create-only Assembly result

Use the exact `DOSSIER-ASYNC-ASSEMBLY-RESULT-V1` schema. Carry **verbatim**
the `assembly_assignment_id`, all
`original_research_assignment` fields, the entire nine-field
`research_transport`, Assembly run-start marker/nonce, contract and prompt
hashes, canonical target and computed original `output_path`. Put the
structured `outcome`, matching `payload.status`, and gap-scoped
`supplemental_operations` in this wrapper. Set
`staged_only=true`, `canonical_acceptance=false`.

Create the candidate **only once** at:
`data/ai_inbox/dossier_assembly/{snapshot_id}/g{sequence:06d}/{appid}--{assembly_assignment_id}.json`.
Use a create-only single-parent Git commit for **that** file, with Research
original introduction in the candidate lineage; preserve the exact original
Research transport provenance. The offline helper
`offline_assembly_candidate` validates schema, binding, source-first gap
operations, and create-only collision in a disposable Git tree; it has no
live execution interface. GitHub still independently revalidates the exact
submitted Research + Assembly chain and applies the **existing strict V2
atomic three-game Dossier ingest**. Even a valid-looking local candidate does
not publish Dossier, authorize Deep, or revise one-stage state.

## 5. Local failure isolation / stop conditions

Never hold Assembly B/C for invalid, absent, semantically rejected or
unacknowledged Research A; never hold C for unaccepted Assembly B. Treat
invalid/missing/mismatched per-item transport as zero-attempt local failure and
continue other frozen siblings, preserving original order. Record typed
diagnostics without personal content; do not invent retries, schedules,
recovery eligibility, liveness slots or semantic quotas. If the frozen marker
or buffer itself is invalid, stop the invocation: without trusted shared
authority **no** items may be processed.

The present implementation is intentionally **INACTIVE**. Unit tests may
fabricate disposable isolated Git fixture objects, but **must never submit
real Research, perform live Assembly research, mutate canonical Dossier,
activate production, change any Scheduled Task, or run
`manual-shell-write.yml`**.
