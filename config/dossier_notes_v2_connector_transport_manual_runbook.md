# Dossier Notes V2 — lean GitHub Connector transport (no GH_TOKEN)

**Role:** one explicitly user-launched isolated Research or separate Assembly worker for an existing owner-authorized cohort. This is not issuer, scheduler, retry manager, strict writer or production.

**Source:** `scripts/dossier_notes_v2_connector_transport.mjs`. The source is plain JavaScript declarations for ChatGPT Code Mode. Copy the complete trusted declarations from current `main` as literal code into the same code-orchestration call as the GitHub tool adapter. **Never eval/import downloaded code.** Data from public reviews is never executable.

## Minimal connector operations

Required: connected GitHub `fetch`, `fetch_file`, `create_blob`, `create_tree`, `create_commit`, `update_ref`. The repository is fixed in the module; no `GH_TOKEN` or `get_repo` permission read is needed. Missing write permission fails on GitHub's own write operation. `update_ref(expected_sha, force:false)` MUST reject stale branches; never use a non-leased alternative.

Required inputs: actual owner `trialId`, `markerCommit`, `authorizationCommit`, first-attempt `freezeRunId`, and independently read current sandbox `expectedHead`. The user cannot invent or change the frozen manifest.

## Mandatory owner proof (once per invocation)

```js
// Immediately after the declarations from the trusted module:
const api = {
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
  freezeRunId: "<OWNER_FREEZE_RUN_ID>",
  expectedHead: "<CURRENT_SANDBOX_HEAD>",
  phase: "research", // "assembly" only in the separately approved Assembly chat
});
text({head:ctx.head,items:ctx.manifest.items.map(x=>[x.appid,x.title]),
  authorized:ctx.github_owner_runs_authenticated});
```

This preflight checks real first-attempt owner-issued **Freeze and Authorize** Actions, exact owner login/id/event/workflow/main/run name, original grant → manifest → marker → separate authorization Git parent chain, immutable assignment/title/edition/source manifest, and the exact current sandbox HEAD. A moved/unrelated sandbox stops. On an already populated sandbox it uses **one compare** to discover previously added paths instead of scanning every historical commit. Source-signed Git committer names, timestamps and repeated main comparisons are not relied upon as authorization. Research fetches only its own frozen schema plus receipt schema; Assembly fetches its schema plus receipt schema.

**Do not repeat owner proof for every item inside the same Code Mode call.** Reuse the verified `ctx`; after a context/tool-call boundary run a fresh preflight with the newly verified current sandbox HEAD. A fresh call repeats immutable checks but does not create/authorize a new cohort.

## Publish one independently authorized item

```js
const document = /* ready Research or Assembly JSON matching frozen assignment */;
const result = await connectorPublishItem(api,ctx,{
  phase: "research", // must match ctx.phase
  appid: "<EXACT_APPID>",
  expectedHead: ctx.head,
  document,
  // researchCommit: "<ORIGINAL_RESEARCH_CANDIDATE_COMMIT>" // Assembly only
});
text(result);
```

Use the same `ctx` for the next item in that single invocation if the first returned a confirmed receipt; `ctx.head` is updated by the transport. No automatic traversal, retry, replacement candidate or queue is introduced.

Per item, GitHub receives one new Research/Assembly candidate and a **separate typed receipt** as two sequential create-only Git commits. For each commit the connector makes exactly one blob, one tree, one commit, a non-force expected-head CAS, and one independent **branch HEAD** readback. There is no repeated download of the just-written bytes or per-commit full history scan. The strict GitHub writer later checks original immutable bytes, one-add parent history, exact schemas, privacy and semantics. A connector write is **NOT** a canonical or semantic acceptance.

If the candidate publishes but receipt fails, report candidate-only with exact commit SHA, stop, and inspect remote state before any new action. No blind retry, overwrite, force push, alternate filename, reissue, new marker or automated recovery. Existing receipt path means already submitted; do not republish.

Assembly must independently find the original Research candidate and its separate typed receipt, cross-check original commit/blob/SHA and frozen `research_transport`; incomplete/bad A must not hold valid siblings B/C. For a resumed Assembly session, it discovers the Research receipt's introduction via a single path-filtered GitHub commits lookup rather than a full historical traversal. The existing Python strict writer determines final acceptance.

## Limits and tests

- The JS checks schema structure/assignment before write, but does not reproduce Python privacy/evidence/strict Dossier validation. Final strict writer alone accepts or rejects each item.
- Token-backed `scripts/dossier_notes_v2_batch_pilot.py` remains unchanged and usable only in authenticated Python checkout environments.
- All writes stay in `sandbox/{trial_id}`. No issuer workflow dispatch, no original18, V1, Deep, active policy, canonical cache, production or scheduled task changes.
- Required tests: `node --test scripts/test_dossier_notes_v2_connector_transport.mjs` plus existing Python V2 tests, and exact-head GitHub PR CI. Regression explicitly verifies 10 GitHub operations per Research candidate+receipt pair and one-comparison resume.
- Any failed owner proof, wrong assignment/phase, missing receipt, duplicate path, stale CAS, ambiguous remote branch readback or unavailable connector capability **STOP**. A rejected CAS is never automatically retried.
