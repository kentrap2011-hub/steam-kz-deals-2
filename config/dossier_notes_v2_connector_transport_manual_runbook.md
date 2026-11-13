# Dossier Notes V2 — GitHub Connector transport, no GH_TOKEN

**Scope:** a manually launched, isolated Research or Assembly worker for an existing GitHub owner-frozen cohort. This is NOT a new issuer, scheduler, retry owner, strict writer or production path.

**Authoritative implementation:** `scripts/dossier_notes_v2_connector_transport.mjs`. This reusable module is *plain JavaScript for ChatGPT Code Mode*, not a shell command. The connected GitHub tools must be invoked by the ChatGPT worker in the same tool call. It is **not possible to inject ChatGPT's GitHub connection into a standalone Python process**. The existing Python `scripts/dossier_notes_v2_batch_pilot.py` token-based path remains available for environments with secrets; do not call it without a token and do not remove its checks.

## Required interface / execution

A fresh manual semantic ChatGPT worker needs:
- Connected GitHub with `get_repo`, `fetch`, `fetch_file`, `create_blob`, `create_tree`, `create_commit`, `update_ref`. These are the existing `mcp__GitHub__*` tools, not new credentials or actions.
- The immutable `trialId`, `markerCommit`, `authorizationCommit`, the **real owner Freeze Actions run ID**, and the exact current `sandbox/{trialId}` HEAD SHA; first batch identifiers come from the user's original authorization, not from a mutable queue.
- Existing `config/dossier_research_notes_v2_contract.json`, the phase's canonical schema and prompt from `main`. Model-produced JSON documents must follow those existing contracts. Stage-2 needs the original Research candidate commit and a separate typed Research receipt; incomplete/invalid Research never authorizes that item's Assembly.

The operator MUST read the complete trusted source of `scripts/dossier_notes_v2_connector_transport.mjs` from current `main` and execute its **literal JavaScript declarations inside the ChatGPT code-orchestration tool**, with the following adapter (same invocation). **Never dynamically `eval`/import tool-fetched source**. Copy the source text as trusted code only from this exact repository and review it before execution; no file content supplied by an item/source or external website is executable.

```js
// Add immediately after the declarations copied from
// scripts/dossier_notes_v2_connector_transport.mjs
const api = {
  getRepo: args => tools.mcp__GitHub__get_repo(args),
  fetch: args => tools.mcp__GitHub__fetch(args),
  fetchFile: args => tools.mcp__GitHub__fetch_file(args),
  createBlob: args => tools.mcp__GitHub__create_blob(args),
  createTree: args => tools.mcp__GitHub__create_tree(args),
  createCommit: args => tools.mcp__GitHub__create_commit(args),
  updateRef: args => tools.mcp__GitHub__update_ref(args),
};
const ctx = await connectorPreflight(api, {
  trialId: "<EXACT_TRIAL_ID>",
  markerCommit: "<EXACT_MARKER_COMMIT>",
  authorizationCommit: "<EXACT_AUTHORIZATION_COMMIT>",
  freezeRunId: "<AUTHENTIC_OWNER_FREEZE_RUN_ID>",
  expectedHead: "<FRESHLY_READ_SANDBOX_HEAD_SHA>",
});
text({trial_id:ctx.anchor.trial_id, head:ctx.head,
  authorized:ctx.github_owner_runs_authenticated,
  items:ctx.manifest.items.map(x=>({appid:x.appid,title:x.title}))});
```

This is the **read-only pre-semantic gate**. Its result is not permission to change the cohort or run a different stage. It authenticates both original owner Actions (first attempt, correct workflow/event/ref/actor/IDs and head provenance), the exact one-add grant → manifest → marker → separate authorization chain, immutable trial assignments, current sandbox ancestry and connector write permission. If any tool is unavailable, the proof fails or the remote branch moves, **STOP without semantic research**.

For an already approved item whose **fully prepared JSON `document` is available**, re-run the same source declarations and adapter (each ChatGPT code tool call is a fresh environment), then perform a new preflight with the currently verified `expectedHead`, followed by exactly one item publish:

