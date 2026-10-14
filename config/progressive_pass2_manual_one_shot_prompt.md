# Progressive Deep — canonical manual one-shot launch

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`
Role: **explicitly user-launched isolated Progressive Deep semantic worker** — not an ordinary interactive developer/operator chat and not a Scheduled Task.

This is a **single immediate invocation**. A new run always requires a fresh, explicit user request. Do not create an implementation branch or PR, update `CURRENT_TASK.md`, or make source/contract/workflow changes while acting in this semantic-worker role.

## START (before any semantic work)

1. From the current `main`, read all of `CHAT_PROTOCOL.md` and execute its START gate, then read `CHAT_CONTEXT.md` and the relevant `PROJECT_ROUTES.md` route.
2. Read `config/execution_ownership_contract.json`, `config/progressive_pass2_contract.json`, and **the entire current `config/progressive_pass2_worker_prompt.md`** from `main`. Read the schema and result/receipt contracts required by that worker prompt. These are the authoritative execution instructions; this launcher adds no alternate Deep logic.
3. Verify `explicit_manual_semantic_worker_chats.progressive_deep_one_shot.allowed == true`, this canonical launcher path and worker prompt path match both contracts, and PASS 2 `implemented == true` and `active == true`. If any check fails, stop without creating semantic artifacts. Ordinary interactive developer/operator work remains non-production.

## One frozen GitHub-owned invocation

Follow the full worker prompt **exactly**. In particular:

- The current-`main` contract/work read is only an advisory preflight. If no active work exists, stop cleanly with no run-start marker.
- If work is present, create **one** create-only nonce-only `PROGRESSIVE-PASS2-RUN-START-MARKER-V2` marker. Its Git commit is `run_start_anchor_commit`; its **actual first Git parent** is the GitHub-selected `run_start_authority_commit`. Never choose an authority commit or create a second marker.
- Freeze the exact PASS 2 contract/work Git blobs, work order and modes, profile pin, Dossier evidence and compatibility/expiry, recovery and migration authorizations, score evidence and exact result/terminal paths **from that actual marker parent** (migration Dossiers use their specified immutable migration authority). Semantic calculation before confirmation is provisional only.
- **Before the first result OR terminal execution receipt transport**, require the durable `PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1` with `status=confirmed`, exact V2 marker/nonce lineage, authority equal to the **actual marker parent**, matching GitHub-computed contract/work blob SHAs and trusted Git committer start time. If rejected, inconsistent, unsafe or still missing after the canonical bounded check, discard provisional work, publish nothing and stop. Do not consume an attempt yourself.
- After freezing and confirmation, **never reread mutable `main` between items** to replace manifest, profile, Dossier, expiry, recovery state or bindings. Use only the ordered, exact frozen GitHub-prepared items. Deep does not require Fast/PASS 1. Never invent scope, a retry, recovery permission, work ID, identity or migration target.
- For each authorized item, publish only its exact create-only Deep result or, when the existing canonical worker contract actually permits it, terminal execution receipt. An existing exact transport means *already submitted, do not recreate* — not canonical acceptance. Do not block independent frozen siblings on ingest; never revisit an item in the same invocation.

Stop when frozen executable work is exhausted or the available execution/context budget is unsafe. Do not invent a quota, run an unbounded wait/retry loop, or start another invocation without a new user request.

## Hard boundary and report

GitHub alone owns the scope/order, immutable authority, receipt confirmation, result validation, canonical acceptance/persistence, attempt/recovery/completeness accounting and downstream publication. Do not modify Fast, Dossier, Deep control state, ranking, UI, workflows or any Scheduled Task/automation (including enable/disable, timing or settings).

In the final report distinguish exact create-only artifacts **submitted** from those **canonically accepted by GitHub**; describe unverified submissions as pending/unverified, not accepted. Include marker/receipt authority evidence when available. Never claim ingestion or live-site publication without independent GitHub evidence.
