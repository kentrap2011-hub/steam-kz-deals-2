# Manual owner-requested Notes V2 Assembly replay — reusable route (no new source PR)

This is a **generic operator entrypoint**; it is not permission for automatic semantic Research, a scheduler, canonical writer or retry. User must explicitly ask for **each** new Assembly attempt: e.g. “Повтори второй этап Dossier для этих игр; используй тот же Research”. Developer code does not change for repeat #2, #3, #10.

## Technical connector capability / limit

The connected GitHub app exposes `mcp__GitHub__create_branch`, `mcp__GitHub__create_file`, `mcp__GitHub__fetch` and `mcp__GitHub__fetch_file`; **there is no workflow_dispatch action in the currently exposed connector**. Therefore the supported low-friction request path is one **new branch** and one **create-only request file**, both done by ChatGPT through that connected GitHub app (the user need not edit files or open GitHub UI). This push triggers one owner-only GitHub Actions workflow on the request branch. The branch creation itself has no matching request file and does not grant authority. Do not invoke the real request during source implementation/PR CI.

## Operator request flow (new user consent every run)

1. Read current `CHAT_PROTOCOL.md` and `CHAT_CONTEXT.md`. Verify this generic source PR is merged into current `main`, `config/dossier_notes_v2_generic_replay_policy.json` allows owner-request activation and all Lean canonical/Deep/production flags remain off. Verify the user just approved the exact Research source and selected AppIDs. This is a manual operator request, NOT a semantic worker.
2. Choose a **new random 128-bit lowercase hex** request nonce (32 hex chars); nonce is a uniqueness handle, **not authorization**. Obtain the latest immutable `main` SHA. Using connected GitHub, invoke `create_branch` exactly once with `branch_name: "dossier-assembly-requests/<nonce>"` and exact `sha: <latest-main-sha>`. No generic retry on collision.
3. Using `create_file` exactly once on that request branch, write to `data/control/dossier_notes_v2/replay_requests/<nonce>.json` with precisely:
   ```json
   {
     "schema": "DOSSIER-NOTES-V2-GENERIC-ASSEMBLY-REPLAY-REQUEST-V1",
     "schema_version": 1,
     "nonce": "<nonce>",
     "source_trial_id": "dossier-notes-v2-fresh6-20261114-rerun1",
     "appids": ["1000010","102600","1029690","49520","499180","501590"],
     "purpose": "repeat_assembly_from_exact_accepted_research"
   }
   ```
   This sample is the **six-game first use only**; future requests may use an owner-issued Notes V2 source trial and a correctly ordered subset. Never choose arbitrary new AppIDs, reorder the frozen source manifest, or accept terminal/rejected/missing Research receipts. The server verifies real exact owner actor, event/first attempt, the one-add request and source provenance, not a ChatGPT assertion. If `create_file` fails/returns ambiguous state, **STOP**; inspect remote state, do not invent a new path to avoid the original result.
4. GitHub Action `.github/workflows/issue-dossier-notes-v2-generic-assembly-replay.yml` runs on the exact request branch push, **not** on merge to main or on a schedule. Exact first-attempt real owner run validates the request/immutability, approved source Notes V2 issuer and completed original owner run, exact source Research candidate and typed receipt for **every** item, exact AppID/edition/title/order, nonexisting destination namespace, then creates fresh grant → manifest → nonce marker → direct-child authorization → one-add re-bound Research candidate+receipt per item; one nonforce sandbox push.
5. New trial ID is deterministic from nonce: `dossier-notes-v2-assembly-replay-<nonce>`; sandbox is `sandbox/<trial_id>`. GitHub owns the identifiers/assignments and verifies source, not the operator. **Do not run Assembly** before the run has actually completed successfully, the exact GitHub Actions actor/ref/run-attempt/path/title/request-commit matches the grant and all new Research candidate+receipt commits are independently visible on the sandbox. A valid new request is one additional semantic attempt; **rerun the same GitHub workflow is not another semantic attempt** and must never reissue on a collision.
6. Only then open a **SEPARATE NEW physical user-launched Assembly chat**, supplying `config/dossier_notes_v2_generic_assembly_replay_manual_one_shot_prompt.md`, the exact request nonce and verified GitHub authority. That chat must read frozen manifest/Research and follow existing one-item-at-a-time connector preflight/handoff/CAS publisher. Only new-trial Research introduction SHAs are eligible, not source-trial Research SHAs. The operator does not call the sandbox writer; canonical/Deep/production remain off absent separate owner activation.

### Fail-closed, no invisible automation

If GitHub's connected app cannot create a request branch or push the request file under the genuine owner identity (e.g. permission/trigger limitations), **report `BLOCKED_AUTHORITY`** and the exact failed GitHub operation. The safe fallback is an explicitly owner-run GitHub request operation once connectivity/permissions are corrected; never fake a grant or silently use ChatGPT as GitHub control plane. Source PR CI alone does not prove live owner-action trigger. Technical GitHub job retry is **not** a semantic retry; only a **new user request and new namespace** can begin another attempt. No scheduled task.

## Optional individually owner-authorized Lean sandbox automatic writer (source-only until activation)

The old request schema and manual strict/Lean writer route remain the default. **Do not add automatic writer consent without a fresh explicit owner instruction for that specific new trial.** To make a brand-new future trial eligible, add only `"lean_auto_writer": true` to the original **first-attempt owner request JSON** shown above. The request branch push is still owner-authenticated, and the issuer must prove exact original signed Research, baseline strict Dossier blob, original release year, ordered title/edition and typed receipts. It embeds `sandbox_lean_auto_writer_authorized: true` in new immutable grant and authorization (and extra year/baseline fields in new manifest rows). Old requests without this optional key and existing strict V1/V2/original18 remain **manual**. Do not use `allow_automatic_writer=true`, do not generate owner consent from a mutable sandbox, and do not create a new Research or Assembly worker.

After a separately user-started Assembly chat has published the exact original create-only Assembly + typed terminal receipt pairs, a successful read-only signal workflow may wake the trusted main-owned writer once every bound item is actually ready. Writer derives pairs from the exact Git receipt Git history, not from owner-pasted JSON. One durable create-only control Git ref per trial suppresses a second attempt regardless of outcome, and the existing serialized sandbox writer stages exactly N docs + N acceptance receipts in one Git commit and single nonforce push. A missing/invalid/stale year, game identity, receipt, owner issuer, token, branch, TTL or output collision stops. Failures are not automatically retried.

**Activation remains separately blocked** by `config/dossier_lean_writer_auto_ready_v1.json#activation_enabled=false`, exact-final-HEAD CI, independent substantive L3 and a separately approved main activation change. This operator route documents future readiness; it is not permission to issue a new trial or run the writer as part of a source PR.