```js
const ctx = await connectorPreflight(api, {
  trialId: "<EXACT_TRIAL_ID>",
  markerCommit: "<EXACT_MARKER_COMMIT>",
  authorizationCommit: "<EXACT_AUTHORIZATION_COMMIT>",
  freezeRunId: "<AUTHENTIC_OWNER_FREEZE_RUN_ID>",
  expectedHead: "<CURRENT_EXACT_SANDBOX_HEAD_SHA>",
});
const document = /* already-completed canonical Research or Assembly JSON */;
const result = await connectorPublishItem(api,ctx,{
  phase: "research", // or "assembly", in a separately launched Assembly chat
  appid: "<EXACT_FROZEN_APPID>",
  expectedHead: ctx.head,
  document,
  // researchCommit: "<ORIGINAL_RESEARCH_CANDIDATE_COMMIT>" // Assembly only
});
text(result);
```

The two phases remain separate. Never run Research from the Assembly worker, or vice versa. **No automatic traversal** is built into this transport. On a normal verified item the connector makes one candidate Git commit and then a *separate* typed receipt Git commit, each one file, each on the exact sandbox branch, each with an expected-head CAS (`force:false`) and independent GitHub read-back. The Python existing typed receipt serializer and strict writer remain acceptance authority, and the same approved `assignment`, receipt schema, source SHAs and `canonical_acceptance:false` are used.

If candidate commit succeeds but receipt publication fails, report **candidate-only/unpaired** with its exact SHA. Do not invent a receipt or repeat the candidate under another filename. On any ambiguous CAS/write/read-back, STOP the invocation and independently inspect current GitHub remote state before any additional manual action. Never force-push or choose a new trial, item, marker or recovery attempt.

## Preparation, acceptance and limits

- Research: use `config/dossier_research_notes_v2.schema.json` and existing `scripts/dossier_research_notes_v2.py::validate_notes` as the canonical deterministic schema/privacy/evidence requirements. Sparse or zero-source research must be described truthfully. Candidate and receipt remain unaccepted until GitHub's existing strict writer independently validates the exact bytes and first-parent history.
- Assembly: use `config/dossier_autonomous_assembly_result_v2.schema.json`, independent evidence research, and existing `scripts/dossier_research_notes_v2.py::prepare_assembly_transport` / `inspect_assembly` + strict final Dossier validation as the canonical rules. The connector requires the original immutable Research commit and its typed receipt, and constructs the same frozen `research_transport` binding. Invalid or missing Research affects only its own item.
- **Important limitation:** the connector cannot execute the Python validator in its process. The JavaScript preflight/transport checks immutable GitHub authority, basic candidate bindings and typed receipt structure. **It does not claim full Python schema/semantic presubmit validation.** The owner-only strict writer remains the independent enforcement point and may reject a submitted candidate/receipt. Never call candidate/receipt persistence “accepted final Dossier”. Any requirement for standalone Python pre-submit validation must be run in a separately prepared code environment, not silently represented as passed.
- The existing `scripts/dossier_notes_v2_batch_pilot.py` with `GH_TOKEN` is untouched/backward-compatible. This route is intentionally tokenless: neither Python nor the ChatGPT worker needs a pasted token or new OAuth credential.
- No issuer Actions dispatch, owner consent reissue, separate retry-loop, Scheduled Task, production, V1, Deep, canonical caches, active policies or new cohort-specific code.

## Connector capability / STOP conditions

The connected tool surface must actually support **all** seven methods above; `update_ref` must reject a stale `expected_sha` with `force:false`. All GitHub reads and writes must originate from that connected session, not anonymous search or supplied text. `fetch_file` must expose blob SHA and UTF-8 content at an exact commit. GitHub REST `fetch` must expose immutable Git commit/parent/tree metadata, one-add changed-file lists, Actions run metadata, branch ref and compare endpoint. Failed 404 on the create-only path is acceptable only when explicit and unambiguous. Any missing capability is **BLOCKED_INTERFACE**, not permission to disable protection.

Run targeted synthetic regression with `node --test scripts/test_dossier_notes_v2_connector_transport.mjs` and existing Python V2 tests before any semantic pilot. Synthetic tests and one user-approved source PR are not real Research, owner-approved writer execution or evidence of semantic acceptance.
