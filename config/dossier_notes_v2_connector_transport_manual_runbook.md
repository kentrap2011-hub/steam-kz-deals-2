# Dossier Notes V2 — lean tokenless GitHub Connector

**Role:** manually launched, isolated Research or independently launched Assembly for an already owner-authorized batch. Not an issuer, schedule, retry owner or production process. Source: `scripts/dossier_notes_v2_connector_transport.mjs` from **current main**.

## Why two Code Mode calls are mandatory

**Measured live GitHub Connector limit: 20 nested tool calls per Code Mode invocation.** Real owner preflight costs 14 calls on the empty sandbox; one game with two typed commits needs 10, so 14 + 10 cannot be executed in the same invocation. Use the verified **session handoff** below. This does not create a new GitHub grant, queue, retry or file.

- Call A: full owner preflight only. Verify two successful first-attempt GitHub Actions, issuer parent/manifest, exact immutable assignments, owner ID and real branch HEAD; download current phase schema plus receipt schema. Output the complete machine-readable session handoff.
- Call B: take **only the exact immediately preceding Call A output**, restore the verified context with one fresh remote branch HEAD read, publish **one game** using exactly 10 additional GitHub calls, then output the updated handoff.
- Call C and subsequent calls: use only the just-returned updated handoff from the previous successful game, for **one next game**. Each call uses 11 connected GitHub operations, below the proven limit. Do not combine two games in one Code Mode call.
- If a call fails, loses its output, or an ambiguous GitHub write occurs, **STOP**. The next manual action requires an independent fresh GitHub preflight at the actual current sandbox HEAD; do not forge, edit or reconstruct a handoff from a prompt, outside file, user input or guesses. The handoff SHA256 detects accidental copy corruption **but is not a cryptographic authentication of a user-supplied payload**. Its authority is exclusively the immediately preceding verified output in this same explicit ChatGPT session.

## Call A — read-only preflight, 14 GitHub calls on an empty sandbox

Copy the complete trusted JavaScript declarations from `scripts/dossier_notes_v2_connector_transport.mjs` into the ChatGPT Code Mode tool call. Do not dynamically `eval` or import GitHub-fetched source. Append:

```js
const api = {
  fetch: args => tools.mcp__GitHub__fetch(args),
  fetchFile: args => tools.mcp__GitHub__fetch_file(args),
  createBlob: args => tools.mcp__GitHub__create_blob(args),
  createTree: args => tools.mcp__GitHub__create_tree(args),
  createCommit: args => tools.mcp__GitHub__create_commit(args),
  updateRef: args => tools.mcp__GitHub__update_ref(args)
};
const ctx = await connectorPreflight(api,{
  trialId:"<EXACT_OWNER_ISSUED_TRIAL>",
  markerCommit:"<EXACT_MARKER_COMMIT>",
  authorizationCommit:"<EXACT_AUTHORIZATION_COMMIT>",
  freezeRunId:"<REAL_FIRST_ATTEMPT_OWNER_FREEZE_RUN>",
  expectedHead:"<FRESH_EXACT_SANDBOX_HEAD>",
  phase:"research" // separately launched Assembly chat uses "assembly"
});
text(JSON.stringify(connectorHandoff(ctx)));
```

The returned JSON handoff is usable **only in the next call of this same explicitly authorized manual session**. Preflight is not a Research result and does not authorize publishing another cohort. The first fresh6 cohort still requires exact original manifest/marker/authorization, unchanged owner Actions; never reissue Freeze/Authorize.

## Call B — one game (11 GitHub calls)

In a **new Code Mode call** paste the same trusted JavaScript declarations and the same `api` adapter (not an old cached source). Use only the exact Call A handoff as data:

```js
const handoff = /* exact JSON returned by preceding successful call */;
const ctx = await connectorResumeHandoff(api,handoff);
const document = /* exact prepared Research/Assembly JSON matching frozen assignment */;
const result = await connectorPublishItem(api,ctx,{
  phase:"research", // equal to ctx.phase
  appid:"<NEXT_EXACT_FROZEN_APPID>",
  expectedHead:ctx.head,
  document,
  // researchCommit:"<EXACT_ORIGINAL_RESEARCH_CANDIDATE_COMMIT>" // Assembly only
});
text({result,next_handoff:connectorHandoff(ctx)});
```

The result must include the exact candidate and typed receipt SHA; **only then** use `next_handoff` for the next game with a new Code Mode call. Never reuse the old handoff on a moved branch or retry a published candidate.

GitHub transport performs create-only blob/tree/commit and non-force `update_ref(expected_sha,force:false)`, plus an independent branch HEAD readback **for both** candidate and separately committed typed receipt. This is not final acceptance; existing GitHub Python strict writer independently checks original single-add lineage, bytes/blob, research privacy/evidence and Assembly final dossier validation. A missing or failed receipt leaves an incomplete candidate: stop and report, do not silently retry.

Assembly requires original Research candidate and its typed receipt, with immutable SHA binding. A missing or invalid Research on game A does not automatically block other games. The phase must be set to `assembly` in its **own** full owner preflight; only its own verified handoffs may continue.

## Scope and regression

Only the sandbox branch may change during a separately user-launched semantic run. No original18, V1, Deep, canonical cache, production, GitHub Actions issuer, scheduler or automatic retry. Keep the independent token-backed Python CLI unchanged where authenticated secrets exist.

The current JS schema check prevents malformed field/assignment publication but does not reproduce Python privacy and strict semantics. Synthetic Node tests include exact **14-call preflight + 11-call per-item continuation**, all six immutable Research assignments, restart/duplicate/CAS rejection, and independent Assembly-bound research receipt. Run `node --test scripts/test_dossier_notes_v2_connector_transport.mjs`, existing Python V2 tests and final-HEAD GitHub PR CI before release. Green synthetic tests do not prove actual live Research or accepted dossiers.
